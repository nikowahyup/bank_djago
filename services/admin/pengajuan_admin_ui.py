import sqlite3


from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.services.rekening.pengajuan_service import PengajuanService

from bank_djago.utils.ui import UI
from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import PengajuanRepository
from bank_djago.utils.utility import Utilitas


class PengajuanAdminUI:

    @staticmethod
    def kelola_pengajuan():
        UI.header("KELOLA PENGAJUAN",UI.MERAH)
        daftar_pengajuan = PengajuanRepository.cari_semua_pengajuan_diajukan()
        if not daftar_pengajuan:
            print("Masih belum ada pengajuan")
            return

        for i,data in enumerate( daftar_pengajuan, start=1):
            print(f'{i}.')
            print('---------------------------------')
            print(f"ID Pengajuan    : {data["id"]}")
            print(f"Nomor Rekening  : {data["norek"]}")
            print(f"Jenis Pengajuan : {data["jenis"]}")
            print(f"Alasan          : {data["alasan"]}")
            print(f"Waktu Pengajuan : {Utilitas.format_waktu(data["waktu_pengajuan"])}\n")

        id_pengajuan_valid = [data["id"] for data in daftar_pengajuan]

        while True:
            try:
             id_pengajuan = int(input("Masukkan ID yang ingin diproses(ketik 0 untuk keluar) :"))

            except ValueError:
                UI.gagal("Pilih menggunakan angka")
                continue

            if id_pengajuan == 0:
                return

            if id_pengajuan not in id_pengajuan_valid:
                UI.gagal("ID tidak ditemukan dalam list pengajuan")
                continue
            break

        pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(id_pengajuan)

        if pengajuan is None:
            UI.gagal("Pengajuan tidak ditemukan")
            return

        print()
        UI.header("DETAIL PENGAJUAN REKENING", UI.MERAH)
        print()

        print(f"ID Pengajuan    : {pengajuan['id']}")
        print(f"Nomor Rekening  : {pengajuan['norek']}")
        print(f"Jenis Pengajuan : {pengajuan['jenis']}")
        print(f"Alasan          : {pengajuan['alasan']}")
        print(
            f"Waktu Pengajuan : "
            f"{Utilitas.format_waktu(pengajuan['waktu_pengajuan'])}"
        )

        print()

        if pengajuan["jenis"] == "tutup":
            pinjaman_aktif = PinjamanRepository.cari_pinjaman_aktif(pengajuan["norek"])
            deposito_aktif = DepositoRepository.cari_deposito_aktif(pengajuan["norek"])
            if pinjaman_aktif is None:
                pesan_pinjaman = "Pinjaman berjalan : tidak ada"
            else:
                pesan_pinjaman = f"Pinjaman berjalan : ada — status {pinjaman_aktif["status"]}"

            if deposito_aktif is None:
                pesan_deposito = "Deposito berjalan : tidak ada"
            else:
                pesan_deposito = f"Deposito berjalan : ada — status {deposito_aktif["status"]} "

            if pinjaman_aktif is None and deposito_aktif is None:
                pesan = "Rekening memenuhi syarat penutupan"
            else:
                pesan = "Rekening belum memenuhi syarat penutupan"

            print("========== KONDISI REKENING ==========")
            print()
            print(pesan_pinjaman)
            print(pesan_deposito)
            print(f"Kesimpulan : {pesan}")

        while True:
            print()
            print("1. Setujui Pengajuan")
            print("2. Tolak Pengajuan")
            print("3. Tunda/kembali\n")

            try:
                pilihan = int(input("Masukkan pilihan kamu: "))
            except ValueError:
                UI.gagal("Pilih menggunakan angka")
                continue
            if pilihan not in(1,2,3):
                UI.gagal("Pilihan tidak valid")
                continue
            break

        if pilihan == 1:
            catatan = input("Buat catatan untuk nasabah: ")
            try:
                PengajuanService.setujui_pengajuan(id_pengajuan=id_pengajuan,catatan_admin=catatan)
                UI.sukses("Penyetujuan pengajuan berhasil")
            except ValueError as e:
                UI.gagal(str(e))

            except sqlite3.Error as e:
                print(f"Terjadi kesalahan dalam memperbarui pengajuan : {e}")

        elif pilihan == 2:
            try:
                catatan = input("Buat catatan untuk nasabah: ")
                PengajuanService.tolak_pengajuan(id_pengajuan=id_pengajuan,catatan_admin=catatan)
                UI.sukses("Penolakan pengajuan berhasil")
            except ValueError as e:
                UI.gagal(str(e))

            except sqlite3.Error as e:
                print(f"Terjadi kesalahan dalam memperbarui pengajuan : {e}")
        elif pilihan == 3:
            return

        else:
            UI.gagal("Masukkan opsi yang valid")


