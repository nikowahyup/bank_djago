import datetime
import random


from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.services.exceptions import (
    NasabahTidakDitemukan,
    InputTidakValid,
    RekeningTidakDitemukan,
    NikTidakSesuai,
    StatusTidakValid,
    LevelRekeningTidakValid,
    PerbaruiStatusGagal,
    PenambahanSaldoGagal,
    RekeningTerkunci,
    PinTidakCocok,
)
from bank_djago.services.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.core.rekening import (
    Rekening,
    RekeningReguler,
    RekeningPrioritas,
    RekeningGold,
    RekeningPlatinum,
)
from bank_djago.penyimpanan.pencatatan_helper import HelperPencatatan

from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
import bank_djago.penyimpanan.sqlite.database as db_module
from bank_djago.utils.utility import JenisTransaksi, Utilitas
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_baca, buat_koneksi_tulis

reguler = RekeningReguler(norek="1234", pin="1234", pemilik=None)
prioritas = RekeningPrioritas(norek="1234", pin="1234", pemilik=None)
gold = RekeningGold(norek="1234", pin="1234", pemilik=None)
platinum = RekeningPlatinum(norek="1234", pin="1234", pemilik=None)


class RekeningService:

    PESAN_REKENING_TERKUNCI = "Rekening terkunci sementara karena terlalu banyak percobaan PIN salah. Coba beberapa saat lagi"

    level = {1: "Reguler", 2: "Prioritas", 3: "Gold", 4: "Platinum"}
    jenis_rekening = {
        1: {
            "prefix": "4001",
            "kelas": RekeningReguler,
            "nama": "Reguler",
            "minimal_upgrade": 0,
            "minimal_setor": reguler.saldosetor_min,
        },
        2: {
            "prefix": "3001",
            "kelas": RekeningPrioritas,
            "nama": "Prioritas",
            "minimal_upgrade": 3_000_000,
            "minimal_setor": prioritas.saldosetor_min,
        },
        3: {
            "prefix": "2001",
            "kelas": RekeningGold,
            "nama": "Gold",
            "minimal_upgrade": 50_000_000,
            "minimal_setor": gold.saldosetor_min,
        },
        4: {
            "prefix": "1001",
            "kelas": RekeningPlatinum,
            "nama": "Platinum",
            "minimal_upgrade": 200_000_000,
            "minimal_setor": platinum.saldosetor_min,
        },
    }

    @staticmethod
    def muat_rekening_dan_validasi_pemilik(nik: str, norek: str, koneksi):

        rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi)

        if rekening is None:
            raise RekeningTidakDitemukan("Rekening tidak terdaftar")

        nasabah = rekening.pemilik

        if nasabah.NIK != nik:
            raise NikTidakSesuai(f"NIK ini tidak terdaftar sebagai pemilik rekening")

        return rekening, nasabah

    @staticmethod
    def validasi_target_level(target_level):
        if not isinstance(target_level, int) or isinstance(target_level, bool):
            raise InputTidakValid("Level rekening harus berupa angka")

        if target_level <= 0:
            raise InputTidakValid("Level rekening tidak boleh 0 atau negatif")

        if target_level not in RekeningService.jenis_rekening:
            raise InputTidakValid("Level rekening tidak tersedia")

    @staticmethod
    def _buat_konfigurasi_rekening(rekening: Rekening, target_level: int) -> Rekening:
        kelas_rekening = RekeningService.jenis_rekening[target_level]["kelas"]

        return kelas_rekening(
            norek=rekening.norek, pin=rekening.pin, pemilik=rekening.pemilik
        )

    @staticmethod
    def upgrade_rekening(nik: str, norek: str, target_level: int, pin: str) -> bool:

        RekeningService.validasi_target_level(target_level=target_level)
        Validator.validasi_format_identitas(nik=nik, norek=norek, pin=pin)
        RekeningService.verifikasi_pin_rekening(
            nik_aktif=nik, norek_aktif=norek, pin_input=pin
        )

        with buat_koneksi_tulis() as koneksi:

            rekening, nasabah = RekeningService.muat_rekening_dan_validasi_pemilik(
                nik=nik, norek=norek, koneksi=koneksi
            )

            if not rekening.boleh_ubah_level:
                raise StatusTidakValid(
                    "Perubahan rekening hanya bisa dilakukan 1 kali sehari"
                )
            if rekening.level == 4:
                raise StatusTidakValid("Level rekening ini sudah level tertinggi")

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

            konfigurasi_target_rekening = RekeningService._buat_konfigurasi_rekening(
                rekening=rekening, target_level=target_level
            )

            jenis_rekening_awal = rekening.jenis
            jenis_rekening_tujuan = konfigurasi_target_rekening.jenis

            terakhir_ubah_rekening_lama = rekening.terakhir_ubah_rekening
            terakhir_ubah_rekening_baru = datetime.date.today()
            limit_sisa_baru = konfigurasi_target_rekening.limit_harian

            jumlah_baris = RekeningRepository.ubah_state_setelah_upgrade_atau_downgrade(
                norek=rekening.norek,
                limit_sisa_baru=limit_sisa_baru,
                level_baru=target_level,
                terakhir_ubah_rekening_lama=terakhir_ubah_rekening_lama,
                terakhir_ubah_rekening_baru=terakhir_ubah_rekening_baru,
                koneksi=koneksi,
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal("Gagal melakukan peningkatan rekening")

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="peningkatan rekening",
                log=f"PENINGKATAN REKENING | Rekening awal {jenis_rekening_awal} ke Rekening {jenis_rekening_tujuan}",
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="peningkatan_level_rekening",
                log=(
                    f"{nasabah.nama} meningkatkan rekening "
                    f"dari {jenis_rekening_awal} ke {jenis_rekening_tujuan}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=konfigurasi_target_rekening.norek,
            )
            HelperPencatatan.simpan(
                koneksi=koneksi, norek=rekening.norek, audit=audit, riwayat=riwayat
            )

            return True

    @staticmethod
    def downgrade_rekening(nik: str, norek: str, target_level: int, pin: str) -> bool:

        RekeningService.validasi_target_level(target_level=target_level)
        Validator.validasi_format_identitas(nik=nik, norek=norek, pin=pin)
        RekeningService.verifikasi_pin_rekening(
            nik_aktif=nik, norek_aktif=norek, pin_input=pin
        )

        with buat_koneksi_tulis() as koneksi:

            rekening, nasabah = RekeningService.muat_rekening_dan_validasi_pemilik(
                nik=nik, norek=norek, koneksi=koneksi
            )

            if not rekening.boleh_ubah_level:
                raise StatusTidakValid(
                    "Perubahan rekening hanya bisa dilakukan 1 kali sehari"
                )
            if rekening.level == 1:
                raise StatusTidakValid("Level rekening ini sudah level terendah")

            if target_level >= rekening.level:
                raise LevelRekeningTidakValid(
                    "Pilihan level rekening harus lebih rendah dari level saat ini"
                )

            Validator.amankan_rekening(rekening=rekening)

            konfigurasi_target_rekening = RekeningService._buat_konfigurasi_rekening(
                rekening=rekening, target_level=target_level
            )
            jenis_rek_awal = rekening.jenis
            jenis_rek_tujuan = konfigurasi_target_rekening.jenis

            limit_sisa_baru = konfigurasi_target_rekening.limit_harian
            terakhir_ubah_rekening_lama = rekening.terakhir_ubah_rekening
            terakhir_ubah_rekening_baru = datetime.date.today()

            jumlah_baris = RekeningRepository.ubah_state_setelah_upgrade_atau_downgrade(
                norek=rekening.norek,
                limit_sisa_baru=limit_sisa_baru,
                level_baru=target_level,
                terakhir_ubah_rekening_lama=terakhir_ubah_rekening_lama,
                terakhir_ubah_rekening_baru=terakhir_ubah_rekening_baru,
                koneksi=koneksi,
            )
            if jumlah_baris != 1:
                raise PerbaruiStatusGagal("Gagal melakukan penurunan rekening")

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="penurunan rekening",
                log=f" PENURUNAN REKENING | Rekening Awal {jenis_rek_awal} ke Rekening {jenis_rek_tujuan}",
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="penurunan_level_rekening",
                log=(
                    f"{nasabah.nama} menurunkan rekening "
                    f"dari {jenis_rek_awal} ke {jenis_rek_tujuan}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek,
            )

            HelperPencatatan.simpan(
                koneksi=koneksi, norek=rekening.norek, audit=audit, riwayat=riwayat
            )

            return True

    @staticmethod
    def blokir_rekening(nik: str, norek: str, pin: str, alasan: str) -> bool:

        if not isinstance(alasan, str) or alasan.isdigit():
            raise InputTidakValid("Alasan blokir harus berupa kalimat")

        alasan_blokir = alasan.strip()

        if not alasan_blokir:
            raise InputTidakValid("Alasan blokir tidak boleh kosong")

        Validator.validasi_format_identitas(nik=nik, norek=norek, pin=pin)
        RekeningService.verifikasi_pin_rekening(
            nik_aktif=nik, norek_aktif=norek, pin_input=pin
        )

        with buat_koneksi_tulis() as koneksi:

            rekening, nasabah = RekeningService.muat_rekening_dan_validasi_pemilik(
                nik=nik, norek=norek, koneksi=koneksi
            )

            Validator.amankan_rekening(rekening=rekening)

            status_lama = rekening.status
            status_baru = "blokir"

            jumlah_baris = RekeningRepository.perbarui_status_blokir(
                norek=rekening.norek,
                status_lama=status_lama,
                status_baru=status_baru,
                alasan_blokir=alasan_blokir,
                koneksi=koneksi,
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal("Gagal memblokir rekening")

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="pemblokiran rekening",
                log=(
                    "PEMBLOKIRAN REKENING | "
                    f"Rekening diblokir. "
                    f"Alasan: {alasan_blokir}"
                ),
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="pemblokiran_rekening",
                log=(
                    f"{nasabah.nama} "
                    f"memblokir rekening. "
                    f"Alasan: {alasan_blokir}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek,
            )

            HelperPencatatan.simpan(
                koneksi=koneksi, norek=rekening.norek, audit=audit, riwayat=riwayat
            )

            return True

    @staticmethod
    def buka_blokir(nik: str, norek: str, pin: str) -> bool:

        Validator.validasi_format_identitas(nik=nik, norek=norek, pin=pin)
        RekeningService.verifikasi_pin_rekening(
            nik_aktif=nik, norek_aktif=norek, pin_input=pin
        )

        with buat_koneksi_tulis() as koneksi:

            rekening, nasabah = RekeningService.muat_rekening_dan_validasi_pemilik(
                nik=nik, norek=norek, koneksi=koneksi
            )

            if rekening.status == "tutup":
                raise StatusTidakValid("Rekening ini telah ditutup!")

            if rekening.status == "aktif":
                raise StatusTidakValid("Rekening sudah dalam status aktif")

            if rekening.status != "blokir":
                raise StatusTidakValid("Rekening tidak sedang dalam status blokir")

            status_lama = rekening.status
            status_baru = "aktif"

            jumlah_baris = RekeningRepository.perbarui_status_blokir(
                norek=rekening.norek,
                status_lama=status_lama,
                status_baru=status_baru,
                alasan_blokir=None,
                koneksi=koneksi,
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal("Gagal membuka blokir rekening")

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="pembukaan blokir rekening",
                log="PEMBUKAAN BLOKIR REKENING | " "Rekening kembali diaktifkan",
            )
            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="pembukaan_blokir_rekening",
                log=f"{nasabah.nama} membuka kembali blokir rekening",
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek,
            )

            HelperPencatatan.simpan(
                koneksi=koneksi, norek=rekening.norek, audit=audit, riwayat=riwayat
            )

            return True

    @staticmethod
    def buka_rekening(
        nik: str, pilihan: int, pin: str, setor_awal: int, koneksi: object | None = None
    ) -> Rekening:

        RekeningService.validasi_target_level(target_level=pilihan)
        Validator.validasi_format_nik(nik=nik)
        Validator.validasi_format_pin(pin=pin)

        if not isinstance(setor_awal, int) or isinstance(setor_awal, bool):
            raise InputTidakValid("Setor awal harus berupa angka")

        buat_baru_diluar_daftar = koneksi is None

        if buat_baru_diluar_daftar:
            koneksi = db_module.buat_koneksi()

        try:
            data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(
                nik=nik, koneksi=koneksi
            )

            if data_nasabah is None:
                raise NasabahTidakDitemukan("NIK tidak terdaftar")

            nasabah = NasabahLoader.rangkai_nasabah(data_nasabah=data_nasabah)

            norek = RekeningService.buat_norek(pilihan, koneksi)
            pin_hash = Validator.buat_hash(pin=pin)

            objek_rekening_baru = RekeningService.jenis_rekening[pilihan]["kelas"]

            waktu_dibuat = datetime.datetime.now()

            rekening_baru = objek_rekening_baru(
                norek=norek, pin=pin_hash, pemilik=nasabah, waktu_dibuat=waktu_dibuat
            )

            if setor_awal < rekening_baru.saldosetor_min:
                raise InputTidakValid(
                    "Setor awal tidak memenuhi saldo minimal setoran awal"
                )

            RekeningRepository.tambah_rekening(rekening=rekening_baru, koneksi=koneksi)

            jumlah_baris = RekeningRepository.tambah_saldo(
                norek=rekening_baru.norek,
                nominal=setor_awal,
                koneksi=koneksi,
            )

            if jumlah_baris != 1:
                raise PenambahanSaldoGagal("Gagal memasukkan setoran awal ke rekening")

            transaksi = {
                "jenis": JenisTransaksi.SETOR_AWAL,
                "norek_tujuan": rekening_baru.norek,
                "nominal": setor_awal,
                "saldo_tujuan_sebelum": 0,
                "saldo_tujuan_sesudah": setor_awal,
                "waktu": rekening_baru.waktu_dibuat,
            }

            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="setor awal",
                log=f"SETOR AWAL | +Rp{Utilitas.format_rupiah(setor_awal)}",
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="pembukaan_rekening",
                log=f"{nasabah.nama} membuka rekening baru",
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening_baru.norek,
            )
            riwayat_buka = RiwayatTemplate.template(
                kategori="rekening",
                jenis="pembukaan rekening",
                log=f"BUKA REKENING | {norek}",
            )
            RiwayatRepository.tambah_riwayat(
                norek=rekening_baru.norek, riwayat=riwayat_buka, koneksi=koneksi
            )

            HelperPencatatan.simpan(
                koneksi=koneksi,
                norek=rekening_baru.norek,
                audit=audit,
                riwayat=riwayat,
                transaksi=transaksi,
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
    def ganti_pin(nik: str, norek: str, pin_lama: str, pin_baru: str) -> bool:

        if pin_lama == pin_baru:
            raise InputTidakValid("PiN baru tidak boleh sama dengan PIN lama")

        Validator.validasi_format_identitas(nik=nik, norek=norek, pin=pin_lama)
        Validator.validasi_format_pin(pin=pin_baru)
        RekeningService.verifikasi_pin_rekening(nik_aktif=nik, norek_aktif=norek, pin_input=pin_lama)

        with buat_koneksi_tulis() as koneksi:

            rekening, nasabah = RekeningService.muat_rekening_dan_validasi_pemilik(
                nik=nik, norek=norek, koneksi=koneksi
            )

            Validator.amankan_rekening(rekening=rekening)

            hash_pin_lama = rekening.pin
            Validator.verifikasi_pin(pin_input=pin_lama, pin_database=hash_pin_lama)

            hash_pin_baru = Validator.buat_hash(pin=pin_baru)

            jumlah_baris = RekeningRepository.perbarui_pin(
                norek=rekening.norek,
                pin_lama=hash_pin_lama,
                pin_baru=hash_pin_baru,
                koneksi=koneksi,
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal("Gagal mengganti PIN rekening")

            riwayat = RiwayatTemplate.template(
                kategori="rekening",
                jenis="penggantian pin rekening",
                log="GANTI PIN REKENING | " "PIN rekening berhasil diperbarui",
            )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="rekening",
                aksi="penggantian_pin_rekening",
                log=f"{nasabah.nama} melakukan pergantian PIN rekening",
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek,
            )

            HelperPencatatan.simpan(
                koneksi=koneksi, norek=rekening.norek, audit=audit, riwayat=riwayat
            )

            return True

    @staticmethod
    def verifikasi_pin_rekening(nik_aktif: str, norek_aktif: str, pin_input: str):

        with buat_koneksi_tulis() as koneksi:
            data_rekening = RekeningRepository.ambil_data_rekening_dengan_nik_dan_norek(
                nik=nik_aktif, norek=norek_aktif, koneksi=koneksi
            )
            if data_rekening is None:
                raise RekeningTidakDitemukan("Rekening tidak terdaftar")

            hash_database = data_rekening["pin"]
            waktu_suspend = (
                datetime.datetime.fromisoformat(data_rekening["terkunci_sampai"])
                if data_rekening["terkunci_sampai"] is not None
                else None
            )

            if waktu_suspend is not None:

                sekarang = datetime.datetime.now()
                if sekarang < waktu_suspend:
                    raise RekeningTerkunci(
                        "Rekening terkunci sementara karena terlalu banyak percobaan PIN salah. Coba beberapa saat lagi"
                    )

            gagal = False
            try:
                Validator.verifikasi_pin(
                    pin_input=pin_input, pin_database=hash_database
                )

            except PinTidakCocok:
                gagal = True
                jumlah_baris = RekeningRepository.tambahkan_percobaan_gagal(
                    norek=norek_aktif, nik=nik_aktif, koneksi=koneksi
                )
                if jumlah_baris != 1:
                    raise PerbaruiStatusGagal("Gagal memperbarui data rekening")
                percobaan = RekeningRepository.ambil_jumlah_percobaan_gagal(
                    nik=nik_aktif, norek=norek_aktif, koneksi=koneksi
                )
                percobaan = percobaan["percobaan_gagal"]

                if percobaan >= 3:
                    sekarang = datetime.datetime.now()
                    buat_waktu_suspend = (
                        sekarang + datetime.timedelta(minutes=1)
                    ).isoformat()
                    jumlah_baris = RekeningRepository.ubah_waktu_terkunci(
                        nik=nik_aktif,
                        norek=norek_aktif,
                        koneksi=koneksi,
                        waktu_terkunci_baru=buat_waktu_suspend,
                    )
                    if jumlah_baris != 1:
                        raise PerbaruiStatusGagal("Gagal memperbarui data rekening")

            else:
                jumlah_baris = (
                    RekeningRepository.reset_jumlah_percobaan_dan_waktu_terkunci(
                        norek=norek_aktif, nik=nik_aktif, koneksi=koneksi
                    )
                )
                if jumlah_baris != 1:
                    raise PerbaruiStatusGagal("Gagal memperbarui data rekening")

        if gagal:
            raise PinTidakCocok("PIN yang dimasukkan salah")

    # method untuk membuat nomor rekening sesuai prefix yang tersedia
    @staticmethod
    def buat_norek(level: int, koneksi: object) -> str:

        if level not in RekeningService.jenis_rekening:
            raise InputTidakValid("Pilihan level rekening tidak tersedia")

        prefix = RekeningService.jenis_rekening[level]["prefix"]

        while True:
            digit_sisa = random.randint(100_000_000_000, 999_999_999_999)
            norek = prefix + str(digit_sisa)

            is_norek_terdaftar = RekeningRepository.cari_rekening_dengan_norek(
                norek, koneksi
            )

            if is_norek_terdaftar is None:
                return norek

    # method pencari semua rekening milik nasabah
    @staticmethod
    def cari_semua_rekening(nik: str) -> list:

        with buat_koneksi_baca() as koneksi:
            return RekeningRepository.cari_rekening_dengan_nik(nik=nik, koneksi=koneksi)

    # method filter status rekening selain tutup untuk pilihan login
    @staticmethod
    def cari_norek_tersedia(nik: str) -> list:

        daftar_rekening = RekeningService.cari_semua_rekening(nik=nik)

        daftar_rekening_aktif = []
        for data_rekening in daftar_rekening:
            if data_rekening["status"] != "tutup":
                daftar_rekening_aktif.append(data_rekening["norek"])

        return daftar_rekening_aktif

    # method untuk menampilkan semua rekening nasabah untuk menu riwayat
    @staticmethod
    def cari_semua_rekening_untuk_riwayat(nik: str) -> dict:

        daftar_rekening_nasabah = RekeningService.cari_semua_rekening(nik=nik)

        return {data["norek"]: data["status"] for data in daftar_rekening_nasabah}

    # method untuk menampilkan rekening untuk diupgrade/downgrade serta penutupan
    @staticmethod
    def cari_rekening_untuk_diubah_atau_untuk_pangajuan(norek):
        with buat_koneksi_baca() as koneksi:

            return RekeningRepository.cari_rekening_dengan_norek(
                norek=norek, koneksi=koneksi
            )

    @staticmethod
    def ambil_data_rekening(norek):
        with buat_koneksi_baca() as koneksi:
            data_rekening = RekeningRepository.cari_rekening_dengan_norek(
                norek=norek, koneksi=koneksi
            )
        return data_rekening
