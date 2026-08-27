from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.services.nasabah.nasabah_service import NasabahService
from bank_djago.services.rekening.rekening_service import RekeningService


NIK_UJI_BERHASIL = "9999999999999001"
NIK_UJI_GAGAL = "9999999999999002"


def bersihkan_data_pengujian(*daftar_nik):
    koneksi = buat_koneksi()

    try:
        for nik in daftar_nik:
            # Rekening dihapus lebih dahulu karena memiliki foreign key
            # yang mengarah ke tabel nasabah.
            koneksi.execute(
                """
                DELETE FROM rekening
                WHERE nik_pemilik = ?
                """,
                (nik,)
            )

            koneksi.execute(
                """
                DELETE FROM nasabah
                WHERE nik = ?
                """,
                (nik,)
            )

        koneksi.commit()

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()


def hitung_rekening_nasabah(nik):
    koneksi = buat_koneksi()

    try:
        cursor = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM rekening
            WHERE nik_pemilik = ?
            """,
            (nik,)
        )

        return cursor.fetchone()["jumlah"]

    finally:
        koneksi.close()


def uji_pendaftaran_nasabah():
    # Membersihkan sisa data jika pengujian sebelumnya berhenti di tengah.
    bersihkan_data_pengujian(
        NIK_UJI_BERHASIL,
        NIK_UJI_GAGAL
    )

    try:
        # ============================================================
        # Pengujian 1: pendaftaran dan rekening pertama berhasil
        # ============================================================

        nasabah_baru, rekening_baru = (
            NasabahService.daftar_dan_buka_rekening(
                nik=NIK_UJI_BERHASIL,
                nama="nasabah pengujian",
                alamat="Banyuwangi",
                pin="123456",
                setor_awal=1_000_000,
                level=1
            )
        )

        data_nasabah = (
            NasabahRepository.cari_nasabah_dengan_nik(
                NIK_UJI_BERHASIL
            )
        )

        data_rekening = (
            RekeningRepository.cari_rekening_dengan_norek(
                rekening_baru.norek
            )
        )

        assert data_nasabah is not None, (
            "Nasabah tidak ditemukan setelah pendaftaran"
        )

        assert data_nasabah["nik"] == NIK_UJI_BERHASIL, (
            "NIK nasabah yang tersimpan tidak sesuai"
        )

        assert data_nasabah["nama"] == nasabah_baru.nama, (
            "Nama nasabah yang tersimpan tidak sesuai"
        )

        assert data_nasabah["alamat"] == nasabah_baru.alamat, (
            "Alamat nasabah yang tersimpan tidak sesuai"
        )

        assert data_rekening is not None, (
            "Rekening pertama tidak ditemukan"
        )

        assert data_rekening["nik_pemilik"] == NIK_UJI_BERHASIL, (
            "Foreign key rekening tidak mengarah ke nasabah yang benar"
        )

        assert data_rekening["norek"] == rekening_baru.norek, (
            "Nomor rekening yang tersimpan tidak sesuai"
        )

        assert rekening_baru.pemilik is nasabah_baru, (
            "Objek rekening tidak menunjuk objek nasabah"
        )

        assert rekening_baru in nasabah_baru.rekening, (
            "Rekening belum masuk ke daftar rekening nasabah"
        )

        assert nasabah_baru.rekening.count(rekening_baru) == 1, (
            "Objek rekening masuk ke daftar nasabah lebih dari satu kali"
        )

        print("✅ Nasabah dan rekening pertama berhasil disimpan")
        print("✅ Foreign key rekening mengarah ke nasabah yang benar")
        print("✅ Relasi objek nasabah dan rekening berhasil dibentuk")

        # ============================================================
        # Pengujian 2: NIK duplikat ditolak
        # ============================================================

        jumlah_rekening_sebelum = hitung_rekening_nasabah(
            NIK_UJI_BERHASIL
        )

        try:
            NasabahService.daftar_dan_buka_rekening(
                nik=NIK_UJI_BERHASIL,
                nama="nasabah duplikat",
                alamat="Jember",
                pin="654321",
                setor_awal=1_000_000,
                level=1
            )

            assert False, "NIK duplikat seharusnya ditolak"

        except ValueError as error:
            print(f"✅ NIK duplikat berhasil ditolak: {error}")

        jumlah_rekening_setelah = hitung_rekening_nasabah(
            NIK_UJI_BERHASIL
        )

        assert jumlah_rekening_setelah == jumlah_rekening_sebelum, (
            "Penolakan NIK duplikat justru membuat rekening baru"
        )

        # ============================================================
        # Pengujian 3: kegagalan rekening membatalkan data nasabah
        # ============================================================

        try:
            NasabahService.daftar_dan_buka_rekening(
                nik=NIK_UJI_GAGAL,
                nama="nasabah gagal",
                alamat="Malang",
                pin="112233",
                setor_awal=0,
                level=1
            )

            assert False, (
                "Setoran di bawah minimum seharusnya ditolak"
            )

        except ValueError as error:
            print(
                "✅ Setoran awal tidak valid berhasil ditolak:",
                error
            )

        nasabah_gagal = (
            NasabahRepository.cari_nasabah_dengan_nik(
                NIK_UJI_GAGAL
            )
        )

        jumlah_rekening_gagal = hitung_rekening_nasabah(
            NIK_UJI_GAGAL
        )

        assert nasabah_gagal is None, (
            "Rollback gagal: nasabah tanpa rekening masih tersimpan"
        )

        assert jumlah_rekening_gagal == 0, (
            "Rollback gagal: rekening tidak valid masih tersimpan"
        )

        print("✅ Rollback menghapus nasabah ketika rekening gagal dibuat")

        # ============================================================
        # Pengujian 4: nasabah lama membuka rekening tambahan
        # ============================================================

        jumlah_sebelum = hitung_rekening_nasabah(
            NIK_UJI_BERHASIL
        )

        rekening_tambahan = RekeningService.buka_rekening(
            nasabah=nasabah_baru,
            pilihan=1,
            pin="445566",
            setor_awal=1_000_000
        )

        jumlah_setelah = hitung_rekening_nasabah(
            NIK_UJI_BERHASIL
        )

        data_rekening_tambahan = (
            RekeningRepository.cari_rekening_dengan_norek(
                rekening_tambahan.norek
            )
        )

        assert jumlah_setelah == jumlah_sebelum + 1, (
            "Jumlah rekening nasabah tidak bertambah satu"
        )

        assert data_rekening_tambahan is not None, (
            "Rekening tambahan tidak tersimpan"
        )

        assert (
            data_rekening_tambahan["nik_pemilik"]
            == NIK_UJI_BERHASIL
        ), "Rekening tambahan terhubung ke nasabah yang salah"

        assert rekening_tambahan in nasabah_baru.rekening, (
            "Rekening tambahan belum masuk ke objek nasabah"
        )

        assert nasabah_baru.rekening.count(rekening_tambahan) == 1, (
            "Rekening tambahan masuk ke list lebih dari satu kali"
        )

        print("✅ Nasabah lama berhasil membuka rekening tambahan")
        print("✅ Seluruh pengujian NasabahService berhasil")

    finally:
        # Data pengujian selalu dibersihkan, termasuk ketika assert gagal.
        bersihkan_data_pengujian(
            NIK_UJI_BERHASIL,
            NIK_UJI_GAGAL
        )


if __name__ == "__main__":
    uji_pendaftaran_nasabah()

    # Memastikan proses pembersihan benar-benar berhasil.
    assert (
        NasabahRepository.cari_nasabah_dengan_nik(
            NIK_UJI_BERHASIL
        )
        is None
    )

    assert (
        NasabahRepository.cari_nasabah_dengan_nik(
            NIK_UJI_GAGAL
        )
        is None
    )

    print("✅ Data pengujian berhasil dibersihkan")