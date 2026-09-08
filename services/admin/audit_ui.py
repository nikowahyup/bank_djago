

from bank_djago.services.admin.audit_structure import STRUKTUR_AUDIT
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.utils.ui import UI
from bank_djago.utils.utility import Utilitas

class AuditUI:



    @staticmethod
    def pilih_filter_audit():

        kategori = None
        objek = None
        aksi = None

        # =========================
        # PILIH KATEGORI
        # =========================

        kategori_list = list(
            STRUKTUR_AUDIT.keys()
        )

        UI.header("PILIH KATEGORI",UI.MERAH)
        print()

        for nomor, item in enumerate(
            kategori_list,
            start=1
        ):
            print(
                f"{nomor}. {item.title()}"
            )

        print("0. Keluar\n")

        while True:

            pilihan = input(
                "Pilih kategori: "
            ).strip()

            if pilihan == "0":
                return None

            if not pilihan.isdigit():
                UI.peringatan(
                    "Pilihan harus berupa angka"
                )
                continue

            pilihan = int(pilihan)

            if pilihan < 1 or pilihan > len(kategori_list):
                UI.peringatan(
                    "Pilihan tidak tersedia"
                )
                continue

            kategori = kategori_list[
                pilihan - 1
                ]

            break

        # =========================
        # PILIH OBJEK
        # =========================

        objek_list = list(
            STRUKTUR_AUDIT[
                kategori
            ].keys()
        )

        UI.header("PILIH OBJEK",UI.MERAH)
        print()
        for nomor, item in enumerate(
            objek_list,
            start=1
        ):
            print(
                f"{nomor}. {item.title()}"
            )

        nomor_semua = len(objek_list) + 1

        print(
            f"{nomor_semua}. Semua Objek"
        )
        print("0. Keluar")
        print()

        while True:

            pilihan = input(
                "Pilih objek: "
            ).strip()


            if pilihan == "0":
                return None

            if not pilihan.isdigit():
                UI.peringatan(
                    "Pilihan harus berupa angka"
                )
                continue

            pilihan = int(pilihan)

            if pilihan < 1 or pilihan > nomor_semua:
                UI.peringatan(
                    "Pilihan tidak tersedia"
                )
                continue

            if pilihan == nomor_semua:
                return kategori, None, None

            objek = objek_list[
                pilihan - 1
            ]
            break

        # =========================
        # PILIH AKSI
        # =========================

        aksi_list = STRUKTUR_AUDIT[
            kategori
        ][objek]

        UI.header("PILIH AKSI",UI.MERAH)

        for nomor, item in enumerate(
            aksi_list,
            start=1
        ):
            nama_aksi = item.replace(
                "_",
                " "
            ).title()

            print(
                f"{nomor}. {nama_aksi}"
            )

        nomor_semua = len(aksi_list) + 1

        print(
            f"{nomor_semua}. Semua Aksi"
        )
        print("0. Keluar")


        while True:

            pilihan = input(
                "Pilih aksi: "
            ).strip()

            if pilihan == "0":
                return None

            if not pilihan.isdigit():
                UI.peringatan(
                    "Pilihan harus berupa angka"
                )
                continue

            pilihan = int(pilihan)

            if pilihan < 1 or pilihan > nomor_semua:
                UI.peringatan(
                    "Pilihan tidak tersedia"
                )
                continue

            if pilihan == nomor_semua:
                return kategori, objek, None

            aksi = aksi_list[
                pilihan - 1
            ]
            return kategori, objek, aksi

    @staticmethod
    def menu_tampilkan_audit():

        filter_audit = AuditUI.pilih_filter_audit()

        if filter_audit is None:
            return

        kategori, objek, aksi = filter_audit

        data_audit = AuditService.cari_audit(
            kategori=kategori,
            objek=objek,
            aksi=aksi
        )
        AuditUI.tampilkan_audit(data_audit)

    @staticmethod
    def tampilkan_audit(data_audit):

        if not data_audit:
            print()
            UI.peringatan(
                "Tidak ada data audit yang ditemukan"
            )
            return

        print()
        UI.header(
            "DATA AUDIT",
            UI.MERAH
        )
        print()

        for audit in data_audit:

            print("-" * 70)

            print(
                "Waktu       :",
                Utilitas.format_waktu(
                    audit["waktu"]
                )
            )

            print(
                "Kategori    :",
                audit["kategori"]
                .replace("_", " ")
                .title()
            )

            print(
                "Objek       :",
                audit["objek"]
                .replace("_", " ")
                .title()
            )

            print(
                "Aksi        :",
                audit["aksi"]
                .replace("_", " ")
                .title()
            )

            print(
                "Log         :",
                audit["log"]
            )

            if audit["nama"] is not None:
                print(
                    "Nama        :",
                    audit["nama"]
                )

            if audit["nik"] is not None:
                print(
                    "NIK         :",
                    audit["nik"]
                )

            if audit["norek"] is not None:
                print(
                    "No. Rekening:",
                    audit["norek"]
                )

            if audit["transaksi_id"] is not None:
                print(
                    "ID Transaksi:",
                    audit["transaksi_id"]
                )

        print("-" * 70)
        print()