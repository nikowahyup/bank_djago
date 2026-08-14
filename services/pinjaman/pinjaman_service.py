#DIAJUKAN  = nasabah sudah meminta pinjaman
# DITOLAK   = pengajuan gagal
# DISETUJUI = bank menyetujui, tetapi dana belum dicairkan
# AKTIF     = dana sudah dicairkan dan masih ada kewajiban
# LUNAS     = seluruh pokok dan bunga sudah terselesaikan
import datetime


from bank_djago.core.notifikasi import Notifikasi
from bank_djago.core.pinjaman import Pinjaman
from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.utils.utililty import Utilitas, StatusPinjaman, JenisReferensiID
from bank_djago.utils.validator import Validator





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
            raise  ValueError("Anda masih punya pinjaman aktif")

        nasabah.jumlah_pinjaman += 1
        id_pinjaman = nasabah.jumlah_pinjaman
        bunga = PinjamanService.TENOR[tenor]
        pinjaman = Pinjaman(ID=id_pinjaman,pemilik=nasabah,rekening=rekening,nominal_pinjaman=nominal,bunga=bunga,tenor=tenor)
        pinjaman.status = StatusPinjaman.DIAJUKAN
        nasabah.pinjaman = pinjaman
        AuditService.tambah_audit(bank,kategori="transaksi",jenis="pinjaman",log=f"{nasabah.nama} mengajukan pinjaman",nik=nasabah.NIK,norek=rekening.norek)
        bank.daftar_pinjaman.append(pinjaman)


        return pinjaman

    @staticmethod
    def setujui_pinjaman(bank,pinjaman):
        if pinjaman.status != StatusPinjaman.DIAJUKAN:
            raise ValueError("Pinjaman tidak dalam status pengajuan")

        pinjaman.status = StatusPinjaman.DISETUJUI

        nasabah = pinjaman.pemilik
        PinjamanService.hapus_notif_pinjaman(nasabah)

        notifikasi = Notifikasi(
                                jenis='pinjaman', pesan='Pengajuan berhasil! Kini Anda dapat mencairkan uang pinjaman',
                                referensi_id=JenisReferensiID.PINJAMAN)
        nasabah.notifikasi.append(notifikasi)
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
        bunga_bulanan = pinjaman.sisa_pokok * persentase_bunga
        pinjaman.bunga_bulanan = bunga_bulanan
        pinjaman.tanggal_pencairan = datetime.date.today()
        pinjaman.tanggal_jatuh_tempo = Utilitas.tambah_bulan(pinjaman.tanggal_pencairan,1)




        AuditService.tambah_audit(bank,kategori='transaksi',jenis='pinjaman',log=f'{pinjaman.pemilik.nama} menerima pencairan pinjaman Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}',nik=pinjaman.pemilik.NIK,norek=pinjaman.rekening.norek)
        log = RiwayatTemplate.template(kategori="transaksi",jenis="pinjaman",log=f'PENCAIRAN PINJAMAN |  Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}')

        pinjaman.rekening.simpan_riwayat(log)

        return pinjaman

    @staticmethod
    def bayar_cicilan(bank, pinjaman):
        if pinjaman.status != StatusPinjaman.AKTIF:
            raise ValueError("Pinjaman sedang tidak aktif")

        persentase_bunga = pinjaman.bunga / 12

        bunga_bulanan = pinjaman.sisa_pokok * persentase_bunga
        total_bayar = pinjaman.cicilan_tetap
        pokok_saja = total_bayar - bunga_bulanan

        pinjaman.rekening.kurangi_saldo(total_bayar)

        pinjaman.sisa_pokok -= pokok_saja
        pinjaman.cicilan_terbayar += 1
        pinjaman.bunga_bulanan = bunga_bulanan

        if pinjaman.sisa_pokok <= 0:
            pinjaman.sisa_pokok = 0
            pinjaman.status = StatusPinjaman.LUNAS

            log_audit = (
                f"{pinjaman.pemilik.nama} telah melunasi "
                f"pinjaman {pinjaman.ID} "
                f"sebesar Rp{Utilitas.format_rupiah(total_bayar)}"
            )

            log_riwayat = "PINJAMAN ANDA TELAH LUNAS"
            nasabah = pinjaman.pemilik
            PinjamanService.hapus_notif_pinjaman(nasabah)

            notifikasi = Notifikasi(
                                    jenis='pinjaman',
                                    pesan='🎉 Pinjaman Anda telah lunas. Terima kasih telah mempercayai bank Djago',
                                    referensi_id=JenisReferensiID.PINJAMAN)
            nasabah.notifikasi.append(notifikasi)

        else:
            pinjaman.tanggal_jatuh_tempo = Utilitas.tambah_bulan(
                pinjaman.tanggal_jatuh_tempo,
                1
            )

            pinjaman.notifikasi_jatuh_tempo = False

            log_audit = (
                f"{pinjaman.pemilik.nama} membayar cicilan "
                f"pinjaman {pinjaman.ID} "
                f"sebesar Rp{Utilitas.format_rupiah(total_bayar)}"
            )

            log_riwayat = (
                f"PEMBAYARAN CICILAN PINJAMAN | "
                f"Rp{Utilitas.format_rupiah(total_bayar)}"
            )

        AuditService.tambah_audit(
            bank,
            kategori="transaksi",
            jenis="pinjaman",
            log=log_audit,
            nik=pinjaman.pemilik.NIK,
            norek=pinjaman.rekening.norek
        )

        pinjaman.rekening.simpan_riwayat(
            RiwayatTemplate.template(
                kategori="transaksi",
                jenis="pinjaman",
                log=log_riwayat
            )
        )
        PinjamanService.hapus_notif_pinjaman(pinjaman.pemilik)
        return pinjaman




    @staticmethod
    def ajuan_ditolak(bank,pinjaman):
        if pinjaman.status != StatusPinjaman.DIAJUKAN:
            raise ValueError("Pinjaman tidak dalam status pengajuan")

        nasabah = pinjaman.pemilik
        PinjamanService.hapus_notif_pinjaman(nasabah)

        notifikasi = Notifikasi(
                                jenis='pinjaman',pesan='Maaf,pengajuan pinjaman Anda ditolak',
                                referensi_id=JenisReferensiID.PINJAMAN)

        nasabah.notifikasi.append(notifikasi)


        pinjaman.status = StatusPinjaman.DITOLAK
        AuditService.tambah_audit(bank, kategori="transaksi", jenis="pinjaman",
                                  log=f"Pinjaman {pinjaman.pemilik.nama} ditolak", nik=pinjaman.pemilik.NIK,
                                  norek=pinjaman.rekening.norek)


        return pinjaman


    @staticmethod
    def hapus_notif_pinjaman(nasabah):
        for item in nasabah.notifikasi:
            if item.referensi_id == JenisReferensiID.PINJAMAN:
                nasabah.notifikasi.remove(item)
                break


    @staticmethod
    def daftar_ajuan(bank):
        return [ajuan for ajuan in bank.daftar_pinjaman if ajuan.status == StatusPinjaman.DIAJUKAN]
