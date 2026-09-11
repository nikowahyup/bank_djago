from bank_djago.services.notifikasi_service import NotifikasiService
from bank_djago.utils.utility import JenisReferensi
from bank_djago.utils.utility import UI


class NotifikasiUI:


    @staticmethod
    def menu(nasabah):
        while True :
            UI.header("CEK NOTIFIKASI",UI.BIRU)
            print()
            print("1. Semua Notifikasi ")
            print("2. Notifikasi Deposito")
            print("3. Notifikasi Pinjaman")
            print("4. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                NotifikasiUI.tampilkan_notifikasi(nasabah)

            elif pilihan == "2":
                NotifikasiUI.tampilkan_notifikasi(nasabah,JenisReferensi.DEPOSITO)

            elif pilihan == "3":
                NotifikasiUI.tampilkan_notifikasi(nasabah,JenisReferensi.PINJAMAN)


            elif pilihan == "4":
                break




    @staticmethod
    def filter_notifikasi(nasabah,jenis_referensi=None):

        if jenis_referensi is None:
            return [
                notifikasi for notifikasi in
                nasabah.notifikasi if not notifikasi.sudah_dibaca
            ]

        return [
            notifikasi
            for notifikasi in nasabah.notifikasi
            if (
                notifikasi.jenis_referensi == jenis_referensi
                and not notifikasi.sudah_dibaca
            )
        ]


    @staticmethod
    def tampilkan_notifikasi(nasabah,jenis_referensi=None):

        daftar_notif = NotifikasiUI.filter_notifikasi(
            nasabah=nasabah,
            jenis_referensi=jenis_referensi
        )

        if not daftar_notif:
            UI.gagal("Belum ada notifikasi terbaru")
            return

        for nomor,notifikasi in enumerate(daftar_notif,start=1):
            print()
            print(f"{nomor}. {notifikasi.pesan}")

        NotifikasiService.tandai_sudah_dibaca(daftar_notifikasi=daftar_notif)


