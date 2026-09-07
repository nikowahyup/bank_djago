"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_repo_transaksi.py` (urutan 7).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NIK_PENGUJIAN = "5555666677778888"
NOREK_PENGUJIAN = "2001842427316253"
SETOR_AWAL = 100_000_000


# --------------------------------------------------
# MENGAMBIL DATA SQLITE
# --------------------------------------------------

koneksi = buat_koneksi()

try:
    data_rekening = koneksi.execute(
        """
        SELECT *
        FROM rekening
        WHERE norek = ?
          AND nik_pemilik = ?
        """,
        (
            NOREK_PENGUJIAN,
            NIK_PENGUJIAN
        )
    ).fetchone()

    data_transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_tujuan = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.SETOR_AWAL.value,
            NOREK_PENGUJIAN
        )
    ).fetchone()

    if data_transaksi is None:
        raise ValueError(
            "Transaksi setor awal tidak ditemukan"
        )

    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (data_transaksi["id"],)
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (data_transaksi["id"],)
    ).fetchall()

finally:
    koneksi.close()


if data_rekening is None:
    raise ValueError("Rekening baru tidak ditemukan")


print("HASIL PENGUJIAN SETOR AWAL")
print("NIK                :", data_rekening["nik_pemilik"])
print("Norek              :", data_rekening["norek"])
print("Level              :", data_rekening["level"])
print("Saldo              :", data_rekening["saldo"])
print("Waktu dibuat       :", data_rekening["waktu_dibuat"])
print("ID transaksi       :", data_transaksi["id"])
print("Jenis transaksi    :", data_transaksi["jenis"])
print("Saldo awal tercatat:", data_transaksi["saldo_tujuan_sebelum"])
print("Saldo akhir tercatat:", data_transaksi["saldo_tujuan_sesudah"])
print("Jumlah riwayat     :", len(daftar_riwayat))
print("Jumlah audit       :", len(daftar_audit))

for riwayat in daftar_riwayat:
    print("Riwayat:", riwayat["log"])

for audit in daftar_audit:
    print("Audit:", audit["log"])


# --------------------------------------------------
# MEMERIKSA REKENING
# --------------------------------------------------

assert data_rekening["nik_pemilik"] == NIK_PENGUJIAN
assert data_rekening["norek"] == NOREK_PENGUJIAN
assert data_rekening["saldo"] == SETOR_AWAL
assert data_rekening["status"] == "aktif"

print("✅ Rekening baru dan saldo awal tersimpan benar")


waktu_dibuat = datetime.datetime.fromisoformat(
    data_rekening["waktu_dibuat"]
)

assert isinstance(waktu_dibuat, datetime.datetime)

print("✅ Waktu pembukaan tersimpan sebagai datetime ISO")


# --------------------------------------------------
# MEMERIKSA TRANSAKSI SETOR AWAL
# --------------------------------------------------

assert (
    data_transaksi["jenis"]
    == JenisTransaksi.SETOR_AWAL.value
)

assert data_transaksi["norek_sumber"] is None
assert data_transaksi["norek_tujuan"] == NOREK_PENGUJIAN
assert data_transaksi["nominal"] == SETOR_AWAL
assert data_transaksi["biaya"] == 0

print("✅ Identitas transaksi setor awal tersimpan benar")


assert data_transaksi["saldo_sumber_sebelum"] is None
assert data_transaksi["saldo_sumber_sesudah"] is None
assert data_transaksi["saldo_tujuan_sebelum"] == 0
assert data_transaksi["saldo_tujuan_sesudah"] == SETOR_AWAL

print("✅ Snapshot setor awal tercatat dari 0 ke Rp100 juta")


assert (
    data_rekening["saldo"]
    == data_transaksi["saldo_tujuan_sesudah"]
)

print("✅ Saldo rekening sama dengan snapshot akhir")


assert data_transaksi["jenis_referensi"] is None
assert data_transaksi["id_referensi"] is None

print("✅ Referensi deposito/pinjaman tersimpan NULL")


# --------------------------------------------------
# MEMERIKSA RIWAYAT DAN AUDIT
# --------------------------------------------------

assert len(daftar_riwayat) == 1
assert len(daftar_audit) == 1

riwayat = daftar_riwayat[0]
audit = daftar_audit[0]

assert riwayat["transaksi_id"] == data_transaksi["id"]
assert audit["transaksi_id"] == data_transaksi["id"]

assert riwayat["norek"] == NOREK_PENGUJIAN
assert audit["norek"] == NOREK_PENGUJIAN
assert audit["nik"] == NIK_PENGUJIAN

assert riwayat["jenis"] == "setor awal"
assert audit["jenis"] == "pembukaan"

print(
    "✅ Riwayat dan audit terhubung ke transaksi "
    "setor awal yang sama"
)


# --------------------------------------------------
# MEMERIKSA LOADER
# --------------------------------------------------

koneksi = buat_koneksi()

try:
    rekening = RekeningLoader.muat_rekening(
        norek=NOREK_PENGUJIAN,
        koneksi=koneksi
    )
finally:
    koneksi.close()


if rekening is None:
    raise ValueError("Loader gagal memuat rekening baru")


assert rekening.norek == NOREK_PENGUJIAN
assert rekening.pemilik.NIK == NIK_PENGUJIAN
assert rekening.saldo == SETOR_AWAL
assert rekening.waktu_dibuat == waktu_dibuat

print("✅ Loader memulihkan rekening dan waktu pembukaan")


print(
    "\n✅ Pembukaan rekening dan transaksi SETOR_AWAL "
    "tersimpan secara konsisten"
)
