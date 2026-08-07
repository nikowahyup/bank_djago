from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.ui import UI
from bank_djago.utils.utililty import Utilitas


class AdminTeller:

    @staticmethod
    def menu(bank):
        pass

    @staticmethod
    def setor_tunai(bank):
        UI.header("SETOR TUNAI")
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")
        try:
            rekening = bank.autentikasi_rekening(norek,pin)
            nominal  = int(input("Masukkan nominal setor: "))
            TransaksiService.setor_tunai(rekening,nominal)
            UI.sukses(f"Rp{Utilitas.format_rupiah(nominal)} telah masuk ke rekening Anda")
            log = RiwayatTemplate.setor_uang(nominal)
            rekening.simpan_riwayat(log)
            AuditService.tambah_audit(bank,kategori="transaksi",jenis="setor uang",log=f"{rekening.pemilik.nama} Setor Uang Rp{Utilitas.format_rupiah(nominal)}",nik=rekening.pemilik.NIK,norek=rekening.norek)

        except ValueError as e:
            UI.gagal(str(e))
            return


    @staticmethod
    def tarik_tunai(bank):
        UI.header("TARIK TUNAI")
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")
        try:
            rekening = bank.autentikasi_rekening(norek,pin)
            nominal  = int(input("Masukkan nominal tarik: "))
            TransaksiService.tarik_tunai(rekening,nominal)
            UI.sukses(f"Rp{Utilitas.format_rupiah(nominal)} telah dipotong dari rekening Anda")
            log = RiwayatTemplate.tarik_uang(nominal)
            rekening.simpan_riwayat(log)
            AuditService.tambah_audit(bank,kategori="transaksi",jenis="tarik uang",log=f"{rekening.pemilik.nama} Tarik Uang Rp{Utilitas.format_rupiah(nominal)}",nik=rekening.pemilik.NIK,norek=rekening.norek)


        except ValueError as e:
            UI.gagal(str(e))
            return

    @staticmethod
    def transfer(bank):
        UI.header("TRANSFER SALDO")
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")
        try:

            pengirim     = bank.autentikasi_rekening(norek,pin)
            rek_penerima = input("Masukkan nomor rekening penerima: ")
            penerima     = bank.cari_penerima(pengirim,rek_penerima)
            nominal      = int(input("Masukkan nominal transfer: "))
            TransaksiService.transfer(pengirim,penerima,nominal)
            UI.sukses(f"Rp{Utilitas.format_rupiah(nominal)} telah masuk ke rekening {penerima.pemilik.nama}")
            log_kirim = RiwayatTemplate.transfer_kirim(nominal,penerima)
            log_terima = RiwayatTemplate.transfer_terima(nominal,pengirim)
            pengirim.simpan_riwayat(log_kirim)
            penerima.simpan_riwayat(log_terima)
            AuditService.tambah_audit(bank,kategori="transaksi",jenis="transfer saldo",log=f"{pengirim.pemilik.nama} Transfer Uang ke {penerima.pemilik.nama} Rp{Utilitas.format_rupiah(nominal)}",nik=pengirim.pemilik.NIK,norek=pengirim.norek)
            AuditService.tambah_audit(bank,kategori="transaksi",jenis="terima saldo",log=f"{penerima.pemilik.nama} Terima Uang dari {pengirim.pemilik.nama} Rp{Utilitas.format_rupiah(nominal)}",nik=penerima.pemilik.NIK,norek=penerima.norek)

        except ValueError as e:
            UI.gagal(str(e))

    @staticmethod
    def lihat_riwayat(bank):
        UI.header("LIHAT RIWAYAT")
        from bank_djago.services.transaksi.riwayat.ui import RiwayatUI
        norek = input("Masukkan nomor rekening Anda: ")
        pin   = input("Masukkan PIN Anda: ")

        try:
            rekening = bank.autentikasi_rekening(norek,pin)
            RiwayatUI.menu_riwayat(rekening)
        except ValueError as e:
            UI.gagal(str(e))


