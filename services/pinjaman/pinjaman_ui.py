

from bank_djago.services.pinjaman.pinjaman_service import  PinjamanService
from bank_djago.utils.utility import Utilitas,StatusPinjaman
from bank_djago.utils.ui import UI

class PinjamanUI:

    @staticmethod
    def menu(nasabah,rekening):
        while True:

            UI.header("MENU PINJAMAN",UI.BIRU)
            print()
            print("1. Ajukan Pinjaman")
            print("2. Cairkan Pinjaman")
            print("3. Lihat Status Pinjaman")
            print("4. Bayar Cicilan")
            print("5. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                PinjamanUI.ajukan_pinjaman(nasabah,rekening)

            elif pilihan == "2":
                PinjamanUI.cairkan_pinjaman(bank,nasabah)

            elif pilihan == "3":
                PinjamanUI.lihat_pinjaman(nasabah)

            elif pilihan == "4":
                PinjamanUI.bayar_cicilan(bank,nasabah)

            elif pilihan == "5":
                break







    @staticmethod
    def ajukan_pinjaman(nasabah, rekening):
        UI.header("AJUKAN PINJAMAN", UI.MERAH)
        print()

        try:
            nominal = int(input("Masukkan nominal pinjaman: "))
        except ValueError:
            UI.gagal("Masukkan nominal yang valid")
            return

        print("Pilihan Tenor dan Bunga\n")

        for tenor, bunga in PinjamanService.TENOR.items():
            print(
                f"{tenor} bulan dengan bunga "
                f"{round(bunga * 100)}% / tahun"
            )

        print()

        while True:
            try:
                tenor = int(input("Masukkan pilihan bulan: "))

                if tenor not in PinjamanService.TENOR:
                    UI.gagal("Pilihan tidak tersedia")
                    continue

            except ValueError:
                UI.gagal("Tolong pilih menggunakan angka")
                continue

            break

        try:
            PinjamanService.ajukan_pinjaman(

                nasabah=nasabah,
                rekening=rekening,
                nominal=nominal,
                tenor=tenor
            )

            UI.sukses(
                "Pengajuan telah dikirim. "
                "Mohon tunggu dan lihat status pinjaman "
                "di menu lihat pinjaman"
            )

        except ValueError as e:
            UI.gagal(str(e))



    @staticmethod
    def cairkan_pinjaman(bank,nasabah):
        pinjaman = nasabah.pinjaman
        try:
            PinjamanService.cairkan_pinjaman(bank,pinjaman)
            UI.sukses("Pencairan berhasil! Status pinjaman Anda kini sudah aktif")
        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def lihat_pinjaman(nasabah):
        pinjaman = nasabah.pinjaman
        if pinjaman is None:
            print("Anda masih belum melakukan pinjaman")
            return


        if pinjaman.status == StatusPinjaman.DIAJUKAN:
            print()
            print("⚠️ Pinjaman masih dalam proses verifikasi")
            UI.kotak_status_pinjaman(status=pinjaman.status.value,
                                     nominal=Utilitas.format_rupiah(pinjaman.nominal_pinjaman),
                                     bunga=round(pinjaman.bunga*100),tenor=pinjaman.tenor)




        if pinjaman.status == StatusPinjaman.AKTIF:
            print("╔" + "═" * 35 + "╗")
            print(  f"  STATUS : {pinjaman.status.value}\n"
                    f"  NOMINAL AWAL     : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}\n"
                    f"  SISA POKOK       : Rp{Utilitas.format_rupiah(round(pinjaman.sisa_pokok))}\n"
                    f"  CICILAN TETAP    : Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}\n"
                    f"  CICILAN TERBAYAR : {pinjaman.cicilan_terbayar}/{pinjaman.tenor}\n"
                    f"  BUNGA BULAN INI  : Rp{Utilitas.format_rupiah(round(pinjaman.bunga_bulanan))}")
            print("╚" + "═" * 35 + "╝")
            PinjamanService.hapus_notif_pinjaman(nasabah)
            pinjaman.notifikasi_jatuh_tempo = True




    @staticmethod
    def bayar_cicilan(bank,nasabah):
        UI.header("BAYAR CICILAN",UI.MERAH)
        try:
            konfirmasi = input("Konfirmasi pembayaran cicilan bulanan(ya/tidak): ")
            if konfirmasi not in ("y",'ya','iya'):
                return
            pinjaman = nasabah.pinjaman
            PinjamanService.bayar_cicilan(bank,pinjaman)
            print()
            UI.sukses(f"Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))} telah dipotong dari rekening Anda")
            print("SETELAH BAYAR :", pinjaman.tanggal_jatuh_tempo)
        except ValueError as e:
            UI.gagal(str(e))


