from bank_djago.services.admin.AdminTeller.admin_payroll import BiayaAdminService
from bank_djago.services.deposito.deposito_service import StatusDeposito,DepositoService,JenisAro
from bank_djago.services.bunga import BungaService
from bank_djago.services.transaksi.limit import LimitService
import datetime

class Scheduler:

    @staticmethod
    def jalankan(bank):
        for rekening in bank.rekening_index.values():
            BungaService.berikan_bunga(rekening)

            LimitService.reset_limit(bank,rekening)

            BiayaAdminService.potong_admin(bank, rekening)




        hari_ini = datetime.date.today()

        for nasabah in bank.data_nasabah.values():
            for deposito in nasabah.deposito:

                if deposito.status != StatusDeposito.AKTIF:
                    continue

                if deposito.jatuh_tempo > hari_ini:
                    continue

                if deposito.jenis_aro == JenisAro.TIDAK:

                    deposito.status = StatusDeposito.JATUH_TEMPO

                else:
                    DepositoService.perpanjangan(bank, deposito)