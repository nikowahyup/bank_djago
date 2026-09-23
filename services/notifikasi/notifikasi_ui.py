from bank_djago.services.notifikasi.notifikasi_service import NotifikasiService
from bank_djago.utils.utility import JenisReferensi
from bank_djago.utils.utility import UI


class NotifikasiUI:


    @staticmethod
    def menu(nik):
        while True :
            UI.header("CEK NOTIFIKASI",UI.BIRU)
            print()
            print("1. Semua Notifikasi ")
            print("2. Notifikasi Deposito")
            print("3. Notifikasi Pinjaman")
            print("4. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                NotifikasiUI.tampilkan_notifikasi(nik=nik)

            elif pilihan == "2":
                NotifikasiUI.tampilkan_notifikasi(nik=nik,jenis_referensi=JenisReferensi.DEPOSITO)

            elif pilihan == "3":
                NotifikasiUI.tampilkan_notifikasi(nik=nik,jenis_referensi=JenisReferensi.PINJAMAN)


            elif pilihan == "4":
                break


    @staticmethod
    def filter_notifikasi(nik, jenis_referensi=None):
        daftar_notifikasi = NotifikasiService.cari_semua_notifikasi_belum_dibaca(nik=nik)

        if jenis_referensi is not None:
            daftar_notifikasi = [data_notif for data_notif in daftar_notifikasi if data_notif['jenis_referensi'] == jenis_referensi]

        return daftar_notifikasi

    @staticmethod
    def tampilkan_notifikasi(nik, jenis_referensi=None):

        daftar_notif = NotifikasiUI.filter_notifikasi(nik=nik, jenis_referensi=jenis_referensi)

        if not daftar_notif:
            UI.gagal("Belum ada notifikasi terbaru")
            return

        for nomor,data_notif in enumerate(daftar_notif,start=1):
            print()
            print(f"{nomor}. {data_notif['pesan']}")
            print(f"Untuk nomor rekening  {data_notif['norek']}")

        NotifikasiService.tandai_sudah_dibaca(daftar_notifikasi=daftar_notif)


