from bank_djago.services.NasabahMenu import NasabahMenu
from bank_djago.services.rekening.rekeningUI import RekeningUI
from bank_djago.utils.debug import Debug
from penyimpanan.storage import JsonStorage
from bank_djago.utils.utililty import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin


def menu():

    bank = JsonStorage.muat_bank()
    Debug.cek_jatuh_tempo(bank,12)
    Debug.cek_jatuh_tempo_pinjaman(bank,1)
    bank.proses_harian()

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

if __name__ == '__main__':
    menu()
