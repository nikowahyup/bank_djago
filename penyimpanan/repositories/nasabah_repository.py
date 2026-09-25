from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class NasabahRepository:

    # method simpan data nasabah ke database
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
            (nasabah.NIK, nasabah.nama, nasabah.alamat),
        )

    @staticmethod
    def cari_nasabah_dengan_nik(nik, koneksi=None):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:

            sql = """
                    SELECT nik, nama, alamat
                    FROM nasabah
                    WHERE nik = ?
                """

            cursor = koneksi.execute(sql, (nik,))

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()

    # method untuk ganti alamat nasabah
    @staticmethod
    def ganti_alamat(nik_pemilik, alamat_lama, alamat_baru, koneksi):

        cursor = koneksi.execute(
            """
            UPDATE nasabah
             SET alamat = ?
              WHERE nik = ?
              AND alamat = ?""",
            (alamat_baru, nik_pemilik, alamat_lama),
        )

        return cursor.rowcount
