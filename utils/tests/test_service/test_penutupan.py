# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
#     PengajuanRepository
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
#
#
# # NOREK = "4001518075450587"
# #
# # data_rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
# #
# # pengajuan = PengajuanRepository.cari_pengajuan_aktif(
# #     norek=NOREK,
# #     jenis="tutup"
# # )
# #
# # daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
# #
# #
# # print("STATE REKENING")
# # print("Norek  :", data_rekening["norek"])
# # print("Level  :", data_rekening["level"])
# # print("Saldo  :", data_rekening["saldo"])
# # print("Status :", data_rekening["status"])
# #
# # print()
# # print("PENGAJUAN PENUTUPAN")
# #
# # if pengajuan is None:
# #     print("Pengajuan tidak ditemukan")
# # else:
# #     print("ID                :", pengajuan["id"])
# #     print("Norek             :", pengajuan["norek"])
# #     print("Jenis             :", pengajuan["jenis"])
# #     print("Alasan            :", pengajuan["alasan"])
# #     print("Status            :", pengajuan["status"])
# #     print("Waktu pengajuan   :", pengajuan["waktu_pengajuan"])
# #     print("Waktu diproses    :", pengajuan["waktu_diproses"])
# #     print("Catatan admin     :", pengajuan["catatan_admin"])
# #
# # print()
# # print("AUDIT TERBARU")
# #
# # if daftar_audit:
# #     audit_terbaru = daftar_audit[0]
# #
# #     print("ID       :", audit_terbaru["id"])
# #     print("Kategori :", audit_terbaru["kategori"])
# #     print("Jenis    :", audit_terbaru["jenis"])
# #     print("Waktu    :", audit_terbaru["waktu"])
# #     print("Log      :", audit_terbaru["log"])
# #     print("Nama     :", audit_terbaru["nama"])
# #     print("NIK      :", audit_terbaru["nik"])
# #     print("Norek    :", audit_terbaru["norek"])
# # else:
# #     print("Audit tidak ditemukan")
# #
# #
# # assert data_rekening is not None
# # assert data_rekening["status"] == "aktif"
# #
# # assert pengajuan is not None
# # assert pengajuan["norek"] == NOREK
# # assert pengajuan["jenis"] == "tutup"
# # assert pengajuan["status"] == "diajukan"
# # assert pengajuan["waktu_diproses"] is None
# # assert pengajuan["catatan_admin"] is None
# #
# # assert daftar_audit
# # assert daftar_audit[0]["jenis"] == "pengajuan penutupan"
# # assert daftar_audit[0]["norek"] == NOREK
# #
# # print()
# # print("✅ Pengajuan penutupan berhasil disimpan")
# # print("✅ Rekening tetap aktif selama menunggu admin")
# # print("✅ Waktu proses dan catatan admin masih kosong")
# # print("✅ Audit pengajuan berhasil disimpan")
#
#
#
#
#
# from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
#     PengajuanRepository
# )
# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
#
#
# ID_PENGAJUAN = 1
# NOREK = "4001518075450587"
#
#
# pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
#     ID_PENGAJUAN
# )
#
# rekening = RekeningRepository.cari_rekening_dengan_norek(
#     NOREK
# )
#
# daftar_audit = AuditRepository.cari_audit_dengan_norek(
#     NOREK
# )
#
#
# print("KONDISI PENGAJUAN")
#
# if pengajuan is None:
#     raise AssertionError("Pengajuan tidak ditemukan")
#
# print("ID                :", pengajuan["id"])
# print("Norek             :", pengajuan["norek"])
# print("Jenis             :", pengajuan["jenis"])
# print("Alasan            :", pengajuan["alasan"])
# print("Status            :", pengajuan["status"])
# print("Waktu pengajuan   :", pengajuan["waktu_pengajuan"])
# print("Waktu diproses    :", pengajuan["waktu_diproses"])
# print("Catatan admin     :", pengajuan["catatan_admin"])
#
#
# print()
# print("KONDISI REKENING")
#
# if rekening is None:
#     raise AssertionError("Rekening tidak ditemukan")
#
# print("Norek  :", rekening["norek"])
# print("Saldo  :", rekening["saldo"])
# print("Level  :", rekening["level"])
# print("Status :", rekening["status"])
#
#
# print()
# print("AUDIT TERBARU")
#
# if not daftar_audit:
#     raise AssertionError("Audit rekening tidak ditemukan")
#
# audit_terbaru = daftar_audit[0]
#
# print("ID       :", audit_terbaru["id"])
# print("Kategori :", audit_terbaru["kategori"])
# print("Jenis    :", audit_terbaru["jenis"])
# print("Waktu    :", audit_terbaru["waktu"])
# print("Log      :", audit_terbaru["log"])
# print("Nama     :", audit_terbaru["nama"])
# print("NIK      :", audit_terbaru["nik"])
# print("Norek    :", audit_terbaru["norek"])
#
#
# assert pengajuan["id"] == ID_PENGAJUAN
# assert pengajuan["norek"] == NOREK
# assert pengajuan["jenis"] == "tutup"
# assert pengajuan["status"] == "ditolak"
# assert pengajuan["waktu_diproses"] is not None
# assert pengajuan["catatan_admin"] is not None
# assert pengajuan["catatan_admin"].strip() != ""
#
# assert rekening["status"] == "aktif"
#
# assert audit_terbaru["kategori"] == "rekening"
# assert audit_terbaru["jenis"] == "penolakan pengajuan"
# assert audit_terbaru["norek"] == NOREK
#
# print()
# print("✅ Status pengajuan berhasil berubah menjadi ditolak")
# print("✅ Waktu proses dan catatan admin berhasil disimpan")
# print("✅ Rekening tetap aktif setelah pengajuan ditolak")
# print("✅ Audit penolakan berhasil disimpan")
#
#
#

# from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository  import (
#     PengajuanRepository
# )
# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
#
#
# ID_PENGAJUAN = 2
# NOREK = "4001518075450587"
#
#
# pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(ID_PENGAJUAN)
# rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
# daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
# daftar_pending = PengajuanRepository.cari_semua_pengajuan_diajukan()
#
#
# print("HASIL PENGAJUAN")
# print("ID               :", pengajuan["id"])
# print("Jenis            :", pengajuan["jenis"])
# print("Status           :", pengajuan["status"])
# print("Waktu diproses   :", pengajuan["waktu_diproses"])
# print("Catatan admin    :", pengajuan["catatan_admin"])
#
# print()
# print("KONDISI REKENING")
# print("Norek            :", rekening["norek"])
# print("Status rekening  :", rekening["status"])
# print("Saldo            :", rekening["saldo"])
#
# print()
# print("AUDIT TERBARU")
# audit_terbaru = daftar_audit[0]
#
# print("Jenis            :", audit_terbaru["jenis"])
# print("Log              :", audit_terbaru["log"])
# print("NIK              :", audit_terbaru["nik"])
# print("Norek            :", audit_terbaru["norek"])
#
# print()
# print("PENGAJUAN YANG MASIH MENUNGGU")
# print("Jumlah           :", len(daftar_pending))
#
#
# assert pengajuan["status"] == "disetujui"
# assert pengajuan["waktu_diproses"] is not None
# assert pengajuan["catatan_admin"] is not None
# assert rekening["status"] == "aktif"
# assert audit_terbaru["jenis"] == "persetujuan pengajuan"
# assert all(data["id"] != ID_PENGAJUAN for data in daftar_pending)
#
# print()
# print("✅ Status pengajuan berhasil diubah menjadi disetujui")
# print("✅ Waktu proses dan catatan admin berhasil disimpan")
# print("✅ Rekening tetap aktif sampai penutupan diselesaikan nasabah")
# print("✅ Audit persetujuan berhasil disimpan")
# print("✅ Pengajuan tidak lagi muncul dalam daftar yang menunggu")


# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository  import (
#     PengajuanRepository
# )
# from bank_djago.penyimpanan.repositories.riwayat_repository import (
#     RiwayatRepository
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
#
#
# NOREK = "4001518075450587"
# ID_PENGAJUAN = 2
#
#
# data_rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
#
# data_pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
#     ID_PENGAJUAN
# )
#
# daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(NOREK)
#
# daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
#
#
# print("KONDISI REKENING SETELAH PENUTUPAN")
# print("Norek   :", data_rekening["norek"])
# print("Saldo   :", data_rekening["saldo"])
# print("Status  :", data_rekening["status"])
#
#
# print()
# print("KONDISI PENGAJUAN")
# print("ID              :", data_pengajuan["id"])
# print("Jenis           :", data_pengajuan["jenis"])
# print("Status          :", data_pengajuan["status"])
# print("Waktu diproses  :", data_pengajuan["waktu_diproses"])
# print("Catatan admin   :", data_pengajuan["catatan_admin"])
#
#
# print()
# print("RIWAYAT TERBARU")
#
# riwayat_terbaru = daftar_riwayat[0]
#
# print("Kategori :", riwayat_terbaru["kategori"])
# print("Jenis    :", riwayat_terbaru["jenis"])
# print("Waktu    :", riwayat_terbaru["waktu"])
# print("Log      :", riwayat_terbaru["log"])
#
#
# print()
# print("AUDIT TERBARU")
#
# audit_terbaru = daftar_audit[0]
#
# print("Kategori :", audit_terbaru["kategori"])
# print("Jenis    :", audit_terbaru["jenis"])
# print("Waktu    :", audit_terbaru["waktu"])
# print("Log      :", audit_terbaru["log"])
# print("Nama     :", audit_terbaru["nama"])
# print("NIK      :", audit_terbaru["nik"])
# print("Norek    :", audit_terbaru["norek"])
#
#
# assert data_rekening["saldo"] == 0
# assert data_rekening["status"] == "tutup"
#
# assert data_pengajuan["id"] == ID_PENGAJUAN
# assert data_pengajuan["jenis"] == "tutup"
# assert data_pengajuan["status"] == "disetujui"
#
# assert riwayat_terbaru["jenis"] == "penutupan rekening"
# assert audit_terbaru["jenis"] == "penutupan tarik saldo"
#
#
# print()
# print("✅ Saldo rekening berhasil dikosongkan")
# print("✅ Status rekening berhasil diubah menjadi tutup")
# print("✅ Persetujuan penutupan tetap tersimpan")
# print("✅ Riwayat penutupan berhasil disimpan")
# print("✅ Audit penarikan seluruh saldo berhasil disimpan")
# print("✅ Penyelesaian penutupan rekening bekerja sesuai rancangan")




from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)


# NOREK_ASAL = "3001946913802745"
# NOREK_PENERIMA = "2001569043650499"
#
#
# rekening_asal = RekeningRepository.cari_rekening_dengan_norek(
#     NOREK_ASAL
# )
#
# rekening_penerima = RekeningRepository.cari_rekening_dengan_norek(
#     NOREK_PENERIMA
# )
#
#
# print("KONDISI SEBELUM PENUTUPAN")
#
# print()
# print("REKENING ASAL")
# print("Norek  :", rekening_asal["norek"])
# print("Saldo  :", rekening_asal["saldo"])
# print("Status :", rekening_asal["status"])
#
# print()
# print("REKENING PENERIMA")
# print("Norek  :", rekening_penerima["norek"])
# print("Saldo  :", rekening_penerima["saldo"])
# print("Status :", rekening_penerima["status"])



# NOREK_ASAL = "3001946913802745"
# NOREK_PENERIMA = "2001569043650499"
#
#
# rekening_asal = RekeningRepository.cari_rekening_dengan_norek(
#     NOREK_ASAL
# )
#
# rekening_penerima = RekeningRepository.cari_rekening_dengan_norek(
#     NOREK_PENERIMA
# )
#
#
# print("KONDISI SETELAH PENUTUPAN")
#
# print()
# print("REKENING ASAL")
# print("Norek  :", rekening_asal["norek"])
# print("Saldo  :", rekening_asal["saldo"])
# print("Status :", rekening_asal["status"])
#
# print()
# print("REKENING PENERIMA")
# print("Norek  :", rekening_penerima["norek"])
# print("Saldo  :", rekening_penerima["saldo"])
# print("Status :", rekening_penerima["status"])


from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository  import (
    PengajuanRepository
)
from bank_djago.penyimpanan.repositories.riwayat_repository import (
    RiwayatRepository
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)


NOREK_ASAL = "3001946913802745"
NOREK_PENERIMA = "2001569043650499"
ID_PENGAJUAN = 3


rekening_asal = RekeningRepository.cari_rekening_dengan_norek(
    NOREK_ASAL
)

rekening_penerima = RekeningRepository.cari_rekening_dengan_norek(
    NOREK_PENERIMA
)

pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
    ID_PENGAJUAN
)

riwayat_asal = RiwayatRepository.cari_seluruh_riwayat(
    NOREK_ASAL
)

audit_asal = AuditRepository.cari_audit_dengan_norek(
    NOREK_ASAL
)


print("REKENING ASAL SETELAH PENUTUPAN")
print("Norek  :", rekening_asal["norek"])
print("Saldo  :", rekening_asal["saldo"])
print("Status :", rekening_asal["status"])


print()
print("REKENING PENERIMA SETELAH TRANSFER")
print("Norek  :", rekening_penerima["norek"])
print("Saldo  :", rekening_penerima["saldo"])
print("Status :", rekening_penerima["status"])


print()
print("KONDISI PENGAJUAN")
print("ID      :", pengajuan["id"])
print("Jenis   :", pengajuan["jenis"])
print("Status  :", pengajuan["status"])


print()
print("RIWAYAT TERBARU REKENING ASAL")

riwayat_terbaru = riwayat_asal[0]

print("Jenis   :", riwayat_terbaru["jenis"])
print("Waktu   :", riwayat_terbaru["waktu"])
print("Log     :", riwayat_terbaru["log"])


print()
print("AUDIT TERBARU")

audit_terbaru = audit_asal[0]

print("Jenis   :", audit_terbaru["jenis"])
print("Waktu   :", audit_terbaru["waktu"])
print("Log     :", audit_terbaru["log"])
print("NIK     :", audit_terbaru["nik"])
print("Norek   :", audit_terbaru["norek"])


assert rekening_asal["saldo"] == 0
assert rekening_asal["status"] == "tutup"

assert rekening_penerima["saldo"] == 109_000_000
assert rekening_penerima["status"] == "aktif"

assert pengajuan["id"] == ID_PENGAJUAN
assert pengajuan["status"] == "disetujui"

assert riwayat_terbaru["jenis"] == "penutupan rekening"
assert audit_terbaru["jenis"] == "penutupan transfer saldo"


print()
print("✅ Saldo rekening asal berhasil dikosongkan")
print("✅ Rekening asal berhasil ditutup")
print("✅ Saldo penerima bertambah menjadi Rp109.000.000")
print("✅ Rekening penerima tetap aktif")
print("✅ Pengajuan persetujuan tetap tersimpan")
print("✅ Riwayat dan audit penutupan berhasil disimpan")