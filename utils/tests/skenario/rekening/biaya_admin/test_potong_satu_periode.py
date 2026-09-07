"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_load_untuk_biayaadmin.py` (urutan 2).

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
SALDO_AWAL = 512_000
BIAYA_ADMIN = 2_000


def muat_rekening():
    """
    Memuat objek rekening pengujian tanpa melibatkan scheduler.
    """
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
    Mengambil keadaan rekening dan jumlah transaksi biaya admin.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT
                norek,
                saldo,
                level,
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

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi
        }

    finally:
        koneksi.close()


# Memuat rekening pengujian sebagai objek Python.
rekening = muat_rekening()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )


# Memastikan rekening masih berada pada kondisi awal.
assert rekening.level == 1, (
    "Rekening pengujian bukan rekening Reguler"
)

assert rekening.saldo == SALDO_AWAL, (
    f"Saldo aktual Rp{Utilitas.format_rupiah(rekening.saldo)}, "
    f"bukan Rp{Utilitas.format_rupiah(SALDO_AWAL)}"
)

assert rekening.biaya_admin == BIAYA_ADMIN, (
    "Biaya admin rekening Reguler bukan Rp2.000"
)


kondisi_sebelum = ambil_kondisi_database()

periode_terakhir_dibayar = rekening.waktu_bayar_admin

# Mensimulasikan satu bulan setelah periode terakhir dibayar.
hari_simulasi = Utilitas.tambah_bulan(
    periode_terakhir_dibayar,
    1
)

saldo_yang_diharapkan = SALDO_AWAL - BIAYA_ADMIN


print("=== KONDISI SEBELUM PEMOTONGAN ===")
print("Nomor rekening       :", rekening.norek)
print("Level rekening       :", rekening.level)
print("Saldo                :", rekening.saldo)
print("Biaya admin          :", rekening.biaya_admin)
print("Periode terakhir     :", periode_terakhir_dibayar)
print("Hari simulasi        :", hari_simulasi)
print("Jumlah transaksi lama:",
      kondisi_sebelum["jumlah_transaksi"])
print()


# Memanggil service secara langsung tanpa scheduler.
total_dibayar = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)


kondisi_sesudah = ambil_kondisi_database()
data_rekening_sesudah = kondisi_sesudah["rekening"]


# Memastikan nilai yang dikembalikan service sesuai.
assert total_dibayar == BIAYA_ADMIN, (
    "Jumlah biaya admin yang dibayar tidak sesuai"
)


# Memastikan perubahan tersimpan di SQLite.
assert data_rekening_sesudah["saldo"] == saldo_yang_diharapkan, (
    "Saldo SQLite tidak berkurang sebesar biaya admin"
)

assert (
    data_rekening_sesudah["waktu_bayar_admin"]
    == hari_simulasi.isoformat()
), "Periode pembayaran admin di SQLite tidak sesuai"


# Memastikan tepat satu transaksi baru terbentuk.
assert (
    kondisi_sesudah["jumlah_transaksi"]
    == kondisi_sebelum["jumlah_transaksi"] + 1
), "Transaksi biaya admin tidak bertambah tepat satu"


# Memastikan objek Python diperbarui setelah commit.
assert rekening.saldo == saldo_yang_diharapkan, (
    "Saldo objek rekening tidak ikut diperbarui"
)

assert rekening.waktu_bayar_admin == hari_simulasi, (
    "Waktu bayar admin objek tidak ikut diperbarui"
)


print("=== KONDISI SETELAH PEMOTONGAN ===")
print("Total biaya admin :", total_dibayar)
print("Saldo SQLite      :", data_rekening_sesudah["saldo"])
print("Saldo objek       :", rekening.saldo)
print(
    "Periode terakhir  :",
    data_rekening_sesudah["waktu_bayar_admin"]
)
print(
    "Jumlah transaksi  :",
    kondisi_sesudah["jumlah_transaksi"]
)
print()


# Memanggil service lagi pada tanggal yang sama.
# Pemanggilan kedua tidak boleh memotong saldo kembali.
hasil_kedua = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_setelah_panggilan_kedua = (
    ambil_kondisi_database()
)

assert hasil_kedua == 0, (
    "Pemanggilan kedua seharusnya tidak membayar periode baru"
)

assert (
    kondisi_setelah_panggilan_kedua["rekening"]["saldo"]
    == saldo_yang_diharapkan
), "Saldo kembali terpotong pada tanggal yang sama"

assert (
    kondisi_setelah_panggilan_kedua["jumlah_transaksi"]
    == kondisi_sesudah["jumlah_transaksi"]
), "Transaksi ganda terbentuk pada tanggal yang sama"


print(
    "✅ PEMOTONGAN BIAYA ADMIN BERHASIL: "
    "saldo berkurang Rp2.000, periode diperbarui, "
    "dan pemanggilan kedua tidak memotong saldo lagi"
)



# from bank_djago.penyimpanan.sqlite.database import (
#     buat_koneksi,
#     lokasi_database
# )
#
#
# NOREK = "4001701216150609"
#
# koneksi = buat_koneksi()
#
# try:
#     rekening = koneksi.execute(
#         """
#         SELECT
#             norek,
#             saldo,
#             status,
#             waktu_bayar_admin
#         FROM rekening
#         WHERE norek = ?
#         """,
#         (NOREK,)
#     ).fetchone()
#
#     transaksi_setor = koneksi.execute(
#         """
#         SELECT
#             id,
#             jenis,
#             norek_tujuan,
#             nominal,
#             saldo_tujuan_sebelum,
#             saldo_tujuan_sesudah,
#             waktu
#         FROM transaksi
#         WHERE norek_tujuan = ?
#           AND jenis = 'setor_tunai'
#         ORDER BY id DESC
#         LIMIT 5
#         """,
#         (NOREK,)
#     ).fetchall()
#
# finally:
#     koneksi.close()
#
#
# print("=== LOKASI DATABASE ===")
# print(lokasi_database.resolve())
# print()
#
# print("=== DATA REKENING ===")
# print(dict(rekening) if rekening else None)
# print()
#
# print("=== TRANSAKSI SETOR TUNAI TERAKHIR ===")
#
# if not transaksi_setor:
#     print("Tidak ditemukan transaksi setor tunai")
# else:
#     for transaksi in transaksi_setor:
#         print(dict(transaksi))
