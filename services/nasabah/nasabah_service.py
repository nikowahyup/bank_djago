from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.core.nasabah import Nasabahh
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.services.admin.audit_service import AuditService

class NasabahService:

    @staticmethod
    def daftar_dan_buka_rekening(nik, nama, alamat, pin, setor_awal, level):
        validasi_nik = NasabahRepository.cari_nasabah_dengan_nik(nik)
        if validasi_nik is not None:
            raise ValueError("NIK sudah terdaftar. Silahkan pilih opsi buka rekening untuk nasabah lama")

        nasabah_baru = Nasabahh(nama=nama,alamat=alamat,nik=nik)

        koneksi_database = buat_koneksi()

        try:
            NasabahRepository.tambah_nasabah(nasabah_baru, koneksi_database)

            rekening_baru = RekeningService.buka_rekening(nasabah=nasabah_baru, pilihan=level, pin=pin, setor_awal=setor_awal,koneksi=koneksi_database)

            audit_pendaftaran = AuditService.tambah_audit(
                kategori="nasabah",
                jenis="pendaftaran nasabah",
                log=f"{nasabah_baru.nama} terdaftar sebagai nasabah baru",
                nama=nasabah_baru.nama,
                nik=nasabah_baru.NIK,
                norek=rekening_baru.norek
            )
            AuditRepository.tambah_audit(audit_pendaftaran,koneksi_database)
            koneksi_database.commit()
            nasabah_baru.rekening.append(rekening_baru)

            return nasabah_baru, rekening_baru

        except Exception:
            koneksi_database.rollback()
            raise

        finally:
                koneksi_database.close()


