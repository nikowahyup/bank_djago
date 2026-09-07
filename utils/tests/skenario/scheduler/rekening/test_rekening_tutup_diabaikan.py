"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_uji_schdeuler.py` (urutan 2).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi


# Mengambil semua nomor rekening yang telah ditutup
# langsung dari SQLite.
koneksi = buat_koneksi()

try:
    data_rekening_tutup = koneksi.execute(
        """
        SELECT norek
        FROM rekening
        WHERE status = 'tutup'
        ORDER BY norek
        """
    ).fetchall()
finally:
    koneksi.close()


norek_tutup = {
    data["norek"]
    for data in data_rekening_tutup
}

if not norek_tutup:
    raise AssertionError(
        "Tidak ditemukan rekening tutup untuk pengujian"
    )


# Loader ini seharusnya hanya mengembalikan rekening
# yang masih berjalan.
daftar_rekening_berjalan = (
    RekeningLoader.muat_semua_rekening_berjalan()
)

norek_berjalan = {
    rekening.norek
    for rekening in daftar_rekening_berjalan
}


print("=== REKENING TUTUP ===")
for norek in sorted(norek_tutup):
    print("-", norek)

print()
print("=== JUMLAH REKENING BERJALAN ===")
print(len(norek_berjalan))


# Tidak boleh ada nomor rekening yang muncul
# pada kedua kumpulan.
rekening_tutup_yang_ikut = (
    norek_tutup & norek_berjalan
)

assert not rekening_tutup_yang_ikut, (
    "Loader masih memuat rekening tutup: "
    f"{sorted(rekening_tutup_yang_ikut)}"
)


print()
print(
    "✅ REKENING TUTUP BERHASIL DIABAIKAN: "
    "tidak ada rekening tutup yang dimuat untuk scheduler"
)
