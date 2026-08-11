from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas
from bank_djago.utils.validator import Validator



class RekeningUI:
    level = {1: 'Reguler',
             2: 'Prioritas',
             3: 'Gold',
             4: 'Platinum'}
    @staticmethod
    def menu(bank,rekening):

        while True:
            UI.header("MENU LAYANAN REKENING", UI.KUNING)
            print()
            print("1. Tingkatkan Rekening")
            print("2. Turunkan Rekening")
            print("3. Blokir Rekening")
            print("4. Buka Blokir")
            print("5. Tutup Rekening")
            print("6. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                RekeningUI.upgrade_rekening(bank, rekening)
            elif pilihan == "2":
                RekeningUI.downgrade_rekening(bank, rekening)
            elif pilihan == "3":
                RekeningUI.blokir_rekening(rekening)
            elif pilihan == "4":
                RekeningUI.buka_blokir(rekening)
            elif pilihan == "5":
                RekeningUI.tutup_rekening(bank,rekening)
            elif pilihan == "6":
                break


    @staticmethod
    def upgrade_rekening(bank,rekening):
        UI.header("TINGKATKAN REKENING",UI.MERAH)
        print()
        if rekening.level == 4:
            print("Rekening ini sudah platinum")
            return
        print("Mau tingkatkan ke mana: ")
        opsi = list(range(rekening.level+1,5))
        while True:
            for i in opsi:
                print(f"{i}. {RekeningUI.level[i]}")
            try:
                pilihan = int(input("Masukkan pilihan: "))
            except ValueError:
                print("Tolong masukkan angka")
                continue
            if pilihan not in opsi:
                print("Pilihan tidak valid")
                continue

            break

        try:
            RekeningService.upgrade_rekening(bank,rekening,pilihan)
            UI.sukses('Peningkatan Sukses!')
            UI.sukses(f"Rekening telah ditingkatkan ke {RekeningUI.level[pilihan]}")
        except ValueError as e:
            UI.gagal("Peningkatan Gagal")
            UI.gagal(str(e))


    @staticmethod
    def downgrade_rekening(bank,rekening):
        UI.header("TURUNKAN REKENING",UI.MERAH)

        print(f"Rekening saat ini : {RekeningUI.level[rekening.level]}")
        if rekening.level == 1:
            print("Rekening sudah reguler")
            return
        while True:
            print("Mau turunkan ke mana: ")
            opsi = list(range(1,rekening.level))
            for i in opsi:
                print(f"{i}. {RekeningUI.level[i]}")
            try:
                pilihan = int(input("Masukkan pilihan: "))
            except ValueError:
                print("Tolong masukkan angka")
                continue
            if pilihan not in opsi:
                print("Pilihan tidak valid")
                continue

            break

        try:
            RekeningService.downgrade_rekening(bank,rekening,pilihan)
            UI.sukses('Penurunan Sukses!')
            UI.sukses(f"Rekening telah diturunkan ke {RekeningUI.level[pilihan]}")
        except ValueError as e:
            UI.gagal("Penurunan Gagal!")
            UI.gagal(str(e))

    @staticmethod
    def blokir_rekening(rekening):
        UI.header("BLOKIR REKENING",UI.MERAH)

        alasan = input("Masukkan alasan pemblokiran: ")

        try:
            RekeningService.blokir_rekening(rekening,alasan)
            UI.sukses(f"Rekening dengan nomor {rekening.norek} berhasil diblokir")
        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def buka_blokir(rekening):
        UI.header("BUKA BLOKIR REKENING",UI.MERAH)

        konfirmasi = input("Apakah Anda yakin ingin membuka kembali rekening ini(ya/tidak): ").lower()
        if konfirmasi not in('ya','y','iya'):
            return
        try:
            RekeningService.buka_blokir(rekening)
            UI.sukses(f"Rekening dengan nomor {rekening.norek} berhasil dibuka kembali")
        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def reset_pin(bank,rekening):
        UI.header("RESET PIN REKENING",UI.MERAH)

        pin = input("Masukkan PIN baru: ")
        Utilitas.animasi('Proses')
        if pin == rekening.pin:
            return
        rekening.reset_pin()
        UI.sukses("PIN berhasil direset dan diganti")
        AuditService.tambah_audit(bank,"rekening",jenis="reset pin",log=f"{rekening.pemilik.nama} meminta reset pin pada rekeningnya",norek=rekening.norek)

    @staticmethod
    def tutup_rekening(bank,rekening):
        UI.header("TUTUP REKENING",UI.MERAH)
        if rekening.saldo > 0:
            print(f"Masih ada saldo Rp{rekening.cek_saldo()}. Harus dikosongkan sebelum ditutup")
            print("Pilih cara pengosongan rekening")
            print("1. Tarik seluruh saldo")
            print("2. Transfer ke rekening lain")
            print()
            try:

                pilihan = input("Pilihan Anda: ")
                if pilihan == "1":
                    konfirmasi = input("Apakah Anda yakin(ya/tidak):").lower()
                    if konfirmasi not in ('iya','ya','y'):
                        return
                    RekeningService.tutup_rekening(rekening)
                    UI.sukses(f"Rekening dengan nomor {rekening.norek} telah ditutup!")
                elif pilihan == "2":
                    rek_penerima = input("Masukkan nomor rekening penerima: ")
                    konfirmasi = input("Apakah Anda yakin(ya/tidak):").lower()
                    if konfirmasi not in ('iya','ya','y'):
                        return

                    saldo = rekening.saldo
                    penerima = TransaksiService.cari_penerima(bank,rek_penerima,rekening)
                    RekeningService.tutup_rekening(rekening, penerima)
                    UI.sukses(f"Rp{Utilitas.format_rupiah(saldo)} telah masuk ke rekening {penerima.pemilik.nama}")
                    UI.sukses(f"Rekening dengan nomor {rekening.norek} telah ditutup!")

            except ValueError as e:
                UI.gagal(str(e))


    @staticmethod
    def buka_rekening(bank):
        while True:
            print()
            UI.header("SIAPA ANDA?")
            print()
            print("1. Nasabah Baru")
            print("2. Nasabah Lama")
            print("3. Kembali\n")

            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                while True:
                    nama   = input("Masukkan nama lengkap Anda: ")
                    nik    = input("Masukkan NIK Anda: ")
                    alamat = input("Masukkan alamat Anda: ")
                    pin    = input("Silahkah Buat PIN 6 digit: ")
                    Utilitas.animasi("Memeriksa data")
                    print()
                    try:
                        Validator.validasi_nasabah(nama,nik,alamat, pin)
                    except ValueError as e:
                        for pesan in e.args[0]:
                            print(f"❌", pesan)
                        continue
                    break
                print()
                Utilitas.keuntungan_rekening()
                while True:
                    try:
                        print()
                        pilihan = int(input("Masukkan pilihan Anda: "))
                        if pilihan not in(1,2,3,4):
                            UI.gagal("Tolong pilih pilihan yang tersedia")
                            continue
                    except ValueError:
                        print(f"Silahkan masukkan pilihan yang valid")
                        continue
                    break

                try:
                    UI.peringatan("Anda wajib menyetorkan uang setoran awal")
                    setor_awal = int(input("Masukkan nominal: "))
                    Utilitas.animasi('Proses')
                except ValueError:
                    UI.gagal("Masukkan angka yang valid.")

                try:
                    nasabah_baru,rekening_baru = bank.daftar_nasabah(nama,nik,alamat,pin,pilihan,setor_awal)
                    Utilitas.sapaan(nasabah_baru,rekening_baru)
                    log = RiwayatTemplate.setor_uang(setor_awal)
                    rekening_baru.simpan_riwayat(log)
                    AuditService.tambah_audit(bank,kategori="rekening", jenis="buka rekening",log=f"{nasabah_baru.nama} membuka rekening pertama", nik=nasabah_baru.NIK,norek=rekening_baru.norek)
                    AuditService.tambah_audit(bank,kategori="nasabah", jenis="daftar", log="Pendaftaran Menjadi Nasabah Bank Djago",nama=nasabah_baru.nama,nik=nasabah_baru.NIK)

                except ValueError as e:
                    UI.gagal(str(e))


            elif pilihan == "2":

                while True:
                    nik = input("Masukkan NIK Anda: ")
                    Utilitas.animasi("Mencari nasabah")
                    nasabah = bank.cari_nasabah(nik)
                    if not nasabah:
                        UI.gagal("NIK belum terdaftar")
                        continue
                    break

                print(f"Halo,{nasabah.nama}!")

                Utilitas.keuntungan_rekening()

                while True:
                    print()
                    try:
                        pilihan = int(input("Masukkan pilihan Anda: "))
                        if pilihan not in(1,2,3,4):
                            UI.gagal("Tolong pilih pilihan yang tersedia")
                            continue
                    except ValueError:
                        UI.peringatan("Silahkan masukkan pilihan memakai angka")
                        continue
                    break

                while True:
                    pin = input("Silahkan buat PIN 6 digit angka: ")
                    try:
                        Validator.validasi_pin(pin)
                    except ValueError as e:
                        UI.gagal(str(e))
                        continue
                    break
                try:
                    UI.peringatan("Anda wajib menyetorkan uang setoran awal")
                    setor_awal = int(input("Masukkan nominal: "))
                    Utilitas.animasi("Proses")

                except ValueError:
                    UI.gagal("Masukkan angka yang valid.")

                try:
                    rekening_baru = RekeningService.buka_rekening(bank,nasabah,pilihan,pin,setor_awal)
                    print(f"Selamat! Rekening dengan nomor {rekening_baru.norek} telah dibuka!")
                    AuditService.tambah_audit(bank,kategori="rekening",jenis="buka",log=f"{nasabah.nama} membuka rekening lain",nik=nasabah.NIK,norek=rekening_baru.norek)
                except ValueError as e:
                    UI.gagal(str(e))

            elif pilihan == "3":
                break

            else:
                UI.gagal("Pilih opsi yang valid!")

