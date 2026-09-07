from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
# from bank_djago.utils.tests.test_service.test_ambil_rekening import data_rekening
# from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
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

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


# def isi_waktu_dibuat_rekening_lama():
#     koneksi = buat_koneksi()
#
#     try:
#         cursor = koneksi.execute(
#             """
#             UPDATE rekening
#             SET waktu_dibuat = (
#                 SELECT MIN(audit.waktu)
#                 FROM audit
#                 WHERE audit.norek = rekening.norek
#                   AND audit.jenis = 'pembukaan'
#             )
#             WHERE waktu_dibuat IS NULL
#               AND EXISTS (
#                   SELECT 1
#                   FROM audit
#                   WHERE audit.norek = rekening.norek
#                     AND audit.jenis = 'pembukaan'
#               )
#             """
#         )
#
#         koneksi.commit()
#
#         print(
#             f"{cursor.rowcount} rekening lama "
#             f"berhasil mendapatkan waktu_dibuat"
#         )
#
#     except Exception:
#         koneksi.rollback()
#         raise
#
#     finally:
#         koneksi.close()
#
#
# if __name__ == "__main__":
#     isi_waktu_dibuat_rekening_lama()


# koneksi = buat_koneksi()
#
# try:
#     daftar_rekening = koneksi.execute(
#         """
#         SELECT
#             norek,
#             waktu_dibuat
#         FROM rekening
#         ORDER BY norek
#         """
#     ).fetchall()
#
#     for rekening in daftar_rekening:
#         print(
#             rekening["norek"],
#             rekening["waktu_dibuat"]
#         )
#
# finally:
#     koneksi.close()


koneksi = buat_koneksi()

try:
    tanpa_waktu = koneksi.execute(
        """
        SELECT norek
        FROM rekening
        WHERE waktu_dibuat IS NULL
        """
    ).fetchall()

    for rekening in tanpa_waktu:
        print(
            "Tidak memiliki audit pembukaan:",
            rekening["norek"]
        )

finally:
    koneksi.close()