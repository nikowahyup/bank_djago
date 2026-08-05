import datetime


class BiayaAdminService:


    @staticmethod
    def potong_admin(rekening):

        hari_ini = datetime.date.today()

        bulan = (
                (hari_ini.year - rekening.waktu_bayar_admin.year) * 12
                + hari_ini.month
                - rekening.waktu_bayar_admin.month
        )

        if hari_ini.day < rekening.waktu_bayar_admin.day:
            bulan -= 1

        if bulan <= 0:
            return

        total_admin = rekening.biaya_admin * bulan

        rekening.kurangi_saldo(total_admin)

        rekening.waktu_bayar_admin = hari_ini

        simpan = {
            "kategori":"sistem",
            "jenis": "biaya admin",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"BIAYA ADMIN | Jumlah Rp{total_admin:,}".replace(",", ".")
        }
        rekening.simpan_riwayat(simpan)