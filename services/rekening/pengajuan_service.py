import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import PengajuanRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.validator import Validator
from bank_djago.utils.utility import Utilitas
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository


class PengajuanService:



    @staticmethod
    def ajukan_penutupan(rekening, alasan):
        Validator.amankan_rekening(rekening)
        alasan = alasan.strip()
        if not alasan:
            raise ValueError("Mohon isi alasan penutupan")

        koneksi = buat_koneksi()
        try:
            pengajuan_sebelumnya = PengajuanRepository.cari_pengajuan_aktif(rekening.norek,"tutup", koneksi)
            if pengajuan_sebelumnya is not None:
                raise ValueError("Anda sudah mengajukan penutupan sebelumnya. Silahkan tunggu konfirmasi admin")

            id_pengajuan = PengajuanRepository.tambah_pengajuan(norek=rekening.norek,jenis="tutup",alasan=alasan,waktu_pengajuan=datetime.datetime.now(),koneksi=koneksi)
            audit = AuditService.tambah_audit(kategori="rekening",jenis="pengajuan penutupan",log="Pengajuan penutupan rekening",nama=rekening.pemilik.nama,nik=rekening.pemilik.NIK,norek=rekening.norek)
            AuditRepository.tambah_audit(audit,koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise
        finally:
            koneksi.close()

        return id_pengajuan


    @staticmethod
    def tolak_pengajuan(id_pengajuan,catatan_admin):

        catatan_admin = catatan_admin.strip()
        if not catatan_admin:
            raise ValueError("Catatan tidak boleh kosong")

        koneksi = buat_koneksi()

        try:
            cari_pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
                id_pengajuan,
                koneksi
            )

            if cari_pengajuan is None:
                raise ValueError("Pengajuan tidak ditemukan")

            if cari_pengajuan["status"] != "diajukan":
                raise ValueError(
                    f"Status pengajuan sudah {cari_pengajuan['status']}"
                )

            rekening = RekeningLoader.muat_rekening(
                cari_pengajuan["norek"],
                koneksi
            )

            if rekening is None:
                raise ValueError(
                    "Rekening pada pengajuan tidak ditemukan"
                )

            jumlah_baris = PengajuanRepository.perbarui_pengajuan(id_pengajuan=id_pengajuan,status_baru="ditolak",waktu_proses=datetime.datetime.now(),catatan=catatan_admin,koneksi=koneksi)
            if jumlah_baris != 1:
                raise ValueError("Gagal memperbarui status pengajuan")

            audit = AuditService.tambah_audit(kategori="rekening",jenis="penolakan pengajuan",log=f"Pengajuan {cari_pengajuan['jenis']} rekening ditolak",nama=rekening.pemilik.nama,nik=rekening.pemilik.NIK,norek=rekening.norek)
            AuditRepository.tambah_audit(audit,koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()
        return True

    @staticmethod
    def setujui_pengajuan(id_pengajuan, catatan_admin):
        catatan_admin = catatan_admin.strip()

        if not catatan_admin:
            raise ValueError("Catatan tidak boleh kosong")

        koneksi = buat_koneksi()

        try:
            pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
                id_pengajuan=id_pengajuan,
                koneksi=koneksi
            )

            if pengajuan is None:
                raise ValueError("Pengajuan tidak ditemukan")

            if pengajuan["status"] != "diajukan":
                raise ValueError(
                    f"Status pengajuan sudah {pengajuan['status']}"
                )

            rekening = RekeningLoader.muat_rekening(
                pengajuan["norek"],
                koneksi
            )

            if rekening is None:
                raise ValueError(
                    "Rekening pada pengajuan tidak ditemukan"
                )

            if rekening.status != "aktif":
                raise ValueError(
                    f"Rekening saat ini berstatus {rekening.status}"
                )

            # Untuk sementara, jenis pengajuan yang sudah dapat
            # disetujui baru penutupan rekening.
            if pengajuan["jenis"] != "tutup":
                raise ValueError(
                    "Jenis pengajuan ini belum dapat diproses"
                )

            deposito_aktif = (
                DepositoRepository.cari_deposito_aktif(
                    rekening.norek,
                    koneksi
                )
            )

            pinjaman_aktif = (
                PinjamanRepository.cari_pinjaman_aktif(
                    rekening.norek,
                    koneksi
                )
            )

            if deposito_aktif is not None:
                raise ValueError(
                    "Rekening masih mempunyai deposito aktif"
                )

            if pinjaman_aktif is not None:
                raise ValueError(
                    "Rekening masih mempunyai pinjaman berjalan"
                )

            jumlah_baris = PengajuanRepository.perbarui_pengajuan(
                id_pengajuan=id_pengajuan,
                status_baru="disetujui",
                waktu_proses=datetime.datetime.now(),
                catatan=catatan_admin,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise ValueError(
                    "Gagal memperbarui status pengajuan"
                )

            audit = AuditService.tambah_audit(
                kategori="rekening",
                jenis="persetujuan pengajuan",
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

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True

    @staticmethod
    def selesaikan_penutupan(rekening, metode, norek_penerima=None):
        Validator.amankan_rekening(rekening)

        if metode not in ("tarik", "transfer"):
            raise ValueError("Metode penyelesaian saldo tidak tersedia")

        if metode == "transfer" and not norek_penerima:
            raise ValueError("Nomor rekening penerima wajib diisi")

        koneksi = buat_koneksi()
        penerima = None
        saldo_baru_penerima = None

        try:
            pengajuan = PengajuanRepository.cari_penutupan_disetujui(
                norek=rekening.norek,
                koneksi=koneksi
            )

            if pengajuan is None:
                raise ValueError(
                    "Belum ada persetujuan penutupan untuk rekening ini"
                )

            nominal_penyelesaian = rekening.saldo

            if metode == "tarik":
                log_riwayat = (
                    "PENUTUPAN REKENING | "
                    f"Seluruh saldo Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)} ditarik"
                )

                log_audit = (
                    "Rekening ditutup dengan penarikan seluruh saldo "
                    f"sebesar Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)}"
                )

                jenis_audit = "penutupan tarik saldo"

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
                audit_penerima = AuditService.tambah_audit(
                    kategori="transaksi",
                    jenis="terima saldo penutupan",
                    log=(
                        f"Menerima saldo Rp"
                        f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                        f"dari penutupan rekening {rekening.norek}"
                    ),
                    nama=penerima.pemilik.nama,
                    nik=penerima.pemilik.NIK,
                    norek=penerima.norek
                )
                AuditRepository.tambah_audit(audit_penerima, koneksi)

                riwayat_penerima = RiwayatTemplate.transfer_terima(
                    nominal_penyelesaian,
                    rekening
                )

                RiwayatRepository.tambah_riwayat(
                    norek=penerima.norek,
                    riwayat=riwayat_penerima,
                    koneksi=koneksi
                )

                log_riwayat = (
                    "PENUTUPAN REKENING | "
                    f"Seluruh saldo Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                    f"dipindahkan ke rekening {penerima.norek}"
                )

                log_audit = (
                    "Rekening ditutup dengan pemindahan seluruh saldo "
                    f"sebesar Rp"
                    f"{Utilitas.format_rupiah(nominal_penyelesaian)} "
                    f"ke rekening {penerima.norek}"
                )

                jenis_audit = "penutupan transfer saldo"

            jumlah_baris = (
                RekeningRepository.perbarui_saldo_dan_status(
                    norek=rekening.norek,
                    saldo_baru=0,
                    status_baru="tutup",
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise ValueError("Gagal melakukan penutupan rekening")

            riwayat = RiwayatTemplate.template(
                kategori="sistem",
                jenis="penutupan rekening",
                log=log_riwayat
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi
            )

            audit = AuditService.tambah_audit(
                kategori="rekening",
                jenis=jenis_audit,
                log=log_audit,
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
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

        rekening.set_saldo(0)
        rekening.status = "tutup"
        rekening.simpan_riwayat(riwayat)

        if penerima is not None:
            penerima.set_saldo(saldo_baru_penerima)

        return nominal_penyelesaian

