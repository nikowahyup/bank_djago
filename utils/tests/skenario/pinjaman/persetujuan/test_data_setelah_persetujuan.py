"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 7).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import StatusPinjaman


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"

NOMINAL_PENGUJIAN = 1_000_000
BUNGA_PENGUJIAN = 0.10
TENOR_PENGUJIAN = 6


koneksi = buat_koneksi()

try:
    # Mengambil data pinjaman langsung dari SQLite.
    data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
        ID_PINJAMAN,
        koneksi
    )

    if data_pinjaman is None:
        raise AssertionError(
            f"Pinjaman ID {ID_PINJAMAN} tidak ditemukan"
        )

    # Mengambil rekening yang terhubung dengan pinjaman.
    # Data rekening dibutuhkan untuk memeriksa pemilik dan mencatat
    # saldo awal sebelum pencairan dilakukan.
    data_rekening = RekeningRepository.cari_rekening_dengan_norek(
        data_pinjaman["norek"],
        koneksi
    )

    if data_rekening is None:
        raise AssertionError(
            "Rekening yang terhubung dengan pinjaman tidak ditemukan"
        )

    print("=== DATA PINJAMAN SETELAH PERSETUJUAN ===")
    print("ID pinjaman       :", data_pinjaman["id"])
    print("Nomor rekening    :", data_pinjaman["norek"])
    print("Nominal pinjaman  :", data_pinjaman["nominal_pinjaman"])
    print("Bunga             :", data_pinjaman["bunga"])
    print("Tenor             :", data_pinjaman["tenor"])
    print("Cicilan tetap     :", data_pinjaman["cicilan_tetap"])
    print("Sisa pokok        :", data_pinjaman["sisa_pokok"])
    print("Cicilan terbayar  :", data_pinjaman["cicilan_terbayar"])
    print("Status            :", data_pinjaman["status"])
    print("Tanggal pencairan :", data_pinjaman["tanggal_pencairan"])
    print("Jatuh tempo       :", data_pinjaman["tanggal_jatuh_tempo"])
    print()

    print("=== DATA REKENING TUJUAN ===")
    print("Nomor rekening :", data_rekening["norek"])
    print("NIK pemilik    :", data_rekening["nik_pemilik"])
    print("Saldo awal     :", data_rekening["saldo"])
    print("Status         :", data_rekening["status"])
    print()

    # Memastikan pinjaman yang ditemukan adalah pinjaman pengujian.
    assert data_pinjaman["id"] == ID_PINJAMAN, (
        "ID pinjaman tidak sesuai"
    )

    assert data_pinjaman["norek"] == NOREK_PENGUJIAN, (
        "Pinjaman terhubung dengan rekening yang salah"
    )

    assert data_rekening["nik_pemilik"] == NIK_PENGUJIAN, (
        "Rekening pinjaman dimiliki nasabah yang berbeda"
    )

    assert data_pinjaman["nominal_pinjaman"] == NOMINAL_PENGUJIAN, (
        "Nominal pinjaman bukan Rp1.000.000"
    )

    # Float dibandingkan menggunakan toleransi kecil agar tidak
    # terganggu oleh cara komputer menyimpan angka pecahan.
    assert abs(data_pinjaman["bunga"] - BUNGA_PENGUJIAN) < 1e-9, (
        "Bunga pinjaman bukan 10% per tahun"
    )

    assert data_pinjaman["tenor"] == TENOR_PENGUJIAN, (
        "Tenor pinjaman bukan enam bulan"
    )

    assert (
        data_pinjaman["status"]
        == StatusPinjaman.DISETUJUI.value
    ), "Pinjaman belum berstatus disetujui"

    # Sebelum pencairan, jadwal pembayaran seharusnya belum dibentuk.
    assert data_pinjaman["cicilan_tetap"] == 0, (
        "Cicilan tetap sudah terisi sebelum pencairan"
    )

    assert data_pinjaman["cicilan_terbayar"] == 0, (
        "Pinjaman sudah mempunyai cicilan terbayar"
    )

    assert data_pinjaman["tanggal_pencairan"] is None, (
        "Tanggal pencairan sudah terisi"
    )

    assert data_pinjaman["tanggal_jatuh_tempo"] is None, (
        "Tanggal jatuh tempo sudah terisi"
    )

    assert data_rekening["status"] == "aktif", (
        "Rekening tujuan tidak berstatus aktif"
    )

    print(
        "✅ Pinjaman ID 8 sudah disetujui dan siap diuji "
        "untuk pencairan"
    )

finally:
    koneksi.close()
