import datetime


class RiwayatRepository:

    @staticmethod
    def tambah_riwayat(norek, riwayat, koneksi, id_transaksi=None):

        waktu = riwayat["waktu"]

        if isinstance(waktu, (datetime.date, datetime.datetime)):
            waktu = waktu.isoformat()

        cursor = koneksi.execute(
            """
                INSERT INTO riwayat (
                    norek,
                    kategori,
                    jenis,
                    waktu,
                    log,
                    transaksi_id
                )
                VALUES (?, ?, ?, ?, ?,?)
                """,
            (
                norek,
                riwayat["kategori"],
                riwayat["jenis"],
                waktu,
                riwayat["log"],
                id_transaksi,
            ),
        )

        return cursor.lastrowid

    @staticmethod
    def cari_riwayat_dengan_kategori(norek, kategori, koneksi):

        sql = """SELECT * FROM riwayat
            WHERE norek = ? 
            AND kategori = ?
            ORDER BY id DESC"""

        cursor = koneksi.execute(sql, (norek, kategori))

        return cursor.fetchall()
