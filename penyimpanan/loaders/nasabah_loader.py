
from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
from bank_djago.penyimpanan.loaders.notifikai_loader import NotifikasiLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository

from bank_djago.core.nasabah import Nasabahh




class NasabahLoader:

    @staticmethod
    def muat_nasabah(nik):
        from bank_djago.penyimpanan.loaders.pinjaman_loader import PinjamanLoader
        data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(nik)

        if data_nasabah is None:
            return None

        nasabah = Nasabahh(nama=data_nasabah["nama"],
                           alamat=data_nasabah["alamat"],
                           nik=data_nasabah["nik"])


        RekeningLoader.muat_semua_rekening(nasabah)
        DepositoLoader.muat_deposito(nasabah)
        PinjamanLoader.muat_pinjaman(nasabah)
        NotifikasiLoader.muat_notifikasi(nasabah)

        return nasabah




    @staticmethod
    def rangkai_nasabah(data_nasabah):
        if data_nasabah is None:
            raise ValueError("Data nasabah tidak ditemukan")

        return Nasabahh(nama=data_nasabah['nama'],
                        alamat=data_nasabah['alamat'],
                        nik=data_nasabah['nik'])

