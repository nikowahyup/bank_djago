# # # import datetime
# # #
# # # from bank_djago.penyimpanan.loaders.pinjaman_loader import (
# # #     PinjamanLoader
# # # )
# # # from bank_djago.services.pinjaman.pinjaman_service import (
# # #     PinjamanService
# # # )
# # #
# # #
# # # ID_PINJAMAN = 10
# # #
# # # daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()
# # #
# # # pinjaman = next(
# # #     (
# # #         pinjaman
# # #         for pinjaman in daftar_pinjaman
# # #         if pinjaman.ID == ID_PINJAMAN
# # #     ),
# # #     None
# # # )
# # #
# # # if pinjaman is None:
# # #     raise AssertionError(
# # #         f"Pinjaman aktif ID {ID_PINJAMAN} tidak ditemukan"
# # #     )
# # #
# # # jatuh_tempo = pinjaman.tanggal_jatuh_tempo
# # # batas_toleransi = PinjamanService.BATAS_HARI_TUNGGAKAN
# # #
# # # skenario = [
# # #     {
# # #         "nama": "H-4 belum perlu pengingat",
# # #         "hari": jatuh_tempo - datetime.timedelta(days=4),
# # #         "teks_wajib": None
# # #     },
# # #     {
# # #         "nama": "H-3 mulai diingatkan",
# # #         "hari": jatuh_tempo - datetime.timedelta(days=3),
# # #         "teks_wajib": "3 hari"
# # #     },
# # #     {
# # #         "nama": "H-1 jatuh tempo besok",
# # #         "hari": jatuh_tempo - datetime.timedelta(days=1),
# # #         "teks_wajib": "1 hari"
# # #     },
# # #     {
# # #         "nama": "Hari jatuh tempo",
# # #         "hari": jatuh_tempo,
# # #         "teks_wajib": "Hari ini"
# # #     },
# # #     {
# # #         "nama": "Terlambat satu hari",
# # #         "hari": jatuh_tempo + datetime.timedelta(days=1),
# # #         "teks_wajib": "terlambat 1 hari"
# # #     },
# # #     {
# # #         "nama": "Hari terakhir toleransi",
# # #         "hari": (
# # #             jatuh_tempo
# # #             + datetime.timedelta(days=batas_toleransi)
# # #         ),
# # #         "teks_wajib": "hari terakhir masa toleransi"
# # #     },
# # #     {
# # #         "nama": "Hari pertama terkena denda",
# # #         "hari": (
# # #             jatuh_tempo
# # #             + datetime.timedelta(days=batas_toleransi + 1)
# # #         ),
# # #         "teks_wajib": "Denda telah berjalan selama 1 hari"
# # #     }
# # # ]
# # #
# # #
# # # print("=== PENGUJIAN PESAN PENGINGAT PINJAMAN ===")
# # # print("ID pinjaman :", pinjaman.ID)
# # # print("Jatuh tempo :", jatuh_tempo)
# # # print("Toleransi   :", batas_toleransi, "hari")
# # # print()
# # #
# # # for nomor, data_uji in enumerate(skenario, start=1):
# # #     pesan = PinjamanService.buat_pesan_pengingat(
# # #         pinjaman=pinjaman,
# # #         hari_ini=data_uji["hari"]
# # #     )
# # #
# # #     print(f"--- SKENARIO {nomor}: {data_uji['nama']} ---")
# # #     print("Hari simulasi :", data_uji["hari"])
# # #     print("Pesan         :", pesan)
# # #     print()
# # #
# # #     if data_uji["teks_wajib"] is None:
# # #         assert pesan is None, (
# # #             f"{data_uji['nama']} seharusnya belum menghasilkan pesan"
# # #         )
# # #
# # #     else:
# # #         assert pesan is not None, (
# # #             f"{data_uji['nama']} seharusnya menghasilkan pesan"
# # #         )
# # #
# # #         assert data_uji["teks_wajib"].lower() in pesan.lower(), (
# # #             f"Pesan skenario '{data_uji['nama']}' tidak sesuai.\n"
# # #             f"Teks yang dicari: {data_uji['teks_wajib']}\n"
# # #             f"Pesan aktual: {pesan}"
# # #         )
# # #
# # # print(
# # #     "✅ SELURUH CABANG PESAN BERHASIL: "
# # #     "H-4, H-3, H-1, jatuh tempo, toleransi, "
# # #     "dan denda menghasilkan pesan yang sesuai"
# # # )
# #
# #
# #
# # import datetime
# #
# # from bank_djago.penyimpanan.loaders.pinjaman_loader import (
# #     PinjamanLoader
# # )
# # from bank_djago.penyimpanan.repositories.notifikasi_repository import (
# #     NotifikasiRepository
# # )
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # from bank_djago.services.notifikasi_service import NotifikasiService
# # from bank_djago.services.pinjaman.pinjaman_service import (
# #     PinjamanService
# # )
# # from bank_djago.utils.utility import JenisReferensi
# #
# #
# # ID_PINJAMAN = 10
# #
# #
# # def ambil_notifikasi_pinjaman(nasabah, id_pinjaman):
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         return (
# #             NotifikasiRepository.cari_notifikasi_dengan_referensi(
# #                 nik_pemilik=nasabah.NIK,
# #                 jenis_referensi=JenisReferensi.PINJAMAN,
# #                 id_objek=id_pinjaman,
# #                 koneksi=koneksi
# #             )
# #         )
# #     finally:
# #         koneksi.close()
# #
# #
# # # Memuat pinjaman aktif beserta pemiliknya.
# # daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()
# #
# # pinjaman = next(
# #     (
# #         pinjaman
# #         for pinjaman in daftar_pinjaman
# #         if pinjaman.ID == ID_PINJAMAN
# #     ),
# #     None
# # )
# #
# # if pinjaman is None:
# #     raise AssertionError(
# #         f"Pinjaman aktif ID {ID_PINJAMAN} tidak ditemukan"
# #     )
# #
# # nasabah = pinjaman.pemilik
# # jatuh_tempo = pinjaman.tanggal_jatuh_tempo
# #
# # hari_h_minus_3 = (
# #     jatuh_tempo - datetime.timedelta(days=3)
# # )
# #
# # hari_h_minus_2 = (
# #     jatuh_tempo - datetime.timedelta(days=2)
# # )
# #
# #
# # print("=== KONDISI AWAL ===")
# # print("ID pinjaman :", pinjaman.ID)
# # print("NIK pemilik :", nasabah.NIK)
# # print("Jatuh tempo :", jatuh_tempo)
# # print()
# #
# #
# # # ============================================================
# # # 1. Simulasi scheduler pada H-3
# # # ============================================================
# #
# # pesan_h_minus_3 = PinjamanService.buat_pesan_pengingat(
# #     pinjaman=pinjaman,
# #     hari_ini=hari_h_minus_3
# # )
# #
# # assert pesan_h_minus_3 is not None, (
# #     "H-3 seharusnya menghasilkan pesan"
# # )
# #
# # hasil_pertama = (
# #     NotifikasiService.simpan_notifikasi_referensi(
# #         nasabah=nasabah,
# #         jenis="pinjaman",
# #         pesan=pesan_h_minus_3,
# #         jenis_referensi=JenisReferensi.PINJAMAN,
# #         id_objek=pinjaman.ID
# #     )
# # )
# #
# # notifikasi_h_minus_3 = ambil_notifikasi_pinjaman(
# #     nasabah=nasabah,
# #     id_pinjaman=pinjaman.ID
# # )
# #
# # assert hasil_pertama is True, (
# #     "Pemanggilan H-3 seharusnya menyimpan notifikasi"
# # )
# #
# # assert notifikasi_h_minus_3 is not None, (
# #     "Notifikasi H-3 tidak ditemukan di SQLite"
# # )
# #
# # assert notifikasi_h_minus_3["pesan"] == pesan_h_minus_3, (
# #     "Pesan H-3 yang tersimpan tidak sesuai"
# # )
# #
# # id_notifikasi_h_minus_3 = notifikasi_h_minus_3["id"]
# #
# # print("=== SETELAH PEMANGGILAN H-3 ===")
# # print("Hari simulasi  :", hari_h_minus_3)
# # print("ID notifikasi  :", id_notifikasi_h_minus_3)
# # print("Pesan          :", notifikasi_h_minus_3["pesan"])
# # print()
# #
# #
# # # ============================================================
# # # 2. Jalankan kembali pada tanggal yang sama
# # # ============================================================
# #
# # hasil_pengulangan = (
# #     NotifikasiService.simpan_notifikasi_referensi(
# #         nasabah=nasabah,
# #         jenis="pinjaman",
# #         pesan=pesan_h_minus_3,
# #         jenis_referensi=JenisReferensi.PINJAMAN,
# #         id_objek=pinjaman.ID
# #     )
# # )
# #
# # notifikasi_setelah_pengulangan = (
# #     ambil_notifikasi_pinjaman(
# #         nasabah=nasabah,
# #         id_pinjaman=pinjaman.ID
# #     )
# # )
# #
# # assert hasil_pengulangan is False, (
# #     "Pesan yang sama seharusnya tidak disimpan kembali"
# # )
# #
# # assert (
# #     notifikasi_setelah_pengulangan["id"]
# #     == id_notifikasi_h_minus_3
# # ), "Pemanggilan kedua membuat notifikasi baru"
# #
# # assert (
# #     notifikasi_setelah_pengulangan["pesan"]
# #     == pesan_h_minus_3
# # ), "Pesan berubah pada tanggal simulasi yang sama"
# #
# # print(
# #     "✅ Pemanggilan berulang tidak menggandakan notifikasi"
# # )
# # print()
# #
# #
# # # ============================================================
# # # 3. Simulasi scheduler pada H-2
# # # ============================================================
# #
# # pesan_h_minus_2 = PinjamanService.buat_pesan_pengingat(
# #     pinjaman=pinjaman,
# #     hari_ini=hari_h_minus_2
# # )
# #
# # assert pesan_h_minus_2 is not None, (
# #     "H-2 seharusnya menghasilkan pesan"
# # )
# #
# # assert pesan_h_minus_2 != pesan_h_minus_3, (
# #     "Pesan H-2 seharusnya berbeda dari pesan H-3"
# # )
# #
# # hasil_perubahan = (
# #     NotifikasiService.simpan_notifikasi_referensi(
# #         nasabah=nasabah,
# #         jenis="pinjaman",
# #         pesan=pesan_h_minus_2,
# #         jenis_referensi=JenisReferensi.PINJAMAN,
# #         id_objek=pinjaman.ID
# #     )
# # )
# #
# # notifikasi_h_minus_2 = ambil_notifikasi_pinjaman(
# #     nasabah=nasabah,
# #     id_pinjaman=pinjaman.ID
# # )
# #
# # assert hasil_perubahan is True, (
# #     "Pesan H-2 seharusnya mengganti pesan H-3"
# # )
# #
# # assert notifikasi_h_minus_2 is not None, (
# #     "Notifikasi H-2 tidak ditemukan"
# # )
# #
# # assert notifikasi_h_minus_2["pesan"] == pesan_h_minus_2, (
# #     "Pesan H-2 yang tersimpan tidak sesuai"
# # )
# #
# # assert (
# #     notifikasi_h_minus_2["jenis_referensi"]
# #     == JenisReferensi.PINJAMAN.value
# # ), "Jenis referensi notifikasi bukan pinjaman"
# #
# # assert notifikasi_h_minus_2["id_objek"] == pinjaman.ID, (
# #     "ID objek notifikasi tidak menunjuk pinjaman ID 10"
# # )
# #
# # print("=== SETELAH PEMANGGILAN H-2 ===")
# # print("Hari simulasi :", hari_h_minus_2)
# # print("ID notifikasi :", notifikasi_h_minus_2["id"])
# # print("Pesan         :", notifikasi_h_minus_2["pesan"])
# # print()
# #
# # print(
# #     "✅ INTEGRASI NOTIFIKASI BERHASIL: "
# #     "H-3 membuat notifikasi, pemanggilan berulang tidak "
# #     "menggandakan, dan H-2 mengganti pesan lama"
# # )
#
#
#
# import datetime
#
# from bank_djago.penyimpanan.loaders.pinjaman_loader import (
#     PinjamanLoader
# )
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.services.notifikasi_service import NotifikasiService
# from bank_djago.services.pinjaman.pinjaman_service import (
#     PinjamanService
# )
# from bank_djago.utils.utility import JenisReferensi
#
#
# ID_PINJAMAN_PERTAMA = 9
# ID_PINJAMAN_KEDUA = 10
#
#
# def ambil_notifikasi_pinjaman(nik_pemilik, daftar_id):
#     koneksi = buat_koneksi()
#
#     try:
#         placeholder = ", ".join("?" for _ in daftar_id)
#
#         return koneksi.execute(
#             f"""
#             SELECT
#                 id,
#                 nik_pemilik,
#                 jenis,
#                 pesan,
#                 jenis_referensi,
#                 id_objek
#             FROM notifikasi
#             WHERE nik_pemilik = ?
#               AND jenis_referensi = ?
#               AND id_objek IN ({placeholder})
#             ORDER BY id_objek
#             """,
#             (
#                 nik_pemilik,
#                 JenisReferensi.PINJAMAN.value,
#                 *daftar_id
#             )
#         ).fetchall()
#
#     finally:
#         koneksi.close()
#
#
# daftar_pinjaman_aktif = (
#     PinjamanLoader.muat_semua_pinjaman_aktif()
# )
#
# pinjaman_9 = next(
#     (
#         pinjaman
#         for pinjaman in daftar_pinjaman_aktif
#         if pinjaman.ID == ID_PINJAMAN_PERTAMA
#     ),
#     None
# )
#
# pinjaman_10 = next(
#     (
#         pinjaman
#         for pinjaman in daftar_pinjaman_aktif
#         if pinjaman.ID == ID_PINJAMAN_KEDUA
#     ),
#     None
# )
#
# assert pinjaman_9 is not None, (
#     "Pinjaman aktif ID 9 tidak ditemukan"
# )
#
# assert pinjaman_10 is not None, (
#     "Pinjaman aktif ID 10 tidak ditemukan"
# )
#
# # Keduanya seharusnya memakai objek nasabah yang sama
# # karena loader menggunakan nasabah_index.
# assert pinjaman_9.pemilik is pinjaman_10.pemilik, (
#     "Kedua pinjaman tidak menggunakan objek nasabah yang sama"
# )
#
# nasabah = pinjaman_9.pemilik
# daftar_id = [pinjaman_9.ID, pinjaman_10.ID]
#
#
# print("=== KONDISI PINJAMAN ===")
# print("NIK pemilik     :", nasabah.NIK)
# print("Pinjaman pertama:", pinjaman_9.ID)
# print("Jatuh tempo     :", pinjaman_9.tanggal_jatuh_tempo)
# print("Pinjaman kedua  :", pinjaman_10.ID)
# print("Jatuh tempo     :", pinjaman_10.tanggal_jatuh_tempo)
# print()
#
#
# # Membuat pesan H-3 berdasarkan jadwal masing-masing.
# for pinjaman in (pinjaman_9, pinjaman_10):
#     hari_simulasi = (
#         pinjaman.tanggal_jatuh_tempo
#         - datetime.timedelta(days=3)
#     )
#
#     pesan = PinjamanService.buat_pesan_pengingat(
#         pinjaman=pinjaman,
#         hari_ini=hari_simulasi
#     )
#
#     assert pesan is not None, (
#         f"Pinjaman ID {pinjaman.ID} tidak menghasilkan pesan H-3"
#     )
#
#     NotifikasiService.simpan_notifikasi_referensi(
#         nasabah=pinjaman.pemilik,
#         jenis="pinjaman",
#         pesan=pesan,
#         jenis_referensi=JenisReferensi.PINJAMAN,
#         id_objek=pinjaman.ID
#     )
#
#     print(f"Notifikasi pinjaman ID {pinjaman.ID} diproses")
#     print("Hari simulasi:", hari_simulasi)
#     print("Pesan        :", pesan)
#     print()
#
#
# # Membaca kembali hasil akhirnya langsung dari SQLite.
# notifikasi_sqlite = ambil_notifikasi_pinjaman(
#     nik_pemilik=nasabah.NIK,
#     daftar_id=daftar_id
# )
#
# print("=== NOTIFIKASI DI SQLITE ===")
#
# for data in notifikasi_sqlite:
#     print(
#         f"ID notifikasi {data['id']} | "
#         f"Pinjaman {data['id_objek']} | "
#         f"{data['pesan']}"
#     )
#
# assert len(notifikasi_sqlite) == 2, (
#     "Seharusnya terdapat tepat dua notifikasi pinjaman"
# )
#
# id_objek_sqlite = {
#     data["id_objek"]
#     for data in notifikasi_sqlite
# }
#
# assert id_objek_sqlite == {9, 10}, (
#     "Notifikasi tidak menunjuk pinjaman ID 9 dan 10"
# )
#
# for data in notifikasi_sqlite:
#     assert data["nik_pemilik"] == nasabah.NIK, (
#         "Notifikasi terhubung dengan nasabah yang salah"
#     )
#
#     assert (
#         data["jenis_referensi"]
#         == JenisReferensi.PINJAMAN.value
#     ), "Jenis referensi notifikasi tidak sesuai"
#
#
# # Objek nasabah juga seharusnya mempunyai kedua notifikasi.
# notifikasi_objek = [
#     notifikasi
#     for notifikasi in nasabah.notifikasi
#     if (
#         notifikasi.jenis_referensi
#         == JenisReferensi.PINJAMAN
#         and notifikasi.id_objek in daftar_id
#     )
# ]
#
# id_objek_python = {
#     notifikasi.id_objek
#     for notifikasi in notifikasi_objek
# }
#
# assert id_objek_python == {9, 10}, (
#     "Daftar notifikasi objek nasabah tidak memuat "
#     "pinjaman ID 9 dan 10"
# )
#
# print()
# print(
#     "✅ ISOLASI NOTIFIKASI BERHASIL: "
#     "pinjaman ID 9 dan 10 mempunyai notifikasi sendiri "
#     "tanpa saling menghapus"
# )



from bank_djago.core.notifikasi import Notifikasi
from bank_djago.penyimpanan.loaders.pinjaman_loader import (
    PinjamanLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)
from bank_djago.utils.utility import (
    JenisReferensi,
    StatusPinjaman
)


ID_PINJAMAN_DIBAYAR = 10
ID_PINJAMAN_DIPERTAHANKAN = 9


def ambil_snapshot(nik_pemilik):
    koneksi = buat_koneksi()

    try:
        data_pinjaman = koneksi.execute(
            """
            SELECT
                id,
                norek,
                status,
                cicilan_terbayar,
                sisa_pokok,
                tanggal_jatuh_tempo
            FROM pinjaman
            WHERE id = ?
            """,
            (ID_PINJAMAN_DIBAYAR,)
        ).fetchone()

        data_rekening = koneksi.execute(
            """
            SELECT norek, saldo
            FROM rekening
            WHERE norek = ?
            """,
            (data_pinjaman["norek"],)
        ).fetchone()

        daftar_notifikasi = koneksi.execute(
            """
            SELECT
                id,
                nik_pemilik,
                jenis,
                pesan,
                jenis_referensi,
                id_objek
            FROM notifikasi
            WHERE nik_pemilik = ?
              AND jenis_referensi = ?
              AND id_objek IN (?, ?)
            ORDER BY id_objek
            """,
            (
                nik_pemilik,
                JenisReferensi.PINJAMAN.value,
                ID_PINJAMAN_DIPERTAHANKAN,
                ID_PINJAMAN_DIBAYAR
            )
        ).fetchall()

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis_referensi = ?
              AND id_referensi = ?
              AND jenis = 'pembayaran_cicilan'
            """,
            (
                JenisReferensi.PINJAMAN.value,
                ID_PINJAMAN_DIBAYAR
            )
        ).fetchone()["jumlah"]

        return {
            "pinjaman": dict(data_pinjaman),
            "rekening": dict(data_rekening),
            "notifikasi": [
                dict(data)
                for data in daftar_notifikasi
            ],
            "jumlah_transaksi": jumlah_transaksi
        }

    finally:
        koneksi.close()


# Memuat graph objek pinjaman, nasabah, dan rekening.
daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()

pinjaman = next(
    (
        pinjaman
        for pinjaman in daftar_pinjaman
        if pinjaman.ID == ID_PINJAMAN_DIBAYAR
    ),
    None
)

if pinjaman is None:
    raise AssertionError(
        f"Pinjaman aktif ID {ID_PINJAMAN_DIBAYAR} "
        f"tidak ditemukan"
    )

nasabah = pinjaman.pemilik
rekening = pinjaman.rekening

snapshot_sebelum = ambil_snapshot(nasabah.NIK)

id_notifikasi_sebelum = {
    data["id_objek"]
    for data in snapshot_sebelum["notifikasi"]
}

assert id_notifikasi_sebelum == {9, 10}, (
    "Pengujian membutuhkan notifikasi pinjaman ID 9 dan 10"
)

assert (
    snapshot_sebelum["pinjaman"]["status"]
    == StatusPinjaman.AKTIF.value
), "Pinjaman ID 10 sudah tidak aktif"

assert (
    snapshot_sebelum["pinjaman"]["cicilan_terbayar"] == 0
), (
    "Pinjaman ID 10 sudah pernah dibayar. "
    "Jangan menjalankan pengujian ini kembali."
)


# Memuat dua notifikasi SQLite ke dalam objek nasabah.
# Ini membuat pemeriksaan state objek Python tidak bersifat semu.
nasabah.notifikasi = [
    Notifikasi(
        jenis=data["jenis"],
        pesan=data["pesan"],
        jenis_referensi=JenisReferensi(
            data["jenis_referensi"]
        ),
        id_objek=data["id_objek"]
    )
    for data in snapshot_sebelum["notifikasi"]
]


print("=== KONDISI SEBELUM PEMBAYARAN ===")
print("ID pinjaman        :", pinjaman.ID)
print(
    "Cicilan terbayar  :",
    snapshot_sebelum["pinjaman"]["cicilan_terbayar"]
)
print(
    "Sisa pokok        :",
    snapshot_sebelum["pinjaman"]["sisa_pokok"]
)
print(
    "Saldo rekening    :",
    snapshot_sebelum["rekening"]["saldo"]
)
print(
    "Notifikasi tersedia:",
    sorted(id_notifikasi_sebelum)
)
print("Hari pembayaran    :", pinjaman.tanggal_jatuh_tempo)
print()


# Membayar tepat pada tanggal jatuh tempo agar tidak terkena denda.
PinjamanService.bayar_cicilan(
    nasabah=nasabah,
    id_pinjaman=pinjaman.ID,
    hari_ini=pinjaman.tanggal_jatuh_tempo
)

snapshot_setelah = ambil_snapshot(nasabah.NIK)

id_notifikasi_setelah = {
    data["id_objek"]
    for data in snapshot_setelah["notifikasi"]
}

id_notifikasi_objek = {
    notifikasi.id_objek
    for notifikasi in nasabah.notifikasi
    if (
        notifikasi.jenis_referensi
        == JenisReferensi.PINJAMAN
    )
}


# Pinjaman berhasil diperbarui.
assert (
    snapshot_setelah["pinjaman"]["cicilan_terbayar"]
    == snapshot_sebelum["pinjaman"]["cicilan_terbayar"] + 1
), "Jumlah cicilan terbayar tidak bertambah"

assert (
    snapshot_setelah["pinjaman"]["sisa_pokok"]
    < snapshot_sebelum["pinjaman"]["sisa_pokok"]
), "Sisa pokok tidak berkurang"

assert (
    snapshot_setelah["rekening"]["saldo"]
    < snapshot_sebelum["rekening"]["saldo"]
), "Saldo rekening tidak berkurang"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"] + 1
), "Transaksi pembayaran cicilan tidak bertambah"


# Hanya notifikasi pinjaman yang dibayar yang dihapus.
assert ID_PINJAMAN_DIBAYAR not in id_notifikasi_setelah, (
    "Notifikasi pinjaman ID 10 masih tersimpan di SQLite"
)

assert ID_PINJAMAN_DIPERTAHANKAN in id_notifikasi_setelah, (
    "Notifikasi pinjaman ID 9 ikut terhapus"
)

assert id_notifikasi_setelah == {9}, (
    "Hasil akhir notifikasi SQLite tidak sesuai"
)


# State objek Python juga harus mengikuti SQLite.
assert pinjaman.cicilan_terbayar == 1, (
    "State cicilan objek pinjaman tidak diperbarui"
)

assert rekening.saldo == snapshot_setelah["rekening"]["saldo"], (
    "Saldo objek rekening tidak sesuai SQLite"
)

assert ID_PINJAMAN_DIBAYAR not in id_notifikasi_objek, (
    "Notifikasi pinjaman ID 10 masih ada pada objek nasabah"
)

assert ID_PINJAMAN_DIPERTAHANKAN in id_notifikasi_objek, (
    "Notifikasi pinjaman ID 9 hilang dari objek nasabah"
)


print("=== KONDISI SETELAH PEMBAYARAN ===")
print(
    "Cicilan terbayar :",
    snapshot_setelah["pinjaman"]["cicilan_terbayar"]
)
print(
    "Sisa pokok       :",
    snapshot_setelah["pinjaman"]["sisa_pokok"]
)
print(
    "Saldo rekening   :",
    snapshot_setelah["rekening"]["saldo"]
)
print(
    "Notifikasi tersisa:",
    sorted(id_notifikasi_setelah)
)
print()

print(
    "✅ PENGHAPUSAN NOTIFIKASI BERHASIL: "
    "pembayaran pinjaman ID 10 menghapus notifikasinya, "
    "sedangkan notifikasi pinjaman ID 9 tetap tersimpan"
)