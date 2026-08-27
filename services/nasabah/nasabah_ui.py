import sqlite3

from bank_djago.services.nasabah.nasabah_service import NasabahService
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.validator import Validator
from bank_djago.utils.ui import UI


class NasabahUI:

    @staticmethod
    def daftar_jadi_nasabah():
        # Meminta dan memvalidasi data pribadi nasabah.
        while True:
            nama = input("Masukkan nama lengkap Anda: ")
            nik = input("Masukkan NIK Anda: ")
            alamat = input("Masukkan alamat Anda: ")
            pin = input("Silakan buat PIN 6 digit: ")

            Utilitas.animasi("Memeriksa data")
            print()

            try:
                Validator.validasi_nasabah(
                    nama,
                    nik,
                    alamat,
                    pin
                )

            except ValueError as error:
                daftar_pesan = error.args[0]

                if isinstance(daftar_pesan, list):
                    for pesan in daftar_pesan:
                        print("❌", pesan)
                else:
                    UI.gagal(str(error))

                continue

            break


        print()
        Utilitas.keuntungan_rekening()

        while True:
            try:
                print()
                pilihan = int(
                    input("Masukkan pilihan Anda: ")
                )

                if pilihan not in (1, 2, 3, 4):
                    UI.gagal(
                        "Tolong pilih pilihan yang tersedia"
                    )
                    continue

                break

            except ValueError:
                UI.gagal(
                    "Silakan masukkan pilihan yang valid"
                )


        while True:
            try:
                UI.peringatan(
                    "Anda wajib menyetorkan uang setoran awal"
                )

                setor_awal = int(
                    input("Masukkan nominal: ")
                )

                break

            except ValueError:
                UI.gagal("Masukkan angka yang valid")

        Utilitas.animasi("Memproses pendaftaran")

        try:
            nasabah, rekening = (
                NasabahService.daftar_dan_buka_rekening(
                    nik=nik,
                    nama=nama,
                    alamat=alamat,
                    pin=pin,
                    setor_awal=setor_awal,
                    level=pilihan
                )
            )

            Utilitas.sapaan(nasabah, rekening)



        except ValueError as error:

            UI.gagal(str(error))

        except sqlite3.Error:
            print("Terjadi kesalahan dalam menyimpan data. Silahkan coba lagi")

