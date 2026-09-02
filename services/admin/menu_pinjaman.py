
import sqlite3
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas

# from bank_djago.services.pinjaman.pinjaman_service import PinjamanService


class AdminPinjaman:

    @staticmethod
    def kelola_pengajuan_pinjaman():
        daftar_pengajuan = (
            PinjamanRepository.cari_semua_pinjaman_diajukan()
        )

        if not daftar_pengajuan:
            print("Belum ada pengajuan pinjaman")
            return

        UI.header("DAFTAR PENGAJUAN PINJAMAN", UI.BIRU)

        for nomor, data_pinjaman in enumerate(
                daftar_pengajuan,
                start=1
        ):
            data_rekening = (
                RekeningRepository.cari_rekening_dengan_norek(
                    norek=data_pinjaman["norek"]
                )
            )

            if data_rekening is None:
                UI.gagal(
                    f"Rekening untuk pinjaman ber-ID "
                    f"{data_pinjaman['id']} tidak ditemukan"
                )
                return

            data_nasabah = (
                NasabahRepository.cari_nasabah_dengan_nik(
                    nik=data_rekening["nik_pemilik"]
                )
            )

            if data_nasabah is None:
                UI.gagal(
                    f"Nasabah untuk pinjaman ber-ID "
                    f"{data_pinjaman['id']} tidak ditemukan"
                )
                return

            print()
            print(f"{nomor}. Pinjaman #{data_pinjaman['id']}")
            print(f"   Nasabah : {data_nasabah['nama']}")
            print(f"   NIK     : {data_nasabah['nik']}")
            print(f"   Norek   : {data_pinjaman['norek']}")


        daftar_id = {
            data_pinjaman["id"]
            for data_pinjaman in daftar_pengajuan
        }

        while True:
            try:
                id_pinjaman = int(
                    input(
                        "\nMasukkan ID yang ingin diproses "
                        "(ketik 0 untuk keluar): "
                    )
                )

            except ValueError:
                UI.gagal("Pilih menggunakan angka")
                continue

            if id_pinjaman == 0:
                return

            if id_pinjaman not in daftar_id:
                UI.gagal("ID tidak ditemukan dalam daftar pengajuan")
                continue

            break

        data_pinjaman = (
            PinjamanRepository.cari_pinjaman_dengan_id(
                id_pinjaman=id_pinjaman
            )
        )

        if data_pinjaman is None:
            UI.gagal("Pinjaman tidak ditemukan")
            return

        data_rekening = (
            RekeningRepository.cari_rekening_dengan_norek(
                norek=data_pinjaman["norek"]
            )
        )

        if data_rekening is None:
            UI.gagal("Rekening pinjaman tidak ditemukan")
            return

        data_nasabah = (
            NasabahRepository.cari_nasabah_dengan_nik(
                nik=data_rekening["nik_pemilik"]
            )
        )

        if data_nasabah is None:
            UI.gagal("Nasabah pemilik pinjaman tidak ditemukan")
            return

        print()
        UI.header("DETAIL PENGAJUAN PINJAMAN", UI.MERAH)
        print()

        print(f"ID Pinjaman : {data_pinjaman['id']}")
        print(f"Nasabah     : {data_nasabah['nama']}")
        print(f"NIK         : {data_nasabah['nik']}")
        print(f"Rekening    : {data_rekening['norek']}")
        print(
            f"Nominal     : Rp"
            f"{Utilitas.format_rupiah(data_pinjaman['nominal_pinjaman'])}"
        )
        print(
            f"Bunga       : "
            f"{data_pinjaman['bunga'] * 100}% per tahun"
        )
        print(f"Tenor       : {data_pinjaman['tenor']} bulan")
        print(f"Status      : {data_pinjaman['status']}")

        while True:
            print()
            print("1. Setujui Pinjaman")
            print("2. Tolak Pinjaman")
            print("3. Tunda/kembali")

            proses = input("Pilih proses pengajuan: ")

            if proses == "1":
                try:
                    PinjamanService.setujui_pinjaman(
                        id_pinjaman=id_pinjaman
                    )

                    UI.sukses(
                        "Pengajuan pinjaman berhasil disetujui"
                    )

                except ValueError as error:
                    UI.gagal(str(error))

                except sqlite3.Error as error:
                    UI.gagal(
                        f"Terjadi kesalahan pada database: {error}"
                    )

                return

            elif proses == "2":
                catatan_admin = input(
                    "Berikan catatan kepada nasabah: "
                )

                try:
                    PinjamanService.tolak_pinjaman(
                        id_pinjaman=id_pinjaman,
                        catatan_admin=catatan_admin
                    )

                    UI.sukses(
                        "Pengajuan pinjaman berhasil ditolak"
                    )

                except ValueError as error:
                    UI.gagal(str(error))

                except sqlite3.Error as error:
                    UI.gagal(
                        f"Terjadi kesalahan pada database: {error}"
                    )

                return

            elif proses == "3":
                return

            else:
                UI.gagal("Pilihan tidak tersedia")