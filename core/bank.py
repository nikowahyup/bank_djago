import random
import datetime

from .deposito import Deposito
from .nasabah import Nasabahh
from .notifikasi import Notifikasi
from .pinjaman import Pinjaman
# from ..services.scheduler import Scheduler
from ..services.deposito.deposito_service import JenisAro
from ..services.rekening.rekening_service import RekeningService
from bank_djago.utils.utility import StatusPinjaman

class Bank:
    def __init__(self,nama,data_audit,data_nasabah=None,data_rekening=None,data_pinjaman=None):
        self.nama            = nama
        self._password_admin = "admin123"
        self.rekening_index  = {}
        self.data_nasabah    = {}
        self.daftar_pinjaman = []
        self.audit_log = data_audit

        if data_rekening:
            self._muat_rekening(data_rekening)

        if data_nasabah:
            self._muat_nasabah(data_nasabah)



        if data_pinjaman:
            self._muat_pinjaman(data_pinjaman)
    # ------------------------------------------------------------------------------------------------------------------------------
    def _muat_rekening(self, data_rekening):
        for norek, info in data_rekening.items():
            level = info.get("level",1)
            kelas = RekeningService.jenis_rekening[level]["kelas"]
            rekening = kelas.dari_dict(info)
            self.rekening_index[norek] = rekening

    # ------------------------------------------------------------------------------------------------------------------------------
    def _muat_nasabah(self, data_nasabah):
        for nik, info in data_nasabah.items():

            nasabah = Nasabahh.dari_dict(info)

            for norek in info["rekening"]:
                rekening = self.rekening_index[norek]
                nasabah.rekening.append(rekening)
                rekening.pemilik = nasabah

            nasabah.notifikasi = [
                Notifikasi.dari_dict(item)
                for item in info.get("notifikasi", [])
            ]


            self.data_nasabah[nik] = nasabah



    def _muat_pinjaman(self, data_pinjaman):
        for nik, daftar_pinjaman in data_pinjaman.items():
            nasabah = self.data_nasabah[nik]


            if "ID" in daftar_pinjaman:
                daftar_pinjaman = {
                    str(daftar_pinjaman["ID"]): daftar_pinjaman
                }

            for id_pinjaman, info in daftar_pinjaman.items():
                norek = info["rekening"]
                rekening = self.rekening_index[norek]

                pinjaman = Pinjaman(
                    ID=int(info["ID"]),
                    pemilik=nasabah,
                    rekening=rekening,
                    nominal_pinjaman=int(info["nominal_pinjaman"]),
                    bunga=float(info["bunga"]),
                    tenor=int(info["tenor"])
                )

                pinjaman.cicilan_tetap = round(float(
                    info["cicilan_tetap"]
                ))

                pinjaman.sisa_pokok = round(float(
                    info["sisa_pokok"]
                ))

                pinjaman.cicilan_terbayar = int(
                    info["cicilan_terbayar"]
                )

                pinjaman.bunga_bulanan = round(float(
                    info["bunga_bulanan"]
                ))

                pinjaman.status = StatusPinjaman(
                    info["status"]
                )

                if info["tanggal_pencairan"]:
                    pinjaman.tanggal_pencairan = (
                        datetime.date.fromisoformat(
                            info["tanggal_pencairan"]
                        )
                    )

                if info["jatuh_tempo"]:
                    pinjaman.tanggal_jatuh_tempo = (
                        datetime.date.fromisoformat(
                            info["jatuh_tempo"]
                        )
                    )


                self.daftar_pinjaman.append(pinjaman)

                if pinjaman.status in (
                        StatusPinjaman.DIAJUKAN,
                        StatusPinjaman.DISETUJUI,
                        StatusPinjaman.AKTIF
                ):
                    nasabah.pinjaman = pinjaman

            if daftar_pinjaman:
                nasabah.jumlah_pinjaman = max(
                    int(id_pinjaman)
                    for id_pinjaman in daftar_pinjaman
                )

    # ------------------------------------------------------------------------------------------------------------------------------
    def buat_norek(self,digit_awal):
        while True:
            digit_sisa = random.randint(100000000000,999999999999)
            digit_sisa = str(digit_sisa)
            norek = digit_awal+digit_sisa
            if norek not in self.rekening_index:
                break
        return norek

    # ------------------------------------------------------------------------------------------------------------------------------

    def daftar_nasabah(self,nama,nik,alamat,pin,pilihan,setor_awal):
        nasabah_baru  = Nasabahh(nama,alamat,nik)
        rekening_baru = RekeningService.buka_rekening(self,nasabah_baru,pilihan,pin,setor_awal)
        self.data_nasabah[nik] = nasabah_baru
        return nasabah_baru,rekening_baru

    # ------------------------------------------------------------------------------------------------------------------------------

    def cari_nasabah(self,nik):
        return self.data_nasabah.get(nik,None)

    # ------------------------------------------------------------------------------------------------------------------------------

    def cari_rekening(self,rekening:str):
        return self.rekening_index.get(rekening,None)

    # ------------------------------------------------------------------------------------------------------------------------------





    # ------------------------------------------------------------------------------------------------------------------------------

    def data_rekening_dict(self):
        return {
            norek: rekening.ke_dict()
            for norek, rekening in self.rekening_index.items()
        }

    # ------------------------------------------------------------------------------------------------------------------------------

    def data_nasabah_dict(self):
        return {
            nik: nasabah.ke_dict()
            for nik, nasabah in self.data_nasabah.items()
        }

    def data_pinjaman_dict(self):
        return {
                pinjaman.pemilik.NIK : pinjaman.ke_dict()
        for pinjaman in self.daftar_pinjaman}
    # ------------------------------------------------------------------------------------------------------------------------------

    # def proses_harian(self):
    #         tanggal = datetime.date(2028,8,13)
    #         Scheduler.jalankan(self,tanggal)


    def verifikasi_admin(self,password):
        return password == self._password_admin

    # ------------------------------------------------------------------------------------------------------------------------------





