import datetime
from bank_djago.core.deposito import Deposito
from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.sqlite.database import  buat_koneksi_tulis
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.riwayat.riwayat_template import RiwayatTemplate

from bank_djago.utils.validator import Validator
from bank_djago.utils.utility import Utilitas
from bank_djago.utils.utility import JenisTransaksi
from bank_djago.utils.utility import JenisReferensi
from bank_djago.utils.utility import JenisAro

from bank_djago.services.exceptions import (
    DepositoTidakDitemukan, JenisAroTidakValid, InputTidakValid, NikTidakSesuai,
    PenguranganSaldoGagal, RekeningTidakDitemukan, RekeningTidakSesuai, StatusTidakValid,
    PenambahanSaldoGagal,PerbaruiStatusGagal
)

from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.notifikasi_repository import NotifikasiRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository




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
    MIN_DEPO = 1_000_000


    @staticmethod
    def buka_deposito(
            nik ,
            norek,
            nominal,
            lama_bulan,
            jenis_aro=JenisAro.TIDAK,
            lama_aro=None,
            hari_ini=None
    ):


        if hari_ini is None:
            hari_ini = datetime.date.today()




        if nominal < DepositoService.MIN_DEPO:
            raise InputTidakValid(
                "Nominal deposito tidak memenuhi syarat"
            )


        if lama_bulan not in DepositoService.JANGKA_WAKTU:
            raise InputTidakValid(
                "Jangka waktu deposito tidak tersedia"
            )

        if jenis_aro == JenisAro.TIDAK:
            if lama_aro is not None:
                raise InputTidakValid(
                    "Deposito tanpa ARO tidak membutuhkan lama perpanjangan"
                )

        elif jenis_aro in (JenisAro.POKOK, JenisAro.POKOK_BUNGA):
            if lama_aro not in DepositoService.JANGKA_WAKTU:
                raise JenisAroTidakValid(
                    "Jangka waktu perpanjangan tidak tersedia"
                )

        else:
            raise JenisAroTidakValid(
                "Jenis ARO tidak tersedia"
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

            if nasabah.NIK != nik:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)


            saldo_minimal = rekening.saldosetor_min

            jumlah_baris = RekeningRepository.kurangi_saldo(
                norek=rekening.norek,
                nominal=nominal,
                saldo_minimal=saldo_minimal,
                koneksi=koneksi
            )
            if jumlah_baris != 1:
                raise PenguranganSaldoGagal(
                    "Terjadi kesalahan saat memotong saldo untuk deposito"
                )

            saldo_baru = RekeningRepository.ambil_saldo(
                norek=norek,
                koneksi=koneksi
            )

            bunga = DepositoService.JANGKA_WAKTU[lama_bulan]
            tanggal_buka = hari_ini
            jatuh_tempo = Utilitas.tambah_bulan(
                tanggal=tanggal_buka,
                bulan=lama_bulan
            )

            deposito_baru = Deposito(
                pemilik=nasabah,
                rekening=rekening,
                nominal=nominal,
                bunga=bunga,
                id=None,
                lama_bulan=lama_bulan,
                tanggal_buka=tanggal_buka,
                tanggal_jatuh_tempo=jatuh_tempo
            )
            deposito_baru.jenis_aro = jenis_aro
            deposito_baru.lama_aro = lama_aro

            id_deposito = DepositoRepository.tambah_deposito(
                deposito=deposito_baru,
                koneksi=koneksi
            )

            transaksi = {
                        "jenis":JenisTransaksi.PEMBUKAAN_DEPOSITO,
                         "norek_sumber":rekening.norek,
                         "nominal":nominal,
                         "saldo_sumber_sebelum":rekening.saldo,
                         "saldo_sumber_sesudah":saldo_baru,
                         "jenis_referensi":JenisReferensi.DEPOSITO,
                         "id_referensi":id_deposito,
                         "waktu":datetime.datetime.now()
                         }

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )

            audit = AuditService.tambah_audit(
                kategori="finansial",
                objek="deposito",
                aksi="pembukaan_deposito",
                log=(
                    f"{nasabah.nama} membuka deposito "
                    f"dengan ID {id_deposito}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )
            riwayat = RiwayatTemplate.template(
                kategori="deposito",
                jenis="pembukaan deposito",
                log=f"DEPOSITO | tenor {lama_bulan} bulan | Rp{Utilitas.format_rupiah(nominal)}")

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )



        return id_deposito

    @staticmethod
    def cairkan_deposito(
            nik,
            norek_pencairan,
            id_deposito,
            hari_ini=None
    ):

        if hari_ini is None:
            hari_ini = datetime.date.today()

        if not isinstance(id_deposito, int):
            raise InputTidakValid(
                "ID deposito harus berupa angka"
            )

        if id_deposito <= 0:
            raise InputTidakValid(
                "ID deposito tidak valid"
            )

        with buat_koneksi_tulis() as koneksi:

            data_deposito = DepositoRepository.cari_deposito_dengan_id(
                id_deposito=id_deposito,
                koneksi=koneksi
            )

            if data_deposito is None:
                raise DepositoTidakDitemukan(
                    "Deposito tidak ditemukan"
                )

            norek = data_deposito['norek']

            if norek != norek_pencairan:
                raise RekeningTidakSesuai(
                    f"Nomoe rekening ini tidak terdaftar sebagai pemilik deposito"
                )

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik deposito"
                )
            Validator.amankan_rekening(rekening=rekening)

            deposito = DepositoLoader.rangkai_deposito(
                data_deposito=data_deposito,
                nasabah=nasabah,
                rekening=rekening
            )

            if deposito.status != StatusDeposito.JATUH_TEMPO:
                raise StatusTidakValid(
                    f"Deposito tidak dapat dicairkan. "
                    f"Status saat ini: {deposito.status}"
                )

            if hari_ini < deposito.jatuh_tempo:
                raise StatusTidakValid(
                    "Deposito belum jatuh tempo"
                )

            status_lama = StatusDeposito.JATUH_TEMPO
            status_baru = StatusDeposito.DICAIRKAN

            jumlah_baris_deposito = DepositoRepository.perbarui_status_deposito(
                id_deposito=id_deposito,
                status_baru=status_baru,
                status_lama=status_lama,
                koneksi=koneksi
            )

            if jumlah_baris_deposito != 1:
                raise PerbaruiStatusGagal(
                    "Terjadi kesalahan saat memperbarui status deposito"
                )

            total_pencairan = deposito.total_pencairan

            jumlah_baris_saldo = RekeningRepository.tambah_saldo(
                norek=rekening.norek,
                nominal=total_pencairan,
                koneksi=koneksi
            )
            if jumlah_baris_saldo != 1:
                raise PenambahanSaldoGagal(
                    "Terjadi kesalahan saat memasukkan saldo ke rekening"
                )


            saldo_baru = RekeningRepository.ambil_saldo(
                norek=norek,
                koneksi=koneksi
            )

            transaksi = {
                        "jenis":JenisTransaksi.PENCAIRAN_DEPOSITO,
                         "norek_tujuan":rekening.norek,
                         "nominal":total_pencairan,
                         "saldo_tujuan_sebelum":rekening.saldo,
                         "saldo_tujuan_sesudah":saldo_baru,
                         "jenis_referensi":JenisReferensi.DEPOSITO,
                         "id_referensi":id_deposito,
                         "waktu":datetime.datetime.now()
                        }

            id_transaksi = TransaksiRepository.tambah_transaksi(
                transaksi=transaksi,
                koneksi=koneksi
            )

            riwayat = RiwayatTemplate.template(
                kategori="deposito",
                jenis="pencairan deposito",
                log=f"PENCAIRAN DEPOSITO +Rp{Utilitas.format_rupiah(total_pencairan)}"
            )

            audit = AuditService.tambah_audit(
                kategori="finansial",
                objek="deposito",
                aksi="pencairan_deposito",
                log=(
                    f"{nasabah.nama} mencairkan "
                    f"deposito dengan ID {id_deposito}"
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
                jenis_referensi=JenisReferensi.DEPOSITO,
                id_objek=id_deposito,
                koneksi=koneksi
            )


        return total_pencairan

    @staticmethod
    def perpanjangan(
            deposito,
            koneksi,
            hari_ini=None
    ):


            if hari_ini is None:
                hari_ini = datetime.date.today()


            data_deposito = DepositoRepository.cari_deposito_dengan_id(
                id_deposito=deposito.ID,
                koneksi=koneksi)

            if data_deposito is None:
                raise DepositoTidakDitemukan(
                    "Data deposito tidak ditemukan"
                )
            norek = data_deposito['norek']

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            if rekening.status == "tutup":
                raise StatusTidakValid(
                    "Deposito tidak dapat diperpanjang karena rekening sudah ditutup"
                )


            nasabah = rekening.pemilik

            deposito = DepositoLoader.rangkai_deposito(
                data_deposito=data_deposito,
                nasabah=nasabah,
                rekening=rekening
            )

            if deposito.status != StatusDeposito.AKTIF:
                raise StatusTidakValid(
                    "Deposito tidak dapat diperpanjang. "
                    f"Status saat ini: {deposito.status}"
                )

            if hari_ini < deposito.jatuh_tempo:
                raise StatusTidakValid(
                    "Deposito belum jatuh tempo"
                )
            # DESAIN BARU : buat deposito aro bisa mengejar ketertinggalan waktu karena scheduler lama tidak dijalankan
            if deposito.jenis_aro == JenisAro.TIDAK:
                return None

            if deposito.jenis_aro not in (
                    JenisAro.POKOK,
                    JenisAro.POKOK_BUNGA
            ):
                raise JenisAroTidakValid(
                    "Jenis ARO tidak valid"
                )

            if deposito.lama_aro not in (
                    DepositoService.JANGKA_WAKTU
            ):
                raise StatusTidakValid(
                    "Lama perpanjangan deposito tidak tersedia"
                )


            total = deposito.total_pencairan


            bunga_periode_ini = total - deposito.nominal

            saldo_sebelum = rekening.saldo

            if deposito.jenis_aro == JenisAro.POKOK:
                nominal_baru = deposito.nominal

            else:
                nominal_baru = total

            lama_bulan_baru = deposito.lama_aro

            bunga_baru = (
                DepositoService.JANGKA_WAKTU[
                    lama_bulan_baru
                ]
            )

            jatuh_tempo_lama = deposito.jatuh_tempo

            tanggal_buka_baru = deposito.jatuh_tempo

            jatuh_tempo_baru = Utilitas.tambah_bulan(
                tanggal_buka_baru,
                lama_bulan_baru
            )

            status_baru = StatusDeposito.AKTIF
            proses_aro = hari_ini

            jumlah_baris_deposito = (
                DepositoRepository.perbarui_setelah_aro(
                    id_deposito=deposito.ID,
                    nominal_baru=nominal_baru,
                    bunga_baru=bunga_baru,
                    lama_bulan_baru=lama_bulan_baru,
                    tanggal_buka_baru=tanggal_buka_baru,
                    jatuh_tempo_baru=jatuh_tempo_baru,
                    status_baru=status_baru,
                    proses_aro=proses_aro,
                    jatuh_tempo_lama=jatuh_tempo_lama,
                    koneksi=koneksi
                )
            )

            if jumlah_baris_deposito != 1:
                raise PerbaruiStatusGagal(
                    "Terjadi kesalahan saat memperbarui ARO"
                )



            if deposito.jenis_aro == JenisAro.POKOK:

                jumlah_baris_rekening = RekeningRepository.tambah_saldo(
                    norek=rekening.norek,
                    nominal=bunga_periode_ini,
                    koneksi=koneksi
                )

                if jumlah_baris_rekening != 1:
                    raise PenambahanSaldoGagal(
                        "Gagal menambahkan bunga ke rekening"
                    )
                saldo_baru = RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi)

                transaksi = {
                    "jenis": JenisTransaksi.BUNGA_DEPOSITO,
                    "norek_tujuan": deposito.rekening.norek,
                    "nominal": bunga_periode_ini,
                    "saldo_tujuan_sebelum": saldo_sebelum,
                    "saldo_tujuan_sesudah": saldo_baru,
                    "jenis_referensi": JenisReferensi.DEPOSITO,
                    "id_referensi": deposito.ID,
                    "waktu": datetime.datetime.now()
                }

                log_bunga = RiwayatTemplate.template(
                    kategori="deposito",
                    jenis="bunga deposito",
                    log=(
                        f"BUNGA DEPOSITO | "
                        f"Deposito {deposito.ID} | "
                        f"+Rp"
                        f"{Utilitas.format_rupiah(bunga_periode_ini)}"
                    )
                )

            else:

                transaksi = {
                    "jenis": (
                        JenisTransaksi
                        .KAPITALISASI_BUNGA_DEPOSITO
                    ),
                    "nominal": bunga_periode_ini,
                    "jenis_referensi": JenisReferensi.DEPOSITO,
                    "id_referensi": deposito.ID,
                    "waktu": datetime.datetime.now()
                }

                log_bunga = RiwayatTemplate.template(
                    kategori="deposito",
                    jenis="kapitalisasi bunga deposito",
                    log=(
                        f"KAPITALISASI BUNGA | "
                        f"Deposito {deposito.ID} | "
                        f"+Rp"
                        f"{Utilitas.format_rupiah(bunga_periode_ini)}"
                    )
                )


            id_transaksi = (
                TransaksiRepository.tambah_transaksi(
                    transaksi=transaksi,
                    koneksi=koneksi
                )
            )
            RiwayatRepository.tambah_riwayat(
                norek=deposito.rekening.norek,
                riwayat=log_bunga,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            riwayat_aro = RiwayatTemplate.template(
                kategori="deposito",
                jenis="perpanjang deposito",
                log=(
                    f"PERPANJANG DEPOSITO | "
                    f"ID {deposito.ID} | "
                    f"Rp"
                    f"{Utilitas.format_rupiah(nominal_baru)}"
                )
            )

            audit_aro = AuditService.tambah_audit(
                kategori="finansial",
                objek="deposito",
                aksi="perpanjangan_deposito_aro",
                log=(
                    f"Deposito dengan ID {deposito.ID} "
                    f"diperpanjang otomatis"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat_aro,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            AuditRepository.tambah_audit(
                audit=audit_aro,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )


            return True


    @staticmethod
    def hentikan_aro(
            nik,
            norek_pemberhentian,
            id_deposito
    ):

        if not isinstance(id_deposito, int):
            raise InputTidakValid(
                "ID deposito harus berupa angka"
            )

        if id_deposito <= 0:
            raise InputTidakValid(
                "ID deposito tidak valid"
            )


        with buat_koneksi_tulis() as koneksi:

            data_deposito = (
                DepositoRepository.cari_deposito_dengan_id(
                    id_deposito=id_deposito, koneksi=koneksi)
            )

            if data_deposito is None:
                raise DepositoTidakDitemukan(
                    "Deposito tidak ditemukan"
                )

            norek = data_deposito['norek']

            if norek != norek_pemberhentian:
                raise RekeningTidakSesuai(
                    "Rekening ini tidak terdaftar sebagai pemilik deposito"
                    )

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi
            )

            nasabah = rekening.pemilik


            if nik != nasabah.NIK:
                raise NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik deposito"
                )

            if rekening.status == "tutup":
                raise StatusTidakValid(
                    "ARO tidak dapat dihentikan karena rekening telah ditutup"
                )

            deposito = DepositoLoader.rangkai_deposito(
                data_deposito=data_deposito,
                nasabah=nasabah,
                rekening=rekening
            )

            if deposito.status != StatusDeposito.AKTIF:
                raise StatusTidakValid(
                    "ARO hanya dapat dihentikan pada deposito aktif"
                )

            if deposito.jenis_aro == JenisAro.TIDAK:
                raise JenisAroTidakValid(
                    "Deposito ini tidak menggunakan ARO"
                )

            if deposito.jenis_aro not in (
                    JenisAro.POKOK,
                    JenisAro.POKOK_BUNGA
            ):
                raise JenisAroTidakValid(
                    "Jenis ARO deposito tidak valid"
                )

            jumlah_baris = DepositoRepository.hentikan_aro(
                id_deposito=id_deposito,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui pengaturan ARO"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="deposito",
                aksi="penghentian_aro_deposito",
                log=(
                    f"{nasabah.nama} menghentikan perpanjangan otomatis "
                    f"deposito dengan ID {id_deposito}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )
            riwayat = RiwayatTemplate.template(
                kategori="deposito",
                jenis="penghentian aro deposito",
                log=(
                    f"HENTIKAN ARO DEPOSITO | "
                    f"ID {id_deposito} | "
                    f"Deposito tidak akan diperpanjang otomatis "
                    f"pada jatuh tempo berikutnya"
                )
            )
            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )
            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi
            )



        return id_deposito



    # method scheduler untuk mengubah status deposito menjadi jatuh tempo
    @staticmethod
    def tandai_jatuh_tempo(deposito ,koneksi,hari_ini=None):
            if hari_ini is None:
                hari_ini = datetime.date.today()




            data_deposito = DepositoRepository.cari_deposito_dengan_id(
                id_deposito=deposito.ID,
                koneksi=koneksi
            )

            if data_deposito is None:
                raise DepositoTidakDitemukan(
                    "Deposito tidak ditemukan"
                )

            if data_deposito['jenis_aro'] != JenisAro.TIDAK:
                raise JenisAroTidakValid(
                    "Deposito ARO harus diproses di perpanjangan"
                )
            if data_deposito['status'] != StatusDeposito.AKTIF:
                raise StatusTidakValid(
                    "Status deposito tidak dapat diubah. "
                    f"Status saat ini: {data_deposito['status']}"
                )

            tanggal_jatuh_tempo = datetime.date.fromisoformat(data_deposito['jatuh_tempo'])

            if tanggal_jatuh_tempo > hari_ini:
                raise StatusTidakValid(
                    "Deposito belum jatuh tempo"
                )

            status_lama = data_deposito['status']
            status_baru = StatusDeposito.JATUH_TEMPO

            jumlah_baris = DepositoRepository.perbarui_status_deposito(
                id_deposito=deposito.ID,
                status_baru=status_baru,
                status_lama=status_lama,
                koneksi=koneksi
            )


            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui status deposito"
                )


            return True

    # method pengonversi tipe data database ke tipe data program
    @staticmethod
    def _normalisasi_data_deposito(data_deposito):

        data = dict(data_deposito)

        data["tanggal_buka"] = datetime.date.fromisoformat(
            data["tanggal_buka"]
        )

        data["jatuh_tempo"] = datetime.date.fromisoformat(
            data["jatuh_tempo"]
        )

        if data["proses_aro"] is not None:
            data["proses_aro"] = datetime.date.fromisoformat(
                data["proses_aro"]
            )

        data["total_pencairan"] = (
            Deposito.hitung_total_pencairan(
                nominal=data["nominal"],
                bunga=data["bunga"],
                lama_bulan=data["lama_bulan"]
            )
        )

        return data

    # method untuk UI melihat semua deposito yang dimiliki nasabah
    @staticmethod
    def cari_deposito_nasabah(nik):
        daftar_deposito = (
            DepositoRepository.cari_deposito_dengan_nik(nik=nik)
        )

        return [
            DepositoService._normalisasi_data_deposito(
                data_deposito=data_deposito
            )
                for data_deposito in daftar_deposito]


    # method untuk filter deposito yang siap dicairkan di fitur pencairan deposito
    @staticmethod
    def cari_deposito_jatuh_tempo_dengan_norek(norek):

        daftar_deposito = (
            DepositoRepository.cari_deposito_jatuh_tempo_dengan_norek(norek=norek)
        )

        return [
            DepositoService._normalisasi_data_deposito(
                data_deposito=data_deposito
            ) for data_deposito in daftar_deposito
        ]


    # method untuk filter deposito ARO yang ingin dihentikan perpanjangan otomatisnya
    @staticmethod
    def cari_deposito_aro_aktif_dengan_norek(norek):

        daftar_deposito = (
            DepositoRepository.cari_deposito_aro_aktif_dengan_norek(norek=norek)
        )


        return [
            DepositoService._normalisasi_data_deposito(data_deposito=data_deposito)
            for data_deposito in daftar_deposito
        ]


    @staticmethod
    def buat_pesan_pengingat(deposito, hari_ini=None):

        if hari_ini is None:
            hari_ini = datetime.date.today()

        sisa_hari = (deposito.jatuh_tempo - hari_ini).days
        if deposito.jenis_aro == JenisAro.TIDAK:

            if sisa_hari > 3:
                return None

            if 0 < sisa_hari <= 3:
                tanggal_jatuh_tempo = (
                    Utilitas.format_tanggal_indonesia(
                        deposito.jatuh_tempo
                    )
                )

                return (
                    f"Deposito ber-ID {deposito.ID} akan jatuh tempo pada "
                    f"{tanggal_jatuh_tempo}"
                )

            if sisa_hari <= 0:
                return  (
                        f"Deposito ber-ID {deposito.ID} telah jatuh tempo. "
                        "Silakan lakukan pencairan deposito."
                        )

        else:
            if sisa_hari <= 0:
                return (
                            f"Deposito ARO ber-ID {deposito.ID} berhasil diperpanjang otomatis. "
                            f"Jatuh tempo berikutnya pada "
                            f"{Utilitas.format_tanggal_indonesia(deposito.jatuh_tempo)}."
                        )
            else:
                return None





