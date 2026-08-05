import datetime
from bank_djago.utils.utililty import Utilitas,UI



class BiayaAdminService:


    @staticmethod
    def potong_admin(rekening):

        hari_ini = datetime.date.today()

        bulan = (
                (hari_ini.year - rekening.waktu_bayar_admin.year) * 12
                + hari_ini.month
                - rekening.waktu_bayar_admin.month
        )

        if hari_ini.day < rekening.waktu_bayar_admin.day:
            bulan -= 1

        if bulan <= 0:
            return

        total_admin = rekening.biaya_admin * bulan

        rekening.kurangi_saldo(total_admin)

        rekening.waktu_bayar_admin = hari_ini

        simpan = {
            "kategori":"sistem",
            "jenis": "biaya admin",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"BIAYA ADMIN | Jumlah Rp{total_admin:,}".replace(",", ".")
        }
        rekening.simpan_riwayat(simpan)





class MenuAdmin:

    @staticmethod
    def menu(bank):
        print()
        UI.peringatan("""PERHATIAN! Menu ini khusus Admin. 
Nasabah tidak diperbolehkan masuk!
Masukkan sembarang simbol untuk keluar""")

        password = input("Masukkan password: ")
        if not bank.verifikasi_admin(password):
            return

        while True:
            UI.header("MENU DATA BANK")
            print()
            print("1. Menu Rekap Bank")
            print("2. Menu Audit")
            print("3. Keluar\n")
            pilihan = input("Pilihan Kamu: ")

            if pilihan == "1":
                MenuAdmin.menu_tampilkan_rekap(bank)
            elif pilihan == "2":
                MenuAdmin.menu_tampilkan_audit(bank)
            elif pilihan == "3":
                break

    @staticmethod
    def menu_tampilkan_rekap(bank):
        while True:
            Utilitas.menu_admin()
            pilihan = input("Masukkan pilihan: ")
            if pilihan == "1":
                total_nasabah,total_rekening,total_saldo = bank.rekap_umum()
                MenuAdmin.umum(total_nasabah,total_rekening, total_saldo)

            elif pilihan == "2":
                reguler,prioritas,gold,platinum = bank.rekap_jumlah_rekening()
                MenuAdmin.rekap_rekening(reguler,prioritas,gold, platinum)

            elif pilihan == "3":
                aktif,blokir,tutup = bank.rekap_status_rekening()
                MenuAdmin.rekap_status(aktif,blokir,tutup)

            elif pilihan == "4":
                reguler,prioritas,gold,platinum = bank.total_saldo_tiap_rekening()
                MenuAdmin.total_saldo_tiap_rekening(reguler, prioritas, gold, platinum)

            elif pilihan == "5":
                saldo_terbesar = bank.saldo_terbesar()
                MenuAdmin.saldo_terbesar(saldo_terbesar)

            elif pilihan == "6":
                saldo_terkecil = bank.saldo_terkecil()
                MenuAdmin.saldo_terkecil(saldo_terkecil)

            elif pilihan == "7":
                break

    @staticmethod
    def umum(total_nasabah,total_rekening,total_saldo):

        print("="*18,"REKAP UMUM","="*18)
        print()
        print(f"👤 Total Nasabah  : {total_nasabah}")
        print(f"💳 Total Rekening : {total_rekening}")
        print(f"💰 Total Saldo    : Rp{Utilitas.format_rupiah(total_saldo)}\n")



    @staticmethod
    def rekap_rekening(reguler,prioritas,gold,platinum):
        print("="*15,"REKAP REKENING","="*15)
        print()
        print(f"{UI.kelas[1]} Rekening Reguler   : {reguler}")
        print(f"{UI.kelas[2]} Rekening Prioritas : {prioritas}")
        print(f"{UI.kelas[3]} Rekening Gold      : {gold}")
        print(f"{UI.kelas[4]} Rekening Platinum  : {platinum}\n")


    @staticmethod
    def rekap_status(aktif,blokir,tutup):
        print("="*12,"REKAP STATUS REKENING","="*12)
        print()
        print(f"✅ Rekening Aktif  : {aktif}")
        print(f"⚠️ Rekening Blokir : {blokir}")
        print(f"❌ Rekening Tutup  : {tutup}\n")

    @staticmethod
    def total_saldo_tiap_rekening(reguler,prioritas,gold,platinum):
        print("="*12,"REKAP SALDO TIAP REKENING","="*12)
        print()
        print(f"{UI.kelas[1]}Rekening Reguler   : Rp{Utilitas.format_rupiah(reguler)}")
        print(f"{UI.kelas[2]}Rekening Prioritas : Rp{Utilitas.format_rupiah(prioritas)}")
        print(f"{UI.kelas[3]}Rekening Gold      : Rp{Utilitas.format_rupiah(gold)}")
        print(f"{UI.kelas[4]}Rekening Platinum  : Rp{Utilitas.format_rupiah(platinum)}\n")

    @staticmethod
    def saldo_terbesar(rekening_terbesar):
        print("="*12,"PEMILIK SALDO TERBESAR","="*12)
        print()
        print(f'{rekening_terbesar.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terbesar.saldo)}\n")



    @staticmethod
    def saldo_terkecil(rekening_terkecil):
        print("="*12,"PEMILIK SALDO TERKECIL","="*12)
        print()
        print(f'{rekening_terkecil.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terkecil.saldo)}\n")


    #--------------------------------------------------------------------------------------------------------------------

    @staticmethod #method template
    def tampilkan_audit(log_audit):
        for item in log_audit:
            print("-"*80)
            print(Utilitas.format_waktu(item["waktu"]), "|",item["jenis"],"|",item["log"])
            if "nama" in item:
                print("Nama     :",item["nama"])
            if "NIK" in item:
                print("NIK      :",item["NIK"])
            if "Rekening" in item:
                print("Rekening :",item["Rekening"])

    @staticmethod
    def menu_tampilkan_audit(bank):
        while  True:
            Utilitas.menu_audit()
            pilihan = input('Masukkan pilihan: ')
            if pilihan == "1":
                print('='*25,"SEMUA AKTIVITAS","="*25)
                MenuAdmin.tampilkan_audit(bank.audit_log)
                print()
            elif pilihan == "2":
                print('='*25,"AKTIVITAS TRANSAKSI","="*25)
                log_audit = bank.cari_kategori_audit("transaksi")
                MenuAdmin.tampilkan_audit(log_audit)
                print()
            elif pilihan == "3":
                print('='*25,"AKTIVITAS REKENING","="*25)
                log_audit = bank.cari_kategori_audit("rekening")
                MenuAdmin.tampilkan_audit(log_audit)
                print()
            elif pilihan == "4":
                print('='*25,"AKTIVITAS NASABAH","="*25)
                log_audit = bank.cari_kategori_audit("nasabah")
                MenuAdmin.tampilkan_audit(log_audit)
                print()
            elif pilihan == "5":
                break