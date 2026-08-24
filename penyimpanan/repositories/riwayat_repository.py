import datetime
import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class RiwayatRepository:

    @staticmethod
    def tambah_riwayat(norek, riwayat):
        koneksi = buat_koneksi()

        try:
            waktu = riwayat["waktu"]

            # Mengubah date atau datetime menjadi teks ISO.
            if isinstance(waktu, (datetime.date, datetime.datetime)):
                waktu = waktu.isoformat()

            cursor = koneksi.execute(
                """
                INSERT INTO riwayat (
                    norek,
                    kategori,
                    jenis,
                    waktu,
                    log
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    norek,
                    riwayat["kategori"],
                    riwayat["jenis"],
                    waktu,
                    riwayat["log"]
                )
            )

            id_riwayat = cursor.lastrowid

            koneksi.commit()
            return id_riwayat

        except sqlite3.IntegrityError as error:
            koneksi.rollback()
            print(f"Gagal menyimpan riwayat: {error}")
            return None

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menyimpan riwayat: {error}")
            return None

        finally:
            koneksi.close()

    @staticmethod
    def cari_seluruh_riwayat(norek):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM riwayat
                WHERE norek = ?
                ORDER BY id DESC
                """,
                (norek,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()

    @staticmethod
    def cari_riwayat_berdasarkan_jenis(norek, jenis):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM riwayat
                WHERE norek = ?
                  AND jenis = ?
                ORDER BY id DESC
                """,
                (
                    norek,
                    jenis
                )
            )

            return cursor.fetchall()

        finally:
            koneksi.close()