import sqlite3

from bank_djago.services.pinjaman.pinjaman_service import  PinjamanService
from bank_djago.utils.utility import Utilitas,StatusPinjaman
from bank_djago.utils.ui import UI


class PinjamanUI:

    BATAL = object()

    @staticmethod
    def menu(nik ,norek):
        while True:

            UI.header("MENU PINJAMAN",UI.BIRU)
            print()
            print("1. Ajukan Pinjaman")
            print("2. Cairkan Pinjaman")
            print("3. Lihat Status Pinjaman")
            print("4. Bayar Cicilan")
            print("5. Keluar\n")
            pilihan = input("Masukkan pilihan Anda: ")
            if pilihan == "1":
                PinjamanUI.ajukan_pinjaman(nik=nik, norek=norek)

            elif pilihan == "2":
                PinjamanUI.cairkan_pinjaman(nik=nik, norek=norek)

            elif pilihan == "3":
                PinjamanUI.lihat_pinjaman(nik=nik)

            elif pilihan == "4":
                PinjamanUI.bayar_cicilan(nik=nik, norek=norek)

            elif pilihan == "5":
                break





    @staticmethod
    def ajukan_pinjaman(nik, norek):
        UI.header("AJUKAN PINJAMAN", UI.MERAH)
        print()

        try:
            nominal = int(input("Masukkan nominal pinjaman: "))
        except ValueError:
            UI.gagal("Masukkan nominal yang valid")
            return

        print("Pilihan Tenor dan Bunga\n")

        for tenor, bunga in PinjamanService.TENOR.items():
            print(
                f"{tenor} bulan dengan bunga "
                f"{round(bunga * 100)}% / tahun"
            )

        print()

        while True:
            try:
                tenor = int(input("Masukkan pilihan bulan: "))

                if tenor not in PinjamanService.TENOR:
                    UI.gagal("Pilihan tidak tersedia")
                    continue

            except ValueError:
                UI.gagal("Tolong pilih menggunakan angka")
                continue
            break

        try:
            id_pinjaman = PinjamanService.ajukan_pinjaman(
                nik=nik,
                norek=norek,
                nominal=nominal,
                tenor=tenor
            )
            UI.sukses(
                f"Pengajuan berhasil! ID pinjaman : {id_pinjaman}\n"
                f"Mohon tunggu persetujuan admin untuk mencairkan pinjaman"
            )

        except ValueError as e:
            UI.gagal(str(e))







    @staticmethod
    def cairkan_pinjaman(nik, norek):
        data_pinjaman = (
            PinjamanUI.pilih_pinjaman(
                nik=nik,
                norek=norek,
                status=StatusPinjaman.DISETUJUI
            )
        )
        if data_pinjaman is PinjamanUI.BATAL:
            return

        if data_pinjaman is None:
            UI.gagal("Nomor rekening ini tidak memiliki pinjaman yang disetujui")
            return

        try:

            PinjamanService.cairkan_pinjaman(
                nik=nik,
                id_pinjaman=data_pinjaman['id']
            )
            UI.sukses(
                f"Pinjaman {data_pinjaman['id']} berhasil dicairkan"
            )

            UI.sukses(
                f"Rp{Utilitas.format_rupiah(data_pinjaman['nominal_pinjaman'])} telah masuk "
                f"ke rekening {data_pinjaman['norek']}"
                    )
        except ValueError as e:
            UI.gagal(str(e))






    @staticmethod
    def bayar_cicilan(nik, norek):
        data_pinjaman = (
            PinjamanUI.pilih_pinjaman(
                nik=nik,
                norek=norek,
                status=StatusPinjaman.AKTIF
            )
        )

        if data_pinjaman is PinjamanUI.BATAL:
            return

        if data_pinjaman is None:
            UI.gagal("Nomor rekening ini tidak memiliki pinjaman aktif")
            return

        print()
        print(f"ID pinjaman   : {data_pinjaman['id']}")
        print(
            f"Cicilan tetap : "
            f"Rp{Utilitas.format_rupiah(data_pinjaman['cicilan_tetap'])}"
        )
        print(
            "Denda keterlambatan akan ditambahkan jika ada."
        )
        print()

        konfirmasi = input(
            "Lanjutkan pembayaran cicilan? (ya/tidak): "
        ).strip().lower()

        if konfirmasi not in ("y", "ya", "iya"):
            UI.gagal("Pembayaran cicilan dibatalkan")
            return

        try:
            hasil = PinjamanService.bayar_cicilan(
                nik=nik,
                norek_pembayaran=norek,
                id_pinjaman=data_pinjaman['id']
            )
            UI.sukses(f"Pembayaran cicilan pinjaman"
                      f" {hasil['id_pinjaman']} berhasil")

            if hasil['status'] == StatusPinjaman.LUNAS:
                UI.sukses("Seluruh cicilan pinjaman telah lunas")
            else:
                print(
                    "Cicilan selanjutnya bisa dibayar mulai: "
                    f"{Utilitas.format_tanggal_indonesia(
                        hasil['tanggal_bayar_selanjutnya']
                    )}"
                )

        except ValueError as e:
            UI.gagal(str(e))

        except sqlite3.Error as e:
            UI.gagal(f"Terjadi kesalahan saat pembayaran: {e}")



    @staticmethod
    def pilih_pinjaman(nik,norek=None,status=None):

        if norek is not None:

            daftar_pinjaman = (
                PinjamanService.cari_semua_pinjaman_dengan_norek(
                    norek=norek,
                    status=status
                )
            )
        else:
            daftar_pinjaman = (
                PinjamanService.cari_pinjaman_nasabah(nik=nik)
            )

        if not daftar_pinjaman:
            return None



        print("===== SILAHKAN PILIH PINJAMAN =====")
        print()
        for nomor, data_pinjaman in enumerate(daftar_pinjaman, start=1):
            print(f"{nomor}.")
            print(f"Rekening    : {data_pinjaman['norek']}")
            print(f"Status      : {data_pinjaman['status'].value}")
            print(f"ID pinjaman : {data_pinjaman['id']}")
            print(
                f"Nominal     : "
                f"Rp{Utilitas.format_rupiah(data_pinjaman['nominal_pinjaman'])}"
            )
            print(f"Tenor       : {data_pinjaman['tenor']} bulan")
            print(f"Bunga       : {data_pinjaman['bunga'] * 100:.1f}% / tahun")
            print()


        while True:
            try:
                pilihan = int(
                    input(
                        "Pilih nomor pinjaman "
                        "(ketik 0 untuk keluar): "
                    )
                )
            except ValueError:
                UI.gagal("Silakan pilih menggunakan angka")
                continue

            if pilihan == 0:
                return PinjamanUI.BATAL

            if pilihan < 1 or pilihan > len(daftar_pinjaman):
                UI.gagal("Nomor pilihan tidak tersedia")
                continue

            return daftar_pinjaman[pilihan - 1]



    @staticmethod
    def lihat_pinjaman(nik):
        data_pinjaman = PinjamanUI.pilih_pinjaman(nik=nik)

        if data_pinjaman is PinjamanUI.BATAL:
            return

        if data_pinjaman is None:
            UI.gagal("Anda masih belum memiliki pinjaman")
            return

        def buat_baris(label, nilai):
            return f"{label:<17}: {nilai}"

        baris_informasi = [
            buat_baris("ID pinjaman", data_pinjaman['id']),

            buat_baris(
                "Nominal awal",
                f"Rp{Utilitas.format_rupiah(
                    data_pinjaman['nominal_pinjaman']
                )}"
            ),
            buat_baris(
                "Bunga",
                f"{data_pinjaman['bunga'] * 100:.1f}% / tahun"
            ),
            buat_baris(
                "Tenor",
                f"{data_pinjaman['tenor']} bulan"
            ),
            buat_baris(
                "Status",
                data_pinjaman['status'].value
            )
        ]

        if data_pinjaman['status'] == StatusPinjaman.DIAJUKAN:
            baris_informasi.append(
                buat_baris(
                    "Keterangan",
                    "Menunggu pemeriksaan admin"
                )
            )

        elif data_pinjaman['status'] == StatusPinjaman.DISETUJUI:
            baris_informasi.append(
                buat_baris(
                    "Keterangan",
                    "Pinjaman siap dicairkan"
                )
            )

        elif data_pinjaman['status'] == StatusPinjaman.DITOLAK:
            baris_informasi.append(
                buat_baris(
                    "Keterangan",
                    "Pengajuan pinjaman ditolak"
                )
            )

        elif data_pinjaman['status'] == StatusPinjaman.AKTIF:
            baris_informasi.extend([
                buat_baris(
                    "Cicilan tetap",
                    f"Rp{Utilitas.format_rupiah(
                    data_pinjaman['cicilan_tetap']
                    )}"
                ),
                buat_baris(
                    "Cicilan dibayar",
                    f"{data_pinjaman['cicilan_terbayar']}/{data_pinjaman['tenor']}"
                ),
                buat_baris(
                    "Sisa pokok",
                    f"Rp{Utilitas.format_rupiah(
                        data_pinjaman['sisa_pokok']
                    )}"
                ),
                buat_baris(
                    "Tanggal cair",
                    Utilitas.format_tanggal_indonesia(
                        data_pinjaman['tanggal_pencairan'])

                ),
                buat_baris(
                    "Jatuh tempo",
                    Utilitas.format_tanggal_indonesia(
                        data_pinjaman['tanggal_jatuh_tempo']
                    )
                )
            ])

        elif data_pinjaman['status'] == StatusPinjaman.LUNAS:
            baris_informasi.extend([
                buat_baris(
                    "Cicilan tetap",
                    f"Rp{Utilitas.format_rupiah(
                        data_pinjaman['cicilan_tetap']
                    )}"
                ),
                buat_baris(
                    "Cicilan dibayar",
                    f"{data_pinjaman['cicilan_terbayar']}/{data_pinjaman['tenor']}"
                ),
                buat_baris(
                    "Sisa pokok",
                    f"Rp{Utilitas.format_rupiah(
                        data_pinjaman['sisa_pokok']
                    )}"
                ),
                buat_baris(
                    "Tanggal cair",
                    Utilitas.format_tanggal_indonesia(
                        data_pinjaman['tanggal_pencairan'])

                ),
                buat_baris(
                    "Keterangan",
                    "Seluruh cicilan telah dibayar"
                )
            ])

        lebar_isi = max(
            len(baris)
            for baris in baris_informasi
        )

        print()
        print("╔" + "═" * (lebar_isi + 2) + "╗")

        for baris in baris_informasi:
            print(f"║ {baris:<{lebar_isi}} ║")

        print("╚" + "═" * (lebar_isi + 2) + "╝")









