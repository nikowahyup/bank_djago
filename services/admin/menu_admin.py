from bank_djago.services.admin.menu_pinjaman import AdminPinjaman
from bank_djago.utils.utililty import UI
from bank_djago.services.admin.audit_ui  import AuditUI
from bank_djago.services.admin.rekap_ui  import RekapUI

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
            print("1. Kelola Rekap Bank")
            print("2. Kelola Audit")
            print("3. Kelola Pinjaman")
            print("4. Kelola Deposito")
            print("5. Keluar\n")

            pilihan = input("Pilihan Kamu: ")

            if pilihan == "1":
                RekapUI.menu_tampilkan_rekap(bank)
            elif pilihan == "2":
                AuditUI.menu_tampilkan_audit(bank)
            elif pilihan == "3":
                AdminPinjaman.menu(bank)

            elif pilihan == "5":
                break