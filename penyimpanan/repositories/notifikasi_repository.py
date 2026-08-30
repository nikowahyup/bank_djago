from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class NotifikasiRepository:

    @staticmethod
    def tambah_notifikasi(nik_pemilik, notifikasi, koneksi):
        jenis_referensi = (
            notifikasi.jenis_referensi.value
            if notifikasi.jenis_referensi is not None
            else None
        )

        cursor = koneksi.execute(
            """
            INSERT INTO notifikasi (
                nik_pemilik,
                jenis,
                pesan,
                jenis_referensi,
                id_objek
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                nik_pemilik,
                notifikasi.jenis,
                notifikasi.pesan,
                jenis_referensi,
                notifikasi.id_objek
            )
        )

        return cursor.lastrowid

    @staticmethod
    def cari_notifikasi_nasabah(nik_pemilik, koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT
                    id,
                    nik_pemilik,
                    jenis,
                    pesan,
                    jenis_referensi,
                    id_objek
                FROM notifikasi
                WHERE nik_pemilik = ?
                ORDER BY id DESC
                """,
                (nik_pemilik,)
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def cari_notifikasi_dengan_referensi(
        nik_pemilik,
        jenis_referensi,
        id_objek,
        koneksi=None
    ):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT
                    id,
                    nik_pemilik,
                    jenis,
                    pesan,
                    jenis_referensi,
                    id_objek
                FROM notifikasi
                WHERE nik_pemilik = ?
                  AND jenis_referensi = ?
                  AND id_objek = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    nik_pemilik,
                    jenis_referensi.value,
                    id_objek
                )
            )

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def hapus_notifikasi_dengan_referensi(
        nik_pemilik,
        jenis_referensi,
        id_objek,
        koneksi
    ):
        cursor = koneksi.execute(
            """
            DELETE FROM notifikasi
            WHERE nik_pemilik = ?
              AND jenis_referensi = ?
              AND id_objek = ?
            """,
            (
                nik_pemilik,
                jenis_referensi.value,
                id_objek
            )
        )

        return cursor.rowcount

    @staticmethod
    def hapus_semua_notifikasi_nasabah(
        nik_pemilik,
        koneksi
    ):
        cursor = koneksi.execute(
            """
            DELETE FROM notifikasi
            WHERE nik_pemilik = ?
            """,
            (nik_pemilik,)
        )

        return cursor.rowcount