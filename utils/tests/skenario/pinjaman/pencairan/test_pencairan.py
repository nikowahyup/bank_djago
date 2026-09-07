"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 8).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)
from bank_djago.utils.utility import StatusPinjaman


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"

NOMINAL_PINJAMAN = 1_000_000


# ============================================================
# 1. MEMUAT OBJEK NASABAH BESERTA REKENING DAN PINJAMANNYA
# ============================================================

nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)

if nasabah is None:
    raise AssertionError("Nasabah pengujian tidak ditemukan")


rekening = next(
    (
        rekening
        for rekening in nasabah.rekening
        if rekening.norek == NOREK_PENGUJIAN
    ),
    None
)

if rekening is None:
    raise AssertionError(
        "Objek rekening pengujian tidak ditemukan"
    )


pinjaman = next(
    (
        pinjaman
        for pinjaman in nasabah.daftar_pinjaman
        if pinjaman.ID == ID_PINJAMAN
    ),
    None
)

if pinjaman is None:
    raise AssertionError(
        "Objek pinjaman ID 8 tidak ditemukan"
    )


# Menyimpan kondisi objek sebelum pencairan.
# Nilai ini akan dibandingkan setelah service dijalankan.
saldo_objek_sebelum = rekening.saldo
objek_pinjaman_sebelum = pinjaman
objek_rekening_sebelum = rekening


print("=== KONDISI SEBELUM PENCAIRAN ===")
print("ID pinjaman    :", pinjaman.ID)
print("Status         :", pinjaman.status)
print("Nominal        :", pinjaman.nominal_pinjaman)
print("Sisa pokok     :", pinjaman.sisa_pokok)
print("Saldo rekening :", saldo_objek_sebelum)
print()


assert pinjaman.status == StatusPinjaman.DISETUJUI, (
    "Objek pinjaman belum berstatus disetujui"
)


# ============================================================
# 2. MENJALANKAN SERVICE PENCAIRAN
# ============================================================

hari_pencairan = datetime.date.today()

pinjaman_hasil = PinjamanService.cairkan_pinjaman(
    nasabah=nasabah,
    id_pinjaman=ID_PINJAMAN,
    hari_ini=hari_pencairan
)

saldo_yang_diharapkan = (
    saldo_objek_sebelum + NOMINAL_PINJAMAN
)


# ============================================================
# 3. MEMERIKSA PERUBAHAN OBJEK PYTHON
# ============================================================

# Service harus mengembalikan objek pinjaman yang sama,
# bukan menciptakan objek pinjaman baru.
assert pinjaman_hasil is objek_pinjaman_sebelum, (
    "Service mengembalikan objek pinjaman yang berbeda"
)

# Objek rekening pada pinjaman juga harus tetap menggunakan
# objek rekening yang berada di dalam daftar rekening nasabah.
assert pinjaman_hasil.rekening is objek_rekening_sebelum, (
    "Pinjaman tidak menggunakan objek rekening milik nasabah"
)

assert pinjaman_hasil.status == StatusPinjaman.AKTIF, (
    "Status objek pinjaman belum berubah menjadi aktif"
)

assert pinjaman_hasil.cicilan_tetap > 0, (
    "Cicilan tetap belum berhasil dihitung"
)

assert pinjaman_hasil.tanggal_pencairan == hari_pencairan, (
    "Tanggal pencairan objek tidak sesuai"
)

assert pinjaman_hasil.tanggal_jatuh_tempo is not None, (
    "Tanggal jatuh tempo belum ditentukan"
)

assert rekening.saldo == saldo_yang_diharapkan, (
    "Saldo objek rekening tidak bertambah sesuai nominal pinjaman"
)

print("✅ State objek Python berhasil diperbarui")


# ============================================================
# 4. MEMERIKSA HASIL PENYIMPANAN DI DATABASE
# ============================================================

koneksi = buat_koneksi()

try:
    data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
        ID_PINJAMAN,
        koneksi
    )

    data_rekening = RekeningRepository.cari_rekening_dengan_norek(
        NOREK_PENGUJIAN,
        koneksi
    )

    # Mengambil transaksi pencairan berdasarkan referensi pinjaman.
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = 'pencairan_pinjaman'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (ID_PINJAMAN,)
    ).fetchone()

    if transaksi is None:
        raise AssertionError(
            "Transaksi pencairan pinjaman tidak ditemukan"
        )

    # Mengambil riwayat yang terhubung dengan transaksi pencairan.
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (transaksi["id"],)
    ).fetchall()

    # Mengambil audit yang terhubung dengan transaksi pencairan.
    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (transaksi["id"],)
    ).fetchall()


    print()
    print("=== KONDISI SETELAH PENCAIRAN ===")
    print("Status pinjaman   :", data_pinjaman["status"])
    print("Cicilan tetap     :", data_pinjaman["cicilan_tetap"])
    print("Sisa pokok        :", data_pinjaman["sisa_pokok"])
    print("Tanggal pencairan :", data_pinjaman["tanggal_pencairan"])
    print("Jatuh tempo       :", data_pinjaman["tanggal_jatuh_tempo"])
    print("Saldo rekening    :", data_rekening["saldo"])
    print()

    print("=== DATA TRANSAKSI ===")
    print("ID transaksi       :", transaksi["id"])
    print("Jenis transaksi    :", transaksi["jenis"])
    print("Rekening tujuan    :", transaksi["norek_tujuan"])
    print("Nominal             :", transaksi["nominal"])
    print("Saldo tujuan awal  :", transaksi["saldo_tujuan_sebelum"])
    print("Saldo tujuan akhir :", transaksi["saldo_tujuan_sesudah"])
    print("Jenis referensi    :", transaksi["jenis_referensi"])
    print("ID referensi       :", transaksi["id_referensi"])
    print("Waktu              :", transaksi["waktu"])
    print()

    print("=== RIWAYAT TERHUBUNG ===")
    for riwayat in daftar_riwayat:
        print(
            f"ID {riwayat['id']} | "
            f"Transaksi {riwayat['transaksi_id']} | "
            f"{riwayat['jenis']} | "
            f"{riwayat['log']}"
        )

    print()
    print("=== AUDIT TERHUBUNG ===")
    for audit in daftar_audit:
        print(
            f"ID {audit['id']} | "
            f"Transaksi {audit['transaksi_id']} | "
            f"{audit['jenis']} | "
            f"{audit['log']}"
        )


    # ========================================================
    # 5. MEMASTIKAN SELURUH HASIL SESUAI
    # ========================================================

    assert data_pinjaman["status"] == StatusPinjaman.AKTIF.value, (
        "Status pinjaman di database bukan aktif"
    )

    assert data_pinjaman["cicilan_tetap"] > 0, (
        "Cicilan tetap tidak tersimpan"
    )

    assert (
        data_pinjaman["tanggal_pencairan"]
        == hari_pencairan.isoformat()
    ), "Tanggal pencairan database tidak sesuai"

    assert data_pinjaman["tanggal_jatuh_tempo"] is not None, (
        "Tanggal jatuh tempo tidak tersimpan"
    )

    assert data_rekening["saldo"] == saldo_yang_diharapkan, (
        "Saldo rekening di database tidak sesuai"
    )

    assert transaksi["norek_tujuan"] == NOREK_PENGUJIAN, (
        "Rekening tujuan transaksi salah"
    )

    assert transaksi["nominal"] == NOMINAL_PINJAMAN, (
        "Nominal transaksi pencairan salah"
    )

    assert transaksi["saldo_tujuan_sebelum"] == saldo_objek_sebelum, (
        "Snapshot saldo sebelum pencairan salah"
    )

    assert transaksi["saldo_tujuan_sesudah"] == saldo_yang_diharapkan, (
        "Snapshot saldo setelah pencairan salah"
    )

    assert transaksi["jenis_referensi"] == "pinjaman", (
        "Jenis referensi transaksi bukan pinjaman"
    )

    assert transaksi["id_referensi"] == ID_PINJAMAN, (
        "ID referensi tidak menunjuk pinjaman ID 8"
    )

    assert len(daftar_riwayat) == 1, (
        "Jumlah riwayat yang terhubung bukan satu"
    )

    assert len(daftar_audit) == 1, (
        "Jumlah audit yang terhubung bukan satu"
    )

finally:
    koneksi.close()


print()
print(
    "✅ PENCAIRAN PINJAMAN ID 8 BERHASIL: "
    "saldo, pinjaman, transaksi, riwayat, audit, "
    "dan objek Python tersimpan dengan benar"
)
