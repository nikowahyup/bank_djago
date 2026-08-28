import datetime

from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
# from bank_djago.utils.tests.test_service.test_deposito import daftar_riwayat
from bank_djago.core.deposito import Deposito


# from bank_djago.utils.tests.test_service.test_deposito import daftar_deposito


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