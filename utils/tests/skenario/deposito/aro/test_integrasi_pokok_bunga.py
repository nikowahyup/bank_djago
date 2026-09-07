"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 10).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.deposito_loader import (
    DepositoLoader
)
from bank_djago.penyimpanan.sqlite.database import (
    buat_koneksi
)
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)
from bank_djago.core.deposito import JenisAro
from bank_djago.utils.utility import (
    JenisReferensi,
    JenisTransaksi,
    Utilitas
)


ID_DEPOSITO = 14
NOREK_PENGUJIAN = "3001781978899033"

TANGGAL_BUKA_AWAL = datetime.date(2026, 9, 4)
JATUH_TEMPO_AWAL = datetime.date(2026, 10, 4)


def cari_deposito_aktif(id_deposito):
    """
    Memuat seluruh deposito aktif, lalu mencari objek deposito
    berdasarkan ID.
    """
    daftar_deposito = (
        DepositoLoader.muat_semua_deposito_aktif()
    )

    return next(
        (
            deposito
            for deposito in daftar_deposito
            if deposito.ID == id_deposito
        ),
        None
    )


def hitung_jumlah_data():
    """
    Menghitung jumlah transaksi, riwayat, dan audit sebelum
    serta setelah proses ARO.
    """
    koneksi = buat_koneksi()

    try:
        return {
            "transaksi": koneksi.execute(
                "SELECT COUNT(*) AS jumlah FROM transaksi"
            ).fetchone()["jumlah"],

            "riwayat": koneksi.execute(
                "SELECT COUNT(*) AS jumlah FROM riwayat"
            ).fetchone()["jumlah"],

            "audit": koneksi.execute(
                "SELECT COUNT(*) AS jumlah FROM audit"
            ).fetchone()["jumlah"]
        }

    finally:
        koneksi.close()


# ============================================================
# 1. MEMUAT DEPOSITO YANG AKAN DIPROSES
# ============================================================

deposito = cari_deposito_aktif(ID_DEPOSITO)

if deposito is None:
    raise AssertionError(
        f"Deposito aktif ID {ID_DEPOSITO} tidak ditemukan"
    )

rekening = deposito.rekening


# ============================================================
# 2. PENGAMAN SEBELUM PERPANJANGAN
# ============================================================
#
# Semua assertion ini berjalan sebelum service dipanggil.
# Jika pengujian dijalankan lagi, kondisi deposito sudah berubah
# sehingga proses akan berhenti di sini.
# ============================================================

assert rekening.norek == NOREK_PENGUJIAN, (
    "Deposito terhubung dengan rekening yang salah"
)

assert deposito.nominal == 1_000_000, (
    "Nominal deposito bukan nominal awal Rp1.000.000. "
    "Kemungkinan pengujian sudah pernah dijalankan."
)

assert deposito.jenis_aro == JenisAro.POKOK_BUNGA, (
    "Jenis ARO deposito bukan pokok+bunga"
)

assert deposito.lama_bulan == 1, (
    "Tenor awal deposito bukan satu bulan"
)

assert deposito.lama_aro == 1, (
    "Lama perpanjangan bukan satu bulan"
)

assert deposito.tanggal_buka == TANGGAL_BUKA_AWAL, (
    "Tanggal buka sudah berubah. "
    "Kemungkinan deposito pernah diperpanjang."
)

assert deposito.jatuh_tempo == JATUH_TEMPO_AWAL, (
    "Jatuh tempo sudah berubah. "
    "Kemungkinan deposito pernah diperpanjang."
)

assert deposito.proses_aro is None, (
    "Deposito sudah pernah diproses ARO"
)

assert deposito.status == StatusDeposito.AKTIF, (
    "Status deposito bukan aktif"
)

print("✅ Pengaman kondisi awal berhasil dilewati")


# ============================================================
# 3. MENYIAPKAN NILAI YANG DIHARAPKAN
# ============================================================

saldo_sebelum = rekening.saldo
nominal_sebelum = deposito.nominal
total_periode = deposito.total_pencairan

# Total periode berisi pokok beserta bunga.
bunga_dihasilkan = total_periode - nominal_sebelum

nominal_yang_diharapkan = total_periode
saldo_yang_diharapkan = saldo_sebelum

tanggal_buka_yang_diharapkan = JATUH_TEMPO_AWAL

jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
    tanggal_buka_yang_diharapkan,
    deposito.lama_aro
)

bunga_baru_yang_diharapkan = (
    DepositoService.JANGKA_WAKTU[deposito.lama_aro]
)

jumlah_sebelum = hitung_jumlah_data()


print("\n=== KONDISI SEBELUM ARO ===")
print("ID deposito       :", deposito.ID)
print("Nomor rekening    :", rekening.norek)
print(
    "Nominal lama      : Rp"
    + Utilitas.format_rupiah(nominal_sebelum)
)
print(
    "Bunga dihasilkan  : Rp"
    + Utilitas.format_rupiah(bunga_dihasilkan)
)
print(
    "Saldo rekening    : Rp"
    + Utilitas.format_rupiah(saldo_sebelum)
)
print("Tanggal buka      :", deposito.tanggal_buka)
print("Jatuh tempo       :", deposito.jatuh_tempo)
print("Jenis ARO         :", deposito.jenis_aro)
print("Lama ARO          :", deposito.lama_aro)
print("Proses ARO        :", deposito.proses_aro)


# ============================================================
# 4. MENJALANKAN PERPANJANGAN
# ============================================================

hasil = DepositoService.perpanjangan(
    deposito=deposito,
    hari_ini=JATUH_TEMPO_AWAL
)

assert hasil is True, (
    "Service perpanjangan tidak mengembalikan True"
)


# ============================================================
# 5. MEMUAT ULANG HASIL DARI SQLITE
# ============================================================
#
# Kita memuat objek baru agar yang diperiksa benar-benar hasil
# penyimpanan SQLite, bukan hanya perubahan objek di memori.
# ============================================================

deposito_sesudah = cari_deposito_aktif(ID_DEPOSITO)

if deposito_sesudah is None:
    raise AssertionError(
        f"Deposito ID {ID_DEPOSITO} tidak ditemukan setelah ARO"
    )

rekening_sesudah = deposito_sesudah.rekening
jumlah_sesudah = hitung_jumlah_data()


# ============================================================
# 6. MENGAMBIL TRANSAKSI, RIWAYAT, DAN AUDIT
# ============================================================

koneksi = buat_koneksi()

try:
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND jenis_referensi = ?
          AND id_referensi = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.KAPITALISASI_BUNGA_DEPOSITO.value,
            JenisReferensi.DEPOSITO.value,
            ID_DEPOSITO
        )
    ).fetchone()

    assert transaksi is not None, (
        "Transaksi kapitalisasi bunga tidak ditemukan"
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

finally:
    koneksi.close()


# ============================================================
# 7. MEMERIKSA HASIL DEPOSITO
# ============================================================

assert deposito_sesudah.nominal == nominal_yang_diharapkan, (
    f"Nominal seharusnya {nominal_yang_diharapkan}, "
    f"tetapi ditemukan {deposito_sesudah.nominal}"
)
print("✅ Pokok dan bunga menjadi nominal deposito baru")

assert deposito_sesudah.nominal == (
    nominal_sebelum + bunga_dihasilkan
), "Kenaikan nominal tidak sama dengan bunga"
print("✅ Nominal deposito bertambah sebesar bunga")

assert rekening_sesudah.saldo == saldo_yang_diharapkan, (
    "Saldo rekening berubah pada ARO pokok+bunga"
)
print("✅ Saldo rekening tidak berubah")

assert (
    deposito_sesudah.tanggal_buka
    == tanggal_buka_yang_diharapkan
), "Tanggal buka periode baru tidak sesuai"
print("✅ Tanggal buka baru sesuai jatuh tempo lama")

assert (
    deposito_sesudah.jatuh_tempo
    == jatuh_tempo_yang_diharapkan
), "Jatuh tempo periode baru tidak sesuai"
print("✅ Jatuh tempo baru berhasil dihitung")

assert deposito_sesudah.lama_bulan == deposito.lama_aro, (
    "Tenor periode baru tidak mengikuti lama ARO"
)
print("✅ Tenor periode baru mengikuti lama ARO")

assert (
    deposito_sesudah.bunga
    == bunga_baru_yang_diharapkan
), "Bunga periode baru tidak sesuai tenor ARO"
print("✅ Bunga periode baru sesuai tenor ARO")

assert deposito_sesudah.proses_aro == JATUH_TEMPO_AWAL, (
    "Tanggal proses ARO tidak sesuai"
)
print("✅ Tanggal proses ARO berhasil disimpan")

assert deposito_sesudah.status == StatusDeposito.AKTIF, (
    "Deposito tidak aktif setelah diperpanjang"
)
print("✅ Deposito tetap aktif setelah diperpanjang")


# ============================================================
# 8. MEMERIKSA TRANSAKSI KAPITALISASI
# ============================================================

assert jumlah_sesudah["transaksi"] == (
    jumlah_sebelum["transaksi"] + 1
), "Transaksi seharusnya bertambah tepat satu"
print("✅ Transaksi bertambah tepat satu")

assert transaksi["jenis"] == (
    JenisTransaksi.KAPITALISASI_BUNGA_DEPOSITO.value
), "Jenis transaksi tidak sesuai"
print("✅ Jenis transaksi kapitalisasi sesuai")

assert transaksi["nominal"] == bunga_dihasilkan, (
    "Nominal transaksi tidak sama dengan bunga kapitalisasi"
)
print("✅ Nominal transaksi berisi bunga kapitalisasi")

assert transaksi["biaya"] == 0, (
    "Kapitalisasi deposito seharusnya tidak memiliki biaya"
)
print("✅ Kapitalisasi tidak memiliki biaya")

assert transaksi["norek_sumber"] is None, (
    "Kapitalisasi tidak memiliki rekening sumber"
)

assert transaksi["norek_tujuan"] is None, (
    "Kapitalisasi tidak memiliki rekening tujuan"
)
print("✅ Tidak tercatat perpindahan antar-rekening")

assert transaksi["saldo_sumber_sebelum"] is None
assert transaksi["saldo_sumber_sesudah"] is None
assert transaksi["saldo_tujuan_sebelum"] is None
assert transaksi["saldo_tujuan_sesudah"] is None
