
class RekapService:

    @staticmethod
    def rekap_umum(bank):
        total_nasabah  = len(bank.data_nasabah)
        total_rekening = len(bank.rekening_index)
        total_saldo    = sum(rekening.saldo for rekening in bank.rekening_index.values())

        return total_nasabah,total_rekening,total_saldo

    @staticmethod
    def rekap_jumlah_rekening(bank):
        reguler = prioritas = gold = platinum = 0

        for rekening in bank.rekening_index.values():
            if rekening.level   == 1:
                reguler   += 1
            elif rekening.level == 2:
                prioritas += 1
            elif rekening.level == 3:
                gold      += 1
            elif rekening.level == 4:
                platinum  += 1
        return reguler,prioritas,gold,platinum

    @staticmethod
    def rekap_status_rekening(bank):
        aktif = blokir = tutup = 0

        for rekening in bank.rekening_index.values():
            if rekening.status == "aktif":
                aktif += 1
            elif rekening.status == "blokir":
                blokir += 1
            elif rekening.status == "tutup":
                tutup += 1

        return aktif, blokir, tutup

    @staticmethod
    def total_saldo_rekening(bank):
        reguler = prioritas = gold = platinum = 0

        for rekening in bank.rekening_index.values():
            if rekening.level == 1:
                reguler += rekening.saldo

            elif rekening.level == 2:
                prioritas += rekening.saldo

            elif rekening.level == 3:
                gold += rekening.saldo

            elif rekening.level == 4:
                platinum += rekening.saldo
        return reguler, prioritas, gold, platinum

    @staticmethod
    def saldo_terbesar(bank):
        rekening_besar = max(bank.rekening_index.values(),key=lambda r:r.saldo)
        return rekening_besar
    # ------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def saldo_terkecil(bank):
        rekening_kecil = min(bank.rekening_index.values(),key=lambda r:r.saldo)
        return rekening_kecil

