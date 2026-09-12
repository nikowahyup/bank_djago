from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.loaders.notifikai_loader import NotifikasiLoader
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.services.nasabah.nasabah_service import NasabahService
from bank_djago.services.notifikasi import NotifikasiUI
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.transaksi.transaksi_ui import TransaksiUI
from bank_djago.services.rekening.rekening_ui import RekeningUI
from bank_djago.services.deposito.deposito_ui import DepositoUI
from bank_djago.services.transaksi.riwayat.riwayat_ui import RiwayatUI
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas
from bank_djago.services.pinjaman.pinjaman_ui import PinjamanUI
from bank_djago.services.nasabah.nasabah_ui import NasabahUI


class NasabahMenu:

    @staticmethod
    def login():
        while True:
            print()
            print("LOGIN")
            nik = input("Masukkan NIK Anda (ketik 0 untuk keluar): ")

            if nik == "0":
                return

            data_login = NasabahService.cari_data_login(nik=nik)

            if data_login is None:
                UI.gagal("Data nasabah tidak ditemukan. Coba Lagi")
                continue
            break

        nik_aktif = data_login['nik']


        daftar_norek_aktif = RekeningService.cari_norek_tersedia(nik=nik_aktif)

        norek_aktif = RekeningUI.pilih_rekening(daftar_norek_aktif=daftar_norek_aktif)

        sesi = {'nama': data_login['nama'],
                'nik':nik_aktif,
                'norek':norek_aktif}
        NasabahMenu.menu_utama(sesi)





    @staticmethod
    def menu_utama(sesi):



        while True:
            UI.header("SELAMAT DATANG DI BANK DJAGO",UI.BIRU)
            print()
            print(f"👋 Halo,{sesi['nama']}!")
            print(f"💳 Rekening Aktif : {sesi['norek']}")
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
                RekeningUI.menu(nasabah,rekening)
                pass
            elif pilihan == "2":
                TransaksiUI.menu_transaksi(sesi['norek'])

            elif pilihan == "3":
                DepositoUI.menu_deposito(nasabah, rekening)

            elif pilihan == "4":
                PinjamanUI.menu(nasabah, rekening)

            elif pilihan == "5":
                RiwayatUI.menu_riwayat(nasabah)

            elif pilihan == "6":
                NasabahUI.menu_profil(nik=sesi['nik'])

            elif pilihan == "7":
                daftar_norek = RekeningService.cari_norek_tersedia(nik=sesi['nik'])
                norek_baru = RekeningUI.pilih_rekening(daftar_norek_aktif=daftar_norek)

                if norek_baru is not None:
                    sesi['norek'] = norek_baru
                    UI.sukses("Ganti rekening berhasil")
\


            elif pilihan == "8":
                NotifikasiUI.menu(nasabah)

            elif pilihan == "9":
                break













