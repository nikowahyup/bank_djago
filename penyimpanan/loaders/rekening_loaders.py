# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
import datetime
from bank_djago.core.nasabah import Nasabahh
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository



class RekeningLoader:


    @staticmethod
    def muat_rekening(norek:str,koneksi) -> "Rekening | None":
        from bank_djago.services.rekening.rekening_service import RekeningService

        data_rekening = RekeningRepository.cari_rekening_dengan_norek(
            norek,
            koneksi
        )


        if data_rekening is None:
            return None


        data_nasabah = NasabahRepository.cari_nasabah_dengan_nik(data_rekening["nik_pemilik"],koneksi)


        if data_nasabah is None:
            return None

        nasabah = Nasabahh(nama=data_nasabah["nama"],alamat=data_nasabah["alamat"],nik=data_nasabah["nik"])

        level = data_rekening["level"]
        if level not in RekeningService.jenis_rekening:
            raise ValueError("Jenis rekening tidak terdaftar")
        info = RekeningService.jenis_rekening[data_rekening["level"]]
        kelas = info["kelas"]
        rekening = kelas(norek=data_rekening["norek"],
                             pin=data_rekening["pin"],
                             pemilik=nasabah)

        rekening.set_saldo(data_rekening["saldo"])
        rekening.reset = datetime.date.fromisoformat(data_rekening["reset"])
        rekening.status = data_rekening["status"]
        rekening.waktu_bayar_admin = datetime.date.fromisoformat(data_rekening["waktu_bayar_admin"])
        rekening.dapat_bunga = datetime.date.fromisoformat(data_rekening["dapat_bunga"])
        rekening.alasan_blokir = data_rekening["alasan_blokir"]
        rekening.limit_sisa = data_rekening["limit_sisa"]

        terakhir_ubah = data_rekening["terakhir_ubah_rekening"]
        rekening.terakhir_ubah_rekening = datetime.date.fromisoformat(terakhir_ubah) if terakhir_ubah is not None else None


        return rekening

    @staticmethod
    def muat_semua_rekening(nasabah):
        from bank_djago.services.rekening.rekening_service import RekeningService
        daftar_rekening = RekeningRepository.cari_rekening_dengan_nik(nasabah.NIK)

        if not daftar_rekening:
            return

        for data in daftar_rekening:
            level = data["level"]
            if level not in RekeningService.jenis_rekening:
                raise ValueError("Jenis rekening tidak tersedia")

            kelas = RekeningService.jenis_rekening[level]["kelas"]

            rekening = kelas(norek=data["norek"],
                             pin=data["pin"],
                             pemilik=nasabah)

            rekening.set_saldo(data["saldo"])
            rekening.reset = datetime.date.fromisoformat(data["reset"])
            rekening.status = data["status"]
            rekening.waktu_bayar_admin = datetime.date.fromisoformat(data["waktu_bayar_admin"])
            rekening.dapat_bunga = datetime.date.fromisoformat(data["dapat_bunga"])
            rekening.alasan_blokir = data["alasan_blokir"]
            rekening.limit_sisa = data["limit_sisa"]

            terakhir_ubah = data["terakhir_ubah_rekening"]
            rekening.terakhir_ubah_rekening = datetime.date.fromisoformat(
                terakhir_ubah) if terakhir_ubah is not None else None

            nasabah.rekening.append(rekening)
