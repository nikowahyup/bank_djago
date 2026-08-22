import datetime

class Rekening:
    def __init__(self,norek,pin,pemilik,limit:int|None = 5000000,bunga=0.03,biaya_admin=2000,pajak=2000,level=1,minimum=500000):

        self.norek     = norek
        self.level     = level
        self.__saldo   = 0
        self.__pin     = pin
        self.bunga     = bunga
        self.pajak     = pajak
        self.riwayat   = []
        self.status    = "aktif"
        self.pemilik   = pemilik

        self.reset             = datetime.date.today()
        self.dapat_bunga       = datetime.date.today()
        self.biaya_admin       = biaya_admin
        self.limit_sisa        = limit
        self. limit_harian     = limit
        self.waktu_bayar_admin = datetime.date.today()
        self.saldosetor_min    = minimum
        self.penutupan         = None
        self.alasan_blokir     = None
        self.boleh_ubah_rekening = None

#------------------------------------------------------------------------------------------------------------------------------

    def ke_dict(self): # pengonversi objek ke dict buat disimpan di JSON
        return {"norek"  :self.norek,
                "pin"    :self.__pin,
                "saldo"  :self.__saldo,
                "limit"  :self.limit_sisa,
                "riwayat":self.riwayat,
                "status" :self.status,
                "level"  :self.level,
                "kesempatan_ubah":self.boleh_ubah_rekening.isoformat() if self.boleh_ubah_rekening  is not None else None,
                "reset":self.reset.isoformat(),
                "dapat_bunga":self.dapat_bunga.isoformat(),
                "bayar_admin":self.waktu_bayar_admin.isoformat()
                }

    # ------------------------------------------------------------------------------------------------------------------------------

    @classmethod
    def dari_dict(cls,data): # pengonversi file JSON ke objek kembali


        rekening = cls(norek  =data["norek"],
                       pin    =data["pin"],
                       pemilik=None,
                       )
        rekening.set_saldo(data["saldo"])
        rekening.limit_sisa     = data["limit"]
        rekening.riwayat        = data["riwayat"]
        rekening.status         = data["status"]
        terakhir_ubah_level = data.get("kesempatan_ubah")
        tanggal_reset = data.get("reset")
        tanggal_dapat_bunga = data.get("dapat_bunga")
        tanggal_bayar_admin = data.get("bayar_admin")
        rekening.boleh_ubah_rekening = (datetime.date.fromisoformat(terakhir_ubah_level) if terakhir_ubah_level is not None else None)

        if tanggal_reset is not None:
            rekening.reset = datetime.date.fromisoformat(tanggal_reset)

        if tanggal_dapat_bunga is not None:
            rekening.dapat_bunga = datetime.date.fromisoformat(tanggal_dapat_bunga)

        if tanggal_bayar_admin is not None:
            rekening.reset = datetime.date.fromisoformat(tanggal_bayar_admin)

        return rekening



   # ------------------------------------------------------------------------------------------------------------------------------

    def cek_saldo(self):
        rupiah = f"{self.__saldo:,}".replace(",",".")
        return rupiah

   # ------------------------------------------------------------------------------------------------------------------------------

    @property
    def pin(self):
        return self.__pin

    # ------------------------------------------------------------------------------------------------------------------------------

    @property
    def saldo(self):
        return self.__saldo

    # ------------------------------------------------------------------------------------------------------------------------------

    def cek_pin(self,pin):
        return self.__pin == pin

    # ------------------------------------------------------------------------------------------------------------------------------

    def kurangi_saldo(self,jumlah):
        self.__saldo -= jumlah

    # ------------------------------------------------------------------------------------------------------------------------------

    def tambah_saldo(self,jumlah):
        self.__saldo += jumlah

    # ------------------------------------------------------------------------------------------------------------------------------

    def set_saldo(self,nominal):
        if nominal >= 0:
            self.__saldo = nominal

    # ------------------------------------------------------------------------------------------------------------------------------

    def simpan_riwayat(self,log):
            self.riwayat.append(log)

    # ------------------------------------------------------------------------------------------------------------------------------

    def ganti_pin(self,pin_baru):
        self.__pin = pin_baru

    # ------------------------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------------------------

    @property
    def jenis(self):
        return {
            1: "Reguler",
            2: "Prioritas",
            3: "Gold",
            4: "Platinum"
        }[self.level]

    @property
    def boleh_ubah_level(self):
        return (
                self.boleh_ubah_rekening is None
                or self.boleh_ubah_rekening < datetime.date.today()
        )

class RekeningReguler(Rekening):
    pass

#------------------------------------------------------------------------------------------------------------------------------

class RekeningPrioritas(Rekening):
    def __init__(self,norek,pin,pemilik):
        self.saldo_min = 3_000_000
        self.limit = 15_000_000
        self.bunga = 0.05
        super().__init__(norek,pin,pemilik,limit=self.limit,bunga=self.bunga,biaya_admin=5000,pajak=0,level=2,minimum=self.saldo_min)

#------------------------------------------------------------------------------------------------------------------------------

class RekeningGold(Rekening):
    def __init__(self,norek,pin,pemilik):
        self.saldo_min = 50_000_000
        self.limit = 200_000_000
        self.bunga = 0.07
        super().__init__(norek,pin,pemilik,limit=self.limit,bunga=self.bunga,biaya_admin=10000,pajak=0,level=3,minimum=self.saldo_min)

#------------------------------------------------------------------------------------------------------------------------------

class RekeningPlatinum(Rekening):
    SALDO_MIN = 200_000_000
    LIMIT = None
    BUNGA = 0.1
    def __init__(self,norek,pin,pemilik):
        super().__init__(norek,pin,pemilik,limit=self.LIMIT,bunga=self.BUNGA,biaya_admin=20000,pajak=0,level=4,minimum=self.SALDO_MIN)

#------------------------------------------------------------------------------------------------------------------------------


kelas_rekening = {
            "Reguler"  : RekeningReguler,
            "Prioritas": RekeningPrioritas,
            "Gold"     : RekeningGold,
            "Platinum" : RekeningPlatinum}