"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 16).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot():
    """
    Mengambil kondisi database untuk memastikan pembayaran
    setelah lunas tidak meninggalkan perubahan.
    """
    koneksi = buat_koneksi()

    try:
        pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            ID_PINJAMAN,
            koneksi
        )

        rekening = RekeningRepository.cari_rekening_dengan_norek(
            NOREK_PENGUJIAN,
            koneksi
        )

        jumlah_transaksi = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM transaksi"
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM riwayat"
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM audit"
        ).fetchone()["jumlah"]

        jumlah_pembayaran = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'pembayaran_cicilan'
              AND jenis_referensi = 'pinjaman'
              AND id_referensi = ?
            """,
            (ID_PINJAMAN,)
        ).fetchone()["jumlah"]

        return {
            "pinjaman": dict(pinjaman),
            "rekening": dict(rekening),
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "jumlah_pembayaran": jumlah_pembayaran
        }

    finally:
        koneksi.close()


# Memuat nasabah karena service tetap membutuhkan konteks pemilik.
nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)

if nasabah is None:
    raise AssertionError("Nasabah pengujian tidak ditemukan")


snapshot_sebelum = ambil_snapshot()

assert snapshot_sebelum["pinjaman"]["status"] == "lunas", (
    "Pinjaman ID 8 belum berstatus lunas"
)

assert snapshot_sebelum["pinjaman"]["cicilan_terbayar"] == 6, (
    "Jumlah cicilan terbayar bukan enam"
)

assert snapshot_sebelum["pinjaman"]["sisa_pokok"] == 0, (
    "Sisa pokok pinjaman belum nol"
)


print("=== KONDISI SEBELUM PERCOBAAN PEMBAYARAN KETUJUH ===")
print("Status            :", snapshot_sebelum["pinjaman"]["status"])
print(
    "Cicilan terbayar :",
    snapshot_sebelum["pinjaman"]["cicilan_terbayar"]
)
print("Sisa pokok        :", snapshot_sebelum["pinjaman"]["sisa_pokok"])
print("Saldo rekening    :", snapshot_sebelum["rekening"]["saldo"])
print("Jumlah pembayaran :", snapshot_sebelum["jumlah_pembayaran"])
print()


# Service seharusnya berhenti saat menemukan status bukan 'aktif'.
try:
    PinjamanService.bayar_cicilan(
        id_pinjaman=ID_PINJAMAN,
        nasabah=nasabah
    )

except ValueError as error:
    assert str(error) == "Pinjaman sedang tidak aktif", (
        f"Pembayaran ditolak karena alasan berbeda: {error}"
    )

    print("✅ Pembayaran ketujuh berhasil ditolak")
    print("Pesan error:", error)

else:
    raise AssertionError(
        "Pinjaman yang sudah lunas masih dapat dibayar"
    )


snapshot_setelah = ambil_snapshot()


# Memastikan tidak ada data yang berubah.
assert (
    snapshot_setelah["pinjaman"]
    == snapshot_sebelum["pinjaman"]
), "Data pinjaman berubah"

assert (
    snapshot_setelah["rekening"]
    == snapshot_sebelum["rekening"]
), "Data rekening berubah"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi baru muncul"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat baru muncul"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Audit baru muncul"

assert (
    snapshot_setelah["jumlah_pembayaran"]
    == snapshot_sebelum["jumlah_pembayaran"]
), "Jumlah pembayaran berubah"


print()
print(
    "✅ PEMBAYARAN SETELAH LUNAS BERHASIL DITOLAK "
    "DAN SELURUH DATA TETAP SAMA"
)
