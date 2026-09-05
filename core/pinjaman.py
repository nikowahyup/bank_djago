from bank_djago.utils.utility import StatusPinjaman

#blueprint untuk pinjaman
class Pinjaman:
    def __init__(self,pemilik,rekening,nominal_pinjaman,bunga,tenor,id=None):
        self.ID = id
        self.pemilik = pemilik
        self.rekening = rekening
        self.nominal_pinjaman = nominal_pinjaman
        self.bunga = bunga
        self.tenor = tenor
        self.sisa_pokok = 0
        self.cicilan_tetap = 0
        self.cicilan_terbayar = 0
        self.status = StatusPinjaman.DIAJUKAN
        self.tanggal_pencairan = None
        self.tanggal_jatuh_tempo = None



    def ke_dict(self):
        return {
            "ID": self.ID,
            "nik":self.pemilik.NIK,
            "rekening": self.rekening.norek,
            "nominal_pinjaman": self.nominal_pinjaman,
            "bunga": self.bunga,
            "tenor": self.tenor,
            "cicilan_tetap": self.cicilan_tetap,
            "sisa_pokok": self.sisa_pokok,
            "cicilan_terbayar": self.cicilan_terbayar,
            "status": self.status.value,
            "tanggal_pencairan": (
                self.tanggal_pencairan.isoformat()
                if self.tanggal_pencairan
                else None),
            "jatuh_tempo": (self.tanggal_jatuh_tempo.isoformat()
                            if self.tanggal_jatuh_tempo
                            else None)
        }


