

from bank_djago.services.deposito.deposito_service import DepositoService, JenisAro
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas



class DepositoUI:

    @staticmethod
    def menu(bank):
        while True:
            UI.header("DEPOSITO",UI.KUNING)
            print("1. Lihat Deposito Anda")
            print("2. Cairkan Deposito")
            print("3. Buka Deposito")
            print("4. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                DepositoUI.lihat_deposito(bank)
            elif pilihan == "2":
                 DepositoUI.cairkan_deposito(bank)
            elif pilihan == "3":
                DepositoUI.buka_deposito(bank)
            elif pilihan == "4":
                break



    @staticmethod
    def lihat_deposito(bank):
            UI.header("LIHAT DEPOSITO ANDA", UI.MERAH)
            print()
            nik = input("Masukkan NIK Anda: ")
            Utilitas.animasi("Mencari nasabah")
            nasabah = bank.cari_nasabah(nik)
            if not nasabah:
                print("NIK tidak terdaftar")
                return

            deposito = nasabah.deposito

            if not deposito:
                print("Anda belum melakukan deposito")
                return

            for i, daftar in enumerate(deposito, start=1):
                print(
                    f"{i}. Rp{Utilitas.format_rupiah(daftar.nominal)}"
                    f" | Waktu {daftar.lama_bulan} bulan"
                    f" | Status {daftar.status}"
                )

            try:
                pilihan = int(input("Masukkan pilihan Anda: "))

                if pilihan < 1 or pilihan > len(deposito):
                    print("Pilihan tidak tersedia")
                    return

            except ValueError:
                print("Masukkan nomor pilihan yang valid")
                return

            depo = deposito[pilihan - 1]

            UI.info_deposito(depo)



    @staticmethod
    def cairkan_deposito(bank):
        UI.header("CAIRKAN DEPOSITO", UI.MERAH)
        print()
        nik = input("Masukkan NIK Anda: ")
        Utilitas.animasi("Mencari nasabah")
        nasabah = bank.cari_nasabah(nik)
        if not nasabah:
            print("NIK tidak terdaftar")
            return

        deposito = nasabah.deposito

        if not deposito:
            print("Anda belum melakukan deposito")
            return

        for i, daftar in enumerate(deposito, start=1):
            print(
                f"{i}. Rp{Utilitas.format_rupiah(daftar.nominal)}"
                f" | Waktu {daftar.lama_bulan} bulan"
                f" | Status {daftar.status}"
            )

        try:
            pilihan = int(input("Masukkan pilihan Anda: "))

        except ValueError:
            print("Masukkan nomor pilihan yang valid")
            return
        if pilihan < 1 or pilihan > len(deposito):
            print("Pilihan tidak tersedia")
            return

        try:
            Utilitas.animasi("Proses")
            depo = deposito[pilihan - 1]
            total_deposito = DepositoService.cairkan_deposito(bank,depo)
            UI.sukses(f"Pencairan berhasil! Rp{Utilitas.format_rupiah(total_deposito)} masuk ke rekening Anda")
        except ValueError as e:
            UI.gagal(str(e))


    @staticmethod
    def buka_deposito(bank):
        UI.header("BUKA DEPOSITO", UI.MERAH)
        print()
        nik = input("Masukkan NIK Anda: ")
        Utilitas.animasi("Mencari nasabah")
        nasabah = bank.cari_nasabah(nik)
        if not nasabah:
            print("NIK tidak terdaftar")
            return

        try:
            norek = input("Masukkan nomor rekening Anda: ")
            pin = input("Masukkan PIN Anda: ")
            Utilitas.animasi("Mencari rekening")
            rekening = bank.autentikasi_rekening(norek,pin)
            if rekening not in nasabah.rekening:
                raise ValueError("Rekening ini bukan milik Anda")
            UI.sukses("Rekening ditemukan")
            UI.wadah_info(rekening.pemilik.nama,norek,rekening.cek_saldo())
        except ValueError as e:
            UI.gagal(str(e))
            return

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
            Utilitas.animasi("Membuka deposito")
            jenis_aro,lama_aro = DepositoUI.tanya_aro()
            DepositoService.buka_deposito(bank,rekening,nominal,lama_bulan,jenis_aro,lama_aro)
            UI.sukses("Deposito berhasil dibuka!")
        except ValueError as e:
            UI.gagal(str(e))


    @staticmethod
    def tanya_aro():
        print("\n=== PERPANJANGAN DEPOSITO ===")
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

                return jenis_aro, lama_aro

            except ValueError:
                print("Masukkan angka yang valid.")




