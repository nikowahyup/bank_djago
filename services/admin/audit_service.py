
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_structure import STRUKTUR_AUDIT

from bank_djago.utils.utility import Utilitas
class AuditService:

    @staticmethod
    def tambah_audit(kategori,objek,aksi,log,nama=None,nik=None,norek=None):
        audit = {
            "kategori":kategori,
            "objek":objek,
            "aksi":aksi,
            "waktu":Utilitas.waktu_sekarang(),
            "log":log
        }
        if nik is not None:
            audit["nik"] = nik
        if nama is not None:
            audit["nama"] = nama
        if norek is not None:
            audit["norek"] = norek

        return audit


    @staticmethod
    def cari_audit(
        kategori=None,
        objek=None,
        aksi=None
    ):

        if kategori is not None:
            if kategori not in STRUKTUR_AUDIT:
                raise ValueError(
                    "Kategori audit tidak terdaftar"
                )

        if objek is not None:
            if kategori is None:
                raise ValueError(
                    "Kategori harus dipilih sebelum objek"
                )

            if objek not in STRUKTUR_AUDIT[kategori]:
                raise ValueError(
                    "Objek audit tidak terdaftar"
                )

        if aksi is not None:
            if objek is None:
                raise ValueError(
                    "Objek harus dipilih sebelum aksi"
                )

            if aksi not in STRUKTUR_AUDIT[kategori][objek]:
                raise ValueError(
                    "Aksi audit tidak terdaftar"
                )

        koneksi = buat_koneksi()

        try:
            data_audit = AuditRepository.cari_audit(
                koneksi=koneksi,
                kategori=kategori,
                objek=objek,
                aksi=aksi
            )

            return data_audit

        finally:
            koneksi.close()

