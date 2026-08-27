import datetime

from bank_djago.services.nasabah_menu import NasabahMenu
from bank_djago.services.scheduler import Scheduler
from penyimpanan.storage import JsonStorage
from bank_djago.utils.utility import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin
from bank_djago.services.nasabah.nasabah_ui import NasabahUI



def menu():

    bank = JsonStorage.muat_bank()
    hari_ini = datetime.date(2026,9,22)
    Scheduler.jalankan(bank,hari_ini)

    while True:
        print()
        pilihan = Utilitas.pilihan_menu()

        if pilihan == "1":
            NasabahUI.daftar_jadi_nasabah()

        elif pilihan == "2":
            NasabahMenu.login()
            # NasabahMenu.menu_utama(nasabah)

        elif pilihan == "3":
            JsonStorage.simpan_bank(bank)
            print("🙏 Terima Kasih Telah Mengunjungi Bank Djago!")
            break

        elif pilihan == "0":
            MenuAdmin.menu(bank)

if __name__ == "__main__":
    menu()




















