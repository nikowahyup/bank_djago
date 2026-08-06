import random
import datetime

from .rekening import RekeningGold,RekeningReguler,RekeningPrioritas,RekeningPlatinum
from .nasabah import Nasabahh
from bank_djago.services.transaksi import TransaksiService
from bank_djago.utils.utililty import Utilitas
from ..services.admin.admin_audit import Audit
from ..services.scheduler import Scheduler
from bank_djago.services.admin.menu_admin import MenuAdmin


kelas_rekening = {
            "Reguler"  : RekeningReguler,
            "Prioritas": RekeningPrioritas,
            "Gold"     : RekeningGold,
            "Platinum" : RekeningPlatinum}

class Bank:
    def __init__(self,nama,data_audit,data_rekening=None,data_nasabah=None):
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

    # ------------------------------------------------------------------------------------------------------------------------------
    def cari_rekening(self,rekening:str):
        return self.rekening_index.get(rekening,None)

    def cek_saldo(self,norek:str,pin:str):
        rekening = self.autentikasi_rekening(norek,pin)
        return rekening



    # ------------------------------------------------------------------------------------------------------------------------------
    def setor_tunai(self,norek:str,pin:str):
        rekening = self.autentikasi_rekening(norek,pin)
        return rekening
    # ------------------------------------------------------------------------------------------------------------------------------
    def tarik_tunai(self,norek:str,pin:str):
        rekening = self.autentikasi_rekening(norek,pin)
        return rekening
    # ------------------------------------------------------------------------------------------------------------------------------
    def transfer(self,norek_pengirim:str,pin:str,norek_penerima:str):
        pengirim = self.autentikasi_rekening(norek_pengirim,pin)
        penerima = self.cari_penerima(pengirim, norek_penerima)
        TransaksiService.transfer(self,pengirim, penerima)

    # ------------------------------------------------------------------------------------------------------------------------------
    def lihat_riwayat(self,norek):
        rekening = self.cari_rekening(norek)
        if not rekening:
            raise ValueError("Nomor rekening tidak terdaftar")
        return rekening
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
    def autentikasi_rekening(self,norek,pin):
        rekening = self.cari_rekening(norek)
        if not rekening:
            raise ValueError("Nomor rekening tidak terdaftar")
        if rekening.status != "aktif":
            raise ValueError(f"Rekening telah di{rekening.status}")

        if not rekening.cek_pin(pin):
            raise ValueError("PIN salah")

        return rekening


    def cari_nasabah(self,nik):
        return self.data_nasabah.get(nik,None)

    # ------------------------------------------------------------------------------------------------------------------------------
    def cari_penerima(self,pengirim,norek_penerima):
        penerima = self.cari_rekening(norek_penerima)
        if not penerima:
            raise ValueError("Penerima tidak terdaftar")
        if penerima == pengirim:
            raise ValueError("Tidak dapat transfer ke akun sendiri")
        return penerima
    # ------------------------------------------------------------------------------------------------------------------------------
    def layanan_nasabah(self,nik_nasabah):
        nasabah = self.cari_nasabah(nik_nasabah)
        if not nasabah:
            raise ValueError("NIK tidak terdaftar")

        return nasabah
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
    def tutup_rekening(self,rekening,pilihan):
        if pilihan == "1":
            TransaksiService.transfer_semua_saldo(self,rekening)
        elif pilihan == "2":
            TransaksiService.tarik_semua_saldo(self,rekening)
        return True
    # ------------------------------------------------------------------------------------------------------------------------------
    def proses_harian(self):

            Scheduler.jalankan(self)
    # ------------------------------------------------------------------------------------------------------------------------------
    def debug_bunga(self, bulan=1):
        for rekening in self.rekening_index.values():
            rekening.dapat_bunga -= datetime.timedelta(days=bulan * 31)

    def debug_admin(self,bulan=1):
        for rekening in self.rekening_index.values():
            rekening.waktu_bayar_admin -= datetime.timedelta(days=bulan * 31)

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
        return True

    def blokir_rekening(self,rekening,alasan):
        if rekening.status == "tutup":
            return False
        rekening.alasan_blokir = alasan
        rekening.status = "blokir"

        return True
    def buka_blokir(self,rekening):
        if rekening.status == "tutup":
            return False
        rekening.status = "aktif"
        return True

    def rekap(self):
        MenuAdmin.menu(self)

    def rekap_umum(self):
        total_nasabah  = len(self.data_nasabah)
        total_rekening = len(self.rekening_index)
        total_saldo = sum(rekening.saldo for rekening in self.rekening_index.values())

        return total_nasabah,total_rekening,total_saldo

    def rekap_jumlah_rekening(self):
        reguler = prioritas = gold = platinum = 0

        for rekening in self.rekening_index.values():
            if rekening.level   == 1:
                reguler   += 1
            elif rekening.level == 2:
                prioritas += 1
            elif rekening.level == 3:
                gold      += 1
            elif rekening.level == 4:
                platinum  += 1

        return reguler,prioritas,gold,platinum

    def rekap_status_rekening(self):
        aktif = blokir = tutup = 0

        for rekening in self.rekening_index.values():
            if rekening.status   == "aktif":
                aktif += 1
            elif rekening.status == "blokir":
                blokir += 1
            elif rekening.status == "tutup":
                tutup  += 1

        return aktif,blokir,tutup




    def total_saldo_tiap_rekening(self):
        reguler = prioritas = gold = platinum = 0

        for rekening in self.rekening_index.values():
            if rekening.level == 1:
                reguler += rekening.saldo

            elif rekening.level == 2:
                prioritas += rekening.saldo

            elif rekening.level == 3:
                gold += rekening.saldo

            elif rekening.level == 4:
                platinum += rekening.saldo
        return reguler, prioritas, gold, platinum


    def saldo_terbesar(self):
        rekening_besar = max(self.rekening_index.values(),key=lambda r:r.saldo)
        return rekening_besar

    def saldo_terkecil(self):
        rekening_kecil = min(self.rekening_index.values(),key=lambda r:r.saldo)
        return rekening_kecil



    def tambah_audit(self,kategori,jenis,log,nama=None,nik=None,norek=None):
        audit = {"kategori":kategori,
                 "waktu":Utilitas.waktu_sekarang(),
                 "jenis":jenis.upper(),
                 "log":log}
        if nik is not None:
            audit["nik"] = nik
        if nama is not None:
            audit["nama"] = nama
        if norek is not None:
            audit["rekening"] = norek
        self.audit_log.append(audit)

    def cari_kategori_audit(self,kategori):
        return [item for item in self.audit_log
                if item["kategori"] == kategori]

    def lihat_audit(self):
        Audit.menu_tampilkan_audit(self)

    def verifikasi_admin(self,password):
        return password == self._password_admin


    def reset_pin(self,rekening,pin_baru):
        rekening.ganti_pin(pin_baru)
        return True