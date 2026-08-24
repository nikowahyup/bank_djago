import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi



class NasabahRepository:



    @staticmethod
    def tambah_nasabah(nasabah):
        koneksi = buat_koneksi()
        try:
            koneksi.execute("""
            INSERT INTO nasabah
            (nik,nama,alamat)
            VALUES 
            (?,?,?)"""
            ,(nasabah.NIK, nasabah.nama, nasabah.alamat))

            koneksi.commit()
            return True
        except sqlite3.IntegrityError as e:
            koneksi.rollback()

            print(f"gagal menyimpan data nasabah : {e}")
            return False

        except sqlite3.Error as e:
            koneksi.rollback()

            print(f"gagal menyimpan data nasabah : {e}")
            return False

        finally:
            if koneksi is not None:
                koneksi.close()

    @staticmethod
    def cari_nasabah_dengan_nik(nik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""
                SELECT nik, nama, alamat
                FROM nasabah
                WHERE nik = ?
            """, (nik,))

            return cursor.fetchone()

        finally:
            koneksi.close()
