import datetime

from bank_djago.services.nasabah_menu import NasabahMenu
from bank_djago.services.rekening.rekening_ui import RekeningUI
from bank_djago.services.scheduler import Scheduler
# from bank_djago.utils.debug import Debug
from penyimpanan.storage import JsonStorage
from bank_djago.utils.utility import Utilitas
from bank_djago.services.admin.menu_admin import MenuAdmin
from bank_djago.services.rekening.rekening_service import RekeningService


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








#

# #
# #
# #
# #
# #


#

from bank_djago.penyimpanan.storage import JsonStorage
from bank_djago.utils.utility import StatusPinjaman
from bank_djago.utils.tests.test_pinjaman import (
    siapkan_dua_pinjaman_untuk_uji
)
from bank_djago.utils.tests.cek_integritas import (
    cek_integritas_pinjaman
)

def uji_integritas_pinjaman():
    # Memuat dataset utama sebagai objek bank.
    bank = JsonStorage.muat_bank()

    # Helper ini membutuhkan satu pinjaman aktif.
    # Pinjaman tersebut akan dilunasi, lalu dibuatkan
    # pinjaman aktif baru untuk nasabah yang sama.
    nasabah, pinjaman_lunas, pinjaman_aktif = (
        siapkan_dua_pinjaman_untuk_uji(bank)
    )

    # Memastikan dataset pengujian benar-benar siap.
    pinjaman_milik_nasabah = [
        pinjaman
        for pinjaman in bank.daftar_pinjaman
        if pinjaman.pemilik is nasabah
    ]

    assert pinjaman_lunas in pinjaman_milik_nasabah, (
        "Pinjaman lunas tidak ditemukan dalam daftar bank"
    )

    assert pinjaman_aktif in pinjaman_milik_nasabah, (
        "Pinjaman aktif tidak ditemukan dalam daftar bank"
    )

    assert pinjaman_lunas.status == StatusPinjaman.LUNAS, (
        "Pinjaman lama belum berstatus lunas"
    )

    assert pinjaman_aktif.status == StatusPinjaman.AKTIF, (
        "Pinjaman baru belum berstatus aktif"
    )

    assert nasabah.pinjaman is pinjaman_aktif, (
        "Nasabah tidak menunjuk pinjaman aktif"
    )

    # Menjalankan pemeriksaan umum seluruh relasi pinjaman.
    daftar_error = cek_integritas_pinjaman(bank)

    if daftar_error:
        print("\nMASALAH INTEGRITAS PINJAMAN:")

        for nomor, error in enumerate(daftar_error, start=1):
            print(f"{nomor}. {error}")

        raise AssertionError(
            f"Ditemukan {len(daftar_error)} masalah integritas"
        )

    print()
    print("RINGKASAN PENGUJIAN")
    print("Nasabah          :", nasabah.nama)
    print("Jumlah historis  :", len(pinjaman_milik_nasabah))
    print("Pinjaman lunas   :", pinjaman_lunas.ID)
    print("Pinjaman aktif   :", pinjaman_aktif.ID)
    print("Referensi aktif  :", nasabah.pinjaman.ID)
    print()
    print("✅ Integritas pinjaman tidak menemukan masalah")

if __name__=="__main__":
    uji_integritas_pinjaman()




















