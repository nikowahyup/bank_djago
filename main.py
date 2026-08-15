import datetime

from bank_djago.services.NasabahMenu import NasabahMenu
from bank_djago.services.bank_service import BankService
from bank_djago.services.rekening.rekeningUI import RekeningUI
from bank_djago.services.scheduler import Scheduler
from penyimpanan.storage import JsonStorage
from bank_djago.utils.utililty import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin


def menu():

    bank = JsonStorage.muat_bank()
    hari_ini = datetime.date(2026,9,15)
    Scheduler.jalankan(bank,hari_ini)
    # Scheduler.jalankan(bank)
    # bank.proses_harian()
    # error = BankService.cek_integritas_rekening(bank)
    #
    # if not error:
    #     print("✅ Integritas rekening valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #     for item in error:
    #         print("-", item)
    # error = BankService.cek_integritas_deposito(bank)
    #
    # if not error:
    #     print("✅ Integritas deposito valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #
    #     for item in error:
    #         print("-", item)
    #
    # error = BankService.cek_integritas_pinjaman(bank)
    #
    # if not error:
    #     print("✅ Integritas pinjaman valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #
    #     for item in error:
    #         print("-", item)
    #
    error = BankService.cek_integritas_notifikasi(bank)

    if not error:
        print("✅ Integritas notifikasi valid.")
    else:
        print("❌ Ditemukan masalah:")
        for item in error:
            print("-", item)

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
