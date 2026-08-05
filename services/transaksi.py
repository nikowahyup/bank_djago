import datetime,time
from ..utils.utililty import Utilitas
from bank_djago.services.limit import LimitService
from bank_djago.utils.ui import UI



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
    def setor_tunai(bank,rekening):
        try:
            jumlah = int(input("Masukkan nominal setor: "))
            TransaksiService.animasi()
            if jumlah <= 0:
                UI.gagal("Nominal harus lebih dari 0\n")
                return

            rekening.tambah_saldo(jumlah)
            log = RiwayatService.setor_uang(jumlah)
            rekening.simpan_riwayat(log)

            rupiah = Utilitas.format_rupiah(jumlah)
            UI.sukses(f"Rp{rupiah} berhasil masuk ke rekening Anda!")
            bank.tambah_audit(kategori="transaksi",jenis="setor uang",log=f"Rp{Utilitas.format_rupiah(jumlah)}",nama=f"{rekening.pemilik.nama}",nik=f"{rekening.pemilik.NIK}",norek=f"{rekening.norek}")


        except ValueError:
            print("Tolong masukkan angka yang valid")


    @staticmethod
    def tarik_tunai(bank,rekening):
        try:
            jumlah = int(input("Masukkan nominal tarik: "))
            TransaksiService.animasi()
            if jumlah <= 0:
                UI.gagal("Penarikan ditolak")
                print("Nominal harus lebih dari 0\n")
                return

            if rekening.saldo - jumlah < rekening.saldosetor_min:
                UI.gagal("Penarikan ditolak")
                print(f"Saldo minimum yang harus tetap di rekening adalah Rp{Utilitas.format_rupiah(rekening.saldosetor_min)}")
                return

            rekening.kurangi_saldo(jumlah)
            log = RiwayatService.tarik_uang(jumlah)
            rekening.simpan_riwayat(log)

            Utilitas.format_rupiah(jumlah)
            print(f"✅ Tarik Tunai Berhasil!")
            print(f"Rp{Utilitas.format_rupiah(jumlah)} telah dipotong dari rekening Anda")
            bank.tambah_audit(kategori="transaksi",jenis="tarik uang",log=f"Rp{Utilitas.format_rupiah(jumlah)}",nama=f"{rekening.pemilik.nama}",nik=f"{rekening.pemilik.NIK}",norek=f"{rekening.norek}")

        except ValueError:
            print("Tolong masukkan angka yang valid")

    @staticmethod
    def transfer(bank,pengirim,penerima):
        try:
            jumlah = int(input("Masukkan nominal transfer: "))
            TransaksiService.animasi()
            if jumlah <= 0:
                UI.gagal("Transfer Gagal!")
                print("Nominal harus lebih dari 0\n")
                return

            LimitService.reset_limit(pengirim)
            if pengirim.limit_harian is not None:
                if pengirim.limit_sisa < jumlah:
                    UI.gagal("Transfer Gagal!")
                    print("Nominal transfer melebihi limit")
                    return

            total = jumlah + pengirim.pajak
            if pengirim.saldo - total < pengirim.saldosetor_min:
                UI.gagal("Transfer Gagal!")
                print(f"Saldo minimum yang harus tetap di rekening adalah Rp{Utilitas.format_rupiah(pengirim.saldosetor_min)}")
                return

            if pengirim.limit_harian is not None:
                pengirim.limit_sisa -= jumlah
            pengirim.kurangi_saldo(total)
            penerima.tambah_saldo(jumlah)

            log_terima = RiwayatService.transfer_terima(jumlah,pengirim)
            log_kirim  = RiwayatService.transfer_kirim(jumlah,penerima)
            pengirim.simpan_riwayat(log_kirim)
            penerima.simpan_riwayat(log_terima)

            rupiah = Utilitas.format_rupiah(jumlah)
            UI.sukses(" Transfer berhasil!")
            print(f'Rp{rupiah} masuk ke rekening {penerima.pemilik.nama}')
            bank.tambah_audit(kategori="transaksi",jenis="transfer saldo",log=f"Penerima {penerima.pemilik.nama} Rp{rupiah}",nama=f"{pengirim.pemilik.nama}",nik=f"{pengirim.pemilik.NIK}",norek=f"{pengirim.pemilik.norek}")
            bank.tambah_audit(kategori="transaksi",jenis="terima saldo",log=f"Dari {pengirim.pemilik.nama} Rp{rupiah}",nama=f"{penerima.pemilik.nama}",nik=f"{penerima.pemilik.NIK}",norek=f"{penerima.pemilik.norek}")
        except ValueError:
            print("Tolong masukkan angka yang valid")

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