from bank_djago.utils.ui import UI


class LayananNasabah:



    @staticmethod
    def menu_profil(nasabah, rekening):
        while True:
                UI.header("MENU PROFIL", UI.KUNING)
                print()
                print("1. Lihat Biodata")
                print("2. Lihat Daftar Rekening")
                print("3. Ubah PIN")
                print("4. Keluar\n")
                pilihan = input("Masukkan pilihan Anda: ")
                if pilihan == "1":
                    LayananNasabah.biodata(nasabah)
                elif pilihan == "2":
                    LayananNasabah.daftar_rekening(nasabah)
                elif pilihan == "3":
                    LayananNasabah.ganti_pin(rekening)
                elif pilihan == "4":
                    break


    @staticmethod
    def biodata(nasabah):
        UI.header("BIODATA ANDA",UI.MERAH)
        print()
        print('='*39,)
        print(f"NAMA   : {nasabah.nama}")
        print(f"NIK    : {nasabah.NIK}")
        print(f"ALAMAT : {nasabah.alamat}")
        print('='*39,'\n')

    @staticmethod
    def daftar_rekening(nasabah):
        UI.header("DAFTAR REKENING ANDA",UI.MERAH)
        print()
        for i,rek in enumerate(nasabah.rekening,1):
            print(f"{i}. {rek.jenis}")
            print(f"💳 Nomor Rekening : {rek.norek}")
            print(f"📃 Status         : {rek.status}")
            print(f"💰 Saldo          : Rp{rek.cek_saldo()}\n")

    @staticmethod
    def ganti_alamat(nasabah):
        UI.header("GANTI ALAMAT",UI.MERAH)
        print()
        alamat_lama = input("Masukkan alamat lama Anda: ")
        if alamat_lama != nasabah.alamat:
            UI.gagal("Alamat tidak cocok")
            return

        alamat_baru = input("Masukkan alamat baru Anda: ")
        nasabah.alamat = alamat_baru
        UI.sukses("Alamat berhasil diubah!\n")


    @staticmethod
    def ganti_pin(rekening):
        UI.header("GANTI PIN",UI.MERAH)


        pin_lama = input("Masukkan PIN lama: ")
        if not rekening.cek_pin(pin_lama):
            UI.gagal("PIN salah. Akses tidak diberikan")
            return

        pin_baru = input("Masukkan PIN baru: ")
        rekening.ganti_pin(pin_baru)

        UI.sukses("PIN berhasil diganti!\n")

















