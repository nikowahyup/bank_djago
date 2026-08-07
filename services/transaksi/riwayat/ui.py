from bank_djago.utils.utililty import Utilitas
from .service import RiwayatService
from bank_djago.utils.ui import UI
class RiwayatUI:


    @staticmethod
    def menu_riwayat(rekening):
            while True:
                print()
                UI.header("MENU LIHAT RIWAYAT")
                print()
                print("1. Semua transaksi".title())
                print("2. Setor tunai saja".title())
                print("3. Tarik Tunai saja".title())
                print("4. Transfer Kirim saja".title())
                print("5. Transfer Masuk  saja".title())
                print("6. Lihat Upgrade atau Downgrade saja".title())
                print("7. Keluar".title())

                pilihan = input("Masukkan pilihan Anda: ")

                if pilihan == "1":
                   riwayat = RiwayatService.ambil_riwayat(rekening)
                   for item in riwayat:
                       print(Utilitas.format_waktu(item["waktu"]),'|',item["log"])
                elif pilihan == "2":
                    riwayat = RiwayatService.ambil_riwayat(rekening,"setor tunai".title())
                    for item in riwayat:
                        print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])
                elif pilihan == "3":
                    riwayat = RiwayatService.ambil_riwayat(rekening,"tarik tunai".title())
                    for item in riwayat:
                        print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])
                elif pilihan == "4":
                    riwayat = RiwayatService.ambil_riwayat(rekening,"transfer saldo".title())
                    for item in riwayat:
                        print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])
                elif pilihan == "5":
                    riwayat = RiwayatService.ambil_riwayat(rekening,"terima saldo".title())
                    for item in riwayat:
                        print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])
                elif pilihan == "6":
                    riwayat = RiwayatService.ambil_riwayat(rekening,"perubahan".title())
                    for item in riwayat:
                        print(Utilitas.format_waktu(item["waktu"]), '|', item["log"])
                elif pilihan == "7":
                    break
                elif pilihan == "8":
                    pass
                elif pilihan == "9":
                    pass
