import datetime
import secrets

from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis
from bank_djago.penyimpanan.repositories.sesi_repository import SesiRepository
from bank_djago.services.exceptions import StatusTidakValid, TokenKedaluwarsa, TokenTidakValid, PerbaruiStatusGagal
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository



class SesiService:
    MASA_BERLAKU_MENIT= 10




    @staticmethod
    def buat_sesi(nik, norek, pin):
        RekeningService.verifikasi_pin_rekening(nik_aktif=nik, norek_aktif=norek, pin_input=pin)

        with buat_koneksi_tulis() as koneksi:
            token = secrets.token_urlsafe(32)
            kadaluwarsa = datetime.datetime.now() + datetime.timedelta(minutes=SesiService.MASA_BERLAKU_MENIT)

            baris = SesiRepository.tambah_token(token=token, nik=nik, norek=norek, kadaluwarsa=kadaluwarsa, koneksi=koneksi)
            if baris != 1:
                raise StatusTidakValid("Gagal membuat token")
        return token, kadaluwarsa

    @staticmethod
    def cek_sesi(token):
        masalah = None

        with buat_koneksi_tulis() as koneksi:
            data_token = SesiRepository.cari_token(token=token, koneksi=koneksi)
            if data_token is None:
                raise TokenTidakValid("Token tidak ditemukan")

            if datetime.datetime.fromisoformat(data_token["kadaluwarsa"]) < datetime.datetime.now():
                masalah = TokenKedaluwarsa("Sesi telah berakhir, silakan login kembali")
            else:
                status = RekeningRepository.ambil_status_rekening(norek=data_token['norek'], nik=data_token['nik'],koneksi=koneksi)
                if status == "tutup":
                    masalah = StatusTidakValid("Rekening tidak aktif")

            if masalah is not None:
                baris = SesiRepository.hapus_token(token=token, koneksi=koneksi)
                if baris != 1:
                    raise PerbaruiStatusGagal("Gagal menghapus sesi")

        if masalah is not None:
            raise masalah

        return {"nik": data_token["nik"], "norek": data_token["norek"]}




