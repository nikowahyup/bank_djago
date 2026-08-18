import datetime

from bank_djago.services.nasabah_menu import NasabahMenu
from bank_djago.services.rekening.rekening_ui import RekeningUI
from bank_djago.services.scheduler import Scheduler
from penyimpanan.storage import JsonStorage
from bank_djago.utils.utility import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin


def menu():

    bank = JsonStorage.muat_bank()
    hari_ini = datetime.date(2026,9,25)
    Scheduler.jalankan(bank,hari_ini)


    while True:
        print()
        pilihan = Utilitas.pilihan_menu()

        if pilihan == "1":
            RekeningUI.buka_rekening(bank)

        elif pilihan == "2":
            nasabah = NasabahMenu.login(bank)
            NasabahMenu.menu_utama(bank,nasabah)

        elif pilihan == "3":
            JsonStorage.simpan_bank(bank)
            print("🙏 Terima Kasih Telah Mengunjungi Bank Djago!")
            break

        elif pilihan == "0":
            MenuAdmin.menu(bank)

if __name__ == "__main__":
    menu()

















