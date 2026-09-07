"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_scheduler_pinjaman.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.pinjaman_loader import (
    PinjamanLoader
)
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)


ID_PINJAMAN = 10

daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()

pinjaman = next(
    (
        pinjaman
        for pinjaman in daftar_pinjaman
        if pinjaman.ID == ID_PINJAMAN
    ),
    None
)

if pinjaman is None:
    raise AssertionError(
        f"Pinjaman aktif ID {ID_PINJAMAN} tidak ditemukan"
    )

jatuh_tempo = pinjaman.tanggal_jatuh_tempo
batas_toleransi = PinjamanService.BATAS_HARI_TUNGGAKAN

skenario = [
    {
        "nama": "H-4 belum perlu pengingat",
        "hari": jatuh_tempo - datetime.timedelta(days=4),
        "teks_wajib": None
    },
    {
        "nama": "H-3 mulai diingatkan",
        "hari": jatuh_tempo - datetime.timedelta(days=3),
        "teks_wajib": "3 hari"
    },
    {
        "nama": "H-1 jatuh tempo besok",
        "hari": jatuh_tempo - datetime.timedelta(days=1),
        "teks_wajib": "1 hari"
    },
    {
        "nama": "Hari jatuh tempo",
        "hari": jatuh_tempo,
        "teks_wajib": "Hari ini"
    },
    {
        "nama": "Terlambat satu hari",
        "hari": jatuh_tempo + datetime.timedelta(days=1),
        "teks_wajib": "terlambat 1 hari"
    },
    {
        "nama": "Hari terakhir toleransi",
        "hari": (
            jatuh_tempo
            + datetime.timedelta(days=batas_toleransi)
        ),
        "teks_wajib": "hari terakhir masa toleransi"
    },
    {
        "nama": "Hari pertama terkena denda",
        "hari": (
            jatuh_tempo
            + datetime.timedelta(days=batas_toleransi + 1)
        ),
        "teks_wajib": "Denda telah berjalan selama 1 hari"
    }
]


print("=== PENGUJIAN PESAN PENGINGAT PINJAMAN ===")
print("ID pinjaman :", pinjaman.ID)
print("Jatuh tempo :", jatuh_tempo)
print("Toleransi   :", batas_toleransi, "hari")
print()

for nomor, data_uji in enumerate(skenario, start=1):
    pesan = PinjamanService.buat_pesan_pengingat(
        pinjaman=pinjaman,
        hari_ini=data_uji["hari"]
    )

    print(f"--- SKENARIO {nomor}: {data_uji['nama']} ---")
    print("Hari simulasi :", data_uji["hari"])
    print("Pesan         :", pesan)
    print()

    if data_uji["teks_wajib"] is None:
        assert pesan is None, (
            f"{data_uji['nama']} seharusnya belum menghasilkan pesan"
        )

    else:
        assert pesan is not None, (
            f"{data_uji['nama']} seharusnya menghasilkan pesan"
        )

        assert data_uji["teks_wajib"].lower() in pesan.lower(), (
            f"Pesan skenario '{data_uji['nama']}' tidak sesuai.\n"
            f"Teks yang dicari: {data_uji['teks_wajib']}\n"
            f"Pesan aktual: {pesan}"
        )

print(
    "✅ SELURUH CABANG PESAN BERHASIL: "
    "H-4, H-3, H-1, jatuh tempo, toleransi, "
    "dan denda menghasilkan pesan yang sesuai"
)
