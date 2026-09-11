import datetime

from bank_djago.services.nasabah_menu import NasabahMenu
from bank_djago.services.scheduler import Scheduler
from bank_djago.utils.utility import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin
from bank_djago.services.nasabah.nasabah_ui import NasabahUI



def menu():


    Scheduler.jalankan()

    while True:
        print()
        pilihan = Utilitas.pilihan_menu()

        if pilihan == "1":
            NasabahUI.daftar_jadi_nasabah()

        elif pilihan == "2":
            NasabahMenu.login()

        elif pilihan == "3":

            print("🙏 Terima Kasih Telah Mengunjungi Bank Djago!")
            break

        elif pilihan == "0":
            MenuAdmin.menu()

if __name__ == "__main__":
    menu()




















