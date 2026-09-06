
from bank_djago.services.pinjaman.pinjaman_service import  PinjamanService
from bank_djago.utils.utility import Utilitas,StatusPinjaman
from bank_djago.utils.ui import UI


class PinjamanUI:

    @staticmethod
    def menu(nasabah, rekening):
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
                PinjamanUI.ajukan_pinjaman(nasabah, rekening)

            elif pilihan == "2":
                PinjamanUI.cairkan_pinjaman(nasabah)

            elif pilihan == "3":
                PinjamanUI.lihat_pinjaman(nasabah)

            elif pilihan == "4":
                PinjamanUI.bayar_cicilan(nasabah)

            elif pilihan == "5":
                break





    @staticmethod
    def ajukan_pinjaman(nasabah, rekening):
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
            PinjamanService.ajukan_pinjaman(

                nasabah=nasabah,
                rekening=rekening,
                nominal=nominal,
                tenor=tenor
            )

            UI.sukses(
                "Pengajuan telah dikirim. "
                "Mohon tunggu dan lihat status pinjaman "
                "di menu lihat pinjaman"
            )

        except ValueError as e:
            UI.gagal(str(e))



    @staticmethod
    def cairkan_pinjaman(nasabah):
        pinjaman = PinjamanUI.pilih_pinjaman(nasabah,StatusPinjaman.DISETUJUI)

        if pinjaman is None:
            return

        try:
            PinjamanService.cairkan_pinjaman(nasabah=nasabah,id_pinjaman=pinjaman.ID)
            UI.sukses(f"Pinjaman {pinjaman.ID} berhasil dicairkan")

            UI.sukses(
                f"Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)} telah masuk ke rekening Anda"
                    )
        except ValueError as e:
            UI.gagal(str(e))



    @staticmethod
    def pilih_pinjaman(nasabah,status=None):
        daftar_pinjaman = nasabah.daftar_pinjaman
        if status is not None:
            daftar_pinjaman = [pinjaman
                               for pinjaman in daftar_pinjaman
                               if pinjaman.status == status]

        if not daftar_pinjaman:
            if status is not None:
                UI.gagal(f"Tidak ada pinjaman berstatus {status.value}")
            else:
                UI.gagal("Anda belum memiiliki pinjaman")
            return None




        print("===== SILAHKAN PILIH PINJAMAN =====")
        print()
        for nomor, pinjaman in enumerate(daftar_pinjaman, start=1):
            print(f"{nomor}.")
            print(f"Status      : {pinjaman.status.value}")
            print(f"ID pinjaman : {pinjaman.ID}")
            print(
                f"Nominal     : "
                f"Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}"
            )
            print(f"Tenor       : {pinjaman.tenor} bulan")
            print(f"Bunga       : {pinjaman.bunga * 100:.1f}% / tahun")
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
                return None

            if pilihan < 1 or pilihan > len(daftar_pinjaman):
                UI.gagal("Nomor pilihan tidak tersedia")
                continue

            return daftar_pinjaman[pilihan - 1]

    @staticmethod
    def lihat_pinjaman(nasabah):
        pinjaman = PinjamanUI.pilih_pinjaman(nasabah=nasabah)

        if pinjaman is None:
            return

        # Semua label diberi ruang selebar 17 karakter.
        # Dengan demikian, seluruh titik dua berada di kolom yang sama.
        def buat_baris(label, nilai):
            return f"{label:<17}: {nilai}"

        baris_informasi = [
            buat_baris("ID pinjaman", pinjaman.ID),
            buat_baris(
                "Nominal awal",
                f"Rp{Utilitas.format_rupiah(
                    pinjaman.nominal_pinjaman
                )}"
            ),
            buat_baris(
                "Bunga",
                f"{pinjaman.bunga * 100:.1f}% / tahun"
            ),
            buat_baris(
                "Tenor",
                f"{pinjaman.tenor} bulan"
            ),
            buat_baris(
                "Status",
                pinjaman.status.value
            )
        ]

        if pinjaman.status == StatusPinjaman.DIAJUKAN:
            baris_informasi.append(
                buat_baris(
                    "Keterangan",
                    "Menunggu pemeriksaan admin"
                )
            )

        elif pinjaman.status == StatusPinjaman.DISETUJUI:
            baris_informasi.append(
                buat_baris(
                    "Keterangan",
                    "Pinjaman siap dicairkan"
                )
            )

        elif pinjaman.status == StatusPinjaman.DITOLAK:
            baris_informasi.append(
                buat_baris(
                    "Keterangan",
                    "Pengajuan pinjaman ditolak"
                )
            )

        elif pinjaman.status == StatusPinjaman.AKTIF:
            baris_informasi.extend([
                buat_baris(
                    "Cicilan tetap",
                    f"Rp{Utilitas.format_rupiah(
                        pinjaman.cicilan_tetap
                    )}"
                ),
                buat_baris(
                    "Cicilan dibayar",
                    f"{pinjaman.cicilan_terbayar}/{pinjaman.tenor}"
                ),
                buat_baris(
                    "Sisa pokok",
                    f"Rp{Utilitas.format_rupiah(
                        pinjaman.sisa_pokok
                    )}"
                ),
                buat_baris(
                    "Tanggal cair",
                    Utilitas.format_tanggal_indonesia(
                        pinjaman.tanggal_pencairan
                    )
                ),
                buat_baris(
                    "Jatuh tempo",
                    Utilitas.format_tanggal_indonesia(
                        pinjaman.tanggal_jatuh_tempo
                    )
                )
            ])

        elif pinjaman.status == StatusPinjaman.LUNAS:
            baris_informasi.extend([
                buat_baris(
                    "Cicilan tetap",
                    f"Rp{Utilitas.format_rupiah(
                        pinjaman.cicilan_tetap
                    )}"
                ),
                buat_baris(
                    "Cicilan dibayar",
                    f"{pinjaman.cicilan_terbayar}/{pinjaman.tenor}"
                ),
                buat_baris(
                    "Sisa pokok",
                    f"Rp{Utilitas.format_rupiah(
                        pinjaman.sisa_pokok
                    )}"
                ),
                buat_baris(
                    "Tanggal cair",
                    Utilitas.format_tanggal_indonesia(
                        pinjaman.tanggal_pencairan
                    )
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


    @staticmethod
    def bayar_cicilan(nasabah):
        pinjaman = PinjamanUI.pilih_pinjaman(nasabah=nasabah,status=StatusPinjaman.AKTIF)

        if pinjaman is None:
            return

        print()
        print(f"ID pinjaman   : {pinjaman.ID}")
        print(
            f"Cicilan tetap : "
            f"Rp{Utilitas.format_rupiah(pinjaman.cicilan_tetap)}"
        )
        print("Denda keterlambatan akan ditambahkan jika ada.")
        print()

        konfirmasi = input(
            "Lanjutkan pembayaran cicilan? (ya/tidak): "
        ).strip().lower()

        if konfirmasi not in ("y", "ya", "iya"):
            UI.gagal("Pembayaran cicilan dibatalkan")
            return

        try:
            pinjaman = PinjamanService.bayar_cicilan(nasabah=nasabah,id_pinjaman=pinjaman.ID)
            UI.sukses(f"Pembayaran cicilan pinjaman {pinjaman.ID} berhasil")
            if pinjaman.status == StatusPinjaman.LUNAS:
                UI.sukses("Seluruh cicilan pinjaman telah lunas")
            else:
                print(
                    "Jatuh tempo berikutnya: "
                    f"{Utilitas.format_tanggal_indonesia(
                        pinjaman.tanggal_jatuh_tempo
                    )}"
                )

        except ValueError as e:
            UI.gagal(str(e))







