class RiwayatService:


    @staticmethod
    def ambil_riwayat(rekening,jenis=None):
        if jenis is None:
            data = rekening.riwayat

        else:
            data = [item for item in rekening.riwayat if item["jenis"] == jenis]

        if not data:
            raise ValueError("Riwayat tidak ditemukan")
        return data
