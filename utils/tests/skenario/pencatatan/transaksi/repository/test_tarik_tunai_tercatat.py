"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_repo_transaksi.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NOREK_PENGUJIAN = "3001781978899033"
NOMINAL_TARIK = 10_000


koneksi = buat_koneksi()

try:
    data_rekening = koneksi.execute(
        """
        SELECT norek, saldo
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

    data_transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE norek_sumber = ?
          AND jenis = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            NOREK_PENGUJIAN,
            JenisTransaksi.TARIK_TUNAI.value
        )
    ).fetchone()

    data_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE norek = ?
          AND jenis = 'tarik uang'
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

    data_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE norek = ?
          AND jenis = 'tarik uang'
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

finally:
    koneksi.close()


if data_rekening is None:
    raise ValueError("Rekening pengujian tidak ditemukan")

if data_transaksi is None:
    raise ValueError("Transaksi tarik tunai tidak ditemukan")

if data_riwayat is None:
    raise ValueError("Riwayat tarik tunai tidak ditemukan")

if data_audit is None:
    raise ValueError("Audit tarik tunai tidak ditemukan")


print("HASIL PENGUJIAN TARIK TUNAI")
print("ID transaksi :", data_transaksi["id"])
print("Jenis        :", data_transaksi["jenis"])
print("Norek sumber :", data_transaksi["norek_sumber"])
print("Nominal      :", data_transaksi["nominal"])
print(
    "Saldo sebelum:",
    data_transaksi["saldo_sumber_sebelum"]
)
print(
    "Saldo sesudah:",
    data_transaksi["saldo_sumber_sesudah"]
)
print("Saldo SQLite :", data_rekening["saldo"])
print("Riwayat      :", data_riwayat["log"])
print("Audit        :", data_audit["log"])


# Memeriksa arah transaksi
assert data_transaksi["norek_sumber"] == NOREK_PENGUJIAN
assert data_transaksi["norek_tujuan"] is None
assert data_transaksi["saldo_tujuan_sebelum"] is None
assert data_transaksi["saldo_tujuan_sesudah"] is None

print("✅ Arah transaksi tarik tunai tersimpan benar")


# Memeriksa nominal dan biaya
assert data_transaksi["nominal"] == NOMINAL_TARIK
assert data_transaksi["biaya"] == 0

print("✅ Nominal dan biaya tersimpan benar")


# Memeriksa perhitungan snapshot
assert (
    data_transaksi["saldo_sumber_sesudah"]
    == data_transaksi["saldo_sumber_sebelum"]
    - data_transaksi["nominal"]
)

print("✅ Perubahan snapshot saldo sesuai nominal tarik")


# Memeriksa saldo terbaru SQLite
assert (
    data_rekening["saldo"]
    == data_transaksi["saldo_sumber_sesudah"]
)

print("✅ Saldo SQLite sama dengan snapshot akhir transaksi")


# Memeriksa format waktu
waktu_transaksi = datetime.datetime.fromisoformat(
    data_transaksi["waktu"]
)

assert isinstance(waktu_transaksi, datetime.datetime)

print("✅ Waktu transaksi tersimpan sebagai datetime ISO")


# Memeriksa riwayat dan audit
assert data_riwayat["jenis"] == "tarik uang"
assert data_audit["jenis"] == "tarik uang"

print("✅ Riwayat dan audit tarik tunai berhasil disimpan")


# Memeriksa loader
koneksi = buat_koneksi()

try:
    rekening = RekeningLoader.muat_rekening(
        norek=NOREK_PENGUJIAN,
        koneksi=koneksi
    )
finally:
    koneksi.close()


if rekening is None:
    raise ValueError("Loader gagal memuat rekening")


assert rekening.saldo == data_rekening["saldo"]

print("✅ Loader memulihkan saldo terbaru")


print(
    "\n✅ Tarik tunai tersimpan konsisten pada "
    "saldo, transaksi, riwayat, audit, dan loader"
)
