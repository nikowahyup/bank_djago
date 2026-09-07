"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pemberian_bunga.py` (urutan 4).

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
from bank_djago.services.rekening.bunga_service import (
    BungaService
)
from bank_djago.utils.utility import Utilitas


NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot(norek):
    """
    Mengambil seluruh kondisi penting dari SQLite.

    Snapshot sebelum dan sesudah kegagalan akan dibandingkan
    untuk membuktikan bahwa rollback bekerja.
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


# Memuat rekening menjadi objek Python.
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

if rekening.saldo <= 0:
    raise AssertionError(
        "Pengujian rollback membutuhkan rekening "
        "yang menghasilkan bunga lebih dari nol"
    )


# Menyimpan kondisi database sebelum kegagalan buatan.
snapshot_sebelum = ambil_snapshot(
    NOREK_PENGUJIAN
)

data_sebelum = snapshot_sebelum["rekening"]

periode_sebelum = datetime.date.fromisoformat(
    data_sebelum["dapat_bunga"]
)

# Satu periode baru dibuat agar service benar-benar mencoba
# memperbarui rekening dan membuat transaksi.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    1
)

bunga_yang_seharusnya = round(
    data_sebelum["saldo"] * rekening.bunga / 12
)

# Menyimpan state objek Python sebelum service dijalankan.
saldo_objek_sebelum = rekening.saldo
periode_objek_sebelum = rekening.dapat_bunga
riwayat_objek_sebelum = list(rekening.riwayat)


print("=== KONDISI SEBELUM PENGUJIAN ROLLBACK ===")
print("Nomor rekening   :", rekening.norek)
print(
    "Saldo            :",
    f"Rp{Utilitas.format_rupiah(data_sebelum['saldo'])}"
)
print(
    "Bunga percobaan  :",
    f"Rp{Utilitas.format_rupiah(bunga_yang_seharusnya)}"
)
print("Periode terakhir :", periode_sebelum)
print("Hari simulasi     :", hari_simulasi)
print(
    "Jumlah transaksi :",
    snapshot_sebelum["jumlah_transaksi"]
)
print(
    "Jumlah riwayat   :",
    snapshot_sebelum["jumlah_riwayat"]
)
print(
    "Jumlah audit     :",
    snapshot_sebelum["jumlah_audit"]
)
print()


# AuditRepository sengaja dibuat gagal.
#
# Kegagalan terjadi setelah:
# 1. rekening diperbarui,
# 2. transaksi ditambahkan,
# 3. riwayat ditambahkan.
#
# Dengan demikian, kita dapat membuktikan bahwa ketiga
# perubahan tersebut benar-benar dibatalkan oleh rollback.
try:
    with patch(
        "bank_djago.services.rekening.bunga_service."
        "AuditRepository.tambah_audit",
        side_effect=RuntimeError(
            "Kegagalan audit untuk menguji rollback bunga"
        )
    ):
        BungaService.berikan_bunga(
            rekening=rekening,
            hari_ini=hari_simulasi
        )

except RuntimeError as error:
    print("✅ Kegagalan buatan berhasil dipicu")
    print("Pesan error:", error)

else:
    raise AssertionError(
        "Kegagalan audit tidak berhasil dipicu"
    )


# Mengambil ulang data dari SQLite setelah rollback.
snapshot_setelah = ambil_snapshot(
    NOREK_PENGUJIAN
)

data_setelah = snapshot_setelah["rekening"]

print()
print("=== KONDISI SETELAH ROLLBACK ===")
print(
    "Saldo SQLite     :",
    f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
)
print(
    "Saldo objek      :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Periode SQLite   :",
    data_setelah["dapat_bunga"]
)
print(
    "Periode objek    :",
    rekening.dapat_bunga
)
print(
    "Jumlah transaksi :",
    snapshot_setelah["jumlah_transaksi"]
)
print(
    "Jumlah riwayat   :",
    snapshot_setelah["jumlah_riwayat"]
)
print(
    "Jumlah audit     :",
    snapshot_setelah["jumlah_audit"]
)
print()


# Seluruh kondisi SQLite harus identik dengan kondisi awal.
assert snapshot_setelah == snapshot_sebelum, (
    "Data SQLite berubah meskipun transaksi telah di-rollback"
)

# State objek Python juga tidak boleh berubah karena perubahan
# objek dilakukan service hanya setelah commit berhasil.
assert rekening.saldo == saldo_objek_sebelum, (
    "Saldo objek Python berubah meskipun proses gagal"
)

assert rekening.dapat_bunga == periode_objek_sebelum, (
    "Periode bunga objek berubah meskipun proses gagal"
)

assert rekening.riwayat == riwayat_objek_sebelum, (
    "Riwayat objek bertambah meskipun proses gagal"
)


# Pemeriksaan lebih terperinci agar sumber masalah mudah
# ditemukan apabila salah satu assertion gagal.
assert (
    data_setelah["saldo"]
    == data_sebelum["saldo"]
), "Saldo SQLite tidak berhasil dipulihkan"

assert (
    data_setelah["dapat_bunga"]
    == data_sebelum["dapat_bunga"]
), "Periode bunga SQLite tidak berhasil dipulihkan"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi bunga masih tersisa setelah rollback"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat bunga masih tersisa setelah rollback"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Audit bunga bertambah meskipun proses gagal"


print(
    "✅ ROLLBACK BUNGA BERHASIL: "
    "saldo, periode bunga, transaksi, riwayat, audit, "
    "dan state objek Python tidak berubah"
)
