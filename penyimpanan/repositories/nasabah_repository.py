

from bank_djago.penyimpanan.sqlite.database import buat_koneksi



class NasabahRepository:

    @staticmethod
    def tambah_nasabah(nasabah, koneksi):
        koneksi.execute(
            """
            INSERT INTO nasabah (
                nik,
                nama,
                alamat
            )
            VALUES (?, ?, ?)
            """,
            (
                nasabah.NIK,
                nasabah.nama,
                nasabah.alamat
            )
        )



    @staticmethod
    def cari_nasabah_dengan_nik(nik,koneksi=None):

        transaksi_koneksi = koneksi is None

        if transaksi_koneksi:
            koneksi = buat_koneksi()


        try:
            cursor = koneksi.execute("""
                    SELECT nik, nama, alamat
                    FROM nasabah
                    WHERE nik = ?
                """, (nik,))



            return cursor.fetchone()

        finally:
            if transaksi_koneksi:
                koneksi.close()


