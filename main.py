from penyimpanan.storage import JSOnbase
from bank_djago.utils.utililty import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin
from bank_djago.services.admin.admin_teller import AdminTeller
from bank_djago.services.admin.admin_cs import AdminCs


def menu():

    bank = JSOnbase.muat_bank()
    bank.debug_bunga(10)
    bank.debug_admin(10)
    bank.proses_harian()
    while True:
        print()
        Utilitas.pilihan_menu()

        pilihan = int(input("Masukkan pilihan Anda: "))

        if pilihan == 1:
            AdminCs.buka_rekening(bank)

        elif pilihan == 2:
            bank.cek_saldo()

        elif pilihan == 3:
            AdminTeller.setor_tunai(bank)

        elif pilihan == 4:
            AdminTeller.tarik_tunai(bank)

        elif pilihan == 5:
            AdminTeller.transfer(bank)

        elif pilihan == 6:
            AdminTeller.lihat_riwayat(bank)

        elif pilihan == 7:
            AdminCs.layanan_nasabah(bank)

        elif pilihan == 8:
            MenuAdmin.menu(bank)

        elif pilihan == 9:
            JSOnbase.simpan_bank(bank)
            print("🙏 Terima Kasih Telah Mengunjungi Bank Djago!")
            break

if __name__ == '__main__':
    menu()
