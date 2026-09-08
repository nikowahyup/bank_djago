"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.txt` (urutan 9).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)


NIK_PENGUJIAN = "0000111122223333"
ID_PINJAMAN = 8

nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)

try:
    PinjamanService.cairkan_pinjaman(
        nasabah=nasabah,
        id_pinjaman=ID_PINJAMAN
    )

except ValueError as error:
    print("✅ Pencairan kedua berhasil ditolak")
    print("Pesan error:", error)

else:
    raise AssertionError(
        "Pinjaman dapat dicairkan dua kali"
    )
