from bank_djago.penyimpanan.repositories.notifikasi_repository import NotifikasiRepository
from bank_djago.utils.utility import JenisReferensi
from bank_djago.core.notifikasi import Notifikasi

class NotifikasiLoader:


    @staticmethod
    def muat_notifikasi(nasabah):
        daftar_notifikasi = NotifikasiRepository.cari_notifikasi_nasabah(nasabah.NIK)

        daftar_notifikasi_baru = []

        for data_notif in daftar_notifikasi:
            jenis_referensi = (
                JenisReferensi.dari_nilai(data_notif["jenis_referensi"])
                if data_notif["jenis_referensi"] is not None
                else None
            )

            notifikasi = Notifikasi(jenis=data_notif["jenis"],
                                    pesan=data_notif["pesan"],
                                    jenis_referensi=jenis_referensi,
                                    id_objek=data_notif["id_objek"],
                                    sudah_dibaca=bool(data_notif['sudah_dibaca'])
                                    )

            notifikasi.ID = data_notif['id']


            daftar_notifikasi_baru.append(notifikasi)

        nasabah.notifikasi = daftar_notifikasi_baru