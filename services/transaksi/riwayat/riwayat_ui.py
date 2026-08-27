from bank_djago.utils.utility import Utilitas
from .riwayat_service import RiwayatService
from bank_djago.utils.ui import UI
class RiwayatUI:


    @staticmethod
    def menu_riwayat(nasabah):
            UI.header("PILIH REKENING TERLEBIH DAHULU",UI.KUNING)
            print()
            rekening = Utilitas.pilih_rekening_riwayat(nasabah)

            if rekening is None:
             return

            while True:
                print()
                print(f"👋 Halo,{nasabah.nama}!")
                UI.header("MENU LIHAT RIWAYAT",UI.KUNING)
                print()
                print("1. Semua riwayat")
                print("2. Setor Uang saja")
                print("3. Tarik Uang saja")
                print("4. Transfer Kirim saja")
                print("5. Transfer Masuk  saja")
                print("6. Lihat Upgrade atau Downgrade saja")
                print("7. Keluar")
                print()
                pilihan = input("Masukkan pilihan Anda: ")
                try:
                    if pilihan == "1":
                        riwayat = RiwayatService.ambil_riwayat(rekening)
                        for item in riwayat:
                            print(Utilitas.format_waktu(item["waktu"]) ,"|",item["log"])

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



