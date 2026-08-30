from bank_djago.penyimpanan.repositories.notifikasi_repository import NotifikasiRepository
from bank_djago.utils.utility import JenisReferensiID
from bank_djago.core.notifikasi import Notifikasi

class NotifikasiLoader:


    @staticmethod
    def muat_notifikasi(nasabah):
        daftar_notifikasi = NotifikasiRepository.cari_notifikasi_nasabah(nasabah.NIK)

        for data_notif in daftar_notifikasi:
            jenis_referensi = (
                JenisReferensiID(data_notif["jenis_referensi"])
                if data_notif["jenis_referensi"] is not None
                else None
            )

            notifikasi = Notifikasi(jenis=data_notif["jenis"],
                                    pesan=data_notif["pesan"],
                                    jenis_referensi=jenis_referensi,
                                    id_objek=data_notif["id_objek"])

            nasabah.notifikasi.append(notifikasi)