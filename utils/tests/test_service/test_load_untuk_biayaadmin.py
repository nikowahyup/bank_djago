# # # # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # # # #     RekeningLoader
# # # # # )
# # # # #
# # # # #
# # # # # # Memuat rekening aktif dan blokir dari SQLite.
# # # # # daftar_rekening = (
# # # # #     RekeningLoader.muat_semua_rekening_berjalan()
# # # # # )
# # # # #
# # # # # print("=== REKENING YANG BERJALAN ===")
# # # # # print("Jumlah rekening:", len(daftar_rekening))
# # # # # print()
# # # # #
# # # # #
# # # # # # Menyimpan objek nasabah pertama untuk setiap NIK.
# # # # # # Ini digunakan untuk memastikan satu nasabah tidak dirangkai
# # # # # # menjadi beberapa objek selama proses loader yang sama.
# # # # # nasabah_index = {}
# # # # #
# # # # # for rekening in daftar_rekening:
# # # # #     nasabah = rekening.pemilik
# # # # #     nik = nasabah.NIK
# # # # #
# # # # #     print("Nomor rekening :", rekening.norek)
# # # # #     print("Status         :", rekening.status)
# # # # #     print("Saldo          :", rekening.saldo)
# # # # #     print("NIK pemilik    :", nik)
# # # # #     print("Nama pemilik   :", nasabah.nama)
# # # # #     print()
# # # # #
# # # # #     # Repository seharusnya sudah mengeluarkan rekening tutup
# # # # #     # dari hasil query.
# # # # #     assert rekening.status != "tutup", (
# # # # #         f"Rekening tutup {rekening.norek} masih ikut dimuat"
# # # # #     )
# # # # #
# # # # #     assert rekening.pemilik is not None, (
# # # # #         f"Rekening {rekening.norek} tidak memiliki objek pemilik"
# # # # #     )
# # # # #
# # # # #     if nik in nasabah_index:
# # # # #         # Rekening milik nasabah yang sama harus menunjuk
# # # # #         # objek nasabah Python yang sama.
# # # # #         assert rekening.pemilik is nasabah_index[nik], (
# # # # #             f"Nasabah {nik} dirangkai menjadi objek berbeda"
# # # # #         )
# # # # #
# # # # #     else:
# # # # #         nasabah_index[nik] = rekening.pemilik
# # # # #
# # # # #
# # # # # print(
# # # # #     "✅ LOADER REKENING BERHASIL: "
# # # # #     "seluruh rekening berjalan berhasil dimuat, "
# # # # #     "rekening tutup tidak ikut, dan identitas pemilik konsisten"
# # # # # )
# # # # #
# # # # #
# # # # #
# # # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # # #     RekeningLoader
# # # # )
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # from bank_djago.services.rekening.biaya_admin_service import (
# # # #     BiayaAdminService
# # # # )
# # # # from bank_djago.utils.utility import JenisTransaksi, Utilitas
# # # #
# # # #
# # # # NOREK_PENGUJIAN = "4001701216150609"
# # # # SALDO_AWAL = 512_000
# # # # BIAYA_ADMIN = 2_000
# # # #
# # # #
# # # # def muat_rekening():
# # # #     """
# # # #     Memuat objek rekening pengujian tanpa melibatkan scheduler.
# # # #     """
# # # #     koneksi = buat_koneksi()
# # # #
# # # #     try:
# # # #         return RekeningLoader.muat_rekening(
# # # #             norek=NOREK_PENGUJIAN,
# # # #             koneksi=koneksi
# # # #         )
# # # #     finally:
# # # #         koneksi.close()
# # # #
# # # #
# # # # def ambil_kondisi_database():
# # # #     """
# # # #     Mengambil keadaan rekening dan jumlah transaksi biaya admin.
# # # #     """
# # # #     koneksi = buat_koneksi()
# # # #
# # # #     try:
# # # #         rekening = koneksi.execute(
# # # #             """
# # # #             SELECT
# # # #                 norek,
# # # #                 saldo,
# # # #                 level,
# # # #                 status,
# # # #                 waktu_bayar_admin
# # # #             FROM rekening
# # # #             WHERE norek = ?
# # # #             """,
# # # #             (NOREK_PENGUJIAN,)
# # # #         ).fetchone()
# # # #
# # # #         jumlah_transaksi = koneksi.execute(
# # # #             """
# # # #             SELECT COUNT(*) AS jumlah
# # # #             FROM transaksi
# # # #             WHERE norek_sumber = ?
# # # #               AND jenis = ?
# # # #             """,
# # # #             (
# # # #                 NOREK_PENGUJIAN,
# # # #                 JenisTransaksi.BIAYA_ADMIN.value
# # # #             )
# # # #         ).fetchone()["jumlah"]
# # # #
# # # #         return {
# # # #             "rekening": dict(rekening) if rekening else None,
# # # #             "jumlah_transaksi": jumlah_transaksi
# # # #         }
# # # #
# # # #     finally:
# # # #         koneksi.close()
# # # #
# # # #
# # # # # Memuat rekening pengujian sebagai objek Python.
# # # # rekening = muat_rekening()
# # # #
# # # # if rekening is None:
# # # #     raise AssertionError(
# # # #         f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
# # # #     )
# # # #
# # # #
# # # # # Memastikan rekening masih berada pada kondisi awal.
# # # # assert rekening.level == 1, (
# # # #     "Rekening pengujian bukan rekening Reguler"
# # # # )
# # # #
# # # # assert rekening.saldo == SALDO_AWAL, (
# # # #     f"Saldo aktual Rp{Utilitas.format_rupiah(rekening.saldo)}, "
# # # #     f"bukan Rp{Utilitas.format_rupiah(SALDO_AWAL)}"
# # # # )
# # # #
# # # # assert rekening.biaya_admin == BIAYA_ADMIN, (
# # # #     "Biaya admin rekening Reguler bukan Rp2.000"
# # # # )
# # # #
# # # #
# # # # kondisi_sebelum = ambil_kondisi_database()
# # # #
# # # # periode_terakhir_dibayar = rekening.waktu_bayar_admin
# # # #
# # # # # Mensimulasikan satu bulan setelah periode terakhir dibayar.
# # # # hari_simulasi = Utilitas.tambah_bulan(
# # # #     periode_terakhir_dibayar,
# # # #     1
# # # # )
# # # #
# # # # saldo_yang_diharapkan = SALDO_AWAL - BIAYA_ADMIN
# # # #
# # # #
# # # # print("=== KONDISI SEBELUM PEMOTONGAN ===")
# # # # print("Nomor rekening       :", rekening.norek)
# # # # print("Level rekening       :", rekening.level)
# # # # print("Saldo                :", rekening.saldo)
# # # # print("Biaya admin          :", rekening.biaya_admin)
# # # # print("Periode terakhir     :", periode_terakhir_dibayar)
# # # # print("Hari simulasi        :", hari_simulasi)
# # # # print("Jumlah transaksi lama:",
# # # #       kondisi_sebelum["jumlah_transaksi"])
# # # # print()
# # # #
# # # #
# # # # # Memanggil service secara langsung tanpa scheduler.
# # # # total_dibayar = BiayaAdminService.potong_admin(
# # # #     rekening=rekening,
# # # #     hari_ini=hari_simulasi
# # # # )
# # # #
# # # #
# # # # kondisi_sesudah = ambil_kondisi_database()
# # # # data_rekening_sesudah = kondisi_sesudah["rekening"]
# # # #
# # # #
# # # # # Memastikan nilai yang dikembalikan service sesuai.
# # # # assert total_dibayar == BIAYA_ADMIN, (
# # # #     "Jumlah biaya admin yang dibayar tidak sesuai"
# # # # )
# # # #
# # # #
# # # # # Memastikan perubahan tersimpan di SQLite.
# # # # assert data_rekening_sesudah["saldo"] == saldo_yang_diharapkan, (
# # # #     "Saldo SQLite tidak berkurang sebesar biaya admin"
# # # # )
# # # #
# # # # assert (
# # # #     data_rekening_sesudah["waktu_bayar_admin"]
# # # #     == hari_simulasi.isoformat()
# # # # ), "Periode pembayaran admin di SQLite tidak sesuai"
# # # #
# # # #
# # # # # Memastikan tepat satu transaksi baru terbentuk.
# # # # assert (
# # # #     kondisi_sesudah["jumlah_transaksi"]
# # # #     == kondisi_sebelum["jumlah_transaksi"] + 1
# # # # ), "Transaksi biaya admin tidak bertambah tepat satu"
# # # #
# # # #
# # # # # Memastikan objek Python diperbarui setelah commit.
# # # # assert rekening.saldo == saldo_yang_diharapkan, (
# # # #     "Saldo objek rekening tidak ikut diperbarui"
# # # # )
# # # #
# # # # assert rekening.waktu_bayar_admin == hari_simulasi, (
# # # #     "Waktu bayar admin objek tidak ikut diperbarui"
# # # # )
# # # #
# # # #
# # # # print("=== KONDISI SETELAH PEMOTONGAN ===")
# # # # print("Total biaya admin :", total_dibayar)
# # # # print("Saldo SQLite      :", data_rekening_sesudah["saldo"])
# # # # print("Saldo objek       :", rekening.saldo)
# # # # print(
# # # #     "Periode terakhir  :",
# # # #     data_rekening_sesudah["waktu_bayar_admin"]
# # # # )
# # # # print(
# # # #     "Jumlah transaksi  :",
# # # #     kondisi_sesudah["jumlah_transaksi"]
# # # # )
# # # # print()
# # # #
# # # #
# # # # # Memanggil service lagi pada tanggal yang sama.
# # # # # Pemanggilan kedua tidak boleh memotong saldo kembali.
# # # # hasil_kedua = BiayaAdminService.potong_admin(
# # # #     rekening=rekening,
# # # #     hari_ini=hari_simulasi
# # # # )
# # # #
# # # # kondisi_setelah_panggilan_kedua = (
# # # #     ambil_kondisi_database()
# # # # )
# # # #
# # # # assert hasil_kedua == 0, (
# # # #     "Pemanggilan kedua seharusnya tidak membayar periode baru"
# # # # )
# # # #
# # # # assert (
# # # #     kondisi_setelah_panggilan_kedua["rekening"]["saldo"]
# # # #     == saldo_yang_diharapkan
# # # # ), "Saldo kembali terpotong pada tanggal yang sama"
# # # #
# # # # assert (
# # # #     kondisi_setelah_panggilan_kedua["jumlah_transaksi"]
# # # #     == kondisi_sesudah["jumlah_transaksi"]
# # # # ), "Transaksi ganda terbentuk pada tanggal yang sama"
# # # #
# # # #
# # # # print(
# # # #     "✅ PEMOTONGAN BIAYA ADMIN BERHASIL: "
# # # #     "saldo berkurang Rp2.000, periode diperbarui, "
# # # #     "dan pemanggilan kedua tidak memotong saldo lagi"
# # # # )
# # # #
# # # #
# # # #
# # # # # from bank_djago.penyimpanan.sqlite.database import (
# # # # #     buat_koneksi,
# # # # #     lokasi_database
# # # # # )
# # # # #
# # # # #
# # # # # NOREK = "4001701216150609"
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     rekening = koneksi.execute(
# # # # #         """
# # # # #         SELECT
# # # # #             norek,
# # # # #             saldo,
# # # # #             status,
# # # # #             waktu_bayar_admin
# # # # #         FROM rekening
# # # # #         WHERE norek = ?
# # # # #         """,
# # # # #         (NOREK,)
# # # # #     ).fetchone()
# # # # #
# # # # #     transaksi_setor = koneksi.execute(
# # # # #         """
# # # # #         SELECT
# # # # #             id,
# # # # #             jenis,
# # # # #             norek_tujuan,
# # # # #             nominal,
# # # # #             saldo_tujuan_sebelum,
# # # # #             saldo_tujuan_sesudah,
# # # # #             waktu
# # # # #         FROM transaksi
# # # # #         WHERE norek_tujuan = ?
# # # # #           AND jenis = 'setor_tunai'
# # # # #         ORDER BY id DESC
# # # # #         LIMIT 5
# # # # #         """,
# # # # #         (NOREK,)
# # # # #     ).fetchall()
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # print("=== LOKASI DATABASE ===")
# # # # # print(lokasi_database.resolve())
# # # # # print()
# # # # #
# # # # # print("=== DATA REKENING ===")
# # # # # print(dict(rekening) if rekening else None)
# # # # # print()
# # # # #
# # # # # print("=== TRANSAKSI SETOR TUNAI TERAKHIR ===")
# # # # #
# # # # # if not transaksi_setor:
# # # # #     print("Tidak ditemukan transaksi setor tunai")
# # # # # else:
# # # # #     for transaksi in transaksi_setor:
# # # # #         print(dict(transaksi))
# # #
# # #
# # #
# # #
# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # from bank_djago.utils.utility import JenisTransaksi
# # #
# # #
# # # NOREK_PENGUJIAN = "4001701216150609"
# # #
# # # BIAYA_ADMIN_YANG_DIHARAPKAN = 2_000
# # # SALDO_SEBELUM_YANG_DIHARAPKAN = 512_000
# # # SALDO_SESUDAH_YANG_DIHARAPKAN = 510_000
# # #
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     # Mengambil transaksi biaya admin terbaru milik
# # #     # rekening yang sedang kita uji.
# # #     transaksi = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM transaksi
# # #         WHERE jenis = ?
# # #           AND norek_sumber = ?
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (
# # #             JenisTransaksi.BIAYA_ADMIN.value,
# # #             NOREK_PENGUJIAN
# # #         )
# # #     ).fetchone()
# # #
# # #     if transaksi is None:
# # #         raise AssertionError(
# # #             "Transaksi biaya admin tidak ditemukan"
# # #         )
# # #
# # #     id_transaksi = transaksi["id"]
# # #
# # #     # Mengambil seluruh riwayat yang terhubung
# # #     # dengan transaksi biaya admin tersebut.
# # #     daftar_riwayat = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM riwayat
# # #         WHERE transaksi_id = ?
# # #         ORDER BY id
# # #         """,
# # #         (id_transaksi,)
# # #     ).fetchall()
# # #
# # #     # Mengambil seluruh audit yang terhubung
# # #     # dengan transaksi biaya admin yang sama.
# # #     daftar_audit = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM audit
# # #         WHERE transaksi_id = ?
# # #         ORDER BY id
# # #         """,
# # #         (id_transaksi,)
# # #     ).fetchall()
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # print("=== DATA TRANSAKSI BIAYA ADMIN ===")
# # # print("ID transaksi          :", transaksi["id"])
# # # print("Jenis transaksi       :", transaksi["jenis"])
# # # print("Rekening sumber       :", transaksi["norek_sumber"])
# # # print("Rekening tujuan       :", transaksi["norek_tujuan"])
# # # print("Nominal               :", transaksi["nominal"])
# # # print(
# # #     "Saldo sumber sebelum :",
# # #     transaksi["saldo_sumber_sebelum"]
# # # )
# # # print(
# # #     "Saldo sumber sesudah :",
# # #     transaksi["saldo_sumber_sesudah"]
# # # )
# # # print("Jenis referensi       :", transaksi["jenis_referensi"])
# # # print("ID referensi          :", transaksi["id_referensi"])
# # # print("Waktu                 :", transaksi["waktu"])
# # # print()
# # #
# # #
# # # # Memastikan data utama transaksi sudah benar.
# # # assert transaksi["jenis"] == JenisTransaksi.BIAYA_ADMIN.value, (
# # #     "Jenis transaksi bukan biaya admin"
# # # )
# # #
# # # assert transaksi["norek_sumber"] == NOREK_PENGUJIAN, (
# # #     "Nomor rekening sumber tidak sesuai"
# # # )
# # #
# # # assert transaksi["norek_tujuan"] is None, (
# # #     "Transaksi biaya admin tidak boleh memiliki rekening tujuan"
# # # )
# # #
# # # assert transaksi["nominal"] == BIAYA_ADMIN_YANG_DIHARAPKAN, (
# # #     "Nominal transaksi biaya admin tidak sesuai"
# # # )
# # #
# # # assert (
# # #     transaksi["saldo_sumber_sebelum"]
# # #     == SALDO_SEBELUM_YANG_DIHARAPKAN
# # # ), "Saldo sumber sebelum transaksi tidak sesuai"
# # #
# # # assert (
# # #     transaksi["saldo_sumber_sesudah"]
# # #     == SALDO_SESUDAH_YANG_DIHARAPKAN
# # # ), "Saldo sumber sesudah transaksi tidak sesuai"
# # #
# # # assert transaksi["jenis_referensi"] is None, (
# # #     "Biaya admin tidak membutuhkan jenis referensi"
# # # )
# # #
# # # assert transaksi["id_referensi"] is None, (
# # #     "Biaya admin tidak membutuhkan ID referensi"
# # # )
# # #
# # # assert transaksi["waktu"] is not None, (
# # #     "Waktu transaksi tidak tersimpan"
# # # )
# # #
# # # print("✅ Data transaksi biaya admin tersimpan dengan benar")
# # # print()
# # #
# # #
# # # print("=== RIWAYAT TERHUBUNG ===")
# # #
# # # assert len(daftar_riwayat) == 1, (
# # #     f"Seharusnya ada tepat satu riwayat, "
# # #     f"tetapi ditemukan {len(daftar_riwayat)}"
# # # )
# # #
# # # for riwayat in daftar_riwayat:
# # #     print(
# # #         f"ID {riwayat['id']} | "
# # #         f"Transaksi {riwayat['transaksi_id']} | "
# # #         f"Rekening {riwayat['norek']} | "
# # #         f"{riwayat['jenis']} | "
# # #         f"{riwayat['log']}"
# # #     )
# # #
# # #     assert riwayat["transaksi_id"] == id_transaksi, (
# # #         "Riwayat terhubung dengan transaksi yang salah"
# # #     )
# # #
# # #     assert riwayat["norek"] == NOREK_PENGUJIAN, (
# # #         "Riwayat tersimpan pada rekening yang salah"
# # #     )
# # #
# # # print("✅ Riwayat terhubung dengan transaksi biaya admin")
# # # print()
# # #
# # #
# # # print("=== AUDIT TERHUBUNG ===")
# # #
# # # assert len(daftar_audit) == 1, (
# # #     f"Seharusnya ada tepat satu audit, "
# # #     f"tetapi ditemukan {len(daftar_audit)}"
# # # )
# # #
# # # for audit in daftar_audit:
# # #     print(
# # #         f"ID {audit['id']} | "
# # #         f"Transaksi {audit['transaksi_id']} | "
# # #         f"Rekening {audit['norek']} | "
# # #         f"{audit['jenis']} | "
# # #         f"{audit['log']}"
# # #     )
# # #
# # #     assert audit["transaksi_id"] == id_transaksi, (
# # #         "Audit terhubung dengan transaksi yang salah"
# # #     )
# # #
# # #     assert audit["norek"] == NOREK_PENGUJIAN, (
# # #         "Audit tersimpan pada rekening yang salah"
# # #     )
# # #
# # # print("✅ Audit terhubung dengan transaksi biaya admin")
# # # print()
# # #
# # #
# # # print(
# # #     "✅ PENCATATAN BIAYA ADMIN BERHASIL: "
# # #     "transaksi, riwayat, dan audit terhubung "
# # #     "melalui transaksi_id yang sama"
# # # )
# #
# #
# # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# #     RekeningLoader
# # )
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # from bank_djago.services.rekening.biaya_admin_service import (
# #     BiayaAdminService
# # )
# # from bank_djago.utils.utility import JenisTransaksi, Utilitas
# #
# #
# # NOREK_PENGUJIAN = "4001701216150609"
# #
# # SALDO_AWAL = 504_000
# # BIAYA_ADMIN_PER_BULAN = 2_000
# # JUMLAH_PERIODE = 3
# #
# # TOTAL_BIAYA = BIAYA_ADMIN_PER_BULAN * JUMLAH_PERIODE
# # SALDO_AKHIR = SALDO_AWAL - TOTAL_BIAYA
# #
# #
# # def muat_rekening():
# #     """Memuat rekening pengujian sebagai objek Python."""
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         return RekeningLoader.muat_rekening(
# #             norek=NOREK_PENGUJIAN,
# #             koneksi=koneksi
# #         )
# #     finally:
# #         koneksi.close()
# #
# #
# # def ambil_kondisi_database():
# #     """
# #     Mengambil keadaan rekening dan jumlah transaksi biaya admin
# #     untuk membandingkan kondisi sebelum dan sesudah pemrosesan.
# #     """
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         rekening = koneksi.execute(
# #             """
# #             SELECT
# #                 norek,
# #                 saldo,
# #                 waktu_bayar_admin,
# #                 status
# #             FROM rekening
# #             WHERE norek = ?
# #             """,
# #             (NOREK_PENGUJIAN,)
# #         ).fetchone()
# #
# #         jumlah_transaksi = koneksi.execute(
# #             """
# #             SELECT COUNT(*) AS jumlah
# #             FROM transaksi
# #             WHERE norek_sumber = ?
# #               AND jenis = ?
# #             """,
# #             (
# #                 NOREK_PENGUJIAN,
# #                 JenisTransaksi.BIAYA_ADMIN.value
# #             )
# #         ).fetchone()["jumlah"]
# #
# #         return {
# #             "rekening": dict(rekening) if rekening else None,
# #             "jumlah_transaksi": jumlah_transaksi
# #         }
# #
# #     finally:
# #         koneksi.close()
# #
# #
# # def ambil_pencatatan_terbaru():
# #     """Mengambil transaksi terbaru beserta riwayat dan auditnya."""
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         transaksi = koneksi.execute(
# #             """
# #             SELECT *
# #             FROM transaksi
# #             WHERE norek_sumber = ?
# #               AND jenis = ?
# #             ORDER BY id DESC
# #             LIMIT 1
# #             """,
# #             (
# #                 NOREK_PENGUJIAN,
# #                 JenisTransaksi.BIAYA_ADMIN.value
# #             )
# #         ).fetchone()
# #
# #         if transaksi is None:
# #             raise AssertionError(
# #                 "Transaksi biaya admin tidak ditemukan"
# #             )
# #
# #         riwayat = koneksi.execute(
# #             """
# #             SELECT *
# #             FROM riwayat
# #             WHERE transaksi_id = ?
# #             """,
# #             (transaksi["id"],)
# #         ).fetchall()
# #
# #         audit = koneksi.execute(
# #             """
# #             SELECT *
# #             FROM audit
# #             WHERE transaksi_id = ?
# #             """,
# #             (transaksi["id"],)
# #         ).fetchall()
# #
# #         return transaksi, riwayat, audit
# #
# #     finally:
# #         koneksi.close()
# #
# #
# # rekening = muat_rekening()
# #
# # if rekening is None:
# #     raise AssertionError(
# #         f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
# #     )
# #
# #
# # # Pengamanan agar pengujian tidak dijalankan dua kali
# # # pada rekening yang sudah berubah.
# # assert rekening.saldo == SALDO_AWAL, (
# #     f"Saldo aktual Rp{Utilitas.format_rupiah(rekening.saldo)}, "
# #     f"bukan Rp{Utilitas.format_rupiah(SALDO_AWAL)}. "
# #     "Kemungkinan pengujian sudah pernah dijalankan."
# # )
# #
# # assert rekening.biaya_admin == BIAYA_ADMIN_PER_BULAN, (
# #     "Biaya admin rekening tidak sesuai"
# # )
# #
# #
# # periode_sebelum = rekening.waktu_bayar_admin
# #
# # # Bergerak tiga bulan dari periode terakhir:
# # # 6 Oktober 2026 → 6 Januari 2027.
# # hari_simulasi = Utilitas.tambah_bulan(
# #     periode_sebelum,
# #     JUMLAH_PERIODE
# # )
# #
# # daftar_periode = BiayaAdminService.cari_periode_admin(
# #     waktu_bayar_admin=periode_sebelum,
# #     hari_ini=hari_simulasi
# # )
# #
# # assert len(daftar_periode) == JUMLAH_PERIODE, (
# #     "Method cari_periode_admin tidak menghasilkan tiga periode"
# # )
# #
# # kondisi_sebelum = ambil_kondisi_database()
# #
# #
# # print("=== KONDISI SEBELUM PEMBAYARAN ===")
# # print("Nomor rekening   :", rekening.norek)
# # print("Saldo awal       :", rekening.saldo)
# # print("Biaya per bulan  :", rekening.biaya_admin)
# # print("Periode terakhir :", periode_sebelum)
# # print("Hari simulasi    :", hari_simulasi)
# # print("Periode tertunggak:")
# #
# # for periode in daftar_periode:
# #     print("-", periode)
# #
# # print()
# #
# #
# # # Membayar tiga periode sekaligus.
# # total_dibayar = BiayaAdminService.potong_admin(
# #     rekening=rekening,
# #     hari_ini=hari_simulasi
# # )
# #
# # kondisi_sesudah = ambil_kondisi_database()
# # data_rekening_sesudah = kondisi_sesudah["rekening"]
# #
# #
# # assert total_dibayar == TOTAL_BIAYA, (
# #     f"Total pembayaran seharusnya Rp"
# #     f"{Utilitas.format_rupiah(TOTAL_BIAYA)}"
# # )
# #
# # assert data_rekening_sesudah["saldo"] == SALDO_AKHIR, (
# #     "Saldo SQLite setelah pembayaran tidak sesuai"
# # )
# #
# # assert rekening.saldo == SALDO_AKHIR, (
# #     "Saldo objek Python tidak ikut diperbarui"
# # )
# #
# # assert (
# #     data_rekening_sesudah["waktu_bayar_admin"]
# #     == hari_simulasi.isoformat()
# # ), "Periode terakhir di SQLite tidak sesuai"
# #
# # assert rekening.waktu_bayar_admin == hari_simulasi, (
# #     "Periode terakhir pada objek Python tidak sesuai"
# # )
# #
# # assert (
# #     kondisi_sesudah["jumlah_transaksi"]
# #     == kondisi_sebelum["jumlah_transaksi"] + 1
# # ), "Pembayaran tiga bulan harus menghasilkan satu transaksi"
# #
# #
# # transaksi, daftar_riwayat, daftar_audit = (
# #     ambil_pencatatan_terbaru()
# # )
# #
# #
# # assert transaksi["nominal"] == TOTAL_BIAYA, (
# #     "Nominal transaksi bukan total tiga bulan"
# # )
# #
# # assert transaksi["saldo_sumber_sebelum"] == SALDO_AWAL, (
# #     "Saldo sebelum pada transaksi tidak sesuai"
# # )
# #
# # assert transaksi["saldo_sumber_sesudah"] == SALDO_AKHIR, (
# #     "Saldo sesudah pada transaksi tidak sesuai"
# # )
# #
# # assert len(daftar_riwayat) == 1, (
# #     "Transaksi harus mempunyai tepat satu riwayat"
# # )
# #
# # assert len(daftar_audit) == 1, (
# #     "Transaksi harus mempunyai tepat satu audit"
# # )
# #
# # assert "3 bulan" in daftar_riwayat[0]["log"], (
# #     "Jumlah periode tidak tercantum dalam riwayat"
# # )
# #
# # assert "3 bulan" in daftar_audit[0]["log"], (
# #     "Jumlah periode tidak tercantum dalam audit"
# # )
# #
# #
# # print("=== KONDISI SETELAH PEMBAYARAN ===")
# # print("Periode dibayar :", JUMLAH_PERIODE)
# # print(
# #     "Total dibayar  : Rp"
# #     f"{Utilitas.format_rupiah(total_dibayar)}"
# # )
# # print(
# #     "Saldo SQLite   : Rp"
# #     f"{Utilitas.format_rupiah(data_rekening_sesudah['saldo'])}"
# # )
# # print(
# #     "Saldo objek    : Rp"
# #     f"{Utilitas.format_rupiah(rekening.saldo)}"
# # )
# # print(
# #     "Periode terakhir:",
# #     data_rekening_sesudah["waktu_bayar_admin"]
# # )
# # print("ID transaksi   :", transaksi["id"])
# # print("Riwayat        :", daftar_riwayat[0]["log"])
# # print("Audit          :", daftar_audit[0]["log"])
# # print()
# #
# #
# # # Memastikan pemanggilan ulang pada hari yang sama
# # # tidak membuat pemotongan kedua.
# # hasil_kedua = BiayaAdminService.potong_admin(
# #     rekening=rekening,
# #     hari_ini=hari_simulasi
# # )
# #
# # kondisi_terakhir = ambil_kondisi_database()
# #
# # assert hasil_kedua == 0, (
# #     "Pemanggilan kedua seharusnya tidak memotong biaya"
# # )
# #
# # assert kondisi_terakhir == kondisi_sesudah, (
# #     "Data berubah saat service dipanggil kedua kali"
# # )
# #
# #
# # print(
# #     "✅ PEMBAYARAN TIGA PERIODE BERHASIL: "
# #     "Rp6.000 dipotong dalam satu transaksi, "
# #     "periode terakhir diperbarui, pencatatan terhubung, "
# #     "dan pemanggilan kedua tidak memotong ulang"
# # )
#
#
#
#
# from bank_djago.penyimpanan.loaders.rekening_loaders import (
#     RekeningLoader
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.services.rekening.biaya_admin_service import (
#     BiayaAdminService
# )
# from bank_djago.utils.utility import JenisTransaksi, Utilitas
#
#
# NOREK_PENGUJIAN = "4001701216150609"
#
# SALDO_YANG_DIHARAPKAN = 498_000
# PERIODE_YANG_DIHARAPKAN = "2027-04-06"
#
#
# def muat_rekening():
#     """Memuat objek rekening pengujian dari SQLite."""
#     koneksi = buat_koneksi()
#
#     try:
#         return RekeningLoader.muat_rekening(
#             norek=NOREK_PENGUJIAN,
#             koneksi=koneksi
#         )
#     finally:
#         koneksi.close()
#
#
# def ambil_kondisi_database():
#     """
#     Mengambil snapshot database.
#
#     Snapshot digunakan untuk membuktikan bahwa rekening,
#     transaksi, riwayat, dan audit tidak berubah setelah rollback.
#     """
#     koneksi = buat_koneksi()
#
#     try:
#         rekening = koneksi.execute(
#             """
#             SELECT
#                 norek,
#                 saldo,
#                 waktu_bayar_admin,
#                 status
#             FROM rekening
#             WHERE norek = ?
#             """,
#             (NOREK_PENGUJIAN,)
#         ).fetchone()
#
#         transaksi = koneksi.execute(
#             """
#             SELECT
#                 id,
#                 jenis,
#                 norek_sumber,
#                 nominal,
#                 saldo_sumber_sebelum,
#                 saldo_sumber_sesudah
#             FROM transaksi
#             WHERE norek_sumber = ?
#               AND jenis = ?
#             ORDER BY id
#             """,
#             (
#                 NOREK_PENGUJIAN,
#                 JenisTransaksi.BIAYA_ADMIN.value
#             )
#         ).fetchall()
#
#         riwayat = koneksi.execute(
#             """
#             SELECT
#                 id,
#                 transaksi_id,
#                 norek,
#                 kategori,
#                 jenis,
#                 waktu,
#                 log
#             FROM riwayat
#             WHERE norek = ?
#             ORDER BY id
#             """,
#             (NOREK_PENGUJIAN,)
#         ).fetchall()
#
#         audit = koneksi.execute(
#             """
#             SELECT
#                 id,
#                 transaksi_id,
#                 norek,
#                 kategori,
#                 jenis,
#                 waktu,
#                 log
#             FROM audit
#             WHERE norek = ?
#             ORDER BY id
#             """,
#             (NOREK_PENGUJIAN,)
#         ).fetchall()
#
#         return {
#             "rekening": dict(rekening) if rekening else None,
#             "transaksi": [
#                 dict(data) for data in transaksi
#             ],
#             "riwayat": [
#                 dict(data) for data in riwayat
#             ],
#             "audit": [
#                 dict(data) for data in audit
#             ]
#         }
#
#     finally:
#         koneksi.close()
#
#
# rekening = muat_rekening()
#
# if rekening is None:
#     raise AssertionError(
#         f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
#     )
#
#
# # Memastikan pengujian dimulai dari keadaan yang kita kenal.
# assert rekening.saldo == SALDO_YANG_DIHARAPKAN, (
#     f"Saldo aktual Rp"
#     f"{Utilitas.format_rupiah(rekening.saldo)}, "
#     f"bukan Rp"
#     f"{Utilitas.format_rupiah(SALDO_YANG_DIHARAPKAN)}"
# )
#
# assert rekening.waktu_bayar_admin.isoformat() == (
#     PERIODE_YANG_DIHARAPKAN
# ), "Periode awal rekening tidak sesuai"
#
#
# # Mensimulasikan satu periode berikutnya.
# hari_simulasi = Utilitas.tambah_bulan(
#     rekening.waktu_bayar_admin,
#     1
# )
#
#
# # Menyimpan kondisi database dan objek sebelum kegagalan.
# kondisi_database_sebelum = ambil_kondisi_database()
#
# kondisi_objek_sebelum = {
#     "saldo": rekening.saldo,
#     "waktu_bayar_admin": rekening.waktu_bayar_admin,
#     "riwayat": list(rekening.riwayat)
# }
#
#
# print("=== KONDISI SEBELUM PENGUJIAN ROLLBACK ===")
# print("Nomor rekening       :", rekening.norek)
# print("Saldo                :", rekening.saldo)
# print("Periode terakhir     :", rekening.waktu_bayar_admin)
# print("Hari simulasi        :", hari_simulasi)
# print(
#     "Jumlah transaksi    :",
#     len(kondisi_database_sebelum["transaksi"])
# )
# print(
#     "Jumlah riwayat      :",
#     len(kondisi_database_sebelum["riwayat"])
# )
# print(
#     "Jumlah audit        :",
#     len(kondisi_database_sebelum["audit"])
# )
# print()
#
#
# # Menyimpan method asli agar dapat dikembalikan
# # setelah kegagalan buatan selesai.
# tambah_audit_asli = AuditRepository.tambah_audit
#
#
# def gagalkan_audit(*args, **kwargs):
#     """
#     Kegagalan buatan ini terjadi setelah perubahan rekening,
#     transaksi, dan riwayat dilakukan dalam koneksi yang sama.
#     """
#     raise RuntimeError(
#         "Kegagalan audit untuk menguji rollback biaya admin"
#     )
#
#
# kegagalan_berhasil_dipicu = False
#
# try:
#     # Mengganti sementara method penyimpanan audit
#     # dengan method yang selalu gagal.
#     AuditRepository.tambah_audit = gagalkan_audit
#
#     try:
#         BiayaAdminService.potong_admin(
#             rekening=rekening,
#             hari_ini=hari_simulasi
#         )
#
#     except RuntimeError as error:
#         kegagalan_berhasil_dipicu = True
#
#         print("✅ Kegagalan buatan berhasil dipicu")
#         print("Pesan error:", error)
#         print()
#
# finally:
#     # Method asli wajib dikembalikan agar pengujian lain
#     # tidak ikut mengalami kegagalan buatan.
#     AuditRepository.tambah_audit = tambah_audit_asli
#
#
# assert kegagalan_berhasil_dipicu, (
#     "Kegagalan audit tidak berhasil dipicu"
# )
#
#
# # Mengambil kembali keadaan setelah service melakukan rollback.
# kondisi_database_sesudah = ambil_kondisi_database()
#
# kondisi_objek_sesudah = {
#     "saldo": rekening.saldo,
#     "waktu_bayar_admin": rekening.waktu_bayar_admin,
#     "riwayat": list(rekening.riwayat)
# }
#
#
# print("=== KONDISI SETELAH ROLLBACK ===")
# print(
#     "Saldo rekening      :",
#     kondisi_database_sesudah["rekening"]["saldo"]
# )
# print(
#     "Periode terakhir    :",
#     kondisi_database_sesudah["rekening"]["waktu_bayar_admin"]
# )
# print(
#     "Jumlah transaksi   :",
#     len(kondisi_database_sesudah["transaksi"])
# )
# print(
#     "Jumlah riwayat     :",
#     len(kondisi_database_sesudah["riwayat"])
# )
# print(
#     "Jumlah audit       :",
#     len(kondisi_database_sesudah["audit"])
# )
# print()
#
#
# # Seluruh isi database yang diamati harus sama persis.
# assert (
#     kondisi_database_sesudah
#     == kondisi_database_sebelum
# ), (
#     "Database berubah meskipun transaksi seharusnya "
#     "sudah di-rollback"
# )
#
#
# # Objek Python juga tidak boleh berubah karena bagian
# # sinkronisasi objek hanya dijalankan setelah commit.
# assert kondisi_objek_sesudah == kondisi_objek_sebelum, (
#     "State objek Python berubah meskipun proses gagal"
# )
#
#
# print(
#     "✅ ROLLBACK BIAYA ADMIN BERHASIL: "
#     "saldo, periode pembayaran, transaksi, riwayat, "
#     "audit, dan objek Python tidak berubah"
# )

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.biaya_admin_service import (
    BiayaAdminService
)
from bank_djago.utils.utility import JenisTransaksi, Utilitas


NOREK_PENGUJIAN = "4001701216150609"

SALDO_AWAL = 498_000
BIAYA_ADMIN = 2_000

JUMLAH_PERIODE_TERTUNGGAK = 250
JUMLAH_PERIODE_MAMPU = SALDO_AWAL // BIAYA_ADMIN

TOTAL_DIBAYAR = (
    JUMLAH_PERIODE_MAMPU
    * BIAYA_ADMIN
)

SALDO_AKHIR = SALDO_AWAL - TOTAL_DIBAYAR


def muat_rekening():
    """Memuat rekening pengujian sebagai objek Python."""
    koneksi = buat_koneksi()

    try:
        return RekeningLoader.muat_rekening(
            norek=NOREK_PENGUJIAN,
            koneksi=koneksi
        )
    finally:
        koneksi.close()


def ambil_kondisi_database():
    """
    Mengambil keadaan rekening dan jumlah pencatatan
    untuk memeriksa perubahan yang terjadi.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT
                norek,
                saldo,
                status,
                waktu_bayar_admin
            FROM rekening
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE norek_sumber = ?
              AND jenis = ?
            """,
            (
                NOREK_PENGUJIAN,
                JenisTransaksi.BIAYA_ADMIN.value
            )
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()["jumlah"]

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


def ambil_pencatatan_terbaru():
    """Mengambil transaksi biaya admin terbaru dan catatan terkait."""
    koneksi = buat_koneksi()

    try:
        transaksi = koneksi.execute(
            """
            SELECT *
            FROM transaksi
            WHERE norek_sumber = ?
              AND jenis = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                NOREK_PENGUJIAN,
                JenisTransaksi.BIAYA_ADMIN.value
            )
        ).fetchone()

        if transaksi is None:
            raise AssertionError(
                "Transaksi biaya admin tidak ditemukan"
            )

        riwayat = koneksi.execute(
            """
            SELECT *
            FROM riwayat
            WHERE transaksi_id = ?
            """,
            (transaksi["id"],)
        ).fetchall()

        audit = koneksi.execute(
            """
            SELECT *
            FROM audit
            WHERE transaksi_id = ?
            """,
            (transaksi["id"],)
        ).fetchall()

        return transaksi, riwayat, audit

    finally:
        koneksi.close()


rekening = muat_rekening()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )


# Mencegah pengujian dijalankan setelah rekening berubah.
assert rekening.saldo == SALDO_AWAL, (
    f"Saldo aktual Rp"
    f"{Utilitas.format_rupiah(rekening.saldo)}, "
    f"bukan Rp{Utilitas.format_rupiah(SALDO_AWAL)}. "
    "Kemungkinan pengujian sudah pernah dijalankan."
)

assert rekening.biaya_admin == BIAYA_ADMIN, (
    "Biaya admin rekening tidak sesuai"
)


periode_sebelum = rekening.waktu_bayar_admin

# Membuat 250 periode tertunggak.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    JUMLAH_PERIODE_TERTUNGGAK
)

daftar_periode = BiayaAdminService.cari_periode_admin(
    waktu_bayar_admin=periode_sebelum,
    hari_ini=hari_simulasi
)

assert len(daftar_periode) == JUMLAH_PERIODE_TERTUNGGAK, (
    "Jumlah periode tertunggak tidak sesuai"
)


# Saldo hanya mampu membayar 249 dari 250 periode.
jumlah_periode_dibayar = min(
    len(daftar_periode),
    JUMLAH_PERIODE_MAMPU
)

assert jumlah_periode_dibayar == 249, (
    "Kemampuan pembayaran seharusnya 249 periode"
)


# Periode baru harus menunjuk periode ke-249,
# bukan periode ke-250 yang masih belum dibayar.
periode_terakhir_yang_diharapkan = (
    daftar_periode[jumlah_periode_dibayar - 1]
)

periode_yang_belum_dibayar = (
    daftar_periode[jumlah_periode_dibayar]
)

kondisi_sebelum = ambil_kondisi_database()


print("=== KONDISI SEBELUM PEMBAYARAN SEBAGIAN ===")
print("Nomor rekening      :", rekening.norek)
print("Saldo awal          :", rekening.saldo)
print("Biaya per bulan     :", rekening.biaya_admin)
print("Periode terakhir    :", periode_sebelum)
print("Hari simulasi       :", hari_simulasi)
print(
    "Periode tertunggak :",
    len(daftar_periode)
)
print(
    "Periode mampu bayar:",
    JUMLAH_PERIODE_MAMPU
)
print(
    "Periode tersisa    :",
    len(daftar_periode) - JUMLAH_PERIODE_MAMPU
)
print()


# Menjalankan pembayaran biaya admin.
total_dibayar = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_sesudah = ambil_kondisi_database()
data_rekening_sesudah = kondisi_sesudah["rekening"]


assert total_dibayar == TOTAL_DIBAYAR, (
    "Total biaya admin yang dibayar tidak sesuai"
)

assert total_dibayar == 498_000, (
    "Seharusnya rekening membayar Rp498.000"
)

assert data_rekening_sesudah["saldo"] == SALDO_AKHIR, (
    "Saldo SQLite seharusnya menjadi Rp0"
)

assert rekening.saldo == SALDO_AKHIR, (
    "Saldo objek Python seharusnya menjadi Rp0"
)

assert (
    data_rekening_sesudah["waktu_bayar_admin"]
    == periode_terakhir_yang_diharapkan.isoformat()
), "Periode terakhir di SQLite tidak sesuai"

assert (
    rekening.waktu_bayar_admin
    == periode_terakhir_yang_diharapkan
), "Periode terakhir pada objek Python tidak sesuai"

assert (
    kondisi_sesudah["jumlah_transaksi"]
    == kondisi_sebelum["jumlah_transaksi"] + 1
), "Seharusnya hanya terbentuk satu transaksi"

assert (
    kondisi_sesudah["jumlah_riwayat"]
    == kondisi_sebelum["jumlah_riwayat"] + 1
), "Seharusnya hanya terbentuk satu riwayat"

assert (
    kondisi_sesudah["jumlah_audit"]
    == kondisi_sebelum["jumlah_audit"] + 1
), "Seharusnya hanya terbentuk satu audit"


transaksi, daftar_riwayat, daftar_audit = (
    ambil_pencatatan_terbaru()
)

assert transaksi["nominal"] == TOTAL_DIBAYAR, (
    "Nominal transaksi tidak sesuai"
)

assert transaksi["saldo_sumber_sebelum"] == SALDO_AWAL, (
    "Saldo sumber sebelum transaksi tidak sesuai"
)

assert transaksi["saldo_sumber_sesudah"] == 0, (
    "Saldo sumber sesudah transaksi bukan Rp0"
)

assert len(daftar_riwayat) == 1, (
    "Transaksi tidak memiliki tepat satu riwayat"
)

assert len(daftar_audit) == 1, (
    "Transaksi tidak memiliki tepat satu audit"
)

assert "249 bulan" in daftar_riwayat[0]["log"], (
    "Jumlah periode tidak tercantum dalam riwayat"
)

assert "249 bulan" in daftar_audit[0]["log"], (
    "Jumlah periode tidak tercantum dalam audit"
)


print("=== KONDISI SETELAH PEMBAYARAN SEBAGIAN ===")
print("Periode dibayar :", jumlah_periode_dibayar)
print(
    "Total dibayar  : Rp"
    f"{Utilitas.format_rupiah(total_dibayar)}"
)
print(
    "Saldo akhir    : Rp"
    f"{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Periode terakhir:",
    rekening.waktu_bayar_admin
)
print(
    "Periode tertunggak:",
    periode_yang_belum_dibayar
)
print("ID transaksi   :", transaksi["id"])
print("Riwayat        :", daftar_riwayat[0]["log"])
print("Audit          :", daftar_audit[0]["log"])
print()


# Menyimpan kondisi setelah pembayaran pertama.
# Pemanggilan berikutnya tidak boleh mengubahnya.
kondisi_sebelum_panggilan_kedua = (
    ambil_kondisi_database()
)


# Pada hari simulasi yang sama masih ada satu periode tertunggak,
# tetapi saldo sudah Rp0 sehingga tidak mampu membayarnya.
hasil_kedua = BiayaAdminService.potong_admin(
    rekening=rekening,
    hari_ini=hari_simulasi
)

kondisi_setelah_panggilan_kedua = (
    ambil_kondisi_database()
)


assert hasil_kedua == 0, (
    "Service seharusnya mengembalikan 0 "
    "ketika saldo tidak mencukupi"
)

assert (
    kondisi_setelah_panggilan_kedua
    == kondisi_sebelum_panggilan_kedua
), (
    "Database berubah meskipun saldo tidak mampu "
    "membayar satu periode"
)

assert rekening.saldo == 0, (
    "Saldo objek Python berubah pada pemanggilan kedua"
)

assert (
    rekening.waktu_bayar_admin
    == periode_terakhir_yang_diharapkan
), (
    "Periode pembayaran tetap maju meskipun "
    "periode terakhir belum dibayar"
)


print(
    "✅ PEMBAYARAN SEBAGIAN BERHASIL: "
    "249 dari 250 periode dibayar, saldo menjadi Rp0, "
    "satu periode tetap tertunggak, dan pemanggilan "
    "berikutnya tidak mengubah data"
)