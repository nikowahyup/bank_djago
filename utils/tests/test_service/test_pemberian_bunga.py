# # # import datetime
# # #
# # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # #     RekeningLoader
# # # )
# # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # #     RekeningRepository
# # # )
# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # from bank_djago.services.rekening.bunga_service import (
# # #     BungaService
# # # )
# # # from bank_djago.utils.utility import Utilitas
# # #
# # #
# # # NOREK_PENGUJIAN = "3001781978899033"
# # #
# # #
# # # def ambil_kondisi_database(norek):
# # #     """
# # #     Mengambil kondisi rekening beserta jumlah seluruh pencatatan
# # #     bunga yang dimiliki rekening pengujian.
# # #     """
# # #     koneksi = buat_koneksi()
# # #
# # #     try:
# # #         rekening = RekeningRepository.cari_rekening_dengan_norek(
# # #             norek=norek,
# # #             koneksi=koneksi
# # #         )
# # #
# # #         jumlah_transaksi = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS jumlah
# # #             FROM transaksi
# # #             WHERE jenis = 'bunga_tabungan'
# # #               AND norek_tujuan = ?
# # #             """,
# # #             (norek,)
# # #         ).fetchone()["jumlah"]
# # #
# # #         jumlah_riwayat = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS jumlah
# # #             FROM riwayat
# # #             WHERE norek = ?
# # #               AND jenis = 'bunga bulanan'
# # #             """,
# # #             (norek,)
# # #         ).fetchone()["jumlah"]
# # #
# # #         jumlah_audit = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS jumlah
# # #             FROM audit
# # #             WHERE norek = ?
# # #               AND jenis = 'dapat bunga'
# # #             """,
# # #             (norek,)
# # #         ).fetchone()["jumlah"]
# # #
# # #         return {
# # #             "rekening": dict(rekening) if rekening else None,
# # #             "jumlah_transaksi": jumlah_transaksi,
# # #             "jumlah_riwayat": jumlah_riwayat,
# # #             "jumlah_audit": jumlah_audit
# # #         }
# # #
# # #     finally:
# # #         koneksi.close()
# # #
# # #
# # # # Memuat rekening sebagai objek Python.
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     rekening = RekeningLoader.muat_rekening(
# # #         norek=NOREK_PENGUJIAN,
# # #         koneksi=koneksi
# # #     )
# # # finally:
# # #     koneksi.close()
# # #
# # # if rekening is None:
# # #     raise AssertionError(
# # #         f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
# # #     )
# # #
# # # if rekening.status == "tutup":
# # #     raise AssertionError(
# # #         "Rekening pengujian sudah ditutup"
# # #     )
# # #
# # #
# # # # Menyimpan keadaan sebelum service dijalankan.
# # # kondisi_sebelum = ambil_kondisi_database(
# # #     NOREK_PENGUJIAN
# # # )
# # #
# # # data_sebelum = kondisi_sebelum["rekening"]
# # #
# # # saldo_sebelum = data_sebelum["saldo"]
# # # periode_sebelum = datetime.date.fromisoformat(
# # #     data_sebelum["dapat_bunga"]
# # # )
# # #
# # # # Tanggal simulasi dibuat tepat satu periode sesudah
# # # # periode bunga terakhir.
# # # hari_simulasi = Utilitas.tambah_bulan(
# # #     periode_sebelum,
# # #     1
# # # )
# # #
# # # bunga_diharapkan = round(
# # #     saldo_sebelum * rekening.bunga / 12
# # # )
# # #
# # # saldo_diharapkan = (
# # #     saldo_sebelum + bunga_diharapkan
# # # )
# # #
# # # print("=== KONDISI SEBELUM PEMBERIAN BUNGA ===")
# # # print("Nomor rekening :", rekening.norek)
# # # print(
# # #     "Saldo awal     :",
# # #     f"Rp{Utilitas.format_rupiah(saldo_sebelum)}"
# # # )
# # # print(
# # #     "Bunga tahunan  :",
# # #     f"{rekening.bunga * 100:.1f}%"
# # # )
# # # print(
# # #     "Bunga satu bulan:",
# # #     f"Rp{Utilitas.format_rupiah(bunga_diharapkan)}"
# # # )
# # # print("Periode terakhir:", periode_sebelum)
# # # print("Hari simulasi   :", hari_simulasi)
# # # print()
# # #
# # #
# # # # Menjalankan pemberian bunga satu periode.
# # # total_bunga = BungaService.berikan_bunga(
# # #     rekening=rekening,
# # #     hari_ini=hari_simulasi
# # # )
# # #
# # # kondisi_setelah = ambil_kondisi_database(
# # #     NOREK_PENGUJIAN
# # # )
# # #
# # # data_setelah = kondisi_setelah["rekening"]
# # #
# # # periode_setelah = datetime.date.fromisoformat(
# # #     data_setelah["dapat_bunga"]
# # # )
# # #
# # # print("=== KONDISI SETELAH PEMBERIAN BUNGA ===")
# # # print(
# # #     "Bunga diberikan:",
# # #     f"Rp{Utilitas.format_rupiah(total_bunga)}"
# # # )
# # # print(
# # #     "Saldo SQLite   :",
# # #     f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
# # # )
# # # print(
# # #     "Saldo objek    :",
# # #     f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
# # # )
# # # print("Periode SQLite :", periode_setelah)
# # # print("Periode objek  :", rekening.dapat_bunga)
# # # print()
# # #
# # #
# # # # Memastikan nominal bunga dihitung dengan bunga tahunan / 12.
# # # assert total_bunga == bunga_diharapkan, (
# # #     "Nominal bunga yang diberikan tidak sesuai"
# # # )
# # #
# # # # Memastikan saldo SQLite bertambah tepat sebesar bunga.
# # # assert data_setelah["saldo"] == saldo_diharapkan, (
# # #     "Saldo SQLite setelah pemberian bunga tidak sesuai"
# # # )
# # #
# # # # Memastikan state objek Python ikut diperbarui.
# # # assert rekening.saldo == saldo_diharapkan, (
# # #     "Saldo objek Python tidak sesuai dengan SQLite"
# # # )
# # #
# # # assert rekening.dapat_bunga == hari_simulasi, (
# # #     "Periode bunga pada objek Python belum diperbarui"
# # # )
# # #
# # # assert periode_setelah == hari_simulasi, (
# # #     "Periode bunga pada SQLite belum diperbarui"
# # # )
# # #
# # # # Setiap pemberian bunga harus menghasilkan tepat satu
# # # # transaksi, satu riwayat, dan satu audit.
# # # assert (
# # #     kondisi_setelah["jumlah_transaksi"]
# # #     == kondisi_sebelum["jumlah_transaksi"] + 1
# # # ), "Transaksi bunga tidak bertambah tepat satu"
# # #
# # # assert (
# # #     kondisi_setelah["jumlah_riwayat"]
# # #     == kondisi_sebelum["jumlah_riwayat"] + 1
# # # ), "Riwayat bunga tidak bertambah tepat satu"
# # #
# # # assert (
# # #     kondisi_setelah["jumlah_audit"]
# # #     == kondisi_sebelum["jumlah_audit"] + 1
# # # ), "Audit bunga tidak bertambah tepat satu"
# # #
# # #
# # # # Mengambil transaksi terbaru untuk memeriksa hubungan
# # # # transaksi, riwayat, dan audit.
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     transaksi = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM transaksi
# # #         WHERE jenis = 'bunga_tabungan'
# # #           AND norek_tujuan = ?
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (NOREK_PENGUJIAN,)
# # #     ).fetchone()
# # #
# # #     if transaksi is None:
# # #         raise AssertionError(
# # #             "Transaksi bunga tidak ditemukan"
# # #         )
# # #
# # #     riwayat = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM riwayat
# # #         WHERE transaksi_id = ?
# # #         """,
# # #         (transaksi["id"],)
# # #     ).fetchall()
# # #
# # #     audit = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM audit
# # #         WHERE transaksi_id = ?
# # #         """,
# # #         (transaksi["id"],)
# # #     ).fetchall()
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # print("=== DATA TRANSAKSI BUNGA ===")
# # # print("ID transaksi    :", transaksi["id"])
# # # print("Jenis transaksi :", transaksi["jenis"])
# # # print("Rekening tujuan :", transaksi["norek_tujuan"])
# # # print(
# # #     "Nominal         :",
# # #     f"Rp{Utilitas.format_rupiah(transaksi['nominal'])}"
# # # )
# # # print(
# # #     "Saldo awal      :",
# # #     f"Rp{Utilitas.format_rupiah(
# # #         transaksi['saldo_tujuan_sebelum']
# # #     )}"
# # # )
# # # print(
# # #     "Saldo akhir     :",
# # #     f"Rp{Utilitas.format_rupiah(
# # #         transaksi['saldo_tujuan_sesudah']
# # #     )}"
# # # )
# # # print()
# # #
# # # assert transaksi["nominal"] == bunga_diharapkan, (
# # #     "Nominal transaksi tidak sesuai bunga"
# # # )
# # #
# # # assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum, (
# # #     "Snapshot saldo awal transaksi tidak sesuai"
# # # )
# # #
# # # assert transaksi["saldo_tujuan_sesudah"] == saldo_diharapkan, (
# # #     "Snapshot saldo akhir transaksi tidak sesuai"
# # # )
# # #
# # # assert len(riwayat) == 1, (
# # #     "Riwayat bunga tidak terhubung dengan transaksi"
# # # )
# # #
# # # assert len(audit) == 1, (
# # #     "Audit bunga tidak terhubung dengan transaksi"
# # # )
# # #
# # # print("=== RIWAYAT TERHUBUNG ===")
# # # for data in riwayat:
# # #     print(
# # #         f"ID {data['id']} | "
# # #         f"Transaksi {data['transaksi_id']} | "
# # #         f"{data['jenis']} | "
# # #         f"{data['log']}"
# # #     )
# # #
# # # print()
# # # print("=== AUDIT TERHUBUNG ===")
# # # for data in audit:
# # #     print(
# # #         f"ID {data['id']} | "
# # #         f"Transaksi {data['transaksi_id']} | "
# # #         f"{data['jenis']} | "
# # #         f"{data['log']}"
# # #     )
# # #
# # #
# # # # Memanggil service untuk kedua kalinya pada tanggal yang sama.
# # # # Tidak boleh ada bunga atau pencatatan tambahan.
# # # hasil_kedua = BungaService.berikan_bunga(
# # #     rekening=rekening,
# # #     hari_ini=hari_simulasi
# # # )
# # #
# # # kondisi_pemanggilan_kedua = ambil_kondisi_database(
# # #     NOREK_PENGUJIAN
# # # )
# # #
# # # assert hasil_kedua == 0, (
# # #     "Pemanggilan kedua masih memberikan bunga"
# # # )
# # #
# # # assert (
# # #     kondisi_pemanggilan_kedua
# # #     == kondisi_setelah
# # # ), (
# # #     "Pemanggilan kedua mengubah data meskipun "
# # #     "periodenya sudah diproses"
# # # )
# # #
# # # print()
# # # print(
# # #     "✅ PEMBERIAN BUNGA SATU PERIODE BERHASIL: "
# # #     "saldo, periode, transaksi, riwayat, audit, "
# # #     "state objek, dan pencegahan proses ganda "
# # #     "tersimpan dengan benar"
# # # )
# #
# #
# # import datetime
# #
# # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# #     RekeningLoader
# # )
# # from bank_djago.penyimpanan.repositories.rekening_repository import (
# #     RekeningRepository
# # )
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # from bank_djago.services.rekening.bunga_service import (
# #     BungaService
# # )
# # from bank_djago.utils.utility import Utilitas
# #
# #
# # NOREK_PENGUJIAN = "3001781978899033"
# # JUMLAH_PERIODE = 3
# #
# #
# # def ambil_snapshot(norek):
# #     """
# #     Mengambil kondisi rekening dan jumlah pencatatan bunga
# #     langsung dari SQLite.
# #     """
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         rekening = RekeningRepository.cari_rekening_dengan_norek(
# #             norek=norek,
# #             koneksi=koneksi
# #         )
# #
# #         jumlah_transaksi = koneksi.execute(
# #             """
# #             SELECT COUNT(*) AS jumlah
# #             FROM transaksi
# #             WHERE jenis = 'bunga_tabungan'
# #               AND norek_tujuan = ?
# #             """,
# #             (norek,)
# #         ).fetchone()["jumlah"]
# #
# #         jumlah_riwayat = koneksi.execute(
# #             """
# #             SELECT COUNT(*) AS jumlah
# #             FROM riwayat
# #             WHERE norek = ?
# #               AND jenis = 'bunga bulanan'
# #             """,
# #             (norek,)
# #         ).fetchone()["jumlah"]
# #
# #         jumlah_audit = koneksi.execute(
# #             """
# #             SELECT COUNT(*) AS jumlah
# #             FROM audit
# #             WHERE norek = ?
# #               AND jenis = 'dapat bunga'
# #             """,
# #             (norek,)
# #         ).fetchone()["jumlah"]
# #
# #         return {
# #             "rekening": dict(rekening) if rekening else None,
# #             "jumlah_transaksi": jumlah_transaksi,
# #             "jumlah_riwayat": jumlah_riwayat,
# #             "jumlah_audit": jumlah_audit
# #         }
# #
# #     finally:
# #         koneksi.close()
# #
# #
# # # Memuat rekening sebagai objek Python.
# # koneksi = buat_koneksi()
# #
# # try:
# #     rekening = RekeningLoader.muat_rekening(
# #         norek=NOREK_PENGUJIAN,
# #         koneksi=koneksi
# #     )
# # finally:
# #     koneksi.close()
# #
# # if rekening is None:
# #     raise AssertionError(
# #         f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
# #     )
# #
# # if rekening.status == "tutup":
# #     raise AssertionError(
# #         "Rekening pengujian sudah ditutup"
# #     )
# #
# #
# # # Menyimpan keadaan awal sebelum bunga diberikan.
# # sebelum = ambil_snapshot(NOREK_PENGUJIAN)
# # data_sebelum = sebelum["rekening"]
# #
# # saldo_sebelum = data_sebelum["saldo"]
# #
# # periode_sebelum = datetime.date.fromisoformat(
# #     data_sebelum["dapat_bunga"]
# # )
# #
# # # Mensimulasikan tiga periode setelah periode terakhir.
# # hari_simulasi = Utilitas.tambah_bulan(
# #     periode_sebelum,
# #     JUMLAH_PERIODE
# # )
# #
# # bunga_satu_periode = round(
# #     saldo_sebelum * rekening.bunga / 12
# # )
# #
# # total_bunga_diharapkan = (
# #     bunga_satu_periode * JUMLAH_PERIODE
# # )
# #
# # saldo_diharapkan = (
# #     saldo_sebelum + total_bunga_diharapkan
# # )
# #
# #
# # print("=== KONDISI SEBELUM PEMBERIAN BUNGA ===")
# # print("Nomor rekening   :", rekening.norek)
# # print(
# #     "Saldo awal       :",
# #     f"Rp{Utilitas.format_rupiah(saldo_sebelum)}"
# # )
# # print(
# #     "Bunga per periode:",
# #     f"Rp{Utilitas.format_rupiah(bunga_satu_periode)}"
# # )
# # print("Periode terakhir :", periode_sebelum)
# # print("Hari simulasi     :", hari_simulasi)
# # print("Jumlah periode    :", JUMLAH_PERIODE)
# # print()
# #
# #
# # # Memberikan bunga untuk seluruh periode yang tertunggak.
# # total_bunga = BungaService.berikan_bunga(
# #     rekening=rekening,
# #     hari_ini=hari_simulasi
# # )
# #
# # setelah = ambil_snapshot(NOREK_PENGUJIAN)
# # data_setelah = setelah["rekening"]
# #
# # periode_setelah = datetime.date.fromisoformat(
# #     data_setelah["dapat_bunga"]
# # )
# #
# #
# # print("=== KONDISI SETELAH PEMBERIAN BUNGA ===")
# # print("Periode diproses :", JUMLAH_PERIODE)
# # print(
# #     "Total bunga     :",
# #     f"Rp{Utilitas.format_rupiah(total_bunga)}"
# # )
# # print(
# #     "Saldo SQLite    :",
# #     f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
# # )
# # print(
# #     "Saldo objek     :",
# #     f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
# # )
# # print("Periode SQLite  :", periode_setelah)
# # print("Periode objek   :", rekening.dapat_bunga)
# # print()
# #
# #
# # # Memeriksa perhitungan bunga.
# # assert total_bunga == total_bunga_diharapkan, (
# #     "Total bunga beberapa periode tidak sesuai"
# # )
# #
# # assert data_setelah["saldo"] == saldo_diharapkan, (
# #     "Saldo SQLite setelah pemberian bunga tidak sesuai"
# # )
# #
# # assert rekening.saldo == saldo_diharapkan, (
# #     "Saldo objek Python tidak sesuai dengan SQLite"
# # )
# #
# # assert periode_setelah == hari_simulasi, (
# #     "Periode bunga SQLite tidak diperbarui dengan benar"
# # )
# #
# # assert rekening.dapat_bunga == hari_simulasi, (
# #     "Periode bunga objek Python tidak diperbarui"
# # )
# #
# #
# # # Walaupun ada tiga periode, pencatatan dibuat sebagai
# # # satu transaksi gabungan.
# # assert (
# #     setelah["jumlah_transaksi"]
# #     == sebelum["jumlah_transaksi"] + 1
# # ), "Transaksi bunga tidak bertambah tepat satu"
# #
# # assert (
# #     setelah["jumlah_riwayat"]
# #     == sebelum["jumlah_riwayat"] + 1
# # ), "Riwayat bunga tidak bertambah tepat satu"
# #
# # assert (
# #     setelah["jumlah_audit"]
# #     == sebelum["jumlah_audit"] + 1
# # ), "Audit bunga tidak bertambah tepat satu"
# #
# #
# # # Mengambil transaksi bunga yang baru dibuat.
# # koneksi = buat_koneksi()
# #
# # try:
# #     transaksi = koneksi.execute(
# #         """
# #         SELECT *
# #         FROM transaksi
# #         WHERE jenis = 'bunga_tabungan'
# #           AND norek_tujuan = ?
# #         ORDER BY id DESC
# #         LIMIT 1
# #         """,
# #         (NOREK_PENGUJIAN,)
# #     ).fetchone()
# #
# #     if transaksi is None:
# #         raise AssertionError(
# #             "Transaksi bunga tidak ditemukan"
# #         )
# #
# #     riwayat = koneksi.execute(
# #         """
# #         SELECT *
# #         FROM riwayat
# #         WHERE transaksi_id = ?
# #         """,
# #         (transaksi["id"],)
# #     ).fetchall()
# #
# #     audit = koneksi.execute(
# #         """
# #         SELECT *
# #         FROM audit
# #         WHERE transaksi_id = ?
# #         """,
# #         (transaksi["id"],)
# #     ).fetchall()
# #
# # finally:
# #     koneksi.close()
# #
# #
# # print("=== DATA TRANSAKSI BUNGA ===")
# # print("ID transaksi    :", transaksi["id"])
# # print("Jenis transaksi :", transaksi["jenis"])
# # print(
# #     "Nominal         :",
# #     f"Rp{Utilitas.format_rupiah(transaksi['nominal'])}"
# # )
# # print(
# #     "Saldo awal      :",
# #     f"Rp{Utilitas.format_rupiah(
# #         transaksi['saldo_tujuan_sebelum']
# #     )}"
# # )
# # print(
# #     "Saldo akhir     :",
# #     f"Rp{Utilitas.format_rupiah(
# #         transaksi['saldo_tujuan_sesudah']
# #     )}"
# # )
# # print()
# #
# #
# # assert transaksi["nominal"] == total_bunga_diharapkan, (
# #     "Nominal pada transaksi bunga tidak sesuai"
# # )
# #
# # assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum, (
# #     "Snapshot saldo awal transaksi tidak sesuai"
# # )
# #
# # assert transaksi["saldo_tujuan_sesudah"] == saldo_diharapkan, (
# #     "Snapshot saldo akhir transaksi tidak sesuai"
# # )
# #
# # assert len(riwayat) == 1, (
# #     "Riwayat tidak terhubung dengan transaksi bunga"
# # )
# #
# # assert len(audit) == 1, (
# #     "Audit tidak terhubung dengan transaksi bunga"
# # )
# #
# #
# # print("=== RIWAYAT TERHUBUNG ===")
# # for data in riwayat:
# #     print(
# #         f"ID {data['id']} | "
# #         f"Transaksi {data['transaksi_id']} | "
# #         f"{data['jenis']} | "
# #         f"{data['log']}"
# #     )
# #
# # print()
# # print("=== AUDIT TERHUBUNG ===")
# # for data in audit:
# #     print(
# #         f"ID {data['id']} | "
# #         f"Transaksi {data['transaksi_id']} | "
# #         f"{data['jenis']} | "
# #         f"{data['log']}"
# #     )
# #
# #
# # # Memanggil service kembali pada tanggal simulasi yang sama.
# # # Tidak boleh menghasilkan bunga maupun pencatatan baru.
# # hasil_kedua = BungaService.berikan_bunga(
# #     rekening=rekening,
# #     hari_ini=hari_simulasi
# # )
# #
# # setelah_pemanggilan_kedua = ambil_snapshot(
# #     NOREK_PENGUJIAN
# # )
# #
# # assert hasil_kedua == 0, (
# #     "Pemanggilan kedua masih memberikan bunga"
# # )
# #
# # assert setelah_pemanggilan_kedua == setelah, (
# #     "Pemanggilan kedua mengubah data"
# # )
# #
# #
# # print()
# # print(
# #     "✅ PEMBERIAN BUNGA TIGA PERIODE BERHASIL: "
# #     "bunga dihitung, saldo dan periode diperbarui, "
# #     "pencatatan dibuat dalam satu transaksi, "
# #     "serta pemanggilan kedua tidak mengubah data"
# # )
#
#
# import datetime
#
# from bank_djago.penyimpanan.loaders.rekening_loaders import (
#     RekeningLoader
# )
# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.services.rekening.bunga_service import (
#     BungaService
# )
# from bank_djago.utils.utility import Utilitas
#
#
# NOREK_PENGUJIAN = "4001701216150609"
#
#
# def ambil_snapshot(norek):
#     """
#     Mengambil kondisi rekening dan menghitung seluruh pencatatan
#     bunga milik rekening pengujian.
#     """
#     koneksi = buat_koneksi()
#
#     try:
#         rekening = RekeningRepository.cari_rekening_dengan_norek(
#             norek=norek,
#             koneksi=koneksi
#         )
#
#         jumlah_transaksi = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM transaksi
#             WHERE jenis = 'bunga_tabungan'
#               AND norek_tujuan = ?
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         jumlah_riwayat = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM riwayat
#             WHERE norek = ?
#               AND jenis = 'bunga bulanan'
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         jumlah_audit = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM audit
#             WHERE norek = ?
#               AND jenis = 'dapat bunga'
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         return {
#             "rekening": dict(rekening) if rekening else None,
#             "jumlah_transaksi": jumlah_transaksi,
#             "jumlah_riwayat": jumlah_riwayat,
#             "jumlah_audit": jumlah_audit
#         }
#
#     finally:
#         koneksi.close()
#
#
# # Memuat rekening pengujian sebagai objek Python.
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
# if rekening is None:
#     raise AssertionError(
#         f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
#     )
#
# if rekening.status == "tutup":
#     raise AssertionError(
#         "Rekening pengujian sudah ditutup"
#     )
#
# # Pengujian ini memang membutuhkan rekening bersaldo nol.
# assert rekening.saldo == 0, (
#     f"Saldo rekening Rp{Utilitas.format_rupiah(rekening.saldo)}, "
#     "bukan Rp0"
# )
#
#
# # Menyimpan keadaan sebelum service dijalankan.
# sebelum = ambil_snapshot(NOREK_PENGUJIAN)
# data_sebelum = sebelum["rekening"]
#
# periode_sebelum = datetime.date.fromisoformat(
#     data_sebelum["dapat_bunga"]
# )
#
# # Membuat tepat satu periode bunga yang harus diproses.
# hari_simulasi = Utilitas.tambah_bulan(
#     periode_sebelum,
#     1
# )
#
# jumlah_riwayat_objek_sebelum = len(rekening.riwayat)
#
#
# print("=== KONDISI SEBELUM PEMBERIAN BUNGA NOL ===")
# print("Nomor rekening   :", rekening.norek)
# print(
#     "Saldo            :",
#     f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
# )
# print(
#     "Bunga tahunan    :",
#     f"{rekening.bunga * 100:.1f}%"
# )
# print("Periode terakhir :", periode_sebelum)
# print("Hari simulasi     :", hari_simulasi)
# print("Jumlah transaksi :", sebelum["jumlah_transaksi"])
# print("Jumlah riwayat   :", sebelum["jumlah_riwayat"])
# print("Jumlah audit     :", sebelum["jumlah_audit"])
# print()
#
#
# # Menjalankan service. Karena saldo nol, hasil bunga harus nol.
# hasil = BungaService.berikan_bunga(
#     rekening=rekening,
#     hari_ini=hari_simulasi
# )
#
# setelah = ambil_snapshot(NOREK_PENGUJIAN)
# data_setelah = setelah["rekening"]
#
# periode_setelah = datetime.date.fromisoformat(
#     data_setelah["dapat_bunga"]
# )
#
#
# print("=== KONDISI SETELAH PEMBERIAN BUNGA NOL ===")
# print(
#     "Hasil bunga      :",
#     f"Rp{Utilitas.format_rupiah(hasil)}"
# )
# print(
#     "Saldo SQLite     :",
#     f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
# )
# print(
#     "Saldo objek      :",
#     f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
# )
# print("Periode SQLite   :", periode_setelah)
# print("Periode objek    :", rekening.dapat_bunga)
# print("Jumlah transaksi :", setelah["jumlah_transaksi"])
# print("Jumlah riwayat   :", setelah["jumlah_riwayat"])
# print("Jumlah audit     :", setelah["jumlah_audit"])
# print()
#
#
# # Tidak ada bunga yang dihasilkan.
# assert hasil == 0, (
#     "Rekening bersaldo nol masih menghasilkan bunga"
# )
#
# # Saldo SQLite dan objek Python harus tetap nol.
# assert data_setelah["saldo"] == 0, (
#     "Saldo SQLite berubah setelah bunga nol"
# )
#
# assert rekening.saldo == 0, (
#     "Saldo objek Python berubah setelah bunga nol"
# )
#
# # Walaupun nominalnya nol, periode tetap harus dianggap selesai.
# assert periode_setelah == hari_simulasi, (
#     "Periode bunga SQLite tidak diperbarui"
# )
#
# assert rekening.dapat_bunga == hari_simulasi, (
#     "Periode bunga objek Python tidak diperbarui"
# )
#
# # Tidak boleh ada transaksi bernominal nol.
# assert (
#     setelah["jumlah_transaksi"]
#     == sebelum["jumlah_transaksi"]
# ), "Transaksi bunga nol masih dibuat"
#
# # Karena tidak ada transaksi, riwayat dan audit juga tidak dibuat.
# assert (
#     setelah["jumlah_riwayat"]
#     == sebelum["jumlah_riwayat"]
# ), "Riwayat bunga nol masih dibuat"
#
# assert (
#     setelah["jumlah_audit"]
#     == sebelum["jumlah_audit"]
# ), "Audit bunga nol masih dibuat"
#
# assert (
#     len(rekening.riwayat)
#     == jumlah_riwayat_objek_sebelum
# ), "Riwayat bunga nol masih dimasukkan ke objek Python"
#
#
# # Panggilan kedua pada tanggal yang sama juga tidak boleh
# # menghasilkan perubahan apa pun.
# hasil_kedua = BungaService.berikan_bunga(
#     rekening=rekening,
#     hari_ini=hari_simulasi
# )
#
# setelah_pemanggilan_kedua = ambil_snapshot(
#     NOREK_PENGUJIAN
# )
#
# assert hasil_kedua == 0, (
#     "Pemanggilan kedua masih menghasilkan bunga"
# )
#
# assert setelah_pemanggilan_kedua == setelah, (
#     "Pemanggilan kedua mengubah data SQLite"
# )
#
# assert rekening.saldo == 0, (
#     "Pemanggilan kedua mengubah saldo objek"
# )
#
# assert rekening.dapat_bunga == hari_simulasi, (
#     "Pemanggilan kedua mengubah periode objek"
# )
#
#
# print(
#     "✅ BUNGA NOL BERHASIL DITANGANI: "
#     "saldo tetap Rp0, periode tetap diperbarui, "
#     "transaksi nol tidak dibuat, serta pemanggilan "
#     "kedua tidak mengubah data"
# )



import datetime
from unittest.mock import patch

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.bunga_service import (
    BungaService
)
from bank_djago.utils.utility import Utilitas


NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot(norek):
    """
    Mengambil seluruh kondisi penting dari SQLite.

    Snapshot sebelum dan sesudah kegagalan akan dibandingkan
    untuk membuktikan bahwa rollback bekerja.
    """
    koneksi = buat_koneksi()

    try:
        rekening = RekeningRepository.cari_rekening_dengan_norek(
            norek=norek,
            koneksi=koneksi
        )

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'bunga_tabungan'
              AND norek_tujuan = ?
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
              AND jenis = 'bunga bulanan'
            """,
            (norek,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
              AND jenis = 'dapat bunga'
            """,
            (norek,)
        ).fetchone()["jumlah"]

        return {
            "rekening": dict(rekening) if rekening else None,
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# Memuat rekening menjadi objek Python.
koneksi = buat_koneksi()

try:
    rekening = RekeningLoader.muat_rekening(
        norek=NOREK_PENGUJIAN,
        koneksi=koneksi
    )
finally:
    koneksi.close()

if rekening is None:
    raise AssertionError(
        f"Rekening {NOREK_PENGUJIAN} tidak ditemukan"
    )

if rekening.status == "tutup":
    raise AssertionError(
        "Rekening pengujian sudah ditutup"
    )

if rekening.saldo <= 0:
    raise AssertionError(
        "Pengujian rollback membutuhkan rekening "
        "yang menghasilkan bunga lebih dari nol"
    )


# Menyimpan kondisi database sebelum kegagalan buatan.
snapshot_sebelum = ambil_snapshot(
    NOREK_PENGUJIAN
)

data_sebelum = snapshot_sebelum["rekening"]

periode_sebelum = datetime.date.fromisoformat(
    data_sebelum["dapat_bunga"]
)

# Satu periode baru dibuat agar service benar-benar mencoba
# memperbarui rekening dan membuat transaksi.
hari_simulasi = Utilitas.tambah_bulan(
    periode_sebelum,
    1
)

bunga_yang_seharusnya = round(
    data_sebelum["saldo"] * rekening.bunga / 12
)

# Menyimpan state objek Python sebelum service dijalankan.
saldo_objek_sebelum = rekening.saldo
periode_objek_sebelum = rekening.dapat_bunga
riwayat_objek_sebelum = list(rekening.riwayat)


print("=== KONDISI SEBELUM PENGUJIAN ROLLBACK ===")
print("Nomor rekening   :", rekening.norek)
print(
    "Saldo            :",
    f"Rp{Utilitas.format_rupiah(data_sebelum['saldo'])}"
)
print(
    "Bunga percobaan  :",
    f"Rp{Utilitas.format_rupiah(bunga_yang_seharusnya)}"
)
print("Periode terakhir :", periode_sebelum)
print("Hari simulasi     :", hari_simulasi)
print(
    "Jumlah transaksi :",
    snapshot_sebelum["jumlah_transaksi"]
)
print(
    "Jumlah riwayat   :",
    snapshot_sebelum["jumlah_riwayat"]
)
print(
    "Jumlah audit     :",
    snapshot_sebelum["jumlah_audit"]
)
print()


# AuditRepository sengaja dibuat gagal.
#
# Kegagalan terjadi setelah:
# 1. rekening diperbarui,
# 2. transaksi ditambahkan,
# 3. riwayat ditambahkan.
#
# Dengan demikian, kita dapat membuktikan bahwa ketiga
# perubahan tersebut benar-benar dibatalkan oleh rollback.
try:
    with patch(
        "bank_djago.services.rekening.bunga_service."
        "AuditRepository.tambah_audit",
        side_effect=RuntimeError(
            "Kegagalan audit untuk menguji rollback bunga"
        )
    ):
        BungaService.berikan_bunga(
            rekening=rekening,
            hari_ini=hari_simulasi
        )

except RuntimeError as error:
    print("✅ Kegagalan buatan berhasil dipicu")
    print("Pesan error:", error)

else:
    raise AssertionError(
        "Kegagalan audit tidak berhasil dipicu"
    )


# Mengambil ulang data dari SQLite setelah rollback.
snapshot_setelah = ambil_snapshot(
    NOREK_PENGUJIAN
)

data_setelah = snapshot_setelah["rekening"]

print()
print("=== KONDISI SETELAH ROLLBACK ===")
print(
    "Saldo SQLite     :",
    f"Rp{Utilitas.format_rupiah(data_setelah['saldo'])}"
)
print(
    "Saldo objek      :",
    f"Rp{Utilitas.format_rupiah(rekening.saldo)}"
)
print(
    "Periode SQLite   :",
    data_setelah["dapat_bunga"]
)
print(
    "Periode objek    :",
    rekening.dapat_bunga
)
print(
    "Jumlah transaksi :",
    snapshot_setelah["jumlah_transaksi"]
)
print(
    "Jumlah riwayat   :",
    snapshot_setelah["jumlah_riwayat"]
)
print(
    "Jumlah audit     :",
    snapshot_setelah["jumlah_audit"]
)
print()


# Seluruh kondisi SQLite harus identik dengan kondisi awal.
assert snapshot_setelah == snapshot_sebelum, (
    "Data SQLite berubah meskipun transaksi telah di-rollback"
)

# State objek Python juga tidak boleh berubah karena perubahan
# objek dilakukan service hanya setelah commit berhasil.
assert rekening.saldo == saldo_objek_sebelum, (
    "Saldo objek Python berubah meskipun proses gagal"
)

assert rekening.dapat_bunga == periode_objek_sebelum, (
    "Periode bunga objek berubah meskipun proses gagal"
)

assert rekening.riwayat == riwayat_objek_sebelum, (
    "Riwayat objek bertambah meskipun proses gagal"
)


# Pemeriksaan lebih terperinci agar sumber masalah mudah
# ditemukan apabila salah satu assertion gagal.
assert (
    data_setelah["saldo"]
    == data_sebelum["saldo"]
), "Saldo SQLite tidak berhasil dipulihkan"

assert (
    data_setelah["dapat_bunga"]
    == data_sebelum["dapat_bunga"]
), "Periode bunga SQLite tidak berhasil dipulihkan"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi bunga masih tersisa setelah rollback"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat bunga masih tersisa setelah rollback"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Audit bunga bertambah meskipun proses gagal"


print(
    "✅ ROLLBACK BUNGA BERHASIL: "
    "saldo, periode bunga, transaksi, riwayat, audit, "
    "dan state objek Python tidak berubah"
)