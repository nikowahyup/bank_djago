

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class RekeningRepository:

    @staticmethod
    def tambah_rekening(rekening, koneksi):
        terakhir_ubah = (
            rekening.terakhir_ubah_rekening.isoformat()
            if rekening.terakhir_ubah_rekening is not None
            else None
        )

        waktu_dibuat = (
            rekening.waktu_dibuat.isoformat()
            if rekening.waktu_dibuat is not None
            else None
        )

        koneksi.execute(
            """
            INSERT INTO rekening (
                norek,
                nik_pemilik,
                pin,
                saldo,
                level,
                status,
                waktu_dibuat,
                limit_sisa,
                reset,
                dapat_bunga,
                waktu_bayar_admin,
                terakhir_ubah_rekening,
                alasan_blokir
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rekening.norek,
                rekening.pemilik.NIK,
                rekening.pin,
                rekening.saldo,
                rekening.level,
                rekening.status,
                waktu_dibuat,
                rekening.limit_sisa,
                rekening.reset.isoformat(),
                rekening.dapat_bunga.isoformat(),
                rekening.waktu_bayar_admin.isoformat(),
                terakhir_ubah,
                rekening.alasan_blokir
            )
        )

        return True

    @staticmethod
    def cari_rekening_dengan_norek(norek, koneksi):



        cursor = koneksi.execute("""
                SELECT *
                FROM rekening
                WHERE norek = ?
            """, (norek,))

        return cursor.fetchone()



    @staticmethod
    def cari_rekening_dengan_nik(nik, koneksi):

            sql ="""
                SELECT *
                FROM rekening
                WHERE nik_pemilik = ?
                ORDER BY norek
                """

            cursor = koneksi.execute(
                sql,

                (nik,)
            )

            return cursor.fetchall()



    @staticmethod
    def kurangi_saldo(norek, nominal, saldo_minimal, koneksi):

        sql = """UPDATE rekening 
        SET saldo = saldo - ?
        WHERE norek = ? AND (saldo - ?) >= ?"""

        cursor = koneksi.execute(
            sql,
            (
                nominal,
                norek,
                nominal,
                saldo_minimal
            )
        )

        return cursor.rowcount

    @staticmethod
    def tambah_saldo(norek ,nominal, koneksi):

        sql = """UPDATE rekening
        SET saldo = saldo + ?
        WHERE norek = ?"""

        cursor = koneksi.execute(sql,(nominal, norek))

        return cursor.rowcount


    @staticmethod
    def ambil_saldo(norek ,koneksi):

        sql = """SELECT saldo FROM rekening
        WHERE norek = ?"""

        cursor = koneksi.execute(sql,(norek,))

        hasil = cursor.fetchone()

        return hasil['saldo']

    @staticmethod
    def perbarui_limit(limit_baru,reset_baru, norek, koneksi):
        reset_baru = reset_baru.isoformat()
        cursor = koneksi.execute("""UPDATE rekening
        SET limit_sisa = ?,
        reset = ?
        WHERE norek = ?""",(limit_baru,reset_baru,norek))

        return cursor.rowcount

    @staticmethod
    def perbarui_level_rekening(rekening, koneksi):
        terakhir_ubah = (
            rekening.terakhir_ubah_rekening.isoformat()
            if rekening.terakhir_ubah_rekening is not None
            else None
        )

        cursor = koneksi.execute(
            """
            UPDATE rekening
            SET level = ?,
                limit_sisa = ?,
                terakhir_ubah_rekening = ?
            WHERE norek = ?
            """,
            (
                rekening.level,
                rekening.limit_sisa,
                terakhir_ubah,
                rekening.norek
            )
        )

        return cursor.rowcount



    @staticmethod
    def perbarui_saldo_dan_status(norek, saldo_baru, status_baru, koneksi):

            cursor = koneksi.execute("""UPDATE rekening
            SET saldo = ?,
            status = ?
            WHERE norek = ?
            """,(saldo_baru, status_baru, norek))

            return cursor.rowcount

    @staticmethod
    def perbarui_setelah_bayar_admin(
            norek,
            saldo_baru,
            waktu_bayar_admin_baru,
            koneksi
    ):

        waktu_bayar_admin_sqlite = (
            waktu_bayar_admin_baru.isoformat()
            )



        cursor = koneksi.execute("""UPDATE rekening
            SET saldo = ?,
            waktu_bayar_admin = ?
            WHERE norek = ?
            AND status != 'tutup'""",
            (
            saldo_baru,
            waktu_bayar_admin_sqlite,
            norek))

        return cursor.rowcount

    @staticmethod
    def cari_semua_rekening_berjalan(koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT
                    rekening.*,
                    nasabah.nama AS nama_pemilik,
                    nasabah.alamat AS alamat_pemilik
                FROM rekening
                JOIN nasabah
                    ON nasabah.nik = rekening.nik_pemilik
                WHERE rekening.status != 'tutup'
                ORDER BY rekening.norek
                """
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def perbarui_setelah_dapat_bunga(
            norek,
            waktu_dapat_bunga_baru,
            saldo_baru,
            koneksi
    ):

        dapat_bunga_sqlite = (
            waktu_dapat_bunga_baru.isoformat()
            )

        cursor = koneksi.execute("""UPDATE rekening
        SET saldo = ?,
        dapat_bunga = ?
        WHERE norek = ?
        AND status != 'tutup'
        """,(saldo_baru,
             dapat_bunga_sqlite,
             norek
             )
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_status_blokir(
            norek,
            status_baru,
            alasan_blokir,
            koneksi
    ):

        cursor = koneksi.execute(
            """
            UPDATE rekening 
                SET status = ?,
                alasan_blokir = ?
                WHERE norek = ?
                """,
            (
                status_baru,
                alasan_blokir,
                 norek)
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_pin(
            norek,
            pin_baru,
            koneksi
    ):

        cursor = koneksi.execute(
            """
            UPDATE rekening
            SET pin = ?
            WHERE norek = ?
            """,
            (
                pin_baru,
                norek
            )
        )

        return cursor.rowcount


    @staticmethod
    def ubah_state_setelah_upgrade_atau_downgrade(
            norek,
            limit_sisa_baru,
            level_baru,
            terakhir_ubah_rekening_lama,
            terakhir_ubah_rekening_baru,
            koneksi
    ):

        terakhir_ubah_rekening_baru = terakhir_ubah_rekening_baru.isoformat()
        terakhir_ubah_rekening_lama = (
            terakhir_ubah_rekening_lama.isoformat()
            if terakhir_ubah_rekening_lama is not None
            else None
        )

        sql = """UPDATE rekening
        SET limit_sisa = ?,
        level = ?,
        terakhir_ubah_rekening = ?
        WHERE norek = ? AND (terakhir_ubah_rekening = ? 
        OR (? IS NULL AND terakhir_ubah_rekening IS NULL)
        )
        """


        cursor = koneksi.execute(
            sql,
            (
                limit_sisa_baru,
                level_baru,
                terakhir_ubah_rekening_baru,
                norek,
                terakhir_ubah_rekening_lama,
                terakhir_ubah_rekening_lama
            )
        )

        return cursor.rowcount