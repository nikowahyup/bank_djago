from .admin_cs import AdminCs
from bank_djago.utils.utililty import UI
from bank_djago.utils.AuditUI import AuditUI
from bank_djago.utils.rekapUI import RekapUI

class MenuAdmin:

    @staticmethod
    def menu(bank):
        print()
        UI.peringatan("""PERHATIAN! Menu ini khusus Admin. 
Nasabah tidak diperbolehkan masuk!
Masukkan sembarang simbol untuk keluar""")

        password = input("Masukkan password: ")
        if not bank.verifikasi_admin(password):
            return

        while True:
            UI.header("MENU ADMIN")
            print()
            print("1. Menu Rekap Bank")
            print("2. Menu Audit")
            print("3. Customer Service")
            print("4. Keluar\n")

            pilihan = input("Pilihan Kamu: ")

            if pilihan == "1":
                RekapUI.menu_tampilkan_rekap(bank)
            elif pilihan == "2":
                AuditUI.menu_tampilkan_audit(bank)
            elif pilihan == "3":
                AdminCs.menu(bank)
            elif pilihan == "4":
                break