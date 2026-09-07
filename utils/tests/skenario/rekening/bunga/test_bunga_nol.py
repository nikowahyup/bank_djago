"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pemberian_bunga.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.bunga_service import (
    BungaService
)
from bank_djago.utils.utility import Utilitas


NOREK_PENGUJIAN = "4001701216150609"


def ambil_snapshot(norek):
    """
    Mengambil kondisi rekening dan menghitung seluruh pencatatan
    bunga milik rekening pengujian.
    """
    koneksi = buat_koneksi()

    try:
        rekening = RekeningRepository.cari_rekening_dengan_norek(
            norek=norek,
            koneksi=koneksi
        )

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'bunga_tabungan'
              AND norek_tujuan = ?
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
              AND jenis = 'bunga bulanan'
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
              AND jenis = 'dapat bunga'
            """,
            (norek,)
        ).fetchone()["jumlah"]

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# Memuat rekening pengujian sebagai objek Python.
koneksi = buat_koneksi()

try:
    rekening = RekeningLoader.muat_rekening(
        norek=NOREK_PENGUJIAN,
        koneksi=koneksi
    )
finally:
    koneksi.close()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )

if rekening.status == "tutup":
    raise AssertionError(
        "Rekening pengujian sudah ditutup"
    )

# Pengujian ini memang membutuhkan rekening bersaldo nol.
assert rekening.saldo == 0, (
    f"Saldo rekening Rp{Utilitas.format_rupiah(rekening.saldo)}, "
    "bukan Rp0"
)


# Menyimpan keadaan sebelum service dijalankan.
sebelum = ambil_snapshot(NOREK_PENGUJIAN)
data_sebelum = sebelum["rekening"]

periode_sebelum = datetime.date.fromisoformat(
    data_sebelum["dapat_bunga"]
)

# Membuat tepat satu periode bunga yang harus diproses.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    1
)

jumlah_riwayat_objek_sebelum = len(rekening.riwayat)


print("=== KONDISI SEBELUM PEMBERIAN BUNGA NOL ===")
print("Nomor rekening   :", rekening.norek)
print(
    "Saldo            :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Bunga tahunan    :",
    f"{rekening.bunga * 100:.1f}%"
)
print("Periode terakhir :", periode_sebelum)
print("Hari simulasi     :", hari_simulasi)
print("Jumlah transaksi :", sebelum["jumlah_transaksi"])
print("Jumlah riwayat   :", sebelum["jumlah_riwayat"])
print("Jumlah audit     :", sebelum["jumlah_audit"])
print()


# Menjalankan service. Karena saldo nol, hasil bunga harus nol.
hasil = BungaService.berikan_bunga(
    rekening=rekening,
    hari_ini=hari_simulasi
)

setelah = ambil_snapshot(NOREK_PENGUJIAN)
data_setelah = setelah["rekening"]

periode_setelah = datetime.date.fromisoformat(
    data_setelah["dapat_bunga"]
)


print("=== KONDISI SETELAH PEMBERIAN BUNGA NOL ===")
print(
    "Hasil bunga      :",
    f"Rp{Utilitas.format_rupiah(hasil)}"
)
print(
    "Saldo SQLite     :",
    f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
)
print(
    "Saldo objek      :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print("Periode SQLite   :", periode_setelah)
print("Periode objek    :", rekening.dapat_bunga)
print("Jumlah transaksi :", setelah["jumlah_transaksi"])
print("Jumlah riwayat   :", setelah["jumlah_riwayat"])
print("Jumlah audit     :", setelah["jumlah_audit"])
print()


# Tidak ada bunga yang dihasilkan.
assert hasil == 0, (
    "Rekening bersaldo nol masih menghasilkan bunga"
)

# Saldo SQLite dan objek Python harus tetap nol.
assert data_setelah["saldo"] == 0, (
    "Saldo SQLite berubah setelah bunga nol"
)

assert rekening.saldo == 0, (
    "Saldo objek Python berubah setelah bunga nol"
)

# Walaupun nominalnya nol, periode tetap harus dianggap selesai.
assert periode_setelah == hari_simulasi, (
    "Periode bunga SQLite tidak diperbarui"
)

assert rekening.dapat_bunga == hari_simulasi, (
    "Periode bunga objek Python tidak diperbarui"
)

# Tidak boleh ada transaksi bernominal nol.
assert (
    setelah["jumlah_transaksi"]
    == sebelum["jumlah_transaksi"]
), "Transaksi bunga nol masih dibuat"

# Karena tidak ada transaksi, riwayat dan audit juga tidak dibuat.
assert (
    setelah["jumlah_riwayat"]
    == sebelum["jumlah_riwayat"]
), "Riwayat bunga nol masih dibuat"

assert (
    setelah["jumlah_audit"]
    == sebelum["jumlah_audit"]
), "Audit bunga nol masih dibuat"

assert (
    len(rekening.riwayat)
    == jumlah_riwayat_objek_sebelum
), "Riwayat bunga nol masih dimasukkan ke objek Python"


# Panggilan kedua pada tanggal yang sama juga tidak boleh
# menghasilkan perubahan apa pun.
hasil_kedua = BungaService.berikan_bunga(
    rekening=rekening,
    hari_ini=hari_simulasi
)

setelah_pemanggilan_kedua = ambil_snapshot(
    NOREK_PENGUJIAN
)

assert hasil_kedua == 0, (
    "Pemanggilan kedua masih menghasilkan bunga"
)

assert setelah_pemanggilan_kedua == setelah, (
    "Pemanggilan kedua mengubah data SQLite"
)

assert rekening.saldo == 0, (
    "Pemanggilan kedua mengubah saldo objek"
)

assert rekening.dapat_bunga == hari_simulasi, (
    "Pemanggilan kedua mengubah periode objek"
)


print(
    "✅ BUNGA NOL BERHASIL DITANGANI: "
    "saldo tetap Rp0, periode tetap diperbarui, "
    "transaksi nol tidak dibuat, serta pemanggilan "
    "kedua tidak mengubah data"
)
