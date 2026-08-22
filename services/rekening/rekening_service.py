import datetime
from logging.config import valid_ident

from bank_djago.services.deposito.deposito_service import StatusDeposito
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.core.rekening import RekeningReguler,RekeningPrioritas,RekeningGold,RekeningPlatinum
from bank_djago.services.transaksi.transaksi_service import TransaksiService
from bank_djago.utils.utility import StatusPinjaman
from bank_djago.utils.validator import Validator

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
    def autentikasi_rekening(bank,norek,pin):
        rekening = bank.cari_rekening(norek)
        if not rekening:
            raise ValueError("Nomor rekening tidak terdaftar")

        if rekening.status != "aktif":
            raise ValueError(f"Rekening telah di{rekening.status}")

        if not rekening.cek_pin(pin):
            raise ValueError("PIN salah")

        return rekening

    @staticmethod
    def upgrade_rekening(bank,rekening_lama,target_level):

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

        rek_awal = RekeningService.level[rekening_lama.level]
        rek_tujuan = RekeningService.level[target_level]
        nasabah = rekening_lama.pemilik
        rekening_baru = kelas(norek=rekening_lama.norek,pin=rekening_lama.pin,pemilik=nasabah)
        rekening_baru.set_saldo(rekening_lama.saldo)
        rekening_baru.riwayat = rekening_lama.riwayat
        rekening_baru.waktu_bayar_admin = rekening_lama.waktu_bayar_admin
        rekening_baru.dapat_bunga = rekening_lama.dapat_bunga
        rekening_baru.boleh_ubah_rekening = datetime.date.today()


        for pinjaman in bank.daftar_pinjaman:
            if pinjaman.rekening is rekening_lama:
                pinjaman.rekening = rekening_baru


        for deposito in nasabah.deposito:
            if deposito.rekening is rekening_lama:
                deposito.rekening = rekening_baru

        bank.rekening_index[rekening_baru.norek] = rekening_baru
        indeks = nasabah.rekening.index(rekening_lama)
        nasabah.rekening[indeks] = rekening_baru

        log = RiwayatTemplate.upgrade_rekening(sebelum=rek_awal, sesudah=rek_tujuan)
        AuditService.tambah_audit(bank, "rekening", jenis="upgrade",log=f"{nasabah.nama} meningkatkan rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
        rekening_baru.simpan_riwayat(log)
        return rekening_baru



    @staticmethod
    def downgrade_rekening(bank,rekening_lama,target_level):

        if not rekening_lama.boleh_ubah_level:
            raise  ValueError("Perubahan rekening hanya bisa dilakukan 1 kali sehari")

        if target_level not in RekeningService.jenis_rekening:
            raise ValueError("Level rekening tidak tersedia")

        if target_level >= rekening_lama.level:
            raise ValueError("Pilihan level rekening harus lebih rendah dari level saat ini")
        Validator.amankan_rekening(rekening_lama)

        info = RekeningService.jenis_rekening[target_level]

        rekening_baru = info["kelas"](
            norek=rekening_lama.norek,
            pin=rekening_lama.pin,
            pemilik=rekening_lama.pemilik)

        rekening_baru.set_saldo(rekening_lama.saldo)
        rekening_baru.riwayat = rekening_lama.riwayat
        rekening_baru.waktu_bayar_admin = rekening_lama.waktu_bayar_admin
        rekening_baru.dapat_bunga = rekening_lama.dapat_bunga
        rekening_baru.boleh_ubah_rekening = datetime.date.today()

        rek_awal = RekeningService.level[rekening_lama.level]
        rek_tujuan = RekeningService.level[target_level]

        nasabah = rekening_lama.pemilik
        pinjaman = nasabah.pinjaman
        if pinjaman:
            if pinjaman.rekening is rekening_lama:
                pinjaman.rekening = rekening_baru


        for deposito in nasabah.deposito:
            if deposito.rekening is rekening_lama:
                deposito.rekening = rekening_baru

        bank.rekening_index[rekening_lama.norek] = rekening_baru
        index = nasabah.rekening.index(rekening_lama)
        nasabah.rekening[index] = rekening_baru

        log = RiwayatTemplate.downgrade_rekening(sebelum=rek_awal, sesudah=rek_tujuan)
        AuditService.tambah_audit(bank, "rekening", jenis="downgrade",log=f"{nasabah.nama} menurunkan rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
        rekening_baru.simpan_riwayat(log)
        return rekening_baru


    @staticmethod
    def blokir_rekening(bank,rekening,alasan):
        Validator.amankan_rekening(rekening)
        if rekening.status == "blokir":
            raise ValueError("Rekening ini sudah diblokir")
        if rekening.status == "tutup":
            raise ValueError("Rekening ini telah ditutup")
        rekening.status = "blokir"
        rekening.alasan_blokir = alasan
        AuditService.tambah_audit(bank,kategori="rekening",jenis="pemblokiran",log=f"{rekening.pemilik.nama} telah memblokir rekening",nik=rekening.pemilik.NIK,norek=rekening.norek)



    @staticmethod
    def buka_blokir(bank,rekening):
        if rekening.status == "tutup":
            raise ValueError("Rekening ini telah ditutup!")
        if rekening.status == "aktif":
            raise ValueError("Rekening sudah dalam status aktif")
        rekening.status = "aktif"
        AuditService.tambah_audit(bank,kategori="rekening",jenis="buka blokir",log=f"{rekening.pemilik.nama} membuka kembali blokiran rekening",nik=rekening.pemilik.NIK,norek=rekening.norek)



    @staticmethod
    def tutup_rekening(bank,rekening,penerima=None):
        Validator.amankan_rekening(rekening)
        if rekening.status == "tutup":
            raise ValueError("Rekening memang telah ditutup")

        if rekening.status == "blokir":
            raise ValueError("Rekening dalam status blokir. Tidak bisa ditutup")

        deposito_aktif = any(deposito.rekening is rekening and deposito.status in
                             (StatusDeposito.AKTIF,StatusDeposito.JATUH_TEMPO)
                             for deposito in rekening.pemilik.deposito)
        if deposito_aktif:
            raise ValueError("Rekening ini masih memiliki deposito aktif")

        pinjaman_aktif = any(pinjaman.rekening is rekening and pinjaman.status in
                             (StatusPinjaman.AKTIF,StatusPinjaman.DISETUJUI,StatusPinjaman.DIAJUKAN)
                             for pinjaman in bank.daftar_pinjaman)
        if pinjaman_aktif:
            raise ValueError("Rekening masih memiliki pinjaman aktif")

        if penerima:
            if penerima is rekening:
                raise ValueError("Tidak bisa kirim uang ke rekening yang mau ditutup")

            Validator.amankan_rekening(penerima)
            TransaksiService.transfer_semua_uang(rekening,penerima)

        else:
            TransaksiService.tarik_semua_uang(rekening)
        rekening.status = "tutup"


        AuditService.tambah_audit(bank,kategori="rekening",
                                  jenis="penutupan",
                                  log=f"{rekening.pemilik.nama} telah menutup rekening",
                                  nik=rekening.pemilik.NIK,
                                  norek=rekening.norek)




    @staticmethod
    def buka_rekening(bank,nasabah,pilihan,pin,setor_awal):
        info = RekeningService.jenis_rekening[pilihan]
        prefix = info["prefix"]
        kelas_rek = info["kelas"]
        norek = bank.buat_norek(prefix)
        rekening_baru = kelas_rek(norek=norek,pin=pin,pemilik=nasabah)

        if setor_awal < rekening_baru.saldosetor_min:
            raise  ValueError("Setor awal tidak memenuhi saldo minimal setoran awal")

        bank.rekening_index[norek] = rekening_baru
        rekening_baru.tambah_saldo(setor_awal)


        nasabah.rekening.append(rekening_baru)

        return rekening_baru

    @staticmethod
    def reset_pin(bank,rekening,pin):
        if pin == rekening.pin:
            raise ValueError("PIN masih sama dengan PIN lama")
        rekening.ganti_pin(pin)
        AuditService.tambah_audit(bank, "rekening", jenis="reset pin",
                                  log=f"{rekening.pemilik.nama} meminta reset pin pada rekeningnya",
                                  norek=rekening.norek)
