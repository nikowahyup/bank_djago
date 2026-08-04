from penyimpanan.storage import JSOnbase
from bank_djago.utils.utililty import Utilitas



def menu():


    bank = JSOnbase.muat_bank()
    # bank.debug_bunga(10)
    # bank.debug_admin(10)
    bank.proses_harian()
    while True:
        print()
        Utilitas.pilihan_menu()

        pilihan = int(input("Masukkan pilihan Anda: "))

        if pilihan == 1:
            bank.daftar_nasabah()

        elif pilihan == 2:
            bank.cek_saldo()

        elif pilihan == 3:
            bank.setor_tunai()

        elif pilihan == 4:
            bank.tarik_tunai()
        elif pilihan == 5:
            bank.transfer()

        elif pilihan == 6:
            bank.lihat_riwayat()

        elif pilihan == 7:
            bank.layanan_nasabah()

        elif pilihan == 8:
            JSOnbase.simpan_bank(bank)
            print("🙏 Terima Kasih Telah Mengunjungi Bank Djago!")
            break
        elif pilihan == 9:
            bank.rekap()
        elif pilihan == 10:
            bank.lihat_audit()

if __name__ == '__main__':
    menu()
