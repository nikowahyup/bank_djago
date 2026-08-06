from bank_djago.services.transaksi import TransaksiService
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas


class AdminTeller:

    @staticmethod
    def menu(bank):
        pass

    @staticmethod
    def setor_tunai(bank):
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")
        try:
            rekening = bank.autentikasi_rekening(norek,pin)
            nominal  = int(input("Masukkan nominal setor: "))
            TransaksiService.setor_tunai(rekening,nominal)
            UI.sukses(f"Rp{Utilitas.format_rupiah(nominal)} telah masuk ke rekening Anda")


        except ValueError as e:
            UI.gagal(str(e))
            return


    @staticmethod
    def tarik_tunai(bank):
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")
        try:
            rekening = bank.autentikasi_rekening(norek,pin)
            nominal  = int(input("Masukkan nominal tarik: "))
            TransaksiService.tarik_tunai(rekening,nominal)
            UI.sukses(f"Rp{Utilitas.format_rupiah(nominal)} telah dipotong dari rekening Anda")

        except ValueError as e:
            UI.gagal(str(e))
            return

    @staticmethod
    def transfer(bank):
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")
        try:
            pengirim     = bank.autentikasi_rekening(norek,pin)
            rek_penerima = input("Masukkan nomor rekening penerima: ")
            penerima     = bank.cari_penerima(pengirim,rek_penerima)
            nominal      = int(input("Masukkan nominal transfer: "))
            TransaksiService.transfer(pengirim,penerima,nominal)
            UI.sukses(f"Rp{Utilitas.format_rupiah(nominal)} telah masuk ke rekening {penerima.pemilik.nama}")

        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def lihat_riwayat(bank):
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")

        try:
            rekening = bank.autentikasi_rekening(norek,pin)


