import datetime
class RiwayatTemplate:

    @staticmethod
    def template(kategori,jenis,log):
        return {"kategori":kategori,
                "jenis": jenis.title(),
                "waktu":datetime.datetime.now().isoformat(),
                "log":log}


    @staticmethod
    def transfer_terima(jumlah,pengirim): # untuk penerima
        return RiwayatTemplate.template("transaksi","terima saldo",f"TERIMA SALDO | dari {pengirim.pemilik.nama} | Jumlah Rp{jumlah:,}".replace(",", "."))

    @staticmethod
    def transfer_kirim(jumlah,penerima): # untuk pengirim
        return RiwayatTemplate.template("transaksi","transfer saldo",f"TRANSFER SALDO | Penerima {penerima.pemilik.nama} | Jumlah Rp{jumlah:,}".replace(",", "."))

    @staticmethod
    def tarik_uang(jumlah):
        return RiwayatTemplate.template("kategori","tarik uang",f'TARIK UANG | Jumlah Rp{jumlah:,}'.replace(",","."))

    @staticmethod
    def upgrade_rekening(sebelum,sesudah):
        return RiwayatTemplate.template("sistem","perubahan",f"Upgrade Rekening {sebelum} ke {sesudah}")

    @staticmethod
    def alasan_blokir(alasan:str):
        return RiwayatTemplate.template("sistem","blokir",alasan)

    @staticmethod
    def downgrade_rekening(sebelum,sesudah):
        return RiwayatTemplate.template("sistem","perubahan",f"Turun Rekening {sebelum} ke {sesudah}")

    @staticmethod
    def setor_uang(jumlah):
        return RiwayatTemplate.template("transaksi","setor uang",f"SETOR TUNAI | Jumlah Rp{jumlah:,}".replace(",", "."))