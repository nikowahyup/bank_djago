from bank_djago.services.transaksi.riwayat.factory import RiwayatTemplate
from bank_djago.services.admin.rekap_audit import AuditService
from bank_djago.core.rekening import RekeningReguler,RekeningPrioritas,RekeningGold,RekeningPlatinum
from bank_djago.services.transaksi.transaksi_service import TransaksiService
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

        pinjaman = nasabah.pinjaman
        if pinjaman:
            if pinjaman.rekening == rekening_lama:
                pinjaman.rekening = rekening_baru


        for deposito in nasabah.deposito:
            if deposito.rekening == rekening_lama:
                deposito.rekening = rekening_baru

        bank.rekening_index[rekening_baru.norek] = rekening_baru
        indeks = nasabah.rekening.index(rekening_lama)
        nasabah.rekening[indeks] = rekening_baru

        log = RiwayatTemplate.upgrade_rekening(sebelum=rek_awal, sesudah=rek_tujuan)
        AuditService.tambah_audit(bank, "rekening", jenis="upgrade",log=f"{nasabah.nama} meningkatkan rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
        rekening_baru.simpan_riwayat(log)



    @staticmethod
    def downgrade_rekening(bank,rekening_lama,target_level):
        Validator.amankan_rekening(rekening_lama)

        info = RekeningService.jenis_rekening[target_level]

        rekening_baru = info["kelas"](
            norek=rekening_lama.norek,
            pin=rekening_lama.pin,
            pemilik=rekening_lama.pemilik)

        rekening_baru.set_saldo(rekening_lama.saldo)
        rekening_baru.riwayat = rekening_lama.riwayat

        rek_awal = RekeningService.level[rekening_lama.level]
        rek_tujuan = RekeningService.level[target_level]

        nasabah = rekening_lama.pemilik
        pinjaman = nasabah.pinjaman
        if pinjaman:
            if pinjaman.rekening == rekening_lama:
                pinjaman.rekening = rekening_baru


        for deposito in nasabah.deposito:
            if deposito.rekening == rekening_lama:
                deposito.rekening = rekening_baru

        bank.rekening_index[rekening_lama.norek] = rekening_baru
        index = nasabah.rekening.index(rekening_lama)
        nasabah.rekening[index] = rekening_baru

        log = RiwayatTemplate.downgrade_rekening(sebelum=rek_awal, sesudah=rek_tujuan)
        AuditService.tambah_audit(bank, "rekening", jenis="downgrade",log=f"{nasabah.nama} menurunkan rekeningnya dari {rek_awal} ke {rek_tujuan}",norek=rekening_baru.norek)
        rekening_baru.simpan_riwayat(log)



    @staticmethod
    def blokir_rekening(rekening,alasan):
        Validator.amankan_rekening(rekening)
        if rekening.status == "blokir":
            raise ValueError("Rekening ini sudah diblokir")
        if rekening.status == "tutup":
            raise ValueError("Rekening ini telah ditutup")
        rekening.status = "blokir"
        rekening.alasan_blokir = alasan



    @staticmethod
    def buka_blokir(rekening):
        if rekening.status == "tutup":
            raise ValueError("Rekening ini telah ditutup!")
        if rekening.status == "aktif":
            raise ValueError("Rekening sudah dalam status aktif")
        rekening.status = "aktif"


    @staticmethod
    def tutup_rekening(rekening,penerima=None):
        Validator.amankan_rekening(rekening)
        if rekening.status == "tutup":
            raise ValueError("Rekening memang telah ditutup")
        if rekening.status == "blokir":
            raise ValueError("Rekening dalam status blokir. Tidak bisa ditutup")
        if penerima:
            TransaksiService.transfer_semua_uang(rekening,penerima)
            rekening.status = "tutup"
        else:
            TransaksiService.tarik_semua_uang(rekening)
            rekening.status = "tutup"

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