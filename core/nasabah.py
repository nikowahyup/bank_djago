class Nasabahh:
    def __init__(self,nama,alamat,nik):
        self.nama     = nama.title()
        self.alamat   = alamat
        self.NIK      = nik
        self.rekening = []
        self.deposito = []

    def ke_dict(self): # pengonversi objek nasabah ke dictionary agar bisa disimpan ke JSON
        return {
            "nama"    : self.nama,
            "alamat"  : self.alamat,
            "nik"     : self.NIK,
            "rekening": [
                rekening.norek
                for rekening in self.rekening

            ],
            "deposito":[]
        }
    @classmethod
    def dari_dict(cls,data): # pengonversi file JSON ke objek nasabah kembali
        nasabah = cls(nama  =data['nama'],
                      alamat=data['alamat'],
                      nik   =data['nik'])

        return nasabah




