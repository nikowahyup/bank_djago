"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 7).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

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
from bank_djago.utils.utility import Utilitas,JenisReferensiID,JenisTransaksi


ID_DEPOSITO = 13
NOREK_PENGUJIAN = "3001781978899033"

JENIS_TRANSAKSI = "kapitalisasi_bunga_deposito"
JENIS_REFERENSI_DEPOSITO = 2


# ============================================================
# MENGHITUNG JUMLAH DATA SEBELUM DAN SETELAH PROSES
# ============================================================

def hitung_jumlah_data():
    """
    Menghitung seluruh transaksi, riwayat, dan audit.

    Nilai ini akan dibandingkan sebelum dan setelah ARO
    untuk memastikan jumlah data bertambah dengan benar.
    """
    koneksi = buat_koneksi()

    try:
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
            "transaksi": jumlah_transaksi,
            "riwayat": jumlah_riwayat,
            "audit": jumlah_audit
        }

    finally:
        koneksi.close()


# ============================================================
# MEMUAT DEPOSITO AKTIF DARI SQLITE
# ============================================================

# DepositoLoader mengembalikan objek deposito yang sudah
# terhubung dengan objek rekening dan nasabahnya.
daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()

deposito = next(
    (
        item
        for item in daftar_deposito
        if item.ID == ID_DEPOSITO
    ),
    None
)

if deposito is None:
    raise AssertionError(
        f"Deposito aktif dengan ID {ID_DEPOSITO} tidak ditemukan"
    )


# ============================================================
# MEMERIKSA IDENTITAS DAN KONDISI AWAL DEPOSITO
# ============================================================

assert deposito.rekening.norek == NOREK_PENGUJIAN, (
    "Deposito terhubung dengan rekening yang salah"
)

assert deposito.jenis_aro == JenisAro.POKOK_BUNGA, (
    f"Jenis ARO seharusnya {JenisAro.POKOK_BUNGA}, "
    f"tetapi ditemukan {deposito.jenis_aro}"
)

assert deposito.status == StatusDeposito.AKTIF, (
    f"Status deposito seharusnya aktif, "
    f"tetapi ditemukan {deposito.status}"
)

assert deposito.lama_aro in DepositoService.JANGKA_WAKTU, (
    "Lama perpanjangan deposito tidak valid"
)


# ============================================================
# MENYIMPAN KONDISI SEBELUM ARO
# ============================================================

rekening = deposito.rekening

saldo_sebelum = rekening.saldo
nominal_sebelum = deposito.nominal
bunga_sebelum = deposito.bunga
tenor_sebelum = deposito.lama_bulan
lama_aro = deposito.lama_aro
tanggal_buka_sebelum = deposito.tanggal_buka
jatuh_tempo_sebelum = deposito.jatuh_tempo

# total_pencairan berisi pokok ditambah bunga periode lama.
total_pencairan = deposito.total_pencairan

# Pada ARO pokok+bunga, nilai ini tidak masuk ke rekening.
# Nilainya ditambahkan ke nominal deposito.
bunga_dihasilkan = total_pencairan - nominal_sebelum

nominal_yang_diharapkan = (
    nominal_sebelum + bunga_dihasilkan
)

saldo_yang_diharapkan = saldo_sebelum

tanggal_buka_yang_diharapkan = jatuh_tempo_sebelum

jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
    tanggal_buka_yang_diharapkan,
    lama_aro
)

bunga_baru_yang_diharapkan = (
    DepositoService.JANGKA_WAKTU[lama_aro]
)

jumlah_sebelum = hitung_jumlah_data()


print("=== KONDISI SEBELUM ARO POKOK + BUNGA ===")
print()
print("ID deposito       :", deposito.ID)
print("Nomor rekening    :", rekening.norek)
print("Jenis ARO         :", deposito.jenis_aro)
print(
    "Nominal lama      : Rp"
    + Utilitas.format_rupiah(nominal_sebelum)
)
print(
    "Bunga dihasilkan  : Rp"
    + Utilitas.format_rupiah(bunga_dihasilkan)
)
print(
    "Total periode     : Rp"
    + Utilitas.format_rupiah(total_pencairan)
)
print(
    "Saldo rekening    : Rp"
    + Utilitas.format_rupiah(saldo_sebelum)
)
print(f"Bunga lama        : {bunga_sebelum:.1%}")
print("Tenor lama        :", tenor_sebelum, "bulan")
print("Tenor ARO         :", lama_aro, "bulan")
print("Tanggal buka      :", tanggal_buka_sebelum)
print("Jatuh tempo       :", jatuh_tempo_sebelum)
print("Proses ARO        :", deposito.proses_aro)
print("Jumlah transaksi  :", jumlah_sebelum["transaksi"])
print("Jumlah riwayat    :", jumlah_sebelum["riwayat"])
print("Jumlah audit      :", jumlah_sebelum["audit"])
print()


# ============================================================
# MENJALANKAN ARO DENGAN TANGGAL SIMULASI
# ============================================================

# Tanggal jatuh tempo dipakai sebagai hari simulasi.
# Kita tidak perlu mengubah waktu komputer ataupun main.
hasil = DepositoService.perpanjangan(
    deposito=deposito,
    hari_ini=jatuh_tempo_sebelum
)

assert hasil is True, (
    "Method perpanjangan tidak mengembalikan True"
)


# ============================================================
# MEMUAT ULANG HASIL DARI SQLITE
# ============================================================

# Kita tidak hanya mempercayai perubahan pada objek lama.
# Data dimuat ulang agar terbukti sudah tersimpan di SQLite.
daftar_deposito_sesudah = (
    DepositoLoader.muat_semua_deposito_aktif()
)

deposito_sesudah = next(
    (
        item
        for item in daftar_deposito_sesudah
        if item.ID == ID_DEPOSITO
    ),
    None
)

if deposito_sesudah is None:
    raise AssertionError(
        f"Deposito ID {ID_DEPOSITO} tidak ditemukan setelah ARO"
    )

rekening_sesudah = deposito_sesudah.rekening
jumlah_sesudah = hitung_jumlah_data()


# ============================================================
# MENGAMBIL TRANSAKSI KAPITALISASI
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
            JENIS_TRANSAKSI,
            JENIS_REFERENSI_DEPOSITO,
            ID_DEPOSITO
        )
    ).fetchone()

    assert transaksi is not None, (
        "Transaksi kapitalisasi bunga tidak ditemukan"
    )

    id_transaksi = transaksi["id"]

    # Seluruh riwayat proses ARO harus menunjuk
    # ke transaksi kapitalisasi yang sama.
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    # Audit perpanjangan juga harus menunjuk
    # ke transaksi kapitalisasi tersebut.
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
# MENAMPILKAN KONDISI SETELAH ARO
# ============================================================

print("=== KONDISI SETELAH ARO POKOK + BUNGA ===")
print()
print("ID deposito       :", deposito_sesudah.ID)
print("Jenis ARO         :", deposito_sesudah.jenis_aro)
print(
    "Nominal baru      : Rp"
    + Utilitas.format_rupiah(deposito_sesudah.nominal)
)
print(
    "Saldo rekening    : Rp"
    + Utilitas.format_rupiah(rekening_sesudah.saldo)
)
print(f"Bunga baru        : {deposito_sesudah.bunga:.1%}")
print(
    "Tenor baru        :",
    deposito_sesudah.lama_bulan,
    "bulan"
)
print("Tanggal buka baru :", deposito_sesudah.tanggal_buka)
print("Jatuh tempo baru  :", deposito_sesudah.jatuh_tempo)
print("Status deposito   :", deposito_sesudah.status)
print("Proses ARO        :", deposito_sesudah.proses_aro)
print()


print("=== DATA TRANSAKSI ===")
print()
print("ID transaksi      :", transaksi["id"])
print("Jenis             :", transaksi["jenis"])
print("Rekening sumber   :", transaksi["norek_sumber"])
print("Rekening tujuan   :", transaksi["norek_tujuan"])
print(
    "Nominal bunga     : Rp"
    + Utilitas.format_rupiah(transaksi["nominal"])
)
print("Saldo sumber awal :", transaksi["saldo_sumber_sebelum"])
print("Saldo sumber akhir:", transaksi["saldo_sumber_sesudah"])
print("Saldo tujuan awal :", transaksi["saldo_tujuan_sebelum"])
print("Saldo tujuan akhir:", transaksi["saldo_tujuan_sesudah"])
print("Jenis referensi   :", transaksi["jenis_referensi"])
print("ID referensi      :", transaksi["id_referensi"])
print("Waktu             :", transaksi["waktu"])
print()


print("=== RIWAYAT TERHUBUNG ===")

for riwayat in daftar_riwayat:
    print(
        f"ID {riwayat['id']} | "
        f"Transaksi {riwayat['transaksi_id']} | "
        f"{riwayat['jenis']} | "
        f"{riwayat['log']}"
    )

print()

print("=== AUDIT TERHUBUNG ===")

for audit in daftar_audit:
    print(
        f"ID {audit['id']} | "
        f"Transaksi {audit['transaksi_id']} | "
        f"{audit['jenis']} | "
        f"{audit['log']}"
    )

print()


# ============================================================
# MEMERIKSA HASIL PERPANJANGAN DEPOSITO
# ============================================================

assert deposito_sesudah.nominal == nominal_yang_diharapkan, (
    "Pokok dan bunga tidak menjadi nominal deposito baru"
)
print("✅ Pokok dan bunga menjadi nominal deposito baru")

assert deposito_sesudah.nominal > nominal_sebelum, (
    "Nominal deposito tidak bertambah"
)
print("✅ Nominal deposito bertambah sebesar bunga")

assert rekening_sesudah.saldo == saldo_yang_diharapkan, (
    "Saldo rekening berubah pada ARO pokok+bunga"
)
print("✅ Saldo rekening tidak berubah")

assert deposito_sesudah.bunga == bunga_baru_yang_diharapkan, (
    "Bunga periode baru tidak mengikuti tenor ARO"
)
print("✅ Bunga periode baru mengikuti tenor ARO")

assert deposito_sesudah.lama_bulan == lama_aro, (
    "Tenor baru tidak mengikuti lama ARO"
)
print("✅ Tenor baru mengikuti lama ARO")

assert (
    deposito_sesudah.tanggal_buka
    == tanggal_buka_yang_diharapkan
), "Tanggal buka periode baru tidak sesuai"
print("✅ Tanggal buka baru sesuai jatuh tempo sebelumnya")

assert (
    deposito_sesudah.jatuh_tempo
    == jatuh_tempo_yang_diharapkan
), "Jatuh tempo periode baru tidak sesuai"
print("✅ Jatuh tempo periode baru berhasil dihitung")

assert deposito_sesudah.proses_aro == jatuh_tempo_sebelum, (
    "Tanggal proses ARO tidak sesuai tanggal simulasi"
)
print("✅ Tanggal proses ARO berhasil disimpan")

assert deposito_sesudah.status == StatusDeposito.AKTIF, (
    "Deposito tidak aktif setelah perpanjangan"
)
print("✅ Deposito tetap aktif setelah diperpanjang")


# ============================================================
# MEMERIKSA TRANSAKSI KAPITALISASI
# ============================================================

assert jumlah_sesudah["transaksi"] == (
    jumlah_sebelum["transaksi"] + 1
), "Transaksi seharusnya bertambah tepat satu"
print("✅ Transaksi bertambah tepat satu")

assert transaksi["jenis"] == JENIS_TRANSAKSI, (
    "Jenis transaksi kapitalisasi tidak sesuai"
)
print("✅ Jenis transaksi kapitalisasi sesuai")

assert transaksi["nominal"] == bunga_dihasilkan, (
    "Nominal transaksi tidak sama dengan bunga yang dihasilkan"
)
print("✅ Nominal transaksi berisi bunga yang dikapitalisasi")

assert transaksi["norek_sumber"] is None, (
    "Kapitalisasi seharusnya tidak memiliki rekening sumber"
)

assert transaksi["norek_tujuan"] is None, (
    "Kapitalisasi seharusnya tidak memiliki rekening tujuan"
)
print("✅ Kapitalisasi tidak mencatat perpindahan antar-rekening")

assert transaksi["saldo_sumber_sebelum"] is None
assert transaksi["saldo_sumber_sesudah"] is None
assert transaksi["saldo_tujuan_sebelum"] is None
assert transaksi["saldo_tujuan_sesudah"] is None
print("✅ Snapshot saldo rekening kosong karena saldo tidak berubah")

assert (
    transaksi["jenis_referensi"]
    == JenisReferensiID.DEPOSITO
), "Jenis referensi transaksi bukan deposito"

assert transaksi["id_referensi"] == ID_DEPOSITO, (
    "ID referensi tidak menunjuk deposito ID 13"
)
print("✅ Transaksi terhubung ke deposito melalui referensi")

assert transaksi["waktu"] is not None, (
    "Waktu transaksi tidak tersimpan"
)
print("✅ Waktu transaksi berhasil tersimpan")


# ============================================================
# MEMERIKSA RIWAYAT DAN AUDIT
# ============================================================

assert jumlah_sesudah["riwayat"] == (
    jumlah_sebelum["riwayat"] + 2
), "Riwayat seharusnya bertambah tepat dua"

assert len(daftar_riwayat) == 2, (
    "Harus ada dua riwayat yang terhubung ke transaksi"
)
print("✅ Dua riwayat terhubung ke transaksi yang sama")

assert jumlah_sesudah["audit"] == (
    jumlah_sebelum["audit"] + 1
), "Audit seharusnya bertambah tepat satu"

assert len(daftar_audit) == 1, (
    "Harus ada satu audit yang terhubung ke transaksi"
)
print("✅ Audit perpanjangan terhubung ke transaksi yang sama")


print()
print(
    "✅ ARO POKOK + BUNGA BERHASIL: bunga dikapitalisasi, "
    "saldo rekening tetap, periode diperpanjang, dan seluruh "
    "catatan terhubung ke transaksi yang sama"
)
