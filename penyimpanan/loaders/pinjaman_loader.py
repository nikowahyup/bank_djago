import datetime

from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository

from bank_djago.core.pinjaman import Pinjaman
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi

from bank_djago.utils.utility import StatusPinjaman


class PinjamanLoader:


    @staticmethod
    def muat_pinjaman(nasabah):

        daftar_pinjaman = PinjamanRepository.cari_semua_pinjaman_dengan_nik(nasabah.NIK)

        rekening_index = {rekening.norek : rekening for rekening in nasabah.rekening}

        for data_pinjaman in daftar_pinjaman:

            rekening = rekening_index.get(data_pinjaman["norek"])

            if rekening is None:
                raise ValueError(f"Rekening untuk pinjaman ber-ID {data_pinjaman['id']} tidak ditemukan")

            pinjaman = Pinjaman(pemilik=nasabah,
                                rekening=rekening,
                                nominal_pinjaman=data_pinjaman["nominal_pinjaman"],
                                bunga=data_pinjaman["bunga"],
                                tenor=data_pinjaman["tenor"],
                                id=data_pinjaman["id"])

            pinjaman.status = StatusPinjaman(data_pinjaman['status'])
            pinjaman.cicilan_tetap = data_pinjaman["cicilan_tetap"]
            pinjaman.cicilan_terbayar = data_pinjaman["cicilan_terbayar"]
            pinjaman.sisa_pokok = data_pinjaman["sisa_pokok"]
            tanggal_pencairan = (datetime.date.fromisoformat(data_pinjaman["tanggal_pencairan"]) if data_pinjaman["tanggal_pencairan"] is not None else None)
            tanggal_jatuh_tempo = (datetime.date.fromisoformat(data_pinjaman["tanggal_jatuh_tempo"]) if data_pinjaman["tanggal_jatuh_tempo"] is not None else None)
            pinjaman.tanggal_pencairan = tanggal_pencairan
            pinjaman.tanggal_jatuh_tempo = tanggal_jatuh_tempo

            nasabah.daftar_pinjaman.append(pinjaman)



    @staticmethod
    def rangkai_pinjaman(data_pinjaman,nasabah,rekening):


        pinjaman = Pinjaman(pemilik=nasabah,
                                rekening=rekening,
                                nominal_pinjaman=data_pinjaman["nominal_pinjaman"],
                                bunga=data_pinjaman["bunga"],
                                tenor=data_pinjaman["tenor"],
                                id=data_pinjaman["id"])

        pinjaman.status = StatusPinjaman(data_pinjaman['status'])
        pinjaman.cicilan_tetap = data_pinjaman["cicilan_tetap"]
        pinjaman.cicilan_terbayar = data_pinjaman["cicilan_terbayar"]
        pinjaman.sisa_pokok = data_pinjaman["sisa_pokok"]
        tanggal_pencairan = (datetime.date.fromisoformat(data_pinjaman["tanggal_pencairan"]) if data_pinjaman["tanggal_pencairan"] is not None else None)
        tanggal_jatuh_tempo = (datetime.date.fromisoformat(data_pinjaman["tanggal_jatuh_tempo"]) if data_pinjaman["tanggal_jatuh_tempo"] is not None else None)
        pinjaman.tanggal_pencairan = tanggal_pencairan
        pinjaman.tanggal_jatuh_tempo = tanggal_jatuh_tempo

        return pinjaman


    @staticmethod
    def muat_semua_pinjaman_aktif():


        koneksi = buat_koneksi()

        nasabah_index = {}
        rekening_index = {}
        daftar_pinjaman_aktif = []

        try:
            daftar_pinjaman = PinjamanRepository.cari_semua_pinjaman_aktif(koneksi=koneksi)

            for data_pinjaman in daftar_pinjaman:

                norek = data_pinjaman['norek']
                nik = data_pinjaman['nik_pemilik']

                if nik not in nasabah_index:
                    data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(nik,koneksi)

                    if data_nasabah is None:
                        raise ValueError(f"Nasabah untuk pinjaman {data_pinjaman['id']} tidak ditemukan")

                    nasabah_index[nik] = NasabahLoader.rangkai_nasabah(data_nasabah)


                nasabah = nasabah_index[nik]

                if norek not in rekening_index:
                    data_rekening = RekeningRepository.cari_rekening_dengan_norek(norek, koneksi)

                    if data_rekening is None:
                        raise ValueError(f"Rekening untuk pinjaman {data_pinjaman['id']} tidak ditemukan")

                    rekening_index[norek] = RekeningLoader.rangkai_rekening(data_rekening, nasabah)

                rekening = rekening_index[norek]
                nasabah.rekening.append(rekening)


                pinjaman = PinjamanLoader.rangkai_pinjaman(
                                                            data_pinjaman=data_pinjaman,
                                                            nasabah=nasabah,
                                                            rekening=rekening
                                                            )

                nasabah.daftar_pinjaman.append(pinjaman)
                daftar_pinjaman_aktif.append(pinjaman)


            return daftar_pinjaman_aktif

        finally:
            koneksi.close()




