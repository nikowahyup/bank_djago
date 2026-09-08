import datetime
import random
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.core.rekening import RekeningReguler,RekeningPrioritas,RekeningGold,RekeningPlatinum
from bank_djago.utils.validator import Validator
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.utils.utility import JenisTransaksi, Utilitas



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
    def upgrade_rekening(rekening_lama,target_level):

        if not rekening_lama.boleh_ubah_level:
            raise ValueError("Perubahan rekening hanya bisa dilakukan 1 kali sehari")

        if target_level not in RekeningService.jenis_rekening:
            raise ValueError("Level rekening tidak tersedia")

        if target_level <= rekening_lama.level:
            raise  ValueError("Level upgrade rekening harus lebih tinggi dari level saat ini")

        Validator.amankan_rekening(rekening_lama)
        info = RekeningService.jenis_rekening[target_level]
        kelas = info["kelas"]

        if rekening_lama.saldo < info["minimal_upgrade"]:
            raise ValueError("Saldo kini tidak memenuhi saldo minimum rekening tujuan")

        nasabah = rekening_lama.pemilik

        try:
            indeks = nasabah.rekening.index(rekening_lama)
        except ValueError:
            raise ValueError(
                "Rekening lama tidak ditemukan dalam daftar rekening nasabah"
            )
        koneksi = buat_koneksi()
        try:

            rek_awal = RekeningService.level[rekening_lama.level]
            rek_tujuan = RekeningService.level[target_level]

            rekening_baru = kelas(norek=rekening_lama.norek,pin=rekening_lama.pin,pemilik=nasabah,waktu_dibuat=rekening_lama.waktu_dibuat)
            rekening_baru.set_saldo(rekening_lama.saldo)
            rekening_baru.riwayat = list(rekening_lama.riwayat)
            rekening_baru.waktu_bayar_admin = rekening_lama.waktu_bayar_admin
            rekening_baru.dapat_bunga = rekening_lama.dapat_bunga
            rekening_baru.terakhir_ubah_rekening = datetime.date.today()
            rekening_baru.reset = rekening_lama.reset

            jumlah_baris = RekeningRepository.perbarui_level_rekening(rekening_baru,koneksi)

            if jumlah_baris != 1:
                raise ValueError("Rekening tidak ditemukan")

            riwayat = RiwayatTemplate.upgrade_rekening(
                sebelum=rek_awal,
                sesudah=rek_tujuan
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening_baru.norek,
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
                norek=rekening_baru.norek
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

        for pinjaman in nasabah.daftar_pinjaman:
            if pinjaman.rekening is rekening_lama:
                pinjaman.rekening = rekening_baru


        for deposito in nasabah.deposito:
            if deposito.rekening is rekening_lama:
                deposito.rekening = rekening_baru



        nasabah.rekening[indeks] = rekening_baru
        rekening_baru.simpan_riwayat(riwayat)


        return rekening_baru



    @staticmethod
    def downgrade_rekening(rekening_lama,target_level):

        Validator.amankan_rekening(rekening_lama)
        if not rekening_lama.boleh_ubah_level:
            raise  ValueError("Perubahan rekening hanya bisa dilakukan 1 kali sehari")

        if target_level not in RekeningService.jenis_rekening:
            raise ValueError("Level rekening tidak tersedia")

        if target_level >= rekening_lama.level:
            raise ValueError("Pilihan level rekening harus lebih rendah dari level saat ini")

        nasabah = rekening_lama.pemilik

        try:
            indeks = nasabah.rekening.index(rekening_lama)
        except ValueError:
            raise ValueError(
                "Rekening lama tidak ditemukan dalam daftar rekening nasabah")

        koneksi = buat_koneksi()

        try:

            rek_awal = RekeningService.level[rekening_lama.level]
            rek_tujuan = RekeningService.level[target_level]
            info = RekeningService.jenis_rekening[target_level]


            rekening_baru = info["kelas"](
                norek=rekening_lama.norek,
                pin=rekening_lama.pin,
                pemilik=rekening_lama.pemilik,
                waktu_dibuat=rekening_lama.waktu_dibuat)

            rekening_baru.set_saldo(rekening_lama.saldo)
            rekening_baru.riwayat = list(rekening_lama.riwayat)
            rekening_baru.waktu_bayar_admin = rekening_lama.waktu_bayar_admin
            rekening_baru.dapat_bunga = rekening_lama.dapat_bunga
            rekening_baru.terakhir_ubah_rekening = datetime.date.today()
            rekening_baru.reset = rekening_lama.reset
            jumlah_baris = RekeningRepository.perbarui_level_rekening(rekening_baru,koneksi)
            if jumlah_baris != 1:
                raise ValueError("Rekening tidak ditemukan")

            riwayat = RiwayatTemplate.downgrade_rekening(
                sebelum=rek_awal,
                sesudah=rek_tujuan
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening_baru.norek,
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
                norek=rekening_baru.norek
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


        for pinjaman in nasabah.daftar_pinjaman:
            if pinjaman.rekening is rekening_lama:
                pinjaman.rekening = rekening_baru


        for deposito in nasabah.deposito:
            if deposito.rekening is rekening_lama:
                deposito.rekening = rekening_baru

        nasabah.rekening[indeks] = rekening_baru
        rekening_baru.simpan_riwayat(riwayat)

        return rekening_baru

    @staticmethod
    def blokir_rekening(
            rekening,
            alasan
    ):
        Validator.amankan_rekening(rekening)

        alasan_blokir = alasan.strip()

        if not alasan_blokir:
            raise ValueError(
                "Alasan blokir tidak boleh kosong"
            )

        status_baru = "blokir"

        koneksi = buat_koneksi()

        try:
            jumlah_baris = (
                RekeningRepository.perbarui_status_blokir(
                    norek=rekening.norek,
                    status_baru=status_baru,
                    alasan_blokir=alasan_blokir,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise ValueError(
                    "Gagal memblokir rekening"
                )

            riwayat = RiwayatTemplate.template(
                kategori="sistem",
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

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        rekening.status = status_baru
        rekening.alasan_blokir = alasan_blokir
        rekening.simpan_riwayat(riwayat)




    @staticmethod
    def buka_blokir(
            rekening,
            pin
    ):

        if rekening.status == "tutup":
            raise ValueError(
                "Rekening ini telah ditutup!"
            )

        if rekening.status == "aktif":
            raise ValueError(
                "Rekening sudah dalam status aktif"
            )

        if rekening.status != "blokir":
            raise ValueError(
                "Rekening tidak sedang dalam status blokir"
            )

        if not rekening.cek_pin(pin):
            raise ValueError(
                "PIN rekening salah"
            )

        status_baru = "aktif"

        koneksi = buat_koneksi()

        try:
            jumlah_baris = RekeningRepository.perbarui_status_blokir(
                norek=rekening.norek,
                status_baru=status_baru,
                alasan_blokir=None,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise ValueError("Gagal membuka blokir rekening")

            riwayat = RiwayatTemplate.template(
                kategori="sistem",
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

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        rekening.status = status_baru
        rekening.alasan_blokir = None
        rekening.simpan_riwayat(riwayat)







    @staticmethod
    def buka_rekening(nasabah,pilihan,pin,setor_awal,koneksi=None):

        buat_baru = koneksi is None

        if buat_baru:
            koneksi = buat_koneksi()

        try:
            info = RekeningService.jenis_rekening[pilihan]
            kelas_rek = info["kelas"]
            norek = RekeningService.buat_norek(pilihan, koneksi)

            waktu_dibuat = datetime.datetime.now()
            rekening_baru = kelas_rek(norek=norek,pin=pin,pemilik=nasabah,waktu_dibuat=waktu_dibuat)


            if setor_awal < rekening_baru.saldosetor_min:
                raise  ValueError("Setor awal tidak memenuhi saldo minimal setoran awal")


            rekening_baru.tambah_saldo(setor_awal)

            RekeningRepository.tambah_rekening(rekening_baru, koneksi)
            transaksi = {
                "jenis": JenisTransaksi.SETOR_AWAL,
                "norek_tujuan": rekening_baru.norek,
                "nominal": setor_awal,
                "saldo_tujuan_sebelum": 0,
                "saldo_tujuan_sesudah": setor_awal,
                "waktu": rekening_baru.waktu_dibuat
            }
            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi, koneksi)

            riwayat = RiwayatTemplate.template(kategori="transaksi",jenis="setor awal",log=f"SETOR AWAL | +Rp{Utilitas.format_rupiah(setor_awal)}")

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek = "rekening",
                aksi = "pembukaan_rekening",
                log=f"{nasabah.nama} membuka rekening baru",
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening_baru.norek
            )
            RiwayatRepository.tambah_riwayat(rekening_baru.norek, riwayat, koneksi, id_transaksi)
            AuditRepository.tambah_audit(audit,koneksi,id_transaksi)

            if buat_baru:
                koneksi.commit()
                nasabah.rekening.append(rekening_baru)

            return rekening_baru

        except Exception:
            if buat_baru:
                koneksi.rollback()

            raise

        finally:
            if buat_baru:
                koneksi.close()


    @staticmethod
    def ganti_pin(
            rekening,
            pin_lama,
            pin_baru
    ):

        Validator.amankan_rekening(rekening)

        if not rekening.cek_pin(pin_lama):
            raise ValueError("PIN lama salah")

        Validator.validasi_pin(pin_baru)

        if rekening.cek_pin(pin_baru):
            raise   ValueError(
                "PIN baru tidak boleh sama dengan PIN lama"
            )

        koneksi = buat_koneksi()

        try:

            jumlah_baris = RekeningRepository.perbarui_pin(
                norek=rekening.norek,
                pin_baru=pin_baru,
                koneksi=koneksi)


            if jumlah_baris != 1:
                raise ValueError("Gagal mengganti PIN rekening")

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

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()
        rekening.ganti_pin(pin_baru)
        rekening.simpan_riwayat(riwayat)

    @staticmethod
    def buat_norek(level, koneksi):
        if level not in RekeningService.jenis_rekening:
            raise ValueError("Pilihan level rekening tidak tersedia")

        prefix = RekeningService.jenis_rekening[level]["prefix"]

        while True:
            digit_sisa = random.randint(100_000_000_000,999_999_999_999)
            norek = prefix + str(digit_sisa)

            rekening_terdaftar = RekeningRepository.cari_rekening_dengan_norek(norek, koneksi)

            if rekening_terdaftar is None:
                return norek