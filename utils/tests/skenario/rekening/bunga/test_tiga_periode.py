"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pemberian_bunga.py` (urutan 2).

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
JUMLAH_PERIODE = 3


def ambil_snapshot(norek):
    """
    Mengambil kondisi rekening dan jumlah pencatatan bunga
    langsung dari SQLite.
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


# Menyimpan keadaan awal sebelum bunga diberikan.
sebelum = ambil_snapshot(NOREK_PENGUJIAN)
data_sebelum = sebelum["rekening"]

saldo_sebelum = data_sebelum["saldo"]

periode_sebelum = datetime.date.fromisoformat(
    data_sebelum["dapat_bunga"]
)

# Mensimulasikan tiga periode setelah periode terakhir.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    JUMLAH_PERIODE
)

bunga_satu_periode = round(
    saldo_sebelum * rekening.bunga / 12
)

total_bunga_diharapkan = (
    bunga_satu_periode * JUMLAH_PERIODE
)

saldo_diharapkan = (
    saldo_sebelum + total_bunga_diharapkan
)


print("=== KONDISI SEBELUM PEMBERIAN BUNGA ===")
print("Nomor rekening   :", rekening.norek)
print(
    "Saldo awal       :",
    f"Rp{Utilitas.format_rupiah(saldo_sebelum)}"
)
print(
    "Bunga per periode:",
    f"Rp{Utilitas.format_rupiah(bunga_satu_periode)}"
)
print("Periode terakhir :", periode_sebelum)
print("Hari simulasi     :", hari_simulasi)
print("Jumlah periode    :", JUMLAH_PERIODE)
print()


# Memberikan bunga untuk seluruh periode yang tertunggak.
total_bunga = BungaService.berikan_bunga(
    rekening=rekening,
    hari_ini=hari_simulasi
)

setelah = ambil_snapshot(NOREK_PENGUJIAN)
data_setelah = setelah["rekening"]

periode_setelah = datetime.date.fromisoformat(
    data_setelah["dapat_bunga"]
)


print("=== KONDISI SETELAH PEMBERIAN BUNGA ===")
print("Periode diproses :", JUMLAH_PERIODE)
print(
    "Total bunga     :",
    f"Rp{Utilitas.format_rupiah(total_bunga)}"
)
print(
    "Saldo SQLite    :",
    f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
)
print(
    "Saldo objek     :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print("Periode SQLite  :", periode_setelah)
print("Periode objek   :", rekening.dapat_bunga)
print()


# Memeriksa perhitungan bunga.
assert total_bunga == total_bunga_diharapkan, (
    "Total bunga beberapa periode tidak sesuai"
)

assert data_setelah["saldo"] == saldo_diharapkan, (
    "Saldo SQLite setelah pemberian bunga tidak sesuai"
)

assert rekening.saldo == saldo_diharapkan, (
    "Saldo objek Python tidak sesuai dengan SQLite"
)

assert periode_setelah == hari_simulasi, (
    "Periode bunga SQLite tidak diperbarui dengan benar"
)

assert rekening.dapat_bunga == hari_simulasi, (
    "Periode bunga objek Python tidak diperbarui"
)


# Walaupun ada tiga periode, pencatatan dibuat sebagai
# satu transaksi gabungan.
assert (
    setelah["jumlah_transaksi"]
    == sebelum["jumlah_transaksi"] + 1
), "Transaksi bunga tidak bertambah tepat satu"

assert (
    setelah["jumlah_riwayat"]
    == sebelum["jumlah_riwayat"] + 1
), "Riwayat bunga tidak bertambah tepat satu"

assert (
    setelah["jumlah_audit"]
    == sebelum["jumlah_audit"] + 1
), "Audit bunga tidak bertambah tepat satu"


# Mengambil transaksi bunga yang baru dibuat.
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


assert transaksi["nominal"] == total_bunga_diharapkan, (
    "Nominal pada transaksi bunga tidak sesuai"
)

assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum, (
    "Snapshot saldo awal transaksi tidak sesuai"
)

assert transaksi["saldo_tujuan_sesudah"] == saldo_diharapkan, (
    "Snapshot saldo akhir transaksi tidak sesuai"
)

assert len(riwayat) == 1, (
    "Riwayat tidak terhubung dengan transaksi bunga"
)

assert len(audit) == 1, (
    "Audit tidak terhubung dengan transaksi bunga"
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


# Memanggil service kembali pada tanggal simulasi yang sama.
# Tidak boleh menghasilkan bunga maupun pencatatan baru.
hasil_kedua = BungaService.berikan_bunga(
    rekening=rekening,
    hari_ini=hari_simulasi
)

setelah_pemanggilan_kedua = ambil_snapshot(
    NOREK_PENGUJIAN
)

assert hasil_kedua == 0, (
    "Pemanggilan kedua masih memberikan bunga"
)

assert setelah_pemanggilan_kedua == setelah, (
    "Pemanggilan kedua mengubah data"
)


print()
print(
    "✅ PEMBERIAN BUNGA TIGA PERIODE BERHASIL: "
    "bunga dihitung, saldo dan periode diperbarui, "
    "pencatatan dibuat dalam satu transaksi, "
    "serta pemanggilan kedua tidak mengubah data"
)
