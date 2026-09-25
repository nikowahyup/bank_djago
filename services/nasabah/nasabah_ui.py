import sqlite3

from bank_djago.services.nasabah.nasabah_service import NasabahService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.validator import Validator
from bank_djago.utils.ui import UI
from bank_djago.services.exceptions import BankException


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
            data_nasabah = NasabahService.cari_nik_terdaftar(nik=nik)
            if data_nasabah is not None:
                UI.gagal(
                    "NIK sudah terdaftar. Silahkan pilih opsi buka rekening di menu layanan rekening"
                )
                return
            print()

            try:
                Validator.validasi_nasabah(nama, nik, alamat, pin)

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
                pilihan = int(input("Masukkan pilihan Anda: "))

                if pilihan not in (1, 2, 3, 4):
                    UI.gagal("Tolong pilih pilihan yang tersedia")
                    continue

                break

            except ValueError:
                UI.gagal("Silakan masukkan pilihan yang valid")

        while True:
            try:
                UI.peringatan("Anda wajib menyetorkan uang setoran awal")

                setor_awal = int(input("Masukkan nominal: "))

                break

            except ValueError:
                UI.gagal("Masukkan angka yang valid")

        Utilitas.animasi("Memproses pendaftaran")

        try:
            nasabah, rekening = NasabahService.daftar_dan_buka_rekening(
                nik=nik,
                nama=nama,
                alamat=alamat,
                pin=pin,
                setor_awal=setor_awal,
                level=pilihan,
            )

            Utilitas.sapaan(nasabah, rekening)

        except BankException as error:

            UI.gagal(str(error))

    @staticmethod
    def menu_profil(nik):

        while True:

            UI.header("MENU PROFIL", UI.KUNING)
            print()
            print("1. Lihat Biodata")
            print("2. Lihat Daftar Rekening")
            print("3. Ganti Alamat")
            print("4. Keluar\n")

            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                NasabahUI.biodata(nik)

            elif pilihan == "2":
                NasabahUI.daftar_rekening(nik)

            elif pilihan == "3":
                NasabahUI.ganti_alamat(nik)

            elif pilihan == "4":
                break

    @staticmethod
    def biodata(nik):
        UI.header("BIODATA", UI.MERAH)

        data_nasabah = NasabahService.cari_nik_terdaftar(nik=nik)
        if data_nasabah is None:
            UI.gagal("NIK tidak terdaftar")
            return

        print()
        print(f"Nama   :{data_nasabah['nama']}")
        print(f"NIK    : {data_nasabah['nik']}")
        print(f"Alamat : {data_nasabah['alamat']}")
        print()

    @staticmethod
    def daftar_rekening(nik):
        UI.header("DAFTAR REKENING", UI.MERAH)

        print()
        daftar_rekening = RekeningService.cari_semua_rekening(nik=nik)

        if not daftar_rekening:
            UI.gagal("Anda belum memiliki rekening")
            return

        for nomor, data_rekening in enumerate(daftar_rekening, start=1):
            jenis = RekeningService.level[data_rekening["level"]]
            print()
            print(f"{nomor}. {jenis}")
            print(f"💳 Nomor Rekening : {data_rekening['norek']}")
            print(f"📃 Status : {data_rekening['status']}")
            print(f"💰 Saldo  : Rp{Utilitas.format_rupiah(data_rekening['saldo'])}")
            print()

    @staticmethod
    def ganti_alamat(nik):
        UI.header("GANTI ALAMAT", UI.MERAH)

        data_nasabah = NasabahService.cari_nik_terdaftar(nik=nik)

        if data_nasabah is None:
            UI.gagal("NIK tidak terdaftar")
            return

        while True:
            alamat_baru = input("Masukkan alamat baru Anda (ketik 0 untuk keluar): ")
            if alamat_baru == "0":
                return
            if not alamat_baru.strip():
                UI.peringatan("Alamat tidak boleh kosong")
                continue
            break

        try:
            NasabahService.ganti_alamat(
                nik=data_nasabah["nik"], alamat_baru=alamat_baru
            )
            UI.sukses("Alamat berhasil diubah")

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.gagal("Terjadi kesalahan saat memperbarui alamat. Silakan coba lagi")
