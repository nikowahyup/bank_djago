from bank_djago.utils.utililty import JenisAro

class Deposito:

    def __init__(self,pemilik,rekening,nominal,bunga,id,lama_bulan,tanggal_buka,tanggal_jatuh_tempo):

        self.pemilik      = pemilik
        self.rekening     = rekening
        self.nominal      = nominal
        self.bunga        = bunga
        self.lama_bulan   = lama_bulan
        self.tanggal_buka = tanggal_buka
        self.jatuh_tempo  = tanggal_jatuh_tempo
        self.status       = "aktif"
        self.ID           = id
        self.jenis_aro    = JenisAro.TIDAK
        self.lama_aro     = None
        self.notifikasi_depo = False
        self.proses_aro = None


    @property
    def total_pencairan(self):
        bunga = (self.nominal*self.bunga*self.lama_bulan/12)
        return round(self.nominal + bunga)



    def ke_dict(self):
        return {"norek": self.rekening.norek,
                "nik":self.pemilik.NIK,
                "nominal":self.nominal,
                "bunga":self.bunga,
                "lama_bulan":self.lama_bulan,
                "tanggal_buka":self.tanggal_buka.isoformat(),
                "jatuh_tempo":self.jatuh_tempo.isoformat(),
                "status":self.status,
                "jenis_aro":self.jenis_aro,
                "lama_aro":self.lama_aro,
                "proses_aro":self.proses_aro.isoformat() if self.proses_aro is not None else None}