from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis, buat_koneksi_baca




class SesiRepository:


    @staticmethod
    def tambah_token(token, nik, norek, kadaluwarsa, koneksi):
        kadaluwarsa = kadaluwarsa.isoformat()

        cursor = koneksi.execute("INSERT INTO sesi (token, nik, norek, kadaluwarsa) VALUES (?,?,?,?)",(token,nik, norek, kadaluwarsa))

        return cursor.rowcount

    @staticmethod
    def cari_token(token, koneksi):

        cursor = koneksi.execute("SELECT *  FROM sesi WHERE token = ?",(token,))

        return cursor.fetchone()


    @staticmethod
    def hapus_token(token, koneksi):

        cursor = koneksi.execute("DELETE FROM sesi WHERE token = ?",(token,))

        return cursor.rowcount