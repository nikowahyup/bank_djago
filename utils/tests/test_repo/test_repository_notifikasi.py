from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.notifikasi import Notifikasi
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.notifikasi_repository import (
    NotifikasiRepository
)
from bank_djago.utils.utility import JenisReferensi


def buat_notifikasi(
        jenis,
        pesan,
        jenis_referensi=None,
        id_objek=None
):
    # Membuat objek notifikasi untuk kebutuhan pengujian repository.
    notifikasi = Notifikasi(
        jenis=jenis,
        pesan=pesan,
        referensi_id=jenis_referensi
    )

    notifikasi.id_objek = id_objek

    return notifikasi


def hapus_data_pengujian(daftar_nik):
    # Menghapus notifikasi terlebih dahulu karena bergantung pada nasabah.
    koneksi = buat_koneksi()

    try:
        for nik in daftar_nik:
            koneksi.execute(
                """
                DELETE FROM notifikasi
                WHERE nik_pemilik = ?
                """,
                (nik,)
            )

        for nik in daftar_nik:
            koneksi.execute(
                """
                DELETE FROM nasabah
                WHERE nik = ?
                """,
                (nik,)
            )

        koneksi.commit()

    finally:
        koneksi.close()


def uji_repository_notifikasi():
    nik_pertama = "TEST-NOTIFIKASI-001"
    nik_kedua = "TEST-NOTIFIKASI-002"
    nik_tidak_terdaftar = "NIK-TIDAK-TERDAFTAR"

    daftar_nik = [
        nik_pertama,
        nik_kedua
    ]

    # Membersihkan sisa data jika pengujian pernah dijalankan sebelumnya.
    hapus_data_pengujian(daftar_nik)

    try:
        nasabah_pertama = Nasabahh(
            nama="Nasabah Notifikasi Pertama",
            alamat="Banyuwangi",
            nik=nik_pertama
        )

        nasabah_kedua = Nasabahh(
            nama="Nasabah Notifikasi Kedua",
            alamat="Malang",
            nik=nik_kedua
        )

        notifikasi_tanpa_pemilik = buat_notifikasi(
            jenis="deposito",
            pesan="Deposito pengujian telah jatuh tempo",
            jenis_referensi=JenisReferensi.DEPOSITO,
            id_objek=100
        )

        # Memastikan notifikasi tidak dapat memakai NIK yang belum terdaftar.
        hasil_gagal = NotifikasiRepository.tambah_notifikasi(
            nik_tidak_terdaftar,
            notifikasi_tanpa_pemilik
        )

        assert hasil_gagal is None, (
            "Notifikasi dengan NIK tidak terdaftar seharusnya ditolak"
        )

        print("✅ Notifikasi tanpa nasabah terdaftar berhasil ditolak")

        # Menyimpan dua nasabah sebagai induk data notifikasi.
        assert NasabahRepository.tambah_nasabah(nasabah_pertama), (
            "Nasabah pertama gagal disimpan"
        )

        assert NasabahRepository.tambah_nasabah(nasabah_kedua), (
            "Nasabah kedua gagal disimpan"
        )

        print("✅ Dua nasabah pengujian berhasil disimpan")

        # Nasabah pertama memiliki empat jenis notifikasi pengujian.
        deposito_target = buat_notifikasi(
            jenis="deposito",
            pesan="Deposito pertama telah jatuh tempo",
            jenis_referensi=JenisReferensi.DEPOSITO,
            id_objek=101
        )

        deposito_lain = buat_notifikasi(
            jenis="deposito",
            pesan="Deposito kedua akan segera jatuh tempo",
            jenis_referensi=JenisReferensi.DEPOSITO,
            id_objek=102
        )

        pinjaman = buat_notifikasi(
            jenis="pinjaman",
            pesan="Cicilan pinjaman telah jatuh tempo",
            jenis_referensi=JenisReferensi.PINJAMAN,
            id_objek=201
        )

        notifikasi_umum = buat_notifikasi(
            jenis="rekening",
            pesan="Selamat datang di Bank Djago",
            jenis_referensi=None,
            id_objek=None
        )

        # Nasabah kedua mempunyai referensi objek yang sama.
        # Ini digunakan untuk menguji pemisahan berdasarkan NIK.
        deposito_nasabah_kedua = buat_notifikasi(
            jenis="deposito",
            pesan="Deposito nasabah kedua telah jatuh tempo",
            jenis_referensi=JenisReferensi.DEPOSITO,
            id_objek=101
        )

        id_deposito_target = NotifikasiRepository.tambah_notifikasi(
            nik_pertama,
            deposito_target
        )

        id_deposito_lain = NotifikasiRepository.tambah_notifikasi(
            nik_pertama,
            deposito_lain
        )

        id_pinjaman = NotifikasiRepository.tambah_notifikasi(
            nik_pertama,
            pinjaman
        )

        id_notifikasi_umum = NotifikasiRepository.tambah_notifikasi(
            nik_pertama,
            notifikasi_umum
        )

        id_deposito_nasabah_kedua = (
            NotifikasiRepository.tambah_notifikasi(
                nik_kedua,
                deposito_nasabah_kedua
            )
        )

        seluruh_id = {
            id_deposito_target,
            id_deposito_lain,
            id_pinjaman,
            id_notifikasi_umum,
            id_deposito_nasabah_kedua
        }

        assert None not in seluruh_id, (
            "Ada notifikasi yang gagal disimpan"
        )

        print("✅ Lima notifikasi berhasil disimpan")

        assert len(seluruh_id) == 5, (
            "Setiap notifikasi seharusnya mempunyai ID global berbeda"
        )

        print("✅ Seluruh notifikasi mempunyai ID global berbeda")

        # Mencari satu notifikasi menggunakan ID global.
        hasil_id = NotifikasiRepository.cari_notifikasi_dengan_id(
            id_deposito_target
        )

        assert hasil_id is not None, (
            "Notifikasi tidak ditemukan berdasarkan ID"
        )

        assert hasil_id["id"] == id_deposito_target
        assert hasil_id["nik_pemilik"] == nik_pertama
        assert hasil_id["jenis"] == "deposito"
        assert (
            hasil_id["jenis_referensi"]
            == JenisReferensi.DEPOSITO.value
        )
        assert hasil_id["id_objek"] == 101

        print("✅ Pencarian notifikasi berdasarkan ID berhasil")

        # Memastikan setiap nasabah hanya memperoleh notifikasinya sendiri.
        notifikasi_pertama = (
            NotifikasiRepository.cari_notifikasi_nasabah(nik_pertama)
        )

        notifikasi_kedua = (
            NotifikasiRepository.cari_notifikasi_nasabah(nik_kedua)
        )

        assert len(notifikasi_pertama) == 4
        assert len(notifikasi_kedua) == 1

        assert all(
            item["nik_pemilik"] == nik_pertama
            for item in notifikasi_pertama
        )

        assert all(
            item["nik_pemilik"] == nik_kedua
            for item in notifikasi_kedua
        )

        print("✅ Notifikasi antar-nasabah berhasil dipisahkan")

        # Notifikasi umum diperbolehkan tidak mempunyai referensi objek.
        hasil_umum = NotifikasiRepository.cari_notifikasi_dengan_id(
            id_notifikasi_umum
        )

        assert hasil_umum is not None
        assert hasil_umum["jenis_referensi"] is None
        assert hasil_umum["id_objek"] is None

        print("✅ Notifikasi umum tanpa referensi berhasil disimpan")

        # Nasabah kedua tidak boleh menghapus notifikasi nasabah pertama.
        hapus_milik_orang_lain = (
            NotifikasiRepository.hapus_notifikasi_dengan_id(
                id_deposito_target,
                nik_kedua
            )
        )

        assert hapus_milik_orang_lain is False, (
            "Nasabah kedua tidak boleh menghapus notifikasi nasabah pertama"
        )

        assert (
            NotifikasiRepository.cari_notifikasi_dengan_id(
                id_deposito_target
            )
            is not None
        )

        print("✅ Penghapusan notifikasi milik nasabah lain berhasil ditolak")

        # Menghapus satu notifikasi deposito berdasarkan referensi objek.
        hapus_referensi = (
            NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                nik_pemilik=nik_pertama,
                jenis_referensi=JenisReferensi.DEPOSITO,
                id_objek=101
            )
        )

        assert hapus_referensi is True, (
            "Notifikasi deposito target gagal dihapus"
        )

        assert (
            NotifikasiRepository.cari_notifikasi_dengan_id(
                id_deposito_target
            )
            is None
        )

        # Deposito lain milik nasabah pertama harus tetap ada.
        assert (
            NotifikasiRepository.cari_notifikasi_dengan_id(
                id_deposito_lain
            )
            is not None
        )

        # Referensi yang sama milik nasabah kedua juga harus tetap ada.
        assert (
            NotifikasiRepository.cari_notifikasi_dengan_id(
                id_deposito_nasabah_kedua
            )
            is not None
        )

        print("✅ Penghapusan berdasarkan referensi berhasil diisolasi")

        # Menghapus notifikasi pinjaman berdasarkan ID global.
        hapus_pinjaman = (
            NotifikasiRepository.hapus_notifikasi_dengan_id(
                id_pinjaman,
                nik_pertama
            )
        )

        assert hapus_pinjaman is True
        assert (
            NotifikasiRepository.cari_notifikasi_dengan_id(id_pinjaman)
            is None
        )

        print("✅ Penghapusan notifikasi berdasarkan ID berhasil")

        # Menghapus ID yang tidak ada harus menghasilkan False.
        hapus_tidak_ada = (
            NotifikasiRepository.hapus_notifikasi_dengan_id(
                999_999_999,
                nik_pertama
            )
        )

        assert hapus_tidak_ada is False

        print("✅ Penghapusan ID tidak terdaftar menghasilkan False")

        # Saat ini tersisa deposito kedua dan notifikasi umum.
        sisa_pertama = (
            NotifikasiRepository.cari_notifikasi_nasabah(nik_pertama)
        )

        assert len(sisa_pertama) == 2

        jumlah_dihapus = (
            NotifikasiRepository.hapus_semua_notifikasi_nasabah(
                nik_pertama
            )
        )

        assert jumlah_dihapus == 2

        assert (
            NotifikasiRepository.cari_notifikasi_nasabah(nik_pertama)
            == []
        )

        # Penghapusan semua milik nasabah pertama tidak boleh
        # memengaruhi notifikasi nasabah kedua.
        sisa_kedua = (
            NotifikasiRepository.cari_notifikasi_nasabah(nik_kedua)
        )

        assert len(sisa_kedua) == 1
        assert (
            sisa_kedua[0]["id"]
            == id_deposito_nasabah_kedua
        )

        print("✅ Penghapusan seluruh notifikasi berhasil diisolasi")

        # Pencarian nasabah tidak terdaftar menghasilkan list kosong.
        hasil_tidak_ada = (
            NotifikasiRepository.cari_notifikasi_nasabah(
                nik_tidak_terdaftar
            )
        )

        assert hasil_tidak_ada == []

        assert (
            NotifikasiRepository.cari_notifikasi_dengan_id(
                999_999_999
            )
            is None
        )

        print("✅ Pencarian data tidak terdaftar menghasilkan data kosong")
        print("✅ Repository notifikasi bekerja sesuai rancangan")

    finally:
        # Data tetap dibersihkan apabila salah satu assert gagal.
        hapus_data_pengujian(daftar_nik)


if __name__ == "__main__":
    uji_repository_notifikasi()