from bank_djago.utils.utililty import JenisReferensiID


class Notifikasi:
    def __init__(self,jenis,pesan,referensi_id=None,id_objek=None):

        self.jenis = jenis
        self.pesan = pesan
        self.referensi_id = referensi_id
        self.ID_objek = id_objek

    def ke_dict(self):
        return {
                "jenis":self.jenis,
                "pesan":self.pesan,
                "referensi":self.referensi_id.value if self.referensi_id is not None else None,
                "ID_objek":self.ID_objek if self.ID_objek is not None else None
                }

    @classmethod
    def dari_dict(cls, data):
        referensi = data.get("referensi")

        if referensi in ("", None):
            referensi = None
        else:
            referensi = JenisReferensiID(referensi)

        return cls(

            jenis=data["jenis"],
            pesan=data["pesan"],
            referensi_id=referensi,
            id_objek=data["ID_objek"]
        )

