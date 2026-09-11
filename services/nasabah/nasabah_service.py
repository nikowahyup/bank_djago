
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
                kategori="administratif",
                objek="nasabah",
                aksi="pendaftaran_nasabah",
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

    @staticmethod
    def ganti_alamat(
            nasabah,
            alamat_baru
    ):

        alamat_baru = alamat_baru.strip()

        if not alamat_baru:
            raise ValueError("Alamat baru tidak boleh kosong")

        if nasabah.alamat == alamat_baru:
            raise ValueError("Alamat baru tidak boleh sama dengan alamat lama")

        koneksi = buat_koneksi()

        try:
            data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(nik=nasabah.NIK,koneksi=koneksi)

            if data_nasabah is None:
                raise ValueError("Nasabah tidak terdaftar")


            jumlah_baris = NasabahRepository.ganti_alamat(nik_pemilik=nasabah.NIK,alamat_baru=alamat_baru,koneksi=koneksi)

            if jumlah_baris != 1:
                raise ValueError("Gagal memperbarui alamat nasabah")

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="nasabah",
                aksi="penggantian alamat",
                log=f"{nasabah.nama} mengubah alamatnya",
                nama=nasabah.nama,
                nik=nasabah.NIK
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

        nasabah.alamat = alamat_baru


