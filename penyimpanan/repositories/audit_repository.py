import datetime


from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class AuditRepository:

    @staticmethod
    def tambah_audit(audit, koneksi, id_transaksi=None):

        waktu = audit["waktu"]

        if isinstance(waktu, (datetime.date, datetime.datetime)):
            waktu = waktu.isoformat()

        cursor = koneksi.execute(
            """
            INSERT INTO audit (
                kategori,
                objek,
                aksi,
                waktu,
                log,
                nama,
                nik,
                norek,
                transaksi_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit["kategori"],
                audit["objek"],
                audit["aksi"],
                waktu,
                audit["log"],
                audit.get("nama"),
                audit.get("nik"),
                audit.get("norek"),
                id_transaksi
            )
        )

        return cursor.lastrowid




    @staticmethod
    def cari_audit_dengan_nik(nik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM audit
                WHERE nik = ?
                ORDER BY id DESC
                """,
                (nik,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()

    @staticmethod
    def cari_audit_dengan_norek(norek):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM audit
                WHERE norek = ?
                ORDER BY id DESC
                """,
                (norek,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()

    @staticmethod
    def cari_audit(
            koneksi,
            kategori=None,
            objek=None,
            aksi=None
    ):
        query = """
            SELECT
                id,
                kategori,
                objek,
                aksi,
                waktu,
                log,
                nama,
                nik,
                norek,
                transaksi_id
            FROM audit
        """

        kondisi = []
        parameter = []

        if kategori is not None:
            kondisi.append("kategori = ?")
            parameter.append(kategori)

        if objek is not None:
            kondisi.append("objek = ?")
            parameter.append(objek)

        if aksi is not None:
            kondisi.append("aksi = ?")
            parameter.append(aksi)

        if kondisi:
            query += " WHERE "
            query += " AND ".join(kondisi)

        query += " ORDER BY waktu DESC, id DESC"

        cursor = koneksi.execute(
            query,
            parameter
        )

        hasil = cursor.fetchall()

        return hasil

