from bank_djago.services.deposito.deposito_service import DepositoService
from bank_djago.services.notifikasi import NotifikasiUI
from bank_djago.services.transaksi.transaksiUI import TransaksiUI
from bank_djago.services.rekening.rekeningUI import RekeningUI
from bank_djago.services.deposito.ui import DepositoUI
from bank_djago.services.layanan_nasabah import LayananNasabah
from bank_djago.services.transaksi.riwayat.ui import RiwayatUI
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas


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
            break

        return nasabah



    @staticmethod
    def menu_utama(bank,nasabah):

        rekening = Utilitas.pilihan_rekening(nasabah)

        while True:
            UI.header("SELAMAT DATANG DI BANK DJAGO",UI.BIRU)
            print()
            print(f"👋Halo,{nasabah.nama}!")
            deposito = DepositoService.depo_jatuh_tempo(nasabah)
            if deposito:
                print(f"⚠️ Anda memiliki {len(deposito)} yang telah jatuh tempo")

            print()
            print("1. Menu layanan Rekening")
            print("2. Menu Transaksi")
            print("3. Menu Deposito")
            print("4. Menu Profil")
            print("5. Menu Lihat Riwayat")
            print("6. Ganti rekening")
            print("7. Cek Notifikasi")
            print("8. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                RekeningUI.menu(bank,rekening)

            elif pilihan == "2":
                TransaksiUI.menu_transaksi(bank, rekening)

            elif pilihan == "3":
                DepositoUI.menu_deposito(bank, nasabah, rekening)

            elif pilihan == "4":
                LayananNasabah.menu_profil(nasabah,rekening)

            elif pilihan == "5":
                RiwayatUI.menu_riwayat(rekening)

            elif pilihan == "6":
               rekening = Utilitas.pilihan_rekening(nasabah)
               UI.sukses("Ganti rekening berhasil!")

            elif pilihan == "7":
                NotifikasiUI.menu(nasabah)

            elif pilihan == "8":
                break













