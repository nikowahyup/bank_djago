import sqlite3

from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas
from bank_djago.services.exceptions import BankException


class TransaksiUI:



    @staticmethod
    def menu_transaksi(nik, norek):
        while True:
            UI.header("MENU TRANSAKSI",UI.BIRU)
            print()
            print("1. Setor Tunai")
            print("2. Tarik Tunai")
            print("3. Transfer")
            print("4. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                TransaksiUI.setor_tunai(nik=nik,norek=norek)
            elif pilihan == "2":
                TransaksiUI.tarik_tunai(nik=nik,norek=norek)
            elif pilihan == "3":
                TransaksiUI.transfer(nik=nik, norek=norek)
            elif pilihan == "4":
                break



    @staticmethod
    def setor_tunai(nik,norek):
        print()
        UI.header("SETOR TUNAI",UI.MERAH)
        try:
             print()
             nominal  = int(input("Masukkan nominal setor: "))

             Utilitas.animasi("proses")
             TransaksiService.setor_tunai(
                 nik_masuk=nik,
                 norek=norek,
                 nominal=nominal
             )

             UI.sukses(
                 f"Setor tunai berhasil!\n"
                 f" Rp{Utilitas.format_rupiah(nominal)} telah ditambahkan "
                 f"ke rekening Anda"
            )

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error as error:
            print(
                f"Terjadi kesalahan saat menyimpan transaksi.\n"
                  f" Silahkan coba lagi {error}"
            )

    @staticmethod
    def tarik_tunai(nik, norek):
        print()
        UI.header("TARIK TUNAI",UI.MERAH)
        try:
            print()
            nominal  = int(input("Masukkan nominal tarik: "))
            Utilitas.animasi("proses")

            TransaksiService.tarik_tunai(
                nik_masuk=nik,
                norek=norek,
                nominal=nominal
            )
            UI.sukses(
                f"Tarik tunai berhasil!\n"
                f" Rp{Utilitas.format_rupiah(nominal)} telah dipotong dari rekening Anda")

        except BankException  as e:
            UI.gagal(str(e))

        except sqlite3.Error as error:
            print(f"Terjadi kesalahan saat menyimpan transaksi. \n"
                  f"Silahkan coba lagi {error}")

    @staticmethod
    def transfer(nik, norek):

        print()
        UI.header("TRANSFER SALDO",UI.MERAH)
        try:
            print()
            rek_penerima = input("Masukkan nomor rekening penerima: ")
            Utilitas.animasi("Mencari penerima")
            penerima = TransaksiService.cari_penerima(
                norek_penerima=rek_penerima,
                norek_pengirim=norek)
            UI.sukses("Rekening ditemukan")
            UI.wadah_info(penerima.pemilik.nama,rek_penerima)
        except BankException as e:
            UI.gagal(str(e))
            return

        try:
            print()
            nominal = int(input("Masukkan nominal transfer: "))
            Utilitas.animasi("proses")

            TransaksiService.transfer(
                nik_masuk=nik,
                norek_pengirim=norek,
                norek_penerima=rek_penerima,
                nominal=nominal
            )

            UI.sukses(f"Transfer berhasil! Rp{Utilitas.format_rupiah(nominal)} telah masuk\n"
                      f"ke rekening {penerima.pemilik.nama}")

        except BankException as e:

            UI.gagal(str(e))

