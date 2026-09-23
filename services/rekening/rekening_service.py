import datetime
import random

from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.services.exceptions import NasabahTidakDitemukan, InputTidakValid, RekeningTidakDitemukan, \
    NikTidakSesuai, StatusTidakValid, LevelRekeningTidakValid, PerbaruiStatusGagal, PenambahanSaldoGagal
from bank_djago.services.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.core.rekening import RekeningReguler, RekeningPrioritas, RekeningGold, RekeningPlatinum
from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi, buat_koneksi_tulis
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.utils.utility import JenisTransaksi, Utilitas
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_baca



class RekeningService:
    level = {1: 'Reguler',
             2: 'Prioritas',
             3: 'Gold',
             4: 'Platinum'}
    jenis_rekening = {
        1: {
            "prefix": "4001",
            "kelas": RekeningReguler,
            "nama": "Reguler",
            "minimal_upgrade": 0
        },
        2: {
            "prefix": "3001",
            "kelas": RekeningPrioritas,
            "nama": "Prioritas",
            "minimal_upgrade": 3_000_000
        },
        3: {
            "prefix": "2001",
            "kelas": RekeningGold,
            "nama": "Gold",
            "minimal_upgrade": 50_000_000
        },
        4: {
            "prefix": "1001",
            "kelas": RekeningPlatinum,
            "nama": "Platinum",
            "minimal_upgrade": 200_000_000
        }
    }


    @staticmethod
    def upgrade_rekening(
            nik,
            norek,
            target_level
    ):

        if not isinstance(target_level, int):
            raise InputTidakValid(
                "Level rekening harus berupa angka"
            )



        if target_level not in RekeningService.jenis_rekening:
            raise InputTidakValid(
                "Level rekening tidak tersedia"
            )


        with buat_koneksi_tulis() as koneksi:

            rekening = RekeningLoader.muat_rekening(
                norek=norek,
                koneksi=koneksi)

            if rekening is None:
                raise RekeningTidakDitemukan(
                    "Rekening tidak ditemukan"
                )

            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise  NikTidakSesuai(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )
            if not rekening.boleh_ubah_level:
                raise StatusTidakValid(
                    "Perubahan rekening hanya bisa dilakukan 1 kali sehari"
                )
            if target_level <= rekening.level:
                raise LevelRekeningTidakValid(
                    "Level upgrade rekening harus lebih tinggi dari level saat ini"
                )

            info = RekeningService.jenis_rekening[target_level]

            Validator.amankan_rekening(rekening=rekening)

            if rekening.saldo < info["minimal_upgrade"]:
                raise StatusTidakValid(
                    "Saldo kini tidak memenuhi saldo minimum rekening tujuan"
                )

            kelas_rekening = RekeningService.jenis_rekening[target_level]['kelas']

            konfigurasi_target = kelas_rekening(
                norek=rekening.norek,
                pin=rekening.pin,
                pemilik=nasabah
            )

            rek_awal = rekening.jenis
            rek_tujuan = konfigurasi_target.jenis

            terakhir_ubah_rekening_lama = rekening.terakhir_ubah_rekening
            terakhir_ubah_rekening_baru = datetime.date.today()
            limit_sisa_baru = konfigurasi_target.limit_harian

            jumlah_baris = (
                RekeningRepository.ubah_state_setelah_upgrade_atau_downgrade(
                    norek=rekening.norek,
                    limit_sisa_baru=limit_sisa_baru,
                    level_baru=target_level,
                    terakhir_ubah_rekening_lama=terakhir_ubah_rekening_lama,
                    terakhir_ubah_rekening_baru=terakhir_ubah_rekening_baru,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal melakukan peningkatan rekening"
                )


            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="peningkatan rekening",
                log=f"PENINGKATAN REKENING | Rekening awal {rek_awal} ke Rekening {rek_tujuan}")

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="peningkatan_level_rekening",
                log=(
                    f"{nasabah.nama} meningkatkan rekening "
                    f"dari {rek_awal} ke {rek_tujuan}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=konfigurasi_target.norek
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )





    @staticmethod
    def downgrade_rekening(
            nik,
            norek,
            target_level
    ):

        if not isinstance(target_level, int):
            raise InputTidakValid(
                "Level rekening harus berupa angka"
            )

        if target_level not in RekeningService.jenis_rekening:
            raise InputTidakValid(
                "Level rekening tidak tersedia"
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
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            if not rekening.boleh_ubah_level:
                raise StatusTidakValid(
                    "Perubahan rekening hanya bisa dilakukan 1 kali sehari"
                )

            if target_level >= rekening.level:
                raise LevelRekeningTidakValid(
                    "Pilihan level rekening harus lebih rendah dari level saat ini"
                )

            Validator.amankan_rekening(rekening=rekening)


            kelas_rekening = RekeningService.jenis_rekening[target_level]['kelas']

            konfigurasi_target = kelas_rekening(
                norek=rekening.norek,
                pin=rekening.pin,
                pemilik=nasabah

            )

            limit_sisa_baru = konfigurasi_target.limit_harian
            terakhir_ubah_rekening_lama = rekening.terakhir_ubah_rekening
            terakhir_ubah_rekening_baru = datetime.date.today()


            jumlah_baris = (
                RekeningRepository.ubah_state_setelah_upgrade_atau_downgrade(
                    norek=rekening.norek,
                    limit_sisa_baru=limit_sisa_baru,
                    level_baru=target_level,
                    terakhir_ubah_rekening_lama=terakhir_ubah_rekening_lama,
                    terakhir_ubah_rekening_baru=terakhir_ubah_rekening_baru,
                    koneksi=koneksi
                )
            )
            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal melakukan penurunan rekening"
                )
            rek_awal = rekening.jenis
            rek_tujuan = konfigurasi_target.jenis


            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="penurunan rekening",
                log=f" PENURUNAN REKENING | Rekening Awal {rek_awal} ke Rekening {rek_tujuan}")

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek = "rekening",
                aksi = "penurunan_level_rekening",
                log=(
                    f"{nasabah.nama} menurunkan rekening "
                    f"dari {rek_awal} ke {rek_tujuan}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )



    @staticmethod
    def blokir_rekening(
            nik,
            norek,
            alasan
    ):


        alasan_blokir = alasan.strip()

        if not alasan_blokir:
            raise InputTidakValid(
                "Alasan blokir tidak boleh kosong"
            )


        with buat_koneksi_tulis() as koneksi:

            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

            if rekening is None:
                raise RekeningTidakDitemukan(
                    "Rekening tidak terdaftar"
                )
            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NasabahTidakDitemukan(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)

            status_lama = rekening.status
            status_baru = "blokir"

            jumlah_baris = (
                RekeningRepository.perbarui_status_blokir(
                    norek=rekening.norek,
                    status_lama=status_lama,
                    status_baru=status_baru,
                    alasan_blokir=alasan_blokir,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memblokir rekening"
                )

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="pemblokiran rekening",
                log=(
                    "PEMBLOKIRAN REKENING | "
                    f"Rekening diblokir. "
                    f"Alasan: {alasan_blokir}"
                )
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="pemblokiran_rekening",
                log=(
                    f"{rekening.pemilik.nama} "
                    f"memblokir rekening. "
                    f"Alasan: {alasan_blokir}"
                ),
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
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






    @staticmethod
    def buka_blokir(
            nik,
            norek,
            pin
    ):




        with buat_koneksi_tulis() as koneksi:

            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

            if rekening is None:
                raise RekeningTidakDitemukan(
                    "Rekening tidak terdaftar"
                )
            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NasabahTidakDitemukan(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )
            if not rekening.cek_pin(pin):
                raise InputTidakValid(
                    "PIN rekening salah"
                )
            if rekening.status == "tutup":
                raise StatusTidakValid(
                    "Rekening ini telah ditutup!"
                )

            if rekening.status == "aktif":
                raise StatusTidakValid(
                    "Rekening sudah dalam status aktif"
                )

            if rekening.status != "blokir":
                raise StatusTidakValid(
                    "Rekening tidak sedang dalam status blokir"
                )

            status_lama = rekening.status
            status_baru = "aktif"

            jumlah_baris = RekeningRepository.perbarui_status_blokir(
                norek=rekening.norek,
                status_lama=status_lama,
                status_baru=status_baru,
                alasan_blokir=None,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal membuka blokir rekening"
                )

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="pembukaan blokir rekening",
                log=(
                    "PEMBUKAAN BLOKIR REKENING | "
                    "Rekening kembali diaktifkan"
                )
            )
            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="pembukaan_blokir_rekening",
                log=(
                    f"{rekening.pemilik.nama} membuka kembali blokir rekening"
                ),
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
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









    @staticmethod
    def buka_rekening(
            nik,
            pilihan,
            pin,
            setor_awal,
            koneksi=None
    ):

        buat_baru_diluar_daftar = koneksi is None

        if buat_baru_diluar_daftar:
            koneksi = buat_koneksi()

        try:
            data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(nik=nik, koneksi=koneksi)


            if data_nasabah is None:
                raise NasabahTidakDitemukan(
                    "NIK tidak terdaftar"
                )

            if pilihan not in RekeningService.jenis_rekening:
                raise LevelRekeningTidakValid(
                    "Pilihan jenis rekening tidak tersadia"
                )

            nasabah = NasabahLoader.rangkai_nasabah(data_nasabah=data_nasabah)

            info = RekeningService.jenis_rekening[pilihan]
            kelas_rek = info["kelas"]
            norek = RekeningService.buat_norek(pilihan, koneksi)

            waktu_dibuat = datetime.datetime.now()
            rekening_baru = kelas_rek(
                norek=norek,
                pin=pin,
                pemilik=nasabah,
                waktu_dibuat=waktu_dibuat
            )


            if setor_awal < rekening_baru.saldosetor_min:
                raise  InputTidakValid(
                    "Setor awal tidak memenuhi saldo minimal setoran awal"
                )


            RekeningRepository.tambah_rekening(
                rekening=rekening_baru,
                koneksi=koneksi
            )



            jumlah_baris = (
                RekeningRepository.tambah_saldo(
                    norek=rekening_baru.norek,
                    nominal=setor_awal,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise PenambahanSaldoGagal(
                    "Gagal memasukkan setoran awal ke rekening"
                )

            transaksi = {
                "jenis": JenisTransaksi.SETOR_AWAL,
                "norek_tujuan": rekening_baru.norek,
                "nominal": setor_awal,
                "saldo_tujuan_sebelum": 0,
                "saldo_tujuan_sesudah": setor_awal,
                "waktu": rekening_baru.waktu_dibuat
            }
            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi=transaksi, koneksi=koneksi)

            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="setor awal",
                log=f"SETOR AWAL | +Rp{Utilitas.format_rupiah(setor_awal)}")

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek = "rekening",
                aksi = "pembukaan_rekening",
                log=f"{nasabah.nama} membuka rekening baru",
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening_baru.norek
            )
            riwayat_buka = RiwayatTemplate.template(
                kategori="rekening",
                jenis='pembukaan rekening',
                log=f"BUKA REKENING | {norek}"
            )
            RiwayatRepository.tambah_riwayat(
                norek=rekening_baru.norek,
                riwayat=riwayat_buka,
                koneksi=koneksi
            )
            RiwayatRepository.tambah_riwayat(
                norek=rekening_baru.norek,
                riwayat=riwayat,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi,
                id_transaksi=id_transaksi
            )

            if buat_baru_diluar_daftar:
                koneksi.commit()


            return rekening_baru

        except Exception:
            if buat_baru_diluar_daftar:
                koneksi.rollback()

            raise

        finally:
            if buat_baru_diluar_daftar:
                koneksi.close()


    @staticmethod
    def ganti_pin(
            nik,
            norek,
            pin_lama,
            pin_baru
    ):



        with buat_koneksi_tulis() as koneksi:
            rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

            if rekening is None:
                raise RekeningTidakDitemukan(
                    "Rekening tidak terdaftar"
                )
            nasabah = rekening.pemilik

            if nasabah.NIK != nik:
                raise NasabahTidakDitemukan(
                    "NIK ini tidak terdaftar sebagai pemilik rekening"
                )

            Validator.amankan_rekening(rekening=rekening)

            if not rekening.cek_pin(pin_lama):
                raise InputTidakValid(
                    "PIN lama salah"
                )

            Validator.validasi_pin(pin_baru)

            if rekening.cek_pin(pin_baru):
                raise InputTidakValid(
                    "PIN baru tidak boleh sama dengan PIN lama"
                )


            jumlah_baris = RekeningRepository.perbarui_pin(
                norek=rekening.norek,
                pin_lama=pin_lama,
                pin_baru=pin_baru,
                koneksi=koneksi)


            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal mengganti PIN rekening"
                )

            riwayat = RiwayatTemplate.template(
                kategori="sistem",
                jenis="penggantian_pin_rekening",
                log=(
                    "GANTI PIN REKENING | "
                    "PIN rekening berhasil diperbarui"
                )
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="penggantian_pin_rekening",
                log=(
                    f"{rekening.pemilik.nama} melakukan pergantian PIN rekening"
                ),
                nama=rekening.pemilik.nama,
                nik=rekening.pemilik.NIK,
                norek=rekening.norek
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


    # method untuk membuat nomor rekening sesuai prefix yang tersedia
    @staticmethod
    def buat_norek(level, koneksi):
        if level not in RekeningService.jenis_rekening:
            raise InputTidakValid("Pilihan level rekening tidak tersedia")

        prefix = RekeningService.jenis_rekening[level]["prefix"]

        while True:
            digit_sisa = random.randint(100_000_000_000,999_999_999_999)
            norek = prefix + str(digit_sisa)

            rekening_terdaftar = RekeningRepository.cari_rekening_dengan_norek(norek, koneksi)

            if rekening_terdaftar is None:
                return norek


    # method pencari semua rekening milik nasabah
    @staticmethod
    def cari_semua_rekening(nik):

        with buat_koneksi_baca() as koneksi:
            return RekeningRepository.cari_rekening_dengan_nik(nik=nik, koneksi=koneksi)

    # method filter status rekening selain tutup untuk pilihan login
    @staticmethod
    def cari_norek_tersedia(nik):

            daftar_rekening = RekeningService.cari_semua_rekening(nik=nik)

            daftar_norek_aktif = []
            for data_rekening in daftar_rekening:
                if data_rekening['status'] != "tutup":
                    daftar_norek_aktif.append(data_rekening['norek'])


            return daftar_norek_aktif


    # method untuk menampilkan semua rekening nasabah untuk menu riwayat
    @staticmethod
    def cari_semua_rekening_untuk_riwayat(nik):

        daftar_rekening_nasabah = RekeningService.cari_semua_rekening(nik=nik)

        return {
            data['norek'] : data['status']
            for data in daftar_rekening_nasabah
        }

    # method untuk menampilkan rekening untuk diupgrade/downgrade serta penutupan
    @staticmethod
    def cari_rekening_untuk_diubah_atau_untuk_pangajuan(norek):
     with buat_koneksi_baca() as koneksi:

        return RekeningRepository.cari_rekening_dengan_norek(
            norek=norek,
            koneksi=koneksi
        )