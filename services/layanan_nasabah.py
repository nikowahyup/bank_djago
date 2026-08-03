from bank_djago.services.transaksi import RiwayatService
from bank_djago.utils.utililty import Utilitas
import time

class LayananNasabah:
    @staticmethod
    def animasi():
        print("Proses", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(1)
        print()

    @staticmethod
    def menu_layanan(bank,nasabah):
        print()
        print(f"👋 Halo {nasabah.nama}!")
        while True:
            try:
                print("="*20,"MENU LAYANAN","="*20)
                print()
                print("1. Lihat Biodata")
                print("2. Lihat Rekening")
                print("3. Ganti Alamat")
                print("4. Ganti PIN")
                print("5. Buka Rekening")
                print('6. Tutup Rekening')
                print("7. Tingkatkan Rekening")
                print('8. Turunkan Rekening')
                print('9. Blokir rekening')
                print('10.Verifikasi Identitas')
                print('11. Keluar')
                print()
                pilihan = int(input("Masukkan pilihan Anda: "))

                if pilihan == 1:
                    LayananNasabah.biodata(nasabah)
                elif pilihan == 2:
                    LayananNasabah.daftar_rekening(nasabah)
                elif pilihan == 3:
                    LayananNasabah.ganti_alamat(nasabah)
                elif pilihan == 4:
                    LayananNasabah.ganti_pin(bank,nasabah)
                elif pilihan == 5:
                    LayananNasabah.buka_rekening(bank,nasabah)
                elif pilihan == 6:
                    LayananNasabah.tutup_rekening(bank,nasabah)
                elif pilihan == 7:
                    LayananNasabah.upgrade_rekening(bank,nasabah)
                elif pilihan == 8:
                    LayananNasabah.downgrade_rekening(bank,nasabah)
                elif pilihan == 9:
                    LayananNasabah.blokir_rekening(bank,nasabah)
                elif pilihan == 10:
                    LayananNasabah.verifikasi_identitas(bank)
                elif pilihan == 11:
                    break
            except ValueError:
                print("❌ Tolong masukkan pilihan yang valid")

    @staticmethod
    def biodata(nasabah):
        print('=' * 15, "BIODATA", '=' * 15)
        print(f"NAMA   : {nasabah.nama}")
        print(f"NIK    : {nasabah.NIK}")
        print(f"ALAMAT : {nasabah.alamat}")
        print('='*39,'\n')

    @staticmethod
    def daftar_rekening(nasabah):
        print('=' * 15, "DAFTAR REKENING", '=' * 15)
        for i,rek in enumerate(nasabah.rekening,1):
            print(f"{i}. {rek.jenis}")
            print(f"💳 Nomor Rekening : {rek.norek}")
            print(f"📃 Status         : {rek.status}")
            print(f"💰 Saldo          : Rp{rek.cek_saldo()}\n")

    @staticmethod
    def ganti_alamat(nasabah):
        print('=' * 15, "GANTI ALAMAT", '=' * 15)

        alamat_lama = input("Masukkan alamat lama Anda: ")
        if alamat_lama != nasabah.alamat:
            print("❌ Alamat tidak cocok")
            return

        alamat_baru = input("Masukkan alamat baru Anda: ")
        nasabah.alamat = alamat_baru
        print("✅ Alamat berhasil diubah!\n")


    @staticmethod
    def ganti_pin(bank,nasabah):
        print('=' * 15, "GANTI PIN", '=' * 15)

        norek = input("Masukkan nomor rekening yang ingin Anda ganti pin: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("❌ Nomor rekening tidak terdaftar")
            return

        if rekening not in nasabah.rekening:
            print("❌ Maaf,rekening tidak terdaftar di akun Anda!")
            return

        pin_lama = input("Masukkan PIN lama: ")
        if not rekening.cek_pin(pin_lama):
            print("❌ PIN salah. Akses tidak diberikan")
            return

        pin_baru = input("Masukkan PIN baru: ")
        rekening.ganti_pin(pin_baru)
        LayananNasabah.animasi()
        print("✅ PIN berhasil diganti!\n")



    @staticmethod
    def buka_rekening(bank,nasabah):
        print('='*24,"BUKA REKENING",'='*24)
        Utilitas.keuntungan_rekening()
        try:
            print()
            pilihan = int(input("Masukkan pilihan Anda: "))
            if pilihan not in bank.jenis_rekening:
                print("❌ Masukkan pilihan yang valid!")
                return

            pin = input("Silahkan buat PIN 6 digit: ")

            if len(pin) != 6 or not pin.isdigit():
                print("❌ PIN tidak valid\n")
                return

            rek_baru = bank.buka_rekening(nasabah,pilihan,pin)
            print()
            LayananNasabah.animasi()
            print(f"✅ Rekening Baru Berhasil Dibuat!")
            print(f"💳 Nomor Rekening : {rek_baru.norek[0:4]}-{rek_baru.norek[4:8]}-{rek_baru.norek[8:12]}-{rek_baru.norek[12:16]}\n")

        except ValueError:
            print("Tolong pilih menggunakan angka")

    @staticmethod
    def tutup_rekening(bank,nasabah):
        print('='*15,"TUTUP REKENING",'='*15)
        print()
        print("    ==============INFORMASI===============")
        print("""       Sebelum Anda membekukan rekening
      Harap pastikan saldo dalam rekening 
        telah kosong. Terima Kasih""")
        print()
        norek = input("Masukkan nomor rekening yang ingin Anda tutup: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("❌ Nomor rekening tidak terdaftar\n")
            return

        if rekening not in nasabah.rekening:
            print("❌ Nomor rekening tidak terdaftar di akun Anda!\n")
            return

        if rekening.saldo > 0:
            print(f'❌ Rekening masih memiliki Rp{Utilitas.format_rupiah(rekening.saldo)}')
            print(f'Silahkan tarik atau transfer terlebih dahulu\n')

        print("="*15,"PILIHAN PENGOSONGAN","="*15)
        print('1. Transfer Saldo')
        print('2. Tarik Tunai')
        pilihan = input("Masukkan pilihan Anda(ketik cancel untuk pembatalan): ").lower()
        print()
        if bank.tutup_rekening(rekening,pilihan):
            LayananNasabah.animasi()
            print("✅ Rekening telah ditutup")
            print("🙏 Terima kasih telah mempercayai Bank Djago!")

    @staticmethod
    def upgrade_rekening(bank,nasabah):
        print("="*15,"TINGKATKAN REKENING","="*15)
        info = bank.jenis_rekening
        norek = input("Masukkan nomor rekening yang ingin Anda tingkatkan: ")
        print()
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("Nomor rekening tidak terdaftar")
            return
        if rekening not in nasabah.rekening:
            print("Nomor rekening tidak terdaftar di akun Anda")
            return
        print("✅ Rekening Ditemukan!")
        print(f"💎 Rekening {rekening.jenis}")
        print(f"💳 Nomor rekening {rekening.norek}")
        print(f"💰 Saldo Rp{rekening.cek_saldo()}\n")

        if rekening.level == 4:
            print("Rekening Anda sudah platinum!")
            return

        if rekening.level == 1:
            print(f"Mau tingkatkan rekening Anda ke rekening mana? ")
            print( f"1. {info[rekening.level+1]["nama"]}")
            print( f"2. {info[rekening.level+2]["nama"]}")
            print( f"3. {info[rekening.level+3]["nama"]}")
            upgrade = int(input("Masukkan pilihan Anda: "))
            konfirmasi = input("Konfirmasi perubahan rekening(ya/tidak): ").lower()

            level_up = rekening.level + upgrade
            if konfirmasi in ('y','ya','iya'):
                LayananNasabah.animasi()
                if bank.upgrade_rekening(nasabah,rekening,level_up):

                    print("✅ Peningkatan Berhasil!")
                    print(f"Rekening telah ditingkatkan ke {info[rekening.level+upgrade]["nama"]}!")
                    log = RiwayatService.upgrade_rekening(sebelum=info[rekening.level]["nama"],sesudah=info[rekening.level+upgrade]["nama"])
                    rekening.simpan_riwayat(log)
                else:
                    print("❌ Peningkatan Gagal!")
                    print(f"Saldo akun Anda tidak mencukupi saldo minimum rekening {info[rekening.level+upgrade]["nama"]}")
                    rupiah = info[rekening.level+upgrade]["minimal_upgrade"]
                    print(f"⚠️ Minimum saldo Rp{Utilitas.format_rupiah(rupiah)}")


        elif rekening.level == 2:
            print(f"Mau tingkatkan rekening Anda ke rekening mana? ")
            print( f"1. {info[rekening.level+1]["nama"]}")
            print( f"2. {info[rekening.level+2]["nama"]}")
            upgrade = int(input("Masukkan pilihan Anda: "))
            konfirmasi = input("Konfirmasi perubahan rekening(ya/tidak): ").lower()

            level_up = rekening.level + upgrade
            if konfirmasi in ('y','ya','iya'):
                LayananNasabah.animasi()
                if bank.upgrade_rekening(nasabah,rekening,level_up):
                    print("✅ Peningkatan Berhasil!")
                    print(f"Rekening telah ditingkatkan ke {info[rekening.level+upgrade]["nama"]}!")
                    log = RiwayatService.upgrade_rekening(sebelum=info[rekening.level]["nama"],sesudah=info[rekening.level+upgrade]["nama"])
                    rekening.simpan_riwayat(log)
                else:
                    print("❌ Peningkatan Gagal!")
                    print(f"Saldo akun Anda tidak mencukupi saldo minimum rekening {info[rekening.level+upgrade]["nama"]}")
                    rupiah = info[rekening.level+upgrade]["minimal_upgrade"]
                    print(f"⚠️ Minimum saldo Rp{Utilitas.format_rupiah(rupiah)}")

        elif rekening.level == 3:
            print("Rekening Anda sekarang Gold. Mau tingkatkan ke platiinum?")
            konfirmasi = input("Konfirmasi perubahan rekening(ya/tidak): ").lower()
            if konfirmasi in ('y','ya','iya'):
                upgrade = 1
                level_up = rekening.level + upgrade
                LayananNasabah.animasi()
                if bank.upgrade_rekening(nasabah,rekening,level_up):
                    print("✅ Peningkatan Berhasil!")
                    print(f"Rekening telah ditingkatkan ke platinum!")
                    log = RiwayatService.upgrade_rekening(sebelum=info[rekening.level]["nama"],sesudah=info[rekening.level+upgrade]["nama"])
                    rekening.simpan_riwayat(log)
                else:
                    print("❌ Peningkatan Gagal!")
                    print(
                            f"Saldo akun Anda tidak mencukupi saldo minimum rekening platinum")
                    rupiah = info[rekening.level + upgrade]["minimal_upgrade"]
                    print(f"⚠️ Minimum saldo Rp{Utilitas.format_rupiah(rupiah)}")

    @staticmethod
    def blokir_rekening(bank,nasabah):
        print("="*15,"BLOKIR REKENING","="*15)
        norek = input("Masukkan nomor rekening yang ingin Anda blokir: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("Nomor rekening tidak terdaftar!")
            return
        if rekening not in nasabah.rekening:
            print("Nomor rekening tidak terdaftar di akun Anda")
            return
        alasan = input("Masukkan alasan pemblokiran rekening: ")
        if bank.blokir_rekening(rekening,alasan):
            LayananNasabah.animasi()
            print(f"✅ Rekening dengan nomor {rekening.norek} berhasil diblokir!")

    @staticmethod
    def verifikasi_identitas(bank):
        nik = input("Masukkan NIK Anda: ")
        if nik not in bank.data_nasabah:
            print("❌ Maaf,Anda tidak terdaftar dalam nasabah")
            return
        nasabah = bank.data_nasabah[nik]
        nama = input("Masukkan nama lengkap Anda: ").title()
        if nasabah.nama != nama:
            print("❌ Nama tidak cocok dengan NIK yang terdaftar")
            return
        print(f"👋 Halo,{nama}!")
        norek = input("Masukkan nomor rekening Anda: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("❌ Nomor rekening tidak terdaftar!")
            return
        if rekening not in nasabah.rekening:
            print("❌ Nomor rekening ini tidak terdaftar di akun Anda")
            return
        pin = input("Masukkan PIN lama Anda: ")
        if not rekening.cek_pin(pin):
            print("❌ PIN salah")
            return
        print()
        print("✅ Rekening ditemukan!")
        print(f"💳 Nomor rekening : {rekening.norek}")
        print(f"📃 Status         : {rekening.status}")
        print(f"⚠️ Alasan         : {rekening.alasan_blokir}")
        print()
        buka = input("Mau buka rekening ini(ya/tidak)? ")
        if rekening.status == "aktif":
            print("Rekening ini memang sudah aktif!")
            return
        if buka in ('y','iya','ya'):
            rekening.status = "aktif"
            print()
            LayananNasabah.animasi()
            print("✅ Rekening telah diaktifkan kembali!")
            print("Jaga rekening Anda dengan baik ya")
            return

        elif buka in ("t",'no','tidak'):
            return

        else:
            print("Tolong pilih ya atau tidak")

    @staticmethod
    def downgrade_rekening(bank,nasabah):
        print("="*15,"TURUNKAN REKENING","="*15)

        info = bank.jenis_rekening
        norek = input("Masukkan nomor rekening yang ingin Anda turunkan: ")
        print()
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("Nomor rekening tidak terdaftar")
            return
        if rekening not in nasabah.rekening:
            print("Nomor rekening tidak terdaftar di akun Anda")
            return
        print("✅ Rekening Ditemukan!")
        print(f"💎 Rekening {rekening.jenis}")
        print(f"💳 Nomor rekening {rekening.norek}")
        print(f"💰 Saldo Rp{rekening.cek_saldo()}\n")

        if rekening.level == 1:
            print("Saat ini rekening Anda sudah reguler!")
            return

        if rekening.level == 4:
            print(f"Mau turunkan rekening Anda ke rekening mana? ")
            print( f"1. {info[rekening.level-1]["nama"]}")
            print( f"2. {info[rekening.level-2]["nama"]}")
            print( f"3. {info[rekening.level-3]["nama"]}")
            downgrade = int(input("Masukkan pilihan Anda: "))
            konfirmasi = input("Konfirmasi perubahan rekening(ya/tidak): ").lower()

            turun = rekening.level - downgrade
            if konfirmasi in ('y','ya','iya'):
                LayananNasabah.animasi()
                if bank.downgrade_rekening(nasabah,rekening,turun):
                    print("✅ Penurunan Berhasil!")
                    print(f"Rekening telah diturunkan ke {info[rekening.level-downgrade]["nama"]}!")
                    log = RiwayatService.downgrade_rekening(sebelum=info[rekening.level]["nama"],sesudah=info[rekening.level-downgrade]["nama"])
                    rekening.simpan_riwayat(log)

        if rekening.level == 3:
            print(f"Mau turunkan rekening Anda ke rekening mana? ")
            print(f"1. {info[rekening.level - 1]["nama"]}")
            print(f"2. {info[rekening.level - 2]["nama"]}")
            downgrade = int(input("Masukkan pilihan Anda: "))
            konfirmasi = input("Konfirmasi perubahan rekening(ya/tidak): ").lower()

            turun = rekening.level - downgrade
            if konfirmasi in ('y', 'ya', 'iya'):
                LayananNasabah.animasi()
                if bank.downgrade_rekening(nasabah, rekening, turun):
                    print("✅ Penurunan Berhasil!")
                    print(f"Rekening telah diturunkan ke {info[rekening.level - downgrade]["nama"]}!")
                    log = RiwayatService.downgrade_rekening(sebelum=info[rekening.level]["nama"],
                                                            sesudah=info[rekening.level - downgrade]["nama"])
                    rekening.simpan_riwayat(log)

        if rekening.level == 2:
            print("Mau turunkan ke reguler?")
            konfirmasi = input("Konfirmasi perubahan rekening(ya/tidak): ").lower()
            if konfirmasi in ('y', 'ya', 'iya'):
                LayananNasabah.animasi()
                turun = 1
                if bank.downgrade_rekening(nasabah, rekening, turun):
                    print("✅ Penurunan Berhasil!")
                    print(f"Rekening telah diturunkan ke {info[rekening.level - turun]["nama"]}!")
                    log = RiwayatService.downgrade_rekening(sebelum=info[rekening.level]["nama"],
                                                            sesudah=info[rekening.level - turun]["nama"])
                    rekening.simpan_riwayat(log)







