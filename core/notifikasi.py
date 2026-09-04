from bank_djago.utils.utility import JenisReferensi

#blueprint untuk notifikasi
class Notifikasi:
    def __init__(self,jenis,pesan,jenis_referensi=None,id_objek=None):

        self.jenis = jenis
        self.pesan = pesan
        self.jenis_referensi = jenis_referensi
        self.id_objek = id_objek

    def ke_dict(self):
        return {
                "jenis":self.jenis,
                "pesan":self.pesan,
                "referensi":self.jenis_referensi.value if self.jenis_referensi is not None else None,
                "ID_objek":self.id_objek
                }

    @classmethod
    def dari_dict(cls, data):
        referensi = data.get("referensi")

        if referensi in ("", None):
            referensi = None
        else:
            referensi = JenisReferensi.dari_nilai(referensi)

        return cls(

            jenis=data["jenis"],
            pesan=data["pesan"],
            jenis_referensi=referensi,
            id_objek=data.get("ID_objek")
        )
