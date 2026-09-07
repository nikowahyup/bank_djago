"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_scheduler_pinjaman.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.pinjaman_loader import (
    PinjamanLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.notifikasi_service import NotifikasiService
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)
from bank_djago.utils.utility import JenisReferensi


ID_PINJAMAN_PERTAMA = 9
ID_PINJAMAN_KEDUA = 10


def ambil_notifikasi_pinjaman(nik_pemilik, daftar_id):
    koneksi = buat_koneksi()

    try:
        placeholder = ", ".join("?" for _ in daftar_id)

        return koneksi.execute(
            f"""
            SELECT
                id,
                nik_pemilik,
                jenis,
                pesan,
                jenis_referensi,
                id_objek
            FROM notifikasi
            WHERE nik_pemilik = ?
              AND jenis_referensi = ?
              AND id_objek IN ({placeholder})
            ORDER BY id_objek
            """,
            (
                nik_pemilik,
                JenisReferensi.PINJAMAN.value,
                *daftar_id
            )
        ).fetchall()

    finally:
        koneksi.close()


daftar_pinjaman_aktif = (
    PinjamanLoader.muat_semua_pinjaman_aktif()
)

pinjaman_9 = next(
    (
        pinjaman
        for pinjaman in daftar_pinjaman_aktif
        if pinjaman.ID == ID_PINJAMAN_PERTAMA
    ),
    None
)

pinjaman_10 = next(
    (
        pinjaman
        for pinjaman in daftar_pinjaman_aktif
        if pinjaman.ID == ID_PINJAMAN_KEDUA
    ),
    None
)

assert pinjaman_9 is not None, (
    "Pinjaman aktif ID 9 tidak ditemukan"
)

assert pinjaman_10 is not None, (
    "Pinjaman aktif ID 10 tidak ditemukan"
)

# Keduanya seharusnya memakai objek nasabah yang sama
# karena loader menggunakan nasabah_index.
assert pinjaman_9.pemilik is pinjaman_10.pemilik, (
    "Kedua pinjaman tidak menggunakan objek nasabah yang sama"
)

nasabah = pinjaman_9.pemilik
daftar_id = [pinjaman_9.ID, pinjaman_10.ID]


print("=== KONDISI PINJAMAN ===")
print("NIK pemilik     :", nasabah.NIK)
print("Pinjaman pertama:", pinjaman_9.ID)
print("Jatuh tempo     :", pinjaman_9.tanggal_jatuh_tempo)
print("Pinjaman kedua  :", pinjaman_10.ID)
print("Jatuh tempo     :", pinjaman_10.tanggal_jatuh_tempo)
print()


# Membuat pesan H-3 berdasarkan jadwal masing-masing.
for pinjaman in (pinjaman_9, pinjaman_10):
    hari_simulasi = (
        pinjaman.tanggal_jatuh_tempo
        - datetime.timedelta(days=3)
    )

    pesan = PinjamanService.buat_pesan_pengingat(
        pinjaman=pinjaman,
        hari_ini=hari_simulasi
    )

    assert pesan is not None, (
        f"Pinjaman ID {pinjaman.ID} tidak menghasilkan pesan H-3"
    )

    NotifikasiService.simpan_notifikasi_referensi(
        nasabah=pinjaman.pemilik,
        jenis="pinjaman",
        pesan=pesan,
        jenis_referensi=JenisReferensi.PINJAMAN,
        id_objek=pinjaman.ID
    )

    print(f"Notifikasi pinjaman ID {pinjaman.ID} diproses")
    print("Hari simulasi:", hari_simulasi)
    print("Pesan        :", pesan)
    print()


# Membaca kembali hasil akhirnya langsung dari SQLite.
notifikasi_sqlite = ambil_notifikasi_pinjaman(
    nik_pemilik=nasabah.NIK,
    daftar_id=daftar_id
)

print("=== NOTIFIKASI DI SQLITE ===")

for data in notifikasi_sqlite:
    print(
        f"ID notifikasi {data['id']} | "
        f"Pinjaman {data['id_objek']} | "
        f"{data['pesan']}"
    )

assert len(notifikasi_sqlite) == 2, (
    "Seharusnya terdapat tepat dua notifikasi pinjaman"
)

id_objek_sqlite = {
    data["id_objek"]
    for data in notifikasi_sqlite
}

assert id_objek_sqlite == {9, 10}, (
    "Notifikasi tidak menunjuk pinjaman ID 9 dan 10"
)

for data in notifikasi_sqlite:
    assert data["nik_pemilik"] == nasabah.NIK, (
        "Notifikasi terhubung dengan nasabah yang salah"
    )

    assert (
        data["jenis_referensi"]
        == JenisReferensi.PINJAMAN.value
    ), "Jenis referensi notifikasi tidak sesuai"


# Objek nasabah juga seharusnya mempunyai kedua notifikasi.
notifikasi_objek = [
    notifikasi
    for notifikasi in nasabah.notifikasi
    if (
        notifikasi.jenis_referensi
        == JenisReferensi.PINJAMAN
        and notifikasi.id_objek in daftar_id
    )
]

id_objek_python = {
    notifikasi.id_objek
    for notifikasi in notifikasi_objek
}

assert id_objek_python == {9, 10}, (
    "Daftar notifikasi objek nasabah tidak memuat "
    "pinjaman ID 9 dan 10"
)

print()
print(
    "✅ ISOLASI NOTIFIKASI BERHASIL: "
    "pinjaman ID 9 dan 10 mempunyai notifikasi sendiri "
    "tanpa saling menghapus"
)
