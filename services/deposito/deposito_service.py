import datetime
from bank_djago.core.deposito import Deposito
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas, JenisAro, JenisReferensiID
from bank_djago.utils.validator import Validator
from bank_djago.core.notifikasi import Notifikasi
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
            raise ValueError("Jumlah Depo kurang dari minimum")

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
            jumlah_baris_saldo = RekeningRepository.perbarui_saldo(norek=deposito.rekening.norek,saldo_baru=saldo_baru,koneksi=koneksi)
            if jumlah_baris_saldo != 1:
                raise ValueError("Terjadi kesalahan saat memasukkan saldo ke rekening")

            jumlah_baris_deposito = DepositoRepository.perbarui_status_deposito(id_deposito=deposito.ID,status_baru=StatusDeposito.DICAIRKAN,koneksi=koneksi)
            if jumlah_baris_deposito != 1:
                raise ValueError("Terjadi kesalahan saat memperbarui status deposito")

            riwayat = RiwayatTemplate.template(kategori="transaksi",jenis="pencairan deposito",log=f"PENCAIRAN DEPOSITO +Rp{Utilitas.format_rupiah(total_pencairan)}")
            audit = AuditService.tambah_audit(kategori="transaksi",jenis="pencairan deposito",log=f"{deposito.pemilik.nama} mencairkan depositonya",nama=deposito.pemilik.nama,nik=deposito.pemilik.NIK,norek=deposito.rekening.norek)
            RiwayatRepository.tambah_riwayat(norek=deposito.rekening.norek,riwayat=riwayat,koneksi=koneksi)
            AuditRepository.tambah_audit(audit=audit,koneksi=koneksi)


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
        DepositoService.hapus_notifikasi_deposito(nasabah, deposito)

        deposito.notifikasi_depo = False
        return total_pencairan











    @staticmethod
    def perpanjangan(bank,deposito,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        if deposito.status != StatusDeposito.AKTIF:
            raise ValueError("Deposito sudah tidak aktif")

        if hari_ini < deposito.jatuh_tempo:
            raise ValueError("Deposito belum jatuh tempo")


        if deposito.jenis_aro == JenisAro.TIDAK:
            return None


        total = deposito.total_pencairan

        if deposito.jenis_aro == JenisAro.POKOK:
            nominal_baru = deposito.nominal

        elif deposito.jenis_aro == JenisAro.POKOK_BUNGA:
            nominal_baru = total

        else:
            raise ValueError("ARO tidak valid")


        lama_bulan = deposito.lama_aro
        if lama_bulan not in DepositoService.JANGKA_WAKTU:
            raise ValueError("Lama bulan tidak terdaftar")

        deposito.rekening.tambah_saldo(total)
        deposito.rekening.kurangi_saldo(nominal_baru)

        if deposito.jenis_aro == JenisAro.POKOK:
            nominal_baru = deposito.nominal
            bunga_diterima = total - nominal_baru

        elif deposito.jenis_aro == JenisAro.POKOK_BUNGA:
            nominal_baru = total
            bunga_diterima = 0

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

            deposito.rekening.simpan_riwayat(log_bunga)


        tanggal_buka = deposito.jatuh_tempo # kunci
        jatuh_tempo_baru = Utilitas.tambah_bulan(tanggal_buka,lama_bulan)
        deposito.nominal = nominal_baru
        deposito.bunga = DepositoService.JANGKA_WAKTU[lama_bulan]
        deposito.lama_bulan = lama_bulan
        deposito.tanggal_buka = tanggal_buka
        deposito.jatuh_tempo = jatuh_tempo_baru
        deposito.status = StatusDeposito.AKTIF

        log = RiwayatTemplate.template(
            kategori="transaksi",
            jenis="deposito",
            log=f"PENCAIRAN DAN PERPANJANGAN DEPOSITO | Rp{Utilitas.format_rupiah(nominal_baru)}"

        )

        deposito.rekening.simpan_riwayat(log)

        AuditService.tambah_audit(
            bank,
            kategori="transaksi",
            jenis="deposito",
            log=f"{deposito.pemilik.nama} memperpanjang deposito "
                f"Rp{Utilitas.format_rupiah(nominal_baru)}",
            nik=deposito.pemilik.NIK,
            norek=deposito.rekening.norek
        )

        nasabah = deposito.pemilik
        notifikasi = Notifikasi(jenis="deposito",
                                pesan=f"Deposito Anda diperpanjang otomatis.\n"
                                      f"Jatuh tempo berikutnya : {Utilitas.format_tanggal_indonesia(deposito.jatuh_tempo)}",
                                referensi_id=JenisReferensiID.DEPOSITO)
        notifikasi.id_objek = deposito.ID
        nasabah.notifikasi.append(notifikasi)
        deposito.notifikasi_depo = True

    @staticmethod
    def hapus_notifikasi_deposito(nasabah,deposito):
        for item in nasabah.notifikasi:
            if item.referensi_id == JenisReferensiID.DEPOSITO and item.id_objek == deposito.ID:
                nasabah.notifikasi.remove(item)
                break


    @staticmethod
    def depo_jatuh_tempo(nasabah):
        return [deposito for deposito in nasabah.deposito
                if deposito.status == StatusDeposito.JATUH_TEMPO]