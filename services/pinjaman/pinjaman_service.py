#DIAJUKAN  = nasabah sudah meminta pinjaman
# DITOLAK   = pengajuan gagal
# DISETUJUI = bank menyetujui, tetapi dana belum dicairkan
# AKTIF     = dana sudah dicairkan dan masih ada kewajiban
# LUNAS     = seluruh pokok dan bunga sudah terselesaikan

from enum import Enum

from bank_djago.core.pinjaman import Pinjaman
from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.utils.utililty import Utilitas
from bank_djago.utils.validator import Validator


class StatusPinjaman(Enum):
    DIAJUKAN = "diajukan"
    DITOLAK = "ditolak"
    DISETUJUI = "disetujui"
    AKTIF = "aktif"
    LUNAS = "lunas"


class PinjamanService:
    TENOR = {
        6: 0.10,
        12: 0.12,
        18: 0.13,
        24: 0.14,
    }

    MIN_PINJAMAN = 1_000_000
    MAX_PINJAMAN = 50_000_000


    @staticmethod
    def ajukan_pinjaman(bank,nasabah,rekening,nominal,tenor):
        Validator.amankan_rekening(rekening)

        if nominal < PinjamanService.MIN_PINJAMAN:
            raise ValueError("Nominal pinjaman di bawah minimal pinjaman")

        if nominal > PinjamanService.MAX_PINJAMAN:
            raise ValueError("Nominal pinjaman melebihi batas maksimal")

        if tenor not in PinjamanService.TENOR:
            raise ValueError("Pilihan waktu pinjaman tidak tersedia")

        if nasabah.pinjaman is not None:
            raise  ValueError("Nasabah masih punya pinjaman aktif")

        nasabah.jumlah_pinjaman += 1
        id_pinjaman = nasabah.jumlah_pinjaman
        bunga = PinjamanService.TENOR[tenor]
        pinjaman = Pinjaman(ID=id_pinjaman,pemilik=nasabah,rekening=rekening,nominal_pinjaman=nominal,bunga=bunga,tenor=tenor)
        pinjaman.status = StatusPinjaman.DIAJUKAN
        nasabah.pinjaman = pinjaman

        AuditService.tambah_audit(bank,kategori="transaksi",jenis="pinjaman",log=f"{nasabah.nama} mengajukan pinjaman",nik=nasabah.NIK,norek=rekening.norek)

        return pinjaman

    @staticmethod
    def setujui_pinjaman(bank,pinjaman):
        if pinjaman.status != StatusPinjaman.DIAJUKAN:
            raise ValueError("Pinjaman tidak dalam status pengajuan")

        pinjaman.status = StatusPinjaman.DISETUJUI

        AuditService.tambah_audit(bank,kategori="transaksi",jenis="pinjaman",log=f"Pinjaman {pinjaman.pemilik.nama} telah disetujui",nik=pinjaman.pemilik.NIK,norek=pinjaman.rekening.norek)

        return pinjaman


    @staticmethod
    def cairkan_pinjaman(bank,pinjaman):
        if pinjaman.status != StatusPinjaman.DISETUJUI:
            raise ValueError("Pinjaman masih belum disetujui")

        pinjaman.rekening.tambah_saldo(pinjaman.nominal_pinjaman)
        pinjaman.sisa_pokok = pinjaman.nominal_pinjaman
        persentase_bunga = pinjaman.bunga/12
        pinjaman.cicilan_tetap = (pinjaman.nominal_pinjaman * persentase_bunga * ((1 + persentase_bunga) ** pinjaman.tenor)) / ((1 + persentase_bunga) ** pinjaman.tenor - 1)

        pinjaman.status = StatusPinjaman.AKTIF

        AuditService.tambah_audit(bank,kategori='transaksi',jenis='pinjaman',log=f'{pinjaman.pemilik.nama} menerima pencairan pinjaman Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}',nik=pinjaman.pemilik.NIK,norek=pinjaman.rekening.norek)
        log = RiwayatTemplate.template(kategori="transaksi",jenis="pinjaman",log=f'PENCAIRAN PINJAMAN |  Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}')

        pinjaman.rekening.simpan_riwayat(log)

        return pinjaman


    @staticmethod
    def bayar_cicilan(bank,pinjaman):
        if pinjaman.status != StatusPinjaman.AKTIF:
            raise ValueError("Pinjaman sedang tidak aktif")


        persentase_bunga = pinjaman.bunga/12
        bunga_bulanan = pinjaman.sisa_pokok * persentase_bunga
        pinjaman.bunga_bulanan = bunga_bulanan
        total_bayar = pinjaman.cicilan_tetap
        pinjaman.rekening.kurangi_saldo(total_bayar)
        pokok_saja = total_bayar-bunga_bulanan
        pinjaman.sisa_pokok -= pokok_saja
        pinjaman.cicilan_terbayar += 1

        if pinjaman.sisa_pokok <= 0:
            pinjaman.sisa_pokok = 0
            pinjaman.status = StatusPinjaman.LUNAS

        AuditService.tambah_audit(
            bank,
            kategori="transaksi",
            jenis="pinjaman",
            log=(
                f"{pinjaman.pemilik.nama} membayar cicilan "
                f"pinjaman {pinjaman.ID} "
                f"Rp{Utilitas.format_rupiah(total_bayar)}"
            ),
            nik=pinjaman.pemilik.NIK,
            norek=pinjaman.rekening.norek
        )

        print("\n=== DEBUG CICILAN ===")
        print("ID                 :", pinjaman.ID)
        print("Cicilan ke         :", pinjaman.cicilan_terbayar + 1)
        print("Sisa pokok awal    :", pinjaman.sisa_pokok)
        print("Bunga periode      :", bunga_bulanan)
        print("Cicilan tetap      :", total_bayar)
        print("Pokok dibayar      :", pokok_saja)
        print("Sisa pokok akhir   :", pinjaman.sisa_pokok - pokok_saja)
        print("Saldo rekening     :", pinjaman.rekening.saldo)
        print("====================")
        log = RiwayatTemplate.template(
            kategori="transaksi",
            jenis="pinjaman",
            log=(
                f"PEMBAYARAN CICILAN PINJAMAN | "
                f"Rp{Utilitas.format_rupiah(total_bayar)}"
            )
        )

        pinjaman.rekening.simpan_riwayat(log)

        return pinjaman


    @staticmethod
    def daftar_ajuan(bank):
        return [ajuan for ajuan in bank.daftar_pinjaman if ajuan.status == StatusPinjaman.DIAJUKAN]


    @staticmethod
    def ajuan_ditolak(bank,pinjaman):
        if pinjaman.status != StatusPinjaman.DIAJUKAN:
            raise ValueError("Pinjaman tidak dalam status pengajuan")


        pinjaman.status = StatusPinjaman.DITOLAK
        AuditService.tambah_audit(bank, kategori="transaksi", jenis="pinjaman",
                                  log=f"Pinjaman {pinjaman.pemilik.nama} ditolak", nik=pinjaman.pemilik.NIK,
                                  norek=pinjaman.rekening.norek)


        return pinjaman


