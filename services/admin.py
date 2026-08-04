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
        password = input("Masukkan password: ")
        if not bank.verifikasi_admin(password):
            print("Password salah")
            return


        while True:
            Utilitas.menu_admin()
            pilihan = input("Pilihan Kamu: ")

            if pilihan == "1":
                bank.rekap_umum()
            elif pilihan == "2":
                bank.rekap_jumlah_rekening()
            elif pilihan == "3":
                bank.rekap_status_rekening()
            elif pilihan == "4":
                bank.total_saldo_tiap_rekening()
            elif pilihan =="5":
                bank.saldo_terbesar()
            elif pilihan =="6":
                bank.saldo_terkecil()
            elif pilihan == "7":
                MenuAdmin.menu_tampilkan_audit(bank)
            elif pilihan == "8":
                break


    @staticmethod
    def umum(total_nasabah,total_rekening,total_saldo):

        UI.header('REKAP UMUM')
        print(f"👤 Total Nasabah  : {total_nasabah}")
        print(f"💳 Total Rekening : {total_rekening}")
        print(f"💰 Total Saldo    : Rp{Utilitas.format_rupiah(total_saldo)}")



    @staticmethod
    def rekap_rekening(reguler,prioritas,gold,platinum):
        print("="*20,"REKAP REKENING","="*20)
        print(f"Rekening Reguler   : {reguler}")
        print(f"Rekening Prioritas : {prioritas}")
        print(f"Rekening Gol       : {gold}")
        print(f"Rekening Platinum  : {platinum}")


    @staticmethod
    def rekap_status(aktif,blokir,tutup):

        UI.header('REKAP STATUS REKENING')
        print(f"✅ Rekening Aktif  : {aktif}")
        print(f"⚠️ Rekening Blokir : {blokir}")
        print(f"❌ Rekening Tutup  : {tutup}")

    @staticmethod
    def total_saldo_tiap_rekening(reguler,prioritas,gold,platinum):
        UI.header("REKAP SALDO TIAP REKENING")
        print(f"Rekening Reguler   : Rp{Utilitas.format_rupiah(reguler)}")
        print(f"Rekening Prioritas : Rp{Utilitas.format_rupiah(prioritas)}")
        print(f"Rekening Gold      : Rp{Utilitas.format_rupiah(gold)}")
        print(f"Rekening Platinum  : Rp{Utilitas.format_rupiah(platinum)}")

    @staticmethod
    def saldo_terbesar(rekening_terbesar):
        UI.header("PEMILIK SALDO TERBESAR")
        print(f'{rekening_terbesar.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terbesar.saldo)}")



    @staticmethod
    def saldo_terkecil(rekening_terkecil):
        UI.header('PEMILIK SALDO TERKECIL')
        print(f'{rekening_terkecil.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terkecil.saldo)}")


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
            elif pilihan == "2":
                print('='*25,"AKTIVITAS TRANSAKSI","="*25)
                log_audit = bank.cari_kategori_audit("transaksi")
                MenuAdmin.tampilkan_audit(log_audit)
            elif pilihan == "3":
                print('='*25,"AKTIVITAS REKENING","="*25)
                log_audit = bank.cari_kategori_audit("rekening")
                MenuAdmin.tampilkan_audit(log_audit)
            elif pilihan == "4":
                print('='*25,"AKTIVITAS NASABAH","="*25)
                log_audit = bank.cari_kategori_audit("nasabah")
                MenuAdmin.tampilkan_audit(log_audit)
            elif pilihan == "5":
                break