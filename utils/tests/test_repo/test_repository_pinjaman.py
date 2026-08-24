import datetime

from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.pinjaman import Pinjaman
from bank_djago.core.rekening import RekeningReguler
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import StatusPinjaman


NIK_PERTAMA = "TEST-PINJAMAN-NASABAH-1"
NIK_KEDUA = "TEST-PINJAMAN-NASABAH-2"

NOREK_PERTAMA = "REK-PINJAMAN-001"
NOREK_KEDUA = "REK-PINJAMAN-002"
NOREK_TIDAK_TERDAFTAR = "REK-PINJAMAN-TIDAK-ADA"


def bersihkan_data_uji():
    koneksi = buat_koneksi()

    try:
        # Pinjaman harus dihapus sebelum rekening karena
        # mempunyai foreign key menuju rekening.
        koneksi.execute(
            """
            DELETE FROM pinjaman
            WHERE norek IN (?, ?)
            """,
            (
                NOREK_PERTAMA,
                NOREK_KEDUA
            )
        )

        koneksi.execute(
            """
            DELETE FROM rekening
            WHERE norek IN (?, ?)
            """,
            (
                NOREK_PERTAMA,
                NOREK_KEDUA
            )
        )

        koneksi.execute(
            """
            DELETE FROM nasabah
            WHERE nik IN (?, ?)
            """,
            (
                NIK_PERTAMA,
                NIK_KEDUA
            )
        )

        koneksi.commit()

    finally:
        koneksi.close()


def buat_pinjaman(
        id_lokal,
        nasabah,
        rekening,
        nominal,
        bunga,
        tenor,
        status
):
    # ID yang diberikan kepada constructor masih merupakan ID
    # objek lokal. ID global akan dibuat oleh SQLite.
    pinjaman = Pinjaman(
        ID=id_lokal,
        pemilik=nasabah,
        rekening=rekening,
        nominal_pinjaman=nominal,
        bunga=bunga,
        tenor=tenor
    )

    pinjaman.status = status

    return pinjaman


def buat_data_uji():
    nasabah_pertama = Nasabahh(
        nama="Nasabah Pinjaman Pertama",
        alamat="Banyuwangi",
        nik=NIK_PERTAMA
    )

    rekening_pertama = RekeningReguler(
        norek=NOREK_PERTAMA,
        pin="111111",
        pemilik=nasabah_pertama
    )

    nasabah_kedua = Nasabahh(
        nama="Nasabah Pinjaman Kedua",
        alamat="Jember",
        nik=NIK_KEDUA
    )

    rekening_kedua = RekeningReguler(
        norek=NOREK_KEDUA,
        pin="222222",
        pemilik=nasabah_kedua
    )

    # Pinjaman historis milik nasabah pertama.
    pinjaman_lunas = buat_pinjaman(
        id_lokal=1,
        nasabah=nasabah_pertama,
        rekening=rekening_pertama,
        nominal=6_000_000,
        bunga=0.10,
        tenor=6,
        status=StatusPinjaman.LUNAS
    )

    pinjaman_lunas.cicilan_tetap = 1_050_000
    pinjaman_lunas.sisa_pokok = 0
    pinjaman_lunas.cicilan_terbayar = 6
    pinjaman_lunas.tanggal_pencairan = datetime.date(2026, 1, 23)
    pinjaman_lunas.tanggal_jatuh_tempo = datetime.date(2026, 7, 23)

    # Pinjaman yang masih berjalan milik nasabah pertama.
    pinjaman_aktif = buat_pinjaman(
        id_lokal=2,
        nasabah=nasabah_pertama,
        rekening=rekening_pertama,
        nominal=12_000_000,
        bunga=0.12,
        tenor=12,
        status=StatusPinjaman.AKTIF
    )

    pinjaman_aktif.cicilan_tetap = 1_100_000
    pinjaman_aktif.sisa_pokok = 9_000_000
    pinjaman_aktif.cicilan_terbayar = 3
    pinjaman_aktif.tanggal_pencairan = datetime.date(2026, 5, 23)
    pinjaman_aktif.tanggal_jatuh_tempo = datetime.date(2026, 9, 23)

    # Pinjaman historis milik nasabah kedua.
    pinjaman_ditolak = buat_pinjaman(
        id_lokal=1,
        nasabah=nasabah_kedua,
        rekening=rekening_kedua,
        nominal=3_000_000,
        bunga=0.10,
        tenor=6,
        status=StatusPinjaman.DITOLAK
    )

    # Pinjaman yang sedang diajukan milik nasabah kedua.
    pinjaman_diajukan = buat_pinjaman(
        id_lokal=2,
        nasabah=nasabah_kedua,
        rekening=rekening_kedua,
        nominal=5_000_000,
        bunga=0.10,
        tenor=6,
        status=StatusPinjaman.DIAJUKAN
    )

    return {
        "nasabah": [
            nasabah_pertama,
            nasabah_kedua
        ],
        "rekening": [
            rekening_pertama,
            rekening_kedua
        ],
        "pinjaman": [
            pinjaman_lunas,
            pinjaman_aktif,
            pinjaman_ditolak,
            pinjaman_diajukan
        ]
    }


def uji_repository_pinjaman():
    bersihkan_data_uji()

    data_uji = buat_data_uji()

    nasabah_pertama, nasabah_kedua = data_uji["nasabah"]
    rekening_pertama, rekening_kedua = data_uji["rekening"]

    (
        pinjaman_lunas,
        pinjaman_aktif,
        pinjaman_ditolak,
        pinjaman_diajukan
    ) = data_uji["pinjaman"]

    try:
        # Pinjaman harus ditolak jika rekening induknya
        # belum tersimpan dalam database.
        hasil_tanpa_rekening = (
            PinjamanRepository.tambah_pinjaman(
                pinjaman_lunas
            )
        )

        assert hasil_tanpa_rekening is None, (
            "Pinjaman tanpa rekening terdaftar seharusnya ditolak"
        )

        print("✅ Pinjaman tanpa rekening terdaftar berhasil ditolak")

        # Menyimpan nasabah sebagai data induk rekening.
        assert (
            NasabahRepository.tambah_nasabah(
                nasabah_pertama
            )
            is True
        )

        assert (
            NasabahRepository.tambah_nasabah(
                nasabah_kedua
            )
            is True
        )

        print("✅ Nasabah pengujian berhasil disimpan")

        # Menyimpan rekening sebagai data induk pinjaman.
        assert (
            RekeningRepository.tambah_rekening(
                rekening_pertama
            )
            is True
        )

        assert (
            RekeningRepository.tambah_rekening(
                rekening_kedua
            )
            is True
        )

        print("✅ Rekening pengujian berhasil disimpan")

        # Menyimpan empat pinjaman dan menerima ID global
        # yang dibuat oleh SQLite.
        id_lunas = PinjamanRepository.tambah_pinjaman(
            pinjaman_lunas
        )

        id_aktif = PinjamanRepository.tambah_pinjaman(
            pinjaman_aktif
        )

        id_ditolak = PinjamanRepository.tambah_pinjaman(
            pinjaman_ditolak
        )

        id_diajukan = PinjamanRepository.tambah_pinjaman(
            pinjaman_diajukan
        )

        seluruh_id = {
            id_lunas,
            id_aktif,
            id_ditolak,
            id_diajukan
        }

        assert all(
            isinstance(id_pinjaman, int)
            for id_pinjaman in seluruh_id
        ), "Seluruh ID pinjaman seharusnya berupa integer"

        assert len(seluruh_id) == 4, (
            "Setiap pinjaman seharusnya mempunyai ID global berbeda"
        )

        print("✅ Empat pinjaman berhasil disimpan")
        print("✅ Seluruh pinjaman mempunyai ID global berbeda")

        # Memeriksa pencarian satu pinjaman menggunakan ID global.
        hasil_id = (
            PinjamanRepository.cari_pinjaman_dengan_id(
                id_aktif
            )
        )

        assert hasil_id is not None
        assert hasil_id["id"] == id_aktif
        assert hasil_id["norek"] == NOREK_PERTAMA
        assert (
            hasil_id["nominal_pinjaman"]
            == pinjaman_aktif.nominal_pinjaman
        )
        assert hasil_id["bunga"] == pinjaman_aktif.bunga
        assert hasil_id["tenor"] == pinjaman_aktif.tenor
        assert (
            hasil_id["cicilan_tetap"]
            == pinjaman_aktif.cicilan_tetap
        )
        assert (
            hasil_id["sisa_pokok"]
            == pinjaman_aktif.sisa_pokok
        )
        assert (
            hasil_id["cicilan_terbayar"]
            == pinjaman_aktif.cicilan_terbayar
        )
        assert hasil_id["status"] == StatusPinjaman.AKTIF.value

        assert (
            hasil_id["tanggal_pencairan"]
            == pinjaman_aktif.tanggal_pencairan.isoformat()
        )

        assert (
            hasil_id["tanggal_jatuh_tempo"]
            == pinjaman_aktif.tanggal_jatuh_tempo.isoformat()
        )

        print("✅ Pencarian pinjaman berdasarkan ID berhasil")

        # Nasabah pertama harus mendapatkan pinjaman aktif,
        # bukan pinjaman lamanya yang sudah lunas.
        hasil_berjalan_pertama = (
            PinjamanRepository.cari_pinjaman_berjalan(
                NIK_PERTAMA
            )
        )

        assert hasil_berjalan_pertama is not None
        assert hasil_berjalan_pertama["id"] == id_aktif
        assert (
            hasil_berjalan_pertama["status"]
            == StatusPinjaman.AKTIF.value
        )

        print(
            "✅ Pinjaman berjalan nasabah pertama "
            "berhasil ditemukan"
        )

        # Pinjaman diajukan juga termasuk pinjaman berjalan.
        hasil_berjalan_kedua = (
            PinjamanRepository.cari_pinjaman_berjalan(
                NIK_KEDUA
            )
        )

        assert hasil_berjalan_kedua is not None
        assert hasil_berjalan_kedua["id"] == id_diajukan
        assert (
            hasil_berjalan_kedua["status"]
            == StatusPinjaman.DIAJUKAN.value
        )

        print(
            "✅ Pinjaman berstatus diajukan "
            "termasuk pinjaman berjalan"
        )

        # Riwayat nasabah pertama hanya berisi pinjaman lunas.
        riwayat_pertama = (
            PinjamanRepository.cari_riwayat_semua_pinjaman(
                NIK_PERTAMA
            )
        )

        assert len(riwayat_pertama) == 1
        assert riwayat_pertama[0]["id"] == id_lunas
        assert (
            riwayat_pertama[0]["status"]
            == StatusPinjaman.LUNAS.value
        )

        print("✅ Riwayat pinjaman lunas berhasil ditemukan")

        # Riwayat nasabah kedua hanya berisi pinjaman ditolak.
        riwayat_kedua = (
            PinjamanRepository.cari_riwayat_semua_pinjaman(
                NIK_KEDUA
            )
        )

        assert len(riwayat_kedua) == 1
        assert riwayat_kedua[0]["id"] == id_ditolak
        assert (
            riwayat_kedua[0]["status"]
            == StatusPinjaman.DITOLAK.value
        )

        print("✅ Riwayat pinjaman ditolak berhasil ditemukan")

        # Menu admin harus menerima pinjaman yang masih diajukan.
        seluruh_pengajuan = (
            PinjamanRepository.cari_semua_pengajuan()
        )

        id_seluruh_pengajuan = {
            pinjaman["id"]
            for pinjaman in seluruh_pengajuan
        }

        assert id_diajukan in id_seluruh_pengajuan, (
            "Pinjaman yang diajukan tidak ditemukan oleh menu admin"
        )

        assert all(
            pinjaman["status"] == StatusPinjaman.DIAJUKAN.value
            for pinjaman in seluruh_pengajuan
        ), (
            "Daftar pengajuan berisi status selain diajukan"
        )

        print("✅ Daftar pengajuan admin berhasil disaring")

        # Pencarian data yang tidak tersedia.
        hasil_id_kosong = (
            PinjamanRepository.cari_pinjaman_dengan_id(-999)
        )

        hasil_berjalan_kosong = (
            PinjamanRepository.cari_pinjaman_berjalan(
                "NIK-TIDAK-TERDAFTAR"
            )
        )

        hasil_riwayat_kosong = (
            PinjamanRepository.cari_riwayat_semua_pinjaman(
                "NIK-TIDAK-TERDAFTAR"
            )
        )

        assert hasil_id_kosong is None
        assert hasil_berjalan_kosong is None
        assert hasil_riwayat_kosong == []

        print("✅ Pencarian data tidak terdaftar menghasilkan data kosong")
        print("✅ Repository pinjaman bekerja sesuai rancangan")

    finally:
        bersihkan_data_uji()


if __name__ == "__main__":
    uji_repository_pinjaman()