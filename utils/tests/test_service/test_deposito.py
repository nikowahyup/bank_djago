# from bank_djago.penyimpanan.repositories.nasabah_repository import (
#     NasabahRepository
# )
# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.repositories.deposito_repository import (
#     DepositoRepository
# )
# from bank_djago.penyimpanan.repositories.riwayat_repository import (
#     RiwayatRepository
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
# from bank_djago.utils.utility import Utilitas
#
#
# NIK_PENGUJIAN = "1111222233334444"
# NOREK_PENGUJIAN = "2001569043650499"
#
# NOMINAL_DEPOSITO = 1_000_000
# SALDO_SEBELUM = 109_000_000
# SALDO_SESUDAH = SALDO_SEBELUM - NOMINAL_DEPOSITO
#
#
# # =========================================================
# # MENGAMBIL DATA DARI SQLITE
# # =========================================================
#
# nasabah = NasabahRepository.cari_nasabah_dengan_nik(
#     NIK_PENGUJIAN
# )
#
# rekening = RekeningRepository.cari_rekening_dengan_norek(
#     NOREK_PENGUJIAN
# )
#
# daftar_deposito = DepositoRepository.cari_deposito_dengan_norek(
#     NOREK_PENGUJIAN
# )
#
# daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     NOREK_PENGUJIAN
# )
#
# daftar_audit = AuditRepository.cari_audit_dengan_norek(
#     NOREK_PENGUJIAN
# )
#
#
# # =========================================================
# # MEMASTIKAN DATA UTAMA DITEMUKAN
# # =========================================================
#
# assert nasabah is not None, "Nasabah tidak ditemukan"
# assert rekening is not None, "Rekening tidak ditemukan"
# assert daftar_deposito, "Deposito tidak ditemukan"
#
#
# # Repository mengurutkan deposito berdasarkan ID dari kecil
# # ke besar, sehingga elemen terakhir adalah deposito terbaru.
# deposito_terbaru = daftar_deposito[-1]
#
# riwayat_deposito = [
#     riwayat
#     for riwayat in daftar_riwayat
#     if riwayat["jenis"] == "deposito"
# ]
#
# audit_deposito = [
#     audit
#     for audit in daftar_audit
#     if audit["jenis"] == "deposito"
# ]
#
# assert riwayat_deposito, "Riwayat pembukaan deposito tidak ditemukan"
# assert audit_deposito, "Audit pembukaan deposito tidak ditemukan"
#
# # Riwayat dan audit diurutkan berdasarkan ID terbaru.
# riwayat_terbaru = riwayat_deposito[0]
# audit_terbaru = audit_deposito[0]
#
#
# # =========================================================
# # MENAMPILKAN HASIL
# # =========================================================
#
# print("DATA NASABAH")
# print(f"NIK     : {nasabah['nik']}")
# print(f"Nama    : {nasabah['nama']}")
# print(f"Alamat  : {nasabah['alamat']}")
# print()
#
# print("KONDISI REKENING")
# print(f"Norek   : {rekening['norek']}")
# print(f"Status  : {rekening['status']}")
# print(
#     f"Saldo   : Rp"
#     f"{Utilitas.format_rupiah(rekening['saldo'])}"
# )
# print()
#
# print("DEPOSITO TERBARU")
# print(f"ID             : {deposito_terbaru['id']}")
# print(f"Norek          : {deposito_terbaru['norek']}")
# print(
#     f"Nominal        : Rp"
#     f"{Utilitas.format_rupiah(deposito_terbaru['nominal'])}"
# )
# print(f"Bunga          : {deposito_terbaru['bunga']:.1%}")
# print(f"Tenor          : {deposito_terbaru['lama_bulan']} bulan")
# print(f"Tanggal buka   : {deposito_terbaru['tanggal_buka']}")
# print(f"Jatuh tempo    : {deposito_terbaru['jatuh_tempo']}")
# print(f"Status         : {deposito_terbaru['status']}")
# print(f"Jenis ARO      : {deposito_terbaru['jenis_aro']}")
# print(f"Lama ARO       : {deposito_terbaru['lama_aro']}")
# print(f"Proses ARO     : {deposito_terbaru['proses_aro']}")
# print()
#
# print("RIWAYAT TERBARU")
# print(f"ID        : {riwayat_terbaru['id']}")
# print(f"Kategori  : {riwayat_terbaru['kategori']}")
# print(f"Jenis     : {riwayat_terbaru['jenis']}")
# print(f"Waktu     : {riwayat_terbaru['waktu']}")
# print(f"Log       : {riwayat_terbaru['log']}")
# print()
#
# print("AUDIT TERBARU")
# print(f"ID        : {audit_terbaru['id']}")
# print(f"Kategori  : {audit_terbaru['kategori']}")
# print(f"Jenis     : {audit_terbaru['jenis']}")
# print(f"Waktu     : {audit_terbaru['waktu']}")
# print(f"Log       : {audit_terbaru['log']}")
# print(f"Nama      : {audit_terbaru['nama']}")
# print(f"NIK       : {audit_terbaru['nik']}")
# print(f"Norek     : {audit_terbaru['norek']}")
# print()
#
#
# # =========================================================
# # PEMERIKSAAN INTEGRITAS
# # =========================================================
#
# assert rekening["saldo"] == SALDO_SESUDAH, (
#     "Saldo rekening tidak berkurang sesuai nominal deposito"
# )
#
# assert deposito_terbaru["norek"] == NOREK_PENGUJIAN, (
#     "Foreign key deposito tidak mengarah ke rekening pengujian"
# )
#
# assert deposito_terbaru["nominal"] == NOMINAL_DEPOSITO, (
#     "Nominal deposito tidak sesuai"
# )
#
# assert deposito_terbaru["bunga"] == 0.03, (
#     "Bunga deposito tenor satu bulan tidak sesuai"
# )
#
# assert deposito_terbaru["lama_bulan"] == 1, (
#     "Tenor deposito tidak sesuai"
# )
#
# assert deposito_terbaru["status"] == "aktif", (
#     "Status awal deposito bukan aktif"
# )
#
# assert deposito_terbaru["jenis_aro"] == "tidak", (
#     "Jenis ARO deposito tidak sesuai"
# )
#
# assert deposito_terbaru["lama_aro"] is None, (
#     "Deposito tanpa ARO seharusnya tidak memiliki lama ARO"
# )
#
# assert deposito_terbaru["proses_aro"] is None, (
#     "Deposito baru seharusnya belum memiliki tanggal proses ARO"
# )
#
# assert riwayat_terbaru["norek"] == NOREK_PENGUJIAN, (
#     "Riwayat tersimpan pada rekening yang salah"
# )
#
# assert audit_terbaru["nik"] == NIK_PENGUJIAN, (
#     "Audit tersimpan dengan NIK yang salah"
# )
#
# assert audit_terbaru["norek"] == NOREK_PENGUJIAN, (
#     "Audit tersimpan dengan nomor rekening yang salah"
# )
#
#
# print("✅ Saldo rekening berhasil dikurangi")
# print("✅ Deposito berhasil disimpan dengan ID global")
# print("✅ Foreign key deposito mengarah ke rekening yang benar")
# print("✅ Tenor, bunga, status, dan ARO tersimpan sesuai pilihan")
# print("✅ Riwayat pembukaan deposito berhasil disimpan")
# print("✅ Audit pembukaan deposito berhasil disimpan")
# print("✅ Pembukaan deposito SQLite bekerja sesuai rancangan")











# import datetime
#
# from bank_djago.penyimpanan.loaders.nasabah_loader import (
#     NasabahLoader
# )
# from bank_djago.utils.utility import Utilitas
#
#
# NIK_PENGUJIAN = "1111222233334444"
# NOREK_DEPOSITO = "2001569043650499"
# ID_DEPOSITO = 5
#
#
# # =========================================================
# # MEMUAT NASABAH DARI SQLITE
# # =========================================================
#
# nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# assert nasabah is not None, (
#     "Nasabah pengujian tidak berhasil dimuat"
# )
#
# assert nasabah.rekening, (
#     "Daftar rekening nasabah tidak berhasil dimuat"
# )
#
# assert nasabah.deposito, (
#     "Daftar deposito nasabah tidak berhasil dimuat"
# )
#
#
# # =========================================================
# # MENCARI OBJEK REKENING DAN DEPOSITO
# # =========================================================
#
# rekening_deposito = next(
#     (
#         rekening
#         for rekening in nasabah.rekening
#         if rekening.norek == NOREK_DEPOSITO
#     ),
#     None
# )
#
# deposito = next(
#     (
#         deposito
#         for deposito in nasabah.deposito
#         if deposito.ID == ID_DEPOSITO
#     ),
#     None
# )
#
# assert rekening_deposito is not None, (
#     "Rekening milik deposito tidak berhasil dimuat"
# )
#
# assert deposito is not None, (
#     f"Deposito ID {ID_DEPOSITO} tidak berhasil dimuat"
# )
#
#
# # =========================================================
# # MENAMPILKAN HASIL LOADER
# # =========================================================
#
# print("DATA NASABAH")
# print(f"NIK              : {nasabah.NIK}")
# print(f"Nama             : {nasabah.nama}")
# print(f"Jumlah rekening  : {len(nasabah.rekening)}")
# print(f"Jumlah deposito  : {len(nasabah.deposito)}")
# print()
#
# print("DATA REKENING DEPOSITO")
# print(f"Norek            : {rekening_deposito.norek}")
# print(f"Status           : {rekening_deposito.status}")
# print(
#     f"Saldo            : Rp"
#     f"{Utilitas.format_rupiah(rekening_deposito.saldo)}"
# )
# print()
#
# print("DATA DEPOSITO")
# print(f"ID               : {deposito.ID}")
# print(f"Norek            : {deposito.rekening.norek}")
# print(
#     f"Nominal          : Rp"
#     f"{Utilitas.format_rupiah(deposito.nominal)}"
# )
# print(f"Bunga            : {deposito.bunga:.1%}")
# print(f"Tenor            : {deposito.lama_bulan} bulan")
# print(f"Tanggal buka     : {deposito.tanggal_buka}")
# print(f"Jatuh tempo      : {deposito.jatuh_tempo}")
# print(f"Status           : {deposito.status}")
# print(f"Jenis ARO        : {deposito.jenis_aro}")
# print(f"Lama ARO         : {deposito.lama_aro}")
# print(f"Proses ARO       : {deposito.proses_aro}")
# print()
#
#
# # =========================================================
# # MEMERIKSA DATA YANG DIPULIHKAN
# # =========================================================
#
# assert deposito.nominal == 1_000_000, (
#     "Nominal deposito tidak berhasil dipulihkan"
# )
#
# assert deposito.bunga == 0.03, (
#     "Bunga deposito tidak berhasil dipulihkan"
# )
#
# assert deposito.lama_bulan == 1, (
#     "Tenor deposito tidak berhasil dipulihkan"
# )
#
# assert deposito.status == "aktif", (
#     "Status deposito tidak berhasil dipulihkan"
# )
#
# assert deposito.jenis_aro == "tidak", (
#     "Jenis ARO tidak berhasil dipulihkan"
# )
#
# assert deposito.lama_aro is None, (
#     "Lama ARO seharusnya None"
# )
#
# assert deposito.proses_aro is None, (
#     "Proses ARO seharusnya None"
# )
#
# assert isinstance(
#     deposito.tanggal_buka,
#     datetime.date
# ), "Tanggal buka belum dikembalikan menjadi datetime.date"
#
# assert isinstance(
#     deposito.jatuh_tempo,
#     datetime.date
# ), "Jatuh tempo belum dikembalikan menjadi datetime.date"
#
#
# # =========================================================
# # MEMERIKSA RELASI OBJEK
# # =========================================================
#
# assert rekening_deposito.pemilik is nasabah, (
#     "Pemilik rekening bukan objek nasabah yang dimuat"
# )
#
# assert deposito.pemilik is nasabah, (
#     "Pemilik deposito bukan objek nasabah yang dimuat"
# )
#
# assert deposito.rekening is rekening_deposito, (
#     "Deposito tidak menunjuk objek rekening yang sama"
# )
#
# assert deposito.rekening in nasabah.rekening, (
#     "Rekening deposito tidak berada dalam daftar rekening nasabah"
# )
#
# assert deposito in nasabah.deposito, (
#     "Deposito tidak berada dalam daftar deposito nasabah"
# )
#
#
# print("✅ Nasabah berhasil dimuat dari SQLite")
# print("✅ Seluruh rekening nasabah berhasil dimuat")
# print("✅ Deposito ID 5 berhasil dimuat")
# print("✅ Seluruh tanggal kembali menjadi datetime.date")
# print("✅ Deposito menunjuk objek nasabah yang benar")
# print("✅ Deposito menunjuk objek rekening yang sama")
# print("✅ DepositoLoader bekerja sesuai rancangan")


print("-----------------------------------------------------------------------------------------")

print("TES PENCAIRAN DEPOSITO")



from bank_djago.penyimpanan.sqlite.database import (
    buat_koneksi
)
from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.penyimpanan.repositories.deposito_repository import (
    DepositoRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.repositories.riwayat_repository import (
    RiwayatRepository
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)
from bank_djago.utils.utility import Utilitas


NIK_PENGUJIAN = "1111222233334444"
NOREK_PENGUJIAN = "2001569043650499"
ID_DEPOSITO = 5


# =========================================================
# KONDISI SEBELUM PENCAIRAN
# =========================================================

rekening_sebelum = (
    RekeningRepository.cari_rekening_dengan_norek(
        NOREK_PENGUJIAN
    )
)

deposito_sebelum = (
    DepositoRepository.cari_deposito_dengan_id(
        ID_DEPOSITO
    )
)

riwayat_sebelum = (
    RiwayatRepository.cari_seluruh_riwayat(
        NOREK_PENGUJIAN
    )
)

audit_sebelum = (
    AuditRepository.cari_audit_dengan_norek(
        NOREK_PENGUJIAN
    )
)

assert rekening_sebelum is not None, (
    "Rekening pengujian tidak ditemukan"
)

assert deposito_sebelum is not None, (
    "Deposito pengujian tidak ditemukan"
)

if deposito_sebelum["status"] == StatusDeposito.DICAIRKAN:
    raise ValueError(
        "Deposito ID 5 sudah dicairkan. "
        "Pengujian ini tidak boleh dijalankan kembali."
    )

saldo_sebelum = rekening_sebelum["saldo"]
jumlah_riwayat_sebelum = len(riwayat_sebelum)
jumlah_audit_sebelum = len(audit_sebelum)

print("KONDISI SEBELUM PENCAIRAN")
print(f"ID deposito       : {deposito_sebelum['id']}")
print(f"Status deposito   : {deposito_sebelum['status']}")
print(
    f"Saldo rekening    : Rp"
    f"{Utilitas.format_rupiah(saldo_sebelum)}"
)
print(
    f"Nominal deposito  : Rp"
    f"{Utilitas.format_rupiah(deposito_sebelum['nominal'])}"
)
print(f"Jumlah riwayat    : {jumlah_riwayat_sebelum}")
print(f"Jumlah audit      : {jumlah_audit_sebelum}")
print()


# =========================================================
# MENYIAPKAN STATUS JATUH TEMPO
# =========================================================

if deposito_sebelum["status"] != StatusDeposito.JATUH_TEMPO:
    koneksi = buat_koneksi()

    try:
        jumlah_baris = (
            DepositoRepository.perbarui_status_deposito(
                id_deposito=ID_DEPOSITO,
                status_baru=StatusDeposito.JATUH_TEMPO,
                koneksi=koneksi
            )
        )

        if jumlah_baris != 1:
            raise ValueError(
                "Gagal menyiapkan status jatuh tempo"
            )

        koneksi.commit()

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()

print("✅ Status deposito disiapkan menjadi jatuh tempo")


# =========================================================
# MEMUAT ULANG OBJEK DARI SQLITE
# =========================================================

nasabah = NasabahLoader.muat_nasabah(
    NIK_PENGUJIAN
)

assert nasabah is not None, (
    "Nasabah gagal dimuat"
)

deposito = next(
    (
        item
        for item in nasabah.deposito
        if item.ID == ID_DEPOSITO
    ),
    None
)

assert deposito is not None, (
    "Objek deposito ID 5 gagal dimuat"
)

assert deposito.status == StatusDeposito.JATUH_TEMPO, (
    "Objek deposito tidak memuat status jatuh tempo"
)

assert deposito.rekening.norek == NOREK_PENGUJIAN, (
    "Deposito terhubung dengan rekening yang salah"
)

total_yang_diharapkan = deposito.total_pencairan
saldo_yang_diharapkan = (
    saldo_sebelum + total_yang_diharapkan
)

print()
print("DATA PENCAIRAN")
print(f"Tanggal buka      : {deposito.tanggal_buka}")
print(f"Jatuh tempo       : {deposito.jatuh_tempo}")
print(f"Bunga             : {deposito.bunga:.1%}")
print(
    f"Total pencairan   : Rp"
    f"{Utilitas.format_rupiah(total_yang_diharapkan)}"
)
print()


# =========================================================
# MENJALANKAN PENCAIRAN
# =========================================================

total_pencairan = (
    DepositoService.cairkan_deposito(
        deposito=deposito,
        hari_ini=deposito.jatuh_tempo
    )
)


# =========================================================
# MENGAMBIL KONDISI SETELAH PENCAIRAN
# =========================================================

rekening_setelah = (
    RekeningRepository.cari_rekening_dengan_norek(
        NOREK_PENGUJIAN
    )
)

deposito_setelah = (
    DepositoRepository.cari_deposito_dengan_id(
        ID_DEPOSITO
    )
)

riwayat_setelah = (
    RiwayatRepository.cari_seluruh_riwayat(
        NOREK_PENGUJIAN
    )
)

audit_setelah = (
    AuditRepository.cari_audit_dengan_norek(
        NOREK_PENGUJIAN
    )
)

riwayat_pencairan = [
    item
    for item in riwayat_setelah
    if item["jenis"] == "pencairan deposito"
]

audit_pencairan = [
    item
    for item in audit_setelah
    if item["jenis"] == "pencairan deposito"
]

assert riwayat_pencairan, (
    "Riwayat pencairan tidak ditemukan"
)

assert audit_pencairan, (
    "Audit pencairan tidak ditemukan"
)

riwayat_terbaru = riwayat_pencairan[0]
audit_terbaru = audit_pencairan[0]


# =========================================================
# MENAMPILKAN KONDISI SETELAH
# =========================================================

print("KONDISI SETELAH PENCAIRAN")
print(
    f"Saldo rekening    : Rp"
    f"{Utilitas.format_rupiah(rekening_setelah['saldo'])}"
)
print(f"Status deposito   : {deposito_setelah['status']}")
print(f"Jumlah riwayat    : {len(riwayat_setelah)}")
print(f"Jumlah audit      : {len(audit_setelah)}")
print()

print("RIWAYAT PENCAIRAN")
print(f"ID                : {riwayat_terbaru['id']}")
print(f"Jenis             : {riwayat_terbaru['jenis']}")
print(f"Waktu             : {riwayat_terbaru['waktu']}")
print(f"Log               : {riwayat_terbaru['log']}")
print()

print("AUDIT PENCAIRAN")
print(f"ID                : {audit_terbaru['id']}")
print(f"Jenis             : {audit_terbaru['jenis']}")
print(f"Waktu             : {audit_terbaru['waktu']}")
print(f"Log               : {audit_terbaru['log']}")
print(f"Nama              : {audit_terbaru['nama']}")
print(f"NIK               : {audit_terbaru['nik']}")
print(f"Norek             : {audit_terbaru['norek']}")
print()


# =========================================================
# PEMERIKSAAN HASIL
# =========================================================

assert total_pencairan == total_yang_diharapkan, (
    "Nilai yang dikembalikan service tidak sesuai"
)

assert rekening_setelah["saldo"] == saldo_yang_diharapkan, (
    "Saldo SQLite tidak bertambah sesuai total pencairan"
)

assert deposito_setelah["status"] == StatusDeposito.DICAIRKAN, (
    "Status deposito SQLite tidak berubah menjadi dicairkan"
)

assert deposito.rekening.saldo == saldo_yang_diharapkan, (
    "Saldo objek rekening tidak berhasil disinkronkan"
)

assert deposito.status == StatusDeposito.DICAIRKAN, (
    "Status objek deposito tidak berhasil disinkronkan"
)

assert len(riwayat_setelah) == jumlah_riwayat_sebelum + 1, (
    "Jumlah riwayat tidak bertambah tepat satu"
)

assert len(audit_setelah) == jumlah_audit_sebelum + 1, (
    "Jumlah audit tidak bertambah tepat satu"
)

assert riwayat_terbaru["norek"] == NOREK_PENGUJIAN, (
    "Riwayat pencairan tersimpan pada rekening yang salah"
)

assert audit_terbaru["nik"] == NIK_PENGUJIAN, (
    "Audit pencairan memiliki NIK yang salah"
)

assert audit_terbaru["norek"] == NOREK_PENGUJIAN, (
    "Audit pencairan memiliki norek yang salah"
)


print("✅ Status jatuh tempo berhasil disiapkan")
print("✅ Total pencairan berhasil dihitung")
print("✅ Saldo rekening SQLite berhasil ditambahkan")
print("✅ Status deposito berubah menjadi dicairkan")
print("✅ Objek rekening dan deposito berhasil disinkronkan")
print("✅ Riwayat pencairan bertambah tepat satu")
print("✅ Audit pencairan bertambah tepat satu")
print("✅ Pencairan deposito SQLite bekerja sesuai rancangan")