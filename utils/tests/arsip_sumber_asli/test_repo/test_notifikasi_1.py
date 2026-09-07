# # import datetime
# #
# # from bank_djago.penyimpanan.storage import JsonStorage
# # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # from bank_djago.penyimpanan.repositories.notifikasi_repository import (
# #     NotifikasiRepository
# # )
# # from bank_djago.services.scheduler import Scheduler
# # from bank_djago.services.deposito.deposito_service import StatusDeposito
# # from bank_djago.utils.utility import JenisReferensiID
# #
# #
# # NIK_PENGUJIAN = "1111222233334444"
# # ID_DEPOSITO = 9
# # HARI_JATUH_TEMPO = datetime.date(2026, 9, 29)
# #
# #
# # def cari_deposito_dengan_id(nasabah, id_deposito):
# #     for deposito in nasabah.deposito:
# #         if deposito.ID == id_deposito:
# #             return deposito
# #
# #     raise ValueError(
# #         f"Deposito dengan ID {id_deposito} tidak ditemukan"
# #     )
# #
# #
# # def ambil_notifikasi_deposito(id_deposito):
# #     semua_notifikasi = (
# #         NotifikasiRepository.cari_notifikasi_nasabah(
# #             NIK_PENGUJIAN
# #         )
# #     )
# #
# #     return [
# #         data
# #         for data in semua_notifikasi
# #         if (
# #             data["jenis_referensi"]
# #             == JenisReferensiID.DEPOSITO.value
# #             and data["id_objek"] == id_deposito
# #         )
# #     ]
# #
# #
# # bank = JsonStorage.muat_bank()
# # nasabah_sebelum = NasabahLoader.muat_nasabah(
# #     NIK_PENGUJIAN
# # )
# #
# # deposito_sebelum = cari_deposito_dengan_id(
# #     nasabah_sebelum,
# #     ID_DEPOSITO
# # )
# #
# # notifikasi_sebelum = ambil_notifikasi_deposito(
# #     ID_DEPOSITO
# # )
# #
# # print("KONDISI SEBELUM JATUH TEMPO")
# # print("ID deposito       :", deposito_sebelum.ID)
# # print("Status deposito   :", deposito_sebelum.status)
# # print("Jumlah notifikasi :", len(notifikasi_sebelum))
# # print("Pesan             :", notifikasi_sebelum[0]["pesan"])
# #
# # assert deposito_sebelum.status == StatusDeposito.AKTIF
# # assert len(notifikasi_sebelum) == 1
# # assert "akan jatuh tempo" in notifikasi_sebelum[0]["pesan"].lower()
# #
# # print("✅ Reminder H-3 masih tersimpan")
# #
# #
# # # --------------------------------------------------
# # # JALANKAN SCHEDULER PADA HARI JATUH TEMPO
# # # --------------------------------------------------
# #
# # Scheduler.jalankan(
# #     bank=bank,
# #     hari_ini=HARI_JATUH_TEMPO
# # )
# #
# # nasabah_setelah = NasabahLoader.muat_nasabah(
# #     NIK_PENGUJIAN
# # )
# #
# # deposito_setelah = cari_deposito_dengan_id(
# #     nasabah_setelah,
# #     ID_DEPOSITO
# # )
# #
# # notifikasi_setelah = ambil_notifikasi_deposito(
# #     ID_DEPOSITO
# # )
# #
# # print("\nKONDISI SETELAH JATUH TEMPO")
# # print("ID deposito       :", deposito_setelah.ID)
# # print("Status deposito   :", deposito_setelah.status)
# # print("Jumlah notifikasi :", len(notifikasi_setelah))
# # print("Pesan             :", notifikasi_setelah[0]["pesan"])
# #
# # assert (
# #     deposito_setelah.status
# #     == StatusDeposito.JATUH_TEMPO
# # )
# # print("✅ Status deposito berubah menjadi jatuh tempo")
# #
# # assert len(notifikasi_setelah) == 1
# # print("✅ Notifikasi tetap tepat satu")
# #
# # assert "telah jatuh tempo" in notifikasi_setelah[0]["pesan"].lower()
# # assert "pencairan" in notifikasi_setelah[0]["pesan"].lower()
# #
# # print("✅ Reminder berhasil diganti menjadi pesan pencairan")
# #
# #
# # notifikasi_objek = [
# #     notifikasi
# #     for notifikasi in nasabah_setelah.notifikasi
# #     if (
# #         notifikasi.jenis_referensi
# #         == JenisReferensiID.DEPOSITO
# #         and notifikasi.id_objek == ID_DEPOSITO
# #     )
# # ]
# #
# # assert len(notifikasi_objek) == 1
# # assert notifikasi_objek[0].pesan == notifikasi_setelah[0]["pesan"]
# #
# # print("✅ Notifikasi terbaru berhasil dimuat dari SQLite")
# #
# #
# # # --------------------------------------------------
# # # SCHEDULER KEDUA PADA TANGGAL SAMA
# # # --------------------------------------------------
# #
# # Scheduler.jalankan(
# #     bank=bank,
# #     hari_ini=HARI_JATUH_TEMPO
# # )
# #
# # notifikasi_setelah_scheduler_kedua = (
# #     ambil_notifikasi_deposito(ID_DEPOSITO)
# # )
# #
# # assert len(notifikasi_setelah_scheduler_kedua) == 1
# # print("✅ Scheduler kedua tidak menggandakan notifikasi")
# #
# # print(
# #     "\n✅ Alur notifikasi jatuh tempo non-ARO "
# #     "bekerja sesuai rancangan"
# # )
#
#
#
# # import datetime
# #
# # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # from bank_djago.penyimpanan.repositories.notifikasi_repository import (
# #     NotifikasiRepository
# # )
# # from bank_djago.services.deposito.deposito_service import (
# #     DepositoService,
# #     StatusDeposito
# # )
# # from bank_djago.utils.utility import (
# #     JenisReferensiID,
# #     Utilitas
# # )
# #
# #
# # NIK_PENGUJIAN = "1111222233334444"
# # ID_DEPOSITO = 9
# # HARI_PENCAIRAN = datetime.date(2026, 9, 29)
# #
# #
# # def cari_deposito_dengan_id(nasabah, id_deposito):
# #     for deposito in nasabah.deposito:
# #         if deposito.ID == id_deposito:
# #             return deposito
# #
# #     raise ValueError(
# #         f"Deposito dengan ID {id_deposito} tidak ditemukan"
# #     )
# #
# #
# # def ambil_notifikasi_deposito(id_deposito):
# #     semua_notifikasi = (
# #         NotifikasiRepository.cari_notifikasi_nasabah(
# #             NIK_PENGUJIAN
# #         )
# #     )
# #
# #     return [
# #         data
# #         for data in semua_notifikasi
# #         if (
# #             data["jenis_referensi"]
# #             == JenisReferensiID.DEPOSITO.value
# #             and data["id_objek"] == id_deposito
# #         )
# #     ]
# #
# #
# # # --------------------------------------------------
# # # KONDISI SEBELUM PENCAIRAN
# # # --------------------------------------------------
# #
# # nasabah_sebelum = NasabahLoader.muat_nasabah(
# #     NIK_PENGUJIAN
# # )
# #
# # deposito_sebelum = cari_deposito_dengan_id(
# #     nasabah_sebelum,
# #     ID_DEPOSITO
# # )
# #
# # saldo_sebelum = deposito_sebelum.rekening.saldo
# # total_yang_diharapkan = deposito_sebelum.total_pencairan
# #
# # notifikasi_sebelum = ambil_notifikasi_deposito(
# #     ID_DEPOSITO
# # )
# #
# # print("KONDISI SEBELUM PENCAIRAN")
# # print("ID deposito       :", deposito_sebelum.ID)
# # print("Status deposito   :", deposito_sebelum.status)
# # print(
# #     "Saldo rekening    :",
# #     f"Rp{Utilitas.format_rupiah(saldo_sebelum)}"
# # )
# # print(
# #     "Total pencairan   :",
# #     f"Rp{Utilitas.format_rupiah(total_yang_diharapkan)}"
# # )
# # print("Jumlah notifikasi :", len(notifikasi_sebelum))
# #
# # assert (
# #     deposito_sebelum.status
# #     == StatusDeposito.JATUH_TEMPO
# # )
# # assert len(notifikasi_sebelum) == 1
# #
# # print("✅ Deposito siap dicairkan")
# # print("✅ Notifikasi jatuh tempo masih tersimpan")
# #
# #
# # # --------------------------------------------------
# # # LAKUKAN PENCAIRAN
# # # --------------------------------------------------
# #
# # hasil_pencairan = DepositoService.cairkan_deposito(
# #     deposito=deposito_sebelum,
# #     hari_ini=HARI_PENCAIRAN
# # )
# #
# # assert hasil_pencairan == total_yang_diharapkan
# # print("\n✅ Service mengembalikan nominal pencairan yang benar")
# #
# #
# # # --------------------------------------------------
# # # CEK STATE OBJEK SETELAH COMMIT
# # # --------------------------------------------------
# #
# # notifikasi_memori = [
# #     notifikasi
# #     for notifikasi in nasabah_sebelum.notifikasi
# #     if (
# #         notifikasi.jenis_referensi
# #         == JenisReferensiID.DEPOSITO
# #         and notifikasi.id_objek == ID_DEPOSITO
# #     )
# # ]
# #
# # assert (
# #     deposito_sebelum.status
# #     == StatusDeposito.DICAIRKAN
# # )
# # print("✅ Status objek deposito berubah menjadi dicairkan")
# #
# # assert len(notifikasi_memori) == 0
# # print("✅ Notifikasi hilang dari list memori")
# #
# #
# # # --------------------------------------------------
# # # MUAT ULANG DARI SQLITE
# # # --------------------------------------------------
# #
# # nasabah_setelah = NasabahLoader.muat_nasabah(
# #     NIK_PENGUJIAN
# # )
# #
# # deposito_setelah = cari_deposito_dengan_id(
# #     nasabah_setelah,
# #     ID_DEPOSITO
# # )
# #
# # saldo_setelah = deposito_setelah.rekening.saldo
# #
# # notifikasi_setelah = ambil_notifikasi_deposito(
# #     ID_DEPOSITO
# # )
# #
# # saldo_yang_diharapkan = (
# #     saldo_sebelum + total_yang_diharapkan
# # )
# #
# # print("\nKONDISI SETELAH PENCAIRAN")
# # print("ID deposito       :", deposito_setelah.ID)
# # print("Status deposito   :", deposito_setelah.status)
# # print(
# #     "Saldo rekening    :",
# #     f"Rp{Utilitas.format_rupiah(saldo_setelah)}"
# # )
# # print("Jumlah notifikasi :", len(notifikasi_setelah))
# #
# # assert (
# #     deposito_setelah.status
# #     == StatusDeposito.DICAIRKAN
# # )
# # print("✅ Status dicairkan tersimpan di SQLite")
# #
# # assert saldo_setelah == saldo_yang_diharapkan
# # print("✅ Saldo rekening bertambah sesuai total pencairan")
# #
# # assert len(notifikasi_setelah) == 0
# # print("✅ Notifikasi deposito terhapus dari SQLite")
# #
# #
# # # --------------------------------------------------
# # # CEK LOADER NOTIFIKASI
# # # --------------------------------------------------
# #
# # notifikasi_objek_setelah = [
# #     notifikasi
# #     for notifikasi in nasabah_setelah.notifikasi
# #     if (
# #         notifikasi.jenis_referensi
# #         == JenisReferensiID.DEPOSITO
# #         and notifikasi.id_objek == ID_DEPOSITO
# #     )
# # ]
# #
# # assert len(notifikasi_objek_setelah) == 0
# # print("✅ Loader tidak memuat notifikasi yang sudah dihapus")
# #
# # print(
# #     "\n✅ Pencairan dan penghapusan notifikasi "
# #     "non-ARO bekerja sesuai rancangan"
# # )
#
#
#
# import datetime
#
# from bank_djago.penyimpanan.storage import JsonStorage
# from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# from bank_djago.penyimpanan.repositories.notifikasi_repository import (
#     NotifikasiRepository
# )
# from bank_djago.services.scheduler import Scheduler
# from bank_djago.utils.utility import JenisReferensiID
#
#
# NIK_PENGUJIAN = "1111222233334444"
#
# ID_ARO_POKOK = 6
# ID_ARO_POKOK_BUNGA = 7
#
# HARI_JATUH_TEMPO = datetime.date(2027, 3, 28)
# HARI_SETELAHNYA = datetime.date(2027, 3, 29)
#
#
# def cari_deposito_dengan_id(nasabah, id_deposito):
#     for deposito in nasabah.deposito:
#         if deposito.ID == id_deposito:
#             return deposito
#
#     raise ValueError(
#         f"Deposito dengan ID {id_deposito} tidak ditemukan"
#     )
#
#
# def ambil_notifikasi_deposito(id_deposito):
#     semua_notifikasi = (
#         NotifikasiRepository.cari_notifikasi_nasabah(
#             NIK_PENGUJIAN
#         )
#     )
#
#     return [
#         data
#         for data in semua_notifikasi
#         if (
#             data["jenis_referensi"]
#             == JenisReferensiID.DEPOSITO.value
#             and data["id_objek"] == id_deposito
#         )
#     ]
#
#
# bank = JsonStorage.muat_bank()
#
# nasabah_sebelum = NasabahLoader.muat_nasabah(
#     NIK_PENGUJIAN
# )
#
# aro_pokok_sebelum = cari_deposito_dengan_id(
#     nasabah_sebelum,
#     ID_ARO_POKOK
# )
#
# aro_pokok_bunga_sebelum = cari_deposito_dengan_id(
#     nasabah_sebelum,
#     ID_ARO_POKOK_BUNGA
# )
#
# notifikasi_pokok_sebelum = ambil_notifikasi_deposito(
#     ID_ARO_POKOK
# )
#
# notifikasi_pokok_bunga_sebelum = (
#     ambil_notifikasi_deposito(
#         ID_ARO_POKOK_BUNGA
#     )
# )
#
#
# # --------------------------------------------------
# # KONDISI SEBELUM SCHEDULER
# # --------------------------------------------------
#
# print("KONDISI SEBELUM SCHEDULER ARO")
#
# print("\nARO POKOK")
# print("ID                   :", aro_pokok_sebelum.ID)
# print("Jatuh tempo          :", aro_pokok_sebelum.jatuh_tempo)
# print("Proses ARO           :", aro_pokok_sebelum.proses_aro)
# print(
#     "Jumlah notifikasi   :",
#     len(notifikasi_pokok_sebelum)
# )
#
# print("\nARO POKOK + BUNGA")
# print("ID                   :", aro_pokok_bunga_sebelum.ID)
# print(
#     "Jatuh tempo          :",
#     aro_pokok_bunga_sebelum.jatuh_tempo
# )
# print(
#     "Proses ARO           :",
#     aro_pokok_bunga_sebelum.proses_aro
# )
# print(
#     "Jumlah notifikasi   :",
#     len(notifikasi_pokok_bunga_sebelum)
# )
#
# assert (
#     aro_pokok_sebelum.jatuh_tempo
#     == HARI_JATUH_TEMPO
# )
#
# assert (
#     aro_pokok_bunga_sebelum.jatuh_tempo
#     == HARI_JATUH_TEMPO
# )
#
# assert len(notifikasi_pokok_sebelum) == 0
# assert len(notifikasi_pokok_bunga_sebelum) == 0
#
# print("\n✅ Kedua deposito ARO siap diuji")
#
#
# # --------------------------------------------------
# # JALANKAN SCHEDULER PADA HARI JATUH TEMPO
# # --------------------------------------------------
#
# Scheduler.jalankan(
#     bank=bank,
#     hari_ini=HARI_JATUH_TEMPO
# )
#
# nasabah_setelah_aro = NasabahLoader.muat_nasabah(
#     NIK_PENGUJIAN
# )
#
# aro_pokok_setelah = cari_deposito_dengan_id(
#     nasabah_setelah_aro,
#     ID_ARO_POKOK
# )
#
# aro_pokok_bunga_setelah = cari_deposito_dengan_id(
#     nasabah_setelah_aro,
#     ID_ARO_POKOK_BUNGA
# )
#
# notifikasi_pokok = ambil_notifikasi_deposito(
#     ID_ARO_POKOK
# )
#
# notifikasi_pokok_bunga = ambil_notifikasi_deposito(
#     ID_ARO_POKOK_BUNGA
# )
#
# print("\nSETELAH SCHEDULER HARI JATUH TEMPO")
#
# print("\nARO POKOK")
# print(
#     "Jatuh tempo baru    :",
#     aro_pokok_setelah.jatuh_tempo
# )
# print(
#     "Proses ARO           :",
#     aro_pokok_setelah.proses_aro
# )
# print(
#     "Jumlah notifikasi   :",
#     len(notifikasi_pokok)
# )
# print("Pesan               :", notifikasi_pokok[0]["pesan"])
#
# print("\nARO POKOK + BUNGA")
# print(
#     "Jatuh tempo baru    :",
#     aro_pokok_bunga_setelah.jatuh_tempo
# )
# print(
#     "Proses ARO           :",
#     aro_pokok_bunga_setelah.proses_aro
# )
# print(
#     "Jumlah notifikasi   :",
#     len(notifikasi_pokok_bunga)
# )
# print(
#     "Pesan               :",
#     notifikasi_pokok_bunga[0]["pesan"]
# )
#
# assert (
#     aro_pokok_setelah.proses_aro
#     == HARI_JATUH_TEMPO
# )
#
# assert (
#     aro_pokok_bunga_setelah.proses_aro
#     == HARI_JATUH_TEMPO
# )
#
# print("✅ Tanggal proses ARO tersimpan")
#
# assert len(notifikasi_pokok) == 1
# assert len(notifikasi_pokok_bunga) == 1
#
# print("✅ Masing-masing ARO menghasilkan satu notifikasi")
#
# assert (
#     "berhasil diperpanjang"
#     in notifikasi_pokok[0]["pesan"].lower()
# )
#
# assert (
#     "berhasil diperpanjang"
#     in notifikasi_pokok_bunga[0]["pesan"].lower()
# )
#
# print("✅ Pesan hasil perpanjangan sesuai")
#
#
# # --------------------------------------------------
# # CEK LOADER NOTIFIKASI
# # --------------------------------------------------
#
# notifikasi_objek_pokok = [
#     notifikasi
#     for notifikasi in nasabah_setelah_aro.notifikasi
#     if (
#         notifikasi.jenis_referensi
#         == JenisReferensiID.DEPOSITO
#         and notifikasi.id_objek == ID_ARO_POKOK
#     )
# ]
#
# notifikasi_objek_pokok_bunga = [
#     notifikasi
#     for notifikasi in nasabah_setelah_aro.notifikasi
#     if (
#         notifikasi.jenis_referensi
#         == JenisReferensiID.DEPOSITO
#         and notifikasi.id_objek == ID_ARO_POKOK_BUNGA
#     )
# ]
#
# assert len(notifikasi_objek_pokok) == 1
# assert len(notifikasi_objek_pokok_bunga) == 1
#
# print("✅ Loader memuat kedua notifikasi ARO")
#
#
# # --------------------------------------------------
# # JALANKAN LAGI PADA HARI YANG SAMA
# # --------------------------------------------------
#
# Scheduler.jalankan(
#     bank=bank,
#     hari_ini=HARI_JATUH_TEMPO
# )
#
# notifikasi_pokok_kedua = ambil_notifikasi_deposito(
#     ID_ARO_POKOK
# )
#
# notifikasi_pokok_bunga_kedua = (
#     ambil_notifikasi_deposito(
#         ID_ARO_POKOK_BUNGA
#     )
# )
#
# assert len(notifikasi_pokok_kedua) == 1
# assert len(notifikasi_pokok_bunga_kedua) == 1
#
# print("✅ Scheduler kedua tidak menggandakan notifikasi")
#
#
# # --------------------------------------------------
# # JALANKAN SCHEDULER PADA HARI BERIKUTNYA
# # --------------------------------------------------
#
# Scheduler.jalankan(
#     bank=bank,
#     hari_ini=HARI_SETELAHNYA
# )
#
# notifikasi_pokok_hari_berikutnya = (
#     ambil_notifikasi_deposito(
#         ID_ARO_POKOK
#     )
# )
#
# notifikasi_pokok_bunga_hari_berikutnya = (
#     ambil_notifikasi_deposito(
#         ID_ARO_POKOK_BUNGA
#     )
# )
#
# print("\nSETELAH SCHEDULER HARI BERIKUTNYA")
# print(
#     "Notifikasi ARO pokok         :",
#     len(notifikasi_pokok_hari_berikutnya)
# )
# print(
#     "Notifikasi ARO pokok+bunga   :",
#     len(notifikasi_pokok_bunga_hari_berikutnya)
# )
#
# assert len(notifikasi_pokok_hari_berikutnya) == 0
# assert len(notifikasi_pokok_bunga_hari_berikutnya) == 0
#
# print("✅ Notifikasi ARO dihapus setelah hari pemrosesan")
#
#
# # --------------------------------------------------
# # MUAT ULANG NASABAH
# # --------------------------------------------------
#
# nasabah_hari_berikutnya = NasabahLoader.muat_nasabah(
#     NIK_PENGUJIAN
# )
#
# notifikasi_aro_yang_dimuat = [
#     notifikasi
#     for notifikasi in nasabah_hari_berikutnya.notifikasi
#     if (
#         notifikasi.jenis_referensi
#         == JenisReferensiID.DEPOSITO
#         and notifikasi.id_objek
#         in (ID_ARO_POKOK, ID_ARO_POKOK_BUNGA)
#     )
# ]
#
# assert len(notifikasi_aro_yang_dimuat) == 0
#
# print("✅ Loader tidak memuat notifikasi ARO yang dihapus")
#
# print(
#     "\n✅ Siklus notifikasi ARO bekerja "
#     "sesuai rancangan"
# )