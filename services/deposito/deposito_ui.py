from bank_djago.services.deposito.deposito_service import DepositoService, JenisAro
from bank_djago.services.exceptions import BankException
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas
import sqlite3

class DepositoUI:

    BATAL = object()


    @staticmethod
    def menu_deposito(nik, norek):

        while True:
            UI.header("MENU DEPOSITO",UI.KUNING)
            UI.info_rekening(norek)
            print()
            print("1. Buka Deposito")
            print("2. Cairkan Deposito")
            print("3. Lihat Info Deposito")
            print("4. Hentikan ARO Deposito")
            print("5. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                DepositoUI.buka_deposito(nik=nik, norek=norek)
            elif pilihan == "2":
                DepositoUI.cairkan_deposito(nik=nik, norek=norek)
            elif pilihan == "3":
                DepositoUI.lihat_deposito(nik=nik)
            elif pilihan == "4":
                DepositoUI.hentikan_aro(nik=nik, norek=norek)

            elif pilihan == '5':
                break

    @staticmethod
    def buka_deposito(nik, norek):
        UI.header("BUKA DEPOSITO", UI.MERAH)
        UI.info_rekening(norek)
        print()

        print("Pilihan jangka waktu deposito:\n")

        for i, (bulan, bunga) in enumerate(
                DepositoService.JANGKA_WAKTU.items(), start=1
        ):
            print(f"{i}. {bulan} bulan | Bunga {bunga:.1%} per tahun")

        try:
            pilihan = int(input("Masukkan pilihan Anda: "))
        except ValueError:
            print("Masukkan pilihan yang valid")
            return

        pilihan_bulan = list(DepositoService.JANGKA_WAKTU.keys())


        if pilihan < 1 or pilihan > len(pilihan_bulan):
            print("Pilihan bulan tidak tersedia")
            return
        lama_bulan = pilihan_bulan[pilihan-1]


        try:
            nominal = int(input("Masukkan nominal deposito: "))
            jenis_aro,lama_aro = DepositoUI.tanya_aro()
            Utilitas.animasi("Membuka deposito")

            id_deposito = DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=nominal,
                lama_bulan=lama_bulan,
                jenis_aro=jenis_aro,
                lama_aro=lama_aro
            )

            UI.sukses(f"Deposito berhasil dibuka! ID deposito: {id_deposito} ")

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.peringatan("Terjadi kesalahan saat menyimpan data. Silakan coba lagi")


    @staticmethod
    def tanya_aro():
        print("\n=== PERPANJANGAN OTOMATIS ===")
        print("1. Tidak diperpanjang")
        print("2. Perpanjang pokok")
        print("3. Perpanjang pokok + bunga")

        while True:
            pilihan = input("Pilihan: ")

            if pilihan == "1":
                return JenisAro.TIDAK, None

            elif pilihan == "2":
                jenis_aro = JenisAro.POKOK
                break

            elif pilihan == "3":
                jenis_aro = JenisAro.POKOK_BUNGA
                break

            print("Pilihan tidak valid.")

        while True:
            try:
                print("1/3/6/12 bulan")
                lama_aro = int(input("Masukkan lama perpanjangan (bulan): "))

                if lama_aro <= 0:
                    print("Lama perpanjangan harus lebih dari 0 bulan.")
                    continue
                if lama_aro not in DepositoService.JANGKA_WAKTU:
                    print("Harap pilih tenor yang tersedia")
                    continue

                return jenis_aro, lama_aro

            except ValueError:
                print("Masukkan angka yang valid.")


    @staticmethod
    def pilih_deposito(daftar_deposito):


        print('========== PILIH DEPOSITO ==========')

        for nomor, data_deposito in enumerate(daftar_deposito ,start=1):

            print()
            print(f'{nomor}.')
            print(f"ID DEPOSITO : {data_deposito['id']}")
            print(f"Status      : {data_deposito['status']}")
            print(f"Rekening    : {data_deposito['norek']}")
            print(f"Nominal     : Rp{Utilitas.format_rupiah(data_deposito['nominal'])}")
            print(f"Tenor       : {data_deposito['lama_bulan']} bulan")
            if data_deposito['jenis_aro'] == 'tidak':
                print(f" ARO        : TIDAK")
            elif data_deposito['jenis_aro'] == 'pokok':
                print(f" ARO        : POKOK")
            else:
                print(f" ARO        :  POKOK BUNGA")


        while True:
            try:
                pilihan = int(input("Masukkan pilihan Anda ( ketik 0 untuk keluar): "))
            except ValueError:
                UI.gagal("Silakan pilih menggunakan angka")
                continue

            if pilihan == 0:
                return DepositoUI.BATAL

            if pilihan < 1 or pilihan > (len(daftar_deposito)):
                UI.gagal("Pilihan tidak tersedia")
                continue


            return daftar_deposito[pilihan - 1]


    @staticmethod
    def lihat_deposito(nik):
            UI.header("LIHAT DEPOSITO ANDA", UI.MERAH)


            daftar_deposito = (
                DepositoService.cari_deposito_nasabah(nik=nik)
            )

            if not daftar_deposito:
                print("Anda belum melakukan deposito")
                return
            data_deposito = DepositoUI.pilih_deposito(daftar_deposito)

            if data_deposito is DepositoUI.BATAL:
                return


            UI.info_deposito(data_deposito)



    @staticmethod
    def cairkan_deposito(nik, norek):
        UI.header("CAIRKAN DEPOSITO", UI.MERAH)


        daftar_deposito = DepositoService.cari_deposito_jatuh_tempo_dengan_norek(norek=norek)

        if not daftar_deposito:
            print("Belum ada deposito yang jatuh tempo")
            return

        data_deposito = DepositoUI.pilih_deposito(daftar_deposito=daftar_deposito)

        if data_deposito is DepositoUI.BATAL:
            return


        try:
            Utilitas.animasi("Proses")
            total_pencairan = DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=data_deposito['id']
            )

            UI.sukses(
                f"Pencairan berhasil!"
                f" Rp{Utilitas.format_rupiah(total_pencairan)} "
                f"masuk ke rekening {norek}"
            )

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.peringatan(
                f"Terjadi kesalahan saat pencairan deposito. Silakan coba lagi  "
            )






    @staticmethod
    def hentikan_aro(nik, norek):
        UI.header("HENTIKAN ARO DEPOSITO", UI.MERAH)
        UI.info_rekening(norek)

        daftar_deposito = (
            DepositoService.cari_deposito_aro_aktif_dengan_norek(
                norek=norek
            )
        )

        if not daftar_deposito:
            UI.gagal(
                "Rekening ini tidak memiliki deposito ARO aktif"
            )
            return

        data_deposito = DepositoUI.pilih_deposito(
            daftar_deposito=daftar_deposito
        )

        if data_deposito is DepositoUI.BATAL:
            return

        print()
        print(
            "Deposito tetap berjalan hingga jatuh tempo: "
            f"{Utilitas.format_tanggal_indonesia(
                data_deposito['jatuh_tempo']
            )}"
        )
        print(
            "Setelah ARO dihentikan, deposito tidak akan "
            "diperpanjang otomatis."
        )
        print()

        konfirmasi = input(
            "Hentikan ARO deposito ini? (ya/tidak): "
        ).strip().lower()

        if konfirmasi not in ("y", "ya", "iya"):
            UI.gagal("Penghentian ARO dibatalkan")
            return

        try:
            DepositoService.hentikan_aro(
                nik=nik,
                norek_pemberhentian=norek,
                id_deposito=data_deposito["id"]
            )

            UI.sukses(
                f"ARO deposito {data_deposito['id']} berhasil dihentikan"
            )

            print(
                "Deposito tetap aktif hingga "
                f"{Utilitas.format_tanggal_indonesia(
                    data_deposito['jatuh_tempo']
                )}"
            )

        except BankException as e:
            UI.gagal(str(e))

        except sqlite3.Error:
            UI.peringatan("Terjadi kesalahan saat memperbarui status deposito. Silakan coba lagi")





