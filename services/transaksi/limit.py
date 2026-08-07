import datetime

class LimitService:

    @staticmethod
    def reset_limit(rekening):
        hari_ini     = datetime.date.today()
        if hari_ini != rekening.reset:
            rekening.limit_sisa = rekening.limit_harian
            rekening.reset      = hari_ini

            rekening.simpan_riwayat_sistem("Limit harian telah direset")
            return True

        return False