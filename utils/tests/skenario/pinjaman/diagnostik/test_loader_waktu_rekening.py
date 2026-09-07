"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 4).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from datetime import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.sqlite.database import buat_koneksi


NOREK_PENGUJIAN = "3001781978899033"

koneksi = buat_koneksi()
rekening = RekeningLoader.muat_rekening(
    NOREK_PENGUJIAN,
koneksi)

if rekening is None:
    raise ValueError("Rekening gagal dimuat")


print("HASIL PENGUJIAN LOADER")
print("Norek        :", rekening.norek)
print("Waktu dibuat :", rekening.waktu_dibuat)
print("Tipe data    :", type(rekening.waktu_dibuat))


assert isinstance(rekening.waktu_dibuat, datetime)

print("✅ Loader memulihkan waktu_dibuat sebagai datetime")
