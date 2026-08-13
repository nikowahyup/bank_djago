
from bank_djago.services.notifikasi import NotifikasiUI
from bank_djago.services.transaksi.transaksiUI import TransaksiUI
from bank_djago.services.rekening.rekeningUI import RekeningUI
from bank_djago.services.deposito.ui import DepositoUI
from bank_djago.services.layanan_nasabah import LayananNasabah
from bank_djago.services.transaksi.riwayat.ui import RiwayatUI
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas
from bank_djago.services.pinjaman.pinjamanUI import PinjamanUI


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
                RekeningUI.menu(bank,rekening)

            elif pilihan == "2":
                TransaksiUI.menu_transaksi(bank, rekening)

            elif pilihan == "3":
                DepositoUI.menu_deposito(bank, nasabah, rekening)

            elif pilihan == "4":
                PinjamanUI.menu(bank,nasabah,rekening)

            elif pilihan == "5":
                RiwayatUI.menu_riwayat(rekening)

            elif pilihan == "6":
                LayananNasabah.menu_profil(nasabah,rekening)

            elif pilihan == "7":
               rekening = Utilitas.pilihan_rekening(nasabah)
               UI.sukses("Ganti rekening berhasil!")


            elif pilihan == "8":
                NotifikasiUI.menu(nasabah)

            elif pilihan == "9":
                break













