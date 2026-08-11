from bank_djago.services.deposito.deposito_service import DepositoService
from bank_djago.utils.utililty import Utilitas
from bank_djago.utils.ui import UI


class NotifikasiUI:


    @staticmethod
    def menu(nasabah):
        while True :
            UI.header("CEK NOTIFIKASI",UI.BIRU)
            print()
            print("1. Notifikasi Deposito")
            print("2. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                NotifikasiUI.notif_depo(nasabah)
            elif pilihan == "2":
                break



    @staticmethod
    def notif_depo(nasabah):
        deposito = DepositoService.depo_jatuh_tempo(nasabah)
        if not deposito:
            print("Anda tidak memiliki notifikasi di deposito")
            return
        print(f"Anda memiliki {len(deposito)} yang telah jatuh tempo")
        print()
        for i,depo in enumerate(deposito,start=1):
            print(f"{i}. Deposito #{depo.ID}\n"
                  f"Nominal     : Rp{Utilitas.format_rupiah(depo.total_pencairan)}\n"
                  f"Jatuh tempo : {Utilitas.format_tanggal_indonesia(depo.jatuh_tempo)}\n"
                  f"ARO         : {depo.jenis_aro}\n")