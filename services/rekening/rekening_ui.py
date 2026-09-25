import sqlite3

from bank_djago.services.exceptions import BankException
from bank_djago.services.rekening.pengajuan_ui import PengajuanUI
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.validator import Validator


class RekeningUI:
    level = {1: "Reguler", 2: "Prioritas", 3: "Gold", 4: "Platinum"}

    @staticmethod
    def menu_rekening(nik, norek, nama):

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
                RekeningUI.buka_rekening(nik=nik, nama=nama)
            elif pilihan == "2":
                RekeningUI.upgrade_rekening(nik=nik, norek=norek)
            elif pilihan == "3":
                RekeningUI.downgrade_rekening(nik=nik, norek=norek)
            elif pilihan == "4":
                RekeningUI.blokir_rekening(nik=nik, norek=norek)
            elif pilihan == "5":
                RekeningUI.buka_blokir(nik=nik, norek=norek)
            elif pilihan == "6":
                PengajuanUI.kelola_penutupan_rekening(nik=nik, norek=norek)
            elif pilihan == "7":
                RekeningUI.ganti_pin(nik=nik, norek=norek)
            elif pilihan == "8":
                break

    @staticmethod
    def upgrade_rekening(nik, norek):
        UI.header("TINGKATKAN REKENING", UI.MERAH)
        print()
        data_rekening = RekeningService.cari_rekening_untuk_diubah_atau_untuk_pangajuan(
            norek=norek
        )

        if data_rekening is None:
            UI.gagal("Rekening tidak terdaftar")
            return

        if data_rekening["level"] == 4:
            print("Rekening ini sudah platinum")
            return

        print("Mau tingkatkan ke mana: ")
        opsi = list(range(data_rekening["level"] + 1, len(RekeningUI.level) + 1))
        while True:
            for i in opsi:
                print(f"{i}. {RekeningUI.level[i]}")
            try:
                pilihan = int(input("Masukkan pilihan Anda(ketik 0 untuk keluar): "))
            except ValueError:
                UI.gagal("Silahkan pilih menggunakan angka")
                continue
            if pilihan == 0:
                return
            if pilihan not in opsi:
                print("Pilihan tidak valid")
                continue

            break

        try:
            RekeningService.upgrade_rekening(nik=nik, norek=norek, target_level=pilihan)

            UI.sukses("Peningkatan Sukses!")
            UI.sukses(f"Rekening telah ditingkatkan ke {RekeningUI.level[pilihan]}")

        except BankException as e:
            UI.gagal("Peningkatan Gagal")
            UI.gagal(str(e))

        except sqlite3.Error as e:
            UI.gagal("Peningkatan Gagal")
            UI.gagal(str(e))

    @staticmethod
    def downgrade_rekening(nik, norek):
        UI.header("TURUNKAN REKENING", UI.MERAH)

        data_rekening = RekeningService.cari_rekening_untuk_diubah_atau_untuk_pangajuan(
            norek=norek
        )

        if data_rekening is None:
            UI.gagal("Rekening tidak terdaftar")
            return

        if data_rekening["level"] == 1:
            print("Rekening ini sudah reguler")
            return

        print("Mau turunkan ke mana: ")

        while True:

            opsi = list(range(1, data_rekening["level"]))
            while True:
                for i in opsi:
                    print(f"{i}. {RekeningUI.level[i]}")
                try:
                    pilihan = int(
                        input("Masukkan pilihan Anda(ketik 0 untuk keluar): ")
                    )
                except ValueError:
                    UI.gagal("Silahkan pilih menggunakan angka")
                    continue
                if pilihan == 0:
                    return
                if pilihan not in opsi:
                    print("Pilihan tidak valid")
                    continue

                break

            try:
                RekeningService.downgrade_rekening(
                    nik=nik, norek=norek, target_level=pilihan
                )

                UI.sukses("Peningkatan Sukses!")
                UI.sukses(f"Rekening telah ditingkatkan ke {RekeningUI.level[pilihan]}")

            except BankException as e:
                UI.gagal("Penurunan Gagal")
                UI.gagal(str(e))

            except sqlite3.Error as e:
                UI.gagal("Penurunan Gagal")
                UI.gagal(str(e))

    @staticmethod
    def blokir_rekening(nik, norek):
        UI.header("BLOKIR REKENING", UI.MERAH)

        alasan = input("Masukkan alasan pemblokiran: ")

        konfirmasi = input(
            "Apakah Anda yakin untuk mbmlokir rekening ini(ya/tidak): "
        ).lower()
        if konfirmasi not in ("ya", "iya", "y"):
            return

        try:
            RekeningService.blokir_rekening(nik=nik, norek=norek, alasan=alasan)

            UI.sukses(f"Rekening dengan nomor {norek} berhasil diblokir")

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.peringatan(
                "Terjadi kesalahan saat memblokir rekening. Silakan coba lagi"
            )

    @staticmethod
    def buka_blokir(nik, norek):
        UI.header("BUKA BLOKIR REKENING", UI.MERAH)

        while True:
            pin = input(
                "Masukkan PIN ynag valid untuk rekening ini(ketik 0 untuk keluar): "
            ).strip()

            if pin == "0":
                return

            if len(pin) != 6 or not pin.isdigit():
                UI.peringatan("PIN harus berupa 6 digit angka")
                continue
            break

        konfirmasi = (
            input("Apakah Anda yakin ingin membuka kembali " "rekening ini(ya/tidak): ")
            .lower()
            .strip()
        )

        if konfirmasi not in ("ya", "y", "iya"):
            return
        try:
            RekeningService.buka_blokir(nik=nik, norek=norek, pin=pin)
            UI.sukses(f"Rekening dengan nomor {norek} berhasil dibuka kembali")

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.peringatan(
                "Terjadi kesalahan saat membuka blokir rekening. Silakan coba lagi"
            )

    @staticmethod
    def ganti_pin(nik, norek):
        UI.header("GANTI PIN REKENING", UI.MERAH)

        # Input PIN lama
        while True:
            pin_lama = input("Masukkan PIN lama " "(ketik 0 untuk keluar): ").strip()

            if pin_lama == "0":
                return

            if len(pin_lama) != 6 or not pin_lama.isdigit():
                UI.peringatan("PIN lama harus berupa 6 digit angka")
                continue

            break

        # Input PIN baru
        while True:
            pin_baru = input("Silakan buat PIN baru: ").strip()

            if len(pin_baru) != 6 or not pin_baru.isdigit():
                UI.peringatan("PIN baru harus berupa 6 digit angka")
                continue

            konfirmasi_pin = input("Konfirmasi PIN baru: ").strip()

            if pin_baru != konfirmasi_pin:
                UI.peringatan("Konfirmasi PIN baru tidak sesuai")
                continue

            break

        try:
            RekeningService.ganti_pin(
                nik=nik, norek=norek, pin_lama=pin_lama, pin_baru=pin_baru
            )

            UI.sukses("PIN rekening berhasil diganti")

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.peringatan(
                "Terjadi kesalahan saat memperbarui PIN rekening. Silakan coba lagi"
            )

    @staticmethod
    def buka_rekening(nik, nama):

        print(f"Halo,{nama}!")

        Utilitas.keuntungan_rekening()

        while True:
            print()
            try:
                pilihan = int(input("Masukkan pilihan Anda: "))
                if pilihan not in (1, 2, 3, 4):
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
            rekening_baru = RekeningService.buka_rekening(
                nik=nik, pilihan=pilihan, pin=pin, setor_awal=setor_awal
            )
            print(f"Selamat! Rekening dengan nomor {rekening_baru.norek} telah dibuka!")

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            print("Terjadi kesalahan saat membuka rekening baru. Silahkan coba lagi")

    @staticmethod
    def pilih_rekening(daftar_norek_aktif):

        if not daftar_norek_aktif:
            return None

        if len(daftar_norek_aktif) == 1:
            return daftar_norek_aktif[0]

        while True:
            print("Pilih nomor rekening yang ingin Anda gunakan\n")

            for i, norek in enumerate(daftar_norek_aktif, start=1):
                print(f"{i}. {norek}")

            try:
                print()
                pilihan = int(input("Masukkan pilihan Anda: "))

                if pilihan < 1 or pilihan > len(daftar_norek_aktif):
                    UI.gagal("Pilihan tidak valid")
                    continue

            except ValueError:
                UI.gagal("Silakan masukkan angka")
                continue

            return daftar_norek_aktif[pilihan - 1]

    @staticmethod
    def pilih_rekening_untuk_riwayat(daftar_rekening):

        if not daftar_rekening:
            return None

        while True:
            print("Pilih nomor rekening yang ingin Anda cek riwayatnya\n")

            for nomor, (norek, status) in enumerate(daftar_rekening.items(), start=1):
                print(f"{nomor}. {norek} | {status}")

            try:
                print()
                pilihan = int(input("Masukkan pilihan Anda(ketik 0 untuk keluar): "))

            except ValueError:
                UI.gagal("Silakan masukkan angka")
                continue

            if pilihan == 0:
                return

            if pilihan < 1 or pilihan > len(daftar_rekening):
                UI.gagal("Pilihan tidak valid")
                continue

            daftar_norek = list(daftar_rekening)

            norek_pilihan = daftar_norek[pilihan - 1]

            return norek_pilihan
