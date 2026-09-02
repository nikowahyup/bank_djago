from bank_djago.penyimpanan.repositories.notifikasi_repository import NotifikasiRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.core.notifikasi import Notifikasi
from bank_djago.utils.utility import JenisReferensiID


class NotifikasiService:


    @staticmethod
    def simpan_notifikasi_referensi(nasabah, jenis, pesan, jenis_referensi, id_objek):

        koneksi = buat_koneksi()

        try:
            notifikasi_lama = NotifikasiRepository.cari_notifikasi_dengan_referensi(nik_pemilik=nasabah.NIK,
                                                                                    jenis_referensi=jenis_referensi,
                                                                                    id_objek=id_objek,
                                                                                    koneksi=koneksi)

            if notifikasi_lama is not None and notifikasi_lama["pesan"] == pesan:
                return False

            if notifikasi_lama is not None:
                NotifikasiRepository.hapus_notifikasi_dengan_referensi(nik_pemilik=nasabah.NIK,
                                                                       jenis_referensi=jenis_referensi,
                                                                       id_objek=id_objek,
                                                                       koneksi=koneksi)

            notifikasi_baru = Notifikasi(jenis=jenis,pesan=pesan,jenis_referensi=jenis_referensi,id_objek=id_objek)

            NotifikasiRepository.tambah_notifikasi(nik_pemilik=nasabah.NIK,notifikasi=notifikasi_baru,koneksi=koneksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise
        finally:
            koneksi.close()

        nasabah.notifikasi = [notifikasi
                              for notifikasi in nasabah.notifikasi if not
        (notifikasi.jenis_referensi == jenis_referensi and notifikasi.id_objek == id_objek)]

        nasabah.notifikasi.append(notifikasi_baru)

        return True

    @staticmethod
    def hapus_notifikasi_referensi(
            nasabah,
            jenis_referensi,
            id_objek
    ):
        koneksi = buat_koneksi()

        try:
            jumlah_baris = (
                NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                    nik_pemilik=nasabah.NIK,
                    jenis_referensi=jenis_referensi,
                    id_objek=id_objek,
                    koneksi=koneksi
                )
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        nasabah.notifikasi = [
            notifikasi
            for notifikasi in nasabah.notifikasi
            if not (
                    notifikasi.jenis_referensi == jenis_referensi
                    and notifikasi.id_objek == id_objek
            )
        ]
        return jumlah_baris

    @staticmethod
    def buat_notifikasi_persetujuan_pinjaman(
            id_pinjaman,
            nik_pemilik,
            koneksi
    ):
        notifikasi = Notifikasi(
            jenis="pinjaman",
            pesan=(
                f"Pengajuan pinjaman ber-ID {id_pinjaman} "
                f"telah disetujui."
            ),
            jenis_referensi=JenisReferensiID.PINJAMAN,
            id_objek=id_pinjaman
        )

        id_notifikasi = NotifikasiRepository.tambah_notifikasi(nik_pemilik,notifikasi,koneksi)

        notifikasi.ID = id_notifikasi







    @staticmethod
    def buat_notifikasi_penolakan_pinjaman(
            id_pinjaman,
            nik_pemilik,
            koneksi,
            catatan_admin
    ):
        notifikasi = Notifikasi(
            jenis="pinjaman",
            pesan=(
                f"Pengajuan pinjaman ber-ID {id_pinjaman} "
                f"telah ditolak.\n"
                f"catatan Admin: {catatan_admin}"

            ),
            jenis_referensi=JenisReferensiID.PINJAMAN,
            id_objek=id_pinjaman
        )

        id_notifikasi = NotifikasiRepository.tambah_notifikasi(nik_pemilik,notifikasi,koneksi)

        notifikasi.ID = id_notifikasi


