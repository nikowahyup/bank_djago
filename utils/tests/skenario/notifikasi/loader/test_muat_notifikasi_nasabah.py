"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_notifikasi.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader


nasabah = NasabahLoader.muat_nasabah("1111222233334444")

print("Jumlah notifikasi:", len(nasabah.notifikasi))

for notifikasi in nasabah.notifikasi:
    print("Jenis             :", notifikasi.jenis)
    print("Pesan             :", notifikasi.pesan)
    print("Jenis referensi   :", notifikasi.jenis_referensi)
    print("ID objek          :", notifikasi.id_objek)
    print()
