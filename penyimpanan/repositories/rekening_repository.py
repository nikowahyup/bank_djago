from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class RekeningRepository:

    # method simpan data rekening baru ke database
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
                rekening.alasan_blokir,
            ),
        )

        return True

    @staticmethod
    def cari_rekening_dengan_norek(norek, koneksi):

        cursor = koneksi.execute(
            """
                SELECT *
                FROM rekening
                WHERE norek = ?
            """,
            (norek,),
        )

        return cursor.fetchone()

    # method cari data rekening dengan nik
    @staticmethod
    def cari_rekening_dengan_nik(nik, koneksi):

        sql = """
                SELECT *
                FROM rekening
                WHERE nik_pemilik = ?
                ORDER BY norek
                """

        cursor = koneksi.execute(sql, (nik,))

        return cursor.fetchall()

    # method Update-Lock untuk pengurangan saldo
    @staticmethod
    def kurangi_saldo(norek, nominal, saldo_minimal, koneksi):

        sql = """UPDATE rekening 
        SET saldo = saldo - ?
        WHERE norek = ? AND (saldo - ?) >= ?"""

        cursor = koneksi.execute(sql, (nominal, norek, nominal, saldo_minimal))

        return cursor.rowcount

    # method Update-Lock untuk tambah saldo
    @staticmethod
    def tambah_saldo(norek, nominal, koneksi):

        sql = """UPDATE rekening
        SET saldo = saldo + ?
        WHERE norek = ? """

        cursor = koneksi.execute(
            sql,
            (
                nominal,
                norek,
            ),
        )

        return cursor.rowcount

    # method untuk melihat perubahan saldo setelah tambah/kurang
    @staticmethod
    def ambil_saldo(norek, koneksi):

        sql = """SELECT saldo FROM rekening
        WHERE norek = ?"""

        cursor = koneksi.execute(sql, (norek,))

        hasil = cursor.fetchone()

        return hasil["saldo"]

    # method untuk perbarui waktu limit
    @staticmethod
    def perbarui_limit(limit_baru, reset_baru, norek, koneksi):
        reset_baru = reset_baru.isoformat()
        cursor = koneksi.execute(
            """UPDATE rekening
        SET limit_sisa = ?,
        reset = ?
        WHERE norek = ?""",
            (limit_baru, reset_baru, norek),
        )

        return cursor.rowcount

    # method khusus penutupan rekening(mengubah saldo jadi 0 dan status jadi tutup)
    @staticmethod
    def perbarui_saldo_dan_status_untuk_penutupan(
        norek, saldo_baru, status_lama, status_baru, koneksi
    ):

        sql = """UPDATE rekening
            SET saldo = ?,
            status = ?
            WHERE norek = ?
            AND status = ?
            """
        cursor = koneksi.execute(sql, (saldo_baru, status_baru, norek, status_lama))

        return cursor.rowcount

    @staticmethod
    def perbarui_setelah_bayar_admin(
        norek, nominal, waktu_bayar_admin_lama, waktu_bayar_admin_baru, koneksi
    ):

        waktu_bayar_admin_lama = waktu_bayar_admin_lama.isoformat()
        waktu_bayar_admin_sqlite = waktu_bayar_admin_baru.isoformat()

        sql = """UPDATE rekening
            SET saldo = saldo - ?,
            waktu_bayar_admin = ?
            WHERE norek = ?
            AND status != 'tutup' AND waktu_bayar_admin = ?"""

        cursor = koneksi.execute(
            sql, (nominal, waktu_bayar_admin_sqlite, norek, waktu_bayar_admin_lama)
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_setelah_dapat_bunga(
        norek, waktu_dapat_bunga_lama, waktu_dapat_bunga_baru, nominal, koneksi
    ):

        dapat_bunga_lama = waktu_dapat_bunga_lama.isoformat()
        dapat_bunga_sqlite = waktu_dapat_bunga_baru.isoformat()

        sql = """UPDATE rekening
        SET saldo = saldo + ?,
        dapat_bunga = ?
        WHERE norek = ?
        AND status != 'tutup'
        AND dapat_bunga = ?
        """

        cursor = koneksi.execute(
            sql, (nominal, dapat_bunga_sqlite, norek, dapat_bunga_lama)
        )

        return cursor.rowcount

    # method untuk rekening loader
    @staticmethod
    def cari_semua_rekening_berjalan(koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""
                SELECT
                    rekening.*,
                    nasabah.nama AS nama_pemilik,
                    nasabah.alamat AS alamat_pemilik
                FROM rekening
                JOIN nasabah
                    ON nasabah.nik = rekening.nik_pemilik
                WHERE rekening.status != 'tutup'
                ORDER BY rekening.norek
                """)

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()

    # method untuk perbarui status rekening(blokir dan buka blokir)
    @staticmethod
    def perbarui_status_blokir(norek, status_lama, status_baru, alasan_blokir, koneksi):

        sql = """
            UPDATE rekening 
                SET status = ?,
                alasan_blokir = ?
                WHERE norek = ?
                AND status = ?
                """
        cursor = koneksi.execute(sql, (status_baru, alasan_blokir, norek, status_lama))

        return cursor.rowcount

    # method untuk perbarui pin
    @staticmethod
    def perbarui_pin(norek, pin_lama, pin_baru, koneksi):

        sql = """
            UPDATE rekening
            SET pin = ?
            WHERE norek = ?
            AND pin = ?
            """
        cursor = koneksi.execute(sql, (pin_baru, norek, pin_lama))

        return cursor.rowcount

    # method Update-Lock untuk perubahan hasil upgrade/downgrade rekening
    @staticmethod
    def ubah_state_setelah_upgrade_atau_downgrade(
        norek,
        limit_sisa_baru,
        level_baru,
        terakhir_ubah_rekening_lama,
        terakhir_ubah_rekening_baru,
        koneksi,
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
                terakhir_ubah_rekening_lama,
            ),
        )

        return cursor.rowcount
