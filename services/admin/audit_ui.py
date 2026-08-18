from bank_djago.services.admin.audit_service import AuditService
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.ui import UI
class AuditUI:

    @staticmethod #method template
    def tampilkan_audit(log_audit):
        for item in log_audit:
            print("-"*80)
            print(Utilitas.format_waktu(item["waktu"]), "|",item["jenis"],"|",item["log"])
            if "nama" in item:
                print("Nama     :",item["nama"])
            if "nik" in item:
                print("NIK      :",item["nik"])
            if "rekening" in item:
                print("Rekening :",item["rekening"])

    @staticmethod
    def menu_tampilkan_audit(bank):
        while  True:
            Utilitas.menu_audit()
            pilihan = input('Masukkan pilihan: ')
            if pilihan == "1":
                UI.header("SEMUA AKTIVITAS",UI.MERAH)
                AuditUI.tampilkan_audit(bank.audit_log)
                print()
            elif pilihan == "2":
                UI.header("AKTIVITAS TRANSAKSI", UI.MERAH)
                log_audit = AuditService.cari_kategori_audit(bank,"transaksi")
                AuditUI.tampilkan_audit(log_audit)
                print()
            elif pilihan == "3":
                UI.header("AKTIVITAS REKENING", UI.MERAH)
                log_audit = AuditService.cari_kategori_audit(bank,"rekening")
                AuditUI.tampilkan_audit(log_audit)
                print()
            elif pilihan == "4":
                UI.header("AKTIVITAS NASABAH", UI.MERAH)
                log_audit = AuditService.cari_kategori_audit(bank,"nasabah")
                AuditUI.tampilkan_audit(log_audit)
                print()
            elif pilihan == "5":
                break
