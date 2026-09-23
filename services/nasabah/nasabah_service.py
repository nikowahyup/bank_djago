from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis, buat_koneksi_baca
from bank_djago.core.nasabah import Nasabahh
from bank_djago.services.exceptions import InputTidakValid, NasabahTidakDitemukan, PerbaruiStatusGagal
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.services.admin.audit_service import AuditService

class NasabahService:

    @staticmethod
    def daftar_dan_buka_rekening(
            nik,
            nama,
            alamat,
            pin,
            setor_awal,
            level
    ):


        with buat_koneksi_tulis() as koneksi:
            validasi_nik = NasabahRepository.cari_nasabah_dengan_nik(nik=nik, koneksi=koneksi)

            if validasi_nik is not None:
                raise InputTidakValid(
                    "NIK sudah terdaftar. Silahkan pilih opsi buka rekening untuk nasabah lama"
                )

            nasabah_baru = Nasabahh(nama=nama, alamat=alamat, nik=nik)

            NasabahRepository.tambah_nasabah(nasabah=nasabah_baru, koneksi=koneksi)

            rekening_baru = RekeningService.buka_rekening(
                nik=nasabah_baru.NIK,
                pilihan=level,
                pin=pin,
                setor_awal=setor_awal,
                koneksi=koneksi
            )

            audit_pendaftaran = AuditService.tambah_audit(
                kategori="administratif",
                objek="nasabah",
                aksi="pendaftaran_nasabah",
                log=f"{nasabah_baru.nama} terdaftar sebagai nasabah baru",
                nama=nasabah_baru.nama,
                nik=nasabah_baru.NIK,
                norek=rekening_baru.norek
            )
            AuditRepository.tambah_audit(audit=audit_pendaftaran,koneksi=koneksi)

        return nasabah_baru, rekening_baru


    @staticmethod
    def ganti_alamat(
            nik,
            alamat_baru
    ):

        alamat_baru = alamat_baru.strip()

        if not alamat_baru:
            raise InputTidakValid(
                "Alamat baru tidak boleh kosong"
            )



        with buat_koneksi_tulis() as koneksi:

            data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(
                nik=nik,
                koneksi=koneksi
            )

            if data_nasabah is None:
                raise NasabahTidakDitemukan(
                    "Nasabah tidak terdaftar"
                )

            nasabah = NasabahLoader.rangkai_nasabah(data_nasabah=data_nasabah)
            alamat_lama = nasabah.alamat

            if nasabah.alamat == alamat_baru:
                raise InputTidakValid(
                    "Alamat baru tidak boleh sama dengan alamat lama"
                )

            jumlah_baris = NasabahRepository.ganti_alamat(
                nik_pemilik=nasabah.NIK,
                alamat_lama=alamat_lama,
                alamat_baru=alamat_baru,
                koneksi=koneksi
            )

            if jumlah_baris != 1:
                raise PerbaruiStatusGagal(
                    "Gagal memperbarui alamat nasabah"
                )

            audit = AuditService.tambah_audit(
                kategori="administratif",
                objek="nasabah",
                aksi="penggantian_alamat",
                log=f"{nasabah.nama} mengubah alamatnya",
                nama=nasabah.nama,
                nik=nasabah.NIK
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )


    @staticmethod
    def cari_nik_terdaftar(nik):
        with buat_koneksi_baca() as koneksi:
            return NasabahRepository.cari_nasabah_dengan_nik(nik=nik, koneksi=koneksi)

    @staticmethod
    def cari_data_login(nik):

        data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(nik)

        if data_nasabah is None:
            return None

        return {
            'nik':data_nasabah['nik'],
            'nama':data_nasabah['nama']
        }


