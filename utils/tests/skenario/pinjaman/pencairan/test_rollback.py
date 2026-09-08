"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.txt` (urutan 10).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from unittest.mock import patch

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


ID_PINJAMAN = 9
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot_database():
    """
    Mengambil keadaan database yang harus tetap sama apabila
    pencairan mengalami kegagalan dan di-rollback.
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

        jumlah_transaksi = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM transaksi"
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM riwayat"
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM audit"
        ).fetchone()["jumlah"]

        transaksi_pencairan = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'pencairan_pinjaman'
              AND jenis_referensi = 'pinjaman'
              AND id_referensi = ?
            """,
            (ID_PINJAMAN,)
        ).fetchone()["jumlah"]

        return {
            # Row diubah menjadi dictionary agar dapat dibandingkan
            # setelah koneksi database ditutup.
            "pinjaman": dict(data_pinjaman),
            "rekening": dict(data_rekening),
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "transaksi_pencairan": transaksi_pencairan
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
        "Objek pinjaman ID 9 tidak ditemukan"
    )


# Memastikan pinjaman belum pernah dicairkan.
assert pinjaman.status == StatusPinjaman.DISETUJUI, (
    "Pinjaman ID 9 belum berstatus disetujui"
)


# ============================================================
# 2. MENYIMPAN KONDISI AWAL
# ============================================================

snapshot_sebelum = ambil_snapshot_database()

snapshot_objek_sebelum = {
    "status_pinjaman": pinjaman.status,
    "cicilan_tetap": pinjaman.cicilan_tetap,
    "tanggal_pencairan": pinjaman.tanggal_pencairan,
    "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
    "sisa_pokok": pinjaman.sisa_pokok,
    "saldo_rekening": rekening.saldo,
    "jumlah_riwayat_objek": len(rekening.riwayat)
}


print("=== KONDISI SEBELUM PENCAIRAN ===")
print(snapshot_sebelum)
print()


# ============================================================
# 3. MEMBUAT KEGAGALAN AUDIT
# ============================================================

def gagalkan_audit(*args, **kwargs):
    """
    Menggantikan AuditRepository.tambah_audit untuk sementara.
    Saat service mencoba menyimpan audit, fungsi ini melempar error.
    """
    raise RuntimeError(
        "Kegagalan audit untuk menguji rollback pencairan pinjaman"
    )


# Patch hanya aktif di dalam blok with.
# Setelah blok selesai, method asli otomatis dikembalikan.
with patch.object(
    AuditRepository,
    "tambah_audit",
    side_effect=gagalkan_audit
):
    try:
        PinjamanService.cairkan_pinjaman(
            nasabah=nasabah,
            id_pinjaman=ID_PINJAMAN
        )

    except RuntimeError as error:
        assert str(error) == (
            "Kegagalan audit untuk menguji rollback "
            "pencairan pinjaman"
        )

        print("✅ Kegagalan buatan berhasil dipicu")
        print("Pesan error:", error)

    else:
        raise AssertionError(
            "Pencairan tetap berhasil meskipun audit digagalkan"
        )


# ============================================================
# 4. MEMBACA ULANG DATABASE SETELAH ROLLBACK
# ============================================================

snapshot_setelah = ambil_snapshot_database()

snapshot_objek_setelah = {
    "status_pinjaman": pinjaman.status,
    "cicilan_tetap": pinjaman.cicilan_tetap,
    "tanggal_pencairan": pinjaman.tanggal_pencairan,
    "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
    "sisa_pokok": pinjaman.sisa_pokok,
    "saldo_rekening": rekening.saldo,
    "jumlah_riwayat_objek": len(rekening.riwayat)
}


print()
print("=== KONDISI SETELAH ROLLBACK ===")
print(snapshot_setelah)
print()


# ============================================================
# 5. MEMERIKSA DATABASE
# ============================================================

assert snapshot_setelah["pinjaman"] == snapshot_sebelum["pinjaman"], (
    "Data pinjaman berubah meskipun transaksi di-rollback"
)

assert snapshot_setelah["rekening"] == snapshot_sebelum["rekening"], (
    "Saldo atau data rekening berubah meskipun transaksi di-rollback"
)

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi pencairan masih tersisa"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat pencairan masih tersisa"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Jumlah audit berubah setelah rollback"

assert snapshot_setelah["transaksi_pencairan"] == 0, (
    "Transaksi pencairan pinjaman ID 9 masih tersimpan"
)


# ============================================================
# 6. MEMERIKSA OBJEK PYTHON
# ============================================================

assert snapshot_objek_setelah == snapshot_objek_sebelum, (
    "State objek Python berubah meskipun pencairan gagal"
)


# Memastikan pinjaman masih dapat dicairkan nanti.
assert (
    snapshot_setelah["pinjaman"]["status"]
    == StatusPinjaman.DISETUJUI.value
), "Status pinjaman tidak kembali menjadi disetujui"


print(
    "\n✅ ROLLBACK PENCAIRAN PINJAMAN BERHASIL: "
    "pinjaman, saldo, transaksi, riwayat, audit, "
    "dan objek Python tidak berubah"
)
