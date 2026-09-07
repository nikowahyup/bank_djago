"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_load_untuk_biayaadmin.py` (urutan 6).

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

SALDO_AWAL = 498_000
BIAYA_ADMIN = 2_000

JUMLAH_PERIODE_TERTUNGGAK = 250
JUMLAH_PERIODE_MAMPU = SALDO_AWAL // BIAYA_ADMIN

TOTAL_DIBAYAR = (
    JUMLAH_PERIODE_MAMPU
    * BIAYA_ADMIN
)

SALDO_AKHIR = SALDO_AWAL - TOTAL_DIBAYAR


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
    Mengambil keadaan rekening dan jumlah pencatatan
    untuk memeriksa perubahan yang terjadi.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT
                norek,
                saldo,
                status,
                waktu_bayar_admin
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

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()["jumlah"]

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


def ambil_pencatatan_terbaru():
    """Mengambil transaksi biaya admin terbaru dan catatan terkait."""
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


# Mencegah pengujian dijalankan setelah rekening berubah.
assert rekening.saldo == SALDO_AWAL, (
    f"Saldo aktual Rp"
    f"{Utilitas.format_rupiah(rekening.saldo)}, "
    f"bukan Rp{Utilitas.format_rupiah(SALDO_AWAL)}. "
    "Kemungkinan pengujian sudah pernah dijalankan."
)

assert rekening.biaya_admin == BIAYA_ADMIN, (
    "Biaya admin rekening tidak sesuai"
)


periode_sebelum = rekening.waktu_bayar_admin

# Membuat 250 periode tertunggak.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    JUMLAH_PERIODE_TERTUNGGAK
)

daftar_periode = BiayaAdminService.cari_periode_admin(
    waktu_bayar_admin=periode_sebelum,
    hari_ini=hari_simulasi
)

assert len(daftar_periode) == JUMLAH_PERIODE_TERTUNGGAK, (
    "Jumlah periode tertunggak tidak sesuai"
)


# Saldo hanya mampu membayar 249 dari 250 periode.
jumlah_periode_dibayar = min(
    len(daftar_periode),
    JUMLAH_PERIODE_MAMPU
)

assert jumlah_periode_dibayar == 249, (
    "Kemampuan pembayaran seharusnya 249 periode"
)


# Periode baru harus menunjuk periode ke-249,
# bukan periode ke-250 yang masih belum dibayar.
periode_terakhir_yang_diharapkan = (
    daftar_periode[jumlah_periode_dibayar - 1]
)

periode_yang_belum_dibayar = (
    daftar_periode[jumlah_periode_dibayar]
)

kondisi_sebelum = ambil_kondisi_database()


print("=== KONDISI SEBELUM PEMBAYARAN SEBAGIAN ===")
print("Nomor rekening      :", rekening.norek)
print("Saldo awal          :", rekening.saldo)
print("Biaya per bulan     :", rekening.biaya_admin)
print("Periode terakhir    :", periode_sebelum)
print("Hari simulasi       :", hari_simulasi)
print(
    "Periode tertunggak :",
    len(daftar_periode)
)
print(
    "Periode mampu bayar:",
    JUMLAH_PERIODE_MAMPU
)
print(
    "Periode tersisa    :",
    len(daftar_periode) - JUMLAH_PERIODE_MAMPU
)
print()


# Menjalankan pembayaran biaya admin.
total_dibayar = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_sesudah = ambil_kondisi_database()
data_rekening_sesudah = kondisi_sesudah["rekening"]


assert total_dibayar == TOTAL_DIBAYAR, (
    "Total biaya admin yang dibayar tidak sesuai"
)

assert total_dibayar == 498_000, (
    "Seharusnya rekening membayar Rp498.000"
)

assert data_rekening_sesudah["saldo"] == SALDO_AKHIR, (
    "Saldo SQLite seharusnya menjadi Rp0"
)

assert rekening.saldo == SALDO_AKHIR, (
    "Saldo objek Python seharusnya menjadi Rp0"
)

assert (
    data_rekening_sesudah["waktu_bayar_admin"]
    == periode_terakhir_yang_diharapkan.isoformat()
), "Periode terakhir di SQLite tidak sesuai"

assert (
    rekening.waktu_bayar_admin
    == periode_terakhir_yang_diharapkan
), "Periode terakhir pada objek Python tidak sesuai"

assert (
    kondisi_sesudah["jumlah_transaksi"]
    == kondisi_sebelum["jumlah_transaksi"] + 1
), "Seharusnya hanya terbentuk satu transaksi"

assert (
    kondisi_sesudah["jumlah_riwayat"]
    == kondisi_sebelum["jumlah_riwayat"] + 1
), "Seharusnya hanya terbentuk satu riwayat"

assert (
    kondisi_sesudah["jumlah_audit"]
    == kondisi_sebelum["jumlah_audit"] + 1
), "Seharusnya hanya terbentuk satu audit"


transaksi, daftar_riwayat, daftar_audit = (
    ambil_pencatatan_terbaru()
)

assert transaksi["nominal"] == TOTAL_DIBAYAR, (
    "Nominal transaksi tidak sesuai"
)

assert transaksi["saldo_sumber_sebelum"] == SALDO_AWAL, (
    "Saldo sumber sebelum transaksi tidak sesuai"
)

assert transaksi["saldo_sumber_sesudah"] == 0, (
    "Saldo sumber sesudah transaksi bukan Rp0"
)

assert len(daftar_riwayat) == 1, (
    "Transaksi tidak memiliki tepat satu riwayat"
)

assert len(daftar_audit) == 1, (
    "Transaksi tidak memiliki tepat satu audit"
)

assert "249 bulan" in daftar_riwayat[0]["log"], (
    "Jumlah periode tidak tercantum dalam riwayat"
)

assert "249 bulan" in daftar_audit[0]["log"], (
    "Jumlah periode tidak tercantum dalam audit"
)


print("=== KONDISI SETELAH PEMBAYARAN SEBAGIAN ===")
print("Periode dibayar :", jumlah_periode_dibayar)
print(
    "Total dibayar  : Rp"
    f"{Utilitas.format_rupiah(total_dibayar)}"
)
print(
    "Saldo akhir    : Rp"
    f"{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Periode terakhir:",
    rekening.waktu_bayar_admin
)
print(
    "Periode tertunggak:",
    periode_yang_belum_dibayar
)
print("ID transaksi   :", transaksi["id"])
print("Riwayat        :", daftar_riwayat[0]["log"])
print("Audit          :", daftar_audit[0]["log"])
print()


# Menyimpan kondisi setelah pembayaran pertama.
# Pemanggilan berikutnya tidak boleh mengubahnya.
kondisi_sebelum_panggilan_kedua = (
    ambil_kondisi_database()
)


# Pada hari simulasi yang sama masih ada satu periode tertunggak,
# tetapi saldo sudah Rp0 sehingga tidak mampu membayarnya.
hasil_kedua = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_setelah_panggilan_kedua = (
    ambil_kondisi_database()
)


assert hasil_kedua == 0, (
    "Service seharusnya mengembalikan 0 "
    "ketika saldo tidak mencukupi"
)

assert (
    kondisi_setelah_panggilan_kedua
    == kondisi_sebelum_panggilan_kedua
), (
    "Database berubah meskipun saldo tidak mampu "
    "membayar satu periode"
)

assert rekening.saldo == 0, (
    "Saldo objek Python berubah pada pemanggilan kedua"
)

assert (
    rekening.waktu_bayar_admin
    == periode_terakhir_yang_diharapkan
), (
    "Periode pembayaran tetap maju meskipun "
    "periode terakhir belum dibayar"
)


print(
    "✅ PEMBAYARAN SEBAGIAN BERHASIL: "
    "249 dari 250 periode dibayar, saldo menjadi Rp0, "
    "satu periode tetap tertunggak, dan pemanggilan "
    "berikutnya tidak mengubah data"
)
