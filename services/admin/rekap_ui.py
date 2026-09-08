from bank_djago.services.admin.rekap_bank_service import RekapService
from bank_djago.utils.utility import Utilitas,UI


class RekapUI:

    @staticmethod
    def menu_tampilkan_rekap():
        while True:
            Utilitas.menu_admin()
            pilihan = input("Masukkan pilihan: ")
            if pilihan == "1":
                total_nasabah,total_rekening,total_saldo = RekapService.rekap_umum()
                RekapUI.rekap_umum(total_nasabah,total_rekening, total_saldo)

            elif pilihan == "2":
                reguler,prioritas,gold,platinum = RekapService.rekap_jumlah_rekening()
                RekapUI.rekap_rekening(reguler,prioritas,gold, platinum)

            elif pilihan == "3":
                aktif,blokir,tutup = RekapService.rekap_status_rekening()
                RekapUI.rekap_status(aktif,blokir,tutup)

            elif pilihan == "4":
                reguler,prioritas,gold,platinum = RekapService.total_saldo_rekening()
                RekapUI.total_saldo_tiap_rekening(reguler, prioritas, gold, platinum)

            elif pilihan == "5":
                saldo_terbesar = RekapService.saldo_terbesar()
                RekapUI.saldo_besar(saldo_terbesar)

            elif pilihan == "6":
                saldo_terkecil = RekapService.saldo_terkecil()
                RekapUI.saldo_kecil(saldo_terkecil)

            elif pilihan == "7":
                break


    @staticmethod
    def rekap_umum(total_nasabah,total_rekening,total_saldo):

        UI.header("REKAP UMUM",UI.MERAH)
        print()
        print(f"👤 Total Nasabah  : {total_nasabah}")
        print(f"💳 Total Rekening : {total_rekening}")
        print(f"💰 Total Saldo    : Rp{Utilitas.format_rupiah(total_saldo)}\n")


    @staticmethod
    def rekap_rekening(reguler,prioritas,gold,platinum):
        UI.header("REKAP REKENING",UI.MERAH)
        print()
        print(f"{UI.kelas[1]} Rekening Reguler   : {reguler}")
        print(f"{UI.kelas[2]} Rekening Prioritas : {prioritas}")
        print(f"{UI.kelas[3]} Rekening Gold      : {gold}")
        print(f"{UI.kelas[4]} Rekening Platinum  : {platinum}\n")


    @staticmethod
    def rekap_status(aktif,blokir,tutup):
        UI.header("REKAP STATUS REKENING",UI.MERAH)
        print()
        print(f"✅ Rekening Aktif  : {aktif}")
        print(f"⚠️ Rekening Blokir : {blokir}")
        print(f"❌ Rekening Tutup  : {tutup}\n")

    @staticmethod
    def total_saldo_tiap_rekening(reguler,prioritas,gold,platinum):
        UI.header("REKAP SALDO TIAP REKENING",UI.MERAH)
        print()
        print(f"{UI.kelas[1]} Rekening Reguler   : Rp{Utilitas.format_rupiah(reguler)}")
        print(f"{UI.kelas[2]} Rekening Prioritas : Rp{Utilitas.format_rupiah(prioritas)}")
        print(f"{UI.kelas[3]} Rekening Gold      : Rp{Utilitas.format_rupiah(gold)}")
        print(f"{UI.kelas[4]} Rekening Platinum  : Rp{Utilitas.format_rupiah(platinum)}\n")

    @staticmethod
    def saldo_besar(rekening_terbesar):
        UI.header("PEMILIK SALDO TERBESAR")
        print()
        if rekening_terbesar is None:
            UI.gagal("Belum ada data rekening pemilik saldo terbesar")
            return
        print(f"Nama pemilik : {rekening_terbesar['nama']}")
        print(f"Jumlah saldo : Rp{Utilitas.format_rupiah(rekening_terbesar['saldo'])}")

    @staticmethod
    def saldo_kecil(rekening_terkecil):
        UI.header("PEMILIK SALDO TERKECIL")
        print()
        if rekening_terkecil is None:
            UI.gagal("Belum ada rekening pemilik saldo terkecil")
            return
        print(f"Nama pemilik : {rekening_terkecil['nama']}")
        print(f"Jumlah saldo : Rp{Utilitas.format_rupiah(rekening_terkecil['saldo'])}")

