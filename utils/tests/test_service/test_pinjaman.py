# # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # NOMINAL_PENGUJIAN = 2_000_000
# # # # # # # # # TENOR_PENGUJIAN = 6
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # --------------------------------------------------
# # # # # # # # # # AMBIL DATA MENTAH DARI SQLITE
# # # # # # # # # # --------------------------------------------------
# # # # # # # # #
# # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # #
# # # # # # # # # try:
# # # # # # # # #     data_pinjaman = koneksi.execute(
# # # # # # # # #         """
# # # # # # # # #         SELECT pinjaman.*
# # # # # # # # #         FROM pinjaman
# # # # # # # # #         JOIN rekening
# # # # # # # # #             ON rekening.norek = pinjaman.norek
# # # # # # # # #         WHERE rekening.nik_pemilik = ?
# # # # # # # # #           AND pinjaman.nominal_pinjaman = ?
# # # # # # # # #           AND pinjaman.tenor = ?
# # # # # # # # #         ORDER BY pinjaman.id DESC
# # # # # # # # #         LIMIT 1
# # # # # # # # #         """,
# # # # # # # # #         (
# # # # # # # # #             NIK_PENGUJIAN,
# # # # # # # # #             NOMINAL_PENGUJIAN,
# # # # # # # # #             TENOR_PENGUJIAN
# # # # # # # # #         )
# # # # # # # # #     ).fetchone()
# # # # # # # # #
# # # # # # # # # finally:
# # # # # # # # #     koneksi.close()
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # if data_pinjaman is None:
# # # # # # # # #     raise ValueError("Pinjaman pengujian tidak ditemukan di SQLite")
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # print("DATA PINJAMAN SQLITE")
# # # # # # # # # print("ID                 :", data_pinjaman["id"])
# # # # # # # # # print("Norek              :", data_pinjaman["norek"])
# # # # # # # # # print("Nominal            :", data_pinjaman["nominal_pinjaman"])
# # # # # # # # # print("Bunga              :", data_pinjaman["bunga"])
# # # # # # # # # print("Tenor              :", data_pinjaman["tenor"])
# # # # # # # # # print("Cicilan tetap      :", data_pinjaman["cicilan_tetap"])
# # # # # # # # # print("Sisa pokok         :", data_pinjaman["sisa_pokok"])
# # # # # # # # # print("Cicilan terbayar   :", data_pinjaman["cicilan_terbayar"])
# # # # # # # # # print("Status             :", data_pinjaman["status"])
# # # # # # # # # print("Tanggal pencairan  :", data_pinjaman["tanggal_pencairan"])
# # # # # # # # # print("Jatuh tempo        :", data_pinjaman["tanggal_jatuh_tempo"])
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # assert data_pinjaman["id"] is not None
# # # # # # # # # print("✅ Pinjaman memperoleh ID global SQLite")
# # # # # # # # #
# # # # # # # # # assert data_pinjaman["status"] == StatusPinjaman.DIAJUKAN.value
# # # # # # # # # print("✅ Status diajukan tersimpan di SQLite")
# # # # # # # # #
# # # # # # # # # assert data_pinjaman["nominal_pinjaman"] == NOMINAL_PENGUJIAN
# # # # # # # # # assert data_pinjaman["tenor"] == TENOR_PENGUJIAN
# # # # # # # # # print("✅ Nominal dan tenor tersimpan sesuai pengajuan")
# # # # # # # # #
# # # # # # # # # assert data_pinjaman["cicilan_tetap"] == 0
# # # # # # # # # assert data_pinjaman["cicilan_terbayar"] == 0
# # # # # # # # # assert data_pinjaman["sisa_pokok"] == NOMINAL_PENGUJIAN
# # # # # # # # # print("✅ State awal pinjaman tersimpan dengan benar")
# # # # # # # # #
# # # # # # # # # assert data_pinjaman["tanggal_pencairan"] is None
# # # # # # # # # assert data_pinjaman["tanggal_jatuh_tempo"] is None
# # # # # # # # # print("✅ Tanggal pinjaman masih kosong sebelum pencairan")
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # --------------------------------------------------
# # # # # # # # # # MUAT ULANG NASABAH DAN PINJAMAN
# # # # # # # # # # --------------------------------------------------
# # # # # # # # #
# # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # #
# # # # # # # # # pinjaman = next(
# # # # # # # # #     (
# # # # # # # # #         pinjaman
# # # # # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # # # # #         if pinjaman.ID == data_pinjaman["id"]
# # # # # # # # #     ),
# # # # # # # # #     None
# # # # # # # # # )
# # # # # # # # #
# # # # # # # # # if pinjaman is None:
# # # # # # # # #     raise ValueError(
# # # # # # # # #         "Pinjaman tidak berhasil dimuat oleh PinjamanLoader"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # print("\nHASIL PINJAMAN LOADER")
# # # # # # # # # print("ID                 :", pinjaman.ID)
# # # # # # # # # print("Nama pemilik       :", pinjaman.pemilik.nama)
# # # # # # # # # print("Norek              :", pinjaman.rekening.norek)
# # # # # # # # # print("Nominal            :", pinjaman.nominal_pinjaman)
# # # # # # # # # print("Bunga              :", pinjaman.bunga)
# # # # # # # # # print("Tenor              :", pinjaman.tenor)
# # # # # # # # # print("Status             :", pinjaman.status)
# # # # # # # # # print("Jumlah pinjaman    :", len(nasabah.daftar_pinjaman))
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # assert pinjaman.ID == data_pinjaman["id"]
# # # # # # # # # print("✅ ID pinjaman berhasil dipulihkan")
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # assert pinjaman.status == StatusPinjaman.DIAJUKAN
# # # # # # # # # assert isinstance(pinjaman.status, StatusPinjaman)
# # # # # # # # # print("✅ Status teks kembali menjadi StatusPinjaman")
# # # # # # # # #
# # # # # # # # # assert pinjaman.pemilik is nasabah
# # # # # # # # # print("✅ Pinjaman menunjuk objek nasabah yang benar")
# # # # # # # # #
# # # # # # # # # assert pinjaman.rekening in nasabah.rekening
# # # # # # # # # print("✅ Rekening pinjaman terdapat dalam daftar rekening nasabah")
# # # # # # # # #
# # # # # # # # # rekening_dari_daftar = next(
# # # # # # # # #     rekening
# # # # # # # # #     for rekening in nasabah.rekening
# # # # # # # # #     if rekening.norek == pinjaman.rekening.norek
# # # # # # # # # )
# # # # # # # # #
# # # # # # # # # assert pinjaman.rekening is rekening_dari_daftar
# # # # # # # # # print("✅ Pinjaman memakai objek rekening yang sama")
# # # # # # # # #
# # # # # # # # # assert pinjaman.nominal_pinjaman == NOMINAL_PENGUJIAN
# # # # # # # # # assert pinjaman.tenor == TENOR_PENGUJIAN
# # # # # # # # # assert pinjaman.sisa_pokok == NOMINAL_PENGUJIAN
# # # # # # # # # print("✅ Seluruh state pinjaman berhasil dimuat")
# # # # # # # # #
# # # # # # # # # print(
# # # # # # # # #     "\n✅ Pengajuan pinjaman dan PinjamanLoader "
# # # # # # # # #     "bekerja sesuai rancangan"
# # # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # #
# # # # # # # # # try:
# # # # # # # # #     print("DATA PINJAMAN")
# # # # # # # # #
# # # # # # # # #     semua_pinjaman = koneksi.execute(
# # # # # # # # #         """
# # # # # # # # #         SELECT id, norek, nominal_pinjaman, status
# # # # # # # # #         FROM pinjaman
# # # # # # # # #         ORDER BY id
# # # # # # # # #         """
# # # # # # # # #     ).fetchall()
# # # # # # # # #
# # # # # # # # #     for data in semua_pinjaman:
# # # # # # # # #         print(dict(data))
# # # # # # # # #
# # # # # # # # #     urutan = koneksi.execute(
# # # # # # # # #         """
# # # # # # # # #         SELECT seq
# # # # # # # # #         FROM sqlite_sequence
# # # # # # # # #         WHERE name = 'pinjaman'
# # # # # # # # #         """
# # # # # # # # #     ).fetchone()
# # # # # # # # #
# # # # # # # # #     print("\nID terakhir yang pernah dicatat SQLite:")
# # # # # # # # #     print(urutan["seq"] if urutan is not None else None)
# # # # # # # # #
# # # # # # # # # finally:
# # # # # # # # #     koneksi.close()
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # #
# # # # # # # # # try:
# # # # # # # # #     audit_pinjaman = koneksi.execute(
# # # # # # # # #         """
# # # # # # # # #         SELECT id, jenis, waktu, log, nik, norek
# # # # # # # # #         FROM audit
# # # # # # # # #         WHERE jenis LIKE '%pinjaman%'
# # # # # # # # #            OR log LIKE '%pinjaman%'
# # # # # # # # #         ORDER BY id
# # # # # # # # #         """
# # # # # # # # #     ).fetchall()
# # # # # # # # #
# # # # # # # # #     for audit in audit_pinjaman:
# # # # # # # # #         print(dict(audit))
# # # # # # # # #
# # # # # # # # # finally:
# # # # # # # # #     koneksi.close()
# # # # # # # #
# # # # # # # #
# # # # # # # #
# # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # # #
# # # # # # # #
# # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # ID_PINJAMAN = 5
# # # # # # # #
# # # # # # # #
# # # # # # # # # --------------------------------------------------
# # # # # # # # # PERIKSA DATA SQLITE
# # # # # # # # # --------------------------------------------------
# # # # # # # #
# # # # # # # # koneksi = buat_koneksi()
# # # # # # # #
# # # # # # # # try:
# # # # # # # #     data_pinjaman = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT pinjaman.*
# # # # # # # #         FROM pinjaman
# # # # # # # #         JOIN rekening
# # # # # # # #             ON rekening.norek = pinjaman.norek
# # # # # # # #         WHERE pinjaman.id = ?
# # # # # # # #           AND rekening.nik_pemilik = ?
# # # # # # # #         """,
# # # # # # # #         (ID_PINJAMAN, NIK_PENGUJIAN)
# # # # # # # #     ).fetchone()
# # # # # # # #
# # # # # # # #     audit_persetujuan = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM audit
# # # # # # # #         WHERE jenis = 'persetujuan pinjaman'
# # # # # # # #           AND nik = ?
# # # # # # # #           AND log LIKE ?
# # # # # # # #         ORDER BY id DESC
# # # # # # # #         LIMIT 1
# # # # # # # #         """,
# # # # # # # #         (
# # # # # # # #             NIK_PENGUJIAN,
# # # # # # # #             f"%ID {ID_PINJAMAN}%"
# # # # # # # #         )
# # # # # # # #     ).fetchone()
# # # # # # # #
# # # # # # # #     masih_diajukan = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM pinjaman
# # # # # # # #         WHERE id = ?
# # # # # # # #           AND status = 'diajukan'
# # # # # # # #         """,
# # # # # # # #         (ID_PINJAMAN,)
# # # # # # # #     ).fetchone()
# # # # # # # #
# # # # # # # # finally:
# # # # # # # #     koneksi.close()
# # # # # # # #
# # # # # # # #
# # # # # # # # if data_pinjaman is None:
# # # # # # # #     raise ValueError("Pinjaman pengujian tidak ditemukan")
# # # # # # # #
# # # # # # # #
# # # # # # # # print("DATA PINJAMAN SETELAH PERSETUJUAN")
# # # # # # # # print("ID                :", data_pinjaman["id"])
# # # # # # # # print("Norek             :", data_pinjaman["norek"])
# # # # # # # # print("Nominal           :", data_pinjaman["nominal_pinjaman"])
# # # # # # # # print("Status            :", data_pinjaman["status"])
# # # # # # # # print("Cicilan tetap     :", data_pinjaman["cicilan_tetap"])
# # # # # # # # print("Cicilan terbayar  :", data_pinjaman["cicilan_terbayar"])
# # # # # # # # print("Sisa pokok        :", data_pinjaman["sisa_pokok"])
# # # # # # # # print("Tanggal pencairan :", data_pinjaman["tanggal_pencairan"])
# # # # # # # # print("Jatuh tempo       :", data_pinjaman["tanggal_jatuh_tempo"])
# # # # # # # #
# # # # # # # #
# # # # # # # # assert (
# # # # # # # #     data_pinjaman["status"]
# # # # # # # #     == StatusPinjaman.DISETUJUI.value
# # # # # # # # )
# # # # # # # # print("✅ Status SQLite berubah menjadi disetujui")
# # # # # # # #
# # # # # # # # assert masih_diajukan is None
# # # # # # # # print("✅ Pinjaman hilang dari daftar pengajuan admin")
# # # # # # # #
# # # # # # # # assert data_pinjaman["cicilan_tetap"] == 0
# # # # # # # # assert data_pinjaman["cicilan_terbayar"] == 0
# # # # # # # # assert (
# # # # # # # #     data_pinjaman["sisa_pokok"]
# # # # # # # #     == data_pinjaman["nominal_pinjaman"]
# # # # # # # # )
# # # # # # # # print("✅ State pembayaran belum berubah")
# # # # # # # #
# # # # # # # # assert data_pinjaman["tanggal_pencairan"] is None
# # # # # # # # assert data_pinjaman["tanggal_jatuh_tempo"] is None
# # # # # # # # print("✅ Tanggal tetap kosong sebelum pencairan")
# # # # # # # #
# # # # # # # # assert audit_persetujuan is not None
# # # # # # # # print("✅ Audit persetujuan berhasil disimpan")
# # # # # # # #
# # # # # # # #
# # # # # # # # # --------------------------------------------------
# # # # # # # # # PERIKSA PINJAMAN LOADER
# # # # # # # # # --------------------------------------------------
# # # # # # # #
# # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
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
# # # # # # # #     raise ValueError(
# # # # # # # #         "Pinjaman tidak berhasil dimuat kembali"
# # # # # # # #     )
# # # # # # # #
# # # # # # # # print("\nHASIL LOADER SETELAH PERSETUJUAN")
# # # # # # # # print("ID             :", pinjaman.ID)
# # # # # # # # print("Nama pemilik   :", pinjaman.pemilik.nama)
# # # # # # # # print("Norek          :", pinjaman.rekening.norek)
# # # # # # # # print("Status         :", pinjaman.status)
# # # # # # # #
# # # # # # # # assert pinjaman.status == StatusPinjaman.DISETUJUI
# # # # # # # # print("✅ Loader memulihkan StatusPinjaman.DISETUJUI")
# # # # # # # #
# # # # # # # # assert pinjaman.pemilik is nasabah
# # # # # # # # print("✅ Relasi objek nasabah tetap benar")
# # # # # # # #
# # # # # # # # rekening_nasabah = next(
# # # # # # # #     rekening
# # # # # # # #     for rekening in nasabah.rekening
# # # # # # # #     if rekening.norek == pinjaman.rekening.norek
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert pinjaman.rekening is rekening_nasabah
# # # # # # # # print("✅ Relasi objek rekening tetap benar")
# # # # # # # #
# # # # # # # # print(
# # # # # # # #     "\n✅ Persetujuan pinjaman SQLite "
# # # # # # # #     "bekerja sesuai rancangan"
# # # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # # # #
# # # # # # #
# # # # # # ID_DISETUJUI = 5
# # # # # # ID_DITOLAK = 7
# # # # # # NIK_DITOLAK = "7777888899990000"
# # # # # # CATATAN_ADMIN = "pengajuan belum memenuhi syarat"
# # # # # #
# # # # # #
# # # # # # koneksi = buat_koneksi()
# # # # # #
# # # # # # try:
# # # # # #     pinjaman_disetujui = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM pinjaman
# # # # # #         WHERE id = ?
# # # # # #         """,
# # # # # #         (ID_DISETUJUI,)
# # # # # #     ).fetchone()
# # # # # #
# # # # # #     pinjaman_ditolak = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM pinjaman
# # # # # #         WHERE id = ?
# # # # # #         """,
# # # # # #         (ID_DITOLAK,)
# # # # # #     ).fetchone()
# # # # # #
# # # # # #     masih_diajukan = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM pinjaman
# # # # # #         WHERE id = ?
# # # # # #           AND status = 'diajukan'
# # # # # #         """,
# # # # # #         (ID_DITOLAK,)
# # # # # #     ).fetchone()
# # # # # #
# # # # # #     audit_penolakan = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM audit
# # # # # #         WHERE jenis = 'penolakan pinjaman'
# # # # # #           AND nik = ?
# # # # # #           AND log LIKE ?
# # # # # #         ORDER BY id DESC
# # # # # #         LIMIT 1
# # # # # #         """,
# # # # # #         (
# # # # # #             NIK_DITOLAK,
# # # # # #             f"%ID {ID_DITOLAK}%"
# # # # # #         )
# # # # # #     ).fetchone()
# # # # # #
# # # # # # finally:
# # # # # #     koneksi.close()
# # # # # # #
# # # # # # #
# # # # # # # if pinjaman_disetujui is None:
# # # # # # #     raise ValueError("Pinjaman ID 5 tidak ditemukan")
# # # # # # #
# # # # # # # if pinjaman_ditolak is None:
# # # # # # #     raise ValueError("Pinjaman ID 6 tidak ditemukan")
# # # # # # #
# # # # # # #
# # # # # # # print("HASIL KEPUTUSAN ADMIN")
# # # # # # # print(
# # # # # # #     f"Pinjaman ID {ID_DISETUJUI}:",
# # # # # # #     pinjaman_disetujui["status"]
# # # # # # # )
# # # # # # # print(
# # # # # # #     f"Pinjaman ID {ID_DITOLAK}:",
# # # # # # #     pinjaman_ditolak["status"]
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # assert (
# # # # # # #     pinjaman_disetujui["status"]
# # # # # # #     == StatusPinjaman.DISETUJUI.value
# # # # # # # )
# # # # # # # print("✅ Pinjaman sebelumnya tetap berstatus disetujui")
# # # # # # #
# # # # # # # assert (
# # # # # # #     pinjaman_ditolak["status"]
# # # # # # #     == StatusPinjaman.DITOLAK.value
# # # # # # # )
# # # # # # # print("✅ Status pinjaman baru berubah menjadi ditolak")
# # # # # # #
# # # # # # # assert masih_diajukan is None
# # # # # # # print("✅ Pinjaman ditolak hilang dari antrean admin")
# # # # # # #
# # # # # # # assert audit_penolakan is not None
# # # # # # # print("✅ Audit penolakan berhasil disimpan")
# # # # # # #
# # # # # # # print("Catatan dalam audit:", audit_penolakan["log"])
# # # # # # #
# # # # # # # assert CATATAN_ADMIN.lower() in audit_penolakan["log"].lower()
# # # # # # # print("✅ Catatan admin tersimpan dalam audit")
# # # # # # #
# # # # # # #
# # # # # # # # --------------------------------------------------
# # # # # # # # PERIKSA LOADER PINJAMAN DITOLAK
# # # # # # # # --------------------------------------------------
# # # # # # #
# # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_DITOLAK)
# # # # # # #
# # # # # # # pinjaman = next(
# # # # # # #     (
# # # # # # #         pinjaman
# # # # # # #         for pinjaman in nasabah.daftar_pinjaman
# # # # # # #         if pinjaman.ID == ID_DITOLAK
# # # # # # #     ),
# # # # # # #     None
# # # # # # # )
# # # # # # #
# # # # # # # if pinjaman is None:
# # # # # # #     raise ValueError(
# # # # # # #         "Pinjaman ditolak tidak berhasil dimuat kembali"
# # # # # # #     )
# # # # # # #
# # # # # # #
# # # # # # # print("\nHASIL LOADER PINJAMAN DITOLAK")
# # # # # # # print("ID           :", pinjaman.ID)
# # # # # # # print("Nama pemilik :", pinjaman.pemilik.nama)
# # # # # # # print("Norek        :", pinjaman.rekening.norek)
# # # # # # # print("Status       :", pinjaman.status)
# # # # # # #
# # # # # # # assert pinjaman.status == StatusPinjaman.DITOLAK
# # # # # # # print("✅ Loader memulihkan StatusPinjaman.DITOLAK")
# # # # # # #
# # # # # # # assert pinjaman.pemilik is nasabah
# # # # # # # print("✅ Relasi objek nasabah tetap benar")
# # # # # # #
# # # # # # # rekening_nasabah = next(
# # # # # # #     rekening
# # # # # # #     for rekening in nasabah.rekening
# # # # # # #     if rekening.norek == pinjaman.rekening.norek
# # # # # # # )
# # # # # # #
# # # # # # # assert pinjaman.rekening is rekening_nasabah
# # # # # # # print("✅ Relasi objek rekening tetap benar")
# # # # # # #
# # # # # # # print(
# # # # # # #     "\n✅ Penolakan pinjaman SQLite "
# # # # # # #     "bekerja sesuai rancangan"
# # # # # # # )
# # # # # #
# # # # # #
# # # # # # koneksi = buat_koneksi()
# # # # # #
# # # # # # try:
# # # # # #     daftar_kolom = koneksi.execute(
# # # # # #         "PRAGMA table_info(pinjaman)"
# # # # # #     ).fetchall()
# # # # # #
# # # # # #     for kolom in daftar_kolom:
# # # # # #         print(kolom["name"])
# # # # # # finally:
# # # # # #     koneksi.close()
# # # # #
# # # # #
# # # # #
# # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # from bank_djago.utils.utility import StatusPinjaman
# # # # #
# # # # #
# # # # # NIK_PENGUJIAN = "7777888899990000"
# # # # # NOREK_PENGUJIAN = "2001443311291615"
# # # # #
# # # # # # Harus sama persis dengan catatan yang kamu masukkan melalui UI.
# # # # # CATATAN_ADMIN = "testing catatan admin pada penolakan"
# # # # #
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     # Mengambil pinjaman terbaru milik rekening pengujian.
# # # # #     data_pinjaman = koneksi.execute(
# # # # #         """
# # # # #         SELECT
# # # # #             pinjaman.id,
# # # # #             pinjaman.norek,
# # # # #             pinjaman.status,
# # # # #             pinjaman.catatan_admin
# # # # #         FROM pinjaman
# # # # #         JOIN rekening
# # # # #             ON rekening.norek = pinjaman.norek
# # # # #         WHERE rekening.nik_pemilik = ?
# # # # #           AND pinjaman.norek = ?
# # # # #         ORDER BY pinjaman.id DESC
# # # # #         LIMIT 1
# # # # #         """,
# # # # #         (
# # # # #             NIK_PENGUJIAN,
# # # # #             NOREK_PENGUJIAN
# # # # #         )
# # # # #     ).fetchone()
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # if data_pinjaman is None:
# # # # #     raise ValueError(
# # # # #         "Pinjaman pengujian tidak ditemukan"
# # # # #     )
# # # # #
# # # # #
# # # # # print("HASIL PENGUJIAN PENOLAKAN")
# # # # # print("ID pinjaman  :", data_pinjaman["id"])
# # # # # print("NIK nasabah  :", NIK_PENGUJIAN)
# # # # # print("Norek        :", data_pinjaman["norek"])
# # # # # print("Status       :", data_pinjaman["status"])
# # # # # print("Catatan admin:", data_pinjaman["catatan_admin"])
# # # # #
# # # # #
# # # # # assert (
# # # # #     data_pinjaman["status"]
# # # # #     == StatusPinjaman.DITOLAK.value
# # # # # ), "Status pinjaman belum berubah menjadi ditolak"
# # # # #
# # # # # print("✅ Status pinjaman tersimpan sebagai ditolak")
# # # # #
# # # # #
# # # # # assert (
# # # # #     data_pinjaman["catatan_admin"]
# # # # #     == CATATAN_ADMIN
# # # # # ), "Catatan admin tidak tersimpan sesuai input UI"
# # # # #
# # # # # print("✅ Catatan admin berhasil tersimpan")
# # # # #
# # # # #
# # # # # print(
# # # # #     "\n✅ Pembaruan status dan catatan penolakan "
# # # # #     "berhasil diuji"
# # # # # )
# # # # #
# # # # #
# # # # # # def cek_audit():
# # # # # #     koneksi = buat_koneksi()
# # # # # #
# # # # # #     try:
# # # # # #         cursor = koneksi.execute("""SELECT *
# # # # # #         FROM audit
# # # # # #         ORDER BY id DESC
# # # # # #         LIMIT 1""")
# # # # # #         return cursor.fetchone()
# # # # # #
# # # # # #     finally:
# # # # # #         koneksi.close()
# # # # # #
# # # # # #
# # # # # # data = cek_audit()
# # # # # # print(dict(data))
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # #
# # # # koneksi = buat_koneksi()
# # # #
# # # # try:
# # # #     daftar_kolom = koneksi.execute(
# # # #         "PRAGMA table_info(rekening)"
# # # #     ).fetchall()
# # # #
# # # #     for kolom in daftar_kolom:
# # # #         print(kolom["name"], kolom["type"])
# # # #
# # # # finally:
# # # #     koneksi.close()
# # #
# # #
# # #
# # # from datetime import datetime
# # #
# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # #
# # #
# # # NOREK_PENGUJIAN = "3001781978899033"
# # #
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     data_rekening = koneksi.execute(
# # #         """
# # #         SELECT
# # #             norek,
# # #             nik_pemilik,
# # #             status,
# # #             waktu_dibuat
# # #         FROM rekening
# # #         WHERE norek = ?
# # #         """,
# # #         (NOREK_PENGUJIAN,)
# # #     ).fetchone()
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # if data_rekening is None:
# # #     raise ValueError("Rekening baru tidak ditemukan")
# # #
# # #
# # # print("HASIL PENGUJIAN WAKTU PEMBUKAAN")
# # # print("Norek        :", data_rekening["norek"])
# # # print("NIK pemilik  :", data_rekening["nik_pemilik"])
# # # print("Status       :", data_rekening["status"])
# # # print("Waktu dibuat :", data_rekening["waktu_dibuat"])
# # #
# # #
# # # assert data_rekening["waktu_dibuat"] is not None
# # # print("✅ waktu_dibuat berhasil disimpan")
# # #
# # #
# # # waktu_dibuat = datetime.fromisoformat(
# # #     data_rekening["waktu_dibuat"]
# # # )
# # #
# # # assert isinstance(waktu_dibuat, datetime)
# # # print("✅ waktu_dibuat tersimpan dalam format datetime ISO")
# # #
# # #
# # # selisih = datetime.now() - waktu_dibuat
# # #
# # # assert 0 <= selisih.total_seconds() < 300
# # # print("✅ waktu_dibuat sesuai dengan waktu pengujian")
# # #
# # #
# # # print("\n✅ Pembukaan rekening baru berhasil diuji")
# #
# #
# #
# # from datetime import datetime
# #
# # from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# #
# #
# # NOREK_PENGUJIAN = "3001781978899033"
# #
# # koneksi = buat_koneksi()
# # rekening = RekeningLoader.muat_rekening(
# #     NOREK_PENGUJIAN,
# # koneksi)
# #
# # if rekening is None:
# #     raise ValueError("Rekening gagal dimuat")
# #
# #
# # print("HASIL PENGUJIAN LOADER")
# # print("Norek        :", rekening.norek)
# # print("Waktu dibuat :", rekening.waktu_dibuat)
# # print("Tipe data    :", type(rekening.waktu_dibuat))
# #
# #
# # assert isinstance(rekening.waktu_dibuat, datetime)
# #
# # print("✅ Loader memulihkan waktu_dibuat sebagai datetime")
#
#
#
# import datetime
#
# from bank_djago.penyimpanan.loaders.rekening_loaders import (
#     RekeningLoader
# )
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
#
#
# NOREK_PENGUJIAN = "3001781978899033"
#
#
# # Mengambil waktu asli langsung dari SQLite
# koneksi = buat_koneksi()
#
# try:
#     data_rekening = koneksi.execute(
#         """
#         SELECT waktu_dibuat
#         FROM rekening
#         WHERE norek = ?
#         """,
#         (NOREK_PENGUJIAN,)
#     ).fetchone()
#
# finally:
#     koneksi.close()
#
#
# if data_rekening is None:
#     raise ValueError("Rekening pengujian tidak ditemukan")
#
#
# waktu_sqlite = datetime.datetime.fromisoformat(
#     data_rekening["waktu_dibuat"]
# )
#
#
# # Memuat rekening melalui loader
# koneksi = buat_koneksi()
#
# try:
#     rekening = RekeningLoader.muat_rekening(
#         norek=NOREK_PENGUJIAN,
#         koneksi=koneksi
#     )
# finally:
#     koneksi.close()
#
#
# if rekening is None:
#     raise ValueError("Loader gagal memuat rekening")
#
#
# print("Waktu SQLite:", waktu_sqlite)
# print("Waktu loader:", rekening.waktu_dibuat)
#
#
# assert rekening.waktu_dibuat == waktu_sqlite
#
# print("✅ Loader mempertahankan waktu_dibuat dari SQLite")

from bank_djago.penyimpanan.sqlite.database import buat_koneksi

koneksi = buat_koneksi()

try:
    daftar_kolom = koneksi.execute(
        "PRAGMA table_info(transaksi)"
    ).fetchall()

    for kolom in daftar_kolom:
        print(
            kolom["name"],
            kolom["type"],
            "NOT NULL:" if kolom["notnull"] else "NULLABLE"
        )

finally:
    koneksi.close()