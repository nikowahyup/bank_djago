from bank_djago.core.notifikasi import Notifikasi
from bank_djago.services.admin.AdminTeller.admin_payroll import BiayaAdminService
from bank_djago.services.deposito.deposito_service import StatusDeposito,DepositoService,JenisAro
from bank_djago.services.bunga import BungaService
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.transaksi.limit import LimitService
import datetime

from bank_djago.utils.utililty import StatusPinjaman, Utilitas, JenisReferensiID


class Scheduler:

    @staticmethod
    def jalankan(bank):
        for rekening in bank.rekening_index.values():
            BungaService.berikan_bunga(rekening)

            LimitService.reset_limit(bank,rekening)

            BiayaAdminService.potong_admin(bank, rekening)




        hari_ini = datetime.date.today()

        for nasabah in bank.data_nasabah.values():
            for deposito in nasabah.deposito:

                nasabah = deposito.pemilik
                jatuh_tempo = deposito.jatuh_tempo
                if deposito.status != StatusDeposito.AKTIF:
                    continue

                if deposito.jatuh_tempo > hari_ini:
                    continue




                if deposito.jenis_aro == JenisAro.TIDAK:
                    if hari_ini == jatuh_tempo:
                        for item in nasabah.notifikasi:
                            if item.referensi_id == JenisReferensiID.DEPOSITO:
                                nasabah.notifikasi.remove(item)
                                break

                        notifikasi = Notifikasi(id_notifikasi=nasabah.buat_id_notifikasi(),
                                                jenis="deposito",
                                                pesan=f"Deposito Anda telah jatuh tempo. Silahkan lakukan pencairan",
                                                referensi_id=JenisReferensiID.DEPOSITO)

                        nasabah.notifikasi.append(notifikasi)
                        deposito.notifikasi_depo = True
                        deposito.status = StatusDeposito.JATUH_TEMPO

                    if hari_ini.month == jatuh_tempo.month and hari_ini.year == jatuh_tempo.year:
                        if not deposito.notifikasi_depo:

                            notifikasi = Notifikasi(id_notifikasi=nasabah.buat_id_notifikasi(),
                                                    jenis="deposito",
                                                    pesan=f"Deposito Anda akan jatuh tempo pada {Utilitas.format_tanggal_indonesia(jatuh_tempo)}",
                                                    referensi_id=JenisReferensiID.DEPOSITO)
                            nasabah.notifikasi.append(notifikasi)
                            deposito.notifikasi_depo = True


                else:
                    DepositoService.perpanjangan(bank, deposito)

        for pinjaman in bank.daftar_pinjaman:

            if pinjaman.status != StatusPinjaman.AKTIF:
                continue

            jatuh_tempo = pinjaman.tanggal_jatuh_tempo
            nasabah = pinjaman.pemilik
            #belum masuk bulan jatuh tempo
            if (hari_ini.year < jatuh_tempo.year or
                    (hari_ini.year == jatuh_tempo.year and hari_ini.month < jatuh_tempo.month)):
                continue

            # sudah waktunya jatuh tempo

            if hari_ini == jatuh_tempo:


                    PinjamanService.hapus_notif_pinjaman(nasabah)

                    notifikasi = Notifikasi(id_notifikasi=nasabah.buat_id_notifikasi(),
                                            jenis="pinjaman",
                                            pesan=f"Cicilan bulan {Utilitas.nama_bulan(jatuh_tempo)} telah jatuh tempo. Cicilan sebesar Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}",
                                            referensi_id=JenisReferensiID.PINJAMAN)
                    nasabah.notifikasi.append(notifikasi)
                    pinjaman.notifikasi_jatuh_tempo = True




            if hari_ini.month == jatuh_tempo.month and hari_ini.year == jatuh_tempo.year:
                if not pinjaman.notifikasi_jatuh_tempo:
                    PinjamanService.hapus_notif_pinjaman(nasabah)
                    notifikasi = Notifikasi(id_notifikasi=nasabah.buat_id_notifikasi(),
                                            jenis="pinjaman",
                                            pesan=f"Cicilan bulan {Utilitas.nama_bulan(jatuh_tempo)} akan jatuh pada {Utilitas.format_tanggal_indonesia(jatuh_tempo)}",
                                            referensi_id=JenisReferensiID.PINJAMAN)

                    nasabah.notifikasi.append(notifikasi)
                    pinjaman.notifikasi_jatuh_tempo = True





