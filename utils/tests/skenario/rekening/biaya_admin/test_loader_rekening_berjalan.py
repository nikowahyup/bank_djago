"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_load_untuk_biayaadmin.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)


# Memuat rekening aktif dan blokir dari SQLite.
daftar_rekening = (
    RekeningLoader.muat_semua_rekening_berjalan()
)

print("=== REKENING YANG BERJALAN ===")
print("Jumlah rekening:", len(daftar_rekening))
print()


# Menyimpan objek nasabah pertama untuk setiap NIK.
# Ini digunakan untuk memastikan satu nasabah tidak dirangkai
# menjadi beberapa objek selama proses loader yang sama.
nasabah_index = {}

for rekening in daftar_rekening:
    nasabah = rekening.pemilik
    nik = nasabah.NIK

    print("Nomor rekening :", rekening.norek)
    print("Status         :", rekening.status)
    print("Saldo          :", rekening.saldo)
    print("NIK pemilik    :", nik)
    print("Nama pemilik   :", nasabah.nama)
    print()

    # Repository seharusnya sudah mengeluarkan rekening tutup
    # dari hasil query.
    assert rekening.status != "tutup", (
        f"Rekening tutup {rekening.norek} masih ikut dimuat"
    )

    assert rekening.pemilik is not None, (
        f"Rekening {rekening.norek} tidak memiliki objek pemilik"
    )

    if nik in nasabah_index:
        # Rekening milik nasabah yang sama harus menunjuk
        # objek nasabah Python yang sama.
        assert rekening.pemilik is nasabah_index[nik], (
            f"Nasabah {nik} dirangkai menjadi objek berbeda"
        )

    else:
        nasabah_index[nik] = rekening.pemilik


print(
    "✅ LOADER REKENING BERHASIL: "
    "seluruh rekening berjalan berhasil dimuat, "
    "rekening tutup tidak ikut, dan identitas pemilik konsisten"
)
