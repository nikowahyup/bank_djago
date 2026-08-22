import datetime
from bank_djago.services.admin.audit_service  import AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate


class LimitService:

    @staticmethod
    def reset_limit(bank,rekening,hari_ini=None):
        if hari_ini is None:
            hari_ini     = datetime.date.today()
        if hari_ini != rekening.reset:
            rekening.limit_sisa = rekening.limit_harian
            rekening.reset      = hari_ini

            log = RiwayatTemplate.template(kategori="transaksi",jenis="reset limit",log="Limit harian telah direset")

            rekening.simpan_riwayat(log)
            AuditService.tambah_audit(bank,kategori="sistem",jenis="reset limit",log="Reset limit harian rekening")
            return True

        return False