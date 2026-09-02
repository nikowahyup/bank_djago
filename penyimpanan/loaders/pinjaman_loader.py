import datetime

from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository

from bank_djago.core.pinjaman import Pinjaman
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