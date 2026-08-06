import datetime,time
from ..utils.utililty import Utilitas
from bank_djago.services.limit import LimitService




class TransaksiService:

    @staticmethod
    def cek_saldo(nasabah):
        nasabah.cek_saldo()

    @staticmethod
    def animasi():
        print("Proses", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(1)
        print()

    @staticmethod
    def setor_tunai(rekening,nominal):
        if nominal < 10000:
            raise ValueError("Minimal setor adalah Rp10.0000")
        rekening.tambah_saldo(nominal)



    @staticmethod
    def tarik_tunai(rekening,nominal):
        if nominal < 10000:
            raise ValueError("Minimal tari adalah Rp10.000")
        if rekening.saldo - nominal < rekening.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika Anda menarik sebesar Rp{Utilitas.format_rupiah(nominal)}")
        rekening.kurangi_saldo(nominal)

    @staticmethod
    def transfer(pengirim,penerima,nominal):
        if nominal < 10000:
            raise ValueError("Minimal transfer adalah Rp10.0000")
        LimitService.reset_limit(pengirim)
        total = nominal + pengirim.pajak
        if pengirim.limit_harian is not None:
            if pengirim.limit_sisa < nominal:
                raise ValueError("Limit harian telah tercapai")

        if pengirim.saldo - total < pengirim.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika transfer Rp{Utilitas.format_rupiah(nominal)}")

        pengirim.kurangi_saldo(total)
        penerima.tambah_saldo(nominal)
        if pengirim.limit_harian is not None:
            pengirim.limit_sisa -= nominal


    @staticmethod
    def transfer_semua_saldo(bank,rekening):
        penerima = bank.cari_penerima(rekening)
        if not penerima:
            return
        jumlah = rekening.saldo
        rekening.kurangi_saldo(jumlah)
        penerima.tambah_saldo(jumlah)
        rekening.status = "tutup"
        penerima.riwayat.append(RiwayatService.transfer_terima(jumlah, rekening))
        print(f"✅ Rp{Utilitas.format_rupiah(jumlah)} telah masuk ke rekening {penerima.pemilik.nama}")
        rekening.penutupan = datetime.date.today()


    @staticmethod
    def tarik_semua_saldo(bank,rekening):
        jumlah = rekening.saldo
        rekening.kurangi_saldo(jumlah)
        rekening.status = "tutup"
        print(f"✅ Rp{Utilitas.format_rupiah(jumlah)} berhasil ditarik dari rekening Anda")
        rekening.penutupan = datetime.date.today()

class RiwayatService:

    @staticmethod
    def lihat_riwayat(rekening):
        print('='*23,"RIWAYAT TRANSAKSI",'='*23)
        if not rekening.riwayat:
            print("Belum ada riwayat transaksi")
            return
        print()
        print("1. Lihat Semua Transaksi")
        print("2. Lihat Setor Uang Saja")
        print("3. Lihat Tarik Uang Saja")
        print("4. Lihat Transfer Masuk Saja")
        print("5. Lihat Transfer Keluar Saja")
        print("6. Lihat Upgrade atau Downgrade Rekening Saja")
        pilihan = input("Masukkan pilihan Anda: ")
        print()
        print('='*23,"RIWAYAT TRANSAKSI ANDA",'='*23)
        if pilihan == "1":
            for item in rekening.riwayat:
                print(Utilitas.format_waktu(item["waktu"]), "|", item["log"])
        elif pilihan == "2":
            RiwayatService.tampilkan_riwayat(rekening,"setor uang")
        elif pilihan == "3":
            RiwayatService.tampilkan_riwayat(rekening,"tarik uang")
        elif pilihan == "4":
            RiwayatService.tampilkan_riwayat(rekening,"terima saldo")
        elif pilihan == "5":
            RiwayatService.tampilkan_riwayat(rekening,"transfer saldo")
        elif pilihan == "6":
            RiwayatService.tampilkan_riwayat(rekening,"perubahan")

    @staticmethod
    def transfer_terima(jumlah,pengirim): # untuk penerima

        simpan = {
            "kategori":"transaksi",
            "jenis": "terima saldo",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"TERIMA SALDO | Dari {pengirim.pemilik.nama} | Jumlah Rp{jumlah:,}".replace(",", ".")
        }
        return simpan
    @staticmethod
    def transfer_kirim(jumlah,penerima): # untuk pengirim
        simpan = {
            "kategori":"transaksi",
            "jenis": "transfer saldo",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"TRANSFER SALDO | Penerima {penerima.pemilik.nama} | Jumlah Rp{jumlah:,}".replace(",", ".")
        }
        return simpan

    @staticmethod
    def setor_uang(jumlah):
        simpan = {
            "kategori":"transaksi",
            "jenis": "setor uang",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"SETOR TUNAI | Jumlah Rp{jumlah:,}".replace(",", ".")
        }
        return simpan

    @staticmethod
    def tarik_uang(jumlah):
        simpan = {
            "kategori":"transaksi",
            "jenis": "tarik uang",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"TARIK TUNAI | Jumlah Rp{jumlah:,}".replace(",", ".")
        }
        return simpan

    @staticmethod
    def upgrade_rekening(sebelum,sesudah):
        simpan = {
            "kategori":"sistem",
            "jenis": "perubahan",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"Upgrade Rekening {sebelum} ke {sesudah}"
        }
        return simpan

    @staticmethod
    def alasan_blokir(alasan:str):
        simpan = {
            "kategori":"sistem",
            "jenis": "blokir",
            "waktu": datetime.datetime.now().isoformat(),
            "log": alasan
        }
        return simpan


    @staticmethod
    def tampilkan_riwayat(rekening,jenis):
        log = [item for item in rekening.riwayat if item["jenis"] == jenis]
        if not log:
            print(f"Belum ada riwayat {jenis}")
            return

        for item in log:
            print(Utilitas.format_waktu(item["waktu"]), "|",item["log"])





    @staticmethod
    def downgrade_rekening(sebelum,sesudah):
        simpan = {
            "kategori":"sistem",
            "jenis": "perubahan",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"Turun Rekening {sebelum} ke {sesudah}"
        }
        return simpan