from bank_djago.utils.utility import Utilitas
from .riwayat_service import RiwayatService
from bank_djago.utils.ui import UI
class RiwayatUI:


    @staticmethod
    def menu_riwayat(rekening):
            while True:
                print()
                print(f"👋 Halo,{rekening.pemilik.nama}!")
                UI.header("MENU LIHAT RIWAYAT",UI.KUNING)
                print()
                print("1. Semua transaksi".title())
                print("2. Setor Uang saja".title())
                print("3. Tarik Uang saja".title())
                print("4. Transfer Kirim saja".title())
                print("5. Transfer Masuk  saja".title())
                print("6. Lihat Upgrade atau Downgrade saja".title())
                print("7. Keluar".title())
                print()
                pilihan = input("Masukkan pilihan Anda: ")
                try:
                    if pilihan == "1":
                        riwayat = RiwayatService.ambil_riwayat(rekening)
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])

                    elif pilihan == "2":
                        riwayat = RiwayatService.ambil_riwayat(rekening,"setor uang")
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])

                    elif pilihan == "3":
                        riwayat = RiwayatService.ambil_riwayat(rekening,"tarik uang")
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])

                    elif pilihan == "4":
                        riwayat = RiwayatService.ambil_riwayat(rekening,"transfer saldo")
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])

                    elif pilihan == "5":
                        riwayat = RiwayatService.ambil_riwayat(rekening,"terima saldo")
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])

                    elif pilihan == "6":
                        riwayat = RiwayatService.ambil_riwayat(rekening,"perubahan")
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])

                    elif pilihan == "7":
                        break
                except ValueError as e:
                    UI.gagal(str(e))



