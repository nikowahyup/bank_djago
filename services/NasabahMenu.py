from bank_djago.services.transaksi.transaksiUI import TransaksiUI
from bank_djago.services.admin.rekeningUI import RekeningUI
from bank_djago.services.deposito.ui import DepositoUI
from bank_djago.services.layanan_nasabah import LayananNasabah
from bank_djago.services.transaksi.riwayat.ui import RiwayatUI
from bank_djago.utils.ui import UI



class NasabahMenu:

    @staticmethod
    def login(bank):
        while True:
            print()
            print("LOGIN")
            nik = input("Masukkan NIK Anda: ")
            nasabah = bank.cari_nasabah(nik)

            if not nasabah:
                UI.gagal("NIK tidak terfdatar. Coba Lagi")
                continue

            norek = input("Masukkan nomor rekening Anda: ")
            pin   = input("Masukkan PIN rekening Anda: ")

            try:
                rekening = bank.autentikasi_rekening(norek,pin)
            except ValueError as e:
                UI.gagal(str(e))
                continue

            if rekening not in nasabah.rekening:
                UI.gagal("Nomor rekening ini tidak terdaftar di akun Anda")
                continue

            return nasabah,rekening


    @staticmethod
    def menu_utama(bank,nasabah,rekening):

        while True:
            UI.header("SELAMAT DATANG DI BANK DJAGO",UI.BIRU)
            print()
            print(f"👋Halo,{nasabah.nama}!\n")
            print("1. Menu layanan Rekening")
            print("2. Menu Transaksi")
            print("3. Menu Deposito")
            print("4. Menu Profil")
            print("5. Menu Lihat Riwayat")
            print("6. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                RekeningUI.menu(bank, rekening)

            elif pilihan == "2":
                TransaksiUI.menu_transaksi(bank, rekening)

            elif pilihan == "3":
                DepositoUI.menu_deposito(bank, nasabah, rekening)

            elif pilihan == "4":
                LayananNasabah.menu_profil(nasabah,rekening)

            elif pilihan == "5":
                RiwayatUI.menu_riwayat(rekening)

            elif pilihan == "6":
                break














