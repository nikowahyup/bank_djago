from bank_djago.penyimpanan.sqlite.database import buat_koneksi


def lihat_daftar_tabel():
    koneksi = buat_koneksi()

    try:
        cursor = koneksi.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)

        return cursor.fetchall()

    finally:
        koneksi.close()


def lihat_kolom_rekening():
    koneksi = buat_koneksi()

    try:
        cursor = koneksi.execute("""
            PRAGMA table_info(rekening)
        """)

        return cursor.fetchall()

    finally:
        koneksi.close()


def lihat_foreign_key_rekening():
    koneksi = buat_koneksi()

    try:
        cursor = koneksi.execute("""
            PRAGMA foreign_key_list(rekening)
        """)

        return cursor.fetchall()

    finally:
        koneksi.close()


def lihat_sql_rekening():
    koneksi = buat_koneksi()

    try:
        cursor = koneksi.execute("""
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
            AND name = ?
        """, ("rekening",))

        return cursor.fetchone()

    finally:
        koneksi.close()


# if __name__ == "__main__":
#     print("DAFTAR TABEL")
#
#     for tabel in lihat_daftar_tabel():
#         print("-", tabel["name"])
#
#     print("\nKOLOM TABEL REKENING")
#
#     for kolom in lihat_kolom_rekening():
#         print(dict(kolom))
#
#     print("\nFOREIGN KEY TABEL REKENING")
#
#     for foreign_key in lihat_foreign_key_rekening():
#         print(dict(foreign_key))
#
#     print("\nSQL PEMBUAT TABEL REKENING")
#
#     hasil_sql = lihat_sql_rekening()
#
#     if hasil_sql is not None:
#         print(hasil_sql["sql"])



