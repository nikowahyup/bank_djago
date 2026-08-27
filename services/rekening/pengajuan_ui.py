from bank_djago.utils.utility import UI,Utilitas
import sqlite3
from bank_djago.services.rekening.pengajuan_service import PengajuanService
from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import PengajuanRepository


class PengajuanUI:


    @staticmethod
    def ajukan_penutupan(rekening):
        print()
        UI.header("PENGAJUAN PENUTUPAN REKENING", UI.MERAH)
        print()

        UI.peringatan(
            "Pengajuan ini tidak langsung menutup rekening Anda."
        )
        print(
            "Rekening tetap dapat digunakan hingga pengajuan "
            "diperiksa dan disetujui oleh admin."
        )
        print()

        while True:
            konfirmasi = input(
                "Apakah Anda yakin ingin mengajukan "
                "penutupan rekening? (y/n): "
            ).strip().lower()

            if konfirmasi == "n":
                UI.peringatan(
                    "Pengajuan penutupan rekening dibatalkan"
                )
                return

            if konfirmasi == "y":
                break

            UI.gagal("Masukkan pilihan y atau n")

        alasan = input(
            "Silakan jelaskan alasan penutupan rekening: "
        ).strip()

        try:
            Utilitas.animasi("Mengirim pengajuan")

            id_pengajuan = (
                PengajuanService.ajukan_penutupan(
                    rekening=rekening,
                    alasan=alasan
                )
            )

            UI.sukses(
                "Pengajuan penutupan rekening berhasil dikirim"
            )
            print(f"Nomor pengajuan: {id_pengajuan}")
            print(
                "Rekening Anda masih aktif selama pengajuan "
                "menunggu keputusan admin."
            )

        except ValueError as error:
            UI.gagal(str(error))

        except sqlite3.Error:
            UI.gagal(
                "Terjadi kesalahan saat menyimpan pengajuan. "
                "Silakan coba lagi."
            )

    @staticmethod
    def selesaikan_penutupan(rekening):
        print()
        UI.header("SELESAIKAN PENUTUPAN REKENING", UI.MERAH)
        print()

        print(f"Nomor rekening : {rekening.norek}")
        print(
            f"Saldo           : "
            f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
        )
        print()
        print("1. Transfer seluruh saldo")
        print("2. Tarik seluruh saldo")
        print("3. Kembali")

        while True:
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan not in ("1", "2", "3"):
                UI.gagal("Pilihan tidak tersedia")
                continue

            break

        if pilihan == "3":
            return

        norek_penerima = None

        if pilihan == "1":
            metode = "transfer"
            norek_penerima = input(
                "Masukkan nomor rekening penerima: "
            ).strip()

            if not norek_penerima:
                UI.gagal("Nomor rekening penerima tidak boleh kosong")
                return

        else:
            metode = "tarik"

        try:
            Utilitas.animasi("Menyelesaikan penutupan")

            nominal = PengajuanService.selesaikan_penutupan(
                rekening=rekening,
                metode=metode,
                norek_penerima=norek_penerima
            )

            UI.sukses("Rekening berhasil ditutup")

            if metode == "transfer":
                print(
                    f"Seluruh saldo Rp"
                    f"{Utilitas.format_rupiah(nominal)} "
                    f"berhasil dipindahkan ke rekening "
                    f"{norek_penerima}"
                )
            else:
                print(
                    f"Seluruh saldo Rp"
                    f"{Utilitas.format_rupiah(nominal)} "
                    f"berhasil ditarik"
                )

        except ValueError as error:
            UI.gagal(str(error))

        except sqlite3.Error as error:
            UI.gagal(
                "Terjadi kesalahan database saat menyelesaikan penutupan"
            )
            print(f"Penyebab: {error}")


    @staticmethod
    def kelola_penutupan_rekening(rekening):
        pengajuan = PengajuanRepository.cari_penutupan_terbaru(norek=rekening.norek)
        if pengajuan is None:
            UI.gagal("Anda masih belum melakukan pengajuan")
            PengajuanUI.ajukan_penutupan(rekening=rekening)
            return

        if pengajuan["status"] == "diajukan":
            UI.gagal("Status pengajuan terbaru Anda masih menunggu persetujuan Admin. Mohon menunggu")
            return
        if pengajuan["status"] == "disetujui":
            PengajuanUI.selesaikan_penutupan(rekening=rekening)
            return

        if pengajuan["status"] == "ditolak":
            UI.gagal(
                f"Pengajuan sebelumnya ditolak. "
                f"Catatan admin: {pengajuan['catatan_admin']}")
            PengajuanUI.ajukan_penutupan(rekening)