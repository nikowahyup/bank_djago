import time
from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas


class TellerUI:

    @staticmethod
    def animasi(pencarian):
        print(f"{pencarian}", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(1)
        print()

    @staticmethod
    def menu_transaksi(bank):
        while True:
            print()
            UI.header("MENU TRANSAKSI",UI.KUNING)
            print()
            print("1. Cek saldo")
            print("2. Setor Tunai")
            print("3. Tarik Tunai")
            print("4. Transfer Saldo")
            print("5. Lihat Riwayat")
            print("6. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                TellerUI.cek_saldo(bank)
            elif pilihan == "2":
                TellerUI.setor_tunai(bank)
            elif pilihan == "3":
                TellerUI.tarik_tunai(bank)
            elif pilihan == "4":
                TellerUI.transfer(bank)
            elif pilihan == "5":
                TellerUI.lihat_riwayat(bank)
            elif pilihan == "6":
                break

    @staticmethod
    def cek_saldo(bank):
        print()
        UI.header("CEK SALDO")
        try:
            print()
            norek    = input("Masukkan nomor rekening Anda: ")
            pin      = input("Masukkan PIN Anda: ")
            TellerUI.animasi("Mencari rekening")
            rekening = bank.autentikasi_rekening(norek,pin)
            UI.wadah_info(nama=rekening.pemilik.nama,norek=norek,saldo=rekening.cek_saldo())
        except ValueError as e:
            UI.gagal(str(e))


    @staticmethod
    def setor_tunai(bank):
        print()
        UI.header("SETOR TUNAI",UI.MERAH)
        try:
            print()
            norek    = input("Masukkan nomor rekening Anda: ")
            pin      = input("Masukkan PIN Anda: ")
            TellerUI.animasi("Mencari rekening")
            rekening = bank.autentikasi_rekening(norek,pin)
            print()
            UI.sukses("Rekening ditemukan")
            UI.wadah_info(nama=rekening.pemilik.nama,norek=norek,saldo=rekening.cek_saldo())
        except ValueError as e:

            UI.gagal(str(e))
            return

        try:
             print()
             nominal  = int(input("Masukkan nominal setor: "))
             TellerUI.animasi("proses")
             TransaksiService.setor_tunai(bank,rekening, nominal)
             UI.sukses(f"Setor tunai berhasil! Rp{Utilitas.format_rupiah(nominal)} telah ditambahkan ke rekening Anda")

        except ValueError as e:

            UI.gagal(str(e))

    @staticmethod
    def tarik_tunai(bank):
        print()
        UI.header("TARIK TUNAI",UI.MERAH)
        try:
            print()
            norek    = input("Masukkan nomor rekening Anda: ")
            pin      = input("Masukkan PIN Anda: ")
            TellerUI.animasi("Mencari rekening")
            rekening = bank.autentikasi_rekening(norek,pin)
            print()
            UI.sukses("Rekening ditemukan")
            UI.wadah_info(nama=rekening.pemilik.nama,norek=norek,saldo=rekening.cek_saldo())
        except ValueError as e:

            UI.gagal(str(e))
            return
        try:
            print()
            nominal  = int(input("Masukkan nominal tarik: "))
            TellerUI.animasi("proses")
            TransaksiService.tarik_tunai(bank,rekening,nominal)
            UI.sukses(f"Tarik tunai berhasil! Rp{Utilitas.format_rupiah(nominal)} telah dipotong dari rekening Anda")
        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def transfer(bank):
        print()
        UI.header("TRANSFER SALDO",UI.MERAH)
        try:
            print()
            norek        = input("Masukkan nomor rekening Anda: ")
            pin          = input("Masukkan PIN Anda: ")
            TellerUI.animasi("Mencari rekening")
            rekening = bank.autentikasi_rekening(norek,pin)
            print()
            UI.sukses("Rekening ditemukan")
            UI.wadah_info(nama=rekening.pemilik.nama,norek=norek,saldo=rekening.cek_saldo())
        except ValueError as e:
            UI.gagal(str(e))
            return

        try:
            rek_penerima = input("Masukkan nomor rekening penerima: ")
            penerima     = bank.cari_penerima(rekening,rek_penerima)
        except ValueError as e:
            UI.gagal(str(e))
            return

        try:
            print()
            nominal = int(input("Masukkan nominal transfer: "))
            TellerUI.animasi("proses")
            TransaksiService.transfer(bank,rekening,penerima,nominal)
            UI.sukses(f"Transfer berhasil! Rp{Utilitas.format_rupiah(nominal)} telah masuk ke rekening {penerima.pemilik.nama}")

        except ValueError as e:

            UI.gagal(str(e))

    @staticmethod
    def lihat_riwayat(bank):
        from bank_djago.services.transaksi.riwayat.ui import RiwayatUI
        print()
        try:
            print()
            norek        = input("Masukkan nomor rekening Anda: ")
            pin          = input("Masukkan PIN Anda: ")
            rekening     = bank.autentikasi_rekening(norek,pin)
            RiwayatUI.menu_riwayat(rekening)
        except ValueError as e:
            UI.gagal(str(e))