from bank_djago.core.nasabah import Nasabahh
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi


NIK_PENGUJIAN = "NIK-SQLITE-TEST"


def bersihkan_data_pengujian():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            DELETE FROM nasabah
            WHERE nik = ?
        """, (NIK_PENGUJIAN,))

        koneksi.commit()

    finally:
        koneksi.close()


def uji_repository_nasabah():
    # Memastikan tidak ada data lama dari pengujian sebelumnya.
    bersihkan_data_pengujian()

    try:
        nasabah = Nasabahh(
            nama="niko wahyu pratama",
            alamat="Banyuwangi",
            nik=NIK_PENGUJIAN
        )

        # Menguji penyimpanan nasabah.
        berhasil = NasabahRepository.tambah_nasabah(nasabah)

        assert berhasil is True, (
            "Nasabah valid seharusnya berhasil disimpan"
        )

        print("✅ Nasabah berhasil disimpan")

        # Menguji pencarian kembali berdasarkan NIK.
        hasil = NasabahRepository.cari_nasabah_dengan_nik(
            NIK_PENGUJIAN
        )

        assert hasil is not None, (
            "Nasabah yang telah disimpan seharusnya ditemukan"
        )

        assert hasil["nik"] == nasabah.NIK
        assert hasil["nama"] == nasabah.nama
        assert hasil["alamat"] == nasabah.alamat

        print("✅ Data nasabah yang ditemukan sesuai objek awal")

        # Menguji pencarian NIK yang tidak terdaftar.
        tidak_ditemukan = (
            NasabahRepository.cari_nasabah_dengan_nik(
                "NIK-TIDAK-TERDAFTAR"
            )
        )

        assert tidak_ditemukan is None, (
            "Pencarian NIK asing seharusnya menghasilkan None"
        )

        print("✅ Pencarian NIK tidak terdaftar menghasilkan None")

        # Menguji perlindungan primary key.
        duplikat = NasabahRepository.tambah_nasabah(nasabah)

        assert duplikat is False, (
            "NIK yang sama seharusnya ditolak"
        )

        print("✅ NIK duplikat berhasil ditolak")
        print("✅ Repository nasabah bekerja sesuai rancangan")

    finally:
        # Menghapus hanya nasabah khusus pengujian.
        bersihkan_data_pengujian()


if __name__ == "__main__":
    uji_repository_nasabah()