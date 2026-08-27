from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository



class RiwayatService:


    @staticmethod
    def ambil_riwayat(rekening,jenis=None):

        if jenis is None:
            daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(rekening.norek)

        else:
            daftar_riwayat = RiwayatRepository.cari_riwayat_berdasarkan_jenis(rekening.norek, jenis)

        if not daftar_riwayat:
            raise ValueError("Riwayat tidak ditemukan")

        return daftar_riwayat



