from bank_djago.core.rekening import kelas_rekening
from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class PinjamanRepository:

    @staticmethod
    def tambah_pinjaman(pinjaman, koneksi):
        tanggal_pencairan = (
            pinjaman.tanggal_pencairan.isoformat()
            if pinjaman.tanggal_pencairan is not None
            else None
        )

        tanggal_jatuh_tempo = (
            pinjaman.tanggal_jatuh_tempo.isoformat()
            if pinjaman.tanggal_jatuh_tempo is not None
            else None
        )

        cursor = koneksi.execute(
            """
            INSERT INTO pinjaman (
                norek,
                nominal_pinjaman,
                bunga,
                tenor,
                cicilan_tetap,
                sisa_pokok,
                cicilan_terbayar,
                status,
                tanggal_pencairan,
                tanggal_jatuh_tempo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pinjaman.rekening.norek,
                pinjaman.nominal_pinjaman,
                pinjaman.bunga,
                pinjaman.tenor,
                pinjaman.cicilan_tetap,
                pinjaman.sisa_pokok,
                pinjaman.cicilan_terbayar,
                pinjaman.status.value,
                tanggal_pencairan,
                tanggal_jatuh_tempo
            )
        )

        return cursor.lastrowid

    @staticmethod
    def cari_semua_pinjaman_dengan_nik(nik, koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT pinjaman.*
                FROM pinjaman
                JOIN rekening
                    ON rekening.norek = pinjaman.norek
                WHERE rekening.nik_pemilik = ?
                ORDER BY pinjaman.id ASC
                """,
                (nik,)
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def cari_pengajuan_aktif_nasabah(nik, koneksi):



            cursor = koneksi.execute(
                """
                SELECT pinjaman.*
                FROM pinjaman
                JOIN rekening
                    ON rekening.norek = pinjaman.norek
                WHERE rekening.nik_pemilik = ?
                  AND pinjaman.status IN ('diajukan', 'disetujui')
                ORDER BY pinjaman.id DESC
                LIMIT 1
                """,
                (nik,)
            )

            return cursor.fetchone()



    @staticmethod
    def perbarui_status_pinjaman(
        id_pinjaman,
        status_baru,
        koneksi,
        catatan=None
    ):

        sql = """UPDATE pinjaman
            SET status = ?,
            catatan_admin = ?
            WHERE id = ?
            AND status = 'diajukan'"""

        cursor = koneksi.execute(
            sql,

            (
                status_baru,
                catatan,
                id_pinjaman
            )
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_setelah_pencairan(
            id_pinjaman,
            cicilan_tetap_baru,
            tanggal_jatuh_tempo_baru,
            tanggal_pencairan_baru,
            sisa_pokok_baru,
            status_baru,
            koneksi
            ):

        tanggal_pencairan = tanggal_pencairan_baru.isoformat()

        tanggal_jatuh_tempo = tanggal_jatuh_tempo_baru.isoformat()
        status_baru = status_baru.value

        sql ="""
            UPDATE pinjaman
            SET status = ?,
                cicilan_tetap = ?,
                tanggal_pencairan = ?,
                tanggal_jatuh_tempo = ?,
                sisa_pokok = ?
            WHERE id = ?
            AND status = 'disetujui'
            """

        cursor = koneksi.execute(
                sql,
            (
                status_baru,
                cicilan_tetap_baru,
                tanggal_pencairan,
                tanggal_jatuh_tempo,
                sisa_pokok_baru,
                id_pinjaman
            )
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_setelah_pembayaran(
            id_pinjaman,
            status_baru,
            cicilan_terbayar_baru,
            sisa_pokok_baru,
            tanggal_jatuh_tempo_lama,
            tanggal_jatuh_tempo_baru,
            koneksi
    ):
        tanggal_jatuh_tempo_baru = (
            tanggal_jatuh_tempo_baru.isoformat()
            if tanggal_jatuh_tempo_baru is not None
            else None
        )
        tanggal_jatuh_tempo_lama = (
            tanggal_jatuh_tempo_lama.isoformat()
            if tanggal_jatuh_tempo_lama is not None
            else None
        )

        status_baru = status_baru.value

        sql = """
            UPDATE pinjaman
            SET cicilan_terbayar = ?,
                sisa_pokok = ?,
                status = ?,
                tanggal_jatuh_tempo = ?
            WHERE id = ?
            AND status = 'aktif' AND tanggal_jatuh_tempo = ?
            """

        cursor = koneksi.execute(
                sql,
            (
                cicilan_terbayar_baru,
                sisa_pokok_baru,
                status_baru,
                tanggal_jatuh_tempo_baru,
                id_pinjaman,
                tanggal_jatuh_tempo_lama
            )
        )

        return cursor.rowcount


    @staticmethod
    def cari_pinjaman_dengan_id(id_pinjaman,koneksi=None):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""SELECT *
            FROM pinjaman
            WHERE id = ?
            """,(id_pinjaman,))

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def cari_pinjaman_aktif(norek, koneksi=None):
        kelola_koneksi = koneksi is None


        if kelola_koneksi:
            koneksi = buat_koneksi()


        try:
            cursor = koneksi.execute("""SELECT * 
            FROM pinjaman 
            WHERE norek = ?
            AND status In('diajukan','aktif')
            ORDER BY id DESC
            LIMIT 1""",(norek,))

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def cari_semua_pinjaman_aktif(koneksi):
        cursor = koneksi.execute(
            """
            SELECT
                pinjaman.*,
                rekening.nik_pemilik,
                rekening.status AS status_rekening,
                nasabah.nama AS nama_pemilik,
                nasabah.alamat AS alamat_pemilik
            FROM pinjaman
            JOIN rekening
                ON rekening.norek = pinjaman.norek
            JOIN nasabah
                ON nasabah.nik = rekening.nik_pemilik
            WHERE pinjaman.status = 'aktif'
            ORDER BY pinjaman.id
            """
        )

        return cursor.fetchall()



    @staticmethod
    def cari_semua_pinjaman_diajukan(koneksi=None):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT pinjaman.*,
                    rekening.nik_pemilik,
                    nasabah.nama AS nama_pemilik
                FROM pinjaman
                JOIN rekening 
                ON rekening.norek = pinjaman.norek 
                JOIN nasabah 
                ON rekening.nik_pemilik = nasabah.nik
                WHERE pinjaman.status = 'diajukan'
                ORDER BY pinjaman.id ASC
                """
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def cari_detail_pinjaman(
            id_pinjaman,
            koneksi=None
    ):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            detail_pinjaman = koneksi.execute(
                """
                SELECT pinjaman.*,
                rekening.nik_pemilik,
                nasabah.nama AS nama_pemilik,
                rekening.saldo AS saldo_rekening,
                rekening.status AS status_rekening,
                rekening.level AS level_rekening
                FROM pinjaman 
                JOIN rekening
                ON rekening.norek = pinjaman.norek
                JOIN nasabah
                ON rekening.nik_pemilik = nasabah.nik
                WHERE pinjaman.id = ?
                """,
                (id_pinjaman,)
            ).fetchone()

            if detail_pinjaman is None:
                return None


            ringkasan_pinjaman_aktif = koneksi.execute(
                """
                SELECT
                    COUNT(*) AS jumlah_pinjaman_aktif,
                    COALESCE(SUM(sisa_pokok) ,0) AS total_sisa_pokok,
                    COALESCE(SUM(cicilan_tetap), 0) AS total_cicilan_tetap
                FROM pinjaman
                WHERE norek = ?
                AND status = 'aktif'
            """
            ,(detail_pinjaman['norek'],)
            ).fetchone()

            return {
                "detail_pinjaman":detail_pinjaman,
                "pinjaman_aktif":ringkasan_pinjaman_aktif
                    }

        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def cari_semua_pinjaman_dengan_norek(
            norek,
            status,
            koneksi=None
    ):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:

            cursor = koneksi.execute(
                """
                SELECT *
                 FROM pinjaman
                WHERE norek = ?
                AND status = ?
                ORDER BY id ASC
                """,
                (
                    norek,
                    status.value
                )
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()


