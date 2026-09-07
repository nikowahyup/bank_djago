"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 12).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime
from unittest.mock import patch

from bank_djago.core.deposito import JenisAro
from bank_djago.penyimpanan.loaders.deposito_loader import (
    DepositoLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)


ID_DEPOSITO = 15
NOREK_PENGUJIAN = "3001781978899033"

TANGGAL_BUKA_AWAL = datetime.date(2026, 9, 4)
JATUH_TEMPO_AWAL = datetime.date(2026, 10, 4)

PESAN_ERROR = (
    "Kegagalan audit untuk menguji rollback ARO pokok+bunga"
)


def cari_deposito_aktif():
    """
    Memuat deposito aktif, kemudian mencari deposito ID 15.
    """
    daftar_deposito = (
        DepositoLoader.muat_semua_deposito_aktif()
    )

    return next(
        (
            deposito
            for deposito in daftar_deposito
            if deposito.ID == ID_DEPOSITO
        ),
        None
    )


def ambil_kondisi_database():
    """
    Mengambil kondisi penting dari SQLite.

    Kondisi sebelum dan setelah kegagalan harus sama persis
    apabila rollback bekerja dengan benar.
    """
    koneksi = buat_koneksi()

    try:
        deposito = koneksi.execute(
            """
            SELECT *
            FROM deposito
            WHERE id = ?
            """,
            (ID_DEPOSITO,)
        ).fetchone()

        rekening = koneksi.execute(
            """
            SELECT *
            FROM rekening
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()

        jumlah_transaksi = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM transaksi"
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM riwayat"
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM audit"
        ).fetchone()["jumlah"]

        transaksi_deposito = koneksi.execute(
            """
            SELECT *
            FROM transaksi
            WHERE jenis_referensi = 'deposito'
              AND id_referensi = ?
            ORDER BY id
            """,
            (ID_DEPOSITO,)
        ).fetchall()

        return {
            "deposito": dict(deposito),
            "rekening": dict(rekening),
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "transaksi_deposito": [
                dict(transaksi)
                for transaksi in transaksi_deposito
            ]
        }

    finally:
        koneksi.close()


def ambil_kondisi_objek(deposito):
    """
    Mengambil kondisi objek deposito dan rekening di memori.
    """
    return {
        "nominal": deposito.nominal,
        "bunga": deposito.bunga,
        "lama_bulan": deposito.lama_bulan,
        "tanggal_buka": deposito.tanggal_buka,
        "jatuh_tempo": deposito.jatuh_tempo,
        "status": deposito.status,
        "proses_aro": deposito.proses_aro,
        "saldo_rekening": deposito.rekening.saldo,
        "jumlah_riwayat_objek": len(
            deposito.rekening.riwayat
        )
    }


# ============================================================
# 1. MEMUAT DAN MEMERIKSA DEPOSITO
# ============================================================

deposito = cari_deposito_aktif()

if deposito is None:
    raise AssertionError(
        f"Deposito aktif ID {ID_DEPOSITO} tidak ditemukan"
    )

# Pemeriksaan ini mencegah deposito yang salah ikut diuji.
assert deposito.rekening.norek == NOREK_PENGUJIAN
assert deposito.nominal == 1_000_000
assert deposito.jenis_aro == JenisAro.POKOK_BUNGA
assert deposito.lama_bulan == 1
assert deposito.lama_aro == 1
assert deposito.tanggal_buka == TANGGAL_BUKA_AWAL
assert deposito.jatuh_tempo == JATUH_TEMPO_AWAL
assert deposito.proses_aro is None
assert deposito.status == StatusDeposito.AKTIF

print("✅ Deposito ID 15 siap untuk pengujian rollback")


# ============================================================
# 2. MENYIMPAN KONDISI SEBELUM PENGUJIAN
# ============================================================

database_sebelum = ambil_kondisi_database()
objek_sebelum = ambil_kondisi_objek(deposito)

print("\n=== KONDISI SEBELUM ===")
print(database_sebelum)


# ============================================================
# 3. MEMAKSA PENYIMPANAN AUDIT GAGAL
# ============================================================
#
# Audit berada dekat bagian akhir transaksi database.
# Saat audit gagal, perubahan deposito, transaksi, dan riwayat
# yang sebelumnya sudah dicoba harus ikut dibatalkan.
# ============================================================

error_dipicu = False

with patch.object(
    AuditRepository,
    "tambah_audit",
    side_effect=RuntimeError(PESAN_ERROR)
):
    try:
        DepositoService.perpanjangan(
            deposito=deposito,
            hari_ini=JATUH_TEMPO_AWAL
        )

    except RuntimeError as error:
        # Memastikan RuntimeError berasal dari kegagalan buatan.
        assert str(error) == PESAN_ERROR, (
            f"RuntimeError yang muncul berbeda: {error}"
        )

        error_dipicu = True

        print("\n✅ Kegagalan buatan berhasil dipicu")
        print("Pesan error:", error)


assert error_dipicu, (
    "Kegagalan audit tidak terjadi sehingga rollback belum diuji"
)


# ============================================================
# 4. MENGAMBIL KONDISI SETELAH ROLLBACK
# ============================================================

database_setelah = ambil_kondisi_database()
objek_setelah = ambil_kondisi_objek(deposito)

print("\n=== KONDISI SETELAH ROLLBACK ===")
print(database_setelah)


# ============================================================
# 5. MEMERIKSA DATABASE
# ============================================================

assert database_setelah["deposito"] == (
    database_sebelum["deposito"]
), "Data deposito berubah setelah rollback"

print("✅ Data deposito tidak berubah")


assert database_setelah["rekening"] == (
    database_sebelum["rekening"]
), "Data rekening berubah setelah rollback"

print("✅ Data dan saldo rekening tidak berubah")


assert database_setelah["jumlah_transaksi"] == (
    database_sebelum["jumlah_transaksi"]
), "Transaksi kapitalisasi masih tersimpan"

print("✅ Transaksi kapitalisasi tidak tersisa")


assert database_setelah["jumlah_riwayat"] == (
    database_sebelum["jumlah_riwayat"]
), "Riwayat ARO masih tersimpan"

print("✅ Riwayat ARO tidak tersisa")


assert database_setelah["jumlah_audit"] == (
    database_sebelum["jumlah_audit"]
), "Jumlah audit berubah setelah rollback"

print("✅ Audit tidak bertambah")


assert database_setelah["transaksi_deposito"] == (
    database_sebelum["transaksi_deposito"]
), "Daftar transaksi deposito ID 15 berubah"

print("✅ Transaksi deposito ID 15 tetap seperti semula")


# ============================================================
# 6. MEMERIKSA OBJEK DI MEMORI
# ============================================================
#
# Service memperbarui objek setelah commit berhasil.
# Karena terjadi error, objek seharusnya tidak berubah.
# ============================================================

assert objek_setelah == objek_sebelum, (
    "Objek deposito atau rekening berubah setelah rollback"
)

print("✅ Objek deposito dan rekening tidak berubah")


# ============================================================
# 7. MEMUAT ULANG HASIL DARI SQLITE
# ============================================================

deposito_muat_ulang = cari_deposito_aktif()

if deposito_muat_ulang is None:
    raise AssertionError(
        "Deposito ID 15 tidak ditemukan setelah rollback"
    )

assert deposito_muat_ulang.nominal == 1_000_000
assert deposito_muat_ulang.tanggal_buka == TANGGAL_BUKA_AWAL
assert deposito_muat_ulang.jatuh_tempo == JATUH_TEMPO_AWAL
assert deposito_muat_ulang.proses_aro is None
assert deposito_muat_ulang.status == StatusDeposito.AKTIF

print("✅ Data hasil pemuatan ulang tetap seperti kondisi awal")

print()
print(
    "✅ ROLLBACK ARO POKOK+BUNGA BERHASIL: "
    "deposito, rekening, transaksi, riwayat, audit, "
    "dan objek tidak berubah"
)
