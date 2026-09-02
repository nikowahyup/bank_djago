import datetime
from bank_djago.core.deposito import Deposito
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas, JenisAro, JenisReferensiID
from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.notifikasi_repository import NotifikasiRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository


class StatusDeposito:
    AKTIF = "aktif"
    JATUH_TEMPO = "jatuh tempo"
    DICAIRKAN = "dicairkan"
    SELESAI = "selesai"




class DepositoService:

    JANGKA_WAKTU = {
        1: 0.03,
        3: 0.035,
        6: 0.04,
        12: 0.045
    }
    MIN_DEPO = 1000_000

    @staticmethod
    def buka_deposito(rekening,nominal,lama_bulan,jenis_aro=JenisAro.TIDAK,lama_aro=None):
        Validator.amankan_rekening(rekening)

        if nominal < DepositoService.MIN_DEPO:
            raise ValueError("Jumlah Deposito kurang dari minimum")

        if rekening.saldo - nominal < rekening.saldosetor_min:
            raise ValueError(
                "Saldo tidak mencukupi untuk membuka deposito")

        if lama_bulan not in DepositoService.JANGKA_WAKTU:
            raise ValueError("Jangka waktu deposito tidak tersedia")

        if jenis_aro == JenisAro.TIDAK:
            if lama_aro is not None:
                raise ValueError("Deposito tanpa ARO tidak membutuhkan lama perpanjangan")

        elif jenis_aro in (JenisAro.POKOK, JenisAro.POKOK_BUNGA):
            if lama_aro not in DepositoService.JANGKA_WAKTU:
                raise ValueError("Jangka waktu perpanjangan tidak tersedia")

        else:
            raise ValueError("Jenis ARO tidak tersedia")

        koneksi = buat_koneksi()

        try:

            bunga = DepositoService.JANGKA_WAKTU[lama_bulan]
            tanggal_buka = datetime.date.today()
            jatuh_tempo = Utilitas.tambah_bulan(tanggal_buka,lama_bulan)

            nasabah = rekening.pemilik

            saldo_baru = rekening.saldo - nominal

            jumlah_baris = RekeningRepository.perbarui_saldo(norek=rekening.norek, saldo_baru=saldo_baru, koneksi=koneksi)
            if jumlah_baris != 1:
                raise ValueError("Terjadi kesalahan saat memotong saldo untuk deposito")

            deposito_baru = Deposito(pemilik=nasabah,rekening=rekening,nominal=nominal,bunga=bunga,id=None,lama_bulan=lama_bulan,tanggal_buka=tanggal_buka,tanggal_jatuh_tempo=jatuh_tempo)
            deposito_baru.jenis_aro = jenis_aro
            deposito_baru.lama_aro = lama_aro
            id_deposito = DepositoRepository.tambah_deposito(deposito=deposito_baru, koneksi=koneksi)

            audit = AuditService.tambah_audit(kategori="transaksi",jenis="deposito",log=f"{nasabah.nama} membuka deposito",nama=nasabah.nama,nik=nasabah.NIK,norek=rekening.norek)
            riwayat = RiwayatTemplate.template(kategori="transaksi",jenis="deposito",log=f"DEPOSITO | tenor {lama_bulan} bulan | Rp{Utilitas.format_rupiah(nominal)}")
            AuditRepository.tambah_audit(audit=audit, koneksi=koneksi)
            RiwayatRepository.tambah_riwayat(norek=rekening.norek, riwayat=riwayat, koneksi=koneksi)

            koneksi.commit()
        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()
        nasabah.deposito.append(deposito_baru)
        deposito_baru.ID = id_deposito
        rekening.set_saldo(saldo_baru)
        rekening.simpan_riwayat(riwayat)
        return deposito_baru

    @staticmethod
    def cairkan_deposito(deposito,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        Validator.amankan_rekening(deposito.rekening)
        if deposito.status != StatusDeposito.JATUH_TEMPO:
            raise ValueError(
      f"Deposito belum dapat dicairkan. "
      f"Status saat ini: {deposito.status}"
     )

        if hari_ini < deposito.jatuh_tempo:
            raise ValueError("Deposito belum jatuh tempo")




        total_pencairan = deposito.total_pencairan
        saldo_baru = deposito.rekening.saldo + total_pencairan
        koneksi = buat_koneksi()

        try:

            jumlah_baris_deposito = DepositoRepository.perbarui_status_deposito(id_deposito=deposito.ID,status_baru=StatusDeposito.DICAIRKAN,koneksi=koneksi)
            if jumlah_baris_deposito != 1:
                raise ValueError("Terjadi kesalahan saat memperbarui status deposito")

            jumlah_baris_saldo = RekeningRepository.perbarui_saldo(norek=deposito.rekening.norek,saldo_baru=saldo_baru,koneksi=koneksi)
            if jumlah_baris_saldo != 1:
                raise ValueError("Terjadi kesalahan saat memasukkan saldo ke rekening")

            riwayat = RiwayatTemplate.template(kategori="transaksi",jenis="pencairan deposito",log=f"PENCAIRAN DEPOSITO +Rp{Utilitas.format_rupiah(total_pencairan)}")
            audit = AuditService.tambah_audit(kategori="transaksi",jenis="pencairan deposito",log=f"{deposito.pemilik.nama} mencairkan depositonya",nama=deposito.pemilik.nama,nik=deposito.pemilik.NIK,norek=deposito.rekening.norek)
            RiwayatRepository.tambah_riwayat(norek=deposito.rekening.norek,riwayat=riwayat,koneksi=koneksi)
            AuditRepository.tambah_audit(audit=audit,koneksi=koneksi)
            NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                nik_pemilik=deposito.pemilik.NIK,
                jenis_referensi=JenisReferensiID.DEPOSITO,
                id_objek=deposito.ID,
                koneksi=koneksi
            )


            koneksi.commit()
        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()
        deposito.rekening.set_saldo(saldo_baru)
        deposito.rekening.simpan_riwayat(riwayat)
        deposito.status = StatusDeposito.DICAIRKAN
        nasabah = deposito.pemilik
        nasabah.notifikasi = [
            notifikasi
            for notifikasi in deposito.pemilik.notifikasi
            if not (
                    notifikasi.jenis_referensi
                    == JenisReferensiID.DEPOSITO
                    and notifikasi.id_objek == deposito.ID
            )
        ]
        return total_pencairan



    @staticmethod
    def perpanjangan(deposito,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        Validator.amankan_rekening(deposito.rekening)

        if deposito.status != StatusDeposito.AKTIF:
            raise ValueError(f"Deposito tidak dapat diperpanjang. Status saat ini: {deposito.status}")

        if hari_ini < deposito.jatuh_tempo:
            raise ValueError("Deposito belum jatuh tempo")


        if deposito.jenis_aro == JenisAro.TIDAK:
            return None

        if deposito.jenis_aro not in (JenisAro.POKOK, JenisAro.POKOK_BUNGA):
            raise ValueError("Jenis ARO tidak valid")

        if deposito.lama_aro not in DepositoService.JANGKA_WAKTU:
            raise ValueError("Lama perpanjangan deposito tidak tersedia")

        total = deposito.total_pencairan



        if deposito.jenis_aro == JenisAro.POKOK:
            nominal_baru = deposito.nominal
            bunga_diterima = total - nominal_baru

        elif deposito.jenis_aro == JenisAro.POKOK_BUNGA:
            nominal_baru = total
            bunga_diterima = 0

        saldo_baru = deposito.rekening.saldo + bunga_diterima

        id_deposito = deposito.ID
        lama_bulan_baru = deposito.lama_aro
        bunga_baru = DepositoService.JANGKA_WAKTU[lama_bulan_baru]
        tanggal_buka_baru = deposito.jatuh_tempo
        jatuh_tempo_baru = Utilitas.tambah_bulan(tanggal_buka_baru, lama_bulan_baru)
        status_baru = StatusDeposito.AKTIF
        proses_aro = hari_ini

        koneksi = buat_koneksi()

        try:
            jumlah_baris_rekening = RekeningRepository.perbarui_saldo(norek=deposito.rekening.norek, saldo_baru=saldo_baru, koneksi=koneksi)
            if jumlah_baris_rekening != 1:
                raise ValueError("Terjadi kesalahan saat memperbarui saldo rekening")

            jumlah_baris_deposito = (DepositoRepository.perbarui_setelah_aro
                                     (
                                      id_deposito=id_deposito,
                                      nominal_baru=nominal_baru,
                                      bunga_baru=bunga_baru,
                                      lama_bulan_baru=lama_bulan_baru,
                                      tanggal_buka_baru=tanggal_buka_baru,
                                      jatuh_tempo_baru=jatuh_tempo_baru,
                                      status_baru=status_baru,
                                      proses_aro=proses_aro,
                                      koneksi=koneksi))

            if jumlah_baris_deposito != 1:
                raise ValueError("Terjadi kesalahan saat memperbarui ARO")


            if bunga_diterima > 0:
                log_bunga = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="bunga deposito",
                log=(
                    f"BUNGA DEPOSITO | "
                    f"Deposito {deposito.ID} | "
                    f" +Rp{Utilitas.format_rupiah(bunga_diterima)}"
                )
            )
                RiwayatRepository.tambah_riwayat(norek=deposito.rekening.norek, riwayat=log_bunga, koneksi=koneksi)

            riwayat_aro = RiwayatTemplate.template(kategori="transaksi",jenis="perpanjang deposito",log=f"PERPANJANG DEPOSITO | ID {deposito.ID} | Rp{Utilitas.format_rupiah(nominal_baru)}")
            audit_aro = AuditService.tambah_audit(kategori="transaksi",jenis="perpanjang deposito",log=f"Deposito dengan ID {deposito.ID} diperpanjang otomatis",nama=deposito.pemilik.nama,nik=deposito.pemilik.NIK,norek=deposito.rekening.norek)
            AuditRepository.tambah_audit(audit=audit_aro, koneksi=koneksi)
            RiwayatRepository.tambah_riwayat(norek=deposito.rekening.norek, riwayat=riwayat_aro,koneksi=koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        deposito.rekening.set_saldo(saldo_baru)
        deposito.nominal = nominal_baru
        deposito.bunga = bunga_baru
        deposito.lama_bulan = lama_bulan_baru
        deposito.tanggal_buka = tanggal_buka_baru
        deposito.jatuh_tempo = jatuh_tempo_baru
        deposito.status = status_baru
        deposito.proses_aro = proses_aro
        if bunga_diterima > 0:
            deposito.rekening.simpan_riwayat(log_bunga)
        deposito.rekening.simpan_riwayat(riwayat_aro)
        return True


    @staticmethod
    def depo_jatuh_tempo(nasabah):
        return [deposito for deposito in nasabah.deposito
                if deposito.status == StatusDeposito.JATUH_TEMPO]



    @staticmethod
    def tandai_jatuh_tempo(deposito,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        if deposito.status != StatusDeposito.AKTIF:
            raise ValueError(
                f"Deposito belum dapat ditandai jatuh tempo.Status saat ini: {deposito.status}")

        if hari_ini < deposito.jatuh_tempo:
            raise ValueError("Deposito belum jatuh tempo")

        if deposito.jenis_aro != JenisAro.TIDAK:
            raise ValueError("Deposito ARO harus diproses melalui perpanjangan")


        koneksi = buat_koneksi()

        try:
            jumlah_baris_deposito = DepositoRepository.perbarui_status_deposito(id_deposito=deposito.ID,status_baru=StatusDeposito.JATUH_TEMPO,koneksi=koneksi)

            if jumlah_baris_deposito != 1:
                raise ValueError("Gagal memperbarui status deposito")

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise
        finally:
            koneksi.close()

        deposito.status = StatusDeposito.JATUH_TEMPO
        return True