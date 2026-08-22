from bank_djago.services.admin.audit_service import AuditService
import datetime

from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas

class BiayaAdminService:


    @staticmethod
    def potong_admin(bank,rekening,hari_ini=None):
        if hari_ini is None:


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

        total_admin = round(rekening.biaya_admin * bulan)

        rekening.kurangi_saldo(total_admin)

        rekening.waktu_bayar_admin = Utilitas.tambah_bulan(rekening.waktu_bayar_admin,bulan)

        log = RiwayatTemplate.template(kategori="transaksi",jenis="bayar admin",log=f"Bayar admin bulanan | -Rp{Utilitas.format_rupiah(total_admin)}")
        rekening.simpan_riwayat(log)

        AuditService.tambah_audit(bank, kategori="transaksi", jenis="biaya admin", log="Bayar rutin bulanan biaya admin",nama=rekening.pemilik.nama,nik=rekening.pemilik.NIK,norek=rekening.norek)