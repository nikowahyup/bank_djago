class Nasabahh:
    def __init__(self,nama,alamat,nik):
        self.nama     = nama.title()
        self.alamat   = alamat
        self.NIK      = nik
        self.rekening = []
        self.deposito = []
        self.jumlah_deposito = 0
        self.notifikasi = []


    def ke_dict(self): # pengonversi objek nasabah ke dictionary agar bisa disimpan ke JSON
        return {
            "nama"    : self.nama,
            "alamat"  : self.alamat,
            "nik"     : self.NIK,
            "rekening": [
                rekening.norek
                for rekening in self.rekening

            ],
            "deposito":[],
            "notif" : self.notifikasi
        }
    @classmethod
    def dari_dict(cls,data): # pengonversi file JSON ke objek nasabah kembali
        nasabah = cls(nama  =data['nama'],
                      alamat=data['alamat'],
                      nik   =data['nik'],
                      )
        nasabah.notifikasi = data.get("notif",[])
        return nasabah





    def notifikasi(self):
        if not self.notifikasi:
            return

        for notif in self.notifikasi:
            print(f'. {notif}')

        self.notifikasi.clear()
