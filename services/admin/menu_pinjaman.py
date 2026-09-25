import sqlite3
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas

# from bank_djago.services.pinjaman.pinjaman_service import PinjamanService


class AdminPinjaman:

    @staticmethod
    def pilih_pengajuan():
        daftar_pengajuan = PinjamanService.cari_semua_pinjaman_diajukan()

        if not daftar_pengajuan:
            UI.gagal("Belum ada pengajuan pinjaman")
            return

        UI.header("PILIH PENGAJUAN PINJAMAN", UI.MERAH)
        print()

        for nomor, data_pinjaman in enumerate(daftar_pengajuan, start=1):
            print()
            print(f"{nomor}.")
            print(f"Nama     : {data_pinjaman['nama_pemilik']}")
            print(f"Rekening : {data_pinjaman['norek']}")
            print(
                f"Nominal  : Rp{Utilitas.format_rupiah(data_pinjaman['nominal_pinjaman'])}"
            )
            print(f"Tenor    : {data_pinjaman['tenor']} bulan")
            print(f"Bunga    : {data_pinjaman['bunga'] * 100 :.1f}% / tahun")

        print()
        while True:
            try:
                pilihan = int(input("Masukkan pilihan (ketik 0 untuk keluar): "))

            except ValueError:
                UI.gagal("Pilih menggunakan angka")
                continue

            if pilihan == 0:
                return

            if pilihan < 0 or pilihan > len(daftar_pengajuan):
                UI.gagal("Pilihan tidak valid")
                continue
            break

        return daftar_pengajuan[pilihan - 1]

    @staticmethod
    def proses_pengajuan():

        pengajuan_terpilih = AdminPinjaman.pilih_pengajuan()

        if pengajuan_terpilih is None:
            return

        id_pinjaman = pengajuan_terpilih["id"]

        data_pinjaman = PinjamanService.detail_pinjaman(id_pinjaman=id_pinjaman)

        if data_pinjaman is None:
            UI.gagal("Data pinjaman tidak ditemukan")
            return

        detail = data_pinjaman["detail_pinjaman"]
        beban = data_pinjaman["pinjaman_aktif"]

        print()
        print("╔" + "═" * 17, "DETAIL PINJAMAN", "═" * 17 + "╗")
        print()
        print(f"  ID pinjaman : {id_pinjaman}")
        print(f"  Nama        : {detail['nama_pemilik']}")
        print(f"  Rekening    : {detail['norek']}")
        print(f"  Nominal     : Rp{Utilitas.format_rupiah(detail['nominal_pinjaman'])}")
        print(f"  Tenor       : {detail['tenor']} bulan")
        print(f"  Bunga       : {detail['bunga'] * 100 :.1f}% / tahun\n")

        jenis_rekening = RekeningService.level[detail["level_rekening"]]
        print("-" * 15 + "REKENING PEMBAYARAN" + "-" * 15)
        print()

        print(f"  Nomor Rekening : {detail['norek']}")
        print(f"  Jenis          : {jenis_rekening}")
        print(f"  Status         : {detail['status_rekening']}")
        print(
            f"  Saldo          : Rp{Utilitas.format_rupiah(detail['saldo_rekening'])}\n"
        )

        print("-" * 17 + "BEBAN REKENING" + "-" * 17)
        print()
        print(f"  Pinjaman Aktif Rekening : {beban['jumlah_pinjaman_aktif']}")
        print(
            f"  Total Cicilan           : Rp{Utilitas.format_rupiah(beban['total_cicilan_tetap'])}"
        )
        print(
            f"  Total Sisa Pokok        : Rp{Utilitas.format_rupiah(beban['total_sisa_pokok'])}\n"
        )
        print("╚" + "═" * 46 + "╝")
        print()

        while True:
            print()
            print("1. Setujui Pinjaman")
            print("2. Tolak Pinjaman")
            print("3. Keluar\n")
            pilihan = input("Berikan Keputusan (pilih menggunakan angka): ")

            if not pilihan.isdigit():
                UI.gagal("Pilih menggunakan angka")
                continue

            elif pilihan == "1":
                try:
                    PinjamanService.setujui_pinjaman(id_pinjaman=id_pinjaman)

                    UI.sukses(f"Pinjaman berhasil disetujui")
                    return

                except ValueError as e:
                    UI.gagal(str(e))

            elif pilihan == "2":
                catatan = input("Berikan catatan pada nasabah: ")

                try:

                    PinjamanService.tolak_pinjaman(
                        id_pinjaman=id_pinjaman, catatan_admin=catatan
                    )
                    UI.gagal("Pinjaman berhasil ditolak")
                    return

                except ValueError as e:
                    UI.gagal(str(e))

            elif pilihan == "3":
                return
