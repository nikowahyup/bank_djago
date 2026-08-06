from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.utils.utililty import Utilitas
class AuditUI:

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
                AuditUI.tampilkan_audit(bank.audit_log)
                print()
            elif pilihan == "2":
                print('='*25,"AKTIVITAS TRANSAKSI","="*25)
                log_audit = AuditService.cari_kategori_audit(bank,"transaksi")
                AuditUI.tampilkan_audit(log_audit)
                print()
            elif pilihan == "3":
                print('='*25,"AKTIVITAS REKENING","="*25)
                log_audit = AuditService.cari_kategori_audit(bank,"rekening")
                AuditUI.tampilkan_audit(log_audit)
                print()
            elif pilihan == "4":
                print('='*25,"AKTIVITAS NASABAH","="*25)
                log_audit = AuditService.cari_kategori_audit(bank,"nasabah")
                AuditUI.tampilkan_audit(log_audit)
                print()
            elif pilihan == "5":
                break
