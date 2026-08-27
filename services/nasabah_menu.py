from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader

from bank_djago.services.notifikasi import NotifikasiUI
from bank_djago.services.transaksi.transaksi_ui import TransaksiUI
from bank_djago.services.rekening.rekening_ui import RekeningUI
from bank_djago.services.deposito.deposito_ui import DepositoUI
from bank_djago.services.profil_nasabah_ui import LayananNasabah
from bank_djago.services.transaksi.riwayat.riwayat_ui import RiwayatUI
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas
from bank_djago.services.pinjaman.pinjaman_ui import PinjamanUI


class NasabahMenu:

    @staticmethod
    def login():
        while True:
            print()
            print("LOGIN")
            nik = input("Masukkan NIK Anda (ketik 0 untuk keluar): ")

            if nik == "0":
                return

            nasabah = NasabahLoader.muat_nasabah(nik)

            if nasabah is None:
                UI.gagal("NIK tidak terfdatar. Coba Lagi")
                continue


            NasabahMenu.menu_utama(nasabah)
            return





    @staticmethod
    def menu_utama(nasabah):

        rekening = Utilitas.pilihan_rekening(nasabah)
        if not rekening:
            print("Tidak ada rekening yang terdaftar")
            return
        print(f"nomor rekening {rekening.norek}")

        while True:
            UI.header("SELAMAT DATANG DI BANK DJAGO",UI.BIRU)
            print()
            print(f"👋Halo,{nasabah.nama}!")
            notifikasi = nasabah.notifikasi
            if notifikasi:
                print(f"⚠️ Anda memiliki {len(notifikasi)} notifikasi")

            print()
            print("1. Menu layanan Rekening")
            print("2. Menu Transaksi")
            print("3. Menu Deposito")
            print("4. Menu Pinjaman")
            print("5. Menu Lihat Riwayat")
            print("6. Menu Profil")
            print("7. Ganti rekening")
            print("8. Cek Notifikasi")
            print("9. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                RekeningUI.menu(nasabah,rekening)
                pass
            elif pilihan == "2":
                TransaksiUI.menu_transaksi(rekening)

            elif pilihan == "3":
                DepositoUI.menu_deposito(nasabah, rekening)

            elif pilihan == "4":
                PinjamanUI.menu(nasabah, rekening)

            elif pilihan == "5":
                RiwayatUI.menu_riwayat(nasabah)

            elif pilihan == "6":
                LayananNasabah.menu_profil(nasabah,rekening)

            elif pilihan == "7":
               rekening = Utilitas.pilihan_rekening(nasabah)
               UI.sukses("Ganti rekening berhasil!")


            elif pilihan == "8":
                NotifikasiUI.menu(nasabah)

            elif pilihan == "9":
                break













