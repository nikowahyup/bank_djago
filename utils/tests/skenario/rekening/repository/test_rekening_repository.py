import datetime

from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.rekening import RekeningReguler
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)


NIK_UJI = "TEST-REKENING-001"
NOREK_UJI = "REK-TEST-001"


def bersihkan_data_uji():
    # Rekening harus dihapus lebih dahulu karena memiliki
    # foreign key yang mengarah kepada nasabah.
    koneksi = buat_koneksi()

    try:
        koneksi.execute(
            "DELETE FROM rekening WHERE norek = ?",
            (NOREK_UJI,)
        )

        koneksi.execute(
            "DELETE FROM nasabah WHERE nik = ?",
            (NIK_UJI,)
        )

        koneksi.commit()

    finally:
        koneksi.close()


def buat_data_uji():
    # Membuat nasabah khusus untuk pengujian repository.
    nasabah = Nasabahh(
        nama="Nasabah Pengujian",
        alamat="Banyuwangi",
        nik=NIK_UJI
    )

    # Membuat rekening yang dimiliki nasabah pengujian.
    rekening = RekeningReguler(
        norek=NOREK_UJI,
        pin="123456",
        pemilik=nasabah
    )

    # Menentukan state agar hasil penyimpanan dapat diperiksa
    # menggunakan nilai yang sudah diketahui.
    rekening.set_saldo(10_000_000)
    rekening.limit_sisa = 2_500_000
    rekening.status = "aktif"

    rekening.reset = datetime.date(2026, 8, 23)
    rekening.dapat_bunga = datetime.date(2026, 9, 23)
    rekening.waktu_bayar_admin = datetime.date(2026, 9, 23)
    rekening.terakhir_ubah_rekening = datetime.date(2026, 8, 24)
    rekening.alasan_blokir = None

    return nasabah, rekening


def uji_repository_rekening():
    # Memastikan hasil tes lama tidak mengganggu tes sekarang.
    bersihkan_data_uji()

    nasabah, rekening = buat_data_uji()

    try:
        # Rekening tidak boleh disimpan sebelum pemiliknya
        # terdaftar pada tabel nasabah.
        hasil_tanpa_pemilik = (
            RekeningRepository.tambah_rekening(rekening)
        )

        assert hasil_tanpa_pemilik is False, (
            "Rekening tanpa nasabah terdaftar seharusnya ditolak"
        )

        print("✅ Rekening tanpa pemilik terdaftar berhasil ditolak")

        # Menyimpan nasabah terlebih dahulu agar foreign key
        # pada rekening mempunyai data induk yang valid.
        hasil_nasabah = NasabahRepository.tambah_nasabah(nasabah)

        assert hasil_nasabah is True, (
            "Nasabah pemilik rekening gagal disimpan"
        )

        print("✅ Nasabah pemilik berhasil disimpan")

        # Menyimpan rekening setelah nasabah tersedia.
        hasil_rekening = RekeningRepository.tambah_rekening(rekening)

        assert hasil_rekening is True, (
            "Rekening valid gagal disimpan"
        )

        print("✅ Rekening valid berhasil disimpan")

        # Mengambil kembali rekening yang sudah tersimpan.
        data_rekening = (
            RekeningRepository.cari_rekening_dengan_norek(
                NOREK_UJI
            )
        )

        assert data_rekening is not None, (
            "Rekening yang sudah disimpan tidak ditemukan"
        )

        # Memeriksa identitas dan state utama rekening.
        assert data_rekening["norek"] == NOREK_UJI
        assert data_rekening["nik_pemilik"] == NIK_UJI
        assert data_rekening["pin"] == rekening.pin
        assert data_rekening["saldo"] == rekening.saldo
        assert data_rekening["level"] == rekening.level
        assert data_rekening["status"] == rekening.status
        assert data_rekening["limit_sisa"] == rekening.limit_sisa

        # Atribut date disimpan sebagai TEXT dalam format ISO.
        assert data_rekening["reset"] == rekening.reset.isoformat()

        assert (
            data_rekening["dapat_bunga"]
            == rekening.dapat_bunga.isoformat()
        )

        assert (
            data_rekening["waktu_bayar_admin"]
            == rekening.waktu_bayar_admin.isoformat()
        )

        assert (
            data_rekening["terakhir_ubah_rekening"]
            == rekening.terakhir_ubah_rekening.isoformat()
        )

        assert (
            data_rekening["alasan_blokir"]
            == rekening.alasan_blokir
        )

        print("✅ Data rekening yang ditemukan sesuai objek awal")

        # Primary key harus mencegah nomor rekening yang sama
        # disimpan untuk kedua kalinya.
        hasil_duplikat = RekeningRepository.tambah_rekening(
            rekening
        )

        assert hasil_duplikat is False, (
            "Nomor rekening duplikat seharusnya ditolak"
        )

        print("✅ Nomor rekening duplikat berhasil ditolak")

        # Nomor rekening yang tidak terdaftar harus
        # menghasilkan None.
        rekening_tidak_ada = (
            RekeningRepository.cari_rekening_dengan_norek(
                "REK-TIDAK-TERDAFTAR"
            )
        )

        assert rekening_tidak_ada is None, (
            "Pencarian rekening tidak terdaftar seharusnya menghasilkan None"
        )

        print("✅ Pencarian rekening tidak terdaftar menghasilkan None")
        print("✅ Repository rekening bekerja sesuai rancangan")

    finally:
        # Data pengujian tetap dibersihkan jika salah satu assert gagal.
        bersihkan_data_uji()


if __name__ == "__main__":
    uji_repository_rekening()