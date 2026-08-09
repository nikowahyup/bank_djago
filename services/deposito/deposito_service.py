import datetime
from bank_djago.core.deposito import Deposito
from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.utils.utililty import Utilitas,JenisAro

class StatusDeposito:
    AKTIF = "aktif"
    JATUH_TEMPO = "jatuh tempo"
    DICAIRKAN = "dicairkan"
    SELESAI = "selesai"



class DepositoService:
    JANGKA_WAKTU = {
        1: 0.03,
        3: 0.035,
        6: 0.04,
        12: 0.045
    }
    MIN_DEPO = 1000_000

    @staticmethod
    def buka_deposito(bank,rekening,nominal,lama_bulan,jenis_aro=JenisAro.TIDAK,lama_aro=None):

        if nominal < DepositoService.MIN_DEPO:
            raise ValueError("Jumlah Depo kurang dari minimum")

        if rekening.saldo - nominal < rekening.saldosetor_min:
            raise ValueError(
                "Saldo tidak mencukupi untuk membuka deposito")

        if lama_bulan not in DepositoService.JANGKA_WAKTU:
            raise ValueError("Jangka waktu deposito tidak tersedia")

        bunga = DepositoService.JANGKA_WAKTU[lama_bulan]
        tanggal_buka = datetime.date.today()
        jatuh_tempo = Utilitas.tambah_bulan(tanggal_buka,lama_bulan)

        nasabah = rekening.pemilik
        nasabah.jumlah_deposito += 1

        deposito_baru = Deposito(pemilik=nasabah,rekening=rekening,nominal=nominal,bunga=bunga,id=nasabah.jumlah_deposito,lama_bulan=lama_bulan,tanggal_buka=tanggal_buka,tanggal_jatuh_tempo=jatuh_tempo)
        deposito_baru.status = StatusDeposito.AKTIF
        deposito_baru.jenis_aro = jenis_aro
        deposito_baru.lama_aro = lama_aro
        rekening.kurangi_saldo(nominal)

        nasabah.deposito.append(deposito_baru)
        log = RiwayatTemplate.template(kategori="transaksi",jenis="deposito",log=f"DEPOSITO | Rp{Utilitas.format_rupiah(nominal)} |Bunga {bunga:.1%} | Lama {lama_bulan} bulan| ")
        rekening.simpan_riwayat(log)
        AuditService.tambah_audit(bank,kategori="transaksi",jenis="deposito",log=f"{rekening.pemilik.nama} membuka deposito Rp{Utilitas.format_rupiah(nominal)}",nik=rekening.pemilik.NIK,norek=rekening.norek)

        return deposito_baru

    @staticmethod
    def cairkan_deposito(bank,deposito):
        if deposito.status != StatusDeposito.AKTIF:
            raise ValueError("Deposito sudah dicairkan")

        if datetime.date.today() < deposito.jatuh_tempo:
            raise ValueError("Deposito belum jatuh tempo")

        total = deposito.total_pencairan
        deposito.rekening.tambah_saldo(total)
        deposito.status = StatusDeposito.DICAIRKAN

        log = RiwayatTemplate.template(kategori="transaksi",jenis="deposito",log=f"PENCAIRAN DEPOSITO | Rp{Utilitas.format_rupiah(total)}")

        deposito.rekening.simpan_riwayat(log)

        AuditService.tambah_audit(
            bank,
            kategori="transaksi",
            jenis="deposito",
            log=f"{deposito.pemilik.nama} mencairkan deposito Rp{Utilitas.format_rupiah(total)}"
        )

        return total




    # @staticmethod
    # def perpanjangan(bank,deposito):
    #     if deposito.status == StatusDeposito.AKTIF:
    #         raise ValueError ("Deposito belum jatuh tempo")
    #
    #     if deposito.jenis_aro == JenisAro.TIDAK:
    #         return None
    #
    #     if deposito.jenis_aro == JenisAro.POKOK:
    #         nominal_baru = deposito.nominal
    #
    #     elif deposito.jenis_aro == JenisAro.POKOK_BUNGA:
    #         nominal_baru = deposito.total_pencairan
    #
    #     nasabah = deposito.pemilik
    #     lama_bulan = deposito.lama_aro
    #     deposito_baru = DepositoService.buka_deposito(bank,deposito.rekening,nominal_baru,lama_bulan)
    #     nasabah.deposito.append(deposito_baru)

