import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository

from bank_djago.core.deposito import Deposito
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository

from bank_djago.core.nasabah import Nasabahh
from bank_djago.penyimpanan.sqlite.database import buat_koneksi



class DepositoLoader:

    @staticmethod
    def muat_deposito(nasabah):


        daftar_deposito = DepositoRepository.cari_deposito_dengan_nik(nasabah.NIK)

        rekening_index = {rekening.norek : rekening for rekening in nasabah.rekening}

        for data in daftar_deposito:
            rekening = rekening_index.get(data["norek"])

            if rekening is None:
                raise ValueError(f"Rekening untuk deposito {data["id"]} tidak ditemukan")

            deposito = Deposito(pemilik=nasabah,
                                rekening=rekening,
                                nominal=data["nominal"],
                                bunga=data["bunga"],
                                id=data["id"],
                                lama_bulan=data["lama_bulan"],
                                tanggal_buka=datetime.date.fromisoformat(data["tanggal_buka"]),
                                tanggal_jatuh_tempo=datetime.date.fromisoformat(data["jatuh_tempo"]))

            deposito.status = data["status"]
            deposito.jenis_aro = data["jenis_aro"]
            deposito.lama_aro = data["lama_aro"]

            proses_aro = data["proses_aro"]
            deposito.proses_aro = (
                datetime.date.fromisoformat(proses_aro)
                if proses_aro is not None
                else None
            )

            nasabah.deposito.append(deposito)

    @staticmethod
    def muat_semua_deposito_aktif():
        koneksi = buat_koneksi()

        nasabah_index = {}
        rekening_index = {}
        daftar_deposito_aktif = []

        try:
            data_deposito = DepositoRepository.cari_semua_deposito_aktif(koneksi=koneksi)
            for data_deposito in data_deposito:
                norek = data_deposito["norek"]

                if norek in rekening_index:
                    rekening = rekening_index[norek]
                    nasabah = rekening.pemilik


                else:
                    data_rekening = RekeningRepository.cari_rekening_dengan_norek(norek=norek,koneksi=koneksi)
                    if data_rekening is None:
                        raise ValueError(f"Rekening untuk deposito ber-ID {data_deposito['id']} tidak ditemukan")

                    nik = data_rekening["nik_pemilik"]

                    if nik in nasabah_index:
                        nasabah = nasabah_index[nik]

                    else:


                        data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(nik=nik,koneksi=koneksi)
                        if data_nasabah is None:
                            raise ValueError(f"Nasabah untuk deposito ber-ID {data_deposito['id']} tidak ditemukan")

                        nasabah = Nasabahh(nama=data_nasabah["nama"],alamat=data_nasabah["alamat"],nik=data_nasabah["nik"])
                        nasabah_index[nik] = nasabah

                    rekening = RekeningLoader.rangkai_rekening(data_rekening=data_rekening, nasabah=nasabah)


                    rekening_index[rekening.norek] = rekening

                    nasabah.rekening.append(rekening)

                deposito = Deposito(pemilik=nasabah,
                                    rekening=rekening,
                                    nominal=data_deposito["nominal"],
                                    bunga=data_deposito["bunga"],
                                    id=data_deposito["id"],
                                    lama_bulan=data_deposito["lama_bulan"],
                                    tanggal_buka=datetime.date.fromisoformat(data_deposito["tanggal_buka"]),
                                    tanggal_jatuh_tempo=datetime.date.fromisoformat(data_deposito["jatuh_tempo"]))

                deposito.status = data_deposito["status"]
                deposito.jenis_aro = data_deposito["jenis_aro"]
                deposito.lama_aro = data_deposito["lama_aro"]

                proses_aro = data_deposito["proses_aro"]
                deposito.proses_aro = (
                    datetime.date.fromisoformat(proses_aro)
                    if proses_aro is not None
                    else None
                )

                nasabah.deposito.append(deposito)
                daftar_deposito_aktif.append(deposito)

            return daftar_deposito_aktif

        finally:
            koneksi.close()