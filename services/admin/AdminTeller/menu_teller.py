from bank_djago.services.admin.AdminTeller.teller_transaksi import TellerUI
from bank_djago.services.deposito.ui import DepositoUI
from bank_djago.utils.ui import UI
class MenuTeller:

    @staticmethod
    def menu(bank):
        while True:
            print()
            UI.header("APA YANG INGIN ANDA LAKUKAN?")
            print()
            print("1. Lihat Menu Transaksi")
            print("2. Lihat Menu Deposito")
            print("3. Keluar\n")

            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                TellerUI.menu_transaksi(bank)
            elif pilihan == "2":
                DepositoUI.menu(bank)
            elif pilihan == "3":
                break