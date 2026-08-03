from datetime import datetime
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
        print("=" * 60)
        print("=" * 15, "SELAMAT DATANG DI BANK DJAGO", '=' * 15)
        print("=" * 60)
        print("PILIHAN MENU".center(60))
        print()
        print("1. Daftar dan Buka Rekening Pertama")
        print("2. Cek Saldo")
        print("3. Setor Tunai")
        print("4. Tarik Tunai")
        print("5. Transfer Saldo")
        print("6. Lihat Riwayat")
        print("7. Layanan Nasabah")
        print("8. Simpan dan Keluar")

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