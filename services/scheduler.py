from bank_djago.services.admin.admin_payroll import BiayaAdminService
from bank_djago.services.bunga import BungaService
from bank_djago.services.limit import LimitService

class Scheduler:

    @staticmethod
    def jalankan(bank):
        for rekening in bank.rekening_index.values():
            BungaService.berikan_bunga(rekening)
            bank.tambah_audit(kategori="transaksi",jenis="beri bunga",log="Berikan bunga nasabah")
            LimitService.reset_limit(rekening)
            bank.tambah_audit(kategori="sistem",jenis="reset limit",log="Reset limit harian rekening")
            BiayaAdminService.potong_admin(rekening)
            bank.tambah_audit(kategori="sistem",jenis="biaya admin",log="Bayar rutin bulanan biaya admin")
