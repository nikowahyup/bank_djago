from bank_djago.core.notifikasi import Notifikasi
from bank_djago.services.rekening.biaya_admin_service import  BiayaAdminService
from bank_djago.services.deposito.deposito_service import StatusDeposito,DepositoService,JenisAro
from bank_djago.services.rekening.bunga_service import BungaService
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.transaksi.limit_service import LimitService
import datetime

from bank_djago.utils.utility import StatusPinjaman, Utilitas, JenisReferensiID


class Scheduler:

    @staticmethod
    def jalankan(bank,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        for rekening in bank.rekening_index.values():

            if rekening.status == "tutup":
                continue

            BungaService.berikan_bunga(bank, rekening, hari_ini)

            LimitService.hitung_limit_saat_ini(rekening, hari_ini)

            BiayaAdminService.potong_admin(bank, rekening, hari_ini)






        for nasabah in bank.data_nasabah.values():
            for deposito in nasabah.deposito:

                nasabah = deposito.pemilik
                jatuh_tempo = deposito.jatuh_tempo
                if deposito.status != StatusDeposito.AKTIF:
                    continue






                if deposito.jenis_aro == JenisAro.TIDAK:
                    if hari_ini.day < jatuh_tempo.day and hari_ini.month == jatuh_tempo.month and hari_ini.year == jatuh_tempo.year:
                        if not deposito.notifikasi_depo:
                            DepositoService.hapus_notifikasi_deposito(nasabah, deposito)


                            notifikasi = Notifikasi(
                                                    jenis="deposito",
                                                    pesan=f"Deposito Anda akan jatuh tempo pada {Utilitas.format_tanggal_indonesia(jatuh_tempo)}",
                                                    referensi_id=JenisReferensiID.DEPOSITO)
                            notifikasi.id_objek = deposito.ID
                            nasabah.notifikasi.append(notifikasi)
                            deposito.notifikasi_depo = True

                    elif hari_ini == jatuh_tempo or hari_ini > jatuh_tempo:
                        DepositoService.hapus_notifikasi_deposito(nasabah,deposito)

                        notifikasi = Notifikasi(
                                                jenis="deposito",
                                                pesan=f"Deposito Anda telah jatuh tempo. Silahkan lakukan pencairan",
                                                referensi_id=JenisReferensiID.DEPOSITO)

                        notifikasi.id_objek = deposito.ID
                        nasabah.notifikasi.append(notifikasi)
                        deposito.notifikasi_depo = True
                        deposito.status = StatusDeposito.JATUH_TEMPO


                else:
                    if (
                            deposito.proses_aro is not None
                            and deposito.proses_aro < hari_ini < jatuh_tempo
                    ):
                        nasabah = deposito.pemilik
                        DepositoService.hapus_notifikasi_deposito(
                            nasabah,
                            deposito
                        )

                    elif hari_ini >= jatuh_tempo:
                        nasabah = deposito.pemilik

                        DepositoService.hapus_notifikasi_deposito(
                            nasabah,
                            deposito
                        )

                        DepositoService.perpanjangan(bank, deposito, hari_ini)
                        deposito.proses_aro = hari_ini

        for pinjaman in bank.daftar_pinjaman:

            if pinjaman.status != StatusPinjaman.AKTIF:
                continue



            jatuh_tempo = pinjaman.tanggal_jatuh_tempo
            #sehari sebelum jatuh tempo
            hari_terlambat = PinjamanService.hitung_hari_terlambat(pinjaman, hari_ini)
            denda = PinjamanService.hitung_denda(pinjaman, hari_ini)
            nasabah = pinjaman.pemilik

            #belum masuk bulan jatuh tempo
            if (hari_ini.year < jatuh_tempo.year or
                    (hari_ini.year == jatuh_tempo.year and hari_ini.month < jatuh_tempo.month)):
                continue

            if hari_ini.month == jatuh_tempo.month and hari_ini.year == jatuh_tempo.year and hari_ini.day < jatuh_tempo.day:
                if not pinjaman.notifikasi_jatuh_tempo:
                    PinjamanService.hapus_notif_pinjaman(nasabah)
                    notifikasi = Notifikasi(
                                            jenis="pinjaman",
                                            pesan=f"Batas pembayaran cicilan Anda periode ini akan berakhir pada {Utilitas.format_tanggal_indonesia(jatuh_tempo)}",
                                            referensi_id=JenisReferensiID.PINJAMAN)

                    nasabah.notifikasi.append(notifikasi)
                    pinjaman.notifikasi_jatuh_tempo = True
            # sudah waktunya jatuh tempo

            elif hari_terlambat == 0:

                    PinjamanService.hapus_notif_pinjaman(nasabah)

                    notifikasi = Notifikasi(
                                            jenis="pinjaman",
                                            pesan=f"Hari ini waktu icilan bulan {Utilitas.nama_bulan(jatuh_tempo)} terakhir.\n"
                                                  f"Cicilan sebesar Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}",
                                            referensi_id=JenisReferensiID.PINJAMAN)
                    nasabah.notifikasi.append(notifikasi)
                    pinjaman.notifikasi_jatuh_tempo = True

            elif hari_terlambat <= PinjamanService.BATAS_HARI_TUNGGAKAN:
                PinjamanService.hapus_notif_pinjaman(nasabah)
                sisa_toleransi = PinjamanService.BATAS_HARI_TUNGGAKAN - hari_terlambat

                if sisa_toleransi == 0 :
                    pesan = (
                        "Hari ini adalah hari terakhir masa toleransi"
                        "pembayaran cicilan Anda\n"
                        ". Denda mulai dihitung"
                        "besok jika cicilan belum dibayar.")
                else:
                    pesan = (f"Cicilan Anda terlambat {hari_terlambat} hari.\n"
                        f"Masa toleransi tersisa {sisa_toleransi} hari.")

                notifikasi = Notifikasi(jenis="pinjaman",pesan=pesan,referensi_id=JenisReferensiID.PINJAMAN)
                nasabah.notifikasi.append(notifikasi)
                pinjaman.notifikasi_jatuh_tempo = True

            else:
                hari_denda = hari_terlambat - PinjamanService.BATAS_HARI_TUNGGAKAN
                total_tagihan = pinjaman.cicilan_tetap + denda
                PinjamanService.hapus_notif_pinjaman(nasabah)
                notifikasi = Notifikasi(
                    jenis="pinjaman",
                    pesan=(
                        f"Cicilan Anda terlambat {hari_terlambat} hari.\n"
                        f"Denda telah berjalan selama {hari_denda} hari\n"
                        f"dengan nominal "
                        f"Rp{Utilitas.format_rupiah(denda)}.\n"
                        f"Total pembayaran saat ini "
                        f"Rp{Utilitas.format_rupiah(round(total_tagihan))}."
                    ),
                    referensi_id=JenisReferensiID.PINJAMAN,
                    id_objek=pinjaman.ID
                )
                nasabah.notifikasi.append(notifikasi)
                pinjaman.notifikasi_jatuh_tempo = True








