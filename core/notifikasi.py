


class Notifikasi:
    def __init__(self,id_notifikasi,jenis,pesan,referensi_id=None):
        self.ID = id_notifikasi
        self.jenis = jenis
        self.pesan = pesan
        self.referensi_id = referensi_id


    def ke_dict(self):
        return {"ID":self.ID,
                "jenis":self.jenis,
                "pesan":self.pesan,
                "referensi":self.referensi_id.value if self.referensi_id is not None else None
                }


    @classmethod
    def dari_dict(cls,data):
        return cls(id_notifikasi=data["ID"],
                    jenis=data["jenis"],
                    pesan=data["pesan"],
                    referensi_id=data.get("referensi"))


