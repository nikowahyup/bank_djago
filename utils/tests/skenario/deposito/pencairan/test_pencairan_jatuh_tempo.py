"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 4).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.loaders.deposito_loader import (
    DepositoLoader
)
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)
from bank_djago.utils.utility import JenisReferensiID


ID_DEPOSITO = 10
NOREK = "3001781978899033"


def ambil_kondisi_database():
    """
    Mengambil kondisi terbaru langsung dari SQLite.

    Data ini digunakan untuk membandingkan kondisi rekening
    dan deposito sebelum serta sesudah pencairan.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT norek, saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (NOREK,)
        ).fetchone()

        deposito = koneksi.execute(
            """
            SELECT *
            FROM deposito
            WHERE id = ?
            """,
            (ID_DEPOSITO,)
        ).fetchone()

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE id_referensi = ?
              AND jenis_referensi = ?
            """,
            (
                ID_DEPOSITO,
                JenisReferensiID.DEPOSITO.value
            )
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
            """,
            (NOREK,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
            """,
            (NOREK,)
        ).fetchone()["jumlah"]

        return {
            "rekening": rekening,
            "deposito": deposito,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# ==========================================================
# 1. Muat deposito aktif dari SQLite
# ==========================================================
# Loader membentuk kembali objek deposito beserta rekening
# dan nasabahnya tanpa melewati main.py.
daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()

deposito = next(
    (
        item
        for item in daftar_deposito
        if item.ID == ID_DEPOSITO
    ),
    None
)

assert deposito is not None, (
    f"Deposito ber-ID {ID_DEPOSITO} tidak ditemukan "
    "dalam daftar deposito aktif"
)


# ==========================================================
# 2. Simpan kondisi awal
# ==========================================================
kondisi_sebelum = ambil_kondisi_database()

rekening_sebelum = kondisi_sebelum["rekening"]
deposito_sebelum = kondisi_sebelum["deposito"]

assert rekening_sebelum is not None, (
    "Rekening pengujian tidak ditemukan"
)

assert deposito_sebelum is not None, (
    "Deposito pengujian tidak ditemukan"
)

assert deposito_sebelum["status"] == StatusDeposito.AKTIF, (
    "Deposito sudah tidak aktif. "
    "Gunakan deposito aktif yang belum pernah dicairkan."
)

assert deposito_sebelum["jenis_aro"] == "tidak", (
    "Pengujian ini khusus deposito non-ARO"
)

saldo_sebelum = rekening_sebelum["saldo"]

# Properti total_pencairan menghitung pokok ditambah bunga.
total_pencairan_yang_diharapkan = deposito.total_pencairan
saldo_sesudah_yang_diharapkan = (
    saldo_sebelum + total_pencairan_yang_diharapkan
)

print("=== KONDISI SEBELUM ===")
print(f"ID deposito       : {deposito.ID}")
print(f"Status deposito   : {deposito.status}")
print(f"Tanggal buka      : {deposito.tanggal_buka}")
print(f"Jatuh tempo       : {deposito.jatuh_tempo}")
print(f"Nominal deposito  : {deposito.nominal}")
print(f"Total pencairan   : {total_pencairan_yang_diharapkan}")
print(f"Saldo rekening    : {saldo_sebelum}")


# ==========================================================
# 3. Manipulasi waktu di dalam file pengujian
# ==========================================================
# Kita menggunakan tanggal jatuh tempo milik deposito sebagai
# hari simulasi. Tanggal sistem dan main.py tidak berubah.
hari_simulasi = deposito.jatuh_tempo

print("\n=== WAKTU SIMULASI ===")
print(f"Hari simulasi     : {hari_simulasi}")


# ==========================================================
# 4. Ubah deposito dari aktif menjadi jatuh tempo
# ==========================================================
# Ini meniru tindakan scheduler saat tanggal jatuh tempo tiba.
DepositoService.tandai_jatuh_tempo(
    deposito=deposito,
    hari_ini=hari_simulasi
)

assert deposito.status == StatusDeposito.JATUH_TEMPO, (
    "Status objek deposito gagal berubah menjadi jatuh tempo"
)

# Periksa SQLite juga, bukan hanya objek Python.
koneksi = buat_koneksi()

try:
    status_database = koneksi.execute(
        """
        SELECT status
        FROM deposito
        WHERE id = ?
        """,
        (ID_DEPOSITO,)
    ).fetchone()["status"]

finally:
    koneksi.close()

assert status_database == StatusDeposito.JATUH_TEMPO, (
    "Status deposito dalam database belum jatuh tempo"
)

print(
    "\n✅ Deposito berhasil ditandai jatuh tempo "
    "menggunakan tanggal simulasi"
)


# ==========================================================
# 5. Cairkan deposito pada hari simulasi
# ==========================================================
hasil_pencairan = DepositoService.cairkan_deposito(
    deposito=deposito,
    hari_ini=hari_simulasi
)

assert hasil_pencairan == total_pencairan_yang_diharapkan, (
    "Nilai yang dikembalikan service tidak sesuai "
    "dengan total pencairan"
)


# ==========================================================
# 6. Ambil kondisi setelah pencairan
# ==========================================================
kondisi_sesudah = ambil_kondisi_database()

rekening_sesudah = kondisi_sesudah["rekening"]
deposito_sesudah = kondisi_sesudah["deposito"]


# Cari transaksi pencairan yang merujuk deposito ID 10.
koneksi = buat_koneksi()

try:
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = 'pencairan_deposito'
          AND jenis_referensi = ?
          AND id_referensi = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisReferensiID.DEPOSITO.value,
            ID_DEPOSITO
        )
    ).fetchone()

    assert transaksi is not None, (
        "Transaksi pencairan deposito tidak ditemukan"
    )

    id_transaksi = transaksi["id"]

    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    # Setelah pencairan, tidak boleh ada notifikasi yang masih
    # menunjuk deposito tersebut.
    jumlah_notifikasi = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM notifikasi
        WHERE jenis_referensi = ?
          AND id_objek = ?
        """,
        (
            JenisReferensiID.DEPOSITO.value,
            ID_DEPOSITO
        )
    ).fetchone()["jumlah"]

finally:
    koneksi.close()


# ==========================================================
# 7. Tampilkan hasil pencairan
# ==========================================================
print("\n=== KONDISI SETELAH PENCAIRAN ===")
print(f"Status deposito       : {deposito_sesudah['status']}")
print(f"Saldo rekening        : {rekening_sesudah['saldo']}")

print("\n=== DATA TRANSAKSI ===")
print(f"ID transaksi          : {transaksi['id']}")
print(f"Jenis                 : {transaksi['jenis']}")
print(f"Rekening sumber       : {transaksi['norek_sumber']}")
print(f"Rekening tujuan       : {transaksi['norek_tujuan']}")
print(f"Nominal               : {transaksi['nominal']}")
print(
    f"Saldo tujuan sebelum  : "
    f"{transaksi['saldo_tujuan_sebelum']}"
)
print(
    f"Saldo tujuan sesudah  : "
    f"{transaksi['saldo_tujuan_sesudah']}"
)
print(
    f"Jenis referensi       : "
    f"{transaksi['jenis_referensi']}"
)
print(f"ID referensi          : {transaksi['id_referensi']}")
print(f"Waktu                 : {transaksi['waktu']}")

print("\n=== RIWAYAT TERHUBUNG ===")

for riwayat in daftar_riwayat:
    print(
        f"ID {riwayat['id']} | "
        f"Transaksi {riwayat['transaksi_id']} | "
        f"{riwayat['jenis']} | "
        f"{riwayat['log']}"
    )

print("\n=== AUDIT TERHUBUNG ===")

for audit in daftar_audit:
    print(
        f"ID {audit['id']} | "
        f"Transaksi {audit['transaksi_id']} | "
        f"{audit['jenis']} | "
        f"{audit['log']}"
    )


# ==========================================================
# 8. Periksa perubahan rekening dan deposito
# ==========================================================
assert deposito_sesudah["status"] == (
    StatusDeposito.DICAIRKAN
)

assert rekening_sesudah["saldo"] == (
    saldo_sesudah_yang_diharapkan
)

assert deposito.status == StatusDeposito.DICAIRKAN
assert deposito.rekening.saldo == saldo_sesudah_yang_diharapkan


# ==========================================================
# 9. Periksa isi transaksi
# ==========================================================
assert transaksi["jenis"] == "pencairan_deposito"

# Pencairan merupakan uang masuk, sehingga rekening berada
# pada kolom tujuan dan kolom sumber harus kosong.
assert transaksi["norek_sumber"] is None
assert transaksi["norek_tujuan"] == NOREK

assert transaksi["nominal"] == (
    total_pencairan_yang_diharapkan
)

assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum
assert transaksi["saldo_tujuan_sesudah"] == (
    saldo_sesudah_yang_diharapkan
)

assert transaksi["saldo_sumber_sebelum"] is None
assert transaksi["saldo_sumber_sesudah"] is None

assert str(transaksi["jenis_referensi"]) == str(
    JenisReferensiID.DEPOSITO.value
)

assert transaksi["id_referensi"] == ID_DEPOSITO
assert transaksi["waktu"] is not None


# ==========================================================
# 10. Periksa audit, riwayat, dan notifikasi
# ==========================================================
assert len(daftar_riwayat) == 1
assert len(daftar_audit) == 1

assert daftar_riwayat[0]["norek"] == NOREK
assert daftar_riwayat[0]["transaksi_id"] == id_transaksi

assert daftar_audit[0]["norek"] == NOREK
assert daftar_audit[0]["transaksi_id"] == id_transaksi

assert jumlah_notifikasi == 0, (
    "Notifikasi deposito belum terhapus setelah pencairan"
)


# Pembukaan sudah menghasilkan satu transaksi. Pencairan
# harus menambahkan tepat satu transaksi lagi untuk deposito.
assert kondisi_sesudah["jumlah_transaksi"] == (
    kondisi_sebelum["jumlah_transaksi"] + 1
)

assert kondisi_sesudah["jumlah_riwayat"] == (
    kondisi_sebelum["jumlah_riwayat"] + 1
)

assert kondisi_sesudah["jumlah_audit"] == (
    kondisi_sebelum["jumlah_audit"] + 1
)

print(
    "\n✅ Pencairan deposito dengan waktu simulasi "
    "tersimpan dengan benar"
)
