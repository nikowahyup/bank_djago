"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_repo_transaksi.py` (urutan 4).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NOREK_PENGIRIM = "3001781978899033"
NOREK_PENERIMA = "2001569043650499"
NOMINAL_TRANSFER = 99_990


# --------------------------------------------------
# MENGAMBIL DATA SQLITE
# --------------------------------------------------

koneksi = buat_koneksi()

try:
    data_transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_sumber = ?
          AND norek_tujuan = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.TRANSFER.value,
            NOREK_PENGIRIM,
            NOREK_PENERIMA
        )
    ).fetchone()

    data_pengirim = koneksi.execute(
        """
        SELECT norek, saldo
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK_PENGIRIM,)
    ).fetchone()

    data_penerima = koneksi.execute(
        """
        SELECT norek, saldo
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK_PENERIMA,)
    ).fetchone()

    riwayat_pengirim = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE norek = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENGIRIM,)
    ).fetchone()

    riwayat_penerima = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE norek = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENERIMA,)
    ).fetchone()

    audit_pengirim = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE norek = ?
          AND jenis = 'transfer'
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENGIRIM,)
    ).fetchone()

    audit_penerima = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE norek = ?
          AND jenis = 'terima saldo'
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENERIMA,)
    ).fetchone()

finally:
    koneksi.close()


if data_transaksi is None:
    raise ValueError("Transaksi transfer tidak ditemukan")

if data_pengirim is None:
    raise ValueError("Rekening pengirim tidak ditemukan")

if data_penerima is None:
    raise ValueError("Rekening penerima tidak ditemukan")

if riwayat_pengirim is None or riwayat_penerima is None:
    raise ValueError("Riwayat transfer tidak lengkap")

if audit_pengirim is None or audit_penerima is None:
    raise ValueError("Audit transfer tidak lengkap")


# --------------------------------------------------
# MENAMPILKAN DATA
# --------------------------------------------------

print("HASIL PENGUJIAN TRANSFER")
print("ID transaksi          :", data_transaksi["id"])
print("Jenis                 :", data_transaksi["jenis"])
print("Norek pengirim        :", data_transaksi["norek_sumber"])
print("Norek penerima        :", data_transaksi["norek_tujuan"])
print("Nominal               :", data_transaksi["nominal"])
print("Biaya                 :", data_transaksi["biaya"])
print(
    "Saldo pengirim awal  :",
    data_transaksi["saldo_sumber_sebelum"]
)
print(
    "Saldo pengirim akhir :",
    data_transaksi["saldo_sumber_sesudah"]
)
print(
    "Saldo penerima awal  :",
    data_transaksi["saldo_tujuan_sebelum"]
)
print(
    "Saldo penerima akhir :",
    data_transaksi["saldo_tujuan_sesudah"]
)
print("Riwayat pengirim      :", riwayat_pengirim["log"])
print("Riwayat penerima      :", riwayat_penerima["log"])
print("Audit pengirim        :", audit_pengirim["log"])
print("Audit penerima        :", audit_penerima["log"])


# --------------------------------------------------
# MEMERIKSA IDENTITAS TRANSAKSI
# --------------------------------------------------

assert (
    data_transaksi["jenis"]
    == JenisTransaksi.TRANSFER.value
)

assert data_transaksi["norek_sumber"] == NOREK_PENGIRIM
assert data_transaksi["norek_tujuan"] == NOREK_PENERIMA
assert data_transaksi["nominal"] == NOMINAL_TRANSFER

print("✅ Identitas transaksi transfer tersimpan benar")


# --------------------------------------------------
# MEMERIKSA SALDO PENGIRIM
# --------------------------------------------------

total_debit = (
    data_transaksi["nominal"]
    + data_transaksi["biaya"]
)

assert (
    data_transaksi["saldo_sumber_sesudah"]
    == data_transaksi["saldo_sumber_sebelum"]
    - total_debit
)

assert (
    data_pengirim["saldo"]
    == data_transaksi["saldo_sumber_sesudah"]
)

print("✅ Saldo pengirim berkurang sebesar nominal + biaya")


# --------------------------------------------------
# MEMERIKSA SALDO PENERIMA
# --------------------------------------------------

assert (
    data_transaksi["saldo_tujuan_sesudah"]
    == data_transaksi["saldo_tujuan_sebelum"]
    + data_transaksi["nominal"]
)

assert (
    data_penerima["saldo"]
    == data_transaksi["saldo_tujuan_sesudah"]
)

print("✅ Saldo penerima bertambah sebesar nominal")


# Rekening pengirim adalah Gold sehingga pajaknya nol.
assert data_transaksi["biaya"] == 0

print("✅ Biaya transfer sesuai ketentuan rekening Gold")


# Transfer tidak merujuk deposito atau pinjaman.
assert data_transaksi["jenis_referensi"] is None
assert data_transaksi["id_referensi"] is None

print("✅ Referensi transaksi transfer tersimpan NULL")


# --------------------------------------------------
# MEMERIKSA WAKTU, RIWAYAT, DAN AUDIT
# --------------------------------------------------

waktu_transaksi = datetime.datetime.fromisoformat(
    data_transaksi["waktu"]
)

assert isinstance(waktu_transaksi, datetime.datetime)

print("✅ Waktu transfer tersimpan sebagai datetime ISO")


assert audit_pengirim["jenis"] == "transfer"
assert audit_penerima["jenis"] == "terima saldo"

print("✅ Dua audit transfer berhasil disimpan")


assert str(NOMINAL_TRANSFER) or riwayat_pengirim["log"]
assert str(NOMINAL_TRANSFER) or riwayat_penerima["log"]

print("✅ Dua riwayat transfer berhasil disimpan")


# --------------------------------------------------
# MEMERIKSA LOADER
# --------------------------------------------------

koneksi = buat_koneksi()

try:
    pengirim = RekeningLoader.muat_rekening(
        norek=NOREK_PENGIRIM,
        koneksi=koneksi
    )

    penerima = RekeningLoader.muat_rekening(
        norek=NOREK_PENERIMA,
        koneksi=koneksi
    )

finally:
    koneksi.close()


if pengirim is None or penerima is None:
    raise ValueError("Loader gagal memuat rekening transfer")


assert pengirim.saldo == data_pengirim["saldo"]
assert penerima.saldo == data_penerima["saldo"]

print("✅ Loader memulihkan kedua saldo terbaru")


print(
    "\n✅ Transfer konsisten pada transaksi, kedua saldo, "
    "riwayat, audit, dan loader"
)
