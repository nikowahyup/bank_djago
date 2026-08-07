import datetime
class Deposito:

    def __init__(self,pemilik,rekening,nominal,bunga,lama_bulan,tanggal_buka,tanggal_jatuh_tempo):
        self.pemilik      = pemilik
        self.rekening     = rekening
        self.nominal      = nominal
        self.bunga        = bunga
        self.lama_bulan   = lama_bulan
        self.tanggal_buka = tanggal_buka
        self.jatuh_tempo  = tanggal_jatuh_tempo
        self.status       = "aktif"
        self.aro          = False



    @property
    def total_pencairan(self):
        bunga = (self.nominal*self.bunga*self.lama_bulan/12)
        return self.nominal + bunga