"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_uji_schdeuler.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime
from unittest.mock import patch

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.scheduler import Scheduler
from bank_djago.utils.utility import Utilitas


NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot_rekening(norek):
    """
    Mengambil kondisi rekening dan jumlah pencatatan sistem
    khusus milik rekening pengujian.
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
            WHERE (
                    jenis = 'bunga_tabungan'
                    AND norek_tujuan = ?
                  )
               OR (
                    jenis = 'biaya_admin'
                    AND norek_sumber = ?
                  )
            """,
            (norek, norek)
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
              AND jenis IN (
                    'bunga bulanan',
                    'biaya admin'
              )
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
              AND jenis IN (
                    'dapat bunga',
                    'biaya admin'
              )
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


def cari_periode(tanggal_awal, hari_simulasi):
    """
    Menghitung daftar periode bulanan yang telah tercapai.
    """
    daftar_periode = []

    tanggal_berikutnya = Utilitas.tambah_bulan(
        tanggal_awal,
        1
    )

    while tanggal_berikutnya <= hari_simulasi:
        daftar_periode.append(tanggal_berikutnya)

        tanggal_berikutnya = Utilitas.tambah_bulan(
            tanggal_berikutnya,
            1
        )

    return daftar_periode


# Memuat rekening pengujian menjadi satu objek Python.
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


snapshot_sebelum = ambil_snapshot_rekening(
    NOREK_PENGUJIAN
)

data_sebelum = snapshot_sebelum["rekening"]

saldo_sebelum = data_sebelum["saldo"]

tanggal_bunga_sebelum = datetime.date.fromisoformat(
    data_sebelum["dapat_bunga"]
)

tanggal_admin_sebelum = datetime.date.fromisoformat(
    data_sebelum["waktu_bayar_admin"]
)


# Memilih tanggal terdekat yang membuat bunga dan biaya admin
# rekening ini sama-sama memiliki periode untuk diproses.
hari_simulasi = max(
    Utilitas.tambah_bulan(tanggal_bunga_sebelum, 1),
    Utilitas.tambah_bulan(tanggal_admin_sebelum, 1)
)


# Menghitung hasil yang diharapkan.
# Urutannya mengikuti scheduler: bunga, lalu biaya admin.
periode_bunga = cari_periode(
    tanggal_bunga_sebelum,
    hari_simulasi
)

jumlah_periode_bunga = len(periode_bunga)

bunga_satu_bulan = round(
    saldo_sebelum * rekening.bunga / 12
)

total_bunga = (
    bunga_satu_bulan * jumlah_periode_bunga
)

saldo_setelah_bunga = (
    saldo_sebelum + total_bunga
)

tanggal_bunga_baru = (
    periode_bunga[-1]
    if periode_bunga
    else tanggal_bunga_sebelum
)


periode_admin = cari_periode(
    tanggal_admin_sebelum,
    hari_simulasi
)

jumlah_periode_admin = len(periode_admin)

jumlah_admin_mampu = (
    saldo_setelah_bunga // rekening.biaya_admin
)

jumlah_admin_dibayar = min(
    jumlah_periode_admin,
    jumlah_admin_mampu
)

total_admin = (
    rekening.biaya_admin * jumlah_admin_dibayar
)

saldo_akhir = (
    saldo_setelah_bunga - total_admin
)

tanggal_admin_baru = (
    periode_admin[jumlah_admin_dibayar - 1]
    if jumlah_admin_dibayar > 0
    else tanggal_admin_sebelum
)


# Bunga dan biaya admin masing-masing membuat satu rangkaian
# transaksi, riwayat, dan audit jika nominalnya lebih dari nol.
tambahan_pencatatan = 0

if total_bunga > 0:
    tambahan_pencatatan += 1

if total_admin > 0:
    tambahan_pencatatan += 1


print("=== KONDISI SEBELUM SCHEDULER ===")
print("Nomor rekening   :", rekening.norek)
print(
    "Saldo awal       :",
    f"Rp{Utilitas.format_rupiah(saldo_sebelum)}"
)
print("Periode bunga    :", tanggal_bunga_sebelum)
print("Periode admin    :", tanggal_admin_sebelum)
print("Hari simulasi    :", hari_simulasi)
print(
    "Bunga dihitung  :",
    f"Rp{Utilitas.format_rupiah(total_bunga)}"
)
print(
    "Admin dihitung  :",
    f"Rp{Utilitas.format_rupiah(total_admin)}"
)
print(
    "Saldo diharapkan:",
    f"Rp{Utilitas.format_rupiah(saldo_akhir)}"
)
print()


# Scheduler biasanya memuat objek rekeningnya sendiri.
# Dalam pengujian ini, loader scheduler sementara diarahkan
# untuk memberikan objek yang sudah kita pegang.
#
# Dengan demikian, kita dapat memeriksa apakah scheduler juga
# meninggalkan state objek dalam kondisi yang benar.
with patch(
    "bank_djago.services.scheduler."
    "RekeningLoader.muat_semua_rekening_berjalan",
    return_value=[rekening]
):
    Scheduler.jalankan(
        bank=None,
        hari_ini=hari_simulasi
    )


snapshot_setelah = ambil_snapshot_rekening(
    NOREK_PENGUJIAN
)

data_setelah = snapshot_setelah["rekening"]


print("=== KONDISI SETELAH SCHEDULER ===")
print(
    "Saldo SQLite    :",
    f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
)
print(
    "Saldo objek     :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Periode bunga   :",
    data_setelah["dapat_bunga"]
)
print(
    "Periode admin   :",
    data_setelah["waktu_bayar_admin"]
)
print(
    "Transaksi baru  :",
    (
        snapshot_setelah["jumlah_transaksi"]
        - snapshot_sebelum["jumlah_transaksi"]
    )
)
print()


# Memeriksa saldo SQLite.
assert data_setelah["saldo"] == saldo_akhir, (
    "Saldo SQLite setelah scheduler tidak sesuai"
)

# Pemeriksaan ini sekarang valid karena scheduler menerima
# objek Python yang sama melalui mock loader.
assert rekening.saldo == saldo_akhir, (
    "Saldo objek setelah scheduler tidak sesuai"
)

# Memeriksa periode bunga.
assert (
    data_setelah["dapat_bunga"]
    == tanggal_bunga_baru.isoformat()
), "Periode bunga SQLite tidak sesuai"

assert rekening.dapat_bunga == tanggal_bunga_baru, (
    "Periode bunga objek tidak sesuai"
)

# Memeriksa periode pembayaran admin.
assert (
    data_setelah["waktu_bayar_admin"]
    == tanggal_admin_baru.isoformat()
), "Periode admin SQLite tidak sesuai"

assert (
    rekening.waktu_bayar_admin
    == tanggal_admin_baru
), "Periode admin objek tidak sesuai"

# Memeriksa jumlah pencatatan yang dibuat.
assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
    + tambahan_pencatatan
), "Jumlah transaksi scheduler tidak sesuai"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
    + tambahan_pencatatan
), "Jumlah riwayat scheduler tidak sesuai"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
    + tambahan_pencatatan
), "Jumlah audit scheduler tidak sesuai"


print(
    "✅ PEMANGGILAN PERTAMA BERHASIL: "
    "bunga dan biaya admin diproses dengan urutan benar"
)


# Menjalankan scheduler kembali pada tanggal yang sama.
# Tidak boleh ada pemrosesan kedua.
with patch(
    "bank_djago.services.scheduler."
    "RekeningLoader.muat_semua_rekening_berjalan",
    return_value=[rekening]
):
    Scheduler.jalankan(
        bank=None,
        hari_ini=hari_simulasi
    )


snapshot_kedua = ambil_snapshot_rekening(
    NOREK_PENGUJIAN
)

assert snapshot_kedua == snapshot_setelah, (
    "Pemanggilan scheduler kedua masih mengubah SQLite"
)

assert rekening.saldo == saldo_akhir, (
    "Pemanggilan kedua mengubah saldo objek"
)

assert rekening.dapat_bunga == tanggal_bunga_baru, (
    "Pemanggilan kedua mengubah periode bunga objek"
)

assert (
    rekening.waktu_bayar_admin
    == tanggal_admin_baru
), "Pemanggilan kedua mengubah periode admin objek"


print(
    "✅ INTEGRASI SCHEDULER REKENING BERHASIL: "
    "bunga dan biaya admin diproses, state SQLite "
    "serta objek selaras, dan pemanggilan kedua "
    "tidak menggandakan data"
)
