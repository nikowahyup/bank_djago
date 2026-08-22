import datetime

from bank_djago.services.nasabah_menu import NasabahMenu
from bank_djago.services.rekening.rekening_ui import RekeningUI
from bank_djago.services.scheduler import Scheduler
# from bank_djago.utils.debug import Debug
from penyimpanan.storage import JsonStorage
from bank_djago.utils.utility import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin


# def menu():
#
#     bank = JsonStorage.muat_bank()
#     hari_ini = datetime.date(2026,9,22)
#     Scheduler.jalankan(bank,hari_ini)
#
#     while True:
#         print()
#         pilihan = Utilitas.pilihan_menu()
#
#         if pilihan == "1":
#             RekeningUI.buka_rekening(bank)
#
#         elif pilihan == "2":
#             nasabah = NasabahMenu.login(bank)
#             NasabahMenu.menu_utama(bank,nasabah)
#
#         elif pilihan == "3":
#             JsonStorage.simpan_bank(bank)
#             print("🙏 Terima Kasih Telah Mengunjungi Bank Djago!")
#             break
#
#         elif pilihan == "0":
#             MenuAdmin.menu(bank)
#
# if __name__ == "__main__":
#     menu()







import datetime

from bank_djago.services.scheduler import Scheduler


def uji_scheduler_rekening_dua_kali(bank):
    # Mengambil satu rekening untuk pengujian.
    rekening = next(iter(bank.rekening_index.values()))

    hari_uji = datetime.date(2026, 10, 23)

    # Menyiapkan keadaan agar bunga dan biaya admin sudah jatuh tempo.
    rekening.dapat_bunga = datetime.date(2026, 9, 23)
    rekening.waktu_bayar_admin = datetime.date(2026, 9, 23)

    # Reset limit belum dilakukan pada hari pengujian.
    rekening.reset = datetime.date(2026, 10, 22)
    rekening.limit_sisa = 1

    # Memastikan saldo cukup untuk menerima bunga dan membayar admin.
    rekening.set_saldo(100_000_000)

    print("SEBELUM SCHEDULER")
    print("Saldo             :", rekening.saldo)
    print("Dapat bunga       :", rekening.dapat_bunga)
    print("Bayar admin       :", rekening.waktu_bayar_admin)
    print("Reset limit       :", rekening.reset)
    print("Limit tersisa     :", rekening.limit_sisa)

    # Pemanggilan pertama harus memproses ketiga kegiatan.
    Scheduler.jalankan(bank, hari_uji)

    saldo_setelah_pertama = rekening.saldo
    bunga_setelah_pertama = rekening.dapat_bunga
    admin_setelah_pertama = rekening.waktu_bayar_admin
    reset_setelah_pertama = rekening.reset
    limit_setelah_pertama = rekening.limit_sisa
    jumlah_riwayat_setelah_pertama = len(rekening.riwayat)

    print()
    print("SETELAH PEMANGGILAN PERTAMA")
    print("Saldo             :", saldo_setelah_pertama)
    print("Dapat bunga       :", bunga_setelah_pertama)
    print("Bayar admin       :", admin_setelah_pertama)
    print("Reset limit       :", reset_setelah_pertama)
    print("Limit tersisa     :", limit_setelah_pertama)
    print("Jumlah riwayat    :", jumlah_riwayat_setelah_pertama)

    # Pemanggilan kedua menggunakan tanggal yang sama.
    Scheduler.jalankan(bank, hari_uji)

    print()
    print("SETELAH PEMANGGILAN KEDUA")
    print("Saldo             :", rekening.saldo)
    print("Dapat bunga       :", rekening.dapat_bunga)
    print("Bayar admin       :", rekening.waktu_bayar_admin)
    print("Reset limit       :", rekening.reset)
    print("Limit tersisa     :", rekening.limit_sisa)
    print("Jumlah riwayat    :", len(rekening.riwayat))

    # Pemanggilan kedua tidak boleh mengubah saldo.
    assert rekening.saldo == saldo_setelah_pertama, (
        "Saldo berubah ketika scheduler dipanggil ulang pada hari yang sama"
    )

    # Ketiga penanda waktu tidak boleh bergerak lagi.
    assert rekening.dapat_bunga == bunga_setelah_pertama, (
        "Bunga diberikan lebih dari sekali"
    )

    assert rekening.waktu_bayar_admin == admin_setelah_pertama, (
        "Biaya admin dipotong lebih dari sekali"
    )

    assert rekening.reset == reset_setelah_pertama, (
        "Limit direset lebih dari sekali"
    )

    assert rekening.limit_sisa == limit_setelah_pertama, (
        "Jumlah limit berubah pada pemanggilan kedua"
    )

    # Tidak boleh ada riwayat rekening baru dari pemanggilan kedua.
    assert len(rekening.riwayat) == jumlah_riwayat_setelah_pertama, (
        "Scheduler menambahkan riwayat lagi pada pemanggilan kedua"
    )

    # Memastikan ketiga jadwal sudah diproses menuju tanggal yang benar.
    assert rekening.dapat_bunga == hari_uji, (
        "Penanda bunga tidak sampai pada periode yang diharapkan"
    )

    assert rekening.waktu_bayar_admin == hari_uji, (
        "Penanda biaya admin tidak sampai pada periode yang diharapkan"
    )

    assert rekening.reset == hari_uji, (
        "Tanggal reset limit tidak sesuai hari pengujian"
    )

    assert rekening.limit_sisa == rekening.limit_harian, (
        "Limit tersisa tidak dikembalikan ke limit harian"
    )

    print()
    print("✅ Bunga hanya diberikan satu kali")
    print("✅ Biaya admin hanya dipotong satu kali")
    print("✅ Limit hanya direset satu kali")
    print("✅ Scheduler rekening bersifat idempoten")

bank = JsonStorage.muat_bank()

if __name__=="__main__":
    uji_scheduler_rekening_dua_kali(bank)








