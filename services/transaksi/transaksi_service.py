
from bank_djago.utils.utility import Utilitas
from bank_djago.services.transaksi.limit_service import LimitService
from bank_djago.services.admin.audit_service import  AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.validator import Validator

class TransaksiService:

    @staticmethod
    def setor_tunai(bank,rekening,nominal):
        Validator.amankan_rekening(rekening)
        if nominal < 10000:
            raise ValueError("Minimal setor adalah Rp10.0000")
        rekening.tambah_saldo(nominal)
        log = RiwayatTemplate.setor_uang(nominal)
        rekening.simpan_riwayat(log)
        AuditService.tambah_audit(bank,kategori="transaksi", jenis="setor uang",log=f"{rekening.pemilik.nama} Setor Uang Rp{Utilitas.format_rupiah(nominal)}",nik=rekening.pemilik.NIK, norek=rekening.norek)

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def tarik_tunai(bank,rekening,nominal):
        Validator.amankan_rekening(rekening)
        if nominal < 10000:
            raise ValueError("Minimal tarik adalah Rp10.000")
        if rekening.saldo - nominal < rekening.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika Anda menarik sebesar Rp{Utilitas.format_rupiah(nominal)}")
        rekening.kurangi_saldo(nominal)
        log = RiwayatTemplate.tarik_uang(nominal)
        rekening.simpan_riwayat(log)
        AuditService.tambah_audit(bank,kategori="transaksi", jenis="tarik uang",log=f"{rekening.pemilik.nama} Tarik Uang Rp{Utilitas.format_rupiah(nominal)}",nik=rekening.pemilik.NIK, norek=rekening.norek)

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def transfer(bank,pengirim,penerima,nominal):
        Validator.amankan_rekening(pengirim)
        if nominal < 10000:
            raise ValueError("Minimal transfer adalah Rp10.0000")
        LimitService.reset_limit(bank,pengirim)
        total = nominal + pengirim.pajak
        if pengirim.limit_harian is not None:
            if pengirim.limit_sisa < nominal:
                raise ValueError("Limit harian telah tercapai")

        if pengirim.saldo - total < pengirim.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika transfer Rp{Utilitas.format_rupiah(nominal)}")

        pengirim.kurangi_saldo(total)
        penerima.tambah_saldo(nominal)

        log_kirim  = RiwayatTemplate.transfer_kirim(nominal, penerima)
        log_terima = RiwayatTemplate.transfer_terima(nominal, pengirim)
        pengirim.simpan_riwayat(log_kirim)
        penerima.simpan_riwayat(log_terima)

        AuditService.tambah_audit(bank,kategori="transaksi", jenis="transfer saldo",log=f"{pengirim.pemilik.nama} Transfer Uang ke {penerima.pemilik.nama} Rp{Utilitas.format_rupiah(nominal)}",nik=pengirim.pemilik.NIK, norek=pengirim.norek)
        AuditService.tambah_audit(bank, kategori="transaksi", jenis="terima saldo",log=f"{penerima.pemilik.nama} Terima Uang dari {pengirim.pemilik.nama} Rp{Utilitas.format_rupiah(nominal)}",nik=penerima.pemilik.NIK, norek=penerima.norek)

        if pengirim.limit_harian is not None:
            pengirim.limit_sisa -= nominal

    @staticmethod
    def tarik_semua_uang(rekening):
        Validator.amankan_rekening(rekening)
        total = rekening.saldo
        rekening.kurangi_saldo(total)


    @staticmethod
    def transfer_semua_uang(rekening,penerima):
        Validator.amankan_rekening(rekening)
        total = rekening.saldo
        rekening.kurangi_saldo(total)
        penerima.tambah_saldo(total)


    @staticmethod
    def cari_penerima(bank,norek_penerima,pengirim):

        penerima = bank.cari_rekening(norek_penerima)

        if not penerima:
            raise ValueError("Penerima tidak terdaftar")

        if penerima == pengirim:
            raise ValueError("Tidak dapat transfer ke nomor rekening sendiri")

        if penerima.status != "aktif":
            raise ValueError(f"Rekening penerima sudah/telah di{penerima.status}")

        return penerima