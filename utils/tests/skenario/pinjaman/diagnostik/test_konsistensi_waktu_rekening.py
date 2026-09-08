"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.txt` (urutan 5).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi


NOREK_PENGUJIAN = "3001781978899033"


# Mengambil waktu asli langsung dari SQLite
koneksi = buat_koneksi()

try:
    data_rekening = koneksi.execute(
        """
        SELECT waktu_dibuat
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

finally:
    koneksi.close()


if data_rekening is None:
    raise ValueError("Rekening pengujian tidak ditemukan")


waktu_sqlite = datetime.datetime.fromisoformat(
    data_rekening["waktu_dibuat"]
)


# Memuat rekening melalui loader
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


print("Waktu SQLite:", waktu_sqlite)
print("Waktu loader:", rekening.waktu_dibuat)


assert rekening.waktu_dibuat == waktu_sqlite

print("✅ Loader mempertahankan waktu_dibuat dari SQLite")
