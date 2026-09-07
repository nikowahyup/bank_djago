"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 15).

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

JUMLAH_PEMBAYARAN = 4


def ambil_data():
    """Membaca kondisi terbaru pinjaman dan rekening dari SQLite."""
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

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'pembayaran_cicilan'
              AND jenis_referensi = 'pinjaman'
              AND id_referensi = ?
            """,
            (ID_PINJAMAN,)
        ).fetchone()["jumlah"]

        return {
            "pinjaman": dict(data_pinjaman),
            "rekening": dict(data_rekening),
            "jumlah_transaksi": jumlah_transaksi
        }

    finally:
        koneksi.close()


# ============================================================
# 1. MEMUAT OBJEK
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
# 2. MEMASTIKAN KONDISI AWAL
# ============================================================

kondisi_awal = ambil_data()
data_awal = kondisi_awal["pinjaman"]

assert data_awal["status"] == "aktif", (
    "Pinjaman ID 8 tidak aktif"
)

assert data_awal["cicilan_terbayar"] == 2, (
    "Pengujian harus dimulai setelah tepat dua cicilan"
)

sisa_cicilan = (
    data_awal["tenor"] - data_awal["cicilan_terbayar"]
)

assert sisa_cicilan == JUMLAH_PEMBAYARAN, (
    f"Sisa cicilan bukan {JUMLAH_PEMBAYARAN}"
)


saldo_awal = kondisi_awal["rekening"]["saldo"]
cicilan_tetap = data_awal["cicilan_tetap"]
jumlah_transaksi_awal = kondisi_awal["jumlah_transaksi"]

id_transaksi_baru = []


print("=== KONDISI AWAL PELUNASAN ===")
print("ID pinjaman       :", ID_PINJAMAN)
print("Tenor             :", data_awal["tenor"])
print("Cicilan terbayar  :", data_awal["cicilan_terbayar"])
print("Sisa pembayaran   :", sisa_cicilan)
print("Sisa pokok        :", data_awal["sisa_pokok"])
print("Saldo rekening    :", saldo_awal)
print()


# ============================================================
# 3. MEMBAYAR TEPAT EMPAT KALI
# ============================================================

for nomor_pembayaran in range(3, 7):
    kondisi_sebelum = ambil_data()
    pinjaman_sebelum = kondisi_sebelum["pinjaman"]

    # Memastikan loop tidak melompati atau mengulang cicilan.
    assert pinjaman_sebelum["cicilan_terbayar"] == (
        nomor_pembayaran - 1
    ), "Urutan pembayaran cicilan tidak sesuai"

    assert pinjaman_sebelum["status"] == "aktif", (
        "Pinjaman menjadi tidak aktif terlalu cepat"
    )

    # Pembayaran dilakukan tepat pada tanggal jatuh tempo.
    # Karena tidak terlambat, denda yang diharapkan adalah nol.
    hari_pembayaran = datetime.date.fromisoformat(
        pinjaman_sebelum["tanggal_jatuh_tempo"]
    )

    jumlah_transaksi_sebelum = (
        kondisi_sebelum["jumlah_transaksi"]
    )

    print(f"--- MEMBAYAR CICILAN KE-{nomor_pembayaran} ---")
    print("Hari pembayaran :", hari_pembayaran)
    print("Sisa pokok awal :", pinjaman_sebelum["sisa_pokok"])

    hasil = PinjamanService.bayar_cicilan(
        id_pinjaman=ID_PINJAMAN,
        nasabah=nasabah,
        hari_ini=hari_pembayaran
    )

    assert hasil is pinjaman, (
        "Service mengembalikan objek pinjaman yang berbeda"
    )

    kondisi_setelah = ambil_data()
    pinjaman_setelah = kondisi_setelah["pinjaman"]

    assert pinjaman_setelah["cicilan_terbayar"] == (
        nomor_pembayaran
    ), "Jumlah cicilan tidak bertambah tepat satu"

    assert kondisi_setelah["jumlah_transaksi"] == (
        jumlah_transaksi_sebelum + 1
    ), "Transaksi tidak bertambah tepat satu"

    # Mengambil transaksi yang baru saja dibuat.
    koneksi = buat_koneksi()

    try:
        transaksi_terbaru = koneksi.execute(
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

    finally:
        koneksi.close()

    if transaksi_terbaru is None:
        raise AssertionError(
            f"Transaksi cicilan ke-{nomor_pembayaran} tidak ditemukan"
        )

    assert transaksi_terbaru["nominal"] == cicilan_tetap, (
        "Nominal transaksi tidak sama dengan cicilan tetap"
    )

    assert transaksi_terbaru["biaya"] == 0, (
        "Pembayaran tepat waktu seharusnya tidak memiliki denda"
    )

    id_transaksi_baru.append(transaksi_terbaru["id"])

    print("Sisa pokok akhir :", pinjaman_setelah["sisa_pokok"])
    print("Status           :", pinjaman_setelah["status"])
    print("ID transaksi     :", transaksi_terbaru["id"])
    print()


# ============================================================
# 4. MEMERIKSA KONDISI SETELAH EMPAT PEMBAYARAN
# ============================================================

kondisi_akhir = ambil_data()
pinjaman_akhir = kondisi_akhir["pinjaman"]
rekening_akhir = kondisi_akhir["rekening"]

saldo_yang_diharapkan = (
    saldo_awal - (cicilan_tetap * JUMLAH_PEMBAYARAN)
)


assert pinjaman_akhir["cicilan_terbayar"] == 6, (
    "Jumlah cicilan terbayar bukan enam"
)

assert pinjaman_akhir["status"] == "lunas", (
    "Status pinjaman belum berubah menjadi lunas"
)

assert pinjaman_akhir["sisa_pokok"] == 0, (
    "Sisa pokok pinjaman belum menjadi nol"
)

assert rekening_akhir["saldo"] == saldo_yang_diharapkan, (
    "Saldo rekening setelah empat pembayaran tidak sesuai"
)

assert kondisi_akhir["jumlah_transaksi"] == (
    jumlah_transaksi_awal + JUMLAH_PEMBAYARAN
), "Jumlah transaksi tidak bertambah tepat empat"


# Memastikan objek Python juga diselaraskan.
assert pinjaman.status == StatusPinjaman.LUNAS, (
    "Status objek pinjaman belum menjadi lunas"
)

assert pinjaman.cicilan_terbayar == 6, (
    "Cicilan terbayar pada objek bukan enam"
)

assert pinjaman.sisa_pokok == 0, (
    "Sisa pokok pada objek belum menjadi nol"
)

assert rekening.saldo == saldo_yang_diharapkan, (
    "Saldo objek rekening tidak sesuai"
)


# ============================================================
# 5. MEMERIKSA RIWAYAT DAN AUDIT EMPAT TRANSAKSI
# ============================================================

koneksi = buat_koneksi()

try:
    for id_transaksi in id_transaksi_baru:
        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE transaksi_id = ?
            """,
            (id_transaksi,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE transaksi_id = ?
            """,
            (id_transaksi,)
        ).fetchone()["jumlah"]

        assert jumlah_riwayat == 1, (
            f"Transaksi {id_transaksi} tidak memiliki satu riwayat"
        )

        assert jumlah_audit == 1, (
            f"Transaksi {id_transaksi} tidak memiliki satu audit"
        )

    transaksi_pelunasan = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE id = ?
        """,
        (id_transaksi_baru[-1],)
    ).fetchone()

    riwayat_pelunasan = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        """,
        (id_transaksi_baru[-1],)
    ).fetchone()

    audit_pelunasan = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        """,
        (id_transaksi_baru[-1],)
    ).fetchone()

finally:
    koneksi.close()


assert transaksi_pelunasan["id_referensi"] == ID_PINJAMAN, (
    "Transaksi terakhir tidak menunjuk pinjaman ID 8"
)

assert "PELUNASAN PINJAMAN" in riwayat_pelunasan["log"], (
    "Riwayat terakhir bukan riwayat pelunasan"
)

assert "telah melunasi" in audit_pelunasan["log"], (
    "Audit terakhir bukan audit pelunasan"
)


print("=== KONDISI AKHIR ===")
print("Status pinjaman   :", pinjaman_akhir["status"])
print("Cicilan terbayar  :", pinjaman_akhir["cicilan_terbayar"])
print("Sisa pokok        :", pinjaman_akhir["sisa_pokok"])
print("Saldo rekening    :", rekening_akhir["saldo"])
print("Transaksi baru    :", id_transaksi_baru)
print()

print(
    "✅ EMPAT PEMBAYARAN BERHASIL: cicilan ke-3 sampai "
    "ke-6 tersimpan dan pinjaman ID 8 telah lunas"
)
