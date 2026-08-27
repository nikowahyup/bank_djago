from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository

# pengirim = RekeningRepository.cari_rekening_dengan_nik("1111222233334444")
# penerima = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
#
#
# for data in pengirim:
#     print("kondisi pengirim sebelum")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])
#
#
# print()
# for data in penerima:
#
#     print("kondisi penerima sebelum")
#     print("saldo :",data["saldo"])
#     print("norek :",data["norek"])
#
#
#
#
#
# pengirim = RekeningRepository.cari_rekening_dengan_nik("1111222233334444")
# penerima = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
#
#
# for data in pengirim:
#     print("kondisi pengirim seseudah")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#
#
# print()
# for data in penerima:
#
#     print("kondisi penerima sesudah")
#     print("saldo :",data["saldo"])



# pengirim = RekeningRepository.cari_rekening_dengan_nik("1111222233334444")
# penerima = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
#
#
#
# for data in pengirim:
#     print("kondisi sebelum pengirim")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])
#
#
# print()
#
# for data in penerima:
#     print("kondisi sebelum penerima")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])





# pengirim = RekeningRepository.cari_rekening_dengan_nik("1111222233334444")
# penerima = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
#
# riwayat_pengirim = RiwayatRepository.cari_seluruh_riwayat("2001569043650499")
# riwayat_penerima = RiwayatRepository.cari_seluruh_riwayat("2001934876207884")
#
# audit_pengirim = AuditRepository.cari_audit_dengan_norek("2001569043650499")
# audit_penerima = AuditRepository.cari_audit_dengan_norek("2001934876207884")
#
# for data in pengirim:
#     print("kondisi setelah pengirim")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])
#
#
# print()
#
# for data in penerima:
#     print("kondisi setelah penerima")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])
#
#
# terbaru_pengirim = riwayat_pengirim[0]
# terbaru_penerima = riwayat_penerima[0]
#
# print(terbaru_pengirim["jenis"])
# print(terbaru_pengirim["log"])
#
# print(terbaru_penerima["jenis"])
# print(terbaru_penerima["log"])
#
#
#
# data_pemeriksaan = (
#     ("AUDIT PENGIRIM", "2001569043650499"),
#     ("AUDIT PENERIMA", "2001934876207884"),
# )
#
# for judul, norek in data_pemeriksaan:
#     daftar_audit = AuditRepository.cari_audit_dengan_norek(norek)
#
#     print()
#     print(judul)
#
#     if not daftar_audit:
#         print("Audit tidak ditemukan")
#         continue
#
#     audit_terbaru = daftar_audit[0]
#
#     print("Jenis :", audit_terbaru["jenis"])
#     print("Waktu :", audit_terbaru["waktu"])
#     print("Log   :", audit_terbaru["log"])
#     print("Nama  :", audit_terbaru["nama"])
#     print("NIK   :", audit_terbaru["nik"])
#     print("Norek :", audit_terbaru["norek"])



# pengirim = RekeningRepository.cari_rekening_dengan_nik("1111222233334444")
#
# for data in pengirim:
#     print("kondisi setelah pengujian gagal")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])





# pengirim = RekeningRepository.cari_rekening_dengan_nik("1111222233334444")
#
# for data in pengirim:
#     print("kondisi setelah pengujian gagal")
#     print("saldo :",data["saldo"])
#     print("limit :",data["limit_sisa"])
#     print("norek :",data["norek"])


# import datetime
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
# from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
# from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
# from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
# from bank_djago.services.transaksi.transaksi_service import TransaksiService
#
#
# NOREK_PENGIRIM = "2001569043650499"
# NOREK_PENERIMA = "2001934876207884"
#
# LIMIT_PENGUJIAN = 5_000_000
# NOMINAL_TRANSFER = 10_000_000
#
#
# def uji_transfer_melebihi_limit():
#     koneksi = buat_koneksi()
#
#     try:
#         # Simpan limit asli agar dapat dikembalikan setelah pengujian.
#         data_asli = RekeningRepository.cari_rekening_dengan_norek(
#             NOREK_PENGIRIM,
#             koneksi
#         )
#
#         if data_asli is None:
#             raise AssertionError("Rekening pengirim tidak ditemukan")
#
#         limit_asli = data_asli["limit_sisa"]
#         reset_asli = data_asli["reset"]
#
#         # Reset harus hari ini agar LimitService tidak mengisi ulang limit.
#         jumlah_baris = RekeningRepository.perbarui_limit(
#             LIMIT_PENGUJIAN,
#             datetime.date.today(),
#             NOREK_PENGIRIM,
#             koneksi
#         )
#
#         assert jumlah_baris == 1
#         koneksi.commit()
#
#     finally:
#         koneksi.close()
#
#     try:
#         # Muat ulang objek setelah limit SQLite diubah.
#         koneksi = buat_koneksi()
#
#         try:
#             pengirim = RekeningLoader.muat_rekening(
#                 NOREK_PENGIRIM,
#                 koneksi
#             )
#             penerima = RekeningLoader.muat_rekening(
#                 NOREK_PENERIMA,
#                 koneksi
#             )
#         finally:
#             koneksi.close()
#
#         assert pengirim is not None
#         assert penerima is not None
#
#         saldo_pengirim_sebelum = pengirim.saldo
#         saldo_penerima_sebelum = penerima.saldo
#         limit_sebelum = pengirim.limit_sisa
#
#         riwayat_pengirim_sebelum = len(
#             RiwayatRepository.cari_seluruh_riwayat(NOREK_PENGIRIM)
#         )
#         riwayat_penerima_sebelum = len(
#             RiwayatRepository.cari_seluruh_riwayat(NOREK_PENERIMA)
#         )
#         audit_pengirim_sebelum = len(
#             AuditRepository.cari_audit_dengan_norek(NOREK_PENGIRIM)
#         )
#         audit_penerima_sebelum = len(
#             AuditRepository.cari_audit_dengan_norek(NOREK_PENERIMA)
#         )
#
#         print("SEBELUM PENGUJIAN")
#         print("Saldo pengirim :", saldo_pengirim_sebelum)
#         print("Saldo penerima :", saldo_penerima_sebelum)
#         print("Limit pengirim :", limit_sebelum)
#
#         try:
#             TransaksiService.transfer(
#                 pengirim,
#                 NOREK_PENERIMA,
#                 NOMINAL_TRANSFER
#             )
#
#             raise AssertionError(
#                 "Transfer seharusnya ditolak karena melebihi limit"
#             )
#
#         except ValueError as error:
#             print()
#             print("✅ Transfer berhasil ditolak")
#             print("Penyebab:", error)
#
#             assert "limit" in str(error).lower()
#
#         # Ambil ulang data dari SQLite, jangan hanya memeriksa objek lama.
#         koneksi = buat_koneksi()
#
#         try:
#             pengirim_setelah = RekeningLoader.muat_rekening(
#                 NOREK_PENGIRIM,
#                 koneksi
#             )
#             penerima_setelah = RekeningLoader.muat_rekening(
#                 NOREK_PENERIMA,
#                 koneksi
#             )
#         finally:
#             koneksi.close()
#
#         riwayat_pengirim_setelah = len(
#             RiwayatRepository.cari_seluruh_riwayat(NOREK_PENGIRIM)
#         )
#         riwayat_penerima_setelah = len(
#             RiwayatRepository.cari_seluruh_riwayat(NOREK_PENERIMA)
#         )
#         audit_pengirim_setelah = len(
#             AuditRepository.cari_audit_dengan_norek(NOREK_PENGIRIM)
#         )
#         audit_penerima_setelah = len(
#             AuditRepository.cari_audit_dengan_norek(NOREK_PENERIMA)
#         )
#
#         assert pengirim_setelah.saldo == saldo_pengirim_sebelum
#         assert penerima_setelah.saldo == saldo_penerima_sebelum
#         assert pengirim_setelah.limit_sisa == LIMIT_PENGUJIAN
#
#         assert (
#             riwayat_pengirim_setelah
#             == riwayat_pengirim_sebelum
#         )
#         assert (
#             riwayat_penerima_setelah
#             == riwayat_penerima_sebelum
#         )
#         assert audit_pengirim_setelah == audit_pengirim_sebelum
#         assert audit_penerima_setelah == audit_penerima_sebelum
#
#         print()
#         print("SETELAH PENGUJIAN")
#         print("Saldo pengirim :", pengirim_setelah.saldo)
#         print("Saldo penerima :", penerima_setelah.saldo)
#         print("Limit pengirim :", pengirim_setelah.limit_sisa)
#         print("✅ Saldo, limit, riwayat, dan audit tidak berubah")
#
#     finally:
#         # Kembalikan kondisi asli rekening pengirim.
#         koneksi = buat_koneksi()
#
#         try:
#             reset_asli_date = datetime.date.fromisoformat(reset_asli)
#
#             RekeningRepository.perbarui_limit(
#                 limit_asli,
#                 reset_asli_date,
#                 NOREK_PENGIRIM,
#                 koneksi
#             )
#             koneksi.commit()
#             print("✅ Limit pengirim berhasil dikembalikan")
#         except Exception:
#             koneksi.rollback()
#             raise
#         finally:
#             koneksi.close()
#
#
# if __name__ == "__main__":
#     uji_transfer_melebihi_limit()





import datetime

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.repositories.riwayat_repository import (
    RiwayatRepository
)
from bank_djago.services.transaksi.transaksi_service import TransaksiService


NOREK_PENGIRIM = "2001569043650499"
NOREK_PENERIMA = "2001934876207884"
NOMINAL_TRANSFER = 10_000_000


def muat_rekening(norek):
    koneksi = buat_koneksi()

    try:
        return RekeningLoader.muat_rekening(norek, koneksi)
    finally:
        koneksi.close()


def uji_reset_limit_saat_transfer():
    hari_ini = datetime.date.today()
    kemarin = hari_ini - datetime.timedelta(days=1)

    # Persiapkan kondisi limit habis dan reset sudah kedaluwarsa.
    koneksi = buat_koneksi()

    try:
        jumlah_baris = RekeningRepository.perbarui_limit(
            limit_baru=0,
            reset_baru=kemarin,
            norek=NOREK_PENGIRIM,
            koneksi=koneksi
        )

        assert jumlah_baris == 1
        koneksi.commit()

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()

    # Objek harus dimuat ulang setelah database diubah.
    pengirim = muat_rekening(NOREK_PENGIRIM)
    penerima = muat_rekening(NOREK_PENERIMA)

    assert pengirim is not None
    assert penerima is not None

    saldo_pengirim_sebelum = pengirim.saldo
    saldo_penerima_sebelum = penerima.saldo
    limit_sebelum = pengirim.limit_sisa
    reset_sebelum = pengirim.reset

    jumlah_reset_sebelum = len(
        RiwayatRepository.cari_riwayat_berdasarkan_jenis(
            NOREK_PENGIRIM,
            "reset limit"
        )
    )

    print("SEBELUM TRANSFER")
    print("Saldo pengirim :", saldo_pengirim_sebelum)
    print("Saldo penerima :", saldo_penerima_sebelum)
    print("Limit pengirim :", limit_sebelum)
    print("Tanggal reset  :", reset_sebelum)

    hasil = TransaksiService.transfer(
        pengirim,
        NOREK_PENERIMA,
        NOMINAL_TRANSFER
    )

    assert hasil is True

    # Muat ulang untuk memastikan nilai yang diperiksa berasal dari SQLite.
    pengirim_setelah = muat_rekening(NOREK_PENGIRIM)
    penerima_setelah = muat_rekening(NOREK_PENERIMA)

    jumlah_reset_setelah = len(
        RiwayatRepository.cari_riwayat_berdasarkan_jenis(
            NOREK_PENGIRIM,
            "reset limit"
        )
    )

    print()
    print("SETELAH TRANSFER")
    print("Saldo pengirim :", pengirim_setelah.saldo)
    print("Saldo penerima :", penerima_setelah.saldo)
    print("Limit pengirim :", pengirim_setelah.limit_sisa)
    print("Tanggal reset  :", pengirim_setelah.reset)

    # Gold memiliki limit harian Rp200 juta.
    limit_yang_diharapkan = (
        pengirim_setelah.limit_harian - NOMINAL_TRANSFER
    )

    assert pengirim_setelah.saldo == (
        saldo_pengirim_sebelum - NOMINAL_TRANSFER
    )
    assert penerima_setelah.saldo == (
        saldo_penerima_sebelum + NOMINAL_TRANSFER
    )
    assert pengirim_setelah.limit_sisa == limit_yang_diharapkan
    assert pengirim_setelah.reset == hari_ini
    assert jumlah_reset_setelah == jumlah_reset_sebelum + 1

    print()
    print("✅ Transfer berhasil setelah limit direset")
    print("✅ Limit direset lalu dikurangi nominal transfer")
    print("✅ Tanggal reset berubah menjadi hari ini")
    print("✅ Riwayat reset limit hanya bertambah satu")


if __name__ == "__main__":
    uji_reset_limit_saat_transfer()