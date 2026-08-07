from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas
from bank_djago.utils.validator import Validator



class AdminCs:
    level = {1: 'Reguler',
             2: 'Prioritas',
             3: 'Gold',
             4: 'Platinum'}
    @staticmethod
    def menu(bank):
        while True:
            UI.header("MENU CUSTOMER SERVICE")
            print()
            Utilitas.menu_cs()
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                AdminCs.buka_rekening(bank)
            elif pilihan == "2":
                AdminCs.upgrade_rekening(bank)
            elif pilihan == "3":
                AdminCs.downgrade_rekening(bank)
            elif pilihan == "4":
                AdminCs.blokir_rekening(bank)
            elif pilihan == "5":
                AdminCs.buka_blokir(bank)
            elif pilihan == "6":
                AdminCs.reset_pin(bank)
            elif pilihan == "7":
                AdminCs.tutup_rekening(bank)
            elif pilihan == "8":
                break



    @staticmethod
    def upgrade_rekening(bank):
        norek    = input("Masukkan nomor rekening: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            return
        UI.sukses("Rekening ditemukan!")
        print(f"Rekening saat ini : {AdminCs.level[rekening.level]}")
        if rekening.level == 4:
            print("Rekening sudah platinum")
            return

        print("Mau Upgrade ke mana: ")
        opsi = list(range(rekening.level+1,5))
        for i in opsi:
            print(f"{i}. {AdminCs.level[i]}")
        try:
            pilihan = int(input("Masukkan pilihan: "))
        except ValueError:
            print("Tolong masukkan angka")
            return
        if pilihan not in opsi:
            print("Pilihan tidak valid")
            return
        rek_awal      = AdminCs.level[rekening.level]
        rek_tujuan    = AdminCs.level[pilihan]
        rekening_baru = bank.upgrade_rekening(rekening,pilihan)
        if rekening_baru:
            log = RiwayatTemplate.upgrade_rekening(sebelum=rek_awal,sesudah=rek_tujuan)
            UI.sukses('Peningkatan Sukses!')
            print(f"Rekening telah ditingkatkan ke {AdminCs.level[pilihan]}")
            AuditService.tambah_audit(bank,"rekening",jenis="upgrade",log=f"{rekening.pemilik.nama} mengubah rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
            rekening_baru.simpan_riwayat(log)
        else:
            UI.gagal("Upgrade Gagal!")
            print(f"Saldo tidak memenuhi saldo minimum rekening {rek_tujuan}")


    @staticmethod
    def downgrade_rekening(bank):
        norek    = input("Masukkan nomor rekening: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            return
        UI.sukses("Rekening ditemukan!")
        print(f"Rekening saat ini : {AdminCs.level[rekening.level]}")
        if rekening.level == 1:
            print("Rekening sudah reguler")
            return

        print("Mau downgrade ke mana: ")
        opsi = list(range(1,rekening.level))
        for i in opsi:
            print(f"{i}. {AdminCs.level[i]}")
        try:
            pilihan = int(input("Masukkan pilihan: "))
        except ValueError:
            print("Tolong masukkan angka")
            return
        if pilihan not in opsi:
            print("Pilihan tidak valid")
            return
        rek_awal      = AdminCs.level[rekening.level]
        rek_tujuan    = AdminCs.level[pilihan]
        rekening_baru = bank.upgrade_rekening(rekening,pilihan)
        if rekening_baru:
            log = RiwayatTemplate.upgrade_rekening(sebelum=rek_awal,sesudah=rek_tujuan)
            UI.sukses('Penurunan Sukses!')
            print(f"Rekening telah diturunkan ke {AdminCs.level[pilihan]}")
            AuditService.tambah_audit(bank,kategori="rekening",jenis="downgrade",log=f"{rekening.pemilik.nama} mengubah rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
            rekening_baru.simpan_riwayat(log)

    @staticmethod
    def blokir_rekening(bank):
        norek = input("Masukkan nomor rekening: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            return
        UI.sukses("Rekening Ditemukan!")
        UI.wadah_info(rekening.pemilik.nama,rekening.norek,rekening.cek_saldo())
        alasan = input("Masukkan alasan pemblokiran: ")
        if bank.blokir_rekening(rekening,alasan):
            print(f"Rekening dengan nomor {rekening.norek} berhasil diblokir")
            AuditService.tambah_audit(bank,kategori="rekening", jenis="blokir",log=f"{rekening.pemilik.nama} meminta memblokir rekeningnya",norek=rekening.norek)
        else:
            UI.gagal("Rekening ini telah ditutup!")

    @staticmethod
    def buka_blokir(bank):
        nik = input("Masukkan NIK nasabah: ")
        nasabah = bank.data_nasabah(nik)
        if not nasabah:
            print("NIK tidak terdaftar")
            return
        norek = input("Masukkan nomor rekening: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("Rekening tidak ada")
            return
        UI.sukses("Rekening Ditemukan!")
        UI.wadah_info(rekening.pemilik.nama,rekening.norek,rekening.cek_saldo())
        if bank.buka_blokir(rekening):
            print(f"Rekening dengan nomor {rekening.norek} berhasil dibuka kembali")
            AuditService.tambah_audit(bank,kategori="rekening",jenis="buka blokir",log=f"Rekening milik {nasabah.nama} dibuka kembali",norek=rekening.norek)
        else:
            UI.gagal("Rekening ini telah ditutup!")

    @staticmethod
    def reset_pin(bank):
        nik = input("Masukkan NIK nasabah: ")
        nasabah = bank.data_nasabah(nik)
        if not nasabah:
            print("NIK tidak terdaftar")
            return
        norek = input("Masukkan nomor rekening: ")
        rekening = bank.cari_rekening(norek)
        if not rekening:
            print("Rekening tidak ada")
            return
        if rekening not in nasabah.rekening:
            return
        pin = input("Masukkan PIN baru: ")
        if pin == rekening.pin:
            return
        rekening.reset_pin()
        UI.sukses("PIN berhasil direset dan diganti")
        AuditService.tambah_audit(bank,"rekening",jenis="reset pin",log=f"{nasabah.nama} meminta reset pin pada rekeningnya",norek=rekening.norek)
    @staticmethod
    def tutup_rekening(bank):
        nik = input("Masukkan NIK Nasabah: ")
        nasabah = bank.data_nasabah(nik)
        if not nasabah:
            print("NIK tidak terdaftar")
            return
        norek = input("Masukkan nomor rekening: ")
        rekening = bank.cari_rekening(norek)
        if not  rekening:
            print("Rekening tidak ada")
            return
        if rekening not in nasabah.rekening:
            return
        if rekening.saldo > 0:
            print(f"Masih ada saldo Rp{rekening.cek_saldo()}. Harus dikosongkan sebelum ditutup")
            print("Pilih cara pengosongan rekening")
            print("1. Transfer ke rekening lain")
            print("2. Tarik seluruh saldo")
            pilihan = input("Pilihan: ")
            bank.tutup_rekening(rekening,pilihan)
            UI.sukses(f"Rekening dengan nomor {rekening.norek} telah ditutup!")
            AuditService.tambah_audit(bank,kategori="rekening",jenis="tutup",log=f"Rekening bernomor {rekening.norek} milik {nasabah.nama} telah ditutup")

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
    def menu_layanan():
        while True:
            UI.header("MENU CUSTOMER SERVICE")
            print()
            Utilitas.menu_cs()
            pilihan = input("Masukkan pilihan Anda: ")

            if pilihan == "1":
                AdminCs.template_surat("Buka Rekening",["KTP","Kartu ATM",'Buku Tabungan'])
            elif pilihan == "2":
                AdminCs.template_surat("Tingkatkan Rekening",["KTP","Kartu ATM",'Buku Tabungan'])
            elif pilihan == "3":
                AdminCs.template_surat("Turunkan Rekening",["KTP","Kartu ATM",'Buku Tabungan'])
            elif pilihan == "4":
                AdminCs.template_surat("Blokir Rekening",["KTP","Nomor Hp"])
            elif pilihan == "5":
                AdminCs.template_surat("Buka Blokir",["KTP","Buku Tabungan","Kartu ATM","Nomor Hp"])
            elif pilihan == "6":
                AdminCs.template_surat("Reset PIN",["KTP","Kartu ATM"])
            elif pilihan == "8":
                AdminCs.template_surat("Tutup Rekening",["KTP","Buku Tabungan","Saldo Rekening Harus Rp0","Kartu ATM"])
            elif pilihan == "7":
                break

    @staticmethod
    def buka_rekening(bank):
        UI.header("SIAPA ANDA?")
        while True:
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

    @staticmethod
    def layanan_nasabah(bank):
        from bank_djago.services.layanan_nasabah import LayananNasabah
        nik = input("Masukkan NIK Anda: ")
        nasabah = bank.cari_nasabah(nik)
        if not nasabah:
            UI.gagal("NIK tidak terdaftar")
            return
        LayananNasabah.menu_layanan(bank,nasabah)