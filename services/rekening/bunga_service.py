# from getopt import long_has_args

from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas
import datetime
from bank_djago.services.admin.audit_service import AuditService

class BungaService:

    @staticmethod
    def hitung_bulan(rekening,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        bulan = ((hari_ini.year - rekening.dapat_bunga.year)*12 + hari_ini.month - rekening.dapat_bunga.month)
        if hari_ini.day < rekening.dapat_bunga.day:
            bulan -= 1

        return bulan

    @staticmethod
    def berikan_bunga(bank, rekening, hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        bulan = BungaService.hitung_bulan(rekening,hari_ini)
        if bulan <= 0:
            return

        bunga_bulanan = round(rekening.saldo*rekening.bunga/12)
        bunga_total = round(bunga_bulanan*bulan)

        rekening.tambah_saldo(bunga_total)

        rekening.dapat_bunga  = Utilitas.tambah_bulan(rekening.dapat_bunga, bulan)
        bulan = Utilitas.nama_bulan(rekening.dapat_bunga)
        waktu = f"{bulan.upper()} {rekening.dapat_bunga.year}"
        log = RiwayatTemplate.template(kategori="transaksi",jenis="beri bunga",log=f"BUNGA {waktu} +Rp{Utilitas.format_rupiah(bunga_total)}")

        rekening.simpan_riwayat(log)
        AuditService.tambah_audit(bank, kategori="transaksi", jenis="beri bunga", log="Berikan bunga nasabah",nama=rekening.pemilik.nama,norek=rekening.norek)


        return bunga_total
