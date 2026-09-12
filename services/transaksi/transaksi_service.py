import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.utils.utility import Utilitas,JenisTransaksi
from bank_djago.services.transaksi.limit_service import LimitService
from bank_djago.services.admin.audit_service import  AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository


class TransaksiService:

    @staticmethod
    def setor_tunai(norek ,nominal):

        if nominal < 10000:
            raise ValueError("Minimal setor adalah Rp10.000")

        koneksi = buat_koneksi()

        try:
            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )
            if rekening is None:
                raise ValueError("Rekening tidak ditemukan")

            Validator.amankan_rekening(rekening)

            saldo_baru = rekening.saldo + nominal

            jumlah_baris =  RekeningRepository.perbarui_saldo(
                norek=norek,
                saldo_baru=saldo_baru,
                koneksi=koneksi
            )

            if jumlah_baris != 1 :
                raise ValueError("Gagal melakukan setor tunai")

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

            riwayat = RiwayatTemplate.setor_uang(nominal)

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
            AuditRepository.tambah_audit(audit, koneksi,id_transaksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True

    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def tarik_tunai(norek, nominal):

        if nominal < 10000:
            raise ValueError("Minimal tarik adalah Rp10.000")

        koneksi = buat_koneksi()

        try:
            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            if rekening is None:
                raise ValueError("Rekening tidak terdaftar")


            Validator.amankan_rekening(rekening)

            if rekening.saldo - nominal < rekening.saldosetor_min:
                raise ValueError(
                    f"Saldo tidak memenuhi saldo minimum jika Anda\n"
                    f" menarik sebesar Rp{Utilitas.format_rupiah(nominal)}"
                )

            saldo_baru = rekening.saldo - nominal

            jumlah_baris = RekeningRepository.perbarui_saldo(
                norek=norek,
                saldo_baru=saldo_baru,
                koneksi=koneksi
            )
            if jumlah_baris != 1:
                raise ValueError("Gagal melakukan tarik tunai")


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
            riwayat = RiwayatTemplate.tarik_uang(nominal)

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

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()


        return True
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def transfer(
            norek_pengirim,
            norek_penerima,
            nominal
    ):

        if nominal < 10000:
            raise ValueError(
                "Minimal transfer adalah Rp10.000"
            )
        koneksi = buat_koneksi()


        try:

            pengirim = RekeningLoader.muat_rekening(
                norek=norek_pengirim,
                koneksi=koneksi
            )

            if pengirim is None:
                raise ValueError(
                    "Rekening pengirim tidak terdaftar"
                )


            Validator.amankan_rekening(pengirim)

            penerima = TransaksiService.cari_penerima(
                norek_penerima=norek_penerima,
                norek_pengirim=norek_pengirim,
                koneksi=koneksi
            )

            limit_sekarang,reset_baru,reset_terjadi = LimitService.hitung_limit_saat_ini(pengirim)

            total = nominal + pengirim.pajak

            if pengirim.saldo - total < pengirim.saldosetor_min:
                raise ValueError(
                    "Saldo Anda tidak cukup untuk melakukan transfer"
                )

            if limit_sekarang is None:
                limit_baru = None
            else:
                limit_baru = limit_sekarang - total
                if limit_baru < 0:
                    raise ValueError("Limit harian telah habis")


            saldo_khusus_pengirim = pengirim.saldo - total
            saldo_khusus_penerima = penerima.saldo + nominal

            if reset_terjadi:
                riwayat_reset = RiwayatTemplate.template(
                    kategori="sistem",
                    jenis="reset limit",
                    log="reset limit transfer harian"
                )

                RiwayatRepository.tambah_riwayat(
                    norek=pengirim.norek,
                    riwayat=riwayat_reset,
                    koneksi=koneksi)



            jumlah_baris_pengirim = RekeningRepository.perbarui_saldo(
                norek=pengirim.norek,
                saldo_baru=saldo_khusus_pengirim,
                koneksi=koneksi
            )
            jumlah_baris_penerima = RekeningRepository.perbarui_saldo(
                norek=penerima.norek,
                saldo_baru=saldo_khusus_penerima,
                koneksi=koneksi
            )
            jumlah_baris_limit =RekeningRepository.perbarui_limit(
                limit_baru=limit_baru,
                reset_baru=reset_baru,
                norek=pengirim.norek,
                koneksi=koneksi
            )


            if jumlah_baris_pengirim != 1:
                raise ValueError("Tidak dapat melakukan transfer")

            if jumlah_baris_limit != 1:
                raise ValueError("Terjadi kesalahan saat memperbarui limit")


            if jumlah_baris_penerima != 1:
                raise ValueError("Tidak dapat melakukan transfer")

            transaksi = {
                "jenis": JenisTransaksi.TRANSFER,
                "norek_sumber": pengirim.norek,
                "norek_tujuan":penerima.norek,
                "nominal": nominal,
                "saldo_sumber_sebelum": pengirim.saldo,
                "saldo_sumber_sesudah": saldo_khusus_pengirim,
                "saldo_tujuan_sebelum": penerima.saldo,
                "saldo_tujuan_sesudah": saldo_khusus_penerima,
                "biaya":pengirim.pajak,
                "waktu": datetime.datetime.now()
            }

            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi=transaksi, koneksi=koneksi)


            riwayat_pengirim = RiwayatTemplate.transfer_kirim(nominal,penerima)
            riwayat_penerima = RiwayatTemplate.transfer_terima(nominal,pengirim)
            
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

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True

    @staticmethod
    def tarik_semua_uang(rekening):
        Validator.amankan_rekening(rekening)
        total = rekening.saldo
        rekening.kurangi_saldo(total)


    @staticmethod
    def transfer_semua_uang(rekening,penerima):
        Validator.amankan_rekening(rekening)
        total = rekening.saldo
        rekening.kurangi_saldo(total)
        penerima.tambah_saldo(total)


    @staticmethod
    def cari_penerima(
            norek_penerima,
            norek_pengirim,
            koneksi=None
    ):

        from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader

        if norek_penerima == norek_pengirim:
                raise ValueError("Tidak dapat transfer ke nomor rekening sendiri")
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:

            penerima = RekeningLoader.muat_rekening(norek_penerima,koneksi)

            if penerima is None:
                raise ValueError("Rekening penerima tidak terdaftar")

            if penerima.status != "aktif":
                    raise ValueError(f"Rekening penerima sudah/telah di{penerima.status}")

            return penerima

        finally:
            if kelola_koneksi:
                koneksi.close()




    @staticmethod
    def transfer_semua_saldo(rekening_asal, norek_penerima, koneksi):
        penerima = TransaksiService.cari_penerima(
            norek_penerima=norek_penerima,
            norek_pengirim=rekening_asal,
            koneksi=koneksi
        )

        nominal_transfer = rekening_asal.saldo
        saldo_baru_penerima = penerima.saldo + nominal_transfer

        jumlah_baris_asal = RekeningRepository.perbarui_saldo(
            norek=rekening_asal.norek,
            saldo_baru=0,
            koneksi=koneksi
        )

        jumlah_baris_penerima = RekeningRepository.perbarui_saldo(
            norek=penerima.norek,
            saldo_baru=saldo_baru_penerima,
            koneksi=koneksi
        )

        if jumlah_baris_asal != 1:
            raise ValueError("Gagal mengosongkan saldo rekening yang akan ditutup")

        if jumlah_baris_penerima != 1:
            raise ValueError("Gagal memindahkan saldo ke rekening penerima")

        return penerima, nominal_transfer, saldo_baru_penerima