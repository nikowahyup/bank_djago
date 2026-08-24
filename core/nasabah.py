class Nasabahh:
    def __init__(self,nama,alamat,nik):
        self.nama     = nama.title()
        self.alamat   = alamat
        self.NIK      = nik
        self.rekening = []
        self.deposito = []
        self.jumlah_deposito = 0
        self.notifikasi = []
        self.pinjaman = None
        self.jumlah_pinjaman = 0
        self.jumlah_notifikasi = 0

    def ke_dict(self):
        return {
            "nama": self.nama,
            "alamat": self.alamat,
            "nik": self.NIK,
            "rekening": [
                rekening.norek
                for rekening in self.rekening
            ],
            "notifikasi": [
                notifikasi.ke_dict()
                for notifikasi in self.notifikasi
            ]
        }
    @classmethod
    def dari_dict(cls,data): # pengonversi file JSON ke objek nasabah kembali
        nasabah = cls(nama  =data['nama'],
                      alamat=data['alamat'],
                      nik   =data['nik'],
                      )

        return nasabah




    def buat_id_notifikasi(self):
        self.jumlah_notifikasi += 1
        return self.jumlah_notifikasi
