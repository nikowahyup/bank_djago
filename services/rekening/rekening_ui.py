import sqlite3

from bank_djago.services.rekening.pengajuan_ui import PengajuanUI
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.validator import Validator


class RekeningUI:
    level = {1: 'Reguler',
             2: 'Prioritas',
             3: 'Gold',
             4: 'Platinum'}
    @staticmethod
    def menu(nasabah,rekening):

        while True:
            UI.header("MENU LAYANAN REKENING", UI.KUNING)
            print()
            print("1. Buka Rekening Baru")
            print("2. Tingkatkan Rekening")
            print("3. Turunkan Rekening")
            print("4. Blokir Rekening")
            print("5. Buka Blokir")
            print("6. Penutupan Rekening")
            print("7. Ganti PIN rekening")
            print("8. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                RekeningUI.buka_rekening(nasabah)
            elif pilihan == "2":
                rekening = RekeningUI.upgrade_rekening(rekening)
            elif pilihan == "3":
                rekening = RekeningUI.downgrade_rekening(rekening)
            elif pilihan == "4":
                RekeningUI.blokir_rekening(rekening)
            elif pilihan == "5":
                RekeningUI.buka_blokir(rekening)
            elif pilihan == "6":
                PengajuanUI.kelola_penutupan_rekening(rekening)
            elif pilihan == "7":
                RekeningUI.ganti_pin(rekening)
            elif pilihan == "8":
                break


    @staticmethod
    def upgrade_rekening(rekening):
        UI.header("TINGKATKAN REKENING",UI.MERAH)
        print()
        if rekening.level == 4:
            print("Rekening ini sudah platinum")
            return rekening
        print("Mau tingkatkan ke mana: ")
        opsi = list(range(rekening.level+1,5))
        while True:
            for i in opsi:
                print(f"{i}. {RekeningUI.level[i]}")
            try:
                pilihan = int(input("Masukkan pilihan: "))
            except ValueError:
                print("Tolong masukkan angka")
                continue
            if pilihan not in opsi:
                print("Pilihan tidak valid")
                continue

            break

        try:
            rekening_baru = RekeningService.upgrade_rekening(rekening,pilihan)
            UI.sukses('Peningkatan Sukses!')
            UI.sukses(f"Rekening telah ditingkatkan ke {RekeningUI.level[pilihan]}")
            return rekening_baru
        except ValueError as e:
            UI.gagal("Peningkatan Gagal")
            UI.gagal(str(e))
            return rekening

    @staticmethod
    def downgrade_rekening(rekening):
        UI.header("TURUNKAN REKENING",UI.MERAH)

        print(f"Rekening saat ini : {RekeningUI.level[rekening.level]}")
        if rekening.level == 1:
            print("Rekening sudah reguler")
            return rekening
        while True:
            print("Mau turunkan ke mana: ")
            opsi = list(range(1,rekening.level))
            for i in opsi:
                print(f"{i}. {RekeningUI.level[i]}")
            try:
                pilihan = int(input("Masukkan pilihan: "))
            except ValueError:
                print("Tolong masukkan angka")
                continue
            if pilihan not in opsi:
                print("Pilihan tidak valid")
                continue

            break

        try:
            rekening_baru = RekeningService.downgrade_rekening(rekening,pilihan)
            UI.sukses('Penurunan Sukses!')
            UI.sukses(f"Rekening telah diturunkan ke {RekeningUI.level[pilihan]}")
            return rekening_baru
        except ValueError as e:
            UI.gagal("Penurunan Gagal!")
            UI.gagal(str(e))
            return rekening
    @staticmethod
    def blokir_rekening(rekening):
        UI.header("BLOKIR REKENING",UI.MERAH)

        alasan = input("Masukkan alasan pemblokiran: ")

        konfirmasi = input("Apakah Anda yakin untuk mbmlokir rekening ini(ya/tidak): ").lower()
        if konfirmasi not in('ya','iya','y'):
            return

        try:
            RekeningService.blokir_rekening(rekening=rekening,alasan=alasan)
            UI.sukses(f"Rekening dengan nomor {rekening.norek} berhasil diblokir")
        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def buka_blokir(rekening):
        UI.header("BUKA BLOKIR REKENING",UI.MERAH)

        while True:
            pin = input("Masukkan PIN ynag valid untuk rekening ini(ketik 0 untuk keluar): ").strip()

            if pin == "0":
                return

            if len(pin) != 6 or not pin.isdigit():
                UI.peringatan(
                    "PIN harus berupa 6 digit angka"
                )
                continue
            break

        konfirmasi = input(
            "Apakah Anda yakin ingin membuka kembali "
            "rekening ini(ya/tidak): ").lower().strip()

        if konfirmasi not in('ya','y','iya'):
            return
        try:
            RekeningService.buka_blokir(rekening=rekening,pin=pin)
            UI.sukses(f"Rekening dengan nomor {rekening.norek} berhasil dibuka kembali")

        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def ganti_pin(rekening):
        UI.header(
            "GANTI PIN REKENING",
            UI.MERAH
        )

        # Input PIN lama
        while True:
            pin_lama = input(
                "Masukkan PIN lama "
                "(ketik 0 untuk keluar): "
            ).strip()

            if pin_lama == "0":
                return

            if len(pin_lama) != 6 or not pin_lama.isdigit():
                UI.peringatan(
                    "PIN lama harus berupa 6 digit angka"
                )
                continue

            break

        # Input PIN baru
        while True:
            pin_baru = input(
                "Silakan buat PIN baru: "
            ).strip()

            if len(pin_baru) != 6 or not pin_baru.isdigit():
                UI.peringatan(
                    "PIN baru harus berupa 6 digit angka"
                )
                continue

            konfirmasi_pin = input(
                "Konfirmasi PIN baru: "
            ).strip()

            if pin_baru != konfirmasi_pin:
                UI.peringatan(
                    "Konfirmasi PIN baru tidak sesuai"
                )
                continue

            break

        try:
            RekeningService.ganti_pin(
                rekening=rekening,
                pin_lama=pin_lama,
                pin_baru=pin_baru
            )

            UI.sukses(
                "PIN rekening berhasil diganti"
            )

        except ValueError as e:
            UI.gagal(
                str(e)
            )



    @staticmethod
    def buka_rekening(nasabah):

                print(f"Halo,{nasabah.nama}!")

                Utilitas.keuntungan_rekening()

                while True:
                    print()
                    try:
                        pilihan = int(input("Masukkan pilihan Anda: "))
                        if pilihan not in(1,2,3,4):
                            UI.gagal("Tolong pilih pilihan yang tersedia")
                            continue
                    except ValueError:
                        UI.peringatan("Silahkan masukkan pilihan memakai angka")
                        continue
                    break
                while True:
                    pin = input("Silahkan buat PIN 6 digit angka: ")
                    try:
                        Validator.validasi_pin(pin)
                    except ValueError as e:
                        UI.gagal(str(e))
                        continue
                    break
                try:
                    UI.peringatan("Anda wajib menyetorkan uang setoran awal")
                    setor_awal = int(input("Masukkan nominal: "))
                    Utilitas.animasi("Proses")

                except ValueError:
                    UI.gagal("Masukkan angka yang valid.")
                    return

                try:
                    rekening_baru = RekeningService.buka_rekening(nasabah=nasabah,pilihan=pilihan,pin=pin,setor_awal=setor_awal)
                    print(f"Selamat! Rekening dengan nomor {rekening_baru.norek} telah dibuka!")

                except ValueError as e:
                    UI.gagal(str(e))

                except sqlite3.Error:
                    print("Terjadi kesalahan saat membuka rekening baru. Silahkan coba lagi")




