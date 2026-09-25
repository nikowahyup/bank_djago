from bank_djago.utils.utility import Utilitas
from .riwayat_service import RiwayatService
from bank_djago.utils.ui import UI
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.rekening.rekening_ui import RekeningUI


class RiwayatUI:

    @staticmethod
    def menu_riwayat(nik, nama):

        UI.header("PILIH REKENING TERLEBIH DAHULU", UI.KUNING)
        print()
        daftar_rekening = RekeningService.cari_semua_rekening_untuk_riwayat(nik=nik)
        norek = RekeningUI.pilih_rekening_untuk_riwayat(daftar_rekening=daftar_rekening)

        if norek is None:
            return

        while True:
            print()
            UI.header("MENU LIHAT RIWAYAT", UI.KUNING)
            print(f"👋 Halo,{nama}!")
            UI.info_rekening(norek)
            print()
            for nomor, kategori in enumerate(RiwayatService.SEMUA_KATEGORI, start=1):
                print(f"{nomor}. {kategori}")

            print()

            try:
                pilihan = int(input("Masukkan piihan Anda (ketik 0 untuk keluar): "))

            except ValueError:
                UI.gagal("Silakan pilih menggunakan angka")
                continue

            if pilihan == 0:
                return

            if pilihan < 1 or pilihan > len(RiwayatService.SEMUA_KATEGORI):
                UI.gagal("Pilihan tidak valid")
                continue

            kategori = RiwayatService.SEMUA_KATEGORI[pilihan - 1]

            data_riwayat = RiwayatService.ambil_riwayat(norek=norek, kategori=kategori)

            if not data_riwayat:
                UI.gagal(f"Anda belum memiliki riwayat untuk kategori {kategori}")
                continue

            for item in data_riwayat:
                print(Utilitas.format_waktu(item["waktu"]), "|", item["log"])
