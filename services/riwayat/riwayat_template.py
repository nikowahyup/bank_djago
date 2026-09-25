import datetime


class RiwayatTemplate:

    @staticmethod
    def template(kategori, jenis, log):
        return {
            "kategori": kategori,
            "jenis": jenis,
            "waktu": datetime.datetime.now().isoformat(),
            "log": log,
        }
