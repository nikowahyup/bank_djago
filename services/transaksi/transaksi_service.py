from bank_djago.utils.utililty import Utilitas
from bank_djago.services.transaksi.limit import LimitService
from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate

class TransaksiService:

    @staticmethod
    def setor_tunai(bank,rekening,nominal):
        if nominal < 10000:
            raise ValueError("Minimal setor adalah Rp10.0000")
        rekening.tambah_saldo(nominal)
        log = RiwayatTemplate.setor_uang(nominal)
        rekening.simpan_riwayat(log)
        AuditService.tambah_audit(bank,kategori="transaksi", jenis="setor uang",log=f"{rekening.pemilik.nama} Setor Uang Rp{Utilitas.format_rupiah(nominal)}",nik=rekening.pemilik.NIK, norek=rekening.norek)

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def tarik_tunai(bank,rekening,nominal):
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

        log_kirim  = RiwayatTemplate.transfer_kirim(nominal, penerima)
        log_terima = RiwayatTemplate.transfer_terima(nominal, pengirim)
        pengirim.simpan_riwayat(log_kirim)
        penerima.simpan_riwayat(log_terima)

        AuditService.tambah_audit(bank,kategori="transaksi", jenis="transfer saldo",log=f"{pengirim.pemilik.nama} Transfer Uang ke {penerima.pemilik.nama} Rp{Utilitas.format_rupiah(nominal)}",nik=pengirim.pemilik.NIK, norek=pengirim.norek)
        AuditService.tambah_audit(bank, kategori="transaksi", jenis="terima saldo",log=f"{penerima.pemilik.nama} Terima Uang dari {pengirim.pemilik.nama} Rp{Utilitas.format_rupiah(nominal)}",nik=penerima.pemilik.NIK, norek=penerima.norek)

        if pengirim.limit_harian is not None:
            pengirim.limit_sisa -= nominal

