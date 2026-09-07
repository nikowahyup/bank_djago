"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.repositories.deposito_repository import (
    DepositoRepository
)
from bank_djago.penyimpanan.repositories.riwayat_repository import (
    RiwayatRepository
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.utils.utility import Utilitas


NIK_PENGUJIAN = "1111222233334444"
NOREK_PENGUJIAN = "2001569043650499"

NOMINAL_DEPOSITO = 1_000_000
SALDO_SEBELUM = 109_000_000
SALDO_SESUDAH = SALDO_SEBELUM - NOMINAL_DEPOSITO


# =========================================================
# MENGAMBIL DATA DARI SQLITE
# =========================================================

nasabah = NasabahRepository.cari_nasabah_dengan_nik(
    NIK_PENGUJIAN
)

rekening = RekeningRepository.cari_rekening_dengan_norek(
    NOREK_PENGUJIAN
)

daftar_deposito = DepositoRepository.cari_deposito_dengan_norek(
    NOREK_PENGUJIAN
)

daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(
    NOREK_PENGUJIAN
)

daftar_audit = AuditRepository.cari_audit_dengan_norek(
    NOREK_PENGUJIAN
)


# =========================================================
# MEMASTIKAN DATA UTAMA DITEMUKAN
# =========================================================

assert nasabah is not None, "Nasabah tidak ditemukan"
assert rekening is not None, "Rekening tidak ditemukan"
assert daftar_deposito, "Deposito tidak ditemukan"


# Repository mengurutkan deposito berdasarkan ID dari kecil
# ke besar, sehingga elemen terakhir adalah deposito terbaru.
deposito_terbaru = daftar_deposito[-1]

riwayat_deposito = [
    riwayat
    for riwayat in daftar_riwayat
    if riwayat["jenis"] == "deposito"
]

audit_deposito = [
    audit
    for audit in daftar_audit
    if audit["jenis"] == "deposito"
]

assert riwayat_deposito, "Riwayat pembukaan deposito tidak ditemukan"
assert audit_deposito, "Audit pembukaan deposito tidak ditemukan"

# Riwayat dan audit diurutkan berdasarkan ID terbaru.
riwayat_terbaru = riwayat_deposito[0]
audit_terbaru = audit_deposito[0]


# =========================================================
# MENAMPILKAN HASIL
# =========================================================

print("DATA NASABAH")
print(f"NIK     : {nasabah['nik']}")
print(f"Nama    : {nasabah['nama']}")
print(f"Alamat  : {nasabah['alamat']}")
print()

print("KONDISI REKENING")
print(f"Norek   : {rekening['norek']}")
print(f"Status  : {rekening['status']}")
print(
    f"Saldo   : Rp"
    f"{Utilitas.format_rupiah(rekening['saldo'])}"
)
print()

print("DEPOSITO TERBARU")
print(f"ID             : {deposito_terbaru['id']}")
print(f"Norek          : {deposito_terbaru['norek']}")
print(
    f"Nominal        : Rp"
    f"{Utilitas.format_rupiah(deposito_terbaru['nominal'])}"
)
print(f"Bunga          : {deposito_terbaru['bunga']:.1%}")
print(f"Tenor          : {deposito_terbaru['lama_bulan']} bulan")
print(f"Tanggal buka   : {deposito_terbaru['tanggal_buka']}")
print(f"Jatuh tempo    : {deposito_terbaru['jatuh_tempo']}")
print(f"Status         : {deposito_terbaru['status']}")
print(f"Jenis ARO      : {deposito_terbaru['jenis_aro']}")
print(f"Lama ARO       : {deposito_terbaru['lama_aro']}")
print(f"Proses ARO     : {deposito_terbaru['proses_aro']}")
print()

print("RIWAYAT TERBARU")
print(f"ID        : {riwayat_terbaru['id']}")
print(f"Kategori  : {riwayat_terbaru['kategori']}")
print(f"Jenis     : {riwayat_terbaru['jenis']}")
print(f"Waktu     : {riwayat_terbaru['waktu']}")
print(f"Log       : {riwayat_terbaru['log']}")
print()

print("AUDIT TERBARU")
print(f"ID        : {audit_terbaru['id']}")
print(f"Kategori  : {audit_terbaru['kategori']}")
print(f"Jenis     : {audit_terbaru['jenis']}")
print(f"Waktu     : {audit_terbaru['waktu']}")
print(f"Log       : {audit_terbaru['log']}")
print(f"Nama      : {audit_terbaru['nama']}")
print(f"NIK       : {audit_terbaru['nik']}")
print(f"Norek     : {audit_terbaru['norek']}")
print()


# =========================================================
# PEMERIKSAAN INTEGRITAS
# =========================================================

assert rekening["saldo"] == SALDO_SESUDAH, (
    "Saldo rekening tidak berkurang sesuai nominal deposito"
)

assert deposito_terbaru["norek"] == NOREK_PENGUJIAN, (
    "Foreign key deposito tidak mengarah ke rekening pengujian"
)

assert deposito_terbaru["nominal"] == NOMINAL_DEPOSITO, (
    "Nominal deposito tidak sesuai"
)

assert deposito_terbaru["bunga"] == 0.03, (
    "Bunga deposito tenor satu bulan tidak sesuai"
)

assert deposito_terbaru["lama_bulan"] == 1, (
    "Tenor deposito tidak sesuai"
)

assert deposito_terbaru["status"] == "aktif", (
    "Status awal deposito bukan aktif"
)

assert deposito_terbaru["jenis_aro"] == "tidak", (
    "Jenis ARO deposito tidak sesuai"
)

assert deposito_terbaru["lama_aro"] is None, (
    "Deposito tanpa ARO seharusnya tidak memiliki lama ARO"
)

assert deposito_terbaru["proses_aro"] is None, (
    "Deposito baru seharusnya belum memiliki tanggal proses ARO"
)

assert riwayat_terbaru["norek"] == NOREK_PENGUJIAN, (
    "Riwayat tersimpan pada rekening yang salah"
)

assert audit_terbaru["nik"] == NIK_PENGUJIAN, (
    "Audit tersimpan dengan NIK yang salah"
)

assert audit_terbaru["norek"] == NOREK_PENGUJIAN, (
    "Audit tersimpan dengan nomor rekening yang salah"
)


print("✅ Saldo rekening berhasil dikurangi")
print("✅ Deposito berhasil disimpan dengan ID global")
print("✅ Foreign key deposito mengarah ke rekening yang benar")
print("✅ Tenor, bunga, status, dan ARO tersimpan sesuai pilihan")
print("✅ Riwayat pembukaan deposito berhasil disimpan")
print("✅ Audit pembukaan deposito berhasil disimpan")
print("✅ Pembukaan deposito SQLite bekerja sesuai rancangan")











import datetime

from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.utils.utility import Utilitas


NIK_PENGUJIAN = "1111222233334444"
NOREK_DEPOSITO = "2001569043650499"
ID_DEPOSITO = 5


# =========================================================
# MEMUAT NASABAH DARI SQLITE
# =========================================================

nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)

assert nasabah is not None, (
    "Nasabah pengujian tidak berhasil dimuat"
)

assert nasabah.rekening, (
    "Daftar rekening nasabah tidak berhasil dimuat"
)

assert nasabah.deposito, (
    "Daftar deposito nasabah tidak berhasil dimuat"
)


# =========================================================
# MENCARI OBJEK REKENING DAN DEPOSITO
# =========================================================

rekening_deposito = next(
    (
        rekening
        for rekening in nasabah.rekening
        if rekening.norek == NOREK_DEPOSITO
    ),
    None
)

deposito = next(
    (
        deposito
        for deposito in nasabah.deposito
        if deposito.ID == ID_DEPOSITO
    ),
    None
)

assert rekening_deposito is not None, (
    "Rekening milik deposito tidak berhasil dimuat"
)

assert deposito is not None, (
    f"Deposito ID {ID_DEPOSITO} tidak berhasil dimuat"
)


# =========================================================
# MENAMPILKAN HASIL LOADER
# =========================================================

print("DATA NASABAH")
print(f"NIK              : {nasabah.NIK}")
print(f"Nama             : {nasabah.nama}")
print(f"Jumlah rekening  : {len(nasabah.rekening)}")
print(f"Jumlah deposito  : {len(nasabah.deposito)}")
print()

print("DATA REKENING DEPOSITO")
print(f"Norek            : {rekening_deposito.norek}")
print(f"Status           : {rekening_deposito.status}")
print(
    f"Saldo            : Rp"
    f"{Utilitas.format_rupiah(rekening_deposito.saldo)}"
)
print()

print("DATA DEPOSITO")
print(f"ID               : {deposito.ID}")
print(f"Norek            : {deposito.rekening.norek}")
print(
    f"Nominal          : Rp"
    f"{Utilitas.format_rupiah(deposito.nominal)}"
)
print(f"Bunga            : {deposito.bunga:.1%}")
print(f"Tenor            : {deposito.lama_bulan} bulan")
print(f"Tanggal buka     : {deposito.tanggal_buka}")
print(f"Jatuh tempo      : {deposito.jatuh_tempo}")
print(f"Status           : {deposito.status}")
print(f"Jenis ARO        : {deposito.jenis_aro}")
print(f"Lama ARO         : {deposito.lama_aro}")
print(f"Proses ARO       : {deposito.proses_aro}")
print()


# =========================================================
# MEMERIKSA DATA YANG DIPULIHKAN
# =========================================================

assert deposito.nominal == 1_000_000, (
    "Nominal deposito tidak berhasil dipulihkan"
)

assert deposito.bunga == 0.03, (
    "Bunga deposito tidak berhasil dipulihkan"
)

assert deposito.lama_bulan == 1, (
    "Tenor deposito tidak berhasil dipulihkan"
)

assert deposito.status == "aktif", (
    "Status deposito tidak berhasil dipulihkan"
)

assert deposito.jenis_aro == "tidak", (
    "Jenis ARO tidak berhasil dipulihkan"
)

assert deposito.lama_aro is None, (
    "Lama ARO seharusnya None"
)

assert deposito.proses_aro is None, (
    "Proses ARO seharusnya None"
)

assert isinstance(
    deposito.tanggal_buka,
    datetime.date
), "Tanggal buka belum dikembalikan menjadi datetime.date"

assert isinstance(
    deposito.jatuh_tempo,
    datetime.date
), "Jatuh tempo belum dikembalikan menjadi datetime.date"


# =========================================================
# MEMERIKSA RELASI OBJEK
# =========================================================

assert rekening_deposito.pemilik is nasabah, (
    "Pemilik rekening bukan objek nasabah yang dimuat"
)

assert deposito.pemilik is nasabah, (
    "Pemilik deposito bukan objek nasabah yang dimuat"
)

assert deposito.rekening is rekening_deposito, (
    "Deposito tidak menunjuk objek rekening yang sama"
)

assert deposito.rekening in nasabah.rekening, (
    "Rekening deposito tidak berada dalam daftar rekening nasabah"
)

assert deposito in nasabah.deposito, (
    "Deposito tidak berada dalam daftar deposito nasabah"
)


print("✅ Nasabah berhasil dimuat dari SQLite")
print("✅ Seluruh rekening nasabah berhasil dimuat")
print("✅ Deposito ID 5 berhasil dimuat")
print("✅ Seluruh tanggal kembali menjadi datetime.date")
print("✅ Deposito menunjuk objek nasabah yang benar")
print("✅ Deposito menunjuk objek rekening yang sama")
print("✅ DepositoLoader bekerja sesuai rancangan")
