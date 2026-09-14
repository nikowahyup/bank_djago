import datetime


from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.core.pinjaman import Pinjaman
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_service import AuditService

from bank_djago.utils.utility import Utilitas, StatusPinjaman, JenisReferensi, JenisTransaksi
from bank_djago.utils.validator import Validator
from  bank_djago.penyimpanan.repositories.notifikasi_repository import  NotifikasiRepository
from bank_djago.services.notifikasi_service import NotifikasiService
from bank_djago.penyimpanan.loaders.pinjaman_loader import PinjamanLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate





class PinjamanService:
    TENOR = {
        6: 0.10,
        12: 0.12,
        18: 0.13,
        24: 0.14,
    }

    MIN_PINJAMAN = 1_000_000
    MAX_PINJAMAN = 50_000_000
    BATAS_HARI_TUNGGAKAN = 7
    PERSENTASE_DENDA_HARIAN = 0.001
    MAKSIMAL_PERSENTASE_DENDA = 0.1

    @staticmethod
    def ajukan_pinjaman(
            nik,
            norek,
            nominal,
            tenor
    ):

        if nominal < PinjamanService.MIN_PINJAMAN:
            raise ValueError(
                "Nominal pinjaman di bawah batas minimal"
            )

        if nominal > PinjamanService.MAX_PINJAMAN:
            raise ValueError(
                "Nominal pinjaman melebihi batas maksimal"
            )

        if tenor not in PinjamanService.TENOR:
            raise ValueError(
                "Pilihan tenor pinjaman tidak tersedia"
            )

        koneksi = buat_koneksi()

        try:

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            if rekening is None:
                raise ValueError(
                    "Nomor rekening tidak terdaftar"
                )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise ValueError(
                    "NIK nasabah tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening)

            pengajuan_aktif = (
                PinjamanRepository.cari_pengajuan_aktif_nasabah(
                    nik=nasabah.NIK,
                    koneksi=koneksi
                )
            )

            if pengajuan_aktif is not None:
                raise ValueError(
                    "Anda masih memiliki pengajuan pinjaman "
                    "yang sedang menunggu proses"
                )
            bunga = PinjamanService.TENOR[tenor]

            pinjaman = Pinjaman(
                pemilik=nasabah,
                rekening=rekening,
                nominal_pinjaman=nominal,
                bunga=bunga,
                tenor=tenor,
                id=None
            )
            id_pinjaman = PinjamanRepository.tambah_pinjaman(
                pinjaman=pinjaman,
                koneksi=koneksi
            )


            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="pinjaman",
                log=(
                    f"PENGAJUAN PINJAMAN | ID {id_pinjaman} | "
                    f"Rp{Utilitas.format_rupiah(nominal)} | "
                    f"Tenor {tenor} bulan"
                )
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="pinjaman",
                aksi="pengajuan_pinjaman",
                log=(
                    f"{nasabah.nama} mengajukan pinjaman "
                    f"dengan ID {id_pinjaman} sebesar "
                    f"Rp{Utilitas.format_rupiah(nominal)}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return id_pinjaman

    @staticmethod
    def setujui_pinjaman(id_pinjaman):

        if not isinstance(id_pinjaman, int):
            raise TypeError(
                "ID pinjaman harus berupa angka"
            )

        if id_pinjaman <= 0:
            raise ValueError(
                "ID pinjaman tidak valid"
            )
        koneksi = buat_koneksi()

        try:
            data_pinjaman = (
                PinjamanRepository.cari_pinjaman_dengan_id(
                    id_pinjaman=id_pinjaman,
                    koneksi=koneksi
                )
            )

            if data_pinjaman is None:
                raise ValueError(
                    f"Pinjaman ber-ID {id_pinjaman} tidak ditemukan"
                )

            if (
                    data_pinjaman["status"]
                    != StatusPinjaman.DIAJUKAN.value
            ):
                raise ValueError(
                    f"Pinjaman tidak dapat disetujui. "
                    f"Status saat ini: {data_pinjaman['status']}"
                )
            norek = data_pinjaman['norek']
            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

            if rekening is None:
                raise ValueError(
                    f"Rekening untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            nasabah = rekening.pemilik

            status_baru = StatusPinjaman.DISETUJUI.value

            jumlah_baris = (
                PinjamanRepository.perbarui_status_pinjaman(
                    id_pinjaman=id_pinjaman,
                    status_baru=status_baru,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise ValueError(
                    "Gagal memperbarui status pinjaman"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="pinjaman",
                aksi="persetujuan_pinjaman",
                log=(
                    f"Pinjaman dengan ID {id_pinjaman} "
                    f"milik {nasabah.nama} telah disetujui"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            NotifikasiService.buat_notifikasi_persetujuan_pinjaman(
                id_pinjaman=id_pinjaman,
                nik_pemilik=nasabah.NIK,
                koneksi=koneksi
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True




    @staticmethod
    def cairkan_pinjaman(
            nik,
            id_pinjaman,
            hari_ini=None
    ):

        if hari_ini is None:
            hari_ini = datetime.date.today()

        if not isinstance(id_pinjaman, int):
            raise TypeError("ID pinjaman harus berupa angka")

        if id_pinjaman <= 0:
            raise ValueError("ID pinjaman tidak valid")


        koneksi = buat_koneksi()

        try:
            data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
                id_pinjaman=id_pinjaman,
                koneksi=koneksi
            )

            if data_pinjaman is None:
                raise   ValueError(
                    "Pinjaman tidak ditemukan"
                )


            norek = data_pinjaman['norek']

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            if rekening is None:
                raise ValueError(
                    "Rekening tidak ditemukan"
                )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise ValueError(
                    "NIK ini tidak terdaftar sebagai pemilik pinjaman"
                )
            Validator.amankan_rekening(rekening)

            if data_pinjaman['status'] != StatusPinjaman.DISETUJUI.value:
                raise ValueError(
                    "Pinjaman belum disetujui"
                )


            pinjaman = PinjamanLoader.rangkai_pinjaman(
                data_pinjaman=data_pinjaman,
                nasabah=nasabah,
                rekening=rekening
            )





            bunga = pinjaman.bunga
            tenor = pinjaman.tenor
            nominal_pinjaman = pinjaman.nominal_pinjaman
            persentase_bunga = bunga / 12
            sisa_pokok = nominal_pinjaman

            saldo_sebelum = rekening.saldo
            saldo_baru = saldo_sebelum + nominal_pinjaman
            cicilan_tetap = round(
                (nominal_pinjaman * persentase_bunga *
                 ((1 + persentase_bunga) ** tenor)) /
                 ((1 + persentase_bunga) ** tenor - 1))

            status_baru = StatusPinjaman.AKTIF
            tanggal_pencairan = hari_ini
            tanggal_jatuh_tempo = Utilitas.tambah_bulan(tanggal_pencairan,1)

            jumlah_baris = PinjamanRepository.perbarui_setelah_pencairan(
                                                                         id_pinjaman=id_pinjaman,
                                                                         cicilan_tetap_baru=cicilan_tetap,
                                                                         tanggal_jatuh_tempo_baru=tanggal_jatuh_tempo,
                                                                         tanggal_pencairan_baru=tanggal_pencairan,
                                                                            sisa_pokok_baru=sisa_pokok,
                                                                         status_baru=status_baru,
                                                                         koneksi=koneksi
                                                                         )

            if jumlah_baris != 1:
                raise ValueError(
                    'Gagal memperbarui status pinjaman'
                )


            jumlah_baris_rek = RekeningRepository.perbarui_saldo(
                norek=norek,
                saldo_baru=saldo_baru,
                koneksi=koneksi
            )

            if jumlah_baris_rek != 1:
                raise ValueError(
                    "Gagal menambah saldo rekening"
                )

            transaksi = {"jenis":JenisTransaksi.PENCAIRAN_PINJAMAN,
                         "norek_tujuan":rekening.norek,
                         "nominal": nominal_pinjaman,
                         "saldo_tujuan_sebelum":saldo_sebelum,
                         "saldo_tujuan_sesudah":saldo_baru,
                         "jenis_referensi":JenisReferensi.PINJAMAN,
                         "id_referensi":id_pinjaman,
                         "waktu":datetime.datetime.now()}

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )

            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis='pencairan pinjaman',
                log=f"PENCAIRAN PINJAMAN {id_pinjaman} | "
                    f"+Rp{Utilitas.format_rupiah(nominal_pinjaman)}"
            )

            audit = AuditService.tambah_audit(
                kategori="finansial",
                objek="pinjaman",
                aksi="pencairan_pinjaman",
                log=(
                    f"Nasabah {nasabah.nama} mencairkan "
                    f"pinjaman dengan ID {id_pinjaman} sebesar "
                    f"Rp{Utilitas.format_rupiah(nominal_pinjaman)}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )
            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )
            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                nik_pemilik=nasabah.NIK,
                jenis_referensi=JenisReferensi.PINJAMAN,
                id_objek=id_pinjaman,
                koneksi=koneksi
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()


        return True




    @staticmethod
    def bayar_cicilan(
            nik,
            norek_pembayaran,
            id_pinjaman,
            hari_ini=None
    ):

        if hari_ini is None:
            hari_ini = datetime.date.today()

        if not isinstance(id_pinjaman, int):
            raise TypeError("ID pinjaman harus berupa angka")

        if id_pinjaman <= 0:
            raise ValueError("ID pinjaman tidak valid")


        koneksi = buat_koneksi()

        try:
            data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
                id_pinjaman=id_pinjaman,
                koneksi=koneksi
            )

            if data_pinjaman is None:
                raise ValueError("Pinjaman tidak ditemukan")


            norek = data_pinjaman['norek']

            if norek != norek_pembayaran:
                raise ValueError(
                    "Pinjaman tidak terdaftar pada rekening yang sedang digunakan"
                )

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            if rekening is None:
                raise ValueError(
                    "Rekening untuk pinjaman ini tidak ditemukan"
                )

            nasabah = rekening.pemilik

            if nik != nasabah.NIK:
                raise ValueError(
                    "Nasabah ini tidak terdaftar sebagai pemilik pinjaman"
                )
            if data_pinjaman['status'] != StatusPinjaman.AKTIF.value:
                raise ValueError(
                    "Pinjaman sedang tidak aktif"
                )

            Validator.amankan_rekening(rekening=rekening)

            pinjaman = PinjamanLoader.rangkai_pinjaman(
                data_pinjaman=data_pinjaman,
                nasabah=nasabah,
                rekening=rekening
            )

            if pinjaman.sisa_pokok <= 0:
                raise ValueError(
                    "Pinjaman tidak memiliki sisa pokok"
                )


            if pinjaman.cicilan_terbayar >= pinjaman.tenor:
                raise ValueError(
                    "Seluruh cicilan pinjaman telah dibayar"
                )


            if pinjaman.tanggal_pencairan is None:
                raise ValueError(
                    "Pinjaman belum memiliki tanggal pencairan"
                )

            if pinjaman.tanggal_jatuh_tempo is None:
                raise ValueError(
                    "Jadwal pembayaran pinjaman belum tersedia"
                )


            saldo_sebelum = rekening.saldo

            tenor = pinjaman.tenor
            bunga = pinjaman.bunga
            cicilan_tetap = pinjaman.cicilan_tetap
            cicilan_terbayar = pinjaman.cicilan_terbayar
            sisa_pokok = pinjaman.sisa_pokok

            tanggal_pencairan = pinjaman.tanggal_pencairan

            tanggal_jatuh_tempo = pinjaman.tanggal_jatuh_tempo


            tanggal_boleh_bayar = PinjamanService.tanggal_boleh_bayar(
                                                    cicilan_terbayar=cicilan_terbayar,
                                                    tanggal_pencairan=tanggal_pencairan)

            if hari_ini < tanggal_boleh_bayar:
                raise ValueError(f"Cicilan selanjutnya baru boleh dibayar mulai "
                                 f"{Utilitas.format_tanggal_indonesia(tanggal_boleh_bayar)}")

            hari_terlambat = PinjamanService.hitung_hari_terlambat(
                tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                hari_ini=hari_ini
            )

            denda = PinjamanService.hitung_denda(
                    tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                    cicilan_tetap=cicilan_tetap,
                    hari_ini=hari_ini)

            persentase_bunga = bunga / 12
            total_bayar = cicilan_tetap + denda
            bunga_bulanan = round(sisa_pokok * persentase_bunga)
            pokok_saja = cicilan_tetap - bunga_bulanan
            saldo_baru = saldo_sebelum - total_bayar


            if saldo_baru < rekening.saldosetor_min:
                raise ValueError(
                    "Saldo tidak cukup untuk membayar cicilan dan denda"
                )

            cicilan_terbayar_baru = cicilan_terbayar + 1

            pinjaman_lunas = cicilan_terbayar_baru >= tenor

            if pinjaman_lunas:
                tanggal_bayar_selanjutnya = None

                status_baru = StatusPinjaman.LUNAS
                sisa_pokok_baru = 0
                tanggal_jatuh_tempo_baru = tanggal_jatuh_tempo

                log_audit = (
                    f"{nasabah.nama} telah melunasi "
                    f"pinjaman {id_pinjaman} "
                    f"sebesar Rp"
                    f"{Utilitas.format_rupiah(total_bayar)}"
                )

                log_riwayat = (
                    f"PELUNASAN PINJAMAN | "
                    f"Cicilan Rp"
                    f"{Utilitas.format_rupiah(cicilan_tetap)} | "
                    f"Denda Rp{Utilitas.format_rupiah(denda)} | "
                    f"Terlambat {hari_terlambat} hari | "
                    f"Total Rp"
                    f"{Utilitas.format_rupiah(total_bayar)}"
                )

            else:
                tanggal_bayar_selanjutnya = PinjamanService.tanggal_boleh_bayar(
                    cicilan_terbayar=cicilan_terbayar_baru,
                    tanggal_pencairan=tanggal_pencairan
                )

                sisa_pokok_baru = sisa_pokok - pokok_saja
                status_baru = StatusPinjaman.AKTIF
                tanggal_jatuh_tempo_baru = Utilitas.tambah_bulan(
                    tanggal=tanggal_jatuh_tempo,
                    bulan=1)

                log_audit = (
                    f"{nasabah.nama} membayar cicilan "
                    f"pinjaman {id_pinjaman} "
                    f"sebesar Rp{Utilitas.format_rupiah(total_bayar)}"
                )

                log_riwayat = (
                    f"PEMBAYARAN CICILAN | "
                    f"Cicilan Rp{Utilitas.format_rupiah(cicilan_tetap)} | "
                    f"Denda Rp{Utilitas.format_rupiah(denda)} | "
                    f"Terlambat {hari_terlambat} hari | "
                    f"Total Rp{Utilitas.format_rupiah(total_bayar)}"
                )

            jumlah_baris_rek = RekeningRepository.perbarui_saldo(
                norek=norek,
                saldo_baru=saldo_baru,
                koneksi=koneksi
            )

            if jumlah_baris_rek != 1:
                raise ValueError(
                    "Gagal melakukan pembayaran cicilan"
                )

            jumlah_baris_pin = PinjamanRepository.perbarui_setelah_pembayaran(
                id_pinjaman=id_pinjaman,
                status_baru=status_baru,
                cicilan_terbayar_baru=cicilan_terbayar_baru,
                sisa_pokok_baru=sisa_pokok_baru,
                tanggal_jatuh_tempo_baru=tanggal_jatuh_tempo_baru,
                koneksi=koneksi)

            if jumlah_baris_pin != 1:
                raise ValueError("Gagal memperbarui status pinjaman")

            transaksi = {"jenis": JenisTransaksi.PEMBAYARAN_CICILAN,
                         "norek_sumber": norek,
                         "nominal": cicilan_tetap,
                         "biaya": denda,
                         "saldo_sumber_sebelum": saldo_sebelum,
                         "saldo_sumber_sesudah": saldo_baru,
                         "jenis_referensi": JenisReferensi.PINJAMAN,
                         "id_referensi": id_pinjaman,
                         "waktu": datetime.datetime.now()}

            audit = AuditService.tambah_audit(
                kategori="finansial",
                objek="pinjaman",
                aksi="pembayaran_cicilan_pinjaman",
                log=log_audit,
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=norek
            )

            riwayat = RiwayatTemplate.template(
                kategori='transaksi',
                jenis='pembayaran cicilan',
                log=log_riwayat
            )

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )

            RiwayatRepository.tambah_riwayat(
                norek=norek,
                riwayat=riwayat,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                nik_pemilik=nasabah.NIK,
                jenis_referensi=JenisReferensi.PINJAMAN,
                id_objek=id_pinjaman,
                koneksi=koneksi
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return {
            "id_pinjaman": id_pinjaman,
            "status": status_baru,
            "tanggal_bayar_selanjutnya": (
                None
                if pinjaman_lunas
                else tanggal_bayar_selanjutnya
            )
        }



    @staticmethod
    def tolak_pinjaman(id_pinjaman,catatan_admin):
        catatan_admin = catatan_admin.strip()
        if not catatan_admin:
            raise ValueError("Catatan tidak boleh kosong")
        koneksi = buat_koneksi()

        try:
            data_pinjaman = (
                PinjamanRepository.cari_pinjaman_dengan_id(
                    id_pinjaman=id_pinjaman,
                    koneksi=koneksi
                )
            )

            if data_pinjaman is None:
                raise ValueError(
                    f"Pinjaman ber-ID {id_pinjaman} tidak ditemukan"
                )

            if (
                    data_pinjaman["status"]
                    != StatusPinjaman.DIAJUKAN.value
            ):
                raise ValueError(
                    f"Pinjaman tidak dapat ditolak. "
                    f"Status saat ini: {data_pinjaman['status']}"
                )

            data_rekening = (
                RekeningRepository.cari_rekening_dengan_norek(
                    norek=data_pinjaman["norek"],
                    koneksi=koneksi
                )
            )

            if data_rekening is None:
                raise ValueError(
                    f"Rekening untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            data_nasabah = (
                NasabahRepository.cari_nasabah_dengan_nik(
                    nik=data_rekening["nik_pemilik"],
                    koneksi=koneksi
                )
            )

            if data_nasabah is None:
                raise ValueError(
                    f"Nasabah untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            status_baru = StatusPinjaman.DITOLAK.value

            jumlah_baris = (
                PinjamanRepository.perbarui_status_pinjaman(
                    id_pinjaman=id_pinjaman,
                    status_baru=status_baru,
                    koneksi=koneksi,
                    catatan=catatan_admin

                )
            )

            if jumlah_baris != 1:
                raise ValueError(
                    "Gagal memperbarui status pinjaman"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="pinjaman",
                aksi="penolakan_pinjaman",
                log=(
                    f"Pinjaman dengan ID {id_pinjaman} "
                    f"milik {data_nasabah['nama']} telah ditolak.\n"
                    f"Catatan admin: {catatan_admin}"
                ),
                nama=data_nasabah["nama"],
                nik=data_nasabah["nik"],
                norek=data_pinjaman["norek"]
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            NotifikasiService.buat_notifikasi_penolakan_pinjaman(
                id_pinjaman=id_pinjaman,
                nik_pemilik=data_nasabah['nik'],
                koneksi=koneksi,
                catatan_admin=catatan_admin
            )


            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True




    @staticmethod
    def tanggal_boleh_bayar(cicilan_terbayar,tanggal_pencairan):

        if cicilan_terbayar == 0:
            return tanggal_pencairan

        jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
            tanggal_pencairan,
            1
        )

        for _ in range(cicilan_terbayar - 1):
            jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
                jatuh_tempo_sebelumnya,
                1
            )

        return (
                jatuh_tempo_sebelumnya
                + datetime.timedelta(days=1)
        )

    @staticmethod
    def hitung_hari_terlambat(tanggal_jatuh_tempo,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        return  max(0,(hari_ini - tanggal_jatuh_tempo).days)


    @staticmethod
    def hitung_denda(tanggal_jatuh_tempo,cicilan_tetap,hari_ini=None):
        hari_terlambat = PinjamanService.hitung_hari_terlambat(tanggal_jatuh_tempo, hari_ini)

        hari_denda = max(0,hari_terlambat-PinjamanService.BATAS_HARI_TUNGGAKAN)

        denda = cicilan_tetap*hari_denda*PinjamanService.PERSENTASE_DENDA_HARIAN

        denda_maksimal =cicilan_tetap*PinjamanService.MAKSIMAL_PERSENTASE_DENDA

        return round(min(denda,denda_maksimal))

    @staticmethod
    def buat_pesan_pengingat(pinjaman, hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        if pinjaman.tanggal_jatuh_tempo is None:
            raise ValueError(
                f"Pinjaman ID {pinjaman.ID} belum memiliki jatuh tempo"
            )

        sisa_hari = (
                pinjaman.tanggal_jatuh_tempo - hari_ini
        ).days

        # Belum memasuki tiga hari terakhir.
        if sisa_hari > 3:
            return None

        # Tiga hari terakhir sebelum jatuh tempo.
        if 0 < sisa_hari <= 3:
            tanggal_jatuh_tempo = (
                Utilitas.format_tanggal_indonesia(
                    pinjaman.tanggal_jatuh_tempo
                )
            )

            return (
                f"Batas pembayaran cicilan ke-"
                f"{pinjaman.cicilan_terbayar + 1} "
                f"pinjaman ID {pinjaman.ID}\n"
                f"akan berakhir dalam {sisa_hari} hari, "
                f"pada {tanggal_jatuh_tempo}."
            )

        # Tepat pada tanggal jatuh tempo.
        if sisa_hari == 0:
            return (
                f"Hari ini adalah batas pembayaran cicilan ke-"
                f"{pinjaman.cicilan_terbayar + 1} "
                f"pinjaman ID {pinjaman.ID}."
            )

        # Lewat tanggal jatuh tempo.
        hari_terlambat = abs(sisa_hari)

        if hari_terlambat <= PinjamanService.BATAS_HARI_TUNGGAKAN:
            sisa_toleransi = (
                    PinjamanService.BATAS_HARI_TUNGGAKAN
                    - hari_terlambat
            )

            if sisa_toleransi == 0:
                return (
                    f"Hari ini adalah hari terakhir masa toleransi "
                    f"pembayaran cicilan pinjaman ID {pinjaman.ID}. "
                    f"Denda mulai dihitung besok jika cicilan "
                    f"belum dibayar."
                )

            return (
                f"Cicilan pinjaman ID {pinjaman.ID} terlambat "
                f"{hari_terlambat} hari. Masa toleransi tersisa "
                f"{sisa_toleransi} hari."
            )

        # Masa toleransi sudah berakhir.
        hari_denda = (
                hari_terlambat
                - PinjamanService.BATAS_HARI_TUNGGAKAN
        )

        denda = PinjamanService.hitung_denda(
            tanggal_jatuh_tempo=pinjaman.tanggal_jatuh_tempo,
            cicilan_tetap=pinjaman.cicilan_tetap,
            hari_ini=hari_ini
        )

        total_tagihan = pinjaman.cicilan_tetap + denda

        return (
            f"Cicilan pinjaman ID {pinjaman.ID} terlambat "
            f"{hari_terlambat} hari. Denda telah berjalan selama "
            f"{hari_denda} hari dengan nominal "
            f"Rp{Utilitas.format_rupiah(denda)}. "
            f"Total pembayaran saat ini "
            f"Rp{Utilitas.format_rupiah(total_tagihan)}."
        )

    @staticmethod
    def cari_pinjaman_nasabah(nik):

        daftar_pinjaman = (
            PinjamanRepository.cari_semua_pinjaman_dengan_nik(
                nik=nik
            )
        )

        return [
            PinjamanService._normalisasi_data_pinjaman(
                data_pinjaman
            )
            for data_pinjaman in daftar_pinjaman
        ]









    @staticmethod
    def _normalisasi_data_pinjaman(data_pinjaman):

        data_pinjaman = dict(data_pinjaman)

        data_pinjaman['status'] = StatusPinjaman(data_pinjaman['status'])

        if data_pinjaman['tanggal_pencairan'] is not None:
            data_pinjaman['tanggal_pencairan'] = (
                datetime.date.fromisoformat(data_pinjaman['tanggal_pencairan']
                                            )
            )

        if data_pinjaman['tanggal_jatuh_tempo'] is not None:
            data_pinjaman['tanggal_jatuh_tempo'] = (
                datetime.date.fromisoformat(data_pinjaman['tanggal_jatuh_tempo']
                                            )
            )

        return data_pinjaman


    @staticmethod
    def cari_semua_pinjaman_diajukan():
        daftar_pinjaman = PinjamanRepository.cari_semua_pinjaman_diajukan()

        return [
            PinjamanService._normalisasi_data_pinjaman(data_pinjaman=data_pinjaman)
                for data_pinjaman in daftar_pinjaman]



    @staticmethod
    def detail_pinjaman(id_pinjaman):

        data_pinjaman = PinjamanRepository.cari_detail_pinjaman(
            id_pinjaman=id_pinjaman
        )

        if data_pinjaman is None:
            return None

        detail_pinjaman = PinjamanService._normalisasi_data_pinjaman(
            data_pinjaman=data_pinjaman['detail_pinjaman']
        )

        pinjaman_aktif = dict(data_pinjaman['pinjaman_aktif'])

        return {
            "detail_pinjaman":detail_pinjaman,
            "pinjaman_aktif":pinjaman_aktif
        }

    @staticmethod
    def cari_semua_pinjaman_dengan_norek(
            norek,
            status
    ):

        daftar_pinjaman = (
            PinjamanRepository.cari_semua_pinjaman_dengan_norek(
                norek=norek,
                status=status
            )
        )

        return [
            PinjamanService._normalisasi_data_pinjaman(data_pinjaman)
            for data_pinjaman in daftar_pinjaman
        ]