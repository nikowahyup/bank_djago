import datetime
from bank_djago.services.admin.rekap_audit import AuditService

class LimitService:

    @staticmethod
    def reset_limit(bank,rekening):
        hari_ini     = datetime.date.today()
        if hari_ini != rekening.reset:
            rekening.limit_sisa = rekening.limit_harian
            rekening.reset      = hari_ini

            rekening.simpan_riwayat_sistem("Limit harian telah direset")
            AuditService.tambah_audit(bank,kategori="sistem",jenis="reset limit",log="Reset limit harian rekening")
            return True

        return False