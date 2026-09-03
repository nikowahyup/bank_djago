# # # # # # import datetime
# # # # # #
# # # # # # from bank_djago.penyimpanan.repositories.transaksi_repository import (
# # # # # #     TransaksiRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # from bank_djago.utils.utility import JenisTransaksi
# # # # # #
# # # # # #
# # # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # # NOMINAL_PENGUJIAN = 10_000
# # # # # #
# # # # # #
# # # # # # koneksi = buat_koneksi()
# # # # # #
# # # # # # try:
# # # # # #     data_rekening = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT norek, saldo
# # # # # #         FROM rekening
# # # # # #         WHERE norek = ?
# # # # # #         """,
# # # # # #         (NOREK_PENGUJIAN,)
# # # # # #     ).fetchone()
# # # # # #
# # # # # #     if data_rekening is None:
# # # # # #         raise ValueError(
# # # # # #             "Rekening pengujian tidak ditemukan"
# # # # # #         )
# # # # # #
# # # # # #     jumlah_sebelum = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT COUNT(*) AS jumlah
# # # # # #         FROM transaksi
# # # # # #         """
# # # # # #     ).fetchone()["jumlah"]
# # # # # #
# # # # # #     saldo_sebelum = data_rekening["saldo"]
# # # # # #     saldo_sesudah = saldo_sebelum + NOMINAL_PENGUJIAN
# # # # # #     waktu_pengujian = datetime.datetime.now()
# # # # # #
# # # # # #     transaksi = {
# # # # # #         "jenis": JenisTransaksi.SETOR_TUNAI,
# # # # # #         "norek_tujuan": NOREK_PENGUJIAN,
# # # # # #         "nominal": NOMINAL_PENGUJIAN,
# # # # # #         "saldo_tujuan_sebelum": saldo_sebelum,
# # # # # #         "saldo_tujuan_sesudah": saldo_sesudah,
# # # # # #         "waktu": waktu_pengujian
# # # # # #     }
# # # # # #
# # # # # #     id_transaksi = TransaksiRepository.tambah_transaksi(
# # # # # #         transaksi=transaksi,
# # # # # #         koneksi=koneksi
# # # # # #     )
# # # # # #
# # # # # #     data_transaksi = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM transaksi
# # # # # #         WHERE id = ?
# # # # # #         """,
# # # # # #         (id_transaksi,)
# # # # # #     ).fetchone()
# # # # # #
# # # # # #     if data_transaksi is None:
# # # # # #         raise ValueError(
# # # # # #             "Transaksi tidak berhasil ditambahkan"
# # # # # #         )
# # # # # #
# # # # # #     print("HASIL PENGUJIAN TRANSAKSI REPOSITORY")
# # # # # #     print("ID                    :", data_transaksi["id"])
# # # # # #     print("Jenis                 :", data_transaksi["jenis"])
# # # # # #     print("Norek sumber          :", data_transaksi["norek_sumber"])
# # # # # #     print("Norek tujuan          :", data_transaksi["norek_tujuan"])
# # # # # #     print("Nominal               :", data_transaksi["nominal"])
# # # # # #     print("Biaya                 :", data_transaksi["biaya"])
# # # # # #     print(
# # # # # #         "Saldo tujuan sebelum :",
# # # # # #         data_transaksi["saldo_tujuan_sebelum"]
# # # # # #     )
# # # # # #     print(
# # # # # #         "Saldo tujuan sesudah :",
# # # # # #         data_transaksi["saldo_tujuan_sesudah"]
# # # # # #     )
# # # # # #     print("Waktu                 :", data_transaksi["waktu"])
# # # # # #
# # # # # #     assert (
# # # # # #         data_transaksi["jenis"]
# # # # # #         == JenisTransaksi.SETOR_TUNAI.value
# # # # # #     )
# # # # # #     print("✅ Enum jenis transaksi tersimpan sebagai string")
# # # # # #
# # # # # #     assert data_transaksi["norek_sumber"] is None
# # # # # #     assert data_transaksi["norek_tujuan"] == NOREK_PENGUJIAN
# # # # # #     print("✅ Rekening sumber dan tujuan tersimpan benar")
# # # # # #
# # # # # #     assert data_transaksi["nominal"] == NOMINAL_PENGUJIAN
# # # # # #     assert data_transaksi["biaya"] == 0
# # # # # #     print("✅ Nominal dan biaya tersimpan benar")
# # # # # #
# # # # # #     assert (
# # # # # #         data_transaksi["saldo_tujuan_sebelum"]
# # # # # #         == saldo_sebelum
# # # # # #     )
# # # # # #     assert (
# # # # # #         data_transaksi["saldo_tujuan_sesudah"]
# # # # # #         == saldo_sesudah
# # # # # #     )
# # # # # #     print("✅ Snapshot saldo tersimpan benar")
# # # # # #
# # # # # #     assert data_transaksi["saldo_sumber_sebelum"] is None
# # # # # #     assert data_transaksi["saldo_sumber_sesudah"] is None
# # # # # #     assert data_transaksi["jenis_referensi"] is None
# # # # # #     assert data_transaksi["id_referensi"] is None
# # # # # #     print("✅ Kolom opsional tersimpan sebagai NULL")
# # # # # #
# # # # # #     assert (
# # # # # #         datetime.datetime.fromisoformat(
# # # # # #             data_transaksi["waktu"]
# # # # # #         )
# # # # # #         == waktu_pengujian
# # # # # #     )
# # # # # #     print("✅ Waktu tersimpan dalam format datetime ISO")
# # # # # #
# # # # # #     # Membatalkan insert pengujian.
# # # # # #     koneksi.rollback()
# # # # # #
# # # # # #     jumlah_setelah_rollback = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT COUNT(*) AS jumlah
# # # # # #         FROM transaksi
# # # # # #         """
# # # # # #     ).fetchone()["jumlah"]
# # # # # #
# # # # # #     assert jumlah_setelah_rollback == jumlah_sebelum
# # # # # #     print("✅ Rollback menghapus transaksi pengujian")
# # # # # #
# # # # # #     print(
# # # # # #         "\n✅ TransaksiRepository.tambah_transaksi() "
# # # # # #         "berhasil diuji"
# # # # # #     )
# # # # # #
# # # # # # except Exception:
# # # # # #     koneksi.rollback()
# # # # # #     raise
# # # # # #
# # # # # # finally:
# # # # # #     koneksi.close()
# # # # #
# # # # #
# # # # #
# # # # # import datetime
# # # # #
# # # # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # # # #     RekeningLoader
# # # # # )
# # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # from bank_djago.utils.utility import JenisTransaksi
# # # # #
# # # # #
# # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # # NOMINAL_SETOR = 10_000
# # # # #
# # # # #
# # # # # # --------------------------------------------------
# # # # # # PERIKSA SQLITE
# # # # # # --------------------------------------------------
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     data_rekening = koneksi.execute(
# # # # #         """
# # # # #         SELECT norek, saldo
# # # # #         FROM rekening
# # # # #         WHERE norek = ?
# # # # #         """,
# # # # #         (NOREK_PENGUJIAN,)
# # # # #     ).fetchone()
# # # # #
# # # # #     data_transaksi = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM transaksi
# # # # #         WHERE norek_tujuan = ?
# # # # #           AND jenis = ?
# # # # #         ORDER BY id DESC
# # # # #         LIMIT 1
# # # # #         """,
# # # # #         (
# # # # #             NOREK_PENGUJIAN,
# # # # #             JenisTransaksi.SETOR_TUNAI.value
# # # # #         )
# # # # #     ).fetchone()
# # # # #
# # # # #     data_riwayat = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM riwayat
# # # # #         WHERE norek = ?
# # # # #           AND jenis = 'setor uang'
# # # # #         ORDER BY id DESC
# # # # #         LIMIT 1
# # # # #         """,
# # # # #         (NOREK_PENGUJIAN,)
# # # # #     ).fetchone()
# # # # #
# # # # #     data_audit = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM audit
# # # # #         WHERE norek = ?
# # # # #           AND jenis = 'setor uang'
# # # # #         ORDER BY id DESC
# # # # #         LIMIT 1
# # # # #         """,
# # # # #         (NOREK_PENGUJIAN,)
# # # # #     ).fetchone()
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # if data_rekening is None:
# # # # #     raise ValueError("Rekening pengujian tidak ditemukan")
# # # # #
# # # # # if data_transaksi is None:
# # # # #     raise ValueError("Data transaksi setor tidak ditemukan")
# # # # #
# # # # # if data_riwayat is None:
# # # # #     raise ValueError("Riwayat setor tidak ditemukan")
# # # # #
# # # # # if data_audit is None:
# # # # #     raise ValueError("Audit setor tidak ditemukan")
# # # # #
# # # # #
# # # # # print("HASIL PENGUJIAN SETOR TUNAI")
# # # # # print("ID transaksi :", data_transaksi["id"])
# # # # # print("Jenis        :", data_transaksi["jenis"])
# # # # # print("Norek tujuan :", data_transaksi["norek_tujuan"])
# # # # # print("Nominal      :", data_transaksi["nominal"])
# # # # # print(
# # # # #     "Saldo sebelum:",
# # # # #     data_transaksi["saldo_tujuan_sebelum"]
# # # # # )
# # # # # print(
# # # # #     "Saldo sesudah:",
# # # # #     data_transaksi["saldo_tujuan_sesudah"]
# # # # # )
# # # # # print("Saldo SQLite :", data_rekening["saldo"])
# # # # # print("Riwayat      :", data_riwayat["log"])
# # # # # print("Audit        :", data_audit["log"])
# # # # #
# # # # #
# # # # # # --------------------------------------------------
# # # # # # PERIKSA DATA TRANSAKSI
# # # # # # --------------------------------------------------
# # # # #
# # # # # assert (
# # # # #     data_transaksi["jenis"]
# # # # #     == JenisTransaksi.SETOR_TUNAI.value
# # # # # )
# # # # # assert data_transaksi["norek_sumber"] is None
# # # # # assert data_transaksi["norek_tujuan"] == NOREK_PENGUJIAN
# # # # #
# # # # # print("✅ Arah transaksi setor tersimpan benar")
# # # # #
# # # # #
# # # # # assert data_transaksi["nominal"] == NOMINAL_SETOR
# # # # # assert data_transaksi["biaya"] == 0
# # # # #
# # # # # print("✅ Nominal dan biaya tersimpan benar")
# # # # #
# # # # #
# # # # # assert data_transaksi["saldo_sumber_sebelum"] is None
# # # # # assert data_transaksi["saldo_sumber_sesudah"] is None
# # # # #
# # # # # assert (
# # # # #     data_transaksi["saldo_tujuan_sesudah"]
# # # # #     == data_transaksi["saldo_tujuan_sebelum"]
# # # # #     + data_transaksi["nominal"]
# # # # # )
# # # # #
# # # # # print("✅ Perubahan snapshot saldo sesuai nominal setor")
# # # # #
# # # # #
# # # # # assert (
# # # # #     data_rekening["saldo"]
# # # # #     == data_transaksi["saldo_tujuan_sesudah"]
# # # # # )
# # # # #
# # # # # print("✅ Saldo SQLite sama dengan snapshot akhir transaksi")
# # # # #
# # # # #
# # # # # waktu_transaksi = datetime.datetime.fromisoformat(
# # # # #     data_transaksi["waktu"]
# # # # # )
# # # # #
# # # # # assert isinstance(waktu_transaksi, datetime.datetime)
# # # # #
# # # # # print("✅ Waktu transaksi tersimpan sebagai datetime ISO")
# # # # #
# # # # #
# # # # # # --------------------------------------------------
# # # # # # PERIKSA RIWAYAT DAN AUDIT
# # # # # # --------------------------------------------------
# # # # #
# # # # # assert data_riwayat["jenis"] == "setor uang"
# # # # # assert data_audit["jenis"] == "setor uang"
# # # # #
# # # # # print("✅ Riwayat dan audit setor berhasil disimpan")
# # # # #
# # # # #
# # # # # # --------------------------------------------------
# # # # # # PERIKSA LOADER DAN OBJEK REKENING
# # # # # # --------------------------------------------------
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     rekening = RekeningLoader.muat_rekening(
# # # # #         norek=NOREK_PENGUJIAN,
# # # # #         koneksi=koneksi
# # # # #     )
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # if rekening is None:
# # # # #     raise ValueError("Loader gagal memuat rekening")
# # # # #
# # # # #
# # # # # assert rekening.saldo == data_rekening["saldo"]
# # # # #
# # # # # print("✅ Loader memulihkan saldo terbaru")
# # # # #
# # # # #
# # # # # print(
# # # # #     "\n✅ Setor tunai tersimpan konsisten pada "
# # # # #     "saldo, transaksi, riwayat, audit, dan loader"
# # # # # )
# # # # import datetime
# # # #
# # # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # # #     RekeningLoader
# # # # )
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # from bank_djago.utils.utility import JenisTransaksi
# # # #
# # # #
# # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # NOMINAL_TARIK = 10_000
# # # #
# # # #
# # # # koneksi = buat_koneksi()
# # # #
# # # # try:
# # # #     data_rekening = koneksi.execute(
# # # #         """
# # # #         SELECT norek, saldo
# # # #         FROM rekening
# # # #         WHERE norek = ?
# # # #         """,
# # # #         (NOREK_PENGUJIAN,)
# # # #     ).fetchone()
# # # #
# # # #     data_transaksi = koneksi.execute(
# # # #         """
# # # #         SELECT *
# # # #         FROM transaksi
# # # #         WHERE norek_sumber = ?
# # # #           AND jenis = ?
# # # #         ORDER BY id DESC
# # # #         LIMIT 1
# # # #         """,
# # # #         (
# # # #             NOREK_PENGUJIAN,
# # # #             JenisTransaksi.TARIK_TUNAI.value
# # # #         )
# # # #     ).fetchone()
# # # #
# # # #     data_riwayat = koneksi.execute(
# # # #         """
# # # #         SELECT *
# # # #         FROM riwayat
# # # #         WHERE norek = ?
# # # #           AND jenis = 'tarik uang'
# # # #         ORDER BY id DESC
# # # #         LIMIT 1
# # # #         """,
# # # #         (NOREK_PENGUJIAN,)
# # # #     ).fetchone()
# # # #
# # # #     data_audit = koneksi.execute(
# # # #         """
# # # #         SELECT *
# # # #         FROM audit
# # # #         WHERE norek = ?
# # # #           AND jenis = 'tarik uang'
# # # #         ORDER BY id DESC
# # # #         LIMIT 1
# # # #         """,
# # # #         (NOREK_PENGUJIAN,)
# # # #     ).fetchone()
# # # #
# # # # finally:
# # # #     koneksi.close()
# # # #
# # # #
# # # # if data_rekening is None:
# # # #     raise ValueError("Rekening pengujian tidak ditemukan")
# # # #
# # # # if data_transaksi is None:
# # # #     raise ValueError("Transaksi tarik tunai tidak ditemukan")
# # # #
# # # # if data_riwayat is None:
# # # #     raise ValueError("Riwayat tarik tunai tidak ditemukan")
# # # #
# # # # if data_audit is None:
# # # #     raise ValueError("Audit tarik tunai tidak ditemukan")
# # # #
# # # #
# # # # print("HASIL PENGUJIAN TARIK TUNAI")
# # # # print("ID transaksi :", data_transaksi["id"])
# # # # print("Jenis        :", data_transaksi["jenis"])
# # # # print("Norek sumber :", data_transaksi["norek_sumber"])
# # # # print("Nominal      :", data_transaksi["nominal"])
# # # # print(
# # # #     "Saldo sebelum:",
# # # #     data_transaksi["saldo_sumber_sebelum"]
# # # # )
# # # # print(
# # # #     "Saldo sesudah:",
# # # #     data_transaksi["saldo_sumber_sesudah"]
# # # # )
# # # # print("Saldo SQLite :", data_rekening["saldo"])
# # # # print("Riwayat      :", data_riwayat["log"])
# # # # print("Audit        :", data_audit["log"])
# # # #
# # # #
# # # # # Memeriksa arah transaksi
# # # # assert data_transaksi["norek_sumber"] == NOREK_PENGUJIAN
# # # # assert data_transaksi["norek_tujuan"] is None
# # # # assert data_transaksi["saldo_tujuan_sebelum"] is None
# # # # assert data_transaksi["saldo_tujuan_sesudah"] is None
# # # #
# # # # print("✅ Arah transaksi tarik tunai tersimpan benar")
# # # #
# # # #
# # # # # Memeriksa nominal dan biaya
# # # # assert data_transaksi["nominal"] == NOMINAL_TARIK
# # # # assert data_transaksi["biaya"] == 0
# # # #
# # # # print("✅ Nominal dan biaya tersimpan benar")
# # # #
# # # #
# # # # # Memeriksa perhitungan snapshot
# # # # assert (
# # # #     data_transaksi["saldo_sumber_sesudah"]
# # # #     == data_transaksi["saldo_sumber_sebelum"]
# # # #     - data_transaksi["nominal"]
# # # # )
# # # #
# # # # print("✅ Perubahan snapshot saldo sesuai nominal tarik")
# # # #
# # # #
# # # # # Memeriksa saldo terbaru SQLite
# # # # assert (
# # # #     data_rekening["saldo"]
# # # #     == data_transaksi["saldo_sumber_sesudah"]
# # # # )
# # # #
# # # # print("✅ Saldo SQLite sama dengan snapshot akhir transaksi")
# # # #
# # # #
# # # # # Memeriksa format waktu
# # # # waktu_transaksi = datetime.datetime.fromisoformat(
# # # #     data_transaksi["waktu"]
# # # # )
# # # #
# # # # assert isinstance(waktu_transaksi, datetime.datetime)
# # # #
# # # # print("✅ Waktu transaksi tersimpan sebagai datetime ISO")
# # # #
# # # #
# # # # # Memeriksa riwayat dan audit
# # # # assert data_riwayat["jenis"] == "tarik uang"
# # # # assert data_audit["jenis"] == "tarik uang"
# # # #
# # # # print("✅ Riwayat dan audit tarik tunai berhasil disimpan")
# # # #
# # # #
# # # # # Memeriksa loader
# # # # koneksi = buat_koneksi()
# # # #
# # # # try:
# # # #     rekening = RekeningLoader.muat_rekening(
# # # #         norek=NOREK_PENGUJIAN,
# # # #         koneksi=koneksi
# # # #     )
# # # # finally:
# # # #     koneksi.close()
# # # #
# # # #
# # # # if rekening is None:
# # # #     raise ValueError("Loader gagal memuat rekening")
# # # #
# # # #
# # # # assert rekening.saldo == data_rekening["saldo"]
# # # #
# # # # print("✅ Loader memulihkan saldo terbaru")
# # # #
# # # #
# # # # print(
# # # #     "\n✅ Tarik tunai tersimpan konsisten pada "
# # # #     "saldo, transaksi, riwayat, audit, dan loader"
# # # # )
# # #
# # #
# # #
# # # import datetime
# # #
# # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # #     RekeningLoader
# # # )
# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # from bank_djago.utils.utility import JenisTransaksi
# # #
# # #
# # # NOREK_PENGIRIM = "3001781978899033"
# # # NOREK_PENERIMA = "2001569043650499"
# # # NOMINAL_TRANSFER = 99_990
# # #
# # #
# # # # --------------------------------------------------
# # # # MENGAMBIL DATA SQLITE
# # # # --------------------------------------------------
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     data_transaksi = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM transaksi
# # #         WHERE jenis = ?
# # #           AND norek_sumber = ?
# # #           AND norek_tujuan = ?
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (
# # #             JenisTransaksi.TRANSFER.value,
# # #             NOREK_PENGIRIM,
# # #             NOREK_PENERIMA
# # #         )
# # #     ).fetchone()
# # #
# # #     data_pengirim = koneksi.execute(
# # #         """
# # #         SELECT norek, saldo
# # #         FROM rekening
# # #         WHERE norek = ?
# # #         """,
# # #         (NOREK_PENGIRIM,)
# # #     ).fetchone()
# # #
# # #     data_penerima = koneksi.execute(
# # #         """
# # #         SELECT norek, saldo
# # #         FROM rekening
# # #         WHERE norek = ?
# # #         """,
# # #         (NOREK_PENERIMA,)
# # #     ).fetchone()
# # #
# # #     riwayat_pengirim = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM riwayat
# # #         WHERE norek = ?
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (NOREK_PENGIRIM,)
# # #     ).fetchone()
# # #
# # #     riwayat_penerima = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM riwayat
# # #         WHERE norek = ?
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (NOREK_PENERIMA,)
# # #     ).fetchone()
# # #
# # #     audit_pengirim = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM audit
# # #         WHERE norek = ?
# # #           AND jenis = 'transfer'
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (NOREK_PENGIRIM,)
# # #     ).fetchone()
# # #
# # #     audit_penerima = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM audit
# # #         WHERE norek = ?
# # #           AND jenis = 'terima saldo'
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (NOREK_PENERIMA,)
# # #     ).fetchone()
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # if data_transaksi is None:
# # #     raise ValueError("Transaksi transfer tidak ditemukan")
# # #
# # # if data_pengirim is None:
# # #     raise ValueError("Rekening pengirim tidak ditemukan")
# # #
# # # if data_penerima is None:
# # #     raise ValueError("Rekening penerima tidak ditemukan")
# # #
# # # if riwayat_pengirim is None or riwayat_penerima is None:
# # #     raise ValueError("Riwayat transfer tidak lengkap")
# # #
# # # if audit_pengirim is None or audit_penerima is None:
# # #     raise ValueError("Audit transfer tidak lengkap")
# # #
# # #
# # # # --------------------------------------------------
# # # # MENAMPILKAN DATA
# # # # --------------------------------------------------
# # #
# # # print("HASIL PENGUJIAN TRANSFER")
# # # print("ID transaksi          :", data_transaksi["id"])
# # # print("Jenis                 :", data_transaksi["jenis"])
# # # print("Norek pengirim        :", data_transaksi["norek_sumber"])
# # # print("Norek penerima        :", data_transaksi["norek_tujuan"])
# # # print("Nominal               :", data_transaksi["nominal"])
# # # print("Biaya                 :", data_transaksi["biaya"])
# # # print(
# # #     "Saldo pengirim awal  :",
# # #     data_transaksi["saldo_sumber_sebelum"]
# # # )
# # # print(
# # #     "Saldo pengirim akhir :",
# # #     data_transaksi["saldo_sumber_sesudah"]
# # # )
# # # print(
# # #     "Saldo penerima awal  :",
# # #     data_transaksi["saldo_tujuan_sebelum"]
# # # )
# # # print(
# # #     "Saldo penerima akhir :",
# # #     data_transaksi["saldo_tujuan_sesudah"]
# # # )
# # # print("Riwayat pengirim      :", riwayat_pengirim["log"])
# # # print("Riwayat penerima      :", riwayat_penerima["log"])
# # # print("Audit pengirim        :", audit_pengirim["log"])
# # # print("Audit penerima        :", audit_penerima["log"])
# # #
# # #
# # # # --------------------------------------------------
# # # # MEMERIKSA IDENTITAS TRANSAKSI
# # # # --------------------------------------------------
# # #
# # # assert (
# # #     data_transaksi["jenis"]
# # #     == JenisTransaksi.TRANSFER.value
# # # )
# # #
# # # assert data_transaksi["norek_sumber"] == NOREK_PENGIRIM
# # # assert data_transaksi["norek_tujuan"] == NOREK_PENERIMA
# # # assert data_transaksi["nominal"] == NOMINAL_TRANSFER
# # #
# # # print("✅ Identitas transaksi transfer tersimpan benar")
# # #
# # #
# # # # --------------------------------------------------
# # # # MEMERIKSA SALDO PENGIRIM
# # # # --------------------------------------------------
# # #
# # # total_debit = (
# # #     data_transaksi["nominal"]
# # #     + data_transaksi["biaya"]
# # # )
# # #
# # # assert (
# # #     data_transaksi["saldo_sumber_sesudah"]
# # #     == data_transaksi["saldo_sumber_sebelum"]
# # #     - total_debit
# # # )
# # #
# # # assert (
# # #     data_pengirim["saldo"]
# # #     == data_transaksi["saldo_sumber_sesudah"]
# # # )
# # #
# # # print("✅ Saldo pengirim berkurang sebesar nominal + biaya")
# # #
# # #
# # # # --------------------------------------------------
# # # # MEMERIKSA SALDO PENERIMA
# # # # --------------------------------------------------
# # #
# # # assert (
# # #     data_transaksi["saldo_tujuan_sesudah"]
# # #     == data_transaksi["saldo_tujuan_sebelum"]
# # #     + data_transaksi["nominal"]
# # # )
# # #
# # # assert (
# # #     data_penerima["saldo"]
# # #     == data_transaksi["saldo_tujuan_sesudah"]
# # # )
# # #
# # # print("✅ Saldo penerima bertambah sebesar nominal")
# # #
# # #
# # # # Rekening pengirim adalah Gold sehingga pajaknya nol.
# # # assert data_transaksi["biaya"] == 0
# # #
# # # print("✅ Biaya transfer sesuai ketentuan rekening Gold")
# # #
# # #
# # # # Transfer tidak merujuk deposito atau pinjaman.
# # # assert data_transaksi["jenis_referensi"] is None
# # # assert data_transaksi["id_referensi"] is None
# # #
# # # print("✅ Referensi transaksi transfer tersimpan NULL")
# # #
# # #
# # # # --------------------------------------------------
# # # # MEMERIKSA WAKTU, RIWAYAT, DAN AUDIT
# # # # --------------------------------------------------
# # #
# # # waktu_transaksi = datetime.datetime.fromisoformat(
# # #     data_transaksi["waktu"]
# # # )
# # #
# # # assert isinstance(waktu_transaksi, datetime.datetime)
# # #
# # # print("✅ Waktu transfer tersimpan sebagai datetime ISO")
# # #
# # #
# # # assert audit_pengirim["jenis"] == "transfer"
# # # assert audit_penerima["jenis"] == "terima saldo"
# # #
# # # print("✅ Dua audit transfer berhasil disimpan")
# # #
# # #
# # # assert str(NOMINAL_TRANSFER) or riwayat_pengirim["log"]
# # # assert str(NOMINAL_TRANSFER) or riwayat_penerima["log"]
# # #
# # # print("✅ Dua riwayat transfer berhasil disimpan")
# # #
# # #
# # # # --------------------------------------------------
# # # # MEMERIKSA LOADER
# # # # --------------------------------------------------
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     pengirim = RekeningLoader.muat_rekening(
# # #         norek=NOREK_PENGIRIM,
# # #         koneksi=koneksi
# # #     )
# # #
# # #     penerima = RekeningLoader.muat_rekening(
# # #         norek=NOREK_PENERIMA,
# # #         koneksi=koneksi
# # #     )
# # #
# # # finally:
# # #     koneksi.close()
# # #
# # #
# # # if pengirim is None or penerima is None:
# # #     raise ValueError("Loader gagal memuat rekening transfer")
# # #
# # #
# # # assert pengirim.saldo == data_pengirim["saldo"]
# # # assert penerima.saldo == data_penerima["saldo"]
# # #
# # # print("✅ Loader memulihkan kedua saldo terbaru")
# # #
# # #
# # # print(
# # #     "\n✅ Transfer konsisten pada transaksi, kedua saldo, "
# # #     "riwayat, audit, dan loader"
# # # )
# #
# #
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# #
# #
# # DAFTAR_TABEL = (
# #     "riwayat",
# #     "audit"
# # )
# #
# #
# # koneksi = buat_koneksi()
# #
# # try:
# #     for nama_tabel in DAFTAR_TABEL:
# #         print(f"\nPEMERIKSAAN TABEL {nama_tabel.upper()}")
# #
# #         daftar_kolom = koneksi.execute(
# #             f"PRAGMA table_info({nama_tabel})"
# #         ).fetchall()
# #
# #         kolom_transaksi = next(
# #             (
# #                 kolom
# #                 for kolom in daftar_kolom
# #                 if kolom["name"] == "transaksi_id"
# #             ),
# #             None
# #         )
# #
# #         assert kolom_transaksi is not None, (
# #             f"Kolom transaksi_id tidak ditemukan "
# #             f"pada tabel {nama_tabel}"
# #         )
# #
# #         print("✅ Kolom transaksi_id tersedia")
# #         print("Tipe data :", kolom_transaksi["type"])
# #         print("Not null  :", kolom_transaksi["notnull"])
# #
# #         assert kolom_transaksi["type"] == "INTEGER"
# #         print("✅ Tipe transaksi_id adalah INTEGER")
# #
# #         assert kolom_transaksi["notnull"] == 0
# #         print("✅ transaksi_id dapat menerima NULL")
# #
# #         daftar_foreign_key = koneksi.execute(
# #             f"PRAGMA foreign_key_list({nama_tabel})"
# #         ).fetchall()
# #
# #         foreign_key_transaksi = next(
# #             (
# #                 foreign_key
# #                 for foreign_key in daftar_foreign_key
# #                 if (
# #                     foreign_key["from"] == "transaksi_id"
# #                     and foreign_key["table"] == "transaksi"
# #                     and foreign_key["to"] == "id"
# #                 )
# #             ),
# #             None
# #         )
# #
# #         assert foreign_key_transaksi is not None, (
# #             f"Foreign key transaksi_id pada "
# #             f"{nama_tabel} tidak ditemukan"
# #         )
# #
# #         print("✅ Foreign key transaksi_id tersedia")
# #         print(
# #             "Relasi    :",
# #             f"{nama_tabel}.transaksi_id "
# #             f"→ transaksi.id"
# #         )
# #         print(
# #             "ON UPDATE :",
# #             foreign_key_transaksi["on_update"]
# #         )
# #         print(
# #             "ON DELETE :",
# #             foreign_key_transaksi["on_delete"]
# #         )
# #
# #         assert (
# #             foreign_key_transaksi["on_update"]
# #             == "CASCADE"
# #         )
# #
# #         assert (
# #             foreign_key_transaksi["on_delete"]
# #             == "RESTRICT"
# #         )
# #
# #         print("✅ Aturan foreign key sesuai rancangan")
# #
# #     status_foreign_key = koneksi.execute(
# #         "PRAGMA foreign_keys"
# #     ).fetchone()[0]
# #
# #     print("\nSTATUS FOREIGN KEY:", status_foreign_key)
# #
# #     assert status_foreign_key == 1
# #     print("✅ Pemeriksaan foreign key aktif")
# #
# # finally:
# #     koneksi.close()
# #
# #
# # print(
# #     "\n✅ Kolom transaksi_id pada audit dan riwayat "
# #     "berhasil diverifikasi"
# # )
#
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.utils.utility import JenisTransaksi
#
#
# NOREK_PENGIRIM = "3001781978899033"
# NOREK_PENERIMA = "2001569043650499"
# NOMINAL = 999_999
#
#
# koneksi = buat_koneksi()
#
# try:
#     transaksi_setor = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE jenis = ?
#           AND norek_tujuan = ?
#           AND nominal = ?
#         ORDER BY id DESC
#         LIMIT 1
#         """,
#         (
#             JenisTransaksi.SETOR_TUNAI.value,
#             NOREK_PENGIRIM,
#             NOMINAL
#         )
#     ).fetchone()
#
#     transaksi_tarik = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE jenis = ?
#           AND norek_sumber = ?
#           AND nominal = ?
#         ORDER BY id DESC
#         LIMIT 1
#         """,
#         (
#             JenisTransaksi.TARIK_TUNAI.value,
#             NOREK_PENGIRIM,
#             NOMINAL
#         )
#     ).fetchone()
#
#     transaksi_transfer = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE jenis = ?
#           AND norek_sumber = ?
#           AND norek_tujuan = ?
#           AND nominal = ?
#         ORDER BY id DESC
#         LIMIT 1
#         """,
#         (
#             JenisTransaksi.TRANSFER.value,
#             NOREK_PENGIRIM,
#             NOREK_PENERIMA,
#             NOMINAL
#         )
#     ).fetchone()
#
#     if None in (
#         transaksi_setor,
#         transaksi_tarik,
#         transaksi_transfer
#     ):
#         raise ValueError(
#             "Salah satu transaksi pengujian tidak ditemukan"
#         )
#
#     daftar_transaksi = {
#         "SETOR": transaksi_setor,
#         "TARIK": transaksi_tarik,
#         "TRANSFER": transaksi_transfer
#     }
#
#     for nama, transaksi in daftar_transaksi.items():
#         riwayat = koneksi.execute(
#             """
#             SELECT *
#             FROM riwayat
#             WHERE transaksi_id = ?
#             ORDER BY id
#             """,
#             (transaksi["id"],)
#         ).fetchall()
#
#         audit = koneksi.execute(
#             """
#             SELECT *
#             FROM audit
#             WHERE transaksi_id = ?
#             ORDER BY id
#             """,
#             (transaksi["id"],)
#         ).fetchall()
#
#         print(f"\n{nama}")
#         print("ID transaksi :", transaksi["id"])
#         print("Jenis        :", transaksi["jenis"])
#         print("Jumlah riwayat:", len(riwayat))
#         print("Jumlah audit :", len(audit))
#
#         for data in riwayat:
#             print(
#                 "Riwayat:",
#                 data["norek"],
#                 "|",
#                 data["log"]
#             )
#
#         for data in audit:
#             print(
#                 "Audit:",
#                 data["norek"],
#                 "|",
#                 data["log"]
#             )
#
#         jumlah_yang_diharapkan = (
#             2 if nama == "TRANSFER" else 1
#         )
#
#         assert len(riwayat) == jumlah_yang_diharapkan
#         assert len(audit) == jumlah_yang_diharapkan
#
#         assert all(
#             data["transaksi_id"] == transaksi["id"]
#             for data in riwayat
#         )
#
#         assert all(
#             data["transaksi_id"] == transaksi["id"]
#             for data in audit
#         )
#
#         print(
#             f"✅ Seluruh audit dan riwayat {nama.lower()} "
#             f"terhubung ke transaksi ID {transaksi['id']}"
#         )
#
#     # Setor: saldo tujuan bertambah.
#     assert (
#         transaksi_setor["saldo_tujuan_sesudah"]
#         == transaksi_setor["saldo_tujuan_sebelum"]
#         + NOMINAL
#     )
#
#     print("✅ Snapshot setor tunai benar")
#
#     # Tarik: saldo sumber berkurang.
#     assert (
#         transaksi_tarik["saldo_sumber_sesudah"]
#         == transaksi_tarik["saldo_sumber_sebelum"]
#         - NOMINAL
#     )
#
#     print("✅ Snapshot tarik tunai benar")
#
#     # Transfer: pengirim membayar nominal + biaya.
#     assert (
#         transaksi_transfer["saldo_sumber_sesudah"]
#         == transaksi_transfer["saldo_sumber_sebelum"]
#         - transaksi_transfer["nominal"]
#         - transaksi_transfer["biaya"]
#     )
#
#     assert (
#         transaksi_transfer["saldo_tujuan_sesudah"]
#         == transaksi_transfer["saldo_tujuan_sebelum"]
#         + transaksi_transfer["nominal"]
#     )
#
#     print("✅ Kedua snapshot saldo transfer benar")
#
#     # Memastikan dua sisi transfer memiliki norek yang tepat.
#     riwayat_transfer = koneksi.execute(
#         """
#         SELECT norek
#         FROM riwayat
#         WHERE transaksi_id = ?
#         """,
#         (transaksi_transfer["id"],)
#     ).fetchall()
#
#     audit_transfer = koneksi.execute(
#         """
#         SELECT norek
#         FROM audit
#         WHERE transaksi_id = ?
#         """,
#         (transaksi_transfer["id"],)
#     ).fetchall()
#
#     assert {
#         data["norek"]
#         for data in riwayat_transfer
#     } == {
#         NOREK_PENGIRIM,
#         NOREK_PENERIMA
#     }
#
#     assert {
#         data["norek"]
#         for data in audit_transfer
#     } == {
#         NOREK_PENGIRIM,
#         NOREK_PENERIMA
#     }
#
#     print("✅ Dua sisi transfer terhubung ke rekening yang tepat")
#
#     # Urutan transaksi sesuai tindakan pengujian.
#     assert (
#         transaksi_setor["id"]
#         < transaksi_tarik["id"]
#         < transaksi_transfer["id"]
#     )
#
#     print("✅ Urutan transaksi setor, tarik, dan transfer benar")
#
# finally:
#     koneksi.close()
#
#
# print(
#     "\n✅ Setor, tarik, dan transfer memiliki hubungan "
#     "transaksi–riwayat–audit yang konsisten"
# )



import datetime

from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NIK_PENGUJIAN = "5555666677778888"
NOREK_PENGUJIAN = "2001842427316253"
SETOR_AWAL = 100_000_000


# --------------------------------------------------
# MENGAMBIL DATA SQLITE
# --------------------------------------------------

koneksi = buat_koneksi()

try:
    data_rekening = koneksi.execute(
        """
        SELECT *
        FROM rekening
        WHERE norek = ?
          AND nik_pemilik = ?
        """,
        (
            NOREK_PENGUJIAN,
            NIK_PENGUJIAN
        )
    ).fetchone()

    data_transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_tujuan = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.SETOR_AWAL.value,
            NOREK_PENGUJIAN
        )
    ).fetchone()

    if data_transaksi is None:
        raise ValueError(
            "Transaksi setor awal tidak ditemukan"
        )

    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (data_transaksi["id"],)
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (data_transaksi["id"],)
    ).fetchall()

finally:
    koneksi.close()


if data_rekening is None:
    raise ValueError("Rekening baru tidak ditemukan")


print("HASIL PENGUJIAN SETOR AWAL")
print("NIK                :", data_rekening["nik_pemilik"])
print("Norek              :", data_rekening["norek"])
print("Level              :", data_rekening["level"])
print("Saldo              :", data_rekening["saldo"])
print("Waktu dibuat       :", data_rekening["waktu_dibuat"])
print("ID transaksi       :", data_transaksi["id"])
print("Jenis transaksi    :", data_transaksi["jenis"])
print("Saldo awal tercatat:", data_transaksi["saldo_tujuan_sebelum"])
print("Saldo akhir tercatat:", data_transaksi["saldo_tujuan_sesudah"])
print("Jumlah riwayat     :", len(daftar_riwayat))
print("Jumlah audit       :", len(daftar_audit))

for riwayat in daftar_riwayat:
    print("Riwayat:", riwayat["log"])

for audit in daftar_audit:
    print("Audit:", audit["log"])


# --------------------------------------------------
# MEMERIKSA REKENING
# --------------------------------------------------

assert data_rekening["nik_pemilik"] == NIK_PENGUJIAN
assert data_rekening["norek"] == NOREK_PENGUJIAN
assert data_rekening["saldo"] == SETOR_AWAL
assert data_rekening["status"] == "aktif"

print("✅ Rekening baru dan saldo awal tersimpan benar")


waktu_dibuat = datetime.datetime.fromisoformat(
    data_rekening["waktu_dibuat"]
)

assert isinstance(waktu_dibuat, datetime.datetime)

print("✅ Waktu pembukaan tersimpan sebagai datetime ISO")


# --------------------------------------------------
# MEMERIKSA TRANSAKSI SETOR AWAL
# --------------------------------------------------

assert (
    data_transaksi["jenis"]
    == JenisTransaksi.SETOR_AWAL.value
)

assert data_transaksi["norek_sumber"] is None
assert data_transaksi["norek_tujuan"] == NOREK_PENGUJIAN
assert data_transaksi["nominal"] == SETOR_AWAL
assert data_transaksi["biaya"] == 0

print("✅ Identitas transaksi setor awal tersimpan benar")


assert data_transaksi["saldo_sumber_sebelum"] is None
assert data_transaksi["saldo_sumber_sesudah"] is None
assert data_transaksi["saldo_tujuan_sebelum"] == 0
assert data_transaksi["saldo_tujuan_sesudah"] == SETOR_AWAL

print("✅ Snapshot setor awal tercatat dari 0 ke Rp100 juta")


assert (
    data_rekening["saldo"]
    == data_transaksi["saldo_tujuan_sesudah"]
)

print("✅ Saldo rekening sama dengan snapshot akhir")


assert data_transaksi["jenis_referensi"] is None
assert data_transaksi["id_referensi"] is None

print("✅ Referensi deposito/pinjaman tersimpan NULL")


# --------------------------------------------------
# MEMERIKSA RIWAYAT DAN AUDIT
# --------------------------------------------------

assert len(daftar_riwayat) == 1
assert len(daftar_audit) == 1

riwayat = daftar_riwayat[0]
audit = daftar_audit[0]

assert riwayat["transaksi_id"] == data_transaksi["id"]
assert audit["transaksi_id"] == data_transaksi["id"]

assert riwayat["norek"] == NOREK_PENGUJIAN
assert audit["norek"] == NOREK_PENGUJIAN
assert audit["nik"] == NIK_PENGUJIAN

assert riwayat["jenis"] == "setor awal"
assert audit["jenis"] == "pembukaan"

print(
    "✅ Riwayat dan audit terhubung ke transaksi "
    "setor awal yang sama"
)


# --------------------------------------------------
# MEMERIKSA LOADER
# --------------------------------------------------

koneksi = buat_koneksi()

try:
    rekening = RekeningLoader.muat_rekening(
        norek=NOREK_PENGUJIAN,
        koneksi=koneksi
    )
finally:
    koneksi.close()


if rekening is None:
    raise ValueError("Loader gagal memuat rekening baru")


assert rekening.norek == NOREK_PENGUJIAN
assert rekening.pemilik.NIK == NIK_PENGUJIAN
assert rekening.saldo == SETOR_AWAL
assert rekening.waktu_dibuat == waktu_dibuat

print("✅ Loader memulihkan rekening dan waktu pembukaan")


print(
    "\n✅ Pembukaan rekening dan transaksi SETOR_AWAL "
    "tersimpan secara konsisten"
)