from bank_djago.penyimpanan.repositories.rekap_repository import RekapRepository


class RekapService:

    @staticmethod
    def rekap_umum():

        total_nasabah, total_rekening, total_saldo = RekapRepository.rekap_umum()


        return total_nasabah,total_rekening,total_saldo

    @staticmethod
    def rekap_jumlah_rekening():

        reguler ,prioritas , gold , platinum = RekapRepository.jumlah_tiap_jenis_rekening()

        return reguler,prioritas,gold,platinum

    @staticmethod
    def rekap_status_rekening():
        aktif ,blokir , tutup = RekapRepository.rekap_status_rekening()

        return aktif, blokir, tutup

    @staticmethod
    def total_saldo_rekening():
        reguler , prioritas ,gold ,platinum = RekapRepository.total_saldo_tiap_jenis_rekening()


        return reguler, prioritas, gold, platinum

    @staticmethod
    def saldo_terbesar():
        saldo_terbesar = RekapRepository.cari_saldo_terbesar()
        if saldo_terbesar is None:
            return None
        return saldo_terbesar
    # ------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def saldo_terkecil():
        saldo_terkecil = RekapRepository.cari_saldo_terkecil()

        if saldo_terkecil is None:
            return None
        return saldo_terkecil

