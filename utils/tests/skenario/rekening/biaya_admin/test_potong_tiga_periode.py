"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_load_untuk_biayaadmin.py` (urutan 4).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.biaya_admin_service import (
    BiayaAdminService
)
from bank_djago.utils.utility import JenisTransaksi, Utilitas


NOREK_PENGUJIAN = "4001701216150609"

SALDO_AWAL = 504_000
BIAYA_ADMIN_PER_BULAN = 2_000
JUMLAH_PERIODE = 3

TOTAL_BIAYA = BIAYA_ADMIN_PER_BULAN * JUMLAH_PERIODE
SALDO_AKHIR = SALDO_AWAL - TOTAL_BIAYA


def muat_rekening():
    """Memuat rekening pengujian sebagai objek Python."""
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
    Mengambil keadaan rekening dan jumlah transaksi biaya admin
    untuk membandingkan kondisi sebelum dan sesudah pemrosesan.
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

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE norek_sumber = ?
              AND jenis = ?
            """,
            (
                NOREK_PENGUJIAN,
                JenisTransaksi.BIAYA_ADMIN.value
            )
        ).fetchone()["jumlah"]

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi
        }

    finally:
        koneksi.close()


def ambil_pencatatan_terbaru():
    """Mengambil transaksi terbaru beserta riwayat dan auditnya."""
    koneksi = buat_koneksi()

    try:
        transaksi = koneksi.execute(
            """
            SELECT *
            FROM transaksi
            WHERE norek_sumber = ?
              AND jenis = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                NOREK_PENGUJIAN,
                JenisTransaksi.BIAYA_ADMIN.value
            )
        ).fetchone()

        if transaksi is None:
            raise AssertionError(
                "Transaksi biaya admin tidak ditemukan"
            )

        riwayat = koneksi.execute(
            """
            SELECT *
            FROM riwayat
            WHERE transaksi_id = ?
            """,
            (transaksi["id"],)
        ).fetchall()

        audit = koneksi.execute(
            """
            SELECT *
            FROM audit
            WHERE transaksi_id = ?
            """,
            (transaksi["id"],)
        ).fetchall()

        return transaksi, riwayat, audit

    finally:
        koneksi.close()


rekening = muat_rekening()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )


# Pengamanan agar pengujian tidak dijalankan dua kali
# pada rekening yang sudah berubah.
assert rekening.saldo == SALDO_AWAL, (
    f"Saldo aktual Rp{Utilitas.format_rupiah(rekening.saldo)}, "
    f"bukan Rp{Utilitas.format_rupiah(SALDO_AWAL)}. "
    "Kemungkinan pengujian sudah pernah dijalankan."
)

assert rekening.biaya_admin == BIAYA_ADMIN_PER_BULAN, (
    "Biaya admin rekening tidak sesuai"
)


periode_sebelum = rekening.waktu_bayar_admin

# Bergerak tiga bulan dari periode terakhir:
# 6 Oktober 2026 → 6 Januari 2027.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    JUMLAH_PERIODE
)

daftar_periode = BiayaAdminService.cari_periode_admin(
    waktu_bayar_admin=periode_sebelum,
    hari_ini=hari_simulasi
)

assert len(daftar_periode) == JUMLAH_PERIODE, (
    "Method cari_periode_admin tidak menghasilkan tiga periode"
)

kondisi_sebelum = ambil_kondisi_database()


print("=== KONDISI SEBELUM PEMBAYARAN ===")
print("Nomor rekening   :", rekening.norek)
print("Saldo awal       :", rekening.saldo)
print("Biaya per bulan  :", rekening.biaya_admin)
print("Periode terakhir :", periode_sebelum)
print("Hari simulasi    :", hari_simulasi)
print("Periode tertunggak:")

for periode in daftar_periode:
    print("-", periode)

print()


# Membayar tiga periode sekaligus.
total_dibayar = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_sesudah = ambil_kondisi_database()
data_rekening_sesudah = kondisi_sesudah["rekening"]


assert total_dibayar == TOTAL_BIAYA, (
    f"Total pembayaran seharusnya Rp"
    f"{Utilitas.format_rupiah(TOTAL_BIAYA)}"
)

assert data_rekening_sesudah["saldo"] == SALDO_AKHIR, (
    "Saldo SQLite setelah pembayaran tidak sesuai"
)

assert rekening.saldo == SALDO_AKHIR, (
    "Saldo objek Python tidak ikut diperbarui"
)

assert (
    data_rekening_sesudah["waktu_bayar_admin"]
    == hari_simulasi.isoformat()
), "Periode terakhir di SQLite tidak sesuai"

assert rekening.waktu_bayar_admin == hari_simulasi, (
    "Periode terakhir pada objek Python tidak sesuai"
)

assert (
    kondisi_sesudah["jumlah_transaksi"]
    == kondisi_sebelum["jumlah_transaksi"] + 1
), "Pembayaran tiga bulan harus menghasilkan satu transaksi"


transaksi, daftar_riwayat, daftar_audit = (
    ambil_pencatatan_terbaru()
)


assert transaksi["nominal"] == TOTAL_BIAYA, (
    "Nominal transaksi bukan total tiga bulan"
)

assert transaksi["saldo_sumber_sebelum"] == SALDO_AWAL, (
    "Saldo sebelum pada transaksi tidak sesuai"
)

assert transaksi["saldo_sumber_sesudah"] == SALDO_AKHIR, (
    "Saldo sesudah pada transaksi tidak sesuai"
)

assert len(daftar_riwayat) == 1, (
    "Transaksi harus mempunyai tepat satu riwayat"
)

assert len(daftar_audit) == 1, (
    "Transaksi harus mempunyai tepat satu audit"
)

assert "3 bulan" in daftar_riwayat[0]["log"], (
    "Jumlah periode tidak tercantum dalam riwayat"
)

assert "3 bulan" in daftar_audit[0]["log"], (
    "Jumlah periode tidak tercantum dalam audit"
)


print("=== KONDISI SETELAH PEMBAYARAN ===")
print("Periode dibayar :", JUMLAH_PERIODE)
print(
    "Total dibayar  : Rp"
    f"{Utilitas.format_rupiah(total_dibayar)}"
)
print(
    "Saldo SQLite   : Rp"
    f"{Utilitas.format_rupiah(data_rekening_sesudah['saldo'])}"
)
print(
    "Saldo objek    : Rp"
    f"{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Periode terakhir:",
    data_rekening_sesudah["waktu_bayar_admin"]
)
print("ID transaksi   :", transaksi["id"])
print("Riwayat        :", daftar_riwayat[0]["log"])
print("Audit          :", daftar_audit[0]["log"])
print()


# Memastikan pemanggilan ulang pada hari yang sama
# tidak membuat pemotongan kedua.
hasil_kedua = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_terakhir = ambil_kondisi_database()

assert hasil_kedua == 0, (
    "Pemanggilan kedua seharusnya tidak memotong biaya"
)

assert kondisi_terakhir == kondisi_sesudah, (
    "Data berubah saat service dipanggil kedua kali"
)


print(
    "✅ PEMBAYARAN TIGA PERIODE BERHASIL: "
    "Rp6.000 dipotong dalam satu transaksi, "
    "periode terakhir diperbarui, pencatatan terhubung, "
    "dan pemanggilan kedua tidak memotong ulang"
)
