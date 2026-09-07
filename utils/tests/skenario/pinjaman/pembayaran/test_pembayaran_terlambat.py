"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 13).

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
from bank_djago.utils.utility import StatusPinjaman, Utilitas


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"

# Kita melewati masa toleransi sebanyak tiga hari.
TAMBAHAN_HARI_DENDA = 3


# ============================================================
# 1. MEMUAT OBJEK NASABAH, REKENING, DAN PINJAMAN
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
    raise AssertionError("Objek rekening tidak ditemukan")


pinjaman = next(
    (
        pinjaman
        for pinjaman in nasabah.daftar_pinjaman
        if pinjaman.ID == ID_PINJAMAN
    ),
    None
)

if pinjaman is None:
    raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")


# ============================================================
# 2. MEMBACA KONDISI SEBELUM PEMBAYARAN
# ============================================================

koneksi = buat_koneksi()

try:
    data_pinjaman_sebelum = dict(
        PinjamanRepository.cari_pinjaman_dengan_id(
            ID_PINJAMAN,
            koneksi
        )
    )

    data_rekening_sebelum = dict(
        RekeningRepository.cari_rekening_dengan_norek(
            NOREK_PENGUJIAN,
            koneksi
        )
    )

    jumlah_pembayaran_sebelum = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM transaksi
        WHERE jenis = 'pembayaran_cicilan'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        """,
        (ID_PINJAMAN,)
    ).fetchone()["jumlah"]

finally:
    koneksi.close()


assert data_pinjaman_sebelum["status"] == "aktif", (
    "Pinjaman ID 8 tidak berstatus aktif"
)

assert data_pinjaman_sebelum["cicilan_terbayar"] == 1, (
    "Pinjaman ID 8 bukan berada setelah cicilan pertama"
)


# ============================================================
# 3. MENGHITUNG HASIL YANG DIHARAPKAN
# ============================================================

saldo_sebelum = data_rekening_sebelum["saldo"]
sisa_pokok_sebelum = data_pinjaman_sebelum["sisa_pokok"]

cicilan_tetap = data_pinjaman_sebelum["cicilan_tetap"]
bunga = data_pinjaman_sebelum["bunga"]

tanggal_jatuh_tempo = datetime.date.fromisoformat(
    data_pinjaman_sebelum["tanggal_jatuh_tempo"]
)

# Hari pengujian berada tiga hari setelah masa toleransi.
hari_pengujian = (
    tanggal_jatuh_tempo
    + datetime.timedelta(
        days=(
            PinjamanService.BATAS_HARI_TUNGGAKAN
            + TAMBAHAN_HARI_DENDA
        )
    )
)

hari_terlambat_diharapkan = (
    PinjamanService.BATAS_HARI_TUNGGAKAN
    + TAMBAHAN_HARI_DENDA
)

hari_denda_diharapkan = TAMBAHAN_HARI_DENDA

denda_sebelum_batas = (
    cicilan_tetap
    * hari_denda_diharapkan
    * PinjamanService.PERSENTASE_DENDA_HARIAN
)

denda_maksimal = (
    cicilan_tetap
    * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
)

denda_diharapkan = round(
    min(denda_sebelum_batas, denda_maksimal)
)

bunga_bulanan_diharapkan = round(
    sisa_pokok_sebelum * (bunga / 12)
)

pokok_dibayar_diharapkan = (
    cicilan_tetap - bunga_bulanan_diharapkan
)

sisa_pokok_diharapkan = (
    sisa_pokok_sebelum - pokok_dibayar_diharapkan
)

total_bayar_diharapkan = (
    cicilan_tetap + denda_diharapkan
)

saldo_diharapkan = (
    saldo_sebelum - total_bayar_diharapkan
)

jatuh_tempo_diharapkan = Utilitas.tambah_bulan(
    tanggal_jatuh_tempo,
    1
)


print("=== KONDISI SEBELUM PEMBAYARAN TERLAMBAT ===")
print("ID pinjaman       :", ID_PINJAMAN)
print("Cicilan terbayar  :", data_pinjaman_sebelum["cicilan_terbayar"])
print("Sisa pokok        :", sisa_pokok_sebelum)
print("Saldo rekening    :", saldo_sebelum)
print("Jatuh tempo       :", tanggal_jatuh_tempo)
print("Hari pengujian    :", hari_pengujian)
print()

print("=== PERHITUNGAN YANG DIHARAPKAN ===")
print("Hari terlambat    :", hari_terlambat_diharapkan)
print("Hari terkena denda:", hari_denda_diharapkan)
print("Cicilan tetap     :", cicilan_tetap)
print("Denda             :", denda_diharapkan)
print("Bunga bulan ini   :", bunga_bulanan_diharapkan)
print("Pokok dibayar     :", pokok_dibayar_diharapkan)
print("Total pembayaran  :", total_bayar_diharapkan)
print()


# ============================================================
# 4. MENJALANKAN PEMBAYARAN
# ============================================================

pinjaman_hasil = PinjamanService.bayar_cicilan(
    id_pinjaman=ID_PINJAMAN,
    nasabah=nasabah,
    hari_ini=hari_pengujian
)


# ============================================================
# 5. MEMERIKSA OBJEK PYTHON
# ============================================================

assert pinjaman_hasil is pinjaman, (
    "Service mengembalikan objek pinjaman yang berbeda"
)

assert pinjaman_hasil.status == StatusPinjaman.AKTIF, (
    "Pinjaman seharusnya masih aktif"
)

assert pinjaman_hasil.cicilan_terbayar == 2, (
    "Cicilan terbayar pada objek bukan dua"
)

assert pinjaman_hasil.sisa_pokok == sisa_pokok_diharapkan, (
    "Sisa pokok pada objek tidak sesuai"
)

assert (
    pinjaman_hasil.tanggal_jatuh_tempo
    == jatuh_tempo_diharapkan
), "Jatuh tempo objek tidak sesuai"

assert rekening.saldo == saldo_diharapkan, (
    "Saldo objek rekening tidak sesuai"
)

print("✅ State objek Python berhasil diperbarui")


# ============================================================
# 6. MEMBACA HASIL DARI SQLITE
# ============================================================

koneksi = buat_koneksi()

try:
    data_pinjaman_setelah = PinjamanRepository.cari_pinjaman_dengan_id(
        ID_PINJAMAN,
        koneksi
    )

    data_rekening_setelah = RekeningRepository.cari_rekening_dengan_norek(
        NOREK_PENGUJIAN,
        koneksi
    )

    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = 'pembayaran_cicilan'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (ID_PINJAMAN,)
    ).fetchone()

    if transaksi is None:
        raise AssertionError(
            "Transaksi pembayaran terlambat tidak ditemukan"
        )

    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (transaksi["id"],)
    ).fetchall()

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
    print("=== KONDISI SETELAH PEMBAYARAN ===")
    print("Status pinjaman   :", data_pinjaman_setelah["status"])
    print("Cicilan terbayar  :", data_pinjaman_setelah["cicilan_terbayar"])
    print("Sisa pokok        :", data_pinjaman_setelah["sisa_pokok"])
    print("Jatuh tempo baru  :", data_pinjaman_setelah["tanggal_jatuh_tempo"])
    print("Saldo rekening    :", data_rekening_setelah["saldo"])
    print()

    print("=== DATA TRANSAKSI ===")
    print("ID transaksi      :", transaksi["id"])
    print("Jenis             :", transaksi["jenis"])
    print("Rekening sumber   :", transaksi["norek_sumber"])
    print("Nominal cicilan   :", transaksi["nominal"])
    print("Denda             :", transaksi["biaya"])
    print("Saldo awal        :", transaksi["saldo_sumber_sebelum"])
    print("Saldo akhir       :", transaksi["saldo_sumber_sesudah"])
    print("Jenis referensi   :", transaksi["jenis_referensi"])
    print("ID referensi      :", transaksi["id_referensi"])
    print("Waktu             :", transaksi["waktu"])
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
    # 7. MEMASTIKAN HASIL DATABASE
    # ========================================================

    assert data_pinjaman_setelah["status"] == "aktif", (
        "Pinjaman seharusnya masih aktif"
    )

    assert data_pinjaman_setelah["cicilan_terbayar"] == 2, (
        "Cicilan terbayar di database bukan dua"
    )

    assert (
        data_pinjaman_setelah["sisa_pokok"]
        == sisa_pokok_diharapkan
    ), "Sisa pokok di database tidak sesuai"

    assert (
        data_pinjaman_setelah["tanggal_jatuh_tempo"]
        == jatuh_tempo_diharapkan.isoformat()
    ), "Jatuh tempo baru tidak sesuai"

    assert data_rekening_setelah["saldo"] == saldo_diharapkan, (
        "Saldo rekening di database tidak sesuai"
    )

    assert transaksi["norek_sumber"] == NOREK_PENGUJIAN, (
        "Rekening sumber transaksi salah"
    )

    assert transaksi["nominal"] == cicilan_tetap, (
        "Nominal transaksi tidak sama dengan cicilan tetap"
    )

    assert transaksi["biaya"] == denda_diharapkan, (
        "Denda transaksi tidak sesuai"
    )

    assert transaksi["saldo_sumber_sebelum"] == saldo_sebelum, (
        "Snapshot saldo sebelum pembayaran salah"
    )

    assert transaksi["saldo_sumber_sesudah"] == saldo_diharapkan, (
        "Snapshot saldo setelah pembayaran salah"
    )

    assert transaksi["jenis_referensi"] == "pinjaman", (
        "Jenis referensi transaksi bukan pinjaman"
    )

    assert transaksi["id_referensi"] == ID_PINJAMAN, (
        "ID referensi transaksi salah"
    )

    assert len(daftar_riwayat) == 1, (
        "Jumlah riwayat terhubung bukan satu"
    )

    assert len(daftar_audit) == 1, (
        "Jumlah audit terhubung bukan satu"
    )

    jumlah_pembayaran_setelah = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM transaksi
        WHERE jenis = 'pembayaran_cicilan'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        """,
        (ID_PINJAMAN,)
    ).fetchone()["jumlah"]

    assert jumlah_pembayaran_setelah == (
        jumlah_pembayaran_sebelum + 1
    ), "Jumlah pembayaran tidak bertambah tepat satu"

finally:
    koneksi.close()


print()
print(
    "✅ PEMBAYARAN TERLAMBAT BERHASIL: denda, saldo, "
    "sisa pokok, jadwal, transaksi, riwayat, audit, "
    "dan objek Python tersimpan dengan benar"
)
