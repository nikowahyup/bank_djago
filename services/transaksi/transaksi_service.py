from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import PengajuanRepository
from bank_djago.utils.utility import Utilitas
from bank_djago.services.transaksi.limit_service import LimitService
from bank_djago.services.admin.audit_service import  AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class TransaksiService:

    @staticmethod
    def setor_tunai(rekening ,nominal):
        Validator.amankan_rekening(rekening)
        if nominal < 10000:
            raise ValueError("Minimal setor adalah Rp10.000")

        saldo_baru = rekening.saldo + nominal
        koneksi = buat_koneksi()

        try:
            jumlah_baris =  RekeningRepository.perbarui_saldo(rekening.norek, saldo_baru, koneksi)
            if jumlah_baris != 1 :
                raise ValueError("Rekening tidak terdaftar")

            riwayat = RiwayatTemplate.setor_uang(nominal)
            RiwayatRepository.tambah_riwayat(norek=rekening.norek, riwayat=riwayat, koneksi=koneksi)
            audit = AuditService.tambah_audit(kategori="transaksi",jenis="setor uang",log=f"Setor uang Rp{Utilitas.format_rupiah(nominal)}",nama=rekening.pemilik.nama,nik=rekening.pemilik.NIK,norek=rekening.norek)
            AuditRepository.tambah_audit(audit, koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        rekening.set_saldo(saldo_baru)
        rekening.simpan_riwayat(riwayat)
        return True





    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def tarik_tunai(rekening,nominal):
        Validator.amankan_rekening(rekening)
        if nominal < 10000:
            raise ValueError("Minimal tarik adalah Rp10.000")
        if rekening.saldo - nominal < rekening.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika Anda menarik sebesar Rp{Utilitas.format_rupiah(nominal)}")

        saldo_baru = rekening.saldo - nominal
        koneksi = buat_koneksi()

        try:
            jumlah_baris = RekeningRepository.perbarui_saldo(rekening.norek, saldo_baru, koneksi)
            if jumlah_baris != 1:
                raise ValueError("Rekening tidak terdaftar")
            riwayat = RiwayatTemplate.tarik_uang(nominal)
            RiwayatRepository.tambah_riwayat(rekening.norek, riwayat, koneksi)
            audit = AuditService.tambah_audit(kategori="transaksi",jenis="tarik uang",log=f"Tarik uang Rp{Utilitas.format_rupiah(nominal)}",nama=rekening.pemilik.nama,nik=rekening.pemilik.NIK,norek=rekening.norek)
            AuditRepository.tambah_audit(audit, koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        rekening.set_saldo(saldo_baru)
        rekening.simpan_riwayat(riwayat)
        return True
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def transfer(pengirim,norek_penerima,nominal):

        Validator.amankan_rekening(pengirim)
        if nominal < 10000:
            raise ValueError("Minimal transfer adalah Rp10.000")

        total = nominal + pengirim.pajak

        if pengirim.saldo - total < pengirim.saldosetor_min:
            raise ValueError(f"Saldo sekarang tidak memenuhi saldo minimal jika melakukan transfer Rp{Utilitas.format_rupiah(nominal)}")

        koneksi = buat_koneksi()


        try:

            penerima = TransaksiService.cari_penerima(norek_penerima, pengirim, koneksi)

            limit_sekarang,reset_baru,reset_terjadi = LimitService.hitung_limit_saat_ini(pengirim)

            if limit_sekarang is None:
                limit_baru = None
            else:
                limit_baru = limit_sekarang - total
                if limit_baru < 0:
                    raise ValueError("Limit harian telah habis")

            saldo_khusus_pengirim = pengirim.saldo - total
            saldo_khusus_penerima = penerima.saldo + nominal

            if reset_terjadi:
                riwayat_reset = RiwayatTemplate.template("sistem","reset limit","reset limit transfer harian")
                RiwayatRepository.tambah_riwayat(norek=pengirim.norek,riwayat=riwayat_reset,koneksi=koneksi)



            jumlah_baris_pengirim = RekeningRepository.perbarui_saldo(pengirim.norek,saldo_khusus_pengirim,koneksi)
            jumlah_baris_penerima = RekeningRepository.perbarui_saldo(penerima.norek,saldo_khusus_penerima,koneksi)
            jumlah_baris_limit =RekeningRepository.perbarui_limit(limit_baru,reset_baru,pengirim.norek,koneksi)


            if jumlah_baris_pengirim != 1:
                raise ValueError("Tidak dapat melakukan transfer")

            if jumlah_baris_limit != 1:
                raise ValueError("Terjadi kesalahan saat memperbarui limit")


            if jumlah_baris_penerima != 1:
                raise ValueError("Tidak dapat melakukan transfer")




            riwayat_pengirim = RiwayatTemplate.transfer_kirim(nominal,penerima)
            riwayat_penerima = RiwayatTemplate.transfer_terima(nominal,pengirim)
            audit_penerima = AuditService.tambah_audit(kategori="transaksi",jenis="terima saldo",log=f"Terima saldo Rp{Utilitas.format_rupiah(nominal)}",nama=penerima.pemilik.nama,nik=penerima.pemilik.NIK,norek=norek_penerima)
            audit_pengirim  = AuditService.tambah_audit(kategori="transaksi",jenis="transfer",log=f"Transfer Rp{Utilitas.format_rupiah(nominal)}",nama=pengirim.pemilik.nama,nik=pengirim.pemilik.NIK,norek=pengirim.norek)


            RiwayatRepository.tambah_riwayat(pengirim.norek,riwayat_pengirim,koneksi)
            RiwayatRepository.tambah_riwayat(penerima.norek,riwayat_penerima,koneksi)
            AuditRepository.tambah_audit(audit_pengirim,koneksi)
            AuditRepository.tambah_audit(audit_penerima,koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        pengirim.set_saldo(saldo_khusus_pengirim)
        penerima.set_saldo(saldo_khusus_penerima)
        pengirim.simpan_riwayat(riwayat_pengirim)
        penerima.simpan_riwayat(riwayat_penerima)
        pengirim.limit_sisa = limit_baru
        if reset_terjadi:
            pengirim.reset = reset_baru
            pengirim.simpan_riwayat(riwayat_reset)

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
    def cari_penerima(norek_penerima,pengirim, koneksi=None):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:

            penerima = RekeningLoader.muat_rekening(norek_penerima,koneksi)

            if penerima is None:
                raise ValueError("Rekening penerima tidak terdaftar")

            if  penerima.norek == pengirim.norek:
                    raise ValueError("Tidak dapat transfer ke nomor rekening sendiri")

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
            pengirim=rekening_asal,
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