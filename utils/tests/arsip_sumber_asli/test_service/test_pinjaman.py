# # # # # # # # # # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # # # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # # # # # # # # # NOMINAL_PENGUJIAN = 2_000_000
# # # # # # # # # # # # # # # # # # # TENOR_PENGUJIAN = 6
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # # # AMBIL DATA MENTAH DARI SQLITE
# # # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # # # # # #     data_pinjaman = koneksi.execute(
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #         SELECT pinjaman.*
# # # # # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # # # # #         JOIN rekening
# # # # # # # # # # # # # # # # # # #             ON rekening.norek = pinjaman.norek
# # # # # # # # # # # # # # # # # # #         WHERE rekening.nik_pemilik = ?
# # # # # # # # # # # # # # # # # # #           AND pinjaman.nominal_pinjaman = ?
# # # # # # # # # # # # # # # # # # #           AND pinjaman.tenor = ?
# # # # # # # # # # # # # # # # # # #         ORDER BY pinjaman.id DESC
# # # # # # # # # # # # # # # # # # #         LIMIT 1
# # # # # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # # # # #         (
# # # # # # # # # # # # # # # # # # #             NIK_PENGUJIAN,
# # # # # # # # # # # # # # # # # # #             NOMINAL_PENGUJIAN,
# # # # # # # # # # # # # # # # # # #             TENOR_PENGUJIAN
# # # # # # # # # # # # # # # # # # #         )
# # # # # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # if data_pinjaman is None:
# # # # # # # # # # # # # # # # # # #     raise ValueError("Pinjaman pengujian tidak ditemukan di SQLite")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # print("DATA PINJAMAN SQLITE")
# # # # # # # # # # # # # # # # # # # print("ID                 :", data_pinjaman["id"])
# # # # # # # # # # # # # # # # # # # print("Norek              :", data_pinjaman["norek"])
# # # # # # # # # # # # # # # # # # # print("Nominal            :", data_pinjaman["nominal_pinjaman"])
# # # # # # # # # # # # # # # # # # # print("Bunga              :", data_pinjaman["bunga"])
# # # # # # # # # # # # # # # # # # # print("Tenor              :", data_pinjaman["tenor"])
# # # # # # # # # # # # # # # # # # # print("Cicilan tetap      :", data_pinjaman["cicilan_tetap"])
# # # # # # # # # # # # # # # # # # # print("Sisa pokok         :", data_pinjaman["sisa_pokok"])
# # # # # # # # # # # # # # # # # # # print("Cicilan terbayar   :", data_pinjaman["cicilan_terbayar"])
# # # # # # # # # # # # # # # # # # # print("Status             :", data_pinjaman["status"])
# # # # # # # # # # # # # # # # # # # print("Tanggal pencairan  :", data_pinjaman["tanggal_pencairan"])
# # # # # # # # # # # # # # # # # # # print("Jatuh tempo        :", data_pinjaman["tanggal_jatuh_tempo"])
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["id"] is not None
# # # # # # # # # # # # # # # # # # # print("✅ Pinjaman memperoleh ID global SQLite")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["status"] == StatusPinjaman.DIAJUKAN.value
# # # # # # # # # # # # # # # # # # # print("✅ Status diajukan tersimpan di SQLite")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["nominal_pinjaman"] == NOMINAL_PENGUJIAN
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["tenor"] == TENOR_PENGUJIAN
# # # # # # # # # # # # # # # # # # # print("✅ Nominal dan tenor tersimpan sesuai pengajuan")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["cicilan_tetap"] == 0
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["cicilan_terbayar"] == 0
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["sisa_pokok"] == NOMINAL_PENGUJIAN
# # # # # # # # # # # # # # # # # # # print("✅ State awal pinjaman tersimpan dengan benar")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["tanggal_pencairan"] is None
# # # # # # # # # # # # # # # # # # # assert data_pinjaman["tanggal_jatuh_tempo"] is None
# # # # # # # # # # # # # # # # # # # print("✅ Tanggal pinjaman masih kosong sebelum pencairan")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # # # MUAT ULANG NASABAH DAN PINJAMAN
# # # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # pinjaman = next(
# # # # # # # # # # # # # # # # # # #     (
# # # # # # # # # # # # # # # # # # #         pinjaman
# # # # # # # # # # # # # # # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # # # # # # # # # # # # # # #         if pinjaman.ID == data_pinjaman["id"]
# # # # # # # # # # # # # # # # # # #     ),
# # # # # # # # # # # # # # # # # # #     None
# # # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # if pinjaman is None:
# # # # # # # # # # # # # # # # # # #     raise ValueError(
# # # # # # # # # # # # # # # # # # #         "Pinjaman tidak berhasil dimuat oleh PinjamanLoader"
# # # # # # # # # # # # # # # # # # #     )
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # print("\nHASIL PINJAMAN LOADER")
# # # # # # # # # # # # # # # # # # # print("ID                 :", pinjaman.ID)
# # # # # # # # # # # # # # # # # # # print("Nama pemilik       :", pinjaman.pemilik.nama)
# # # # # # # # # # # # # # # # # # # print("Norek              :", pinjaman.rekening.norek)
# # # # # # # # # # # # # # # # # # # print("Nominal            :", pinjaman.nominal_pinjaman)
# # # # # # # # # # # # # # # # # # # print("Bunga              :", pinjaman.bunga)
# # # # # # # # # # # # # # # # # # # print("Tenor              :", pinjaman.tenor)
# # # # # # # # # # # # # # # # # # # print("Status             :", pinjaman.status)
# # # # # # # # # # # # # # # # # # # print("Jumlah pinjaman    :", len(nasabah.daftar_pinjaman))
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert pinjaman.ID == data_pinjaman["id"]
# # # # # # # # # # # # # # # # # # # print("✅ ID pinjaman berhasil dipulihkan")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert pinjaman.status == StatusPinjaman.DIAJUKAN
# # # # # # # # # # # # # # # # # # # assert isinstance(pinjaman.status, StatusPinjaman)
# # # # # # # # # # # # # # # # # # # print("✅ Status teks kembali menjadi StatusPinjaman")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert pinjaman.pemilik is nasabah
# # # # # # # # # # # # # # # # # # # print("✅ Pinjaman menunjuk objek nasabah yang benar")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert pinjaman.rekening in nasabah.rekening
# # # # # # # # # # # # # # # # # # # print("✅ Rekening pinjaman terdapat dalam daftar rekening nasabah")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # rekening_dari_daftar = next(
# # # # # # # # # # # # # # # # # # #     rekening
# # # # # # # # # # # # # # # # # # #     for rekening in nasabah.rekening
# # # # # # # # # # # # # # # # # # #     if rekening.norek == pinjaman.rekening.norek
# # # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert pinjaman.rekening is rekening_dari_daftar
# # # # # # # # # # # # # # # # # # # print("✅ Pinjaman memakai objek rekening yang sama")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # assert pinjaman.nominal_pinjaman == NOMINAL_PENGUJIAN
# # # # # # # # # # # # # # # # # # # assert pinjaman.tenor == TENOR_PENGUJIAN
# # # # # # # # # # # # # # # # # # # assert pinjaman.sisa_pokok == NOMINAL_PENGUJIAN
# # # # # # # # # # # # # # # # # # # print("✅ Seluruh state pinjaman berhasil dimuat")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # print(
# # # # # # # # # # # # # # # # # # #     "\n✅ Pengajuan pinjaman dan PinjamanLoader "
# # # # # # # # # # # # # # # # # # #     "bekerja sesuai rancangan"
# # # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # # # # # #     print("DATA PINJAMAN")
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #     semua_pinjaman = koneksi.execute(
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #         SELECT id, norek, nominal_pinjaman, status
# # # # # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # # # # #         ORDER BY id
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #     ).fetchall()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #     for data in semua_pinjaman:
# # # # # # # # # # # # # # # # # # #         print(dict(data))
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #     urutan = koneksi.execute(
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #         SELECT seq
# # # # # # # # # # # # # # # # # # #         FROM sqlite_sequence
# # # # # # # # # # # # # # # # # # #         WHERE name = 'pinjaman'
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #     print("\nID terakhir yang pernah dicatat SQLite:")
# # # # # # # # # # # # # # # # # # #     print(urutan["seq"] if urutan is not None else None)
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # # # # # #     audit_pinjaman = koneksi.execute(
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #         SELECT id, jenis, waktu, log, nik, norek
# # # # # # # # # # # # # # # # # # #         FROM audit
# # # # # # # # # # # # # # # # # # #         WHERE jenis LIKE '%pinjaman%'
# # # # # # # # # # # # # # # # # # #            OR log LIKE '%pinjaman%'
# # # # # # # # # # # # # # # # # # #         ORDER BY id
# # # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # # #     ).fetchall()
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # #     for audit in audit_pinjaman:
# # # # # # # # # # # # # # # # # # #         print(dict(audit))
# # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # # # # # # # # ID_PINJAMAN = 5
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # # PERIKSA DATA SQLITE
# # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # # # # #     data_pinjaman = koneksi.execute(
# # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # #         SELECT pinjaman.*
# # # # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # # # #         JOIN rekening
# # # # # # # # # # # # # # # # # #             ON rekening.norek = pinjaman.norek
# # # # # # # # # # # # # # # # # #         WHERE pinjaman.id = ?
# # # # # # # # # # # # # # # # # #           AND rekening.nik_pemilik = ?
# # # # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # # # #         (ID_PINJAMAN, NIK_PENGUJIAN)
# # # # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #     audit_persetujuan = koneksi.execute(
# # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # #         SELECT *
# # # # # # # # # # # # # # # # # #         FROM audit
# # # # # # # # # # # # # # # # # #         WHERE jenis = 'persetujuan pinjaman'
# # # # # # # # # # # # # # # # # #           AND nik = ?
# # # # # # # # # # # # # # # # # #           AND log LIKE ?
# # # # # # # # # # # # # # # # # #         ORDER BY id DESC
# # # # # # # # # # # # # # # # # #         LIMIT 1
# # # # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # # # #         (
# # # # # # # # # # # # # # # # # #             NIK_PENGUJIAN,
# # # # # # # # # # # # # # # # # #             f"%ID {ID_PINJAMAN}%"
# # # # # # # # # # # # # # # # # #         )
# # # # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #     masih_diajukan = koneksi.execute(
# # # # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # # # #         SELECT *
# # # # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # # # #         WHERE id = ?
# # # # # # # # # # # # # # # # # #           AND status = 'diajukan'
# # # # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # # # #         (ID_PINJAMAN,)
# # # # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # if data_pinjaman is None:
# # # # # # # # # # # # # # # # # #     raise ValueError("Pinjaman pengujian tidak ditemukan")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # print("DATA PINJAMAN SETELAH PERSETUJUAN")
# # # # # # # # # # # # # # # # # # print("ID                :", data_pinjaman["id"])
# # # # # # # # # # # # # # # # # # print("Norek             :", data_pinjaman["norek"])
# # # # # # # # # # # # # # # # # # print("Nominal           :", data_pinjaman["nominal_pinjaman"])
# # # # # # # # # # # # # # # # # # print("Status            :", data_pinjaman["status"])
# # # # # # # # # # # # # # # # # # print("Cicilan tetap     :", data_pinjaman["cicilan_tetap"])
# # # # # # # # # # # # # # # # # # print("Cicilan terbayar  :", data_pinjaman["cicilan_terbayar"])
# # # # # # # # # # # # # # # # # # print("Sisa pokok        :", data_pinjaman["sisa_pokok"])
# # # # # # # # # # # # # # # # # # print("Tanggal pencairan :", data_pinjaman["tanggal_pencairan"])
# # # # # # # # # # # # # # # # # # print("Jatuh tempo       :", data_pinjaman["tanggal_jatuh_tempo"])
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert (
# # # # # # # # # # # # # # # # # #     data_pinjaman["status"]
# # # # # # # # # # # # # # # # # #     == StatusPinjaman.DISETUJUI.value
# # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # # print("✅ Status SQLite berubah menjadi disetujui")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert masih_diajukan is None
# # # # # # # # # # # # # # # # # # print("✅ Pinjaman hilang dari daftar pengajuan admin")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert data_pinjaman["cicilan_tetap"] == 0
# # # # # # # # # # # # # # # # # # assert data_pinjaman["cicilan_terbayar"] == 0
# # # # # # # # # # # # # # # # # # assert (
# # # # # # # # # # # # # # # # # #     data_pinjaman["sisa_pokok"]
# # # # # # # # # # # # # # # # # #     == data_pinjaman["nominal_pinjaman"]
# # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # # print("✅ State pembayaran belum berubah")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert data_pinjaman["tanggal_pencairan"] is None
# # # # # # # # # # # # # # # # # # assert data_pinjaman["tanggal_jatuh_tempo"] is None
# # # # # # # # # # # # # # # # # # print("✅ Tanggal tetap kosong sebelum pencairan")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert audit_persetujuan is not None
# # # # # # # # # # # # # # # # # # print("✅ Audit persetujuan berhasil disimpan")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # # PERIKSA PINJAMAN LOADER
# # # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # pinjaman = next(
# # # # # # # # # # # # # # # # # #     (
# # # # # # # # # # # # # # # # # #         pinjaman
# # # # # # # # # # # # # # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # # # # # # # # # # # # # #         if pinjaman.ID == ID_PINJAMAN
# # # # # # # # # # # # # # # # # #     ),
# # # # # # # # # # # # # # # # # #     None
# # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # if pinjaman is None:
# # # # # # # # # # # # # # # # # #     raise ValueError(
# # # # # # # # # # # # # # # # # #         "Pinjaman tidak berhasil dimuat kembali"
# # # # # # # # # # # # # # # # # #     )
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # print("\nHASIL LOADER SETELAH PERSETUJUAN")
# # # # # # # # # # # # # # # # # # print("ID             :", pinjaman.ID)
# # # # # # # # # # # # # # # # # # print("Nama pemilik   :", pinjaman.pemilik.nama)
# # # # # # # # # # # # # # # # # # print("Norek          :", pinjaman.rekening.norek)
# # # # # # # # # # # # # # # # # # print("Status         :", pinjaman.status)
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert pinjaman.status == StatusPinjaman.DISETUJUI
# # # # # # # # # # # # # # # # # # print("✅ Loader memulihkan StatusPinjaman.DISETUJUI")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert pinjaman.pemilik is nasabah
# # # # # # # # # # # # # # # # # # print("✅ Relasi objek nasabah tetap benar")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # rekening_nasabah = next(
# # # # # # # # # # # # # # # # # #     rekening
# # # # # # # # # # # # # # # # # #     for rekening in nasabah.rekening
# # # # # # # # # # # # # # # # # #     if rekening.norek == pinjaman.rekening.norek
# # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # assert pinjaman.rekening is rekening_nasabah
# # # # # # # # # # # # # # # # # # print("✅ Relasi objek rekening tetap benar")
# # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # print(
# # # # # # # # # # # # # # # # # #     "\n✅ Persetujuan pinjaman SQLite "
# # # # # # # # # # # # # # # # # #     "bekerja sesuai rancangan"
# # # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # ID_DISETUJUI = 5
# # # # # # # # # # # # # # # # ID_DITOLAK = 7
# # # # # # # # # # # # # # # # NIK_DITOLAK = "7777888899990000"
# # # # # # # # # # # # # # # # CATATAN_ADMIN = "pengajuan belum memenuhi syarat"
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # # #     pinjaman_disetujui = koneksi.execute(
# # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # #         SELECT *
# # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # #         WHERE id = ?
# # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # #         (ID_DISETUJUI,)
# # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #     pinjaman_ditolak = koneksi.execute(
# # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # #         SELECT *
# # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # #         WHERE id = ?
# # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # #         (ID_DITOLAK,)
# # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #     masih_diajukan = koneksi.execute(
# # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # #         SELECT *
# # # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # # #         WHERE id = ?
# # # # # # # # # # # # # # # #           AND status = 'diajukan'
# # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # #         (ID_DITOLAK,)
# # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #     audit_penolakan = koneksi.execute(
# # # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # # #         SELECT *
# # # # # # # # # # # # # # # #         FROM audit
# # # # # # # # # # # # # # # #         WHERE jenis = 'penolakan pinjaman'
# # # # # # # # # # # # # # # #           AND nik = ?
# # # # # # # # # # # # # # # #           AND log LIKE ?
# # # # # # # # # # # # # # # #         ORDER BY id DESC
# # # # # # # # # # # # # # # #         LIMIT 1
# # # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # # #         (
# # # # # # # # # # # # # # # #             NIK_DITOLAK,
# # # # # # # # # # # # # # # #             f"%ID {ID_DITOLAK}%"
# # # # # # # # # # # # # # # #         )
# # # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # if pinjaman_disetujui is None:
# # # # # # # # # # # # # # # # #     raise ValueError("Pinjaman ID 5 tidak ditemukan")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # if pinjaman_ditolak is None:
# # # # # # # # # # # # # # # # #     raise ValueError("Pinjaman ID 6 tidak ditemukan")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # print("HASIL KEPUTUSAN ADMIN")
# # # # # # # # # # # # # # # # # print(
# # # # # # # # # # # # # # # # #     f"Pinjaman ID {ID_DISETUJUI}:",
# # # # # # # # # # # # # # # # #     pinjaman_disetujui["status"]
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # print(
# # # # # # # # # # # # # # # # #     f"Pinjaman ID {ID_DITOLAK}:",
# # # # # # # # # # # # # # # # #     pinjaman_ditolak["status"]
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert (
# # # # # # # # # # # # # # # # #     pinjaman_disetujui["status"]
# # # # # # # # # # # # # # # # #     == StatusPinjaman.DISETUJUI.value
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # print("✅ Pinjaman sebelumnya tetap berstatus disetujui")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert (
# # # # # # # # # # # # # # # # #     pinjaman_ditolak["status"]
# # # # # # # # # # # # # # # # #     == StatusPinjaman.DITOLAK.value
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # # print("✅ Status pinjaman baru berubah menjadi ditolak")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert masih_diajukan is None
# # # # # # # # # # # # # # # # # print("✅ Pinjaman ditolak hilang dari antrean admin")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert audit_penolakan is not None
# # # # # # # # # # # # # # # # # print("✅ Audit penolakan berhasil disimpan")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # print("Catatan dalam audit:", audit_penolakan["log"])
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert CATATAN_ADMIN.lower() in audit_penolakan["log"].lower()
# # # # # # # # # # # # # # # # # print("✅ Catatan admin tersimpan dalam audit")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # # # PERIKSA LOADER PINJAMAN DITOLAK
# # # # # # # # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_DITOLAK)
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # pinjaman = next(
# # # # # # # # # # # # # # # # #     (
# # # # # # # # # # # # # # # # #         pinjaman
# # # # # # # # # # # # # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # # # # # # # # # # # # #         if pinjaman.ID == ID_DITOLAK
# # # # # # # # # # # # # # # # #     ),
# # # # # # # # # # # # # # # # #     None
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # if pinjaman is None:
# # # # # # # # # # # # # # # # #     raise ValueError(
# # # # # # # # # # # # # # # # #         "Pinjaman ditolak tidak berhasil dimuat kembali"
# # # # # # # # # # # # # # # # #     )
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # print("\nHASIL LOADER PINJAMAN DITOLAK")
# # # # # # # # # # # # # # # # # print("ID           :", pinjaman.ID)
# # # # # # # # # # # # # # # # # print("Nama pemilik :", pinjaman.pemilik.nama)
# # # # # # # # # # # # # # # # # print("Norek        :", pinjaman.rekening.norek)
# # # # # # # # # # # # # # # # # print("Status       :", pinjaman.status)
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert pinjaman.status == StatusPinjaman.DITOLAK
# # # # # # # # # # # # # # # # # print("✅ Loader memulihkan StatusPinjaman.DITOLAK")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert pinjaman.pemilik is nasabah
# # # # # # # # # # # # # # # # # print("✅ Relasi objek nasabah tetap benar")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # rekening_nasabah = next(
# # # # # # # # # # # # # # # # #     rekening
# # # # # # # # # # # # # # # # #     for rekening in nasabah.rekening
# # # # # # # # # # # # # # # # #     if rekening.norek == pinjaman.rekening.norek
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # assert pinjaman.rekening is rekening_nasabah
# # # # # # # # # # # # # # # # # print("✅ Relasi objek rekening tetap benar")
# # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # print(
# # # # # # # # # # # # # # # # #     "\n✅ Penolakan pinjaman SQLite "
# # # # # # # # # # # # # # # # #     "bekerja sesuai rancangan"
# # # # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # # #     daftar_kolom = koneksi.execute(
# # # # # # # # # # # # # # # #         "PRAGMA table_info(pinjaman)"
# # # # # # # # # # # # # # # #     ).fetchall()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #     for kolom in daftar_kolom:
# # # # # # # # # # # # # # # #         print(kolom["name"])
# # # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # NIK_PENGUJIAN = "7777888899990000"
# # # # # # # # # # # # # # # NOREK_PENGUJIAN = "2001443311291615"
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # Harus sama persis dengan catatan yang kamu masukkan melalui UI.
# # # # # # # # # # # # # # # CATATAN_ADMIN = "testing catatan admin pada penolakan"
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # try:
# # # # # # # # # # # # # # #     # Mengambil pinjaman terbaru milik rekening pengujian.
# # # # # # # # # # # # # # #     data_pinjaman = koneksi.execute(
# # # # # # # # # # # # # # #         """
# # # # # # # # # # # # # # #         SELECT
# # # # # # # # # # # # # # #             pinjaman.id,
# # # # # # # # # # # # # # #             pinjaman.norek,
# # # # # # # # # # # # # # #             pinjaman.status,
# # # # # # # # # # # # # # #             pinjaman.catatan_admin
# # # # # # # # # # # # # # #         FROM pinjaman
# # # # # # # # # # # # # # #         JOIN rekening
# # # # # # # # # # # # # # #             ON rekening.norek = pinjaman.norek
# # # # # # # # # # # # # # #         WHERE rekening.nik_pemilik = ?
# # # # # # # # # # # # # # #           AND pinjaman.norek = ?
# # # # # # # # # # # # # # #         ORDER BY pinjaman.id DESC
# # # # # # # # # # # # # # #         LIMIT 1
# # # # # # # # # # # # # # #         """,
# # # # # # # # # # # # # # #         (
# # # # # # # # # # # # # # #             NIK_PENGUJIAN,
# # # # # # # # # # # # # # #             NOREK_PENGUJIAN
# # # # # # # # # # # # # # #         )
# # # # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # if data_pinjaman is None:
# # # # # # # # # # # # # # #     raise ValueError(
# # # # # # # # # # # # # # #         "Pinjaman pengujian tidak ditemukan"
# # # # # # # # # # # # # # #     )
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # print("HASIL PENGUJIAN PENOLAKAN")
# # # # # # # # # # # # # # # print("ID pinjaman  :", data_pinjaman["id"])
# # # # # # # # # # # # # # # print("NIK nasabah  :", NIK_PENGUJIAN)
# # # # # # # # # # # # # # # print("Norek        :", data_pinjaman["norek"])
# # # # # # # # # # # # # # # print("Status       :", data_pinjaman["status"])
# # # # # # # # # # # # # # # print("Catatan admin:", data_pinjaman["catatan_admin"])
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # assert (
# # # # # # # # # # # # # # #     data_pinjaman["status"]
# # # # # # # # # # # # # # #     == StatusPinjaman.DITOLAK.value
# # # # # # # # # # # # # # # ), "Status pinjaman belum berubah menjadi ditolak"
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # print("✅ Status pinjaman tersimpan sebagai ditolak")
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # assert (
# # # # # # # # # # # # # # #     data_pinjaman["catatan_admin"]
# # # # # # # # # # # # # # #     == CATATAN_ADMIN
# # # # # # # # # # # # # # # ), "Catatan admin tidak tersimpan sesuai input UI"
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # print("✅ Catatan admin berhasil tersimpan")
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # print(
# # # # # # # # # # # # # # #     "\n✅ Pembaruan status dan catatan penolakan "
# # # # # # # # # # # # # # #     "berhasil diuji"
# # # # # # # # # # # # # # # )
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # def cek_audit():
# # # # # # # # # # # # # # # #     koneksi = buat_koneksi()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #     try:
# # # # # # # # # # # # # # # #         cursor = koneksi.execute("""SELECT *
# # # # # # # # # # # # # # # #         FROM audit
# # # # # # # # # # # # # # # #         ORDER BY id DESC
# # # # # # # # # # # # # # # #         LIMIT 1""")
# # # # # # # # # # # # # # # #         return cursor.fetchone()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #     finally:
# # # # # # # # # # # # # # # #         koneksi.close()
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # data = cek_audit()
# # # # # # # # # # # # # # # # print(dict(data))
# # # # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # try:
# # # # # # # # # # # # # #     daftar_kolom = koneksi.execute(
# # # # # # # # # # # # # #         "PRAGMA table_info(rekening)"
# # # # # # # # # # # # # #     ).fetchall()
# # # # # # # # # # # # # #
# # # # # # # # # # # # # #     for kolom in daftar_kolom:
# # # # # # # # # # # # # #         print(kolom["name"], kolom["type"])
# # # # # # # # # # # # # #
# # # # # # # # # # # # # # finally:
# # # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # from datetime import datetime
# # # # # # # # # # # # #
# # # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # #
# # # # # # # # # # # # # try:
# # # # # # # # # # # # #     data_rekening = koneksi.execute(
# # # # # # # # # # # # #         """
# # # # # # # # # # # # #         SELECT
# # # # # # # # # # # # #             norek,
# # # # # # # # # # # # #             nik_pemilik,
# # # # # # # # # # # # #             status,
# # # # # # # # # # # # #             waktu_dibuat
# # # # # # # # # # # # #         FROM rekening
# # # # # # # # # # # # #         WHERE norek = ?
# # # # # # # # # # # # #         """,
# # # # # # # # # # # # #         (NOREK_PENGUJIAN,)
# # # # # # # # # # # # #     ).fetchone()
# # # # # # # # # # # # #
# # # # # # # # # # # # # finally:
# # # # # # # # # # # # #     koneksi.close()
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # if data_rekening is None:
# # # # # # # # # # # # #     raise ValueError("Rekening baru tidak ditemukan")
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # print("HASIL PENGUJIAN WAKTU PEMBUKAAN")
# # # # # # # # # # # # # print("Norek        :", data_rekening["norek"])
# # # # # # # # # # # # # print("NIK pemilik  :", data_rekening["nik_pemilik"])
# # # # # # # # # # # # # print("Status       :", data_rekening["status"])
# # # # # # # # # # # # # print("Waktu dibuat :", data_rekening["waktu_dibuat"])
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # assert data_rekening["waktu_dibuat"] is not None
# # # # # # # # # # # # # print("✅ waktu_dibuat berhasil disimpan")
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # waktu_dibuat = datetime.fromisoformat(
# # # # # # # # # # # # #     data_rekening["waktu_dibuat"]
# # # # # # # # # # # # # )
# # # # # # # # # # # # #
# # # # # # # # # # # # # assert isinstance(waktu_dibuat, datetime)
# # # # # # # # # # # # # print("✅ waktu_dibuat tersimpan dalam format datetime ISO")
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # selisih = datetime.now() - waktu_dibuat
# # # # # # # # # # # # #
# # # # # # # # # # # # # assert 0 <= selisih.total_seconds() < 300
# # # # # # # # # # # # # print("✅ waktu_dibuat sesuai dengan waktu pengujian")
# # # # # # # # # # # # #
# # # # # # # # # # # # #
# # # # # # # # # # # # # print("\n✅ Pembukaan rekening baru berhasil diuji")
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # # from datetime import datetime
# # # # # # # # # # # #
# # # # # # # # # # # # from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
# # # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # # # # # # # #
# # # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # # # rekening = RekeningLoader.muat_rekening(
# # # # # # # # # # # #     NOREK_PENGUJIAN,
# # # # # # # # # # # # koneksi)
# # # # # # # # # # # #
# # # # # # # # # # # # if rekening is None:
# # # # # # # # # # # #     raise ValueError("Rekening gagal dimuat")
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # # print("HASIL PENGUJIAN LOADER")
# # # # # # # # # # # # print("Norek        :", rekening.norek)
# # # # # # # # # # # # print("Waktu dibuat :", rekening.waktu_dibuat)
# # # # # # # # # # # # print("Tipe data    :", type(rekening.waktu_dibuat))
# # # # # # # # # # # #
# # # # # # # # # # # #
# # # # # # # # # # # # assert isinstance(rekening.waktu_dibuat, datetime)
# # # # # # # # # # # #
# # # # # # # # # # # # print("✅ Loader memulihkan waktu_dibuat sebagai datetime")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # import datetime
# # # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # # # # # # # # # #     RekeningLoader
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # Mengambil waktu asli langsung dari SQLite
# # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # #
# # # # # # # # # # # try:
# # # # # # # # # # #     data_rekening = koneksi.execute(
# # # # # # # # # # #         """
# # # # # # # # # # #         SELECT waktu_dibuat
# # # # # # # # # # #         FROM rekening
# # # # # # # # # # #         WHERE norek = ?
# # # # # # # # # # #         """,
# # # # # # # # # # #         (NOREK_PENGUJIAN,)
# # # # # # # # # # #     ).fetchone()
# # # # # # # # # # #
# # # # # # # # # # # finally:
# # # # # # # # # # #     koneksi.close()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # if data_rekening is None:
# # # # # # # # # # #     raise ValueError("Rekening pengujian tidak ditemukan")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # waktu_sqlite = datetime.datetime.fromisoformat(
# # # # # # # # # # #     data_rekening["waktu_dibuat"]
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # Memuat rekening melalui loader
# # # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # #
# # # # # # # # # # # try:
# # # # # # # # # # #     rekening = RekeningLoader.muat_rekening(
# # # # # # # # # # #         norek=NOREK_PENGUJIAN,
# # # # # # # # # # #         koneksi=koneksi
# # # # # # # # # # #     )
# # # # # # # # # # # finally:
# # # # # # # # # # #     koneksi.close()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # if rekening is None:
# # # # # # # # # # #     raise ValueError("Loader gagal memuat rekening")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("Waktu SQLite:", waktu_sqlite)
# # # # # # # # # # # print("Waktu loader:", rekening.waktu_dibuat)
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert rekening.waktu_dibuat == waktu_sqlite
# # # # # # # # # # #
# # # # # # # # # # # print("✅ Loader mempertahankan waktu_dibuat dari SQLite")
# # # # # # # # # #
# # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # #
# # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # #
# # # # # # # # # # try:
# # # # # # # # # #     daftar_kolom = koneksi.execute(
# # # # # # # # # #         "PRAGMA table_info(transaksi)"
# # # # # # # # # #     ).fetchall()
# # # # # # # # # #
# # # # # # # # # #     for kolom in daftar_kolom:
# # # # # # # # # #         print(
# # # # # # # # # #             kolom["name"],
# # # # # # # # # #             kolom["type"],
# # # # # # # # # #             "NOT NULL:" if kolom["notnull"] else "NULLABLE"
# # # # # # # # # #         )
# # # # # # # # # #
# # # # # # # # # # finally:
# # # # # # # # # #     koneksi.close()
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# # # # # # # # #     PinjamanRepository
# # # # # # # # # )
# # # # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # # # #     RekeningRepository
# # # # # # # # # )
# # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # ID_PINJAMAN = 8
# # # # # # # # # NIK_PENGUJIAN = "0000111122223333"
# # # # # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # # # # #
# # # # # # # # # NOMINAL_PENGUJIAN = 1_000_000
# # # # # # # # # BUNGA_PENGUJIAN = 0.10
# # # # # # # # # TENOR_PENGUJIAN = 6
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # #
# # # # # # # # # try:
# # # # # # # # #     # Mengambil data pinjaman langsung dari SQLite.
# # # # # # # # #     data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
# # # # # # # # #         ID_PINJAMAN,
# # # # # # # # #         koneksi
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     if data_pinjaman is None:
# # # # # # # # #         raise AssertionError(
# # # # # # # # #             f"Pinjaman ID {ID_PINJAMAN} tidak ditemukan"
# # # # # # # # #         )
# # # # # # # # #
# # # # # # # # #     # Mengambil rekening yang terhubung dengan pinjaman.
# # # # # # # # #     # Data rekening dibutuhkan untuk memeriksa pemilik dan mencatat
# # # # # # # # #     # saldo awal sebelum pencairan dilakukan.
# # # # # # # # #     data_rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # # # #         data_pinjaman["norek"],
# # # # # # # # #         koneksi
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     if data_rekening is None:
# # # # # # # # #         raise AssertionError(
# # # # # # # # #             "Rekening yang terhubung dengan pinjaman tidak ditemukan"
# # # # # # # # #         )
# # # # # # # # #
# # # # # # # # #     print("=== DATA PINJAMAN SETELAH PERSETUJUAN ===")
# # # # # # # # #     print("ID pinjaman       :", data_pinjaman["id"])
# # # # # # # # #     print("Nomor rekening    :", data_pinjaman["norek"])
# # # # # # # # #     print("Nominal pinjaman  :", data_pinjaman["nominal_pinjaman"])
# # # # # # # # #     print("Bunga             :", data_pinjaman["bunga"])
# # # # # # # # #     print("Tenor             :", data_pinjaman["tenor"])
# # # # # # # # #     print("Cicilan tetap     :", data_pinjaman["cicilan_tetap"])
# # # # # # # # #     print("Sisa pokok        :", data_pinjaman["sisa_pokok"])
# # # # # # # # #     print("Cicilan terbayar  :", data_pinjaman["cicilan_terbayar"])
# # # # # # # # #     print("Status            :", data_pinjaman["status"])
# # # # # # # # #     print("Tanggal pencairan :", data_pinjaman["tanggal_pencairan"])
# # # # # # # # #     print("Jatuh tempo       :", data_pinjaman["tanggal_jatuh_tempo"])
# # # # # # # # #     print()
# # # # # # # # #
# # # # # # # # #     print("=== DATA REKENING TUJUAN ===")
# # # # # # # # #     print("Nomor rekening :", data_rekening["norek"])
# # # # # # # # #     print("NIK pemilik    :", data_rekening["nik_pemilik"])
# # # # # # # # #     print("Saldo awal     :", data_rekening["saldo"])
# # # # # # # # #     print("Status         :", data_rekening["status"])
# # # # # # # # #     print()
# # # # # # # # #
# # # # # # # # #     # Memastikan pinjaman yang ditemukan adalah pinjaman pengujian.
# # # # # # # # #     assert data_pinjaman["id"] == ID_PINJAMAN, (
# # # # # # # # #         "ID pinjaman tidak sesuai"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_pinjaman["norek"] == NOREK_PENGUJIAN, (
# # # # # # # # #         "Pinjaman terhubung dengan rekening yang salah"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_rekening["nik_pemilik"] == NIK_PENGUJIAN, (
# # # # # # # # #         "Rekening pinjaman dimiliki nasabah yang berbeda"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_pinjaman["nominal_pinjaman"] == NOMINAL_PENGUJIAN, (
# # # # # # # # #         "Nominal pinjaman bukan Rp1.000.000"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     # Float dibandingkan menggunakan toleransi kecil agar tidak
# # # # # # # # #     # terganggu oleh cara komputer menyimpan angka pecahan.
# # # # # # # # #     assert abs(data_pinjaman["bunga"] - BUNGA_PENGUJIAN) < 1e-9, (
# # # # # # # # #         "Bunga pinjaman bukan 10% per tahun"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_pinjaman["tenor"] == TENOR_PENGUJIAN, (
# # # # # # # # #         "Tenor pinjaman bukan enam bulan"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert (
# # # # # # # # #         data_pinjaman["status"]
# # # # # # # # #         == StatusPinjaman.DISETUJUI.value
# # # # # # # # #     ), "Pinjaman belum berstatus disetujui"
# # # # # # # # #
# # # # # # # # #     # Sebelum pencairan, jadwal pembayaran seharusnya belum dibentuk.
# # # # # # # # #     assert data_pinjaman["cicilan_tetap"] == 0, (
# # # # # # # # #         "Cicilan tetap sudah terisi sebelum pencairan"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_pinjaman["cicilan_terbayar"] == 0, (
# # # # # # # # #         "Pinjaman sudah mempunyai cicilan terbayar"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_pinjaman["tanggal_pencairan"] is None, (
# # # # # # # # #         "Tanggal pencairan sudah terisi"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_pinjaman["tanggal_jatuh_tempo"] is None, (
# # # # # # # # #         "Tanggal jatuh tempo sudah terisi"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     assert data_rekening["status"] == "aktif", (
# # # # # # # # #         "Rekening tujuan tidak berstatus aktif"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     print(
# # # # # # # # #         "✅ Pinjaman ID 8 sudah disetujui dan siap diuji "
# # # # # # # # #         "untuk pencairan"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # # finally:
# # # # # # # # #     koneksi.close()
# # # # # # # #
# # # # # # # #
# # # # # # # #
# # # # # # # #
# # # # # # # # import datetime
# # # # # # # #
# # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # # # # # #     NasabahLoader
# # # # # # # # )
# # # # # # # # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# # # # # # # #     PinjamanRepository
# # # # # # # # )
# # # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # # #     RekeningRepository
# # # # # # # # )
# # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # from bank_djago.services.pinjaman.pinjaman_service import (
# # # # # # # #     PinjamanService
# # # # # # # # )
# # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # #
# # # # # # # #
# # # # # # # # ID_PINJAMAN = 8
# # # # # # # # NIK_PENGUJIAN = "0000111122223333"
# # # # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # # # #
# # # # # # # # NOMINAL_PINJAMAN = 1_000_000
# # # # # # # #
# # # # # # # #
# # # # # # # # # ============================================================
# # # # # # # # # 1. MEMUAT OBJEK NASABAH BESERTA REKENING DAN PINJAMANNYA
# # # # # # # # # ============================================================
# # # # # # # #
# # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # #
# # # # # # # # if nasabah is None:
# # # # # # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # # # # # #
# # # # # # # #
# # # # # # # # rekening = next(
# # # # # # # #     (
# # # # # # # #         rekening
# # # # # # # #         for rekening in nasabah.rekening
# # # # # # # #         if rekening.norek == NOREK_PENGUJIAN
# # # # # # # #     ),
# # # # # # # #     None
# # # # # # # # )
# # # # # # # #
# # # # # # # # if rekening is None:
# # # # # # # #     raise AssertionError(
# # # # # # # #         "Objek rekening pengujian tidak ditemukan"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #
# # # # # # # # pinjaman = next(
# # # # # # # #     (
# # # # # # # #         pinjaman
# # # # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # # # #         if pinjaman.ID == ID_PINJAMAN
# # # # # # # #     ),
# # # # # # # #     None
# # # # # # # # )
# # # # # # # #
# # # # # # # # if pinjaman is None:
# # # # # # # #     raise AssertionError(
# # # # # # # #         "Objek pinjaman ID 8 tidak ditemukan"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #
# # # # # # # # # Menyimpan kondisi objek sebelum pencairan.
# # # # # # # # # Nilai ini akan dibandingkan setelah service dijalankan.
# # # # # # # # saldo_objek_sebelum = rekening.saldo
# # # # # # # # objek_pinjaman_sebelum = pinjaman
# # # # # # # # objek_rekening_sebelum = rekening
# # # # # # # #
# # # # # # # #
# # # # # # # # print("=== KONDISI SEBELUM PENCAIRAN ===")
# # # # # # # # print("ID pinjaman    :", pinjaman.ID)
# # # # # # # # print("Status         :", pinjaman.status)
# # # # # # # # print("Nominal        :", pinjaman.nominal_pinjaman)
# # # # # # # # print("Sisa pokok     :", pinjaman.sisa_pokok)
# # # # # # # # print("Saldo rekening :", saldo_objek_sebelum)
# # # # # # # # print()
# # # # # # # #
# # # # # # # #
# # # # # # # # assert pinjaman.status == StatusPinjaman.DISETUJUI, (
# # # # # # # #     "Objek pinjaman belum berstatus disetujui"
# # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # ============================================================
# # # # # # # # # 2. MENJALANKAN SERVICE PENCAIRAN
# # # # # # # # # ============================================================
# # # # # # # #
# # # # # # # # hari_pencairan = datetime.date.today()
# # # # # # # #
# # # # # # # # pinjaman_hasil = PinjamanService.cairkan_pinjaman(
# # # # # # # #     nasabah=nasabah,
# # # # # # # #     id_pinjaman=ID_PINJAMAN,
# # # # # # # #     hari_ini=hari_pencairan
# # # # # # # # )
# # # # # # # #
# # # # # # # # saldo_yang_diharapkan = (
# # # # # # # #     saldo_objek_sebelum + NOMINAL_PINJAMAN
# # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # ============================================================
# # # # # # # # # 3. MEMERIKSA PERUBAHAN OBJEK PYTHON
# # # # # # # # # ============================================================
# # # # # # # #
# # # # # # # # # Service harus mengembalikan objek pinjaman yang sama,
# # # # # # # # # bukan menciptakan objek pinjaman baru.
# # # # # # # # assert pinjaman_hasil is objek_pinjaman_sebelum, (
# # # # # # # #     "Service mengembalikan objek pinjaman yang berbeda"
# # # # # # # # )
# # # # # # # #
# # # # # # # # # Objek rekening pada pinjaman juga harus tetap menggunakan
# # # # # # # # # objek rekening yang berada di dalam daftar rekening nasabah.
# # # # # # # # assert pinjaman_hasil.rekening is objek_rekening_sebelum, (
# # # # # # # #     "Pinjaman tidak menggunakan objek rekening milik nasabah"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert pinjaman_hasil.status == StatusPinjaman.AKTIF, (
# # # # # # # #     "Status objek pinjaman belum berubah menjadi aktif"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert pinjaman_hasil.cicilan_tetap > 0, (
# # # # # # # #     "Cicilan tetap belum berhasil dihitung"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert pinjaman_hasil.tanggal_pencairan == hari_pencairan, (
# # # # # # # #     "Tanggal pencairan objek tidak sesuai"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert pinjaman_hasil.tanggal_jatuh_tempo is not None, (
# # # # # # # #     "Tanggal jatuh tempo belum ditentukan"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert rekening.saldo == saldo_yang_diharapkan, (
# # # # # # # #     "Saldo objek rekening tidak bertambah sesuai nominal pinjaman"
# # # # # # # # )
# # # # # # # #
# # # # # # # # print("✅ State objek Python berhasil diperbarui")
# # # # # # # #
# # # # # # # #
# # # # # # # # # ============================================================
# # # # # # # # # 4. MEMERIKSA HASIL PENYIMPANAN DI DATABASE
# # # # # # # # # ============================================================
# # # # # # # #
# # # # # # # # koneksi = buat_koneksi()
# # # # # # # #
# # # # # # # # try:
# # # # # # # #     data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
# # # # # # # #         ID_PINJAMAN,
# # # # # # # #         koneksi
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     data_rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # # #         NOREK_PENGUJIAN,
# # # # # # # #         koneksi
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     # Mengambil transaksi pencairan berdasarkan referensi pinjaman.
# # # # # # # #     transaksi = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM transaksi
# # # # # # # #         WHERE jenis = 'pencairan_pinjaman'
# # # # # # # #           AND jenis_referensi = 'pinjaman'
# # # # # # # #           AND id_referensi = ?
# # # # # # # #         ORDER BY id DESC
# # # # # # # #         LIMIT 1
# # # # # # # #         """,
# # # # # # # #         (ID_PINJAMAN,)
# # # # # # # #     ).fetchone()
# # # # # # # #
# # # # # # # #     if transaksi is None:
# # # # # # # #         raise AssertionError(
# # # # # # # #             "Transaksi pencairan pinjaman tidak ditemukan"
# # # # # # # #         )
# # # # # # # #
# # # # # # # #     # Mengambil riwayat yang terhubung dengan transaksi pencairan.
# # # # # # # #     daftar_riwayat = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM riwayat
# # # # # # # #         WHERE transaksi_id = ?
# # # # # # # #         ORDER BY id
# # # # # # # #         """,
# # # # # # # #         (transaksi["id"],)
# # # # # # # #     ).fetchall()
# # # # # # # #
# # # # # # # #     # Mengambil audit yang terhubung dengan transaksi pencairan.
# # # # # # # #     daftar_audit = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM audit
# # # # # # # #         WHERE transaksi_id = ?
# # # # # # # #         ORDER BY id
# # # # # # # #         """,
# # # # # # # #         (transaksi["id"],)
# # # # # # # #     ).fetchall()
# # # # # # # #
# # # # # # # #
# # # # # # # #     print()
# # # # # # # #     print("=== KONDISI SETELAH PENCAIRAN ===")
# # # # # # # #     print("Status pinjaman   :", data_pinjaman["status"])
# # # # # # # #     print("Cicilan tetap     :", data_pinjaman["cicilan_tetap"])
# # # # # # # #     print("Sisa pokok        :", data_pinjaman["sisa_pokok"])
# # # # # # # #     print("Tanggal pencairan :", data_pinjaman["tanggal_pencairan"])
# # # # # # # #     print("Jatuh tempo       :", data_pinjaman["tanggal_jatuh_tempo"])
# # # # # # # #     print("Saldo rekening    :", data_rekening["saldo"])
# # # # # # # #     print()
# # # # # # # #
# # # # # # # #     print("=== DATA TRANSAKSI ===")
# # # # # # # #     print("ID transaksi       :", transaksi["id"])
# # # # # # # #     print("Jenis transaksi    :", transaksi["jenis"])
# # # # # # # #     print("Rekening tujuan    :", transaksi["norek_tujuan"])
# # # # # # # #     print("Nominal             :", transaksi["nominal"])
# # # # # # # #     print("Saldo tujuan awal  :", transaksi["saldo_tujuan_sebelum"])
# # # # # # # #     print("Saldo tujuan akhir :", transaksi["saldo_tujuan_sesudah"])
# # # # # # # #     print("Jenis referensi    :", transaksi["jenis_referensi"])
# # # # # # # #     print("ID referensi       :", transaksi["id_referensi"])
# # # # # # # #     print("Waktu              :", transaksi["waktu"])
# # # # # # # #     print()
# # # # # # # #
# # # # # # # #     print("=== RIWAYAT TERHUBUNG ===")
# # # # # # # #     for riwayat in daftar_riwayat:
# # # # # # # #         print(
# # # # # # # #             f"ID {riwayat['id']} | "
# # # # # # # #             f"Transaksi {riwayat['transaksi_id']} | "
# # # # # # # #             f"{riwayat['jenis']} | "
# # # # # # # #             f"{riwayat['log']}"
# # # # # # # #         )
# # # # # # # #
# # # # # # # #     print()
# # # # # # # #     print("=== AUDIT TERHUBUNG ===")
# # # # # # # #     for audit in daftar_audit:
# # # # # # # #         print(
# # # # # # # #             f"ID {audit['id']} | "
# # # # # # # #             f"Transaksi {audit['transaksi_id']} | "
# # # # # # # #             f"{audit['jenis']} | "
# # # # # # # #             f"{audit['log']}"
# # # # # # # #         )
# # # # # # # #
# # # # # # # #
# # # # # # # #     # ========================================================
# # # # # # # #     # 5. MEMASTIKAN SELURUH HASIL SESUAI
# # # # # # # #     # ========================================================
# # # # # # # #
# # # # # # # #     assert data_pinjaman["status"] == StatusPinjaman.AKTIF.value, (
# # # # # # # #         "Status pinjaman di database bukan aktif"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert data_pinjaman["cicilan_tetap"] > 0, (
# # # # # # # #         "Cicilan tetap tidak tersimpan"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert (
# # # # # # # #         data_pinjaman["tanggal_pencairan"]
# # # # # # # #         == hari_pencairan.isoformat()
# # # # # # # #     ), "Tanggal pencairan database tidak sesuai"
# # # # # # # #
# # # # # # # #     assert data_pinjaman["tanggal_jatuh_tempo"] is not None, (
# # # # # # # #         "Tanggal jatuh tempo tidak tersimpan"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert data_rekening["saldo"] == saldo_yang_diharapkan, (
# # # # # # # #         "Saldo rekening di database tidak sesuai"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert transaksi["norek_tujuan"] == NOREK_PENGUJIAN, (
# # # # # # # #         "Rekening tujuan transaksi salah"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert transaksi["nominal"] == NOMINAL_PINJAMAN, (
# # # # # # # #         "Nominal transaksi pencairan salah"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert transaksi["saldo_tujuan_sebelum"] == saldo_objek_sebelum, (
# # # # # # # #         "Snapshot saldo sebelum pencairan salah"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert transaksi["saldo_tujuan_sesudah"] == saldo_yang_diharapkan, (
# # # # # # # #         "Snapshot saldo setelah pencairan salah"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert transaksi["jenis_referensi"] == "pinjaman", (
# # # # # # # #         "Jenis referensi transaksi bukan pinjaman"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert transaksi["id_referensi"] == ID_PINJAMAN, (
# # # # # # # #         "ID referensi tidak menunjuk pinjaman ID 8"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert len(daftar_riwayat) == 1, (
# # # # # # # #         "Jumlah riwayat yang terhubung bukan satu"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     assert len(daftar_audit) == 1, (
# # # # # # # #         "Jumlah audit yang terhubung bukan satu"
# # # # # # # #     )
# # # # # # # #
# # # # # # # # finally:
# # # # # # # #     koneksi.close()
# # # # # # # #
# # # # # # # #
# # # # # # # # print()
# # # # # # # # print(
# # # # # # # #     "✅ PENCAIRAN PINJAMAN ID 8 BERHASIL: "
# # # # # # # #     "saldo, pinjaman, transaksi, riwayat, audit, "
# # # # # # # #     "dan objek Python tersimpan dengan benar"
# # # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # # # # #     NasabahLoader
# # # # # # # )
# # # # # # # from bank_djago.services.pinjaman.pinjaman_service import (
# # # # # # #     PinjamanService
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # NIK_PENGUJIAN = "0000111122223333"
# # # # # # # ID_PINJAMAN = 8
# # # # # # #
# # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # #
# # # # # # # try:
# # # # # # #     PinjamanService.cairkan_pinjaman(
# # # # # # #         nasabah=nasabah,
# # # # # # #         id_pinjaman=ID_PINJAMAN
# # # # # # #     )
# # # # # # #
# # # # # # # except ValueError as error:
# # # # # # #     print("✅ Pencairan kedua berhasil ditolak")
# # # # # # #     print("Pesan error:", error)
# # # # # # #
# # # # # # # else:
# # # # # # #     raise AssertionError(
# # # # # # #         "Pinjaman dapat dicairkan dua kali"
# # # # # # #     )
# # # # # #
# # # # # #
# # # # # # from unittest.mock import patch
# # # # # #
# # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # # # #     NasabahLoader
# # # # # # )
# # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # #     AuditRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# # # # # #     PinjamanRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # #     RekeningRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # from bank_djago.services.pinjaman.pinjaman_service import (
# # # # # #     PinjamanService
# # # # # # )
# # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # #
# # # # # #
# # # # # # ID_PINJAMAN = 9
# # # # # # NIK_PENGUJIAN = "0000111122223333"
# # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # #
# # # # # #
# # # # # # def ambil_snapshot_database():
# # # # # #     """
# # # # # #     Mengambil keadaan database yang harus tetap sama apabila
# # # # # #     pencairan mengalami kegagalan dan di-rollback.
# # # # # #     """
# # # # # #     koneksi = buat_koneksi()
# # # # # #
# # # # # #     try:
# # # # # #         data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
# # # # # #             ID_PINJAMAN,
# # # # # #             koneksi
# # # # # #         )
# # # # # #
# # # # # #         data_rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # # # #             NOREK_PENGUJIAN,
# # # # # #             koneksi
# # # # # #         )
# # # # # #
# # # # # #         jumlah_transaksi = koneksi.execute(
# # # # # #             "SELECT COUNT(*) AS jumlah FROM transaksi"
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # #             "SELECT COUNT(*) AS jumlah FROM riwayat"
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         jumlah_audit = koneksi.execute(
# # # # # #             "SELECT COUNT(*) AS jumlah FROM audit"
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         transaksi_pencairan = koneksi.execute(
# # # # # #             """
# # # # # #             SELECT COUNT(*) AS jumlah
# # # # # #             FROM transaksi
# # # # # #             WHERE jenis = 'pencairan_pinjaman'
# # # # # #               AND jenis_referensi = 'pinjaman'
# # # # # #               AND id_referensi = ?
# # # # # #             """,
# # # # # #             (ID_PINJAMAN,)
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         return {
# # # # # #             # Row diubah menjadi dictionary agar dapat dibandingkan
# # # # # #             # setelah koneksi database ditutup.
# # # # # #             "pinjaman": dict(data_pinjaman),
# # # # # #             "rekening": dict(data_rekening),
# # # # # #             "jumlah_transaksi": jumlah_transaksi,
# # # # # #             "jumlah_riwayat": jumlah_riwayat,
# # # # # #             "jumlah_audit": jumlah_audit,
# # # # # #             "transaksi_pencairan": transaksi_pencairan
# # # # # #         }
# # # # # #
# # # # # #     finally:
# # # # # #         koneksi.close()
# # # # # #
# # # # # #
# # # # # # # ============================================================
# # # # # # # 1. MEMUAT OBJEK YANG DIGUNAKAN SERVICE
# # # # # # # ============================================================
# # # # # #
# # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # #
# # # # # # if nasabah is None:
# # # # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # # # #
# # # # # #
# # # # # # rekening = next(
# # # # # #     (
# # # # # #         rekening
# # # # # #         for rekening in nasabah.rekening
# # # # # #         if rekening.norek == NOREK_PENGUJIAN
# # # # # #     ),
# # # # # #     None
# # # # # # )
# # # # # #
# # # # # # if rekening is None:
# # # # # #     raise AssertionError(
# # # # # #         "Objek rekening pengujian tidak ditemukan"
# # # # # #     )
# # # # # #
# # # # # #
# # # # # # pinjaman = next(
# # # # # #     (
# # # # # #         pinjaman
# # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # #         if pinjaman.ID == ID_PINJAMAN
# # # # # #     ),
# # # # # #     None
# # # # # # )
# # # # # #
# # # # # # if pinjaman is None:
# # # # # #     raise AssertionError(
# # # # # #         "Objek pinjaman ID 9 tidak ditemukan"
# # # # # #     )
# # # # # #
# # # # # #
# # # # # # # Memastikan pinjaman belum pernah dicairkan.
# # # # # # assert pinjaman.status == StatusPinjaman.DISETUJUI, (
# # # # # #     "Pinjaman ID 9 belum berstatus disetujui"
# # # # # # )
# # # # # #
# # # # # #
# # # # # # # ============================================================
# # # # # # # 2. MENYIMPAN KONDISI AWAL
# # # # # # # ============================================================
# # # # # #
# # # # # # snapshot_sebelum = ambil_snapshot_database()
# # # # # #
# # # # # # snapshot_objek_sebelum = {
# # # # # #     "status_pinjaman": pinjaman.status,
# # # # # #     "cicilan_tetap": pinjaman.cicilan_tetap,
# # # # # #     "tanggal_pencairan": pinjaman.tanggal_pencairan,
# # # # # #     "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
# # # # # #     "sisa_pokok": pinjaman.sisa_pokok,
# # # # # #     "saldo_rekening": rekening.saldo,
# # # # # #     "jumlah_riwayat_objek": len(rekening.riwayat)
# # # # # # }
# # # # # #
# # # # # #
# # # # # # print("=== KONDISI SEBELUM PENCAIRAN ===")
# # # # # # print(snapshot_sebelum)
# # # # # # print()
# # # # # #
# # # # # #
# # # # # # # ============================================================
# # # # # # # 3. MEMBUAT KEGAGALAN AUDIT
# # # # # # # ============================================================
# # # # # #
# # # # # # def gagalkan_audit(*args, **kwargs):
# # # # # #     """
# # # # # #     Menggantikan AuditRepository.tambah_audit untuk sementara.
# # # # # #     Saat service mencoba menyimpan audit, fungsi ini melempar error.
# # # # # #     """
# # # # # #     raise RuntimeError(
# # # # # #         "Kegagalan audit untuk menguji rollback pencairan pinjaman"
# # # # # #     )
# # # # # #
# # # # # #
# # # # # # # Patch hanya aktif di dalam blok with.
# # # # # # # Setelah blok selesai, method asli otomatis dikembalikan.
# # # # # # with patch.object(
# # # # # #     AuditRepository,
# # # # # #     "tambah_audit",
# # # # # #     side_effect=gagalkan_audit
# # # # # # ):
# # # # # #     try:
# # # # # #         PinjamanService.cairkan_pinjaman(
# # # # # #             nasabah=nasabah,
# # # # # #             id_pinjaman=ID_PINJAMAN
# # # # # #         )
# # # # # #
# # # # # #     except RuntimeError as error:
# # # # # #         assert str(error) == (
# # # # # #             "Kegagalan audit untuk menguji rollback "
# # # # # #             "pencairan pinjaman"
# # # # # #         )
# # # # # #
# # # # # #         print("✅ Kegagalan buatan berhasil dipicu")
# # # # # #         print("Pesan error:", error)
# # # # # #
# # # # # #     else:
# # # # # #         raise AssertionError(
# # # # # #             "Pencairan tetap berhasil meskipun audit digagalkan"
# # # # # #         )
# # # # # #
# # # # # #
# # # # # # # ============================================================
# # # # # # # 4. MEMBACA ULANG DATABASE SETELAH ROLLBACK
# # # # # # # ============================================================
# # # # # #
# # # # # # snapshot_setelah = ambil_snapshot_database()
# # # # # #
# # # # # # snapshot_objek_setelah = {
# # # # # #     "status_pinjaman": pinjaman.status,
# # # # # #     "cicilan_tetap": pinjaman.cicilan_tetap,
# # # # # #     "tanggal_pencairan": pinjaman.tanggal_pencairan,
# # # # # #     "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
# # # # # #     "sisa_pokok": pinjaman.sisa_pokok,
# # # # # #     "saldo_rekening": rekening.saldo,
# # # # # #     "jumlah_riwayat_objek": len(rekening.riwayat)
# # # # # # }
# # # # # #
# # # # # #
# # # # # # print()
# # # # # # print("=== KONDISI SETELAH ROLLBACK ===")
# # # # # # print(snapshot_setelah)
# # # # # # print()
# # # # # #
# # # # # #
# # # # # # # ============================================================
# # # # # # # 5. MEMERIKSA DATABASE
# # # # # # # ============================================================
# # # # # #
# # # # # # assert snapshot_setelah["pinjaman"] == snapshot_sebelum["pinjaman"], (
# # # # # #     "Data pinjaman berubah meskipun transaksi di-rollback"
# # # # # # )
# # # # # #
# # # # # # assert snapshot_setelah["rekening"] == snapshot_sebelum["rekening"], (
# # # # # #     "Saldo atau data rekening berubah meskipun transaksi di-rollback"
# # # # # # )
# # # # # #
# # # # # # assert (
# # # # # #     snapshot_setelah["jumlah_transaksi"]
# # # # # #     == snapshot_sebelum["jumlah_transaksi"]
# # # # # # ), "Transaksi pencairan masih tersisa"
# # # # # #
# # # # # # assert (
# # # # # #     snapshot_setelah["jumlah_riwayat"]
# # # # # #     == snapshot_sebelum["jumlah_riwayat"]
# # # # # # ), "Riwayat pencairan masih tersisa"
# # # # # #
# # # # # # assert (
# # # # # #     snapshot_setelah["jumlah_audit"]
# # # # # #     == snapshot_sebelum["jumlah_audit"]
# # # # # # ), "Jumlah audit berubah setelah rollback"
# # # # # #
# # # # # # assert snapshot_setelah["transaksi_pencairan"] == 0, (
# # # # # #     "Transaksi pencairan pinjaman ID 9 masih tersimpan"
# # # # # # )
# # # # # #
# # # # # #
# # # # # # # ============================================================
# # # # # # # 6. MEMERIKSA OBJEK PYTHON
# # # # # # # ============================================================
# # # # # #
# # # # # # assert snapshot_objek_setelah == snapshot_objek_sebelum, (
# # # # # #     "State objek Python berubah meskipun pencairan gagal"
# # # # # # )
# # # # # #
# # # # # #
# # # # # # # Memastikan pinjaman masih dapat dicairkan nanti.
# # # # # # assert (
# # # # # #     snapshot_setelah["pinjaman"]["status"]
# # # # # #     == StatusPinjaman.DISETUJUI.value
# # # # # # ), "Status pinjaman tidak kembali menjadi disetujui"
# # # # # #
# # # # # #
# # # # # # print(
# # # # # #     "\n✅ ROLLBACK PENCAIRAN PINJAMAN BERHASIL: "
# # # # # #     "pinjaman, saldo, transaksi, riwayat, audit, "
# # # # # #     "dan objek Python tidak berubah"
# # # # # # )
# # # # #
# # # # #
# # # # #
# # # # # import datetime
# # # # #
# # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # # #     NasabahLoader
# # # # # )
# # # # # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# # # # #     PinjamanRepository
# # # # # )
# # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # #     RekeningRepository
# # # # # )
# # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # from bank_djago.services.pinjaman.pinjaman_service import (
# # # # #     PinjamanService
# # # # # )
# # # # # from bank_djago.utils.utility import StatusPinjaman, Utilitas
# # # # #
# # # # #
# # # # # ID_PINJAMAN = 8
# # # # # NIK_PENGUJIAN = "0000111122223333"
# # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # 1. MEMUAT OBJEK NASABAH, REKENING, DAN PINJAMAN
# # # # # # ============================================================
# # # # #
# # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # #
# # # # # if nasabah is None:
# # # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # # #
# # # # #
# # # # # rekening = next(
# # # # #     (
# # # # #         rekening
# # # # #         for rekening in nasabah.rekening
# # # # #         if rekening.norek == NOREK_PENGUJIAN
# # # # #     ),
# # # # #     None
# # # # # )
# # # # #
# # # # # if rekening is None:
# # # # #     raise AssertionError("Objek rekening tidak ditemukan")
# # # # #
# # # # #
# # # # # pinjaman = next(
# # # # #     (
# # # # #         pinjaman
# # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # #         if pinjaman.ID == ID_PINJAMAN
# # # # #     ),
# # # # #     None
# # # # # )
# # # # #
# # # # # if pinjaman is None:
# # # # #     raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # 2. MENGAMBIL KONDISI DATABASE SEBELUM PEMBAYARAN
# # # # # # ============================================================
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     data_pinjaman_sebelum = dict(
# # # # #         PinjamanRepository.cari_pinjaman_dengan_id(
# # # # #             ID_PINJAMAN,
# # # # #             koneksi
# # # # #         )
# # # # #     )
# # # # #
# # # # #     data_rekening_sebelum = dict(
# # # # #         RekeningRepository.cari_rekening_dengan_norek(
# # # # #             NOREK_PENGUJIAN,
# # # # #             koneksi
# # # # #         )
# # # # #     )
# # # # #
# # # # #     jumlah_transaksi_sebelum = koneksi.execute(
# # # # #         """
# # # # #         SELECT COUNT(*) AS jumlah
# # # # #         FROM transaksi
# # # # #         WHERE jenis = 'pembayaran_cicilan'
# # # # #           AND jenis_referensi = 'pinjaman'
# # # # #           AND id_referensi = ?
# # # # #         """,
# # # # #         (ID_PINJAMAN,)
# # # # #     ).fetchone()["jumlah"]
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # assert (
# # # # #     data_pinjaman_sebelum["status"]
# # # # #     == StatusPinjaman.AKTIF.value
# # # # # ), "Pinjaman ID 8 tidak berstatus aktif"
# # # # #
# # # # # assert data_pinjaman_sebelum["cicilan_terbayar"] == 0, (
# # # # #     "Pinjaman ID 8 ternyata sudah pernah membayar cicilan"
# # # # # )
# # # # #
# # # # #
# # # # # # Menggunakan tanggal pencairan sebagai tanggal pengujian.
# # # # # # Berdasarkan aturan saat ini, cicilan pertama boleh dibayar
# # # # # # mulai tanggal pencairan.
# # # # # hari_pengujian = datetime.date.fromisoformat(
# # # # #     data_pinjaman_sebelum["tanggal_pencairan"]
# # # # # )
# # # # #
# # # # # saldo_sebelum = data_rekening_sebelum["saldo"]
# # # # # sisa_pokok_sebelum = data_pinjaman_sebelum["sisa_pokok"]
# # # # # cicilan_tetap = data_pinjaman_sebelum["cicilan_tetap"]
# # # # # bunga = data_pinjaman_sebelum["bunga"]
# # # # #
# # # # # persentase_bunga = bunga / 12
# # # # #
# # # # # bunga_bulanan = round(
# # # # #     sisa_pokok_sebelum * persentase_bunga
# # # # # )
# # # # #
# # # # # pokok_dibayar = cicilan_tetap - bunga_bulanan
# # # # #
# # # # # sisa_pokok_diharapkan = (
# # # # #     sisa_pokok_sebelum - pokok_dibayar
# # # # # )
# # # # #
# # # # # # Karena pembayaran dilakukan pada tanggal pencairan,
# # # # # # belum ada keterlambatan dan denda.
# # # # # denda_diharapkan = 0
# # # # # total_bayar_diharapkan = cicilan_tetap
# # # # # saldo_diharapkan = saldo_sebelum - total_bayar_diharapkan
# # # # #
# # # # # jatuh_tempo_lama = datetime.date.fromisoformat(
# # # # #     data_pinjaman_sebelum["tanggal_jatuh_tempo"]
# # # # # )
# # # # #
# # # # # jatuh_tempo_diharapkan = Utilitas.tambah_bulan(
# # # # #     jatuh_tempo_lama,
# # # # #     1
# # # # # )
# # # # #
# # # # #
# # # # # print("=== KONDISI SEBELUM PEMBAYARAN ===")
# # # # # print("ID pinjaman       :", ID_PINJAMAN)
# # # # # print("Saldo rekening    :", saldo_sebelum)
# # # # # print("Cicilan tetap     :", cicilan_tetap)
# # # # # print("Bunga bulan ini   :", bunga_bulanan)
# # # # # print("Pokok dibayar     :", pokok_dibayar)
# # # # # print("Sisa pokok        :", sisa_pokok_sebelum)
# # # # # print("Cicilan terbayar  :", 0)
# # # # # print("Hari pembayaran   :", hari_pengujian)
# # # # # print()
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # 3. MENJALANKAN PEMBAYARAN CICILAN
# # # # # # ============================================================
# # # # #
# # # # # pinjaman_hasil = PinjamanService.bayar_cicilan(
# # # # #     id_pinjaman=ID_PINJAMAN,
# # # # #     nasabah=nasabah,
# # # # #     hari_ini=hari_pengujian
# # # # # )
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # 4. MEMERIKSA STATE OBJEK PYTHON
# # # # # # ============================================================
# # # # #
# # # # # assert pinjaman_hasil is pinjaman, (
# # # # #     "Service mengembalikan objek pinjaman yang berbeda"
# # # # # )
# # # # #
# # # # # assert pinjaman_hasil.status == StatusPinjaman.AKTIF, (
# # # # #     "Pinjaman seharusnya masih aktif setelah cicilan pertama"
# # # # # )
# # # # #
# # # # # assert pinjaman_hasil.cicilan_terbayar == 1, (
# # # # #     "Jumlah cicilan terbayar pada objek bukan satu"
# # # # # )
# # # # #
# # # # # assert pinjaman_hasil.sisa_pokok == sisa_pokok_diharapkan, (
# # # # #     "Sisa pokok pada objek tidak sesuai"
# # # # # )
# # # # #
# # # # # assert (
# # # # #     pinjaman_hasil.tanggal_jatuh_tempo
# # # # #     == jatuh_tempo_diharapkan
# # # # # ), "Jatuh tempo pada objek tidak sesuai"
# # # # #
# # # # # assert rekening.saldo == saldo_diharapkan, (
# # # # #     "Saldo objek rekening tidak sesuai"
# # # # # )
# # # # #
# # # # # print("✅ State objek Python berhasil diperbarui")
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # 5. MEMBACA ULANG HASIL DARI SQLITE
# # # # # # ============================================================
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     data_pinjaman_setelah = PinjamanRepository.cari_pinjaman_dengan_id(
# # # # #         ID_PINJAMAN,
# # # # #         koneksi
# # # # #     )
# # # # #
# # # # #     data_rekening_setelah = RekeningRepository.cari_rekening_dengan_norek(
# # # # #         NOREK_PENGUJIAN,
# # # # #         koneksi
# # # # #     )
# # # # #
# # # # #     transaksi = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM transaksi
# # # # #         WHERE jenis = 'pembayaran_cicilan'
# # # # #           AND jenis_referensi = 'pinjaman'
# # # # #           AND id_referensi = ?
# # # # #         ORDER BY id DESC
# # # # #         LIMIT 1
# # # # #         """,
# # # # #         (ID_PINJAMAN,)
# # # # #     ).fetchone()
# # # # #
# # # # #     if transaksi is None:
# # # # #         raise AssertionError(
# # # # #             "Transaksi pembayaran cicilan tidak ditemukan"
# # # # #         )
# # # # #
# # # # #     daftar_riwayat = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM riwayat
# # # # #         WHERE transaksi_id = ?
# # # # #         ORDER BY id
# # # # #         """,
# # # # #         (transaksi["id"],)
# # # # #     ).fetchall()
# # # # #
# # # # #     daftar_audit = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM audit
# # # # #         WHERE transaksi_id = ?
# # # # #         ORDER BY id
# # # # #         """,
# # # # #         (transaksi["id"],)
# # # # #     ).fetchall()
# # # # #
# # # # #
# # # # #     print()
# # # # #     print("=== KONDISI SETELAH PEMBAYARAN ===")
# # # # #     print("Status pinjaman   :", data_pinjaman_setelah["status"])
# # # # #     print("Cicilan terbayar  :", data_pinjaman_setelah["cicilan_terbayar"])
# # # # #     print("Sisa pokok        :", data_pinjaman_setelah["sisa_pokok"])
# # # # #     print("Jatuh tempo baru  :", data_pinjaman_setelah["tanggal_jatuh_tempo"])
# # # # #     print("Saldo rekening    :", data_rekening_setelah["saldo"])
# # # # #     print()
# # # # #
# # # # #     print("=== DATA TRANSAKSI ===")
# # # # #     print("ID transaksi      :", transaksi["id"])
# # # # #     print("Jenis             :", transaksi["jenis"])
# # # # #     print("Rekening sumber   :", transaksi["norek_sumber"])
# # # # #     print("Nominal cicilan   :", transaksi["nominal"])
# # # # #     print("Denda             :", transaksi["biaya"])
# # # # #     print("Saldo awal        :", transaksi["saldo_sumber_sebelum"])
# # # # #     print("Saldo akhir       :", transaksi["saldo_sumber_sesudah"])
# # # # #     print("Jenis referensi   :", transaksi["jenis_referensi"])
# # # # #     print("ID referensi      :", transaksi["id_referensi"])
# # # # #     print("Waktu             :", transaksi["waktu"])
# # # # #     print()
# # # # #
# # # # #     print("=== RIWAYAT TERHUBUNG ===")
# # # # #     for riwayat in daftar_riwayat:
# # # # #         print(
# # # # #             f"ID {riwayat['id']} | "
# # # # #             f"Transaksi {riwayat['transaksi_id']} | "
# # # # #             f"{riwayat['jenis']} | "
# # # # #             f"{riwayat['log']}"
# # # # #         )
# # # # #
# # # # #     print()
# # # # #     print("=== AUDIT TERHUBUNG ===")
# # # # #     for audit in daftar_audit:
# # # # #         print(
# # # # #             f"ID {audit['id']} | "
# # # # #             f"Transaksi {audit['transaksi_id']} | "
# # # # #             f"{audit['jenis']} | "
# # # # #             f"{audit['log']}"
# # # # #         )
# # # # #
# # # # #
# # # # #     # ========================================================
# # # # #     # 6. MEMASTIKAN HASIL DATABASE
# # # # #     # ========================================================
# # # # #
# # # # #     assert data_pinjaman_setelah["status"] == "aktif", (
# # # # #         "Pinjaman tidak lagi berstatus aktif"
# # # # #     )
# # # # #
# # # # #     assert data_pinjaman_setelah["cicilan_terbayar"] == 1, (
# # # # #         "Jumlah cicilan terbayar di database bukan satu"
# # # # #     )
# # # # #
# # # # #     assert (
# # # # #         data_pinjaman_setelah["sisa_pokok"]
# # # # #         == sisa_pokok_diharapkan
# # # # #     ), "Sisa pokok di database tidak sesuai"
# # # # #
# # # # #     assert (
# # # # #         data_pinjaman_setelah["tanggal_jatuh_tempo"]
# # # # #         == jatuh_tempo_diharapkan.isoformat()
# # # # #     ), "Tanggal jatuh tempo baru tidak sesuai"
# # # # #
# # # # #     assert data_rekening_setelah["saldo"] == saldo_diharapkan, (
# # # # #         "Saldo rekening di database tidak sesuai"
# # # # #     )
# # # # #
# # # # #     assert transaksi["norek_sumber"] == NOREK_PENGUJIAN, (
# # # # #         "Rekening sumber transaksi salah"
# # # # #     )
# # # # #
# # # # #     assert transaksi["nominal"] == cicilan_tetap, (
# # # # #         "Nominal transaksi tidak sama dengan cicilan tetap"
# # # # #     )
# # # # #
# # # # #     assert transaksi["biaya"] == denda_diharapkan, (
# # # # #         "Denda transaksi seharusnya nol"
# # # # #     )
# # # # #
# # # # #     assert transaksi["saldo_sumber_sebelum"] == saldo_sebelum, (
# # # # #         "Snapshot saldo sebelum pembayaran salah"
# # # # #     )
# # # # #
# # # # #     assert transaksi["saldo_sumber_sesudah"] == saldo_diharapkan, (
# # # # #         "Snapshot saldo setelah pembayaran salah"
# # # # #     )
# # # # #
# # # # #     assert transaksi["jenis_referensi"] == "pinjaman", (
# # # # #         "Jenis referensi transaksi bukan pinjaman"
# # # # #     )
# # # # #
# # # # #     assert transaksi["id_referensi"] == ID_PINJAMAN, (
# # # # #         "ID referensi transaksi tidak sesuai"
# # # # #     )
# # # # #
# # # # #     assert len(daftar_riwayat) == 1, (
# # # # #         "Jumlah riwayat terhubung bukan satu"
# # # # #     )
# # # # #
# # # # #     assert len(daftar_audit) == 1, (
# # # # #         "Jumlah audit terhubung bukan satu"
# # # # #     )
# # # # #
# # # # #     jumlah_transaksi_setelah = koneksi.execute(
# # # # #         """
# # # # #         SELECT COUNT(*) AS jumlah
# # # # #         FROM transaksi
# # # # #         WHERE jenis = 'pembayaran_cicilan'
# # # # #           AND jenis_referensi = 'pinjaman'
# # # # #           AND id_referensi = ?
# # # # #         """,
# # # # #         (ID_PINJAMAN,)
# # # # #     ).fetchone()["jumlah"]
# # # # #
# # # # #     assert jumlah_transaksi_setelah == (
# # # # #         jumlah_transaksi_sebelum + 1
# # # # #     ), "Jumlah transaksi pembayaran tidak bertambah tepat satu"
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # print()
# # # # # print(
# # # # #     "✅ PEMBAYARAN CICILAN PERTAMA BERHASIL: "
# # # # #     "saldo, sisa pokok, jadwal, transaksi, riwayat, "
# # # # #     "audit, dan objek Python tersimpan dengan benar"
# # # # # )
# # # #
# # # #
# # # #
# # # # import datetime
# # # #
# # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # #     NasabahLoader
# # # # )
# # # # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# # # #     PinjamanRepository
# # # # )
# # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # #     RekeningRepository
# # # # )
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # from bank_djago.services.pinjaman.pinjaman_service import (
# # # #     PinjamanService
# # # # )
# # # #
# # # #
# # # # ID_PINJAMAN = 8
# # # # NIK_PENGUJIAN = "0000111122223333"
# # # # NOREK_PENGUJIAN = "3001781978899033"
# # # #
# # # #
# # # # def ambil_snapshot_database():
# # # #     """
# # # #     Mengambil kondisi penting dari database.
# # # #
# # # #     Seluruh nilai ini akan dibandingkan sebelum dan setelah
# # # #     percobaan pembayaran yang seharusnya ditolak.
# # # #     """
# # # #     koneksi = buat_koneksi()
# # # #
# # # #     try:
# # # #         data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
# # # #             ID_PINJAMAN,
# # # #             koneksi
# # # #         )
# # # #
# # # #         data_rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # #             NOREK_PENGUJIAN,
# # # #             koneksi
# # # #         )
# # # #
# # # #         if data_pinjaman is None:
# # # #             raise AssertionError("Pinjaman ID 8 tidak ditemukan")
# # # #
# # # #         if data_rekening is None:
# # # #             raise AssertionError("Rekening pengujian tidak ditemukan")
# # # #
# # # #         jumlah_transaksi = koneksi.execute(
# # # #             """
# # # #             SELECT COUNT(*) AS jumlah
# # # #             FROM transaksi
# # # #             """
# # # #         ).fetchone()["jumlah"]
# # # #
# # # #         jumlah_riwayat = koneksi.execute(
# # # #             """
# # # #             SELECT COUNT(*) AS jumlah
# # # #             FROM riwayat
# # # #             """
# # # #         ).fetchone()["jumlah"]
# # # #
# # # #         jumlah_audit = koneksi.execute(
# # # #             """
# # # #             SELECT COUNT(*) AS jumlah
# # # #             FROM audit
# # # #             """
# # # #         ).fetchone()["jumlah"]
# # # #
# # # #         jumlah_pembayaran_pinjaman = koneksi.execute(
# # # #             """
# # # #             SELECT COUNT(*) AS jumlah
# # # #             FROM transaksi
# # # #             WHERE jenis = 'pembayaran_cicilan'
# # # #               AND jenis_referensi = 'pinjaman'
# # # #               AND id_referensi = ?
# # # #             """,
# # # #             (ID_PINJAMAN,)
# # # #         ).fetchone()["jumlah"]
# # # #
# # # #         return {
# # # #             "pinjaman": dict(data_pinjaman),
# # # #             "rekening": dict(data_rekening),
# # # #             "jumlah_transaksi": jumlah_transaksi,
# # # #             "jumlah_riwayat": jumlah_riwayat,
# # # #             "jumlah_audit": jumlah_audit,
# # # #             "jumlah_pembayaran_pinjaman": (
# # # #                 jumlah_pembayaran_pinjaman
# # # #             )
# # # #         }
# # # #
# # # #     finally:
# # # #         koneksi.close()
# # # #
# # # #
# # # # # ============================================================
# # # # # 1. MEMUAT OBJEK NASABAH
# # # # # ============================================================
# # # #
# # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # #
# # # # if nasabah is None:
# # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # #
# # # #
# # # # rekening = next(
# # # #     (
# # # #         rekening
# # # #         for rekening in nasabah.rekening
# # # #         if rekening.norek == NOREK_PENGUJIAN
# # # #     ),
# # # #     None
# # # # )
# # # #
# # # # if rekening is None:
# # # #     raise AssertionError("Objek rekening tidak ditemukan")
# # # #
# # # #
# # # # pinjaman = next(
# # # #     (
# # # #         pinjaman
# # # #         for pinjaman in nasabah.daftar_pinjaman
# # # #         if pinjaman.ID == ID_PINJAMAN
# # # #     ),
# # # #     None
# # # # )
# # # #
# # # # if pinjaman is None:
# # # #     raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")
# # # #
# # # #
# # # # # ============================================================
# # # # # 2. MENYIMPAN KONDISI AWAL
# # # # # ============================================================
# # # #
# # # # snapshot_sebelum = ambil_snapshot_database()
# # # #
# # # # data_pinjaman = snapshot_sebelum["pinjaman"]
# # # #
# # # # assert data_pinjaman["status"] == "aktif", (
# # # #     "Pinjaman ID 8 tidak berstatus aktif"
# # # # )
# # # #
# # # # assert data_pinjaman["cicilan_terbayar"] == 1, (
# # # #     "Pinjaman ID 8 bukan berada setelah cicilan pertama"
# # # # )
# # # #
# # # #
# # # # tanggal_pencairan = datetime.date.fromisoformat(
# # # #     data_pinjaman["tanggal_pencairan"]
# # # # )
# # # #
# # # # tanggal_boleh_bayar = PinjamanService.tanggal_boleh_bayar(
# # # #     cicilan_terbayar=data_pinjaman["cicilan_terbayar"],
# # # #     tanggal_pencairan=tanggal_pencairan
# # # # )
# # # #
# # # # # Mengambil satu hari sebelum tanggal yang diperbolehkan.
# # # # # Berdasarkan data saat ini, kemungkinan tanggal ini adalah
# # # # # tanggal jatuh tempo periode sebelumnya.
# # # # hari_pengujian = (
# # # #     tanggal_boleh_bayar - datetime.timedelta(days=1)
# # # # )
# # # #
# # # #
# # # # snapshot_objek_sebelum = {
# # # #     "status": pinjaman.status,
# # # #     "cicilan_terbayar": pinjaman.cicilan_terbayar,
# # # #     "sisa_pokok": pinjaman.sisa_pokok,
# # # #     "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
# # # #     "saldo": rekening.saldo,
# # # #     "jumlah_riwayat": len(rekening.riwayat)
# # # # }
# # # #
# # # #
# # # # print("=== PENGUJIAN PEMBAYARAN TERLALU AWAL ===")
# # # # print("ID pinjaman         :", ID_PINJAMAN)
# # # # print("Cicilan terbayar    :", data_pinjaman["cicilan_terbayar"])
# # # # print("Hari pengujian      :", hari_pengujian)
# # # # print("Baru boleh membayar :", tanggal_boleh_bayar)
# # # # print("Saldo sebelum       :", snapshot_sebelum["rekening"]["saldo"])
# # # # print()
# # # #
# # # #
# # # # # ============================================================
# # # # # 3. MENCOBA MEMBAYAR TERLALU AWAL
# # # # # ============================================================
# # # #
# # # # try:
# # # #     PinjamanService.bayar_cicilan(
# # # #         id_pinjaman=ID_PINJAMAN,
# # # #         nasabah=nasabah,
# # # #         hari_ini=hari_pengujian
# # # #     )
# # # #
# # # # except ValueError as error:
# # # #     # Memastikan kegagalan benar-benar berasal dari validasi tanggal,
# # # #     # bukan dari masalah lain seperti saldo atau objek yang hilang.
# # # #     assert str(error).startswith(
# # # #         "Cicilan selanjutnya baru boleh dibayar mulai"
# # # #     ), (
# # # #         "Pembayaran gagal karena alasan yang tidak diharapkan: "
# # # #         f"{error}"
# # # #     )
# # # #
# # # #     print("✅ Pembayaran terlalu awal berhasil ditolak")
# # # #     print("Pesan error:", error)
# # # #
# # # # else:
# # # #     raise AssertionError(
# # # #         "Pembayaran cicilan terlalu awal justru berhasil"
# # # #     )
# # # #
# # # #
# # # # # ============================================================
# # # # # 4. MEMERIKSA DATABASE SETELAH PENOLAKAN
# # # # # ============================================================
# # # #
# # # # snapshot_setelah = ambil_snapshot_database()
# # # #
# # # # snapshot_objek_setelah = {
# # # #     "status": pinjaman.status,
# # # #     "cicilan_terbayar": pinjaman.cicilan_terbayar,
# # # #     "sisa_pokok": pinjaman.sisa_pokok,
# # # #     "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
# # # #     "saldo": rekening.saldo,
# # # #     "jumlah_riwayat": len(rekening.riwayat)
# # # # }
# # # #
# # # #
# # # # # Data pinjaman harus tetap sama persis.
# # # # assert (
# # # #     snapshot_setelah["pinjaman"]
# # # #     == snapshot_sebelum["pinjaman"]
# # # # ), "Data pinjaman berubah setelah pembayaran ditolak"
# # # #
# # # # # Saldo dan seluruh data rekening harus tetap sama.
# # # # assert (
# # # #     snapshot_setelah["rekening"]
# # # #     == snapshot_sebelum["rekening"]
# # # # ), "Data rekening berubah setelah pembayaran ditolak"
# # # #
# # # # assert (
# # # #     snapshot_setelah["jumlah_transaksi"]
# # # #     == snapshot_sebelum["jumlah_transaksi"]
# # # # ), "Transaksi baru muncul setelah pembayaran ditolak"
# # # #
# # # # assert (
# # # #     snapshot_setelah["jumlah_riwayat"]
# # # #     == snapshot_sebelum["jumlah_riwayat"]
# # # # ), "Riwayat baru muncul setelah pembayaran ditolak"
# # # #
# # # # assert (
# # # #     snapshot_setelah["jumlah_audit"]
# # # #     == snapshot_sebelum["jumlah_audit"]
# # # # ), "Audit baru muncul setelah pembayaran ditolak"
# # # #
# # # # assert (
# # # #     snapshot_setelah["jumlah_pembayaran_pinjaman"]
# # # #     == snapshot_sebelum["jumlah_pembayaran_pinjaman"]
# # # # ), "Jumlah transaksi cicilan ID 8 berubah"
# # # #
# # # # # Karena kegagalan terjadi sebelum commit, objek Python
# # # # # juga harus tetap berada pada kondisi awal.
# # # # assert snapshot_objek_setelah == snapshot_objek_sebelum, (
# # # #     "Objek Python berubah setelah pembayaran ditolak"
# # # # )
# # # #
# # # #
# # # # print()
# # # # print("=== KONDISI SETELAH PENOLAKAN ===")
# # # # print("Status pinjaman    :", snapshot_setelah["pinjaman"]["status"])
# # # # print(
# # # #     "Cicilan terbayar   :",
# # # #     snapshot_setelah["pinjaman"]["cicilan_terbayar"]
# # # # )
# # # # print(
# # # #     "Sisa pokok         :",
# # # #     snapshot_setelah["pinjaman"]["sisa_pokok"]
# # # # )
# # # # print(
# # # #     "Saldo rekening     :",
# # # #     snapshot_setelah["rekening"]["saldo"]
# # # # )
# # # # print(
# # # #     "Jumlah pembayaran  :",
# # # #     snapshot_setelah["jumlah_pembayaran_pinjaman"]
# # # # )
# # # #
# # # # print()
# # # # print(
# # # #     "✅ VALIDASI WAKTU BERHASIL: pembayaran terlalu awal "
# # # #     "ditolak dan seluruh state tetap sama"
# # # # )
# # #
# # #
# # #
# # #
# # # import datetime
# # #
# # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # #     NasabahLoader
# # # )
# # # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# # #     PinjamanRepository
# # # )
# # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # #     RekeningRepository
# # # )
# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # from bank_djago.services.pinjaman.pinjaman_service import (
# # #     PinjamanService
# # # )
# # # from bank_djago.utils.utility import StatusPinjaman, Utilitas
# # #
# # #
# # # ID_PINJAMAN = 8
# # # NIK_PENGUJIAN = "0000111122223333"
# # # NOREK_PENGUJIAN = "3001781978899033"
# # #
# # # # Kita melewati masa toleransi sebanyak tiga hari.
# # # TAMBAHAN_HARI_DENDA = 3
# # #
# # #
# # # # ============================================================
# # # # 1. MEMUAT OBJEK NASABAH, REKENING, DAN PINJAMAN
# # # # ============================================================
# # #
# # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # #
# # # if nasabah is None:
# # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # #
# # #
# # # rekening = next(
# # #     (
# # #         rekening
# # #         for rekening in nasabah.rekening
# # #         if rekening.norek == NOREK_PENGUJIAN
# # #     ),
# # #     None
# # # )
# # #
# # # if rekening is None:
# # #     raise AssertionError("Objek rekening tidak ditemukan")
# # #
# # #
# # # pinjaman = next(
# # #     (
# # #         pinjaman
# # #         for pinjaman in nasabah.daftar_pinjaman
# # #         if pinjaman.ID == ID_PINJAMAN
# # #     ),
# # #     None
# # # )
# # #
# # # if pinjaman is None:
# # #     raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")
# # #
# # #
# # # # ============================================================
# # # # 2. MEMBACA KONDISI SEBELUM PEMBAYARAN
# # # # ============================================================
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     data_pinjaman_sebelum = dict(
# # #         PinjamanRepository.cari_pinjaman_dengan_id(
# # #             ID_PINJAMAN,
# # #             koneksi
# # #         )
# # #     )
# # #
# # #     data_rekening_sebelum = dict(
# # #         RekeningRepository.cari_rekening_dengan_norek(
# # #             NOREK_PENGUJIAN,
# # #             koneksi
# # #         )
# # #     )
# # #
# # #     jumlah_pembayaran_sebelum = koneksi.execute(
# # #         """
# # #         SELECT COUNT(*) AS jumlah
# # #         FROM transaksi
# # #         WHERE jenis = 'pembayaran_cicilan'
# # #           AND jenis_referensi = 'pinjaman'
# # #           AND id_referensi = ?
# # #         """,
# # #         (ID_PINJAMAN,)
# # #     ).fetchone()["jumlah"]
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # assert data_pinjaman_sebelum["status"] == "aktif", (
# # #     "Pinjaman ID 8 tidak berstatus aktif"
# # # )
# # #
# # # assert data_pinjaman_sebelum["cicilan_terbayar"] == 1, (
# # #     "Pinjaman ID 8 bukan berada setelah cicilan pertama"
# # # )
# # #
# # #
# # # # ============================================================
# # # # 3. MENGHITUNG HASIL YANG DIHARAPKAN
# # # # ============================================================
# # #
# # # saldo_sebelum = data_rekening_sebelum["saldo"]
# # # sisa_pokok_sebelum = data_pinjaman_sebelum["sisa_pokok"]
# # #
# # # cicilan_tetap = data_pinjaman_sebelum["cicilan_tetap"]
# # # bunga = data_pinjaman_sebelum["bunga"]
# # #
# # # tanggal_jatuh_tempo = datetime.date.fromisoformat(
# # #     data_pinjaman_sebelum["tanggal_jatuh_tempo"]
# # # )
# # #
# # # # Hari pengujian berada tiga hari setelah masa toleransi.
# # # hari_pengujian = (
# # #     tanggal_jatuh_tempo
# # #     + datetime.timedelta(
# # #         days=(
# # #             PinjamanService.BATAS_HARI_TUNGGAKAN
# # #             + TAMBAHAN_HARI_DENDA
# # #         )
# # #     )
# # # )
# # #
# # # hari_terlambat_diharapkan = (
# # #     PinjamanService.BATAS_HARI_TUNGGAKAN
# # #     + TAMBAHAN_HARI_DENDA
# # # )
# # #
# # # hari_denda_diharapkan = TAMBAHAN_HARI_DENDA
# # #
# # # denda_sebelum_batas = (
# # #     cicilan_tetap
# # #     * hari_denda_diharapkan
# # #     * PinjamanService.PERSENTASE_DENDA_HARIAN
# # # )
# # #
# # # denda_maksimal = (
# # #     cicilan_tetap
# # #     * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
# # # )
# # #
# # # denda_diharapkan = round(
# # #     min(denda_sebelum_batas, denda_maksimal)
# # # )
# # #
# # # bunga_bulanan_diharapkan = round(
# # #     sisa_pokok_sebelum * (bunga / 12)
# # # )
# # #
# # # pokok_dibayar_diharapkan = (
# # #     cicilan_tetap - bunga_bulanan_diharapkan
# # # )
# # #
# # # sisa_pokok_diharapkan = (
# # #     sisa_pokok_sebelum - pokok_dibayar_diharapkan
# # # )
# # #
# # # total_bayar_diharapkan = (
# # #     cicilan_tetap + denda_diharapkan
# # # )
# # #
# # # saldo_diharapkan = (
# # #     saldo_sebelum - total_bayar_diharapkan
# # # )
# # #
# # # jatuh_tempo_diharapkan = Utilitas.tambah_bulan(
# # #     tanggal_jatuh_tempo,
# # #     1
# # # )
# # #
# # #
# # # print("=== KONDISI SEBELUM PEMBAYARAN TERLAMBAT ===")
# # # print("ID pinjaman       :", ID_PINJAMAN)
# # # print("Cicilan terbayar  :", data_pinjaman_sebelum["cicilan_terbayar"])
# # # print("Sisa pokok        :", sisa_pokok_sebelum)
# # # print("Saldo rekening    :", saldo_sebelum)
# # # print("Jatuh tempo       :", tanggal_jatuh_tempo)
# # # print("Hari pengujian    :", hari_pengujian)
# # # print()
# # #
# # # print("=== PERHITUNGAN YANG DIHARAPKAN ===")
# # # print("Hari terlambat    :", hari_terlambat_diharapkan)
# # # print("Hari terkena denda:", hari_denda_diharapkan)
# # # print("Cicilan tetap     :", cicilan_tetap)
# # # print("Denda             :", denda_diharapkan)
# # # print("Bunga bulan ini   :", bunga_bulanan_diharapkan)
# # # print("Pokok dibayar     :", pokok_dibayar_diharapkan)
# # # print("Total pembayaran  :", total_bayar_diharapkan)
# # # print()
# # #
# # #
# # # # ============================================================
# # # # 4. MENJALANKAN PEMBAYARAN
# # # # ============================================================
# # #
# # # pinjaman_hasil = PinjamanService.bayar_cicilan(
# # #     id_pinjaman=ID_PINJAMAN,
# # #     nasabah=nasabah,
# # #     hari_ini=hari_pengujian
# # # )
# # #
# # #
# # # # ============================================================
# # # # 5. MEMERIKSA OBJEK PYTHON
# # # # ============================================================
# # #
# # # assert pinjaman_hasil is pinjaman, (
# # #     "Service mengembalikan objek pinjaman yang berbeda"
# # # )
# # #
# # # assert pinjaman_hasil.status == StatusPinjaman.AKTIF, (
# # #     "Pinjaman seharusnya masih aktif"
# # # )
# # #
# # # assert pinjaman_hasil.cicilan_terbayar == 2, (
# # #     "Cicilan terbayar pada objek bukan dua"
# # # )
# # #
# # # assert pinjaman_hasil.sisa_pokok == sisa_pokok_diharapkan, (
# # #     "Sisa pokok pada objek tidak sesuai"
# # # )
# # #
# # # assert (
# # #     pinjaman_hasil.tanggal_jatuh_tempo
# # #     == jatuh_tempo_diharapkan
# # # ), "Jatuh tempo objek tidak sesuai"
# # #
# # # assert rekening.saldo == saldo_diharapkan, (
# # #     "Saldo objek rekening tidak sesuai"
# # # )
# # #
# # # print("✅ State objek Python berhasil diperbarui")
# # #
# # #
# # # # ============================================================
# # # # 6. MEMBACA HASIL DARI SQLITE
# # # # ============================================================
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     data_pinjaman_setelah = PinjamanRepository.cari_pinjaman_dengan_id(
# # #         ID_PINJAMAN,
# # #         koneksi
# # #     )
# # #
# # #     data_rekening_setelah = RekeningRepository.cari_rekening_dengan_norek(
# # #         NOREK_PENGUJIAN,
# # #         koneksi
# # #     )
# # #
# # #     transaksi = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM transaksi
# # #         WHERE jenis = 'pembayaran_cicilan'
# # #           AND jenis_referensi = 'pinjaman'
# # #           AND id_referensi = ?
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (ID_PINJAMAN,)
# # #     ).fetchone()
# # #
# # #     if transaksi is None:
# # #         raise AssertionError(
# # #             "Transaksi pembayaran terlambat tidak ditemukan"
# # #         )
# # #
# # #     daftar_riwayat = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM riwayat
# # #         WHERE transaksi_id = ?
# # #         ORDER BY id
# # #         """,
# # #         (transaksi["id"],)
# # #     ).fetchall()
# # #
# # #     daftar_audit = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM audit
# # #         WHERE transaksi_id = ?
# # #         ORDER BY id
# # #         """,
# # #         (transaksi["id"],)
# # #     ).fetchall()
# # #
# # #
# # #     print()
# # #     print("=== KONDISI SETELAH PEMBAYARAN ===")
# # #     print("Status pinjaman   :", data_pinjaman_setelah["status"])
# # #     print("Cicilan terbayar  :", data_pinjaman_setelah["cicilan_terbayar"])
# # #     print("Sisa pokok        :", data_pinjaman_setelah["sisa_pokok"])
# # #     print("Jatuh tempo baru  :", data_pinjaman_setelah["tanggal_jatuh_tempo"])
# # #     print("Saldo rekening    :", data_rekening_setelah["saldo"])
# # #     print()
# # #
# # #     print("=== DATA TRANSAKSI ===")
# # #     print("ID transaksi      :", transaksi["id"])
# # #     print("Jenis             :", transaksi["jenis"])
# # #     print("Rekening sumber   :", transaksi["norek_sumber"])
# # #     print("Nominal cicilan   :", transaksi["nominal"])
# # #     print("Denda             :", transaksi["biaya"])
# # #     print("Saldo awal        :", transaksi["saldo_sumber_sebelum"])
# # #     print("Saldo akhir       :", transaksi["saldo_sumber_sesudah"])
# # #     print("Jenis referensi   :", transaksi["jenis_referensi"])
# # #     print("ID referensi      :", transaksi["id_referensi"])
# # #     print("Waktu             :", transaksi["waktu"])
# # #     print()
# # #
# # #     print("=== RIWAYAT TERHUBUNG ===")
# # #     for riwayat in daftar_riwayat:
# # #         print(
# # #             f"ID {riwayat['id']} | "
# # #             f"Transaksi {riwayat['transaksi_id']} | "
# # #             f"{riwayat['jenis']} | "
# # #             f"{riwayat['log']}"
# # #         )
# # #
# # #     print()
# # #     print("=== AUDIT TERHUBUNG ===")
# # #     for audit in daftar_audit:
# # #         print(
# # #             f"ID {audit['id']} | "
# # #             f"Transaksi {audit['transaksi_id']} | "
# # #             f"{audit['jenis']} | "
# # #             f"{audit['log']}"
# # #         )
# # #
# # #
# # #     # ========================================================
# # #     # 7. MEMASTIKAN HASIL DATABASE
# # #     # ========================================================
# # #
# # #     assert data_pinjaman_setelah["status"] == "aktif", (
# # #         "Pinjaman seharusnya masih aktif"
# # #     )
# # #
# # #     assert data_pinjaman_setelah["cicilan_terbayar"] == 2, (
# # #         "Cicilan terbayar di database bukan dua"
# # #     )
# # #
# # #     assert (
# # #         data_pinjaman_setelah["sisa_pokok"]
# # #         == sisa_pokok_diharapkan
# # #     ), "Sisa pokok di database tidak sesuai"
# # #
# # #     assert (
# # #         data_pinjaman_setelah["tanggal_jatuh_tempo"]
# # #         == jatuh_tempo_diharapkan.isoformat()
# # #     ), "Jatuh tempo baru tidak sesuai"
# # #
# # #     assert data_rekening_setelah["saldo"] == saldo_diharapkan, (
# # #         "Saldo rekening di database tidak sesuai"
# # #     )
# # #
# # #     assert transaksi["norek_sumber"] == NOREK_PENGUJIAN, (
# # #         "Rekening sumber transaksi salah"
# # #     )
# # #
# # #     assert transaksi["nominal"] == cicilan_tetap, (
# # #         "Nominal transaksi tidak sama dengan cicilan tetap"
# # #     )
# # #
# # #     assert transaksi["biaya"] == denda_diharapkan, (
# # #         "Denda transaksi tidak sesuai"
# # #     )
# # #
# # #     assert transaksi["saldo_sumber_sebelum"] == saldo_sebelum, (
# # #         "Snapshot saldo sebelum pembayaran salah"
# # #     )
# # #
# # #     assert transaksi["saldo_sumber_sesudah"] == saldo_diharapkan, (
# # #         "Snapshot saldo setelah pembayaran salah"
# # #     )
# # #
# # #     assert transaksi["jenis_referensi"] == "pinjaman", (
# # #         "Jenis referensi transaksi bukan pinjaman"
# # #     )
# # #
# # #     assert transaksi["id_referensi"] == ID_PINJAMAN, (
# # #         "ID referensi transaksi salah"
# # #     )
# # #
# # #     assert len(daftar_riwayat) == 1, (
# # #         "Jumlah riwayat terhubung bukan satu"
# # #     )
# # #
# # #     assert len(daftar_audit) == 1, (
# # #         "Jumlah audit terhubung bukan satu"
# # #     )
# # #
# # #     jumlah_pembayaran_setelah = koneksi.execute(
# # #         """
# # #         SELECT COUNT(*) AS jumlah
# # #         FROM transaksi
# # #         WHERE jenis = 'pembayaran_cicilan'
# # #           AND jenis_referensi = 'pinjaman'
# # #           AND id_referensi = ?
# # #         """,
# # #         (ID_PINJAMAN,)
# # #     ).fetchone()["jumlah"]
# # #
# # #     assert jumlah_pembayaran_setelah == (
# # #         jumlah_pembayaran_sebelum + 1
# # #     ), "Jumlah pembayaran tidak bertambah tepat satu"
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # print()
# # # print(
# # #     "✅ PEMBAYARAN TERLAMBAT BERHASIL: denda, saldo, "
# # #     "sisa pokok, jadwal, transaksi, riwayat, audit, "
# # #     "dan objek Python tersimpan dengan benar"
# # # )
# #
# #
# #
# # from unittest.mock import patch
# # import datetime
# #
# # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# #     NasabahLoader
# # )
# # from bank_djago.penyimpanan.repositories.audit_repository import (
# #     AuditRepository
# # )
# # from bank_djago.penyimpanan.repositories.pinjaman_repository import (
# #     PinjamanRepository
# # )
# # from bank_djago.penyimpanan.repositories.rekening_repository import (
# #     RekeningRepository
# # )
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # from bank_djago.services.pinjaman.pinjaman_service import (
# #     PinjamanService
# # )
# # from bank_djago.utils.utility import StatusPinjaman
# #
# #
# # ID_PINJAMAN = 8
# # NIK_PENGUJIAN = "0000111122223333"
# # NOREK_PENGUJIAN = "3001781978899033"
# #
# #
# # def ambil_snapshot_database():
# #     """
# #     Mengambil kondisi yang harus tetap sama jika pembayaran
# #     cicilan mengalami rollback.
# #     """
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
# #             ID_PINJAMAN,
# #             koneksi
# #         )
# #
# #         data_rekening = RekeningRepository.cari_rekening_dengan_norek(
# #             NOREK_PENGUJIAN,
# #             koneksi
# #         )
# #
# #         if data_pinjaman is None:
# #             raise AssertionError("Pinjaman ID 8 tidak ditemukan")
# #
# #         if data_rekening is None:
# #             raise AssertionError("Rekening pengujian tidak ditemukan")
# #
# #         jumlah_transaksi = koneksi.execute(
# #             "SELECT COUNT(*) AS jumlah FROM transaksi"
# #         ).fetchone()["jumlah"]
# #
# #         jumlah_riwayat = koneksi.execute(
# #             "SELECT COUNT(*) AS jumlah FROM riwayat"
# #         ).fetchone()["jumlah"]
# #
# #         jumlah_audit = koneksi.execute(
# #             "SELECT COUNT(*) AS jumlah FROM audit"
# #         ).fetchone()["jumlah"]
# #
# #         jumlah_pembayaran = koneksi.execute(
# #             """
# #             SELECT COUNT(*) AS jumlah
# #             FROM transaksi
# #             WHERE jenis = 'pembayaran_cicilan'
# #               AND jenis_referensi = 'pinjaman'
# #               AND id_referensi = ?
# #             """,
# #             (ID_PINJAMAN,)
# #         ).fetchone()["jumlah"]
# #
# #         return {
# #             "pinjaman": dict(data_pinjaman),
# #             "rekening": dict(data_rekening),
# #             "jumlah_transaksi": jumlah_transaksi,
# #             "jumlah_riwayat": jumlah_riwayat,
# #             "jumlah_audit": jumlah_audit,
# #             "jumlah_pembayaran": jumlah_pembayaran
# #         }
# #
# #     finally:
# #         koneksi.close()
# #
# #
# # # ============================================================
# # # 1. MEMUAT OBJEK YANG DIGUNAKAN SERVICE
# # # ============================================================
# #
# # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# #
# # if nasabah is None:
# #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# #
# #
# # rekening = next(
# #     (
# #         rekening
# #         for rekening in nasabah.rekening
# #         if rekening.norek == NOREK_PENGUJIAN
# #     ),
# #     None
# # )
# #
# # if rekening is None:
# #     raise AssertionError("Objek rekening tidak ditemukan")
# #
# #
# # pinjaman = next(
# #     (
# #         pinjaman
# #         for pinjaman in nasabah.daftar_pinjaman
# #         if pinjaman.ID == ID_PINJAMAN
# #     ),
# #     None
# # )
# #
# # if pinjaman is None:
# #     raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")
# #
# #
# # # ============================================================
# # # 2. MENYIMPAN KONDISI SEBELUM PEMBAYARAN
# # # ============================================================
# #
# # snapshot_sebelum = ambil_snapshot_database()
# #
# # assert snapshot_sebelum["pinjaman"]["status"] == "aktif", (
# #     "Pinjaman ID 8 tidak aktif"
# # )
# #
# # assert snapshot_sebelum["pinjaman"]["cicilan_terbayar"] == 2, (
# #     "Pinjaman ID 8 bukan berada setelah cicilan kedua"
# # )
# #
# #
# # # Menggunakan tanggal jatuh tempo saat ini agar pembayaran
# # # sudah diperbolehkan dan dapat mencapai penyimpanan audit.
# # hari_pengujian = datetime.date.fromisoformat(
# #     snapshot_sebelum["pinjaman"]["tanggal_jatuh_tempo"]
# # )
# #
# #
# # snapshot_objek_sebelum = {
# #     "status": pinjaman.status,
# #     "sisa_pokok": pinjaman.sisa_pokok,
# #     "cicilan_terbayar": pinjaman.cicilan_terbayar,
# #     "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
# #     "saldo": rekening.saldo,
# #     "jumlah_riwayat": len(rekening.riwayat)
# # }
# #
# #
# # print("=== KONDISI SEBELUM PENGUJIAN ROLLBACK ===")
# # print("ID pinjaman       :", ID_PINJAMAN)
# # print(
# #     "Cicilan terbayar  :",
# #     snapshot_sebelum["pinjaman"]["cicilan_terbayar"]
# # )
# # print(
# #     "Sisa pokok        :",
# #     snapshot_sebelum["pinjaman"]["sisa_pokok"]
# # )
# # print(
# #     "Saldo rekening    :",
# #     snapshot_sebelum["rekening"]["saldo"]
# # )
# # print("Hari pengujian    :", hari_pengujian)
# # print(
# #     "Jumlah pembayaran :",
# #     snapshot_sebelum["jumlah_pembayaran"]
# # )
# # print()
# #
# #
# # # ============================================================
# # # 3. MEMBUAT KEGAGALAN PADA PENYIMPANAN AUDIT
# # # ============================================================
# #
# # def gagalkan_audit(*args, **kwargs):
# #     """
# #     Menggantikan AuditRepository.tambah_audit untuk sementara.
# #
# #     Ketika service mencapai penyimpanan audit, error ini membuat
# #     seluruh transaksi SQLite harus di-rollback.
# #     """
# #     raise RuntimeError(
# #         "Kegagalan audit untuk menguji rollback pembayaran cicilan"
# #     )
# #
# #
# # with patch.object(
# #     AuditRepository,
# #     "tambah_audit",
# #     side_effect=gagalkan_audit
# # ):
# #     try:
# #         PinjamanService.bayar_cicilan(
# #             id_pinjaman=ID_PINJAMAN,
# #             nasabah=nasabah,
# #             hari_ini=hari_pengujian
# #         )
# #
# #     except RuntimeError as error:
# #         assert str(error) == (
# #             "Kegagalan audit untuk menguji rollback "
# #             "pembayaran cicilan"
# #         )
# #
# #         print("✅ Kegagalan buatan berhasil dipicu")
# #         print("Pesan error:", error)
# #
# #     else:
# #         raise AssertionError(
# #             "Pembayaran tetap berhasil meskipun audit digagalkan"
# #         )
# #
# #
# # # ============================================================
# # # 4. MEMBACA ULANG DATABASE SETELAH ROLLBACK
# # # ============================================================
# #
# # snapshot_setelah = ambil_snapshot_database()
# #
# # snapshot_objek_setelah = {
# #     "status": pinjaman.status,
# #     "sisa_pokok": pinjaman.sisa_pokok,
# #     "cicilan_terbayar": pinjaman.cicilan_terbayar,
# #     "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
# #     "saldo": rekening.saldo,
# #     "jumlah_riwayat": len(rekening.riwayat)
# # }
# #
# #
# # print()
# # print("=== KONDISI SETELAH ROLLBACK ===")
# # print(
# #     "Status pinjaman   :",
# #     snapshot_setelah["pinjaman"]["status"]
# # )
# # print(
# #     "Cicilan terbayar  :",
# #     snapshot_setelah["pinjaman"]["cicilan_terbayar"]
# # )
# # print(
# #     "Sisa pokok        :",
# #     snapshot_setelah["pinjaman"]["sisa_pokok"]
# # )
# # print(
# #     "Saldo rekening    :",
# #     snapshot_setelah["rekening"]["saldo"]
# # )
# # print(
# #     "Jumlah pembayaran :",
# #     snapshot_setelah["jumlah_pembayaran"]
# # )
# # print()
# #
# #
# # # ============================================================
# # # 5. MEMASTIKAN SELURUH DATABASE TIDAK BERUBAH
# # # ============================================================
# #
# # assert (
# #     snapshot_setelah["pinjaman"]
# #     == snapshot_sebelum["pinjaman"]
# # ), "Data pinjaman berubah setelah rollback"
# #
# # assert (
# #     snapshot_setelah["rekening"]
# #     == snapshot_sebelum["rekening"]
# # ), "Data rekening berubah setelah rollback"
# #
# # assert (
# #     snapshot_setelah["jumlah_transaksi"]
# #     == snapshot_sebelum["jumlah_transaksi"]
# # ), "Transaksi pembayaran masih tersisa"
# #
# # assert (
# #     snapshot_setelah["jumlah_riwayat"]
# #     == snapshot_sebelum["jumlah_riwayat"]
# # ), "Riwayat pembayaran masih tersisa"
# #
# # assert (
# #     snapshot_setelah["jumlah_audit"]
# #     == snapshot_sebelum["jumlah_audit"]
# # ), "Jumlah audit berubah setelah rollback"
# #
# # assert (
# #     snapshot_setelah["jumlah_pembayaran"]
# #     == snapshot_sebelum["jumlah_pembayaran"]
# # ), "Jumlah pembayaran cicilan ID 8 berubah"
# #
# #
# # # ============================================================
# # # 6. MEMASTIKAN OBJEK PYTHON TIDAK BERUBAH
# # # ============================================================
# #
# # assert snapshot_objek_setelah == snapshot_objek_sebelum, (
# #     "State objek Python berubah meskipun pembayaran gagal"
# # )
# #
# # assert pinjaman.status == StatusPinjaman.AKTIF, (
# #     "Status objek pinjaman tidak lagi aktif"
# # )
# #
# # assert pinjaman.cicilan_terbayar == 2, (
# #     "Jumlah cicilan objek berubah setelah rollback"
# # )
# #
# #
# # print(
# #     "\n✅ ROLLBACK PEMBAYARAN CICILAN BERHASIL: "
# #     "saldo, sisa pokok, jumlah cicilan, jadwal, transaksi, "
# #     "riwayat, audit, dan objek Python tidak berubah"
# # )
#
#
#
# import datetime
#
# from bank_djago.penyimpanan.loaders.nasabah_loader import (
#     NasabahLoader
# )
# from bank_djago.penyimpanan.repositories.pinjaman_repository import (
#     PinjamanRepository
# )
# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.services.pinjaman.pinjaman_service import (
#     PinjamanService
# )
# from bank_djago.utils.utility import StatusPinjaman
#
#
# ID_PINJAMAN = 8
# NIK_PENGUJIAN = "0000111122223333"
# NOREK_PENGUJIAN = "3001781978899033"
#
# JUMLAH_PEMBAYARAN = 4
#
#
# def ambil_data():
#     """Membaca kondisi terbaru pinjaman dan rekening dari SQLite."""
#     koneksi = buat_koneksi()
#
#     try:
#         data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
#             ID_PINJAMAN,
#             koneksi
#         )
#
#         data_rekening = RekeningRepository.cari_rekening_dengan_norek(
#             NOREK_PENGUJIAN,
#             koneksi
#         )
#
#         jumlah_transaksi = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM transaksi
#             WHERE jenis = 'pembayaran_cicilan'
#               AND jenis_referensi = 'pinjaman'
#               AND id_referensi = ?
#             """,
#             (ID_PINJAMAN,)
#         ).fetchone()["jumlah"]
#
#         return {
#             "pinjaman": dict(data_pinjaman),
#             "rekening": dict(data_rekening),
#             "jumlah_transaksi": jumlah_transaksi
#         }
#
#     finally:
#         koneksi.close()
#
#
# # ============================================================
# # 1. MEMUAT OBJEK
# # ============================================================
#
# nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# if nasabah is None:
#     raise AssertionError("Nasabah pengujian tidak ditemukan")
#
#
# rekening = next(
#     (
#         rekening
#         for rekening in nasabah.rekening
#         if rekening.norek == NOREK_PENGUJIAN
#     ),
#     None
# )
#
# if rekening is None:
#     raise AssertionError("Objek rekening tidak ditemukan")
#
#
# pinjaman = next(
#     (
#         pinjaman
#         for pinjaman in nasabah.daftar_pinjaman
#         if pinjaman.ID == ID_PINJAMAN
#     ),
#     None
# )
#
# if pinjaman is None:
#     raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")
#
#
# # ============================================================
# # 2. MEMASTIKAN KONDISI AWAL
# # ============================================================
#
# kondisi_awal = ambil_data()
# data_awal = kondisi_awal["pinjaman"]
#
# assert data_awal["status"] == "aktif", (
#     "Pinjaman ID 8 tidak aktif"
# )
#
# assert data_awal["cicilan_terbayar"] == 2, (
#     "Pengujian harus dimulai setelah tepat dua cicilan"
# )
#
# sisa_cicilan = (
#     data_awal["tenor"] - data_awal["cicilan_terbayar"]
# )
#
# assert sisa_cicilan == JUMLAH_PEMBAYARAN, (
#     f"Sisa cicilan bukan {JUMLAH_PEMBAYARAN}"
# )
#
#
# saldo_awal = kondisi_awal["rekening"]["saldo"]
# cicilan_tetap = data_awal["cicilan_tetap"]
# jumlah_transaksi_awal = kondisi_awal["jumlah_transaksi"]
#
# id_transaksi_baru = []
#
#
# print("=== KONDISI AWAL PELUNASAN ===")
# print("ID pinjaman       :", ID_PINJAMAN)
# print("Tenor             :", data_awal["tenor"])
# print("Cicilan terbayar  :", data_awal["cicilan_terbayar"])
# print("Sisa pembayaran   :", sisa_cicilan)
# print("Sisa pokok        :", data_awal["sisa_pokok"])
# print("Saldo rekening    :", saldo_awal)
# print()
#
#
# # ============================================================
# # 3. MEMBAYAR TEPAT EMPAT KALI
# # ============================================================
#
# for nomor_pembayaran in range(3, 7):
#     kondisi_sebelum = ambil_data()
#     pinjaman_sebelum = kondisi_sebelum["pinjaman"]
#
#     # Memastikan loop tidak melompati atau mengulang cicilan.
#     assert pinjaman_sebelum["cicilan_terbayar"] == (
#         nomor_pembayaran - 1
#     ), "Urutan pembayaran cicilan tidak sesuai"
#
#     assert pinjaman_sebelum["status"] == "aktif", (
#         "Pinjaman menjadi tidak aktif terlalu cepat"
#     )
#
#     # Pembayaran dilakukan tepat pada tanggal jatuh tempo.
#     # Karena tidak terlambat, denda yang diharapkan adalah nol.
#     hari_pembayaran = datetime.date.fromisoformat(
#         pinjaman_sebelum["tanggal_jatuh_tempo"]
#     )
#
#     jumlah_transaksi_sebelum = (
#         kondisi_sebelum["jumlah_transaksi"]
#     )
#
#     print(f"--- MEMBAYAR CICILAN KE-{nomor_pembayaran} ---")
#     print("Hari pembayaran :", hari_pembayaran)
#     print("Sisa pokok awal :", pinjaman_sebelum["sisa_pokok"])
#
#     hasil = PinjamanService.bayar_cicilan(
#         id_pinjaman=ID_PINJAMAN,
#         nasabah=nasabah,
#         hari_ini=hari_pembayaran
#     )
#
#     assert hasil is pinjaman, (
#         "Service mengembalikan objek pinjaman yang berbeda"
#     )
#
#     kondisi_setelah = ambil_data()
#     pinjaman_setelah = kondisi_setelah["pinjaman"]
#
#     assert pinjaman_setelah["cicilan_terbayar"] == (
#         nomor_pembayaran
#     ), "Jumlah cicilan tidak bertambah tepat satu"
#
#     assert kondisi_setelah["jumlah_transaksi"] == (
#         jumlah_transaksi_sebelum + 1
#     ), "Transaksi tidak bertambah tepat satu"
#
#     # Mengambil transaksi yang baru saja dibuat.
#     koneksi = buat_koneksi()
#
#     try:
#         transaksi_terbaru = koneksi.execute(
#             """
#             SELECT *
#             FROM transaksi
#             WHERE jenis = 'pembayaran_cicilan'
#               AND jenis_referensi = 'pinjaman'
#               AND id_referensi = ?
#             ORDER BY id DESC
#             LIMIT 1
#             """,
#             (ID_PINJAMAN,)
#         ).fetchone()
#
#     finally:
#         koneksi.close()
#
#     if transaksi_terbaru is None:
#         raise AssertionError(
#             f"Transaksi cicilan ke-{nomor_pembayaran} tidak ditemukan"
#         )
#
#     assert transaksi_terbaru["nominal"] == cicilan_tetap, (
#         "Nominal transaksi tidak sama dengan cicilan tetap"
#     )
#
#     assert transaksi_terbaru["biaya"] == 0, (
#         "Pembayaran tepat waktu seharusnya tidak memiliki denda"
#     )
#
#     id_transaksi_baru.append(transaksi_terbaru["id"])
#
#     print("Sisa pokok akhir :", pinjaman_setelah["sisa_pokok"])
#     print("Status           :", pinjaman_setelah["status"])
#     print("ID transaksi     :", transaksi_terbaru["id"])
#     print()
#
#
# # ============================================================
# # 4. MEMERIKSA KONDISI SETELAH EMPAT PEMBAYARAN
# # ============================================================
#
# kondisi_akhir = ambil_data()
# pinjaman_akhir = kondisi_akhir["pinjaman"]
# rekening_akhir = kondisi_akhir["rekening"]
#
# saldo_yang_diharapkan = (
#     saldo_awal - (cicilan_tetap * JUMLAH_PEMBAYARAN)
# )
#
#
# assert pinjaman_akhir["cicilan_terbayar"] == 6, (
#     "Jumlah cicilan terbayar bukan enam"
# )
#
# assert pinjaman_akhir["status"] == "lunas", (
#     "Status pinjaman belum berubah menjadi lunas"
# )
#
# assert pinjaman_akhir["sisa_pokok"] == 0, (
#     "Sisa pokok pinjaman belum menjadi nol"
# )
#
# assert rekening_akhir["saldo"] == saldo_yang_diharapkan, (
#     "Saldo rekening setelah empat pembayaran tidak sesuai"
# )
#
# assert kondisi_akhir["jumlah_transaksi"] == (
#     jumlah_transaksi_awal + JUMLAH_PEMBAYARAN
# ), "Jumlah transaksi tidak bertambah tepat empat"
#
#
# # Memastikan objek Python juga diselaraskan.
# assert pinjaman.status == StatusPinjaman.LUNAS, (
#     "Status objek pinjaman belum menjadi lunas"
# )
#
# assert pinjaman.cicilan_terbayar == 6, (
#     "Cicilan terbayar pada objek bukan enam"
# )
#
# assert pinjaman.sisa_pokok == 0, (
#     "Sisa pokok pada objek belum menjadi nol"
# )
#
# assert rekening.saldo == saldo_yang_diharapkan, (
#     "Saldo objek rekening tidak sesuai"
# )
#
#
# # ============================================================
# # 5. MEMERIKSA RIWAYAT DAN AUDIT EMPAT TRANSAKSI
# # ============================================================
#
# koneksi = buat_koneksi()
#
# try:
#     for id_transaksi in id_transaksi_baru:
#         jumlah_riwayat = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM riwayat
#             WHERE transaksi_id = ?
#             """,
#             (id_transaksi,)
#         ).fetchone()["jumlah"]
#
#         jumlah_audit = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM audit
#             WHERE transaksi_id = ?
#             """,
#             (id_transaksi,)
#         ).fetchone()["jumlah"]
#
#         assert jumlah_riwayat == 1, (
#             f"Transaksi {id_transaksi} tidak memiliki satu riwayat"
#         )
#
#         assert jumlah_audit == 1, (
#             f"Transaksi {id_transaksi} tidak memiliki satu audit"
#         )
#
#     transaksi_pelunasan = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE id = ?
#         """,
#         (id_transaksi_baru[-1],)
#     ).fetchone()
#
#     riwayat_pelunasan = koneksi.execute(
#         """
#         SELECT *
#         FROM riwayat
#         WHERE transaksi_id = ?
#         """,
#         (id_transaksi_baru[-1],)
#     ).fetchone()
#
#     audit_pelunasan = koneksi.execute(
#         """
#         SELECT *
#         FROM audit
#         WHERE transaksi_id = ?
#         """,
#         (id_transaksi_baru[-1],)
#     ).fetchone()
#
# finally:
#     koneksi.close()
#
#
# assert transaksi_pelunasan["id_referensi"] == ID_PINJAMAN, (
#     "Transaksi terakhir tidak menunjuk pinjaman ID 8"
# )
#
# assert "PELUNASAN PINJAMAN" in riwayat_pelunasan["log"], (
#     "Riwayat terakhir bukan riwayat pelunasan"
# )
#
# assert "telah melunasi" in audit_pelunasan["log"], (
#     "Audit terakhir bukan audit pelunasan"
# )
#
#
# print("=== KONDISI AKHIR ===")
# print("Status pinjaman   :", pinjaman_akhir["status"])
# print("Cicilan terbayar  :", pinjaman_akhir["cicilan_terbayar"])
# print("Sisa pokok        :", pinjaman_akhir["sisa_pokok"])
# print("Saldo rekening    :", rekening_akhir["saldo"])
# print("Transaksi baru    :", id_transaksi_baru)
# print()
#
# print(
#     "✅ EMPAT PEMBAYARAN BERHASIL: cicilan ke-3 sampai "
#     "ke-6 tersimpan dan pinjaman ID 8 telah lunas"
# )


from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot():
    """
    Mengambil kondisi database untuk memastikan pembayaran
    setelah lunas tidak meninggalkan perubahan.
    """
    koneksi = buat_koneksi()

    try:
        pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            ID_PINJAMAN,
            koneksi
        )

        rekening = RekeningRepository.cari_rekening_dengan_norek(
            NOREK_PENGUJIAN,
            koneksi
        )

        jumlah_transaksi = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM transaksi"
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM riwayat"
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM audit"
        ).fetchone()["jumlah"]

        jumlah_pembayaran = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'pembayaran_cicilan'
              AND jenis_referensi = 'pinjaman'
              AND id_referensi = ?
            """,
            (ID_PINJAMAN,)
        ).fetchone()["jumlah"]

        return {
            "pinjaman": dict(pinjaman),
            "rekening": dict(rekening),
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "jumlah_pembayaran": jumlah_pembayaran
        }

    finally:
        koneksi.close()


# Memuat nasabah karena service tetap membutuhkan konteks pemilik.
nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)

if nasabah is None:
    raise AssertionError("Nasabah pengujian tidak ditemukan")


snapshot_sebelum = ambil_snapshot()

assert snapshot_sebelum["pinjaman"]["status"] == "lunas", (
    "Pinjaman ID 8 belum berstatus lunas"
)

assert snapshot_sebelum["pinjaman"]["cicilan_terbayar"] == 6, (
    "Jumlah cicilan terbayar bukan enam"
)

assert snapshot_sebelum["pinjaman"]["sisa_pokok"] == 0, (
    "Sisa pokok pinjaman belum nol"
)


print("=== KONDISI SEBELUM PERCOBAAN PEMBAYARAN KETUJUH ===")
print("Status            :", snapshot_sebelum["pinjaman"]["status"])
print(
    "Cicilan terbayar :",
    snapshot_sebelum["pinjaman"]["cicilan_terbayar"]
)
print("Sisa pokok        :", snapshot_sebelum["pinjaman"]["sisa_pokok"])
print("Saldo rekening    :", snapshot_sebelum["rekening"]["saldo"])
print("Jumlah pembayaran :", snapshot_sebelum["jumlah_pembayaran"])
print()


# Service seharusnya berhenti saat menemukan status bukan 'aktif'.
try:
    PinjamanService.bayar_cicilan(
        id_pinjaman=ID_PINJAMAN,
        nasabah=nasabah
    )

except ValueError as error:
    assert str(error) == "Pinjaman sedang tidak aktif", (
        f"Pembayaran ditolak karena alasan berbeda: {error}"
    )

    print("✅ Pembayaran ketujuh berhasil ditolak")
    print("Pesan error:", error)

else:
    raise AssertionError(
        "Pinjaman yang sudah lunas masih dapat dibayar"
    )


snapshot_setelah = ambil_snapshot()


# Memastikan tidak ada data yang berubah.
assert (
    snapshot_setelah["pinjaman"]
    == snapshot_sebelum["pinjaman"]
), "Data pinjaman berubah"

assert (
    snapshot_setelah["rekening"]
    == snapshot_sebelum["rekening"]
), "Data rekening berubah"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi baru muncul"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat baru muncul"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Audit baru muncul"

assert (
    snapshot_setelah["jumlah_pembayaran"]
    == snapshot_sebelum["jumlah_pembayaran"]
), "Jumlah pembayaran berubah"


print()
print(
    "✅ PEMBAYARAN SETELAH LUNAS BERHASIL DITOLAK "
    "DAN SELURUH DATA TETAP SAMA"
)