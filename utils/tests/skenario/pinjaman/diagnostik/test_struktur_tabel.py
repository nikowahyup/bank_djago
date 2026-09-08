"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.txt` (urutan 2).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi

koneksi = buat_koneksi()

try:
    daftar_kolom = koneksi.execute(
        "PRAGMA table_info(rekening)"
    ).fetchall()

    for kolom in daftar_kolom:
        print(kolom["name"], kolom["type"])

finally:
    koneksi.close()
