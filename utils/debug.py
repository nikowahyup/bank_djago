import datetime
from .utililty import Utilitas
class Debug:

    @staticmethod
    def debug_bunga(bank,bulan=1):

        for rekening in bank.rekening_index.values():
            rekening.dapat_bunga -= datetime.timedelta(days=bulan * 31)
            rekening.waktu_bayar_admin -= datetime.timedelta(days=bulan * 31)


    @staticmethod
    def cek_jatuh_tempo(bank,bulan):
        for nasabah in bank.data_nasabah.values():
            for deposito in nasabah.deposito:
                deposito.jatuh_tempo = Utilitas.tambah_bulan(
                    deposito.jatuh_tempo,
                    -bulan
                )