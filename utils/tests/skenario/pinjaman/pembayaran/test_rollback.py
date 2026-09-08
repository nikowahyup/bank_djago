"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.txt` (urutan 14).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from unittest.mock import patch
import datetime

from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
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


def ambil_snapshot_database():
    """
    Mengambil kondisi yang harus tetap sama jika pembayaran
    cicilan mengalami rollback.
    """
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

        if data_pinjaman is None:
            raise AssertionError("Pinjaman ID 8 tidak ditemukan")

        if data_rekening is None:
            raise AssertionError("Rekening pengujian tidak ditemukan")

        jumlah_transaksi = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM transaksi"
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM riwayat"
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM audit"
        ).fetchone()["jumlah"]

        jumlah_pembayaran = koneksi.execute(
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
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "jumlah_pembayaran": jumlah_pembayaran
        }

    finally:
        koneksi.close()


# ============================================================
# 1. MEMUAT OBJEK YANG DIGUNAKAN SERVICE
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
# 2. MENYIMPAN KONDISI SEBELUM PEMBAYARAN
# ============================================================

snapshot_sebelum = ambil_snapshot_database()

assert snapshot_sebelum["pinjaman"]["status"] == "aktif", (
    "Pinjaman ID 8 tidak aktif"
)

assert snapshot_sebelum["pinjaman"]["cicilan_terbayar"] == 2, (
    "Pinjaman ID 8 bukan berada setelah cicilan kedua"
)


# Menggunakan tanggal jatuh tempo saat ini agar pembayaran
# sudah diperbolehkan dan dapat mencapai penyimpanan audit.
hari_pengujian = datetime.date.fromisoformat(
    snapshot_sebelum["pinjaman"]["tanggal_jatuh_tempo"]
)


snapshot_objek_sebelum = {
    "status": pinjaman.status,
    "sisa_pokok": pinjaman.sisa_pokok,
    "cicilan_terbayar": pinjaman.cicilan_terbayar,
    "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
    "saldo": rekening.saldo,
    "jumlah_riwayat": len(rekening.riwayat)
}


print("=== KONDISI SEBELUM PENGUJIAN ROLLBACK ===")
print("ID pinjaman       :", ID_PINJAMAN)
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
print("Hari pengujian    :", hari_pengujian)
print(
    "Jumlah pembayaran :",
    snapshot_sebelum["jumlah_pembayaran"]
)
print()


# ============================================================
# 3. MEMBUAT KEGAGALAN PADA PENYIMPANAN AUDIT
# ============================================================

def gagalkan_audit(*args, **kwargs):
    """
    Menggantikan AuditRepository.tambah_audit untuk sementara.

    Ketika service mencapai penyimpanan audit, error ini membuat
    seluruh transaksi SQLite harus di-rollback.
    """
    raise RuntimeError(
        "Kegagalan audit untuk menguji rollback pembayaran cicilan"
    )


with patch.object(
    AuditRepository,
    "tambah_audit",
    side_effect=gagalkan_audit
):
    try:
        PinjamanService.bayar_cicilan(
            id_pinjaman=ID_PINJAMAN,
            nasabah=nasabah,
            hari_ini=hari_pengujian
        )

    except RuntimeError as error:
        assert str(error) == (
            "Kegagalan audit untuk menguji rollback "
            "pembayaran cicilan"
        )

        print("✅ Kegagalan buatan berhasil dipicu")
        print("Pesan error:", error)

    else:
        raise AssertionError(
            "Pembayaran tetap berhasil meskipun audit digagalkan"
        )


# ============================================================
# 4. MEMBACA ULANG DATABASE SETELAH ROLLBACK
# ============================================================

snapshot_setelah = ambil_snapshot_database()

snapshot_objek_setelah = {
    "status": pinjaman.status,
    "sisa_pokok": pinjaman.sisa_pokok,
    "cicilan_terbayar": pinjaman.cicilan_terbayar,
    "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
    "saldo": rekening.saldo,
    "jumlah_riwayat": len(rekening.riwayat)
}


print()
print("=== KONDISI SETELAH ROLLBACK ===")
print(
    "Status pinjaman   :",
    snapshot_setelah["pinjaman"]["status"]
)
print(
    "Cicilan terbayar  :",
    snapshot_setelah["pinjaman"]["cicilan_terbayar"]
)
print(
    "Sisa pokok        :",
    snapshot_setelah["pinjaman"]["sisa_pokok"]
)
print(
    "Saldo rekening    :",
    snapshot_setelah["rekening"]["saldo"]
)
print(
    "Jumlah pembayaran :",
    snapshot_setelah["jumlah_pembayaran"]
)
print()


# ============================================================
# 5. MEMASTIKAN SELURUH DATABASE TIDAK BERUBAH
# ============================================================

assert (
    snapshot_setelah["pinjaman"]
    == snapshot_sebelum["pinjaman"]
), "Data pinjaman berubah setelah rollback"

assert (
    snapshot_setelah["rekening"]
    == snapshot_sebelum["rekening"]
), "Data rekening berubah setelah rollback"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi pembayaran masih tersisa"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat pembayaran masih tersisa"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Jumlah audit berubah setelah rollback"

assert (
    snapshot_setelah["jumlah_pembayaran"]
    == snapshot_sebelum["jumlah_pembayaran"]
), "Jumlah pembayaran cicilan ID 8 berubah"


# ============================================================
# 6. MEMASTIKAN OBJEK PYTHON TIDAK BERUBAH
# ============================================================

assert snapshot_objek_setelah == snapshot_objek_sebelum, (
    "State objek Python berubah meskipun pembayaran gagal"
)

assert pinjaman.status == StatusPinjaman.AKTIF, (
    "Status objek pinjaman tidak lagi aktif"
)

assert pinjaman.cicilan_terbayar == 2, (
    "Jumlah cicilan objek berubah setelah rollback"
)


print(
    "\n✅ ROLLBACK PEMBAYARAN CICILAN BERHASIL: "
    "saldo, sisa pokok, jumlah cicilan, jadwal, transaksi, "
    "riwayat, audit, dan objek Python tidak berubah"
)
