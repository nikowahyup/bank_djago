from bank_djago.utils.utililty import Utilitas
class AuditService:

    @staticmethod
    def tambah_audit(bank,kategori,jenis,log,nama=None,nik=None,norek=None):
        audit = {"kategori":kategori,
                 "waktu":Utilitas.waktu_sekarang(),
                 "jenis":jenis.upper(),
                 "log":log}
        if nik is not None:
            audit["nik"] = nik
        if nama is not None:
            audit["nama"] = nama
        if norek is not None:
            audit["rekening"] = norek
        bank.audit_log.append(audit)

    @staticmethod
    def cari_kategori_audit(bank,kategori):
        return [item for item in bank.audit_log
                if item["kategori"] == kategori]