"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from unittest.mock import patch

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    JenisAro
)


norek = "3001781978899033"
nominal_deposito = 1_000_000


def ambil_kondisi_database():
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (norek,)
        ).fetchone()

        jumlah_deposito = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM deposito
            WHERE norek = ?
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            """
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            """
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            """
        ).fetchone()["jumlah"]

        return {
            "saldo": rekening["saldo"],
            "status": rekening["status"],
            "jumlah_deposito": jumlah_deposito,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# ==========================================================
# 1. Simpan kondisi sebelum pengujian
# ==========================================================
kondisi_sebelum = ambil_kondisi_database()

print("=== KONDISI SEBELUM ===")
print(kondisi_sebelum)

assert kondisi_sebelum["saldo"] == 7_890_011
assert kondisi_sebelum["status"] == "aktif"


koneksi = buat_koneksi()
# ==========================================================
# 2. Muat objek rekening
# ==========================================================
rekening = RekeningLoader.muat_rekening(norek,koneksi)

saldo_objek_sebelum = rekening.saldo
jumlah_deposito_objek_sebelum = len(
    rekening.pemilik.deposito
)


# ==========================================================
# 3. Paksa penyimpanan audit gagal
# ==========================================================
try:
    with patch.object(
        AuditRepository,
        "tambah_audit",
        side_effect=RuntimeError(
            "Kegagalan audit untuk menguji rollback deposito"
        )
    ):
        DepositoService.buka_deposito(
            rekening=rekening,
            nominal=nominal_deposito,
            lama_bulan=1,
            jenis_aro=JenisAro.TIDAK
        )

    raise AssertionError(
        "Pembukaan deposito seharusnya gagal"
    )

except RuntimeError as error:
    assert str(error) == (
        "Kegagalan audit untuk menguji rollback deposito"
    )

    print("\n✅ Kegagalan buatan berhasil dipicu")
    print(f"Pesan error: {error}")


# ==========================================================
# 4. Ambil kondisi setelah rollback
# ==========================================================
kondisi_sesudah = ambil_kondisi_database()

print("\n=== KONDISI SETELAH ROLLBACK ===")
print(kondisi_sesudah)


# ==========================================================
# 5. Pastikan database tidak berubah
# ==========================================================
assert kondisi_sesudah == kondisi_sebelum


# ==========================================================
# 6. Pastikan objek Python tidak berubah
# ==========================================================
assert rekening.saldo == saldo_objek_sebelum

assert len(rekening.pemilik.deposito) == (
    jumlah_deposito_objek_sebelum
)

print(
    "\n✅ ROLLBACK DEPOSITO BERHASIL: saldo, deposito, "
    "transaksi, riwayat, audit, dan objek tidak berubah"
)
