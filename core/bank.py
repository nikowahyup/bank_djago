import random
import datetime

from .rekening import RekeningGold,RekeningReguler,RekeningPrioritas,RekeningPlatinum
from .nasabah import Nasabahh
from bank_djago.services.transaksi import TransaksiService,RiwayatService
from bank_djago.services.layanan_nasabah import LayananNasabah
from bank_djago.utils.utililty import Utilitas
from ..services.admin.admin_audit import Audit
from ..services.scheduler import Scheduler
from bank_djago.services.admin.menu_admin import MenuAdmin
from bank_djago.utils.ui import UI

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
    def daftar_nasabah(self,nama,nik,alamat,pin):
        print('='*29,"PILIHAN REKENING","="*30)
        Utilitas.keuntungan_rekening()
        print('='*77)
        print()
        try:
            pilihan = int(input("Masukkan pilihan Anda: "))
            if pilihan not in self.jenis_rekening:
                print("❌ Masukkan pilihan yang valid!")
                return
            nasabah = Nasabahh(nama,alamat,nik)
            self.data_nasabah[nik] = nasabah
            rekening_baru = self.buka_rekening(nasabah,pilihan,pin)
            return nasabah,rekening_baru
        except ValueError:
            print("Tolong pilih menggunakan angka")
    # ------------------------------------------------------------------------------------------------------------------------------
    def cari_rekening(self,rekening):
        return self.rekening_index.get(rekening,None)

    def cek_saldo(self):
        UI.header('CEK SALDO')
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
    # ------------------------------------------------------------------------------------------------------------------------------
    def setor_tunai(self):
        UI.header('SETOR TUNAI')
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
        TransaksiService.setor_tunai(self,nasabah)
    # ------------------------------------------------------------------------------------------------------------------------------
    def tarik_tunai(self):
        UI.header("TARIK TUNAI")
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
        TransaksiService.tarik_tunai(self,nasabah)
    # ------------------------------------------------------------------------------------------------------------------------------
    def transfer(self):
        UI.header("TRANSFER SALDO")
        pengirim = self.autentikasi_rekening()
        if not pengirim:
            return
        penerima = self.cari_penerima(pengirim)
        if not penerima:
            return
        TransaksiService.transfer(self,pengirim,penerima)
    # ------------------------------------------------------------------------------------------------------------------------------
    def lihat_riwayat(self):
        UI.header("RIWAYAT TRANSAKSI")
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
        RiwayatService.lihat_riwayat(nasabah)
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
    def autentikasi_rekening(self):
        norek = input("Masukkan nomor rekening Anda: ")
        rekening = self.cari_rekening(norek)
        if not rekening:
            UI.gagal("Nomor rekening tidak terdaftar\n")
            return
        if rekening.status != "aktif":
            UI.peringatan(f"Rekening telah di{rekening.status}!")
            return
        percobaan = 0
        while percobaan < 3:
            pin = input("Masukkan PIN Anda: ")
            if rekening.cek_pin(pin):
                print()
                UI.sukses("Rekening Ditemukan!")
                UI.wadah_info(rekening.pemilik.nama,rekening.norek,rekening.cek_saldo())
                print()
                return rekening

            percobaan += 1
            UI.gagal("PIN salah. Coba lagi")

        UI.peringatan("Anda telah salah input PIN 3x. Anda akan diblokir!")
        rekening.status = "blokir"
        rekening.alasan_blokir = "Salah input PIN 3x"
        log = RiwayatService.alasan_blokir(rekening.alasan_blokir)
        rekening.simpan_riwayat(log)
        return None






    # ------------------------------------------------------------------------------------------------------------------------------
    def cari_penerima(self,pengirim):
        rekening = input("Masukkan nomor rekening penerima: ")
        penerima = self.cari_rekening(rekening)
        if not penerima:
            UI.gagal("Nomor rekening penerima tidak terdaftar\n")
            return
        if penerima == pengirim:
            UI.gagal("Tidak dapat transfer ke nomor rekening sendiri\n")
            return
        if penerima.status != "aktif":
            UI.gagal(f"Rekening penerima telah di{penerima.status}!")
            return
        return penerima
    # ------------------------------------------------------------------------------------------------------------------------------
    def layanan_nasabah(self):
        nik = input("Masukkan NIK Anda: ")
        if nik not in self.data_nasabah:
            print("Maaf,NIK tidak terdaftar")
            return

        nasabah = self.data_nasabah[nik]
        LayananNasabah.menu_layanan(self,nasabah)
    # ------------------------------------------------------------------------------------------------------------------------------
    def buka_rekening(self,nasabah,pilihan,pin):
        info = self.jenis_rekening[pilihan]
        prefix = info["prefix"]
        kelas_rek = info["kelas"]

        norek = self.buat_norek(prefix)
        rekening_baru = kelas_rek(norek,pin,nasabah)
        UI.peringatan("Anda wajib menyetorkan setoran awal")
        setor_awal = int(input("Masukkan setoran awal Anda: "))
        if setor_awal < rekening_baru.saldosetor_min:
            UI.gagal("Setor awal belum memenuhi syarat minimal")
            return
        rekening_baru.tambah_saldo(setor_awal)
        simpan = {
            "kategori":"transaksi",
            "jenis": "setor uang",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"SETOR AWAL | Jumlah Rp{setor_awal:,}".replace(",", ".")
        }
        self.tambah_audit(kategori="transaksi",jenis="setor uang",log=f"SETOR AWAL |  Rp{setor_awal:,}".replace(",", "."),nama=nasabah.nama,nik=nasabah.NIK,norek=rekening_baru.norek)
        rekening_baru.simpan_riwayat(simpan)
        nasabah.rekening.append(rekening_baru)
        self.rekening_index[norek] = rekening_baru

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