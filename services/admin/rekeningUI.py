from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
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
            print("5. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                RekeningUI.upgrade_rekening(bank, rekening)
            elif pilihan == "2":
                RekeningUI.downgrade_rekening(bank, rekening)
            elif pilihan == "3":
                RekeningUI.blokir_rekening(bank, rekening)
            elif pilihan == "4":
                RekeningUI.buka_blokir(bank, rekening)
            elif pilihan == "5":
                break


    @staticmethod
    def upgrade_rekening(bank,rekening):
        UI.header("TINGKATKAN REKENING",UI.MERAH)
        print()
        if rekening.level == 4:
            print("Rekening sudah platinum")
            return
        print("Mau tingkatkan ke mana: ")
        opsi = list(range(rekening.level+1,5))
        for i in opsi:
            print(f"{i}. {RekeningUI.level[i]}")
        try:
            pilihan = int(input("Masukkan pilihan: "))
        except ValueError:
            print("Tolong masukkan angka")
            return
        if pilihan not in opsi:
            print("Pilihan tidak valid")
            return
        Utilitas.animasi("Proses")
        rek_awal      = RekeningUI.level[rekening.level]
        rek_tujuan    = RekeningUI.level[pilihan]
        rekening_baru = bank.upgrade_rekening(rekening,pilihan)
        if rekening_baru:
            log = RiwayatTemplate.upgrade_rekening(sebelum=rek_awal,sesudah=rek_tujuan)
            UI.sukses('Peningkatan Sukses!')
            print(f"Rekening telah ditingkatkan ke {RekeningUI.level[pilihan]}")
            AuditService.tambah_audit(bank,"rekening",jenis="upgrade",log=f"{rekening.pemilik.nama} mengubah rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
            rekening_baru.simpan_riwayat(log)
        else:
            UI.gagal("Upgrade Gagal!")
            print(f"Saldo tidak memenuhi saldo minimum rekening {rek_tujuan}")


    @staticmethod
    def downgrade_rekening(bank,rekening):
        UI.header("TURUNKAN REKENING",UI.MERAH)

        print(f"Rekening saat ini : {RekeningUI.level[rekening.level]}")
        if rekening.level == 1:
            print("Rekening sudah reguler")
            return

        print("Mau turunkan ke mana: ")
        opsi = list(range(1,rekening.level))
        for i in opsi:
            print(f"{i}. {RekeningUI.level[i]}")
        try:
            pilihan = int(input("Masukkan pilihan: "))
        except ValueError:
            print("Tolong masukkan angka")
            return
        if pilihan not in opsi:
            print("Pilihan tidak valid")
            return
        Utilitas.animasi("Proses")
        rek_awal      = RekeningUI.level[rekening.level]
        rek_tujuan    = RekeningUI.level[pilihan]
        rekening_baru = bank.upgrade_rekening(rekening,pilihan)
        if rekening_baru:
            log = RiwayatTemplate.upgrade_rekening(sebelum=rek_awal,sesudah=rek_tujuan)
            UI.sukses('Penurunan Sukses!')
            print(f"Rekening telah diturunkan ke {RekeningUI.level[pilihan]}")
            AuditService.tambah_audit(bank,kategori="rekening",jenis="downgrade",log=f"{rekening.pemilik.nama} mengubah rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
            rekening_baru.simpan_riwayat(log)

    @staticmethod
    def blokir_rekening(bank,rekening):
        UI.header("BLOKIR REKENING",UI.MERAH)
        UI.wadah_info(rekening.pemilik.nama,rekening.norek,rekening.cek_saldo())
        alasan = input("Masukkan alasan pemblokiran: ")
        Utilitas.animasi("Proses")
        if bank.blokir_rekening(rekening,alasan):
            print(f"Rekening dengan nomor {rekening.norek} berhasil diblokir")
            AuditService.tambah_audit(bank,kategori="rekening", jenis="blokir",log=f"{rekening.pemilik.nama} meminta memblokir rekeningnya",norek=rekening.norek)
        else:
            UI.gagal("Rekening ini telah ditutup!")

    @staticmethod
    def buka_blokir(bank,rekening):
        UI.header("BUKA BLOKIR REKENING",UI.MERAH)

        UI.wadah_info(rekening.pemilik.nama,rekening.norek,rekening.cek_saldo())
        Utilitas.animasi("Proses")
        if bank.buka_blokir(rekening):
            print(f"Rekening dengan nomor {rekening.norek} berhasil dibuka kembali")
            AuditService.tambah_audit(bank,kategori="rekening",jenis="buka blokir",log=f"Rekening milik {rekening.pemilik.nama} dibuka kembali",norek=rekening.norek)
        else:
            UI.gagal("Rekening ini telah ditutup!")

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
            print("1. Transfer ke rekening lain")
            print("2. Tarik seluruh saldo")
            pilihan = input("Pilihan: ")
            Utilitas.animasi("Proses")
            bank.tutup_rekening(rekening,pilihan)
            UI.sukses(f"Rekening dengan nomor {rekening.norek} telah ditutup!")
            AuditService.tambah_audit(bank,kategori="rekening",jenis="tutup",log=f"Rekening bernomor {rekening.norek} milik {rekening.pemilik.nama} telah ditutup")

    @staticmethod
    def template_surat(jenis,syarat):
        print('='*50)
        print()
        print("LAYANAN CUSTOMER SERVICE".center(50))
        print()
        print("Layanan yang Dipilih:")
        print(f"{jenis}\n")
        print("Persyaratan: ")
        for item in syarat:
            print(f"• {item}")
        print()
        print("Estimasi Proses:")
        print("± 10 menit")
        print()
        print("Silahkan mengambil nomor antrean Customer Service\n")
        print('='*50)


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
                nama   = input("Masukkan nama lengkap Anda: ")
                nik    = input("Masukkan NIK Anda: ")
                alamat = input("Masukkan alamat Anda: ")
                pin    = input("Silahkah Buat PIN 6 digit: ")
                Utilitas.animasi("Memeriksa data")
                try:
                    Validator.validasi_nasabah(nama,nik,alamat, pin)
                except ValueError as e:
                    for pesan in e.args[0]:
                        print(f"❌", pesan)
                    return

                Utilitas.keuntungan_rekening()
                try:
                    print()
                    pilihan = int(input("Masukkan pilihan Anda: "))
                    if pilihan not in(1,2,3,4):
                        UI.gagal("Tolong pilih pilihan yang tersedia")
                        return

                    UI.peringatan("Anda wajib menyetorkan uang setoran awal")
                    setor_awal = int(input("Masukkan nominal: "))
                    Utilitas.animasi('Proses')

                except ValueError:
                    UI.gagal("Masukkan angka yang valid.")
                    return

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

                nik = input("Masukkan NIK Anda: ")
                Utilitas.animasi("Mencari nasabah")
                nasabah = bank.cari_nasabah(nik)
                if not nasabah:
                    UI.gagal("NIK tidak terdaftar. Silahkan pilih Opsi nasabah baru")
                    return
                print(f"Halo,{nasabah.nama}!")
                Utilitas.keuntungan_rekening()
                try:
                    print()
                    pilihan = int(input("Masukkan pilihan Anda: "))
                    if pilihan not in(1,2,3,4):
                        UI.gagal("Tolong pilih pilihan yang tersedia")
                        return
                    pin = input("Silahkan buat PIN 6 digit angka: ")
                    try:
                        Validator.validasi_pin(pin)
                    except ValueError as e:
                        UI.gagal(str(e))
                        return

                    UI.peringatan("Anda wajib menyetorkan uang setoran awal")
                    setor_awal = int(input("Masukkan nominal: "))
                    Utilitas.animasi("Proses")

                except ValueError:
                    UI.gagal("Masukkan angka yang valid.")
                    return

                try:
                    rekening_baru = bank.buka_rekening(nasabah,pilihan,pin,setor_awal)
                    print(f"Selamat! Rekening dengan nomor {rekening_baru.norek} telah dibuka!")
                    AuditService.tambah_audit(bank,kategori="rekening",jenis="buka",log=f"{nasabah.nama} membuka rekening lain",nik=nasabah.NIK,norek=rekening_baru.norek)
                except ValueError as e:
                    UI.gagal(str(e))

            elif pilihan == "3":
                break

            else:
                UI.gagal("Pilih opsi yang valid!")

