"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_penutupan.py` (urutan 3).

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
from bank_djago.services.rekening.pengajuan_service import (
    PengajuanService
)


norek_sumber = "2001842427316253"
norek_penerima = "3001781978899033"


def ambil_kondisi_database():
    koneksi = buat_koneksi()

    try:
        sumber = koneksi.execute(
            """
            SELECT norek, saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (norek_sumber,)
        ).fetchone()

        penerima = koneksi.execute(
            """
            SELECT norek, saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (norek_penerima,)
        ).fetchone()

        pengajuan = koneksi.execute(
            """
            SELECT id, status
            FROM pengajuan_rekening
            WHERE id = 8
            """
        ).fetchone()

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
            "saldo_sumber": sumber["saldo"],
            "status_sumber": sumber["status"],
            "saldo_penerima": penerima["saldo"],
            "status_penerima": penerima["status"],
            "status_pengajuan": pengajuan["status"],
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# ==========================================================
# Kondisi sebelum pengujian
# ==========================================================
kondisi_sebelum = ambil_kondisi_database()

print("=== KONDISI SEBELUM ===")
print(kondisi_sebelum)

assert kondisi_sebelum["saldo_sumber"] == 101_000_000
assert kondisi_sebelum["status_sumber"] == "aktif"
assert kondisi_sebelum["status_penerima"] == "aktif"
assert kondisi_sebelum["status_pengajuan"] == "disetujui"


koneksi = buat_koneksi()
# Muat objek rekening sumber.
rekening_sumber = RekeningLoader.muat_rekening(
    norek_sumber,koneksi
)


# ==========================================================
# Paksa kegagalan sebelum commit
# ==========================================================
try:
    with patch.object(
        AuditRepository,
        "tambah_audit",
        side_effect=RuntimeError(
            "Kegagalan audit untuk menguji rollback"
        )
    ):
        PengajuanService.selesaikan_penutupan(
            rekening=rekening_sumber,
            metode="transfer",
            norek_penerima=norek_penerima
        )

    raise AssertionError(
        "Service seharusnya gagal, tetapi justru berhasil"
    )

except RuntimeError as error:
    assert str(error) == (
        "Kegagalan audit untuk menguji rollback"
    )

    print("\n✅ Kegagalan buatan berhasil dipicu")
    print(f"Pesan error: {error}")


# ==========================================================
# Kondisi setelah rollback
# ==========================================================
kondisi_sesudah = ambil_kondisi_database()

print("\n=== KONDISI SETELAH ROLLBACK ===")
print(kondisi_sesudah)


# Seluruh keadaan database harus sama.
assert kondisi_sesudah == kondisi_sebelum

# Objek Python juga belum boleh berubah karena perubahan
# objek dilakukan setelah commit berhasil.
assert rekening_sumber.saldo == 101_000_000
assert rekening_sumber.status == "aktif"

print(
    "\n✅ ROLLBACK BERHASIL: saldo, status, pengajuan, "
    "transaksi, riwayat, dan audit tidak berubah"
)
