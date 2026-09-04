# # # from bank_djago.penyimpanan.sqlite.database import (
# # #     buat_koneksi
# # # )
# # #
# # #
# # # def migrasi_constraint_transaksi():
# # #     """
# # #     Membangun ulang tabel transaksi agar transaksi berbasis
# # #     referensi objek diperbolehkan meskipun tidak memiliki
# # #     rekening sumber atau tujuan.
# # #
# # #     Seluruh ID transaksi lama dipertahankan agar foreign key
# # #     pada tabel audit dan riwayat tidak terputus.
# # #     """
# # #     koneksi = buat_koneksi()
# # #
# # #     try:
# # #         # Foreign key dimatikan sementara karena tabel transaksi
# # #         # lama akan diganti. Ini harus dilakukan sebelum BEGIN.
# # #         koneksi.execute("PRAGMA foreign_keys = OFF")
# # #
# # #         # BEGIN IMMEDIATE mencegah proses lain menulis ke database
# # #         # selama migrasi berlangsung.
# # #         koneksi.execute("BEGIN IMMEDIATE")
# # #
# # #         # Pastikan tidak ada tabel sisa dari percobaan migrasi.
# # #         tabel_sementara = koneksi.execute(
# # #             """
# # #             SELECT name
# # #             FROM sqlite_master
# # #             WHERE type = 'table'
# # #               AND name = 'transaksi_baru'
# # #             """
# # #         ).fetchone()
# # #
# # #         if tabel_sementara is not None:
# # #             raise RuntimeError(
# # #                 "Tabel transaksi_baru sudah tersedia. "
# # #                 "Periksa sisa migrasi sebelumnya."
# # #             )
# # #
# # #         jumlah_data_lama = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS jumlah
# # #             FROM transaksi
# # #             """
# # #         ).fetchone()["jumlah"]
# # #
# # #         # Buat tabel pengganti dengan struktur yang sama.
# # #         # Perbedaannya terletak pada CHECK yang sekarang juga
# # #         # menerima transaksi dengan id_referensi.
# # #         koneksi.execute(
# # #             """
# # #             CREATE TABLE transaksi_baru (
# # #                 id INTEGER PRIMARY KEY AUTOINCREMENT,
# # #
# # #                 jenis TEXT NOT NULL,
# # #
# # #                 norek_sumber TEXT,
# # #                 norek_tujuan TEXT,
# # #
# # #                 nominal INTEGER NOT NULL,
# # #                 biaya INTEGER NOT NULL DEFAULT 0,
# # #
# # #                 saldo_sumber_sebelum INTEGER,
# # #                 saldo_sumber_sesudah INTEGER,
# # #
# # #                 saldo_tujuan_sebelum INTEGER,
# # #                 saldo_tujuan_sesudah INTEGER,
# # #
# # #                 jenis_referensi TEXT,
# # #                 id_referensi INTEGER,
# # #
# # #                 waktu TEXT NOT NULL,
# # #
# # #                 CHECK (nominal > 0),
# # #                 CHECK (biaya >= 0),
# # #
# # #                 CHECK (
# # #                     saldo_sumber_sebelum IS NULL
# # #                     OR saldo_sumber_sebelum >= 0
# # #                 ),
# # #
# # #                 CHECK (
# # #                     saldo_sumber_sesudah IS NULL
# # #                     OR saldo_sumber_sesudah >= 0
# # #                 ),
# # #
# # #                 CHECK (
# # #                     saldo_tujuan_sebelum IS NULL
# # #                     OR saldo_tujuan_sebelum >= 0
# # #                 ),
# # #
# # #                 CHECK (
# # #                     saldo_tujuan_sesudah IS NULL
# # #                     OR saldo_tujuan_sesudah >= 0
# # #                 ),
# # #
# # #                 CHECK (
# # #                     norek_sumber IS NOT NULL
# # #                     OR norek_tujuan IS NOT NULL
# # #                     OR id_referensi IS NOT NULL
# # #                 ),
# # #
# # #                 CHECK (
# # #                     norek_sumber IS NULL
# # #                     OR norek_tujuan IS NULL
# # #                     OR norek_sumber != norek_tujuan
# # #                 ),
# # #
# # #                 FOREIGN KEY (norek_sumber)
# # #                 REFERENCES rekening(norek)
# # #                 ON UPDATE CASCADE
# # #                 ON DELETE RESTRICT,
# # #
# # #                 FOREIGN KEY (norek_tujuan)
# # #                 REFERENCES rekening(norek)
# # #                 ON UPDATE CASCADE
# # #                 ON DELETE RESTRICT
# # #             )
# # #             """
# # #         )
# # #
# # #         # Salin seluruh transaksi lama dengan ID yang sama.
# # #         # ID tidak boleh berubah karena audit dan riwayat
# # #         # telah menyimpan transaksi_id.
# # #         koneksi.execute(
# # #             """
# # #             INSERT INTO transaksi_baru (
# # #                 id,
# # #                 jenis,
# # #                 norek_sumber,
# # #                 norek_tujuan,
# # #                 nominal,
# # #                 biaya,
# # #                 saldo_sumber_sebelum,
# # #                 saldo_sumber_sesudah,
# # #                 saldo_tujuan_sebelum,
# # #                 saldo_tujuan_sesudah,
# # #                 jenis_referensi,
# # #                 id_referensi,
# # #                 waktu
# # #             )
# # #             SELECT
# # #                 id,
# # #                 jenis,
# # #                 norek_sumber,
# # #                 norek_tujuan,
# # #                 nominal,
# # #                 biaya,
# # #                 saldo_sumber_sebelum,
# # #                 saldo_sumber_sesudah,
# # #                 saldo_tujuan_sebelum,
# # #                 saldo_tujuan_sesudah,
# # #                 jenis_referensi,
# # #                 id_referensi,
# # #                 waktu
# # #             FROM transaksi
# # #             """
# # #         )
# # #
# # #         jumlah_data_baru = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS jumlah
# # #             FROM transaksi_baru
# # #             """
# # #         ).fetchone()["jumlah"]
# # #
# # #         # Jangan lanjut mengganti tabel jika jumlah data berbeda.
# # #         if jumlah_data_baru != jumlah_data_lama:
# # #             raise RuntimeError(
# # #                 "Jumlah transaksi hasil salinan tidak sesuai"
# # #             )
# # #
# # #         # Ganti tabel lama dengan tabel baru.
# # #         koneksi.execute("DROP TABLE transaksi")
# # #
# # #         koneksi.execute(
# # #             """
# # #             ALTER TABLE transaksi_baru
# # #             RENAME TO transaksi
# # #             """
# # #         )
# # #
# # #         # Periksa seluruh hubungan foreign key sebelum commit.
# # #         # Jika ada masalah, exception membuat perubahan schema
# # #         # dan penyalinan data ikut di-rollback.
# # #         kesalahan_fk = koneksi.execute(
# # #             """
# # #             PRAGMA foreign_key_check
# # #             """
# # #         ).fetchall()
# # #
# # #         if kesalahan_fk:
# # #             raise RuntimeError(
# # #                 f"Ditemukan masalah foreign key: {kesalahan_fk}"
# # #             )
# # #
# # #         koneksi.commit()
# # #
# # #         print("✅ Migrasi constraint transaksi berhasil")
# # #         print(
# # #             f"Jumlah transaksi dipertahankan: "
# # #             f"{jumlah_data_baru}"
# # #         )
# # #         print("Foreign key tetap valid")
# # #
# # #     except Exception:
# # #         koneksi.rollback()
# # #         raise
# # #
# # #     finally:
# # #         # Aktifkan kembali perlindungan foreign key sebelum
# # #         # koneksi ditutup.
# # #         koneksi.execute("PRAGMA foreign_keys = ON")
# # #         koneksi.close()
# # #
# # #
# # # if __name__ == "__main__":
# # #     migrasi_constraint_transaksi()
# #
# #
# #
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# #
# #
# # koneksi = buat_koneksi()
# #
# # try:
# #     struktur = koneksi.execute(
# #         """
# #         SELECT sql
# #         FROM sqlite_master
# #         WHERE type = 'table'
# #           AND name = 'transaksi'
# #         """
# #     ).fetchone()
# #
# #     print(struktur["sql"])
# #
# #     kesalahan_fk = koneksi.execute(
# #         "PRAGMA foreign_key_check"
# #     ).fetchall()
# #
# #     print(f"\nKesalahan foreign key: {kesalahan_fk}")
# #
# # finally:
# #     koneksi.close()
#
#
#
#
#
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.utils.utility import JenisReferensi
#
#
# def ubah_jenis_referensi_ke_string():
#     """
#     Mengubah nilai jenis_referensi lama:
#
#         1 / "1" -> "pinjaman"
#         2 / "2" -> "deposito"
#         3 / "3" -> "transaksi"
#
#     Perubahan dilakukan pada tabel transaksi dan notifikasi
#     dalam satu database transaction.
#     """
#
#     koneksi = buat_koneksi()
#
#     try:
#         # ====================================================
#         # 1. MEMERIKSA NILAI YANG TIDAK DIKENALI
#         # ====================================================
#         #
#         # Migrasi dihentikan jika ditemukan nilai selain:
#         # - nilai lama: 1, 2, 3
#         # - nilai baru: pinjaman, deposito, transaksi
#         # - NULL
#         #
#         # Dengan begitu data asing tidak diam-diam dibiarkan.
#         # ====================================================
#
#         tabel_yang_diperiksa = (
#             "transaksi",
#             "notifikasi"
#         )
#
#         for nama_tabel in tabel_yang_diperiksa:
#             nilai_tidak_valid = koneksi.execute(
#                 f"""
#                 SELECT DISTINCT
#                     CAST(jenis_referensi AS TEXT) AS nilai
#                 FROM {nama_tabel}
#                 WHERE jenis_referensi IS NOT NULL
#                   AND CAST(jenis_referensi AS TEXT) NOT IN (
#                       '1',
#                       '2',
#                       '3',
#                       ?,
#                       ?,
#                       ?
#                   )
#                 """,
#                 (
#                     JenisReferensi.PINJAMAN.value,
#                     JenisReferensi.DEPOSITO.value,
#                     JenisReferensi.TRANSAKSI.value
#                 )
#             ).fetchall()
#
#             if nilai_tidak_valid:
#                 raise ValueError(
#                     f"Ditemukan jenis_referensi tidak valid "
#                     f"pada tabel {nama_tabel}: "
#                     f"{[data['nilai'] for data in nilai_tidak_valid]}"
#                 )
#
#         # ====================================================
#         # 2. MENGUBAH DATA TRANSAKSI
#         # ====================================================
#
#         cursor_transaksi = koneksi.execute(
#             """
#             UPDATE transaksi
#             SET jenis_referensi =
#                 CASE CAST(jenis_referensi AS TEXT)
#                     WHEN '1' THEN ?
#                     WHEN '2' THEN ?
#                     WHEN '3' THEN ?
#                 END
#             WHERE CAST(jenis_referensi AS TEXT)
#                   IN ('1', '2', '3')
#             """,
#             (
#                 JenisReferensi.PINJAMAN.value,
#                 JenisReferensi.DEPOSITO.value,
#                 JenisReferensi.TRANSAKSI.value
#             )
#         )
#
#         jumlah_transaksi_diubah = cursor_transaksi.rowcount
#
#         # ====================================================
#         # 3. MENGUBAH DATA NOTIFIKASI
#         # ====================================================
#
#         cursor_notifikasi = koneksi.execute(
#             """
#             UPDATE notifikasi
#             SET jenis_referensi =
#                 CASE CAST(jenis_referensi AS TEXT)
#                     WHEN '1' THEN ?
#                     WHEN '2' THEN ?
#                     WHEN '3' THEN ?
#                 END
#             WHERE CAST(jenis_referensi AS TEXT)
#                   IN ('1', '2', '3')
#             """,
#             (
#                 JenisReferensi.PINJAMAN.value,
#                 JenisReferensi.DEPOSITO.value,
#                 JenisReferensi.TRANSAKSI.value
#             )
#         )
#
#         jumlah_notifikasi_diubah = cursor_notifikasi.rowcount
#
#         # ====================================================
#         # 4. MEMASTIKAN NILAI ANGKA SUDAH TIDAK TERSISA
#         # ====================================================
#
#         for nama_tabel in tabel_yang_diperiksa:
#             jumlah_numerik = koneksi.execute(
#                 f"""
#                 SELECT COUNT(*) AS jumlah
#                 FROM {nama_tabel}
#                 WHERE CAST(jenis_referensi AS TEXT)
#                       IN ('1', '2', '3')
#                 """
#             ).fetchone()["jumlah"]
#
#             if jumlah_numerik != 0:
#                 raise RuntimeError(
#                     f"Masih ada {jumlah_numerik} jenis_referensi "
#                     f"lama pada tabel {nama_tabel}"
#                 )
#
#         koneksi.commit()
#
#     except Exception:
#         koneksi.rollback()
#         raise
#
#     finally:
#         koneksi.close()
#
#     return {
#         "transaksi_diubah": jumlah_transaksi_diubah,
#         "notifikasi_diubah": jumlah_notifikasi_diubah
#     }
#
#
# # ============================================================
# # MENJALANKAN MIGRASI
# # ============================================================
#
# hasil = ubah_jenis_referensi_ke_string()
#
# print("✅ Migrasi jenis referensi berhasil")
# print(
#     "Data transaksi yang diubah :",
#     hasil["transaksi_diubah"]
# )
# print(
#     "Data notifikasi yang diubah:",
#     hasil["notifikasi_diubah"]
# )


from bank_djago.penyimpanan.sqlite.database import buat_koneksi


koneksi = buat_koneksi()

try:
    for nama_tabel in ("transaksi", "notifikasi"):
        print(f"\n=== {nama_tabel.upper()} ===")

        hasil = koneksi.execute(
            f"""
            SELECT
                jenis_referensi,
                typeof(jenis_referensi) AS tipe,
                COUNT(*) AS jumlah
            FROM {nama_tabel}
            GROUP BY jenis_referensi, typeof(jenis_referensi)
            ORDER BY jenis_referensi
            """
        ).fetchall()

        for data in hasil:
            print(dict(data))

finally:
    koneksi.close()