import random
import datetime


from .deposito import Deposito
from .rekening import RekeningGold,RekeningReguler,RekeningPrioritas,RekeningPlatinum
from .nasabah import Nasabahh
from ..services.scheduler import Scheduler
from ..services.deposito.deposito_service import StatusDeposito, JenisAro, DepositoService

from ..utils.utililty import Utilitas

kelas_rekening = {
            "Reguler"  : RekeningReguler,
            "Prioritas": RekeningPrioritas,
            "Gold"     : RekeningGold,
            "Platinum" : RekeningPlatinum}

class Bank:
    def __init__(self,nama,data_audit,data_rekening=None,data_nasabah=None,data_deposito=None):
        self.nama            = nama
        self._password_admin = "admin123"
        self.rekening_index  = {}
        self.data_nasabah    = {}
        self.audit_log = data_audit
        self.jenis_rekening  = {
            1: {
                "prefix": "4001",
                "kelas": RekeningReguler,
                "nama": "Reguler",
                "minimal_upgrade": 0
            },
            2: {
                "prefix": "3001",
                "kelas": RekeningPrioritas,
                "nama": "Prioritas",
                "minimal_upgrade": 3_000_000
            },
            3: {
                "prefix": "2001",
                "kelas": RekeningGold,
                "nama": "Gold",
                "minimal_upgrade": 50_000_000
            },
            4: {
                "prefix": "1001",
                "kelas": RekeningPlatinum,
                "nama": "Platinum",
                "minimal_upgrade": 200_000_000
            }
        }

        if data_rekening:
            self._muat_rekening(data_rekening)

        if data_nasabah:
            self._muat_nasabah(data_nasabah)

        if data_deposito:
            self._muat_deposito(data_deposito)
    # ------------------------------------------------------------------------------------------------------------------------------
    def _muat_rekening(self, data_rekening):
        for norek, info in data_rekening.items():
            level = info.get("level",1)
            kelas = self.jenis_rekening[level]["kelas"]
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


            self.data_nasabah[nik] = nasabah

    def _muat_deposito(self,data_deposito):
        for nik,daftar_deposito in data_deposito.items():
            nasabah = self.data_nasabah[nik]

            for id_deposito,info in daftar_deposito.items():
                norek = info["norek"]
                rekening = self.rekening_index[norek]



                deposito = Deposito(pemilik=nasabah,
                                    rekening=rekening,
                                    nominal=info["nominal"],
                                    bunga=info["bunga"],
                                    id=int(id_deposito),
                                    lama_bulan=info["lama_bulan"],
                                    tanggal_buka=datetime.date.fromisoformat(info["tanggal_buka"]),
                                    tanggal_jatuh_tempo=datetime.date.fromisoformat(info["jatuh_tempo"])
                                    )
                deposito.status = info["status"]
                deposito.lama_aro = info.get("lama_aro",None)
                deposito.jenis_aro = info.get("jenis_aro",JenisAro.TIDAK)

                nasabah.deposito.append(deposito)
                if daftar_deposito:
                    nasabah.jumlah_deposito = max(
                        int(id_deposito)
                        for id_deposito in daftar_deposito
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
        rekening_baru = self.buka_rekening(nasabah_baru,pilihan,pin,setor_awal)
        self.data_nasabah[nik] = nasabah_baru
        return nasabah_baru,rekening_baru

    def cari_nasabah(self,nik):
        return self.data_nasabah.get(nik,None)
    # ------------------------------------------------------------------------------------------------------------------------------
    def cari_rekening(self,rekening:str):
        return self.rekening_index.get(rekening,None)
    # ------------------------------------------------------------------------------------------------------------------------------
    def autentikasi_rekening(self,norek,pin):
        rekening = self.cari_rekening(norek)
        if not rekening:
            raise ValueError("Nomor rekening tidak terdaftar")

        if rekening.status != "aktif":
            raise ValueError(f"Rekening telah di{rekening.status}")

        if not rekening.cek_pin(pin):
            raise ValueError("PIN salah")
    # ------------------------------------------------------------------------------------------------------------------------------
        return rekening
    def cari_penerima(self,pengirim,norek_penerima):
        penerima = self.cari_rekening(norek_penerima)

        if not penerima:
            raise ValueError("Penerima tidak terdaftar")

        if penerima == pengirim:
            raise ValueError("Tidak dapat transfer ke akun sendiri")

        return penerima
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
    # ------------------------------------------------------------------------------------------------------------------------------
    def buka_rekening(self,nasabah,pilihan,pin,setor_awal):
        info      = self.jenis_rekening[pilihan]
        prefix    = info["prefix"]
        kelas_rek = info["kelas"]

        norek         = self.buat_norek(prefix)
        rekening_baru = kelas_rek(norek,pin,nasabah)

        if setor_awal < rekening_baru.saldosetor_min:
            raise ValueError("Saldo awal tidak memenuhi saldo setor minimum")

        rekening_baru.tambah_saldo(setor_awal)
        self.rekening_index[norek] = rekening_baru
        nasabah.rekening.append(rekening_baru)

        return rekening_baru
    # ------------------------------------------------------------------------------------------------------------------------------
    def proses_harian(self):
            Scheduler.jalankan(self)
            self.cek_jatuh_tempo()
    # ------------------------------------------------------------------------------------------------------------------------------
    def debug_bunga(self, bulan=1):
        for rekening in self.rekening_index.values():
            rekening.dapat_bunga -= datetime.timedelta(days=bulan * 31)
    # ------------------------------------------------------------------------------------------------------------------------------
    def debug_admin(self,bulan=1):
        for rekening in self.rekening_index.values():
            rekening.waktu_bayar_admin -= datetime.timedelta(days=bulan * 31)
    # ------------------------------------------------------------------------------------------------------------------------------
    def upgrade_rekening(self,rekening_lama, target_level):

        info = self.jenis_rekening[target_level]
        kelas_tujuan = info["minimal_upgrade"]
        if rekening_lama.saldo < kelas_tujuan:
            return False

        rekening_baru = info["kelas"](
            norek=rekening_lama.norek,
            pin=rekening_lama.pin,
            pemilik=rekening_lama.pemilik
        )

        rekening_baru.set_saldo(rekening_lama.saldo)
        rekening_baru.riwayat = rekening_lama.riwayat
        self.rekening_index[rekening_baru.norek] = rekening_baru
        index = rekening_lama.pemilik.rekening.index(rekening_lama)
        rekening_lama.pemilik.rekening[index] = rekening_baru

        return rekening_baru
    # ------------------------------------------------------------------------------------------------------------------------------
    def downgrade_rekening(self,nasabah,rekening_lama,target_level):
        info = self.jenis_rekening[target_level]

        rekening_baru = info["kelas"](
            norek=rekening_lama.norek,
            pin=rekening_lama.pin,
            pemilik=rekening_lama.pemilik)

        rekening_baru.set_saldo(rekening_lama.saldo)
        rekening_baru.riwayat = rekening_lama.riwayat
        self.rekening_index[rekening_lama.norek] = rekening_baru
        index = nasabah.rekening.index(rekening_lama)
        nasabah.rekening[index] = rekening_baru
        return rekening_baru
    # ------------------------------------------------------------------------------------------------------------------------------
    def verifikasi_admin(self,password):
        return password == self._password_admin

    # ------------------------------------------------------------------------------------------------------------------------------

    def cek_jatuh_tempo(self):

        hari_ini = datetime.date.today()

        for nasabah in self.data_nasabah.values():
            for deposito in nasabah.deposito:

                if deposito.status != StatusDeposito.AKTIF:
                    continue

                if deposito.jatuh_tempo > hari_ini:
                    continue

                if deposito.jenis_aro == JenisAro.TIDAK:
                    DepositoService.cairkan_deposito(self,deposito)
                    deposito.status = StatusDeposito.SELESAI

                else:
                    DepositoService.perpanjangan(self,deposito)




    def debug_depo(self, bulan=1):
        for nasabah in self.data_nasabah.values():
            for deposito in nasabah.deposito:
                deposito.jatuh_tempo = Utilitas.tambah_bulan(
                    deposito.jatuh_tempo,
                    -bulan
                )

