import datetime
from .utililty import Utilitas, StatusPinjaman
from ..services.deposito.deposito_service import StatusDeposito


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
                    bulan
                )

    @staticmethod
    def cek_jatuh_tempo_pinjaman(bank,bulan=1):
        for pinjaman in bank.daftar_pinjaman:
            if pinjaman.status != StatusPinjaman.AKTIF:
                continue

            pinjaman.tanggal_jatuh_tempo = Utilitas.tambah_bulan(pinjaman.tanggal_jatuh_tempo,bulan)
