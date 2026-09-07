"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_scheduler_pinjaman.py` (urutan 4).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.core.notifikasi import Notifikasi
from bank_djago.penyimpanan.loaders.pinjaman_loader import (
    PinjamanLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)
from bank_djago.utils.utility import (
    JenisReferensi,
    StatusPinjaman
)


ID_PINJAMAN_DIBAYAR = 10
ID_PINJAMAN_DIPERTAHANKAN = 9


def ambil_snapshot(nik_pemilik):
    koneksi = buat_koneksi()

    try:
        data_pinjaman = koneksi.execute(
            """
            SELECT
                id,
                norek,
                status,
                cicilan_terbayar,
                sisa_pokok,
                tanggal_jatuh_tempo
            FROM pinjaman
            WHERE id = ?
            """,
            (ID_PINJAMAN_DIBAYAR,)
        ).fetchone()

        data_rekening = koneksi.execute(
            """
            SELECT norek, saldo
            FROM rekening
            WHERE norek = ?
            """,
            (data_pinjaman["norek"],)
        ).fetchone()

        daftar_notifikasi = koneksi.execute(
            """
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
              AND id_objek IN (?, ?)
            ORDER BY id_objek
            """,
            (
                nik_pemilik,
                JenisReferensi.PINJAMAN.value,
                ID_PINJAMAN_DIPERTAHANKAN,
                ID_PINJAMAN_DIBAYAR
            )
        ).fetchall()

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis_referensi = ?
              AND id_referensi = ?
              AND jenis = 'pembayaran_cicilan'
            """,
            (
                JenisReferensi.PINJAMAN.value,
                ID_PINJAMAN_DIBAYAR
            )
        ).fetchone()["jumlah"]

        return {
            "pinjaman": dict(data_pinjaman),
            "rekening": dict(data_rekening),
            "notifikasi": [
                dict(data)
                for data in daftar_notifikasi
            ],
            "jumlah_transaksi": jumlah_transaksi
        }

    finally:
        koneksi.close()


# Memuat graph objek pinjaman, nasabah, dan rekening.
daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()

pinjaman = next(
    (
        pinjaman
        for pinjaman in daftar_pinjaman
        if pinjaman.ID == ID_PINJAMAN_DIBAYAR
    ),
    None
)

if pinjaman is None:
    raise AssertionError(
        f"Pinjaman aktif ID {ID_PINJAMAN_DIBAYAR} "
        f"tidak ditemukan"
    )

nasabah = pinjaman.pemilik
rekening = pinjaman.rekening

snapshot_sebelum = ambil_snapshot(nasabah.NIK)

id_notifikasi_sebelum = {
    data["id_objek"]
    for data in snapshot_sebelum["notifikasi"]
}

assert id_notifikasi_sebelum == {9, 10}, (
    "Pengujian membutuhkan notifikasi pinjaman ID 9 dan 10"
)

assert (
    snapshot_sebelum["pinjaman"]["status"]
    == StatusPinjaman.AKTIF.value
), "Pinjaman ID 10 sudah tidak aktif"

assert (
    snapshot_sebelum["pinjaman"]["cicilan_terbayar"] == 0
), (
    "Pinjaman ID 10 sudah pernah dibayar. "
    "Jangan menjalankan pengujian ini kembali."
)


# Memuat dua notifikasi SQLite ke dalam objek nasabah.
# Ini membuat pemeriksaan state objek Python tidak bersifat semu.
nasabah.notifikasi = [
    Notifikasi(
        jenis=data["jenis"],
        pesan=data["pesan"],
        jenis_referensi=JenisReferensi(
            data["jenis_referensi"]
        ),
        id_objek=data["id_objek"]
    )
    for data in snapshot_sebelum["notifikasi"]
]


print("=== KONDISI SEBELUM PEMBAYARAN ===")
print("ID pinjaman        :", pinjaman.ID)
print(
    "Cicilan terbayar  :",
    snapshot_sebelum["pinjaman"]["cicilan_terbayar"]
)
print(
    "Sisa pokok        :",
    snapshot_sebelum["pinjaman"]["sisa_pokok"]
)
print(
    "Saldo rekening    :",
    snapshot_sebelum["rekening"]["saldo"]
)
print(
    "Notifikasi tersedia:",
    sorted(id_notifikasi_sebelum)
)
print("Hari pembayaran    :", pinjaman.tanggal_jatuh_tempo)
print()


# Membayar tepat pada tanggal jatuh tempo agar tidak terkena denda.
PinjamanService.bayar_cicilan(
    nasabah=nasabah,
    id_pinjaman=pinjaman.ID,
    hari_ini=pinjaman.tanggal_jatuh_tempo
)

snapshot_setelah = ambil_snapshot(nasabah.NIK)

id_notifikasi_setelah = {
    data["id_objek"]
    for data in snapshot_setelah["notifikasi"]
}

id_notifikasi_objek = {
    notifikasi.id_objek
    for notifikasi in nasabah.notifikasi
    if (
        notifikasi.jenis_referensi
        == JenisReferensi.PINJAMAN
    )
}


# Pinjaman berhasil diperbarui.
assert (
    snapshot_setelah["pinjaman"]["cicilan_terbayar"]
    == snapshot_sebelum["pinjaman"]["cicilan_terbayar"] + 1
), "Jumlah cicilan terbayar tidak bertambah"

assert (
    snapshot_setelah["pinjaman"]["sisa_pokok"]
    < snapshot_sebelum["pinjaman"]["sisa_pokok"]
), "Sisa pokok tidak berkurang"

assert (
    snapshot_setelah["rekening"]["saldo"]
    < snapshot_sebelum["rekening"]["saldo"]
), "Saldo rekening tidak berkurang"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"] + 1
), "Transaksi pembayaran cicilan tidak bertambah"


# Hanya notifikasi pinjaman yang dibayar yang dihapus.
assert ID_PINJAMAN_DIBAYAR not in id_notifikasi_setelah, (
    "Notifikasi pinjaman ID 10 masih tersimpan di SQLite"
)

assert ID_PINJAMAN_DIPERTAHANKAN in id_notifikasi_setelah, (
    "Notifikasi pinjaman ID 9 ikut terhapus"
)

assert id_notifikasi_setelah == {9}, (
    "Hasil akhir notifikasi SQLite tidak sesuai"
)


# State objek Python juga harus mengikuti SQLite.
assert pinjaman.cicilan_terbayar == 1, (
    "State cicilan objek pinjaman tidak diperbarui"
)

assert rekening.saldo == snapshot_setelah["rekening"]["saldo"], (
    "Saldo objek rekening tidak sesuai SQLite"
)

assert ID_PINJAMAN_DIBAYAR not in id_notifikasi_objek, (
    "Notifikasi pinjaman ID 10 masih ada pada objek nasabah"
)

assert ID_PINJAMAN_DIPERTAHANKAN in id_notifikasi_objek, (
    "Notifikasi pinjaman ID 9 hilang dari objek nasabah"
)


print("=== KONDISI SETELAH PEMBAYARAN ===")
print(
    "Cicilan terbayar :",
    snapshot_setelah["pinjaman"]["cicilan_terbayar"]
)
print(
    "Sisa pokok       :",
    snapshot_setelah["pinjaman"]["sisa_pokok"]
)
print(
    "Saldo rekening   :",
    snapshot_setelah["rekening"]["saldo"]
)
print(
    "Notifikasi tersisa:",
    sorted(id_notifikasi_setelah)
)
print()

print(
    "✅ PENGHAPUSAN NOTIFIKASI BERHASIL: "
    "pembayaran pinjaman ID 10 menghapus notifikasinya, "
    "sedangkan notifikasi pinjaman ID 9 tetap tersimpan"
)
