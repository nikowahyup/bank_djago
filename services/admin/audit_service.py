from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi, buat_koneksi_baca
from bank_djago.services.admin.audit_structure import STRUKTUR_AUDIT
from bank_djago.services.exceptions import InputTidakValid

from bank_djago.utils.utility import Utilitas


class AuditService:

    # method  template untuk audit
    @staticmethod
    def tambah_audit(kategori, objek, aksi, log, nama=None, nik=None, norek=None):
        audit = {
            "kategori": kategori,
            "objek": objek,
            "aksi": aksi,
            "waktu": Utilitas.waktu_sekarang(),
            "log": log,
        }
        if nik is not None:
            audit["nik"] = nik
        if nama is not None:
            audit["nama"] = nama
        if norek is not None:
            audit["norek"] = norek

        return audit

    # method pemfilter audit
    @staticmethod
    def cari_audit(kategori=None, objek=None, aksi=None):

        if kategori is not None:
            if kategori not in STRUKTUR_AUDIT:
                raise InputTidakValid("Kategori audit tidak terdaftar")

        if objek is not None:
            if kategori is None:
                raise InputTidakValid("Kategori harus dipilih sebelum objek")

            if objek not in STRUKTUR_AUDIT[kategori]:
                raise InputTidakValid("Objek audit tidak terdaftar")

        if aksi is not None:
            if objek is None:
                raise InputTidakValid("Objek harus dipilih sebelum aksi")

            if aksi not in STRUKTUR_AUDIT[kategori][objek]:
                raise InputTidakValid("Aksi audit tidak terdaftar")

        with buat_koneksi_baca() as koneksi:
            data_audit = AuditRepository.cari_audit(
                koneksi=koneksi, kategori=kategori, objek=objek, aksi=aksi
            )

            return data_audit
