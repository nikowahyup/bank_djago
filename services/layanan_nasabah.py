from bank_djago.services.transaksi import RiwayatService
from bank_djago.utils.utililty import Utilitas
from bank_djago.utils.ui import UI
from bank_djago.services.admin.admin_cs import AdminCs
import time

class LayananNasabah:
    @staticmethod
    def animasi():
        print("Proses", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(1)
        print()

    @staticmethod
    def menu_layanan(bank,nasabah):
        print()
        print(f"👋 Halo {nasabah.nama}!")
        while True:
            try:
                UI.header("MENU LAYANAN")
                print()
                print("1. Lihat Biodata")
                print("2. Lihat Rekening")
                print("3. Ganti PIN")
                print("4. Customer Service")
                print("5. Keluar")
                print()

                pilihan = int(input("Masukkan pilihan Anda: "))

                if pilihan == 1:
                    LayananNasabah.biodata(nasabah)
                elif pilihan == 2:
                    LayananNasabah.daftar_rekening(nasabah)
                elif pilihan == 3:
                    LayananNasabah.ganti_pin(bank,nasabah)
                elif pilihan == 4:
                    AdminCs.menu_layanan()
                elif pilihan == 5:
                    break
            except ValueError:
                UI.peringatan("Tolong masukkan pilihan yang valid")

    @staticmethod
    def biodata(nasabah):
        UI.header("BIODATA")
        print(f"NAMA   : {nasabah.nama}")
        print(f"NIK    : {nasabah.NIK}")
        print(f"ALAMAT : {nasabah.alamat}")
        print('='*39,'\n')

    @staticmethod
    def daftar_rekening(nasabah):
        UI.header("DAFTAR REKENING")
        for i,rek in enumerate(nasabah.rekening,1):
            print(f"{i}. {rek.jenis}")
            print(f"💳 Nomor Rekening : {rek.norek}")
            print(f"📃 Status         : {rek.status}")
            print(f"💰 Saldo          : Rp{rek.cek_saldo()}\n")

    @staticmethod
    def ganti_alamat(nasabah):
        UI.header("GANTI ALAMAT")

        alamat_lama = input("Masukkan alamat lama Anda: ")
        if alamat_lama != nasabah.alamat:
            UI.gagal("Alamat tidak cocok")
            return

        alamat_baru = input("Masukkan alamat baru Anda: ")
        nasabah.alamat = alamat_baru
        UI.sukses("Alamat berhasil diubah!\n")


    @staticmethod
    def ganti_pin(bank,nasabah):
        UI.header("GANTI PIN")

        norek = input("Masukkan nomor rekening yang ingin Anda ganti pin: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            UI.gagal("Nomor rekening tidak terdaftar")
            return

        if rekening not in nasabah.rekening:
            UI.gagal("Maaf,rekening tidak terdaftar di akun Anda!")
            return

        pin_lama = input("Masukkan PIN lama: ")
        if not rekening.cek_pin(pin_lama):
            UI.gagal("PIN salah. Akses tidak diberikan")
            return

        pin_baru = input("Masukkan PIN baru: ")
        rekening.ganti_pin(pin_baru)
        LayananNasabah.animasi()
        UI.sukses("PIN berhasil diganti!\n")




    @staticmethod
    def buka_rekening(bank,nasabah):
        UI.header("BUKA REKENING")
        Utilitas.keuntungan_rekening()
        try:
            print()
            pilihan = int(input("Masukkan pilihan Anda: "))
            if pilihan not in bank.jenis_rekening:
                UI.peringatan("Masukkan pilihan yang valid!")
                return

            pin = input("Silahkan buat PIN 6 digit: ")

            if len(pin) != 6 or not pin.isdigit():
                UI.gagal("PIN tidak valid\n")
                return

            rek_baru = bank.buka_rekening(nasabah,pilihan,pin)
            print()
            LayananNasabah.animasi()
            UI.sukses("Rekening Baru Berhasil Dibuat!")
            print(f"💳 Nomor Rekening : {rek_baru.norek[0:4]}-{rek_baru.norek[4:8]}-{rek_baru.norek[8:12]}-{rek_baru.norek[12:16]}\n")
            bank.tambah_audit(kategori="rekening",jenis="buka rekening",log=f"{nasabah.nama } membuuka rekening lain",nik=nasabah.NIK,norek=rek_baru.norek)

        except ValueError:
            UI.peringatan("Tolong pilih menggunakan angka")













