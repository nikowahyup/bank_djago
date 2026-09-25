from bank_djago.penyimpanan.repositories.notifikasi_repository import (
    NotifikasiRepository,
)
from bank_djago.penyimpanan.sqlite.database import (
    buat_koneksi,
    buat_koneksi_baca,
    buat_koneksi_tulis,
)
from bank_djago.core.notifikasi import Notifikasi
from bank_djago.utils.utility import JenisReferensi


class NotifikasiService:

    @staticmethod
    def simpan_notifikasi_referensi(
        nasabah, jenis, pesan, jenis_referensi, id_objek, koneksi
    ):

        notifikasi_lama = NotifikasiRepository.cari_notifikasi_dengan_referensi(
            nik_pemilik=nasabah.NIK,
            jenis_referensi=jenis_referensi,
            id_objek=id_objek,
            koneksi=koneksi,
        )

        if notifikasi_lama is not None and notifikasi_lama["pesan"] == pesan:
            return False

        if notifikasi_lama is not None:
            NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                nik_pemilik=nasabah.NIK,
                jenis_referensi=jenis_referensi,
                id_objek=id_objek,
                koneksi=koneksi,
            )

        notifikasi_baru = Notifikasi(
            jenis=jenis, pesan=pesan, jenis_referensi=jenis_referensi, id_objek=id_objek
        )

        NotifikasiRepository.tambah_notifikasi(
            nik_pemilik=nasabah.NIK, notifikasi=notifikasi_baru, koneksi=koneksi
        )

        return True

    @staticmethod
    def hapus_notifikasi_referensi(nasabah, jenis_referensi, id_objek):
        koneksi = buat_koneksi()

        try:
            jumlah_baris = NotifikasiRepository.hapus_notifikasi_dengan_referensi(
                nik_pemilik=nasabah.NIK,
                jenis_referensi=jenis_referensi,
                id_objek=id_objek,
                koneksi=koneksi,
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
    def buat_notifikasi_persetujuan_pinjaman(id_pinjaman, nik_pemilik, koneksi):
        notifikasi = Notifikasi(
            jenis="pinjaman",
            pesan=(f"Pengajuan pinjaman ID {id_pinjaman} " f"telah disetujui."),
            jenis_referensi=JenisReferensi.PINJAMAN,
            id_objek=id_pinjaman,
        )

        NotifikasiRepository.tambah_notifikasi(nik_pemilik, notifikasi, koneksi)

    @staticmethod
    def buat_notifikasi_penolakan_pinjaman(
        id_pinjaman, nik_pemilik, koneksi, catatan_admin
    ):
        notifikasi = Notifikasi(
            jenis="pinjaman",
            pesan=(
                f"Pengajuan pinjaman ber-ID {id_pinjaman} "
                f"telah ditolak.\n"
                f"catatan Admin: {catatan_admin}"
            ),
            jenis_referensi=JenisReferensi.PINJAMAN,
            id_objek=id_pinjaman,
        )

        NotifikasiRepository.tambah_notifikasi(nik_pemilik, notifikasi, koneksi)

    @staticmethod
    def _normalisasi_data_notifikasi(daftar_notifikasi):
        hasil_normalisasi = []

        for data_notif in daftar_notifikasi:
            data_notif = dict(data_notif)
            data_notif["jenis_referensi"] = JenisReferensi.dari_nilai(
                data_notif["jenis_referensi"]
            )

            hasil_normalisasi.append(data_notif)

        return hasil_normalisasi

    @staticmethod
    def cari_semua_notifikasi_belum_dibaca(nik):
        with buat_koneksi_baca() as koneksi:
            daftar_notifikasi = NotifikasiRepository.cari_notifikasi_belum_dibaca(
                nik=nik, koneksi=koneksi
            )

        return NotifikasiService._normalisasi_data_notifikasi(
            daftar_notifikasi=daftar_notifikasi
        )

    @staticmethod
    def tandai_sudah_dibaca(daftar_notifikasi):

        for data_notif in daftar_notifikasi:
            try:
                with buat_koneksi_tulis() as koneksi:
                    NotifikasiRepository.tandai_sudah_dibaca(
                        id_notifikasi=data_notif["id"], koneksi=koneksi
                    )

            except Exception:
                continue
