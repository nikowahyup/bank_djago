"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_scheduler_pinjaman.py` (urutan 2).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.pinjaman_loader import (
    PinjamanLoader
)
from bank_djago.penyimpanan.repositories.notifikasi_repository import (
    NotifikasiRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.notifikasi_service import NotifikasiService
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)
from bank_djago.utils.utility import JenisReferensi


ID_PINJAMAN = 10


def ambil_notifikasi_pinjaman(nasabah, id_pinjaman):
    koneksi = buat_koneksi()

    try:
        return (
            NotifikasiRepository.cari_notifikasi_dengan_referensi(
                nik_pemilik=nasabah.NIK,
                jenis_referensi=JenisReferensi.PINJAMAN,
                id_objek=id_pinjaman,
                koneksi=koneksi
            )
        )
    finally:
        koneksi.close()


# Memuat pinjaman aktif beserta pemiliknya.
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

nasabah = pinjaman.pemilik
jatuh_tempo = pinjaman.tanggal_jatuh_tempo

hari_h_minus_3 = (
    jatuh_tempo - datetime.timedelta(days=3)
)

hari_h_minus_2 = (
    jatuh_tempo - datetime.timedelta(days=2)
)


print("=== KONDISI AWAL ===")
print("ID pinjaman :", pinjaman.ID)
print("NIK pemilik :", nasabah.NIK)
print("Jatuh tempo :", jatuh_tempo)
print()


# ============================================================
# 1. Simulasi scheduler pada H-3
# ============================================================

pesan_h_minus_3 = PinjamanService.buat_pesan_pengingat(
    pinjaman=pinjaman,
    hari_ini=hari_h_minus_3
)

assert pesan_h_minus_3 is not None, (
    "H-3 seharusnya menghasilkan pesan"
)

hasil_pertama = (
    NotifikasiService.simpan_notifikasi_referensi(
        nasabah=nasabah,
        jenis="pinjaman",
        pesan=pesan_h_minus_3,
        jenis_referensi=JenisReferensi.PINJAMAN,
        id_objek=pinjaman.ID
    )
)

notifikasi_h_minus_3 = ambil_notifikasi_pinjaman(
    nasabah=nasabah,
    id_pinjaman=pinjaman.ID
)

assert hasil_pertama is True, (
    "Pemanggilan H-3 seharusnya menyimpan notifikasi"
)

assert notifikasi_h_minus_3 is not None, (
    "Notifikasi H-3 tidak ditemukan di SQLite"
)

assert notifikasi_h_minus_3["pesan"] == pesan_h_minus_3, (
    "Pesan H-3 yang tersimpan tidak sesuai"
)

id_notifikasi_h_minus_3 = notifikasi_h_minus_3["id"]

print("=== SETELAH PEMANGGILAN H-3 ===")
print("Hari simulasi  :", hari_h_minus_3)
print("ID notifikasi  :", id_notifikasi_h_minus_3)
print("Pesan          :", notifikasi_h_minus_3["pesan"])
print()


# ============================================================
# 2. Jalankan kembali pada tanggal yang sama
# ============================================================

hasil_pengulangan = (
    NotifikasiService.simpan_notifikasi_referensi(
        nasabah=nasabah,
        jenis="pinjaman",
        pesan=pesan_h_minus_3,
        jenis_referensi=JenisReferensi.PINJAMAN,
        id_objek=pinjaman.ID
    )
)

notifikasi_setelah_pengulangan = (
    ambil_notifikasi_pinjaman(
        nasabah=nasabah,
        id_pinjaman=pinjaman.ID
    )
)

assert hasil_pengulangan is False, (
    "Pesan yang sama seharusnya tidak disimpan kembali"
)

assert (
    notifikasi_setelah_pengulangan["id"]
    == id_notifikasi_h_minus_3
), "Pemanggilan kedua membuat notifikasi baru"

assert (
    notifikasi_setelah_pengulangan["pesan"]
    == pesan_h_minus_3
), "Pesan berubah pada tanggal simulasi yang sama"

print(
    "✅ Pemanggilan berulang tidak menggandakan notifikasi"
)
print()


# ============================================================
# 3. Simulasi scheduler pada H-2
# ============================================================

pesan_h_minus_2 = PinjamanService.buat_pesan_pengingat(
    pinjaman=pinjaman,
    hari_ini=hari_h_minus_2
)

assert pesan_h_minus_2 is not None, (
    "H-2 seharusnya menghasilkan pesan"
)

assert pesan_h_minus_2 != pesan_h_minus_3, (
    "Pesan H-2 seharusnya berbeda dari pesan H-3"
)

hasil_perubahan = (
    NotifikasiService.simpan_notifikasi_referensi(
        nasabah=nasabah,
        jenis="pinjaman",
        pesan=pesan_h_minus_2,
        jenis_referensi=JenisReferensi.PINJAMAN,
        id_objek=pinjaman.ID
    )
)

notifikasi_h_minus_2 = ambil_notifikasi_pinjaman(
    nasabah=nasabah,
    id_pinjaman=pinjaman.ID
)

assert hasil_perubahan is True, (
    "Pesan H-2 seharusnya mengganti pesan H-3"
)

assert notifikasi_h_minus_2 is not None, (
    "Notifikasi H-2 tidak ditemukan"
)

assert notifikasi_h_minus_2["pesan"] == pesan_h_minus_2, (
    "Pesan H-2 yang tersimpan tidak sesuai"
)

assert (
    notifikasi_h_minus_2["jenis_referensi"]
    == JenisReferensi.PINJAMAN.value
), "Jenis referensi notifikasi bukan pinjaman"

assert notifikasi_h_minus_2["id_objek"] == pinjaman.ID, (
    "ID objek notifikasi tidak menunjuk pinjaman ID 10"
)

print("=== SETELAH PEMANGGILAN H-2 ===")
print("Hari simulasi :", hari_h_minus_2)
print("ID notifikasi :", notifikasi_h_minus_2["id"])
print("Pesan         :", notifikasi_h_minus_2["pesan"])
print()

print(
    "✅ INTEGRASI NOTIFIKASI BERHASIL: "
    "H-3 membuat notifikasi, pemanggilan berulang tidak "
    "menggandakan, dan H-2 mengganti pesan lama"
)
