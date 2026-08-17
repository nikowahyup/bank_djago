from bank_djago.utils.utililty import StatusPinjaman


class Pinjaman:
    def __init__(self,ID,pemilik,rekening,nominal_pinjaman,bunga,tenor):
        self.ID = ID
        self.pemilik = pemilik
        self.rekening = rekening
        self.nominal_pinjaman = nominal_pinjaman
        self.bunga = bunga
        self.tenor = tenor
        self.sisa_pokok = nominal_pinjaman
        self.cicilan_tetap = 0
        self.cicilan_terbayar = 0
        self.status = StatusPinjaman.DIAJUKAN
        self.bunga_bulanan = 0
        self.tanggal_pencairan = None
        self.tanggal_jatuh_tempo = None
        self.notifikasi_jatuh_tempo = False


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
            "bunga_bulanan": self.bunga_bulanan,
            "status": self.status.value,
            "tanggal_pencairan": (
                self.tanggal_pencairan.isoformat()
                if self.tanggal_pencairan
                else None),
            "jatuh_tempo": (self.tanggal_jatuh_tempo.isoformat()
                            if self.tanggal_jatuh_tempo
                            else None)
        }


