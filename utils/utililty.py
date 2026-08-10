from datetime import datetime
import time
from bank_djago.utils.ui import UI



class Utilitas:

    @staticmethod
    def sapaan(nasabah,rekening):
        format_rek = f'{rekening.norek[0:4]}-{rekening.norek[4:8]}-{rekening.norek[8:12]}-{rekening.norek[12:16]}'
        print("="*41)
        print("SELAMAT DATANG DI BANK DJAGO".center(40))
        print("="*41,'\n')
        print("Pendaftaran Berhasil!🎉\n")
        print(f'👋 Halo,{nasabah.nama}.')
        print('Terima kasih telah mempercayai Bank Djago.\n')
        print("Informasi tentang rekening pertama Anda\n")
        print(f"Jenis rekening : {rekening.jenis}")
        print(f"Nomor rekening : {format_rek}\n")
        print("Simpan nomor rekening dan PIN Anda dengan baik.\n")

    @staticmethod
    def format_rupiah(nominal):
        rupiah = f"{nominal:,}".replace(",",'.')
        return rupiah


    @staticmethod
    def pilihan_menu():
        while True:
            UI.header("SIMULASI BANK DJAGO", warna=UI.HIJAU)
            print()
            print("1. Daftar dan Buka Rekening")
            print("2. Login Nasabah")
            print("0. Menu Admin")
            print("3. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")

            return pilihan



        print()

    def debug_bunga(self, bulan=1):
        for rekening in self.rekening_index.values():
            rekening.dapat_bunga -= datetime.timedelta(days=bulan * 31)

    @staticmethod
    def nama_bulan(tanggal):
        BULAN = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"
        }

        return BULAN[tanggal.month]

    @staticmethod
    def format_waktu(iso):
        BULAN = {
            1: "Januari",
            2: "Februari",
            3: "Maret",
            4: "April",
            5: "Mei",
            6: "Juni",
            7: "Juli",
            8: "Agustus",
            9: "September",
            10: "Oktober",
            11: "November",
            12: "Desember"
        }
        waktu = datetime.fromisoformat(iso)

        return (
            f"{waktu.day:02d} "
            f"{BULAN[waktu.month]} "
            f"{waktu.year} | "
            f"{waktu.strftime('%H:%M:%S')}"
        )

    @staticmethod
    def keuntungan_rekening():
        print(f"{'1. REGULER':<40}{'2. PRIORITAS'}")
        print(f"{'-'*15:<40}{'-'*15}")
        print(f"{'- Saldo Min : Rp500.000':<40}{'- Saldo Min : Rp3.000.000'}")
        print(f"{'- Setoran awal : Rp500.000':<40}{'- Setoran awal : Rp3.000.000'}")
        print(f"{'- Bunga     : 3%/tahun':<40}{'- Bunga     : 5%/tahun'}")
        print(f"{'- Admin     : Rp2.000/bulan':<40}{'- Admin     : Rp5.000/bulan'}")
        print(f"{'- Limit transfer : Rp5.000.000/hari':<39}{' - Limit transfer : Rp15.000.0000/hari'}")
        print()

        print(f"{'3. GOLD':<40}{'4. PLATINUM'}")
        print(f"{'-'*15:<40}{'-'*15}")
        print(f"{'- Saldo Min : Rp50.000.000':<40}{'- Saldo Min : Rp200.000.000'}")
        print(f"{'- Setoran awal : Rp50.000.000':<40}{'- Setoran awal : Rp200.000.000'}")
        print(f"{'- Bunga     : 7%/tahun':<40}{'- Bunga     : 10%/tahun'}")
        print(f"{'- Admin     : Rp10.000/bulan':<40}{'- Admin     : Rp20.000/bulan'}")
        print(f"{'- Limit transfer : Rp200.000.000/hari':<39}{' - Limit transfer : Tidak Terbatas'}")

    @staticmethod
    def info_rekening(rekening):
        print("="*30)
        print(f"👋 Halo,{rekening.pemilik.nama}!")
        print(f'🏦 Rekening : {rekening.jenis}')
        print(f"💳 No.Rek   : {rekening.norek}")
        print(f"💰 Saldo    : Rp{rekening.cek_saldo()}")
        print("="*30)

    @staticmethod
    def waktu_sekarang():
        return datetime.now().isoformat()

    @staticmethod
    def menu_admin():
        UI.header("MENU REKAP",UI.KUNING)
        print()
        print('1. Lihat Rekap Umum')
        print('2. Lihat Rekap Rekening')
        print('3. Lihat Rekap Status Rekening')
        print('4. Lihat Rekap Total Saldo')
        print('5. Lihat Rekap Saldo Terbesar')
        print('6. Lihat Rekap Saldo Terkecil')
        print("7. Keluar")

        print()

    @staticmethod
    def menu_audit():
        print()
        UI.header('MENU AUDIT',UI.KUNING)
        print()
        print('1. Semua Aktivitas')
        print('2. Aktivitas Transaksi')
        print('3. Aktivitas Rekening')
        print('4. Aktivitas Nasabah')
        print('5. Keluar\n')

    level = {1: 'Reguler',
             2: 'Prioritas',
             3: 'Gold',
             4: 'Platinum'}

    @staticmethod
    def menu_cs():
        print("1. Buka Rekening")
        print("2. Tingkatkan Rekening")
        print("3. Turunkan Rekening")
        print("4. Blokir Rekening")
        print("5. Buka Blokir Rekening")
        print("6. Reset PIN")
        print("7. Tutup Rekening")
        print("8. Keluar")

    @staticmethod
    def tambah_bulan(tanggal,bulan):
        import datetime
        import calendar
        bulan_baru = tanggal.month + bulan

        tahun = tanggal.year + (bulan_baru-1)//12
        bulan = (bulan_baru - 1)%12 + 1
        hari = min(tanggal.day,calendar.monthrange(tahun,bulan)[1])

        return datetime.date(tahun,bulan,hari)

    @staticmethod
    def animasi(pencarian):
        print(f"{pencarian}", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(1)
        print()

class JenisAro:
    TIDAK = "tidak"
    POKOK = "pokok"
    POKOK_BUNGA = "pokok_bunga"



