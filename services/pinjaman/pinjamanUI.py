from bank_djago.services.pinjaman.pinjaman_service import StatusPinjaman, PinjamanService
from bank_djago.utils.utililty import Utilitas
from bank_djago.utils.ui import UI

class PinjamanUI:
    pass




    @staticmethod
    def menu(bank,nasabah,rekening):
        pass



    @staticmethod
    def ajukan_pinjaman(bank,nasabah,rekening):
        pass


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

        if pinjaman.status == StatusPinjaman.DIAJUKAN:
            print("Pinjaman masih dalam proses verifikasi")
            print(f"STATUS  : {pinjaman.status}\n"
                  f"NOMINAL : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}\n"
                  f"BUNGA   : {pinjaman.bunga*100} / tahun\n"
                  f"TENOR   : {pinjaman.tenor} bulan\n")



        if pinjaman.status == StatusPinjaman.DITOLAK:
            print("Maaf,pengajuan pinjaman Anda ditolak")
            return

        if pinjaman.status == StatusPinjaman.DISETUJUI:
            print("Selamat! Pengajuan pinjaman:")
            print(f"NOMINAL : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}\n"
                  f"BUNGA   : {pinjaman.bunga*100} / tahun\n"
                  f"TENOR   : {pinjaman.tenor} bulan\n"
                  f"CIICLAN : Rp{Utilitas.format_rupiah(pinjaman.cicilan_tetap)}")
            print("Telah disetujui!\n")
            print("Silahkan pergi ke menu pencairan untuk mencairkan pinjaman Anda")


        if pinjaman.status == StatusPinjaman.AKTIF:
            print(f"STATUS : {pinjaman.status}\n"
                  f"NOMINAL AWAL     : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}\n"
                  f"SISA POKOK       : Rp{Utilitas.format_rupiah(pinjaman.sisa_pokok)}\n"
                  f"CICILAN          : Rp{Utilitas.format_rupiah(pinjaman.cicilan_tetap)}\n"
                  f"CICILAN TERBAYAR : {pinjaman.cicilan_terbayar}/{pinjaman.tenor}\n"
                  f"BUNGA BULAN INI  : Rp{Utilitas.format_rupiah(pinjaman.bunga_bulanan)}")




    @staticmethod
    def bayar_cicilan(nasabah):

        pass

