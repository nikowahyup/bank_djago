import sqlite3

from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas


class TransaksiUI:



    @staticmethod
    def menu_transaksi(rekening):
        while True:
            UI.header("MENU TRANSAKSI",UI.BIRU)
            print()
            print("1. Setor Tunai")
            print("2. Tarik Tunai")
            print("3. Transfer")
            print("4. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                TransaksiUI.setor_tunai(rekening)
            elif pilihan == "2":
                TransaksiUI.tarik_tunai(rekening)
            elif pilihan == "3":
                TransaksiUI.transfer(rekening)
            elif pilihan == "4":
                break



    @staticmethod
    def setor_tunai(rekening):
        print()
        UI.header("SETOR TUNAI",UI.MERAH)
        try:
             print()
             nominal  = int(input("Masukkan nominal setor: "))
             Utilitas.animasi("proses")
             TransaksiService.setor_tunai(rekening, nominal)
             UI.sukses(f"Setor tunai berhasil! Rp{Utilitas.format_rupiah(nominal)} telah ditambahkan ke rekening Anda")

        except ValueError as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            print("Terjadi kesalahan saat menyimpan transaksi. Silahkan coba lagi")

    @staticmethod
    def tarik_tunai(rekening):
        print()
        UI.header("TARIK TUNAI",UI.MERAH)
        try:
            print()
            nominal  = int(input("Masukkan nominal tarik: "))
            Utilitas.animasi("proses")
            TransaksiService.tarik_tunai(rekening,nominal)
            UI.sukses(f"Tarik tunai berhasil! Rp{Utilitas.format_rupiah(nominal)} telah dipotong dari rekening Anda")
        except ValueError as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            print("Terjadid kesalahan saat menyimpan transaksi. Silahkan coba lagi")

    @staticmethod
    def transfer(rekening):

        print()
        UI.header("TRANSFER SALDO",UI.MERAH)
        try:
            print()
            rek_penerima = input("Masukkan nomor rekening penerima: ")
            Utilitas.animasi("Mencari penerima")
            penerima = TransaksiService.cari_penerima(rek_penerima,rekening)
            UI.sukses("Rekening ditemukan")
            UI.wadah_info(penerima.pemilik.nama,rek_penerima)
        except ValueError as e:
            UI.gagal(str(e))
            return

        try:
            print()
            nominal = int(input("Masukkan nominal transfer: "))
            Utilitas.animasi("proses")
            TransaksiService.transfer(rekening,rek_penerima,nominal)
            UI.sukses(f"Transfer berhasil! Rp{Utilitas.format_rupiah(nominal)} telah masuk ke rekening {penerima.pemilik.nama}")

        except ValueError as e:

            UI.gagal(str(e))

