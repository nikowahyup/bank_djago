"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 6).

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
from bank_djago.utils.utility import (
    JenisAro,
    JenisReferensiID,
    Utilitas
)


ID_DEPOSITO = 12
NOREK = "3001781978899033"
NOMINAL_DEPOSITO = 1_000_000


def ambil_kondisi_database():
    """
    Mengambil kondisi rekening, deposito, serta jumlah catatan
    yang terkait dengan deposito pengujian.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT saldo, status
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
            WHERE jenis_referensi = ?
              AND id_referensi = ?
            """,
            (
                JenisReferensiID.DEPOSITO.value,
                ID_DEPOSITO
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
    f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
)

# Pastikan tes tidak salah memilih jenis deposito.
assert deposito.rekening.norek == NOREK
assert deposito.nominal == NOMINAL_DEPOSITO
assert deposito.status == StatusDeposito.AKTIF
assert deposito.jenis_aro == JenisAro.POKOK
assert deposito.lama_bulan == 1
assert deposito.lama_aro == 1


# ==========================================================
# 2. Simpan kondisi sebelum ARO diproses
# ==========================================================
kondisi_sebelum = ambil_kondisi_database()

rekening_sebelum = kondisi_sebelum["rekening"]
deposito_sebelum = kondisi_sebelum["deposito"]

assert rekening_sebelum is not None
assert deposito_sebelum is not None

saldo_sebelum = rekening_sebelum["saldo"]
nominal_sebelum = deposito_sebelum["nominal"]
tanggal_buka_sebelum = deposito.tanggal_buka
jatuh_tempo_sebelum = deposito.jatuh_tempo

# Untuk ARO pokok, bunga periode lama masuk ke rekening.
bunga_yang_diharapkan = (
    deposito.total_pencairan - deposito.nominal
)

saldo_yang_diharapkan = (
    saldo_sebelum + bunga_yang_diharapkan
)

# Pokok deposito harus tetap sama.
nominal_yang_diharapkan = nominal_sebelum

# Periode baru dimulai dari jatuh tempo periode sebelumnya.
tanggal_buka_yang_diharapkan = jatuh_tempo_sebelum

jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
    tanggal_buka_yang_diharapkan,
    deposito.lama_aro
)

print("=== KONDISI SEBELUM ARO ===")
print(f"ID deposito          : {deposito.ID}")
print(f"Nominal deposito     : {nominal_sebelum}")
print(f"Saldo rekening       : {saldo_sebelum}")
print(f"Bunga yang diterima  : {bunga_yang_diharapkan}")
print(f"Tanggal buka         : {tanggal_buka_sebelum}")
print(f"Jatuh tempo          : {jatuh_tempo_sebelum}")


# ==========================================================
# 3. Jalankan ARO menggunakan tanggal simulasi
# ==========================================================
# Hari simulasi dibuat sama dengan tanggal jatuh tempo.
# Tanggal sistem dan main.py tidak berubah.
hari_simulasi = jatuh_tempo_sebelum

hasil = DepositoService.perpanjangan(
    deposito=deposito,
    hari_ini=hari_simulasi
)

assert hasil is True


# ==========================================================
# 4. Ambil kondisi setelah ARO
# ==========================================================
kondisi_sesudah = ambil_kondisi_database()

rekening_sesudah = kondisi_sesudah["rekening"]
deposito_sesudah = kondisi_sesudah["deposito"]


# ==========================================================
# 5. Cari transaksi ARO yang baru dibuat
# ==========================================================
koneksi = buat_koneksi()

try:
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = 'bunga_deposito'
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
        "Transaksi bunga deposito tidak ditemukan"
    )

    id_transaksi = transaksi["id"]

    # Satu kejadian ARO pokok menghasilkan dua riwayat:
    # riwayat bunga dan riwayat perpanjangan.
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    # Audit perpanjangan menunjuk transaksi bunga yang sama.
    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

finally:
    koneksi.close()


# ==========================================================
# 6. Tampilkan hasil
# ==========================================================
print("\n=== KONDISI SETELAH ARO ===")
print(f"Nominal deposito     : {deposito_sesudah['nominal']}")
print(f"Saldo rekening       : {rekening_sesudah['saldo']}")
print(f"Tanggal buka baru    : {deposito_sesudah['tanggal_buka']}")
print(f"Jatuh tempo baru     : {deposito_sesudah['jatuh_tempo']}")
print(f"Status deposito      : {deposito_sesudah['status']}")
print(f"Tanggal proses ARO   : {deposito_sesudah['proses_aro']}")

print("\n=== DATA TRANSAKSI ===")
print(f"ID transaksi         : {transaksi['id']}")
print(f"Jenis                : {transaksi['jenis']}")
print(f"Rekening sumber      : {transaksi['norek_sumber']}")
print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
print(f"Nominal              : {transaksi['nominal']}")
print(
    f"Saldo tujuan sebelum : "
    f"{transaksi['saldo_tujuan_sebelum']}"
)
print(
    f"Saldo tujuan sesudah : "
    f"{transaksi['saldo_tujuan_sesudah']}"
)
print(f"Jenis referensi      : {transaksi['jenis_referensi']}")
print(f"ID referensi         : {transaksi['id_referensi']}")
print(f"Waktu                : {transaksi['waktu']}")

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
# 7. Periksa perubahan rekening
# ==========================================================
assert rekening_sesudah["saldo"] == (
    saldo_yang_diharapkan
)
assert rekening_sesudah["status"] == "aktif"


# ==========================================================
# 8. Periksa perubahan deposito
# ==========================================================
# Pada ARO pokok, nominal deposito tidak bertambah.
assert deposito_sesudah["nominal"] == (
    nominal_yang_diharapkan
)

assert deposito_sesudah["lama_bulan"] == 1
assert deposito_sesudah["bunga"] == 0.03
assert deposito_sesudah["status"] == StatusDeposito.AKTIF

assert deposito_sesudah["tanggal_buka"] == (
    tanggal_buka_yang_diharapkan.isoformat()
)

assert deposito_sesudah["jatuh_tempo"] == (
    jatuh_tempo_yang_diharapkan.isoformat()
)

assert deposito_sesudah["proses_aro"] == (
    hari_simulasi.isoformat()
)


# ==========================================================
# 9. Periksa transaksi bunga
# ==========================================================
assert transaksi["jenis"] == "bunga_deposito"
assert transaksi["norek_sumber"] is None
assert transaksi["norek_tujuan"] == NOREK
assert transaksi["nominal"] == bunga_yang_diharapkan

assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum
assert transaksi["saldo_tujuan_sesudah"] == (
    saldo_yang_diharapkan
)

assert transaksi["saldo_sumber_sebelum"] is None
assert transaksi["saldo_sumber_sesudah"] is None

assert str(transaksi["jenis_referensi"]) == str(
    JenisReferensiID.DEPOSITO.value
)

assert transaksi["id_referensi"] == ID_DEPOSITO
assert transaksi["waktu"] is not None


# ==========================================================
# 10. Periksa hubungan audit dan riwayat
# ==========================================================
assert len(daftar_riwayat) == 2
assert len(daftar_audit) == 1

assert all(
    riwayat["transaksi_id"] == id_transaksi
    for riwayat in daftar_riwayat
)

assert daftar_audit[0]["transaksi_id"] == id_transaksi


# ==========================================================
# 11. Periksa jumlah data yang bertambah
# ==========================================================
assert kondisi_sesudah["jumlah_transaksi"] == (
    kondisi_sebelum["jumlah_transaksi"] + 1
)

assert kondisi_sesudah["jumlah_riwayat"] == (
    kondisi_sebelum["jumlah_riwayat"] + 2
)

assert kondisi_sesudah["jumlah_audit"] == (
    kondisi_sebelum["jumlah_audit"] + 1
)


# ==========================================================
# 12. Periksa state objek Python
# ==========================================================
assert deposito.rekening.saldo == saldo_yang_diharapkan
assert deposito.nominal == nominal_yang_diharapkan
assert deposito.tanggal_buka == tanggal_buka_yang_diharapkan
assert deposito.jatuh_tempo == jatuh_tempo_yang_diharapkan
assert deposito.status == StatusDeposito.AKTIF
assert deposito.proses_aro == hari_simulasi


print(
    "\n✅ ARO POKOK BERHASIL: bunga masuk ke rekening, "
    "pokok tetap, periode diperpanjang, dan seluruh catatan "
    "terhubung ke transaksi yang sama"
)
