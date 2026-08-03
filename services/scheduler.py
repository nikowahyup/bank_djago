from bank_djago.services.admin import BiayaAdminService
from bank_djago.services.bunga import BungaService
from bank_djago.services.limit import LimitService


class Scheduler:

    @staticmethod
    def jalankan(bank):
        for rekening in bank.rekening_index.values():
            BungaService.berikan_bunga(rekening)
            LimitService.reset_limit(rekening)
            BiayaAdminService.potong_admin(rekening)
