import datetime
from bank_djago.utils.utililty import Utilitas
class BiayaAdminService:


    @staticmethod
    def potong_admin(rekening):

        hari_ini = datetime.date.today()

        bulan = (
                (hari_ini.year - rekening.waktu_bayar_admin.year) * 12
                + hari_ini.month
                - rekening.waktu_bayar_admin.month
        )

        if hari_ini.day < rekening.waktu_bayar_admin.day:
            bulan -= 1

        if bulan <= 0:
            return

        total_admin = rekening.biaya_admin * bulan

        rekening.kurangi_saldo(total_admin)

        rekening.waktu_bayar_admin = hari_ini

        simpan = {
            "kategori":"sistem",
            "jenis": "biaya admin",
            "waktu": datetime.datetime.now().isoformat(),
            "log": f"BIAYA ADMIN | Jumlah Rp{total_admin:,}".replace(",", ".")
        }
        rekening.simpan_riwayat(simpan)


class AdminService:

    @staticmethod
    def rekap_bank(bank):
        while True:
            print("="*15,"MENU ADMIN","="*15)
            print()
            print('1. Lihat Rekap Umum')
            print('2. Lihat Rekap Rekening')
            print('3. Lihat Rekap Status Rekening')
            print('4. Lihat Rekap Total Saldo')
            print('5. Lihat Rekap Saldo Terbesar')
            print('6. Lihat Rekap Saldo Terkecil')
            print()
            pilihan = input("Pilihan Kamu: ")

            if pilihan == "1":
                bank.rekap_umum()
            elif pilihan == "2":
                bank.rekap_jumlah_rekening()
            elif pilihan == "3":
                bank.rekap_status_rekening()
            elif pilihan == "4":
                bank.total_saldo_tiap_rekening()
            elif pilihan =="5":
                bank.saldo_terbesar()
            elif pilihan =="6":
                bank.saldo_terkecil()
            elif pilihan == "7":
                break


    @staticmethod
    def umum(total_nasabah,total_rekening,total_saldo):

        print("="*20,"REKAP UMUM","="*20)
        print(f"👤 Total Nasabah  : {total_nasabah}")
        print(f"💳 Total Rekening : {total_rekening}")
        print(f"💰 Total Saldo    : Rp{Utilitas.format_rupiah(total_saldo)}")



    @staticmethod
    def rekap_rekening(reguler,prioritas,gold,platinum):
        print("="*20,"REKAP REKENING","="*20)
        print(f"Rekening Reguler   : {reguler}")
        print(f"Rekening Prioritas : {prioritas}")
        print(f"Rekening Gol       : {gold}")
        print(f"Rekening Platinum  : {platinum}")


    @staticmethod
    def rekap_status(aktif,blokir,tutup):

        print("="*20,"REKAP STATUS REKENING","="*20)
        print(f"✅ Rekening Aktif  : {aktif}")
        print(f"⚠️ Rekening Blokir : {blokir}")
        print(f"❌ Rekening Tutup  : {tutup}")

    @staticmethod
    def total_saldo_tiap_rekening(reguler,prioritas,gold,platinum):
        print("="*20,"REKAP SALDO TIAP REKENING","="*20)
        print(f"Rekening Reguler   : Rp{Utilitas.format_rupiah(reguler)}")
        print(f"Rekening Prioritas : Rp{Utilitas.format_rupiah(prioritas)}")
        print(f"Rekening Gold      : Rp{Utilitas.format_rupiah(gold)}")
        print(f"Rekening Platinum  : Rp{Utilitas.format_rupiah(platinum)}")

    @staticmethod
    def saldo_terbesar(rekening_terbesar):
        print("="*20,"PEMILIK SALDO TERBESAR","="*20)
        print(f'{rekening_terbesar.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terbesar.saldo)}")



    @staticmethod
    def saldo_terkecil(rekening_terkecil):
        print("="*20,"PEMILIK SALDO TERKECIL","="*20)
        print(f'{rekening_terkecil.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terkecil.saldo)}")
