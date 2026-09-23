import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.utils.utility import Utilitas,JenisTransaksi
from bank_djago.services.transaksi.limit_service import LimitService
from bank_djago.services.admin.audit_service import  AuditService
from bank_djago.services.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi, buat_koneksi_tulis
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository

from bank_djago.services.exceptions import (
    InputTidakValid, RekeningTidakDitemukan, PenambahanSaldoGagal,
    StatusTidakValid, PerbaruiStatusGagal, PenguranganSaldoGagal, NikTidakSesuai
)

class TransaksiService:

    @staticmethod
    def setor_tunai(nik_masuk,norek ,nominal):

        if nominal < 10000:
            raise InputTidakValid(
                "Minimal setor adalah Rp10.000"
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

            if nasabah.NIK != nik_masuk:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)


            jumlah_baris =  RekeningRepository.tambah_saldo(
                norek=norek,
                nominal=nominal,
                koneksi=koneksi
            )


            if jumlah_baris != 1 :
                raise PenambahanSaldoGagal(
                    "Gagal melakukan setor tunai"
                )

            saldo_baru = RekeningRepository.ambil_saldo(
                norek=rekening.norek,
                koneksi=koneksi
            )

            transaksi = {
                "jenis": JenisTransaksi.SETOR_TUNAI,
                "norek_tujuan": rekening.norek,
                "nominal": nominal,
                "saldo_tujuan_sebelum": rekening.saldo,
                "saldo_tujuan_sesudah": saldo_baru,
                "waktu": datetime.datetime.now()
            }

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )

            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="setor uang",
                log=f"SETOR UANG | +Rp{Utilitas.format_rupiah(nominal)}"
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
                aksi="setor_tunai",
                log=f"Setor uang Rp{Utilitas.format_rupiah(nominal)}",
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
            )
            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )



        return True

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def tarik_tunai(nik_masuk,norek, nominal):

        if nominal < 10000:
            raise InputTidakValid(
                "Minimal tarik adalah Rp10.000"
            )

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

            if nasabah.NIK != nik_masuk:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)

            if rekening.saldo - nominal < rekening.saldosetor_min:
                raise StatusTidakValid(
                    f"Saldo tidak memenuhi saldo minimum jika Anda\n"
                    f" menarik sebesar Rp{Utilitas.format_rupiah(nominal)}"
                )

            saldo_minimal = rekening.saldosetor_min

            jumlah_baris = RekeningRepository.kurangi_saldo(
                norek=rekening.norek,
                nominal=nominal,
                saldo_minimal=saldo_minimal,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PenguranganSaldoGagal(
                    "Gagal melakukan tarik tunai"
                )

            saldo_baru = RekeningRepository.ambil_saldo(
                norek=norek,
                koneksi=koneksi
            )

            transaksi = {
                "jenis": JenisTransaksi.TARIK_TUNAI,
                "norek_sumber": rekening.norek,
                "nominal": nominal,
                "saldo_sumber_sebelum": rekening.saldo,
                "saldo_sumber_sesudah": saldo_baru,
                "waktu": datetime.datetime.now()
            }

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )
            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="tarik uang",
                log=f"TARIK UANG | -Rp{Utilitas.format_rupiah(nominal)}"
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
                aksi="tarik_tunai",
                log=f"Tarik uang Rp{Utilitas.format_rupiah(nominal)}",
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
            )
            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )


        return True

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def transfer(
            nik_masuk,
            norek_pengirim,
            norek_penerima,
            nominal
    ):

        if nominal < 10000:
            raise InputTidakValid(
                "Minimal transfer adalah Rp10.000"
            )
        with buat_koneksi_tulis() as koneksi:

            pengirim = RekeningLoader.muat_rekening(
                norek=norek_pengirim,
                koneksi=koneksi
            )

            if pengirim is None:
                raise RekeningTidakDitemukan(
                    "Rekening pengirim tidak terdaftar"
                )

            nasabah = pengirim.pemilik

            if nasabah.NIK != nik_masuk:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(pengirim)

            penerima = TransaksiService.cari_penerima(
                norek_penerima=norek_penerima,
                norek_pengirim=norek_pengirim,
                koneksi=koneksi
            )

            limit_sisa,reset_baru,is_reset = LimitService.hitung_limit_saat_ini(pengirim)

            total = nominal + pengirim.pajak

            if pengirim.saldo - total < pengirim.saldosetor_min:
                raise StatusTidakValid(
                    "Saldo Anda tidak cukup untuk melakukan transfer"
                )

            if limit_sisa is None:
                limit_baru = None
            else:
                limit_baru = limit_sisa - total
                if limit_baru < 0:
                    raise StatusTidakValid(
                        "Limit harian telah habis"
                    )


            pengurangan_saldo_pengirim = total
            penambahan_saldo_penerima =  nominal
            saldo_minimal_pengirim = pengirim.saldosetor_min

            if is_reset:
                riwayat_reset = RiwayatTemplate.template(
                    kategori="sistem",
                    jenis="reset limit",
                    log="reset limit transfer harian"
                )

                RiwayatRepository.tambah_riwayat(
                    norek=pengirim.norek,
                    riwayat=riwayat_reset,
                    koneksi=koneksi)



            jumlah_baris_pengirim = RekeningRepository.kurangi_saldo(
                norek=pengirim.norek,
                nominal=pengurangan_saldo_pengirim,
                saldo_minimal=saldo_minimal_pengirim,
                koneksi=koneksi
            )

            jumlah_baris_penerima = RekeningRepository.tambah_saldo(
                norek=penerima.norek,
                nominal=penambahan_saldo_penerima,
                koneksi=koneksi
            )

            jumlah_baris_limit =RekeningRepository.perbarui_limit(
                limit_baru=limit_baru,
                reset_baru=reset_baru,
                norek=pengirim.norek,
                koneksi=koneksi
            )


            if jumlah_baris_pengirim != 1:
                raise PenguranganSaldoGagal(
                    "Tidak dapat melakukan transfer"
                )

            if jumlah_baris_limit != 1:
                raise PerbaruiStatusGagal(
                    "Terjadi kesalahan saat memperbarui limit"
                )


            if jumlah_baris_penerima != 1:
                raise PenambahanSaldoGagal(
                    "Tidak dapat melakukan transfer"
                )

            saldo_setelah_pengirim = RekeningRepository.ambil_saldo(
                norek=pengirim.norek,
                koneksi=koneksi
            )

            saldo_setelah_penerima = RekeningRepository.ambil_saldo(
                norek=penerima.norek,
                koneksi=koneksi
            )

            transaksi = {
                "jenis": JenisTransaksi.TRANSFER,
                "norek_sumber": pengirim.norek,
                "norek_tujuan":penerima.norek,
                "nominal": nominal,
                "saldo_sumber_sebelum": pengirim.saldo,
                "saldo_sumber_sesudah": saldo_setelah_pengirim,
                "saldo_tujuan_sebelum": penerima.saldo,
                "saldo_tujuan_sesudah": saldo_setelah_penerima,
                "biaya":pengirim.pajak,
                "waktu": datetime.datetime.now()
            }

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )


            riwayat_pengirim = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="transer saldo",
                log=f"TRANSFER UANG | -Rp{Utilitas.format_rupiah(nominal)} | Penerima {penerima.pemilik.nama} "
            )
            riwayat_penerima = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="terima saldo",
                log=f"TERIMA UANG | +Rp{Utilitas.format_rupiah(nominal)} | Dari {pengirim.pemilik.nama}"
            )
            
            audit_penerima = AuditService.tambah_audit(
                kategori="finansial",
                objek="rekening",
                aksi="penerimaan_transfer",
                log=f"Terima saldo Rp{Utilitas.format_rupiah(nominal)}",
                nama=penerima.pemilik.nama,
                nik=penerima.pemilik.NIK,
                norek=penerima.norek
            )
            
            audit_pengirim = AuditService.tambah_audit(
                kategori="finansial",
                objek="rekening",
                aksi="transfer_keluar",
                log=f"Transfer Rp{Utilitas.format_rupiah(nominal)}",
                nama=pengirim.pemilik.nama,
                nik=pengirim.pemilik.NIK,
                norek=pengirim.norek
            )


            RiwayatRepository.tambah_riwayat(
                norek=pengirim.norek,
                riwayat=riwayat_pengirim,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )
            
            RiwayatRepository.tambah_riwayat(
                norek=penerima.norek,
                riwayat=riwayat_penerima,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )
            
            AuditRepository.tambah_audit(
                audit=audit_pengirim,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )
            AuditRepository.tambah_audit(
                audit=audit_penerima,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )



        return True



    @staticmethod
    def cari_penerima(
            norek_penerima,
            norek_pengirim,
            koneksi=None
    ):

        from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader

        if norek_penerima == norek_pengirim:
                raise StatusTidakValid(
                    "Tidak dapat transfer ke nomor rekening sendiri"
                )

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:

            penerima = RekeningLoader.muat_rekening(norek=norek_penerima,koneksi=koneksi)

            if penerima is None:
                raise RekeningTidakDitemukan(
                    "Rekening penerima tidak terdaftar"
                )

            if penerima.status != "aktif":
                    raise StatusTidakValid(
                        f"Rekening penerima saat ini sedang di{penerima.status}"
                    )

            return penerima

        finally:
            if kelola_koneksi:
                koneksi.close()




    @staticmethod
    def transfer_semua_saldo(
            rekening_asal,
            norek_penerima,
            koneksi
    ):

        penerima = TransaksiService.cari_penerima(
            norek_penerima=norek_penerima,
            norek_pengirim=rekening_asal,
            koneksi=koneksi
        )

        nominal_transfer = rekening_asal.saldo

        jumlah_baris_penerima = (
            RekeningRepository.tambah_saldo(
                norek=penerima.norek,
                nominal=nominal_transfer,
                koneksi=koneksi
            )
        )

        if jumlah_baris_penerima != 1:
            raise PenambahanSaldoGagal(
                "Gagal memindahkan saldo ke rekening penerima"
            )
        saldo_baru_penerima = RekeningRepository.ambil_saldo(
            norek=penerima.norek,
            koneksi=koneksi
        )

        return penerima, nominal_transfer, saldo_baru_penerima
