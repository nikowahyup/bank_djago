"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_load_untuk_biayaadmin.py` (urutan 5).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.biaya_admin_service import (
    BiayaAdminService
)
from bank_djago.utils.utility import JenisTransaksi, Utilitas


NOREK_PENGUJIAN = "4001701216150609"

SALDO_YANG_DIHARAPKAN = 498_000
PERIODE_YANG_DIHARAPKAN = "2027-04-06"


def muat_rekening():
    """Memuat objek rekening pengujian dari SQLite."""
    koneksi = buat_koneksi()

    try:
        return RekeningLoader.muat_rekening(
            norek=NOREK_PENGUJIAN,
            koneksi=koneksi
        )
    finally:
        koneksi.close()


def ambil_kondisi_database():
    """
    Mengambil snapshot database.

    Snapshot digunakan untuk membuktikan bahwa rekening,
    transaksi, riwayat, dan audit tidak berubah setelah rollback.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT
                norek,
                saldo,
                waktu_bayar_admin,
                status
            FROM rekening
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()

        transaksi = koneksi.execute(
            """
            SELECT
                id,
                jenis,
                norek_sumber,
                nominal,
                saldo_sumber_sebelum,
                saldo_sumber_sesudah
            FROM transaksi
            WHERE norek_sumber = ?
              AND jenis = ?
            ORDER BY id
            """,
            (
                NOREK_PENGUJIAN,
                JenisTransaksi.BIAYA_ADMIN.value
            )
        ).fetchall()

        riwayat = koneksi.execute(
            """
            SELECT
                id,
                transaksi_id,
                norek,
                kategori,
                jenis,
                waktu,
                log
            FROM riwayat
            WHERE norek = ?
            ORDER BY id
            """,
            (NOREK_PENGUJIAN,)
        ).fetchall()

        audit = koneksi.execute(
            """
            SELECT
                id,
                transaksi_id,
                norek,
                kategori,
                jenis,
                waktu,
                log
            FROM audit
            WHERE norek = ?
            ORDER BY id
            """,
            (NOREK_PENGUJIAN,)
        ).fetchall()

        return {
            "rekening": dict(rekening) if rekening else None,
            "transaksi": [
                dict(data) for data in transaksi
            ],
            "riwayat": [
                dict(data) for data in riwayat
            ],
            "audit": [
                dict(data) for data in audit
            ]
        }

    finally:
        koneksi.close()


rekening = muat_rekening()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )


# Memastikan pengujian dimulai dari keadaan yang kita kenal.
assert rekening.saldo == SALDO_YANG_DIHARAPKAN, (
    f"Saldo aktual Rp"
    f"{Utilitas.format_rupiah(rekening.saldo)}, "
    f"bukan Rp"
    f"{Utilitas.format_rupiah(SALDO_YANG_DIHARAPKAN)}"
)

assert rekening.waktu_bayar_admin.isoformat() == (
    PERIODE_YANG_DIHARAPKAN
), "Periode awal rekening tidak sesuai"


# Mensimulasikan satu periode berikutnya.
hari_simulasi = Utilitas.tambah_bulan(
    rekening.waktu_bayar_admin,
    1
)


# Menyimpan kondisi database dan objek sebelum kegagalan.
kondisi_database_sebelum = ambil_kondisi_database()

kondisi_objek_sebelum = {
    "saldo": rekening.saldo,
    "waktu_bayar_admin": rekening.waktu_bayar_admin,
    "riwayat": list(rekening.riwayat)
}


print("=== KONDISI SEBELUM PENGUJIAN ROLLBACK ===")
print("Nomor rekening       :", rekening.norek)
print("Saldo                :", rekening.saldo)
print("Periode terakhir     :", rekening.waktu_bayar_admin)
print("Hari simulasi        :", hari_simulasi)
print(
    "Jumlah transaksi    :",
    len(kondisi_database_sebelum["transaksi"])
)
print(
    "Jumlah riwayat      :",
    len(kondisi_database_sebelum["riwayat"])
)
print(
    "Jumlah audit        :",
    len(kondisi_database_sebelum["audit"])
)
print()


# Menyimpan method asli agar dapat dikembalikan
# setelah kegagalan buatan selesai.
tambah_audit_asli = AuditRepository.tambah_audit


def gagalkan_audit(*args, **kwargs):
    """
    Kegagalan buatan ini terjadi setelah perubahan rekening,
    transaksi, dan riwayat dilakukan dalam koneksi yang sama.
    """
    raise RuntimeError(
        "Kegagalan audit untuk menguji rollback biaya admin"
    )


kegagalan_berhasil_dipicu = False

try:
    # Mengganti sementara method penyimpanan audit
    # dengan method yang selalu gagal.
    AuditRepository.tambah_audit = gagalkan_audit

    try:
        BiayaAdminService.potong_admin(
            rekening=rekening,
            hari_ini=hari_simulasi
        )

    except RuntimeError as error:
        kegagalan_berhasil_dipicu = True

        print("✅ Kegagalan buatan berhasil dipicu")
        print("Pesan error:", error)
        print()

finally:
    # Method asli wajib dikembalikan agar pengujian lain
    # tidak ikut mengalami kegagalan buatan.
    AuditRepository.tambah_audit = tambah_audit_asli


assert kegagalan_berhasil_dipicu, (
    "Kegagalan audit tidak berhasil dipicu"
)


# Mengambil kembali keadaan setelah service melakukan rollback.
kondisi_database_sesudah = ambil_kondisi_database()

kondisi_objek_sesudah = {
    "saldo": rekening.saldo,
    "waktu_bayar_admin": rekening.waktu_bayar_admin,
    "riwayat": list(rekening.riwayat)
}


print("=== KONDISI SETELAH ROLLBACK ===")
print(
    "Saldo rekening      :",
    kondisi_database_sesudah["rekening"]["saldo"]
)
print(
    "Periode terakhir    :",
    kondisi_database_sesudah["rekening"]["waktu_bayar_admin"]
)
print(
    "Jumlah transaksi   :",
    len(kondisi_database_sesudah["transaksi"])
)
print(
    "Jumlah riwayat     :",
    len(kondisi_database_sesudah["riwayat"])
)
print(
    "Jumlah audit       :",
    len(kondisi_database_sesudah["audit"])
)
print()


# Seluruh isi database yang diamati harus sama persis.
assert (
    kondisi_database_sesudah
    == kondisi_database_sebelum
), (
    "Database berubah meskipun transaksi seharusnya "
    "sudah di-rollback"
)


# Objek Python juga tidak boleh berubah karena bagian
# sinkronisasi objek hanya dijalankan setelah commit.
assert kondisi_objek_sesudah == kondisi_objek_sebelum, (
    "State objek Python berubah meskipun proses gagal"
)


print(
    "✅ ROLLBACK BIAYA ADMIN BERHASIL: "
    "saldo, periode pembayaran, transaksi, riwayat, "
    "audit, dan objek Python tidak berubah"
)
