from bank_djago.utils.utililty import Utilitas,UI
class RekapBank:

    @staticmethod
    def menu_tampilkan_rekap(bank):
        while True:
            Utilitas.menu_admin()
            pilihan = input("Masukkan pilihan: ")
            if pilihan == "1":
                total_nasabah,total_rekening,total_saldo = bank.rekap_umum()
                RekapBank.umum(total_nasabah,total_rekening, total_saldo)

            elif pilihan == "2":
                reguler,prioritas,gold,platinum = bank.rekap_jumlah_rekening()
                RekapBank.rekap_rekening(reguler,prioritas,gold, platinum)

            elif pilihan == "3":
                aktif,blokir,tutup = bank.rekap_status_rekening()
                RekapBank.rekap_status(aktif,blokir,tutup)

            elif pilihan == "4":
                reguler,prioritas,gold,platinum = bank.total_saldo_tiap_rekening()
                RekapBank.total_saldo_tiap_rekening(reguler, prioritas, gold, platinum)

            elif pilihan == "5":
                saldo_terbesar = bank.saldo_terbesar()
                RekapBank.saldo_terbesar(saldo_terbesar)

            elif pilihan == "6":
                saldo_terkecil = bank.saldo_terkecil()
                RekapBank.saldo_terkecil(saldo_terkecil)

            elif pilihan == "7":
                break

    @staticmethod
    def umum(total_nasabah,total_rekening,total_saldo):

        print("="*18,"REKAP UMUM","="*18)
        print()
        print(f"👤 Total Nasabah  : {total_nasabah}")
        print(f"💳 Total Rekening : {total_rekening}")
        print(f"💰 Total Saldo    : Rp{Utilitas.format_rupiah(total_saldo)}\n")



    @staticmethod
    def rekap_rekening(reguler,prioritas,gold,platinum):
        print("="*15,"REKAP REKENING","="*15)
        print()
        print(f"{UI.kelas[1]} Rekening Reguler   : {reguler}")
        print(f"{UI.kelas[2]} Rekening Prioritas : {prioritas}")
        print(f"{UI.kelas[3]} Rekening Gold      : {gold}")
        print(f"{UI.kelas[4]} Rekening Platinum  : {platinum}\n")


    @staticmethod
    def rekap_status(aktif,blokir,tutup):
        print("="*12,"REKAP STATUS REKENING","="*12)
        print()
        print(f"✅ Rekening Aktif  : {aktif}")
        print(f"⚠️ Rekening Blokir : {blokir}")
        print(f"❌ Rekening Tutup  : {tutup}\n")

    @staticmethod
    def total_saldo_tiap_rekening(reguler,prioritas,gold,platinum):
        print("="*12,"REKAP SALDO TIAP REKENING","="*12)
        print()
        print(f"{UI.kelas[1]} Rekening Reguler   : Rp{Utilitas.format_rupiah(reguler)}")
        print(f"{UI.kelas[2]} Rekening Prioritas : Rp{Utilitas.format_rupiah(prioritas)}")
        print(f"{UI.kelas[3]} Rekening Gold      : Rp{Utilitas.format_rupiah(gold)}")
        print(f"{UI.kelas[4]} Rekening Platinum  : Rp{Utilitas.format_rupiah(platinum)}\n")

    @staticmethod
    def saldo_terbesar(rekening_terbesar):
        print("="*12,"PEMILIK SALDO TERBESAR","="*12)
        print()
        print(f'{rekening_terbesar.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terbesar.saldo)}\n")



    @staticmethod
    def saldo_terkecil(rekening_terkecil):
        print("="*12,"PEMILIK SALDO TERKECIL","="*12)
        print()
        print(f'{rekening_terkecil.pemilik.nama}')
        print(f"Total Saldo : Rp{Utilitas.format_rupiah(rekening_terkecil.saldo)}\n")