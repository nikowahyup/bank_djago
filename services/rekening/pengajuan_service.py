import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import PengajuanRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.exceptions import InputTidakValid, PengajuanTidakDitemukan, StatusTidakValid, \
    RekeningTidakDitemukan, PerbaruiStatusGagal, NasabahTidakDitemukan
from bank_djago.services.transaksi.transaksi_service import TransaksiService

from bank_djago.utils.validator import Validator
from bank_djago.utils.utility import Utilitas, JenisTransaksi
from bank_djago.services.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis, buat_koneksi_baca


class PengajuanService:



    @staticmethod
    def ajukan_penutupan(nik, norek, alasan):

        alasan = alasan.strip()
        if not alasan:
            raise ValueError("Mohon isi alasan penutupan")

        with buat_koneksi_tulis() as koneksi:

            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

            if rekening is None:
                raise ValueError(
                    "Rekening tidak ditemukan"
                )
            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise ValueError(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)

            pengajuan_sebelumnya = PengajuanRepository.cari_pengajuan_aktif(
                norek=norek,
                jenis="tutup",
                koneksi=koneksi
            )

            if pengajuan_sebelumnya is not None:
                raise ValueError(
                    "Anda sudah mengajukan penutupan sebelumnya. Mohon tunggu konfirmasi admin"
                )

            id_pengajuan = PengajuanRepository.tambah_pengajuan(
                norek=rekening.norek,
                jenis="tutup",
                alasan=alasan,
                waktu_pengajuan=datetime.datetime.now(),
                koneksi=koneksi
            )
            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="pengajuan_penutupan_rekening",
                log=f"{rekening.pemilik.nama} mengajukan penutupan rekening {id_pengajuan}",
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )



        return id_pengajuan


    @staticmethod
    def tolak_pengajuan(id_pengajuan,catatan_admin):

        catatan_admin = catatan_admin.strip()
        if not catatan_admin:
            raise InputTidakValid(
                "Catatan tidak boleh kosong"
            )

        with buat_koneksi_tulis() as koneksi:

            cari_pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
                id_pengajuan,
                koneksi
            )

            if cari_pengajuan is None:
                raise PengajuanTidakDitemukan(
                    "Pengajuan tidak ditemukan"
                )

            if cari_pengajuan["status"] != "diajukan":
                raise StatusTidakValid(
                    f"Status pengajuan sudah {cari_pengajuan['status']}"
                )

            rekening = RekeningLoader.muat_rekening(
                cari_pengajuan["norek"],
                koneksi
            )


            jumlah_baris = PengajuanRepository.perbarui_pengajuan(
                id_pengajuan=id_pengajuan,
                status_baru="ditolak",
                waktu_proses=datetime.datetime.now(),
                catatan=catatan_admin,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui status pengajuan"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="penolakan_penutupan_rekening",
                log=f"Pengajuan {cari_pengajuan['jenis']} rekening ditolak",
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
            )
            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

        return True

    @staticmethod
    def setujui_pengajuan(id_pengajuan, catatan_admin):
        catatan_admin = catatan_admin.strip()

        if not catatan_admin:
            raise ValueError(
                "Catatan tidak boleh kosong"
            )

        with buat_koneksi_tulis() as koneksi:

            pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
                id_pengajuan=id_pengajuan,
                koneksi=koneksi
            )

            if pengajuan is None:
                raise PengajuanTidakDitemukan(
                    "Pengajuan tidak ditemukan"
                )

            if pengajuan["status"] != "diajukan":
                raise StatusTidakValid(
                    f"Status pengajuan sudah {pengajuan['status']}"
                )

            rekening = RekeningLoader.muat_rekening(
                pengajuan["norek"],
                koneksi
            )


            # Untuk sementara, jenis pengajuan yang sudah dapat
            # disetujui baru penutupan rekening.
            if pengajuan["jenis"] != "tutup":
                raise StatusTidakValid(
                    "Jenis pengajuan ini belum dapat diproses"
                )



            jumlah_baris = PengajuanRepository.perbarui_pengajuan(
                id_pengajuan=id_pengajuan,
                status_baru="disetujui",
                waktu_proses=datetime.datetime.now(),
                catatan=catatan_admin,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui status pengajuan"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="persetujuan_penutupan_rekening",
                log=(
                    f"Pengajuan {pengajuan['jenis']} "
                    f"rekening disetujui"
                ),
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
            )

            AuditRepository.tambah_audit(
                audit,
                koneksi
            )

        return True

    @staticmethod
    def selesaikan_penutupan(
            nik,
            norek,
            metode,
            norek_penerima=None
    ):


        if metode not in ("tarik", "transfer"):
            raise InputTidakValid(
                "Metode penyelesaian saldo tidak tersedia"
            )

        if metode == "transfer" and not norek_penerima:
            raise InputTidakValid(
                "Nomor rekening penerima wajib diisi"
            )



        penerima = None

        with buat_koneksi_tulis() as koneksi:

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )
            if rekening is None:
                raise RekeningTidakDitemukan(
                    "Rekening tidak terdaftar"
                )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NasabahTidakDitemukan(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            pengajuan = (
                PengajuanRepository.cari_penutupan_disetujui(
                    norek=rekening.norek,
                    koneksi=koneksi
                )
            )

            if pengajuan is None:
                raise PengajuanTidakDitemukan(
                    "Belum ada persetujuan penutupan "
                    "untuk rekening ini"
                )

            Validator.amankan_rekening(rekening=rekening)

            deposito_aktif = (
                DepositoRepository.cari_deposito_aktif(
                    norek=rekening.norek,
                    koneksi=koneksi
                )
            )

            pinjaman_aktif = (
                PinjamanRepository.cari_pinjaman_aktif(
                    norek=rekening.norek,
                    koneksi=koneksi
                )
            )

            if deposito_aktif is not None:
                raise StatusTidakValid(
                    "Rekening masih mempunyai deposito berjalan"
                )

            if pinjaman_aktif is not None:
                raise StatusTidakValid(
                    "Rekening masih mempunyai pinjaman berjalan"
                )


            nominal_penyelesaian = rekening.saldo

            if nominal_penyelesaian <= 0:
                raise StatusTidakValid(
                    "Tidak ada saldo yang bisa dikosongkan"
                )

            waktu_transaksi = datetime.datetime.now()
            status_lama = rekening.status
            status_baru = "tutup"

            jumlah_baris = RekeningRepository.perbarui_saldo_dan_status_untuk_penutupan(
                norek=rekening.norek,
                saldo_baru=0,
                status_lama=status_lama,
                status_baru=status_baru,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Terjadi kesalahan saat memproses penutupan rekening"
                )


            if metode == "tarik":


                transaksi = {
                    "jenis": (
                        JenisTransaksi
                        .PENARIKAN_SALDO_PENUTUPAN
                    ),
                    "norek_sumber": rekening.norek,
                    "nominal": nominal_penyelesaian,
                    "saldo_sumber_sebelum": rekening.saldo,
                    "saldo_sumber_sesudah": 0,
                    "waktu": waktu_transaksi
                }

                log_riwayat = (
                    "PENUTUPAN REKENING | "
                    f"Seluruh saldo Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                    "ditarik"
                )

                log_audit = (
                    "Rekening ditutup dengan penarikan "
                    f"seluruh saldo sebesar Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)}"
                )

                aksi_audit = "penarikan_saldo_penutupan"

            else:

                (
                    penerima,
                    nominal_penyelesaian,
                    saldo_baru_penerima

                ) = TransaksiService.transfer_semua_saldo(
                    rekening_asal=rekening,
                    norek_penerima=norek_penerima,
                    koneksi=koneksi
                )




                transaksi = {
                    "jenis": (
                        JenisTransaksi
                        .PEMINDAHAN_SALDO_PENUTUPAN
                    ),
                    "norek_sumber": rekening.norek,
                    "norek_tujuan": penerima.norek,
                    "nominal": nominal_penyelesaian,
                    "saldo_sumber_sebelum": rekening.saldo,
                    "saldo_sumber_sesudah": 0,
                    "saldo_tujuan_sebelum": penerima.saldo,
                    "saldo_tujuan_sesudah": saldo_baru_penerima,
                    "waktu": waktu_transaksi
                }

                log_riwayat = (
                    "PENUTUPAN REKENING | "
                    f"Seluruh saldo Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                    f"dipindahkan ke rekening {penerima.norek}"
                )

                log_audit = (
                    "Rekening ditutup dengan pemindahan "
                    f"seluruh saldo sebesar Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                    f"ke rekening {penerima.norek}"
                )

                aksi_audit = "pemindahan_saldo_penutupan"



            id_transaksi = (
                TransaksiRepository.tambah_transaksi(
                    transaksi=transaksi,
                    koneksi=koneksi
                )
            )

            if penerima is not None:
                audit_penerima = AuditService.tambah_audit(
                    kategori="finansial",
                    objek="rekening",
                    aksi="penerimaan_saldo_penutupan",
                    log=(
                        f"Menerima saldo Rp"
                        f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                        f"dari penutupan rekening {rekening.norek}"
                    ),
                    nama=penerima.pemilik.nama,
                    nik=penerima.pemilik.NIK,
                    norek=penerima.norek
                )

                AuditRepository.tambah_audit(
                    audit=audit_penerima,
                    koneksi=koneksi,
                    id_transaksi=id_transaksi
                )

                riwayat_penerima = (RiwayatTemplate.template(
                    kategori="transaksi",
                    jenis="terima saldo",
                    log=f"TERIMA SALDO PENUTUPAN REKENING | +Rp{Utilitas.format_rupiah(nominal_penyelesaian)} |"
                        f" Dari Nomor Rekening{rekening.norek}"))

                RiwayatRepository.tambah_riwayat(
                    norek=penerima.norek,
                    riwayat=riwayat_penerima,
                    koneksi=koneksi,
                    id_transaksi=id_transaksi
                )

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="penutupan rekening",
                log=log_riwayat
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            audit = AuditService.tambah_audit(
                kategori="finansial",
                objek="rekening",
                aksi=aksi_audit,
                log=log_audit,
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )



        return nominal_penyelesaian


    @staticmethod
    def cari_semua_pengajuan_diajukan():
        with buat_koneksi_baca() as koneksi:
            return PengajuanRepository.cari_semua_pengajuan_diajukan(koneksi=koneksi)

