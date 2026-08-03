import random
import datetime

from .rekening import RekeningGold,RekeningReguler,RekeningPrioritas,RekeningPlatinum
from .nasabah import Nasabahh
from bank_djago.services.transaksi import TransaksiService,RiwayatService
from bank_djago.services.layanan_nasabah import LayananNasabah
from bank_djago.utils.utililty import Utilitas
from ..services.scheduler import Scheduler
from bank_djago.utils.validator import Validator
from bank_djago.services.admin import AdminService
kelas_rekening = {
            "Reguler"  : RekeningReguler,
            "Prioritas": RekeningPrioritas,
            "Gold"     : RekeningGold,
            "Platinum" : RekeningPlatinum}

class Bank:
    def __init__(self,nama,data_audit,data_rekening=None,data_nasabah=None):
        self.nama           = nama
        self.rekening_index = {}
        self.data_nasabah   = {}
        self.audit_log = data_audit
        self.jenis_rekening = {
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
    def daftar_nasabah(self):
        print("="*20,"DAFTAR JADI NASABAH",'='*20)

        nama   = input("Masukkan nama lengkap Anda: ")
        nik    = input("Masukkan NIK Anda: ")
        alamat = input("Masukkan alamat Anda: ")
        pin    = input("Buat PIN 6 digit angka: ")
        try:
            Validator.validasi_nasabah(nama,nik,alamat,pin)
        except ValueError as e:
            for pesan in e.args[0]:
                print(f"❌",pesan)
            return
        if nik in self.data_nasabah:
            buka_rekening = input("⚠️ NIK sudah terdaftar. Apakah Anda mau membuka rekening lain(ya/tidak): ").lower()
            if buka_rekening in ("ya","y","iya"):
                LayananNasabah.buka_rekening(self,self.data_nasabah[nik])
                return
            elif buka_rekening in ('t','tidak','no'):
                print("🙏 Anda bisa melihat info nasabah di menu Layanan Nasabah")
                return

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
            self.tambah_audit(kategori="rekening",jenis="buka rekening",log="Buka Rekening Pertama")
            Utilitas.sapaan(nasabah,rekening_baru)
            self.tambah_audit(kategori="nasabah",jenis="daftar",log="Pendaftaran Menjadi Nasabah Bank Djago",nama=nasabah.nama,nik=nasabah.NIK)

        except ValueError:
            print("Tolong pilih menggunakan angka")

    # ------------------------------------------------------------------------------------------------------------------------------
    def cari_rekening(self,rekening):
        return self.rekening_index.get(rekening,None)

    def cek_saldo(self):
        print("="*15,"INFO REKENING","="*15)
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
    # ------------------------------------------------------------------------------------------------------------------------------
    def setor_tunai(self):
        print('='*15,"SETOR TUNAI","="*15)
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
        TransaksiService.setor_tunai(self,nasabah)
    # ------------------------------------------------------------------------------------------------------------------------------
    def tarik_tunai(self):
        print('='*15,"TARIK TUNAI","="*15)
        nasabah = self.autentikasi_rekening()
        if not nasabah:
            return
        TransaksiService.tarik_tunai(self,nasabah)
    # ------------------------------------------------------------------------------------------------------------------------------
    def transfer(self):
        print('='*15,"TRANSFER SALDO","="*15)
        pengirim = self.autentikasi_rekening()
        if not pengirim:
            return
        penerima = self.cari_penerima(pengirim)
        if not penerima:
            return
        TransaksiService.transfer(self,pengirim,penerima)
    # ------------------------------------------------------------------------------------------------------------------------------
    def lihat_riwayat(self):
        print('='*15,"RIWAYAT TRANSAKSI","="*15)
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
            print("❌ Nomor rekening tidak terdaftar\n")
            return
        if rekening.status != "aktif":
            print(f"⚠️ Rekening telah di{rekening.status}!")
            return
        percobaan = 0
        while percobaan < 3:
            pin = input("Masukkan PIN Anda: ")
            if rekening.cek_pin(pin):
                print()
                print("Rekening Ditemukan!")
                Utilitas.info_rekening(rekening)
                print()
                return rekening

            percobaan += 1
            print("❌ PIN salah. Coba lagi")

        print("Anda telah salah input PIN 3x. Anda akan diblokir!")
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
            print("❌ Nomor rekening penerima tidak terdaftar\n")
            return
        if penerima == pengirim:
            print("❌ Tidak dapat melakukan transfer ke rekening sendiri!\n")
            return
        if penerima.status != "aktif":
            print(f"Rekening penerima telah di{penerima.status}!")
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
        print("️⚠️ Anda wajib menyetorkan uang setoran awal")
        setor_awal = int(input("Masukkan setoran awal Anda: "))
        if setor_awal < rekening_baru.saldosetor_min:
            print("Setor awal belum memenuhi syarat minimal")
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

    def upgrade_rekening(self, nasabah, rekening_lama, target_level):

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
        index = nasabah.rekening.index(rekening_lama)
        nasabah.rekening[index] = rekening_baru


        return True

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
        rekening.alasan_blokir = alasan
        rekening.status = "blokir"
        return True

    def rekap(self):
        AdminService.rekap_bank(self)

    def rekap_umum(self):
        total_nasabah  = len(self.data_nasabah)
        total_rekening = len(self.rekening_index)
        total_saldo = 0
        for rekening in self.rekening_index.values():
            saldo = rekening.saldo
            total_saldo+=saldo
        AdminService.umum(total_nasabah,total_rekening,total_saldo)

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

        AdminService.rekap_rekening(reguler,prioritas,gold,platinum)

    def rekap_status_rekening(self):
        aktif = blokir = tutup = 0

        for rekening in self.rekening_index.values():
            if rekening.status   == "aktif":
                aktif += 1
            elif rekening.status == "blokir":
                blokir += 1
            elif rekening.status == "tutup":
                tutup  += 1

        AdminService.rekap_status(aktif,blokir,tutup)




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
        AdminService.total_saldo_tiap_rekening(reguler, prioritas, gold, platinum)


    def saldo_terbesar(self):
        rekening_besar = max(self.rekening_index.values(),key=lambda r:r.saldo)
        AdminService.saldo_terbesar(rekening_besar)

    def saldo_terkecil(self):
        rekening_kecil = min(self.rekening_index.values(),key=lambda r:r.saldo)
        AdminService.saldo_terkecil(rekening_kecil)



    def tambah_audit(self,kategori,jenis,log,nama=None,nik=None,norek=None):
        audit = {"kategori":kategori,
                 "waktu":Utilitas.waktu_sekarang(),
                 "jenis":jenis,
                 "log":log}
        if nik is not None:
            audit["NIK"] = nik
        if nama is not None:
            audit["nama"] = nama
        if norek is not None:
            audit["Rekening"] = norek
        self.audit_log.append(audit)
