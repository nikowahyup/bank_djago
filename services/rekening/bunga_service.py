from bank_djago.utils.utility import Utilitas
import datetime

class BungaService:

    @staticmethod
    def hitung_bulan(rekening):
        hari_ini = datetime.date.today()

        bulan = ((hari_ini.year - rekening.dapat_bunga.year)*12 + hari_ini.month - rekening.dapat_bunga.month)
        if hari_ini.day < rekening.dapat_bunga.day:
            bulan -= 1

        return bulan

    @staticmethod
    def berikan_bunga(rekening):
        bulan = BungaService.hitung_bulan(rekening)
        if bulan <= 0:
            return

        bunga_bulanan = round(rekening.saldo*rekening.bunga/12)
        bunga_total = bunga_bulanan*bulan

        rekening.tambah_saldo(bunga_total)

        rekening.dapat_bunga = datetime.date.today()
        bulan = Utilitas.nama_bulan(rekening.dapat_bunga)
        waktu = f"{bulan.upper()} {rekening.dapat_bunga.year}"
        log = f'BUNGA {waktu} | Jumlah Rp{bunga_total:,}'.replace(",",'.')
        simpan = {
            "kategori":"transaksi",
            "jenis": "bunga",
            "waktu": datetime.datetime.now().isoformat(),
            "log": log
        }
        rekening.simpan_riwayat(simpan)


        return bunga_total
