from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas

from bank_djago.services.pinjaman.pinjaman_service import PinjamanService


class AdminPinjaman:
    pass


    @staticmethod
    def menu(bank):
        while True:
            print('1. Lihat Pengajuan')
            print('2. Proses Pengajuan')

            print('3. Keluar\n')

            pilihan = input("Masukkan pilihan kamu: ")

            if pilihan == "1":
                AdminPinjaman.lihat_pengajuan(bank)
            elif pilihan == "2":
                AdminPinjaman.proses_pengajuan(bank)

            elif pilihan == "3":
                break








    @staticmethod
    def lihat_pengajuan(bank):
        daftar = PinjamanService.daftar_ajuan(bank)

        if not daftar:
            print("Belum Ada Pengajuan")
            return

        UI.header("DAFTAR PENGAJUAN PINJAMAN", UI.BIRU)
        for i,pinjaman in enumerate(daftar,start=1):


                print(
                    f"{i}. Pinjaman #{pinjaman.ID}\n"
                    f"   Nasabah : {pinjaman.pemilik.nama}\n"
                    f"   NIK     : {pinjaman.pemilik.NIK}\n"
                    f"   Nominal : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}\n"
                    f"   Bunga   : {pinjaman.bunga * 100:.2f}% / tahun\n"
                    f"   Tenor   : {pinjaman.tenor} bulan\n"
                )




    @staticmethod
    def proses_pengajuan(bank):
        daftar = PinjamanService.daftar_ajuan(bank)
        if not daftar:
            print("Belum ada pengajuan")

        while True:
            for i,pinjaman in enumerate(daftar,start=1):
                print(f"{i}. {pinjaman.pemilik.nama}\n"
                      f"Nominal : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}\n"
                      f"Tenor   : {pinjaman.tenor} bulan")


            try:
                pilihan = int(input("Pilih pengajuan: "))
                if pilihan < 0 or pilihan > len(daftar):
                    UI.gagal("Pilihan tidak valid")
                    continue
            except ValueError:
                    UI.gagal("Masukkan angka")
                    continue
            break

        pinjaman = daftar[pilihan - 1]

        while True :

            print()
            print(f"Nasabah : {pinjaman.pemilik.nama}")
            print(f"Nominal : Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}")
            print(f"Bunga   : {pinjaman.bunga * 100:.2f}% / tahun")
            print(f"Tenor   : {pinjaman.tenor} bulan\n")

            print("1. Setujui")
            print("2. Tolak")
            print("3. Kembali")

            pilihan = input("Masukkan pilihan kamu: ")

            if pilihan == "1":
                PinjamanService.setujui_pinjaman(bank,pinjaman)
                UI.sukses("Pinjaman berhasil disetujui")

            elif pilihan == "2":
                PinjamanService.ajuan_ditolak(bank,pinjaman)
                UI.sukses("Pinjaman berhasil ditolak")

            elif pilihan == "3":
                break

            else:
                UI.gagal("Masukkan pilihan yang valid")





