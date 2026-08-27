from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
# from bank_djago.utils.tests.test_service.test_ambil_rekening import data_rekening
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository

# nasabah = NasabahRepository.cari_nasabah_dengan_nik('1111222233334444')
# daftar_rekening = RekeningRepository.cari_rekening_dengan_nik('1111222233334444')
#
# if daftar_rekening:
#     print('jumlah rekening milik',nasabah["nama"],"=",len(data_rekening))
#
#     for i,data in enumerate(data_rekening,start=1):
#         print({i})
#         print("nomor rekening :",data["norek"])
#         print("saldo ",data["saldo"])
#         print("level",data["level"])



# nasabah = NasabahRepository.cari_nasabah_dengan_nik(
#     "1111222233334444"
# )
#
# daftar_rekening = RekeningRepository.cari_rekening_dengan_nik(
#     "1111222233334444"
# )
#
# if daftar_rekening:
#     print(
#         "jumlah rekening milik",
#         nasabah["nama"],
#         "=",
#         len(daftar_rekening)
#     )
#
#     for i, data in enumerate(daftar_rekening, start=1):
#         print(i)
#         print("nomor rekening :", data["norek"])
#         print("saldo          :", data["saldo"])
#         print("level          :", data["level"])




# nasabah = NasabahRepository.cari_nasabah_dengan_nik(
#     "1111222233334444"
# )
#
# daftar_rekening = RekeningRepository.cari_rekening_dengan_nik(
#     "1111222233334444"
# )
#
# if daftar_rekening:
#     print(
#         "jumlah rekening milik",
#         nasabah["nama"],
#         "=",
#         len(daftar_rekening)
#     )
#
#     for i, data in enumerate(daftar_rekening, start=1):
#         print(i)
#         print("nomor rekening :", data["norek"])
#         print("saldo          :", data["saldo"])
#         print("level          :", data["level"])
#
#
# audit_rekening_baru = AuditRepository.cari_audit_dengan_norek(
#     "3001946913802745"
# )
#
# print("Jumlah audit:", len(audit_rekening_baru))
#
# for audit in audit_rekening_baru:
#     print(audit["jenis"])
#     print(audit["log"])




# nasabah = NasabahRepository.cari_nasabah_dengan_nik(
#     "1111222233334444"
# )
#
# daftar_rekening = RekeningRepository.cari_rekening_dengan_nik(
#     "1111222233334444"
# )
#
# if daftar_rekening:
#     print(
#         "jumlah rekening milik",
#         nasabah["nama"],
#         "=",
#         len(daftar_rekening)
#     )
#
#     for i, data in enumerate(daftar_rekening, start=1):
#         print(i)
#         print("nomor rekening :", data["norek"])
#         print("saldo          :", data["saldo"])
#         print("level          :", data["level"])


# audit_pembukaan = AuditRepository.cari_audit_dengan_norek(
#     "4001518075450587"
# )
#
# print("Jumlah audit:", len(audit_pembukaan))
#
# for audit in audit_pembukaan:
#     print("Kategori :", audit["kategori"])
#     print("Jenis    :", audit["jenis"])
#     print("Waktu    :", audit["waktu"])
#     print("Log      :", audit["log"])
#     print("Nama     :", audit["nama"])
#     print("NIK      :", audit["nik"])
#     print("Norek    :", audit["norek"])




# nasabah = NasabahRepository.cari_nasabah_dengan_nik(
#     "1111222233334444"
# )
#
# daftar_rekening = RekeningRepository.cari_rekening_dengan_nik(
#     "1111222233334444"
# )
#
# if daftar_rekening:
#     print(
#         "jumlah rekening milik",
#         nasabah["nama"],
#         "=",
#         len(daftar_rekening)
#     )
#
#     for i, data in enumerate(daftar_rekening, start=1):
#         print(i)
#         print("nomor rekening :", data["norek"])
#         print("saldo          :", data["saldo"])
#         print("level          :", data["level"])




# audit_pembukaan = AuditRepository.cari_audit_dengan_norek(
#     "4001518075450587"
# )
#
# print("Jumlah audit:", len(audit_pembukaan))
#
# for audit in audit_pembukaan:
#     print("Kategori :", audit["kategori"])
#     print("Jenis    :", audit["jenis"])
#     print("Waktu    :", audit["waktu"])
#     print("Log      :", audit["log"])
#     print("Nama     :", audit["nama"])
#     print("NIK      :", audit["nik"])
#     print("Norek    :", audit["norek"])





# data = RekeningRepository.cari_rekening_dengan_norek(
#     "4001518075450587"
# )
#
# print("Norek                 :", data["norek"])
# print("Level                 :", data["level"])
# print("Saldo                 :", data["saldo"])
# print("Limit tersisa         :", data["limit_sisa"])
# print("Reset                 :", data["reset"])
# print("Dapat bunga           :", data["dapat_bunga"])
# print("Waktu bayar admin     :", data["waktu_bayar_admin"])
# print("Terakhir ubah rekening:", data["terakhir_ubah_rekening"])




# NOREK = "4001518075450587"
#
# daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(NOREK)
# daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
#
# riwayat_terbaru = daftar_riwayat[0]
# audit_terbaru = daftar_audit[0]
#
# print("RIWAYAT TERBARU")
# print("Kategori :", riwayat_terbaru["kategori"])
# print("Jenis    :", riwayat_terbaru["jenis"])
# print("Waktu    :", riwayat_terbaru["waktu"])
# print("Log      :", riwayat_terbaru["log"])
#
# print()
#
# print("AUDIT TERBARU")
# print("Kategori :", audit_terbaru["kategori"])
# print("Jenis    :", audit_terbaru["jenis"])
# print("Waktu    :", audit_terbaru["waktu"])
# print("Log      :", audit_terbaru["log"])
# print("Nama     :", audit_terbaru["nama"])
# print("NIK      :", audit_terbaru["nik"])
# print("Norek    :", audit_terbaru["norek"])



audit_pembukaan = AuditRepository.cari_audit_dengan_norek(
    "4001518075450587"
)

print("Jumlah audit:", len(audit_pembukaan))

for audit in audit_pembukaan:
    print("Kategori :", audit["kategori"])
    print("Jenis    :", audit["jenis"])
    print("Waktu    :", audit["waktu"])
    print("Log      :", audit["log"])
    print("Nama     :", audit["nama"])
    print("NIK      :", audit["nik"])
    print("Norek    :", audit["norek"])