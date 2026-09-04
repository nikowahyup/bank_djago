


from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import JenisReferensi


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
                NotifikasiUI.lihat_notifikasi(nasabah)

            elif pilihan == "2":
                NotifikasiUI.tampilkan_berdasarkan_referensi(nasabah,JenisReferensi.DEPOSITO)

            elif pilihan == "3":
                NotifikasiUI.tampilkan_berdasarkan_referensi(nasabah,JenisReferensi.PINJAMAN)


            elif pilihan == "4":
                break

    @staticmethod
    def lihat_notifikasi(nasabah):
        print(f"BANYAKNYA NOTIFIKASI {len(nasabah.notifikasi)}")
        if not nasabah.notifikasi:
            print("Tidak ada notifikasi.")
            return

        for i, item in enumerate(nasabah.notifikasi, start=1):
            print(f"{i}. {item.pesan}")

    @staticmethod
    def tampilkan_berdasarkan_referensi(nasabah, referensi_id):

        daftar = [
            item
            for item in nasabah.notifikasi
            if item.referensi_id == referensi_id
        ]

        if not daftar:
            print("Tidak ada notifikasi.")
            return

        for i, item in enumerate(daftar, start=1):
            print(f"{i}. {item.pesan}")


