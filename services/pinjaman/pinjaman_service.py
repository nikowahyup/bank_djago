import datetime


from bank_djago.core.pinjaman import Pinjaman

from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.utils.utility import StatusPinjaman
from bank_djago.services.notifikasi.notifikasi_service import NotifikasiService
from bank_djago.services.riwayat.riwayat_template import RiwayatTemplate

from bank_djago.services.exceptions import (
    InputTidakValid, RekeningTidakDitemukan, NikTidakSesuai, StatusTidakValid,
    PinjamanTidakDitemukan, PerbaruiStatusGagal, RekeningTidakSesuai, PenambahanSaldoGagal,
    PenguranganSaldoGagal
)
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.utility import JenisReferensi
from bank_djago.utils.utility import JenisTransaksi
from bank_djago.utils.validator import Validator



from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.penyimpanan.repositories.notifikasi_repository import NotifikasiRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository

from bank_djago.penyimpanan.loaders.pinjaman_loader import PinjamanLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader




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



        if not isinstance(nominal, int):
            raise InputTidakValid(
                "Nominal harus berupa angka"
            )

        if not isinstance(tenor, int):
            raise InputTidakValid(
                "Jangka waktu harus berupa angka"
            )

        if nominal < PinjamanService.MIN_PINJAMAN:
            raise InputTidakValid(
                "Nominal pinjaman di bawah batas minimal"
            )

        if nominal > PinjamanService.MAX_PINJAMAN:
            raise InputTidakValid(
                "Nominal pinjaman melebihi batas maksimal"
            )

        if tenor not in PinjamanService.TENOR:
            raise InputTidakValid(
                "Pilihan tenor pinjaman tidak tersedia"
            )

        with buat_koneksi_tulis() as koneksi:

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            if rekening is None:
                raise RekeningTidakDitemukan(
                    "Rekening tidak ditemukan"
                )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NikTidakSesuai(
                    "NIK nasabah tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)

            pengajuan_aktif = (
                PinjamanRepository.cari_pengajuan_aktif_nasabah(
                    nik=nasabah.NIK,
                    koneksi=koneksi
                )
            )

            if pengajuan_aktif is not None:
                raise StatusTidakValid(
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
                kategori="pinjaman",
                jenis="pembukaan pinjaman",
                log=(
                    f"PENGAJUAN PINJAMAN | ID {id_pinjaman} | "
                    f"Rp{Utilitas.format_rupiah(nominal)} s| "
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



        return id_pinjaman

    @staticmethod
    def setujui_pinjaman(id_pinjaman):


        if not isinstance(id_pinjaman, int):
            raise InputTidakValid(
                "ID pinjaman harus berupa angka"
            )

        if id_pinjaman <= 0:
            raise InputTidakValid(
                "ID pinjaman tidak valid"
            )
        with buat_koneksi_tulis() as koneksi:
            data_pinjaman = (
                PinjamanRepository.cari_pinjaman_dengan_id(
                    id_pinjaman=id_pinjaman,
                    koneksi=koneksi
                )
            )

            if data_pinjaman is None:
                raise PinjamanTidakDitemukan(
                    f"Pinjaman ber-ID {id_pinjaman} tidak ditemukan"
                )

            if (
                    data_pinjaman["status"]
                    != StatusPinjaman.DIAJUKAN.value
            ):
                raise StatusTidakValid(
                    f"Pinjaman tidak dapat disetujui. "
                    f"Status saat ini: {data_pinjaman['status']}"
                )
            norek = data_pinjaman['norek']

            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

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
                raise PerbaruiStatusGagal(
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

        return True




    @staticmethod
    def cairkan_pinjaman(
            nik : str,
            norek_pencairan : str,
            id_pinjaman : int,
            hari_ini : datetime.date | None=None
    ) -> int:


        """
        Pencairan pinjaman setelah statusnya disetujui
        Menangani beberapa validasi seperti ID pinjaman harus valid,
        status pinjaman harus valid, konsistensi hubungan pinjaman -> rekening -> nasabah,

        Args:
            nik: NIK yang mencoba mencairkan pinjaman
            norek_pencairan: Nomor rekening yang mencoba mencairkan pinjaman
            id_pinjaman: ID pinjaman dari input UI
            hari_ini: waktu pencairan pinjaman. Bisa juga digunakan waktu pengujian

        Raises:

        """

        if hari_ini is None:
            hari_ini = datetime.date.today()

        if not isinstance(id_pinjaman, int):
            raise InputTidakValid(
                "ID pinjaman harus berupa angka"
            )

        if id_pinjaman <= 0:
            raise InputTidakValid(
                "ID pinjaman tidak valid"
            )

        if not isinstance(nik, str):
            raise InputTidakValid(
                "NIK tidak valid"
            )
        if not isinstance(norek_pencairan, str):
            raise  InputTidakValid(
                "Nomor rekening tidak valid"
            )

        with buat_koneksi_tulis() as koneksi:
            data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
                id_pinjaman=id_pinjaman,
                koneksi=koneksi
            )

            if data_pinjaman is None:
                raise PinjamanTidakDitemukan(
                    "Pinjaman tidak ditemukan"
                )


            norek = data_pinjaman['norek']

            if norek != norek_pencairan:
                raise RekeningTidakSesuai(
                    "Rekening ini tidak terdaftar sebagai pemilik pinjaman"
                )

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik pinjaman"
                )
            Validator.amankan_rekening(rekening=rekening)

            if data_pinjaman['status'] != StatusPinjaman.DISETUJUI.value:
                raise StatusTidakValid(
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
                raise PerbaruiStatusGagal(
                    'Gagal memperbarui status pinjaman'
                )


            jumlah_baris_rek = RekeningRepository.tambah_saldo(
                norek=rekening.norek,
                nominal=pinjaman.nominal_pinjaman,
                koneksi=koneksi
            )

            if jumlah_baris_rek != 1:
                raise PenambahanSaldoGagal(
                    "Gagal menambah saldo rekening"
                )

            saldo_baru = RekeningRepository.ambil_saldo(
                norek=rekening.norek,
                koneksi=koneksi
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
                kategori="pinjaman",
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


        return True




    @staticmethod
    def bayar_cicilan(
            nik,
            norek_pembayaran,
            id_pinjaman,
            hari_ini : datetime.date | None=None
    ):

        if hari_ini is None:
            hari_ini = datetime.date.today()

        if not isinstance(id_pinjaman, int):
            raise InputTidakValid(
                "ID pinjaman harus berupa angka"
            )

        if id_pinjaman <= 0:
            raise InputTidakValid(
                "ID pinjaman tidak valid"
            )

        with buat_koneksi_tulis() as koneksi:

            data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
                id_pinjaman=id_pinjaman,
                koneksi=koneksi
            )

            if data_pinjaman is None:
                raise PinjamanTidakDitemukan(
                    "Pinjaman tidak ditemukan"
                )


            norek = data_pinjaman['norek']

            if norek != norek_pembayaran:
                raise RekeningTidakSesuai(
                    "Rekening ini tidak terdaftar sebagai pemilik pinjaman"
                )

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )


            nasabah = rekening.pemilik

            if nik != nasabah.NIK:
                raise NikTidakSesuai(
                    "Nasabah ini tidak terdaftar sebagai pemilik pinjaman"
                )
            if data_pinjaman['status'] != StatusPinjaman.AKTIF.value:
                raise StatusTidakValid(
                    "Pinjaman sedang tidak aktif"
                )

            Validator.amankan_rekening(rekening=rekening)

            pinjaman = PinjamanLoader.rangkai_pinjaman(
                data_pinjaman=data_pinjaman,
                nasabah=nasabah,
                rekening=rekening
            )



            if pinjaman.cicilan_terbayar >= pinjaman.tenor:
                raise StatusTidakValid(
                    "Seluruh cicilan pinjaman telah dibayar"
                )


            if pinjaman.tanggal_pencairan is None:
                raise StatusTidakValid(
                    "Pinjaman belum memiliki tanggal pencairan"
                )

            if pinjaman.tanggal_jatuh_tempo is None:
                raise StatusTidakValid(
                    "Jadwal pembayaran pinjaman belum tersedia"
                )


            saldo_sebelum = rekening.saldo

            tenor = pinjaman.tenor
            bunga = pinjaman.bunga
            cicilan_tetap = pinjaman.cicilan_tetap
            cicilan_terbayar = pinjaman.cicilan_terbayar
            sisa_pokok = pinjaman.sisa_pokok

            tanggal_pencairan = pinjaman.tanggal_pencairan

            tanggal_jatuh_tempo_lama = pinjaman.tanggal_jatuh_tempo


            tanggal_boleh_bayar = pinjaman.tanggal_boleh_bayar()

            if hari_ini < tanggal_boleh_bayar:
                raise StatusTidakValid(f"Cicilan selanjutnya baru boleh dibayar mulai "
                                 f"{Utilitas.format_tanggal_indonesia(tanggal_boleh_bayar)}")

            hari_terlambat = pinjaman.hitung_hari_terlambat(hari_ini=hari_ini)

            denda = pinjaman.hitung_denda(hari_ini=hari_ini)

            persentase_bunga = bunga / 12
            total_bayar = cicilan_tetap + denda
            bunga_bulanan = round(sisa_pokok * persentase_bunga)
            pokok_saja = cicilan_tetap - bunga_bulanan



            cicilan_terbayar_baru = cicilan_terbayar + 1

            pinjaman_lunas = cicilan_terbayar_baru >= tenor

            if pinjaman_lunas:
                tanggal_bayar_selanjutnya = None

                status_baru = StatusPinjaman.LUNAS
                sisa_pokok_baru = 0
                tanggal_jatuh_tempo_baru = tanggal_jatuh_tempo_lama

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
                    tanggal=tanggal_jatuh_tempo_lama,
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


            jumlah_baris_pinjaman = (
                PinjamanRepository.perbarui_setelah_pembayaran(
                id_pinjaman=id_pinjaman,
                status_baru=status_baru,
                cicilan_terbayar_baru=cicilan_terbayar_baru,
                sisa_pokok_baru=sisa_pokok_baru,
                tanggal_jatuh_tempo_lama=tanggal_jatuh_tempo_lama,
                tanggal_jatuh_tempo_baru=tanggal_jatuh_tempo_baru,
                koneksi=koneksi
                )

            )



            if jumlah_baris_pinjaman != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui status pinjaman"
                )

            saldo_minimal = rekening.saldosetor_min

            jumlah_baris_rek = RekeningRepository.kurangi_saldo(
                norek=norek,
                nominal=total_bayar,
                saldo_minimal=saldo_minimal,
                koneksi=koneksi
            )


            if jumlah_baris_rek != 1:
                raise PenguranganSaldoGagal(
                    "Gagal melakukan pembayaran cicilan"
                )

            saldo_baru = RekeningRepository.ambil_saldo(
                norek=rekening.norek,
                koneksi=koneksi
            )

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
                kategori='pinjaman',
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
    def tolak_pinjaman(id_pinjaman : int, catatan_admin : str):
        catatan_admin = catatan_admin.strip()
        if not catatan_admin:
            raise InputTidakValid(
                "Catatan tidak boleh kosong"
            )

        if not isinstance(id_pinjaman, int):
            raise InputTidakValid(
                "ID pinjaman harus berupa angka"
            )
        if id_pinjaman <= 0:
            raise InputTidakValid(
                "ID pinjaman tidak valid"
            )





        with buat_koneksi_tulis() as koneksi:
            data_pinjaman = (
                PinjamanRepository.cari_pinjaman_dengan_id(
                    id_pinjaman=id_pinjaman,
                    koneksi=koneksi
                )
            )

            if data_pinjaman is None:
                raise PinjamanTidakDitemukan(
                    f"Pinjaman ber-ID {id_pinjaman} tidak ditemukan"
                )

            if (
                    data_pinjaman["status"]
                    != StatusPinjaman.DIAJUKAN.value
            ):
                raise StatusTidakValid(
                    f"Pinjaman tidak dapat ditolak. "
                    f"Status saat ini: {data_pinjaman['status']}"
                )

            norek = data_pinjaman['norek']
            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

            if rekening is None:
                raise RekeningTidakDitemukan(
                    f"Rekening untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            nasabah = rekening.pemilik

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
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui status pinjaman"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="pinjaman",
                aksi="penolakan_pinjaman",
                log=(
                    f"Pinjaman dengan ID {id_pinjaman} "
                    f"milik {nasabah.nama} ditolak.\n"
                    f"Catatan admin: {catatan_admin}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            NotifikasiService.buat_notifikasi_penolakan_pinjaman(
                id_pinjaman=id_pinjaman,
                nik_pemilik=nasabah.NIK,
                koneksi=koneksi,
                catatan_admin=catatan_admin
            )


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


    # method pembuat pesan siklus pinjaman
    @staticmethod
    def buat_pesan_pengingat(pinjaman, hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

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

        denda = pinjaman.hitung_denda(hari_ini=hari_ini)

        total_tagihan = pinjaman.cicilan_tetap + denda

        return (
            f"Cicilan pinjaman ID {pinjaman.ID} terlambat "
            f"{hari_terlambat} hari. Denda telah berjalan selama "
            f"{hari_denda} hari dengan nominal "
            f"Rp{Utilitas.format_rupiah(denda)}. "
            f"Total pembayaran saat ini "
            f"Rp{Utilitas.format_rupiah(total_tagihan)}."
        )

    # method untuk mencari semua pinjaman yang dimiliki nasabah
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


    # method pengonversi tipe data database ke tipe data program
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


    # method untuk filter status pinjaman yang masih diajukan untuk admin
    @staticmethod
    def cari_semua_pinjaman_diajukan():
        daftar_pinjaman = PinjamanRepository.cari_semua_pinjaman_diajukan()

        return [
            PinjamanService._normalisasi_data_pinjaman(data_pinjaman=data_pinjaman)
                for data_pinjaman in daftar_pinjaman]


    # method untuk mencari ddetail pinjaman untuk bahan pertimbangan keputusan admin
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

    # method untuk filter pinjaman berdasarkan nomor rekening dan statusnya
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