"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_uji_schdeuler.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime
from unittest.mock import patch

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.services.scheduler import Scheduler


HARI_PENGUJIAN = datetime.date(2026, 9, 7)


# Memuat rekening menggunakan loader asli untuk mengetahui
# rekening mana saja yang seharusnya diproses scheduler.
daftar_rekening = (
    RekeningLoader.muat_semua_rekening_berjalan()
)

if not daftar_rekening:
    raise AssertionError(
        "Tidak ditemukan rekening berjalan"
    )

norek_diharapkan = {
    rekening.norek
    for rekening in daftar_rekening
}


# Kedua service diganti sementara dengan mock.
# Scheduler tetap menjalankan loader dan perulangannya,
# tetapi tidak ada saldo atau tanggal yang benar-benar diubah.
with (
    patch(
        "bank_djago.services.scheduler."
        "BungaService.berikan_bunga"
    ) as mock_bunga,
    patch(
        "bank_djago.services.scheduler."
        "BiayaAdminService.potong_admin"
    ) as mock_admin
):
    Scheduler.jalankan(
        bank=None,
        hari_ini=HARI_PENGUJIAN
    )


print("=== HASIL PEMANGGILAN SCHEDULER ===")
print("Rekening berjalan :", len(norek_diharapkan))
print("Panggilan bunga    :", mock_bunga.call_count)
print("Panggilan admin    :", mock_admin.call_count)
print()


# Mengambil nomor rekening dari setiap argumen pemanggilan.
#
# Scheduler saat ini memanggil service dengan posisi:
# BungaService.berikan_bunga(rekening, hari_ini)
norek_dipanggil_bunga = {
    pemanggilan.args[0].norek
    for pemanggilan in mock_bunga.call_args_list
}

norek_dipanggil_admin = {
    pemanggilan.args[0].norek
    for pemanggilan in mock_admin.call_args_list
}


for norek in sorted(norek_diharapkan):
    print(
        f"{norek} | "
        f"Bunga: {'✅' if norek in norek_dipanggil_bunga else '❌'} | "
        f"Admin: {'✅' if norek in norek_dipanggil_admin else '❌'}"
    )


# Setiap rekening berjalan harus diproses tepat satu kali
# oleh masing-masing service.
assert mock_bunga.call_count == len(norek_diharapkan), (
    "Jumlah pemanggilan service bunga tidak sesuai"
)

assert mock_admin.call_count == len(norek_diharapkan), (
    "Jumlah pemanggilan service biaya admin tidak sesuai"
)

assert norek_dipanggil_bunga == norek_diharapkan, (
    "Tidak semua rekening berjalan dikirim ke service bunga"
)

assert norek_dipanggil_admin == norek_diharapkan, (
    "Tidak semua rekening berjalan dikirim ke service biaya admin"
)


print()
print(
    "✅ SELURUH REKENING BERJALAN DIPROSES: "
    "setiap rekening dikirim tepat satu kali ke service "
    "bunga dan biaya admin tanpa mengubah database"
)
