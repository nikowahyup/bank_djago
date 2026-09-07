"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pemberian_bunga.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.bunga_service import (
    BungaService
)
from bank_djago.utils.utility import Utilitas


NOREK_PENGUJIAN = "3001781978899033"


def ambil_kondisi_database(norek):
    """
    Mengambil kondisi rekening beserta jumlah seluruh pencatatan
    bunga yang dimiliki rekening pengujian.
    """
    koneksi = buat_koneksi()

    try:
        rekening = RekeningRepository.cari_rekening_dengan_norek(
            norek=norek,
            koneksi=koneksi
        )

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'bunga_tabungan'
              AND norek_tujuan = ?
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
              AND jenis = 'bunga bulanan'
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
              AND jenis = 'dapat bunga'
            """,
            (norek,)
        ).fetchone()["jumlah"]

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# Memuat rekening sebagai objek Python.
koneksi = buat_koneksi()

try:
    rekening = RekeningLoader.muat_rekening(
        norek=NOREK_PENGUJIAN,
        koneksi=koneksi
    )
finally:
    koneksi.close()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )

if rekening.status == "tutup":
    raise AssertionError(
        "Rekening pengujian sudah ditutup"
    )


# Menyimpan keadaan sebelum service dijalankan.
kondisi_sebelum = ambil_kondisi_database(
    NOREK_PENGUJIAN
)

data_sebelum = kondisi_sebelum["rekening"]

saldo_sebelum = data_sebelum["saldo"]
periode_sebelum = datetime.date.fromisoformat(
    data_sebelum["dapat_bunga"]
)

# Tanggal simulasi dibuat tepat satu periode sesudah
# periode bunga terakhir.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    1
)

bunga_diharapkan = round(
    saldo_sebelum * rekening.bunga / 12
)

saldo_diharapkan = (
    saldo_sebelum + bunga_diharapkan
)

print("=== KONDISI SEBELUM PEMBERIAN BUNGA ===")
print("Nomor rekening :", rekening.norek)
print(
    "Saldo awal     :",
    f"Rp{Utilitas.format_rupiah(saldo_sebelum)}"
)
print(
    "Bunga tahunan  :",
    f"{rekening.bunga * 100:.1f}%"
)
print(
    "Bunga satu bulan:",
    f"Rp{Utilitas.format_rupiah(bunga_diharapkan)}"
)
print("Periode terakhir:", periode_sebelum)
print("Hari simulasi   :", hari_simulasi)
print()


# Menjalankan pemberian bunga satu periode.
total_bunga = BungaService.berikan_bunga(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_setelah = ambil_kondisi_database(
    NOREK_PENGUJIAN
)

data_setelah = kondisi_setelah["rekening"]

periode_setelah = datetime.date.fromisoformat(
    data_setelah["dapat_bunga"]
)

print("=== KONDISI SETELAH PEMBERIAN BUNGA ===")
print(
    "Bunga diberikan:",
    f"Rp{Utilitas.format_rupiah(total_bunga)}"
)
print(
    "Saldo SQLite   :",
    f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
)
print(
    "Saldo objek    :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print("Periode SQLite :", periode_setelah)
print("Periode objek  :", rekening.dapat_bunga)
print()


# Memastikan nominal bunga dihitung dengan bunga tahunan / 12.
assert total_bunga == bunga_diharapkan, (
    "Nominal bunga yang diberikan tidak sesuai"
)

# Memastikan saldo SQLite bertambah tepat sebesar bunga.
assert data_setelah["saldo"] == saldo_diharapkan, (
    "Saldo SQLite setelah pemberian bunga tidak sesuai"
)

# Memastikan state objek Python ikut diperbarui.
assert rekening.saldo == saldo_diharapkan, (
    "Saldo objek Python tidak sesuai dengan SQLite"
)

assert rekening.dapat_bunga == hari_simulasi, (
    "Periode bunga pada objek Python belum diperbarui"
)

assert periode_setelah == hari_simulasi, (
    "Periode bunga pada SQLite belum diperbarui"
)

# Setiap pemberian bunga harus menghasilkan tepat satu
# transaksi, satu riwayat, dan satu audit.
assert (
    kondisi_setelah["jumlah_transaksi"]
    == kondisi_sebelum["jumlah_transaksi"] + 1
), "Transaksi bunga tidak bertambah tepat satu"

assert (
    kondisi_setelah["jumlah_riwayat"]
    == kondisi_sebelum["jumlah_riwayat"] + 1
), "Riwayat bunga tidak bertambah tepat satu"

assert (
    kondisi_setelah["jumlah_audit"]
    == kondisi_sebelum["jumlah_audit"] + 1
), "Audit bunga tidak bertambah tepat satu"


# Mengambil transaksi terbaru untuk memeriksa hubungan
# transaksi, riwayat, dan audit.
koneksi = buat_koneksi()

try:
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = 'bunga_tabungan'
          AND norek_tujuan = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

    if transaksi is None:
        raise AssertionError(
            "Transaksi bunga tidak ditemukan"
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

finally:
    koneksi.close()


print("=== DATA TRANSAKSI BUNGA ===")
print("ID transaksi    :", transaksi["id"])
print("Jenis transaksi :", transaksi["jenis"])
print("Rekening tujuan :", transaksi["norek_tujuan"])
print(
    "Nominal         :",
    f"Rp{Utilitas.format_rupiah(transaksi['nominal'])}"
)
print(
    "Saldo awal      :",
    f"Rp{Utilitas.format_rupiah(
        transaksi['saldo_tujuan_sebelum']
    )}"
)
print(
    "Saldo akhir     :",
    f"Rp{Utilitas.format_rupiah(
        transaksi['saldo_tujuan_sesudah']
    )}"
)
print()

assert transaksi["nominal"] == bunga_diharapkan, (
    "Nominal transaksi tidak sesuai bunga"
)

assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum, (
    "Snapshot saldo awal transaksi tidak sesuai"
)

assert transaksi["saldo_tujuan_sesudah"] == saldo_diharapkan, (
    "Snapshot saldo akhir transaksi tidak sesuai"
)

assert len(riwayat) == 1, (
    "Riwayat bunga tidak terhubung dengan transaksi"
)

assert len(audit) == 1, (
    "Audit bunga tidak terhubung dengan transaksi"
)

print("=== RIWAYAT TERHUBUNG ===")
for data in riwayat:
    print(
        f"ID {data['id']} | "
        f"Transaksi {data['transaksi_id']} | "
        f"{data['jenis']} | "
        f"{data['log']}"
    )

print()
print("=== AUDIT TERHUBUNG ===")
for data in audit:
    print(
        f"ID {data['id']} | "
        f"Transaksi {data['transaksi_id']} | "
        f"{data['jenis']} | "
        f"{data['log']}"
    )


# Memanggil service untuk kedua kalinya pada tanggal yang sama.
# Tidak boleh ada bunga atau pencatatan tambahan.
hasil_kedua = BungaService.berikan_bunga(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_pemanggilan_kedua = ambil_kondisi_database(
    NOREK_PENGUJIAN
)

assert hasil_kedua == 0, (
    "Pemanggilan kedua masih memberikan bunga"
)

assert (
    kondisi_pemanggilan_kedua
    == kondisi_setelah
), (
    "Pemanggilan kedua mengubah data meskipun "
    "periodenya sudah diproses"
)

print()
print(
    "✅ PEMBERIAN BUNGA SATU PERIODE BERHASIL: "
    "saldo, periode, transaksi, riwayat, audit, "
    "state objek, dan pencegahan proses ganda "
    "tersimpan dengan benar"
)
