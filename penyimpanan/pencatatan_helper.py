
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository


class HelperPencatatan:


    @staticmethod
    def simpan(koneksi,norek, audit=None, riwayat=None, transaksi=None):

        id_transaksi = None

        if transaksi is not None:
            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi=transaksi, koneksi=koneksi)

        if audit is not None:
            AuditRepository.tambah_audit(audit=audit,koneksi=koneksi, id_transaksi=id_transaksi)

        if riwayat is not None:
            RiwayatRepository.tambah_riwayat(norek, riwayat, koneksi, id_transaksi=id_transaksi)