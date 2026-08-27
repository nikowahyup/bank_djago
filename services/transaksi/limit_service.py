import datetime


class LimitService:

    @staticmethod
    def hitung_limit_saat_ini(rekening,hari_ini=None):
        if hari_ini is None:
            hari_ini  = datetime.date.today()

        if rekening.limit_harian is None:
            return None,rekening.reset,False

        if hari_ini > rekening.reset:
            return rekening.limit_harian,hari_ini,True

        return rekening.limit_sisa,rekening.reset,False