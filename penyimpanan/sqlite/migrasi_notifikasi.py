# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
#
#
# def migrasi_tabel_notifikasi():
#     koneksi = buat_koneksi()
#
#     try:
#         jumlah_notifikasi = koneksi.execute(
#             "SELECT COUNT(*) AS jumlah FROM notifikasi"
#         ).fetchone()["jumlah"]
#
#         if jumlah_notifikasi != 0:
#             raise ValueError(
#                 "Tabel notifikasi tidak kosong. "
#                 "Migrasi sederhana dibatalkan agar data tidak hilang."
#             )
#
#         koneksi.execute("DROP TABLE notifikasi")
#
#         koneksi.execute(
#             """
#             CREATE TABLE notifikasi (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 nik_pemilik TEXT NOT NULL,
#                 jenis TEXT NOT NULL,
#                 pesan TEXT NOT NULL,
#                 jenis_referensi TEXT,
#                 id_objek INTEGER,
#
#                 CHECK (
#                     jenis_referensi IS NULL
#                     OR jenis_referensi IN (
#                         'pinjaman',
#                         'deposito',
#                         'transaksi'
#                     )
#                 ),
#
#                 FOREIGN KEY (nik_pemilik)
#                 REFERENCES nasabah(nik)
#                 ON UPDATE CASCADE
#                 ON DELETE CASCADE
#             )
#             """
#         )
#
#         koneksi.commit()
#
#         print("✅ Migrasi tabel notifikasi berhasil")
#         print("Jumlah notifikasi dipertahankan: 0")
#
#     except Exception:
#         koneksi.rollback()
#         raise
#
#     finally:
#         koneksi.close()
#
#
# if __name__ == "__main__":
#     migrasi_tabel_notifikasi()



from bank_djago.penyimpanan.sqlite.database import buat_koneksi


koneksi = buat_koneksi()

try:
    sql_tabel = koneksi.execute(
        """
        SELECT sql
        FROM sqlite_master
        WHERE type = 'table'
          AND name = 'notifikasi'
        """
    ).fetchone()

    print(sql_tabel["sql"])

    kesalahan_fk = koneksi.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()

    assert not kesalahan_fk, (
        f"Ditemukan kesalahan foreign key: {kesalahan_fk}"
    )

    print("✅ Struktur notifikasi baru dan foreign key valid")

finally:
    koneksi.close()