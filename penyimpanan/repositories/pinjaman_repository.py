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
    def cari_semua_pinjaman_diajukan(koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM pinjaman
                WHERE status = 'diajukan'
                ORDER BY id ASC
                """
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def cari_pengajuan_aktif_nasabah(nik, koneksi=None):
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
                  AND pinjaman.status IN ('diajukan', 'disetujui')
                ORDER BY pinjaman.id DESC
                LIMIT 1
                """,
                (nik,)
            )

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def perbarui_status_pinjaman(
        id_pinjaman,
        status_baru,
        koneksi=None,
        catatan=None
    ):

        cursor = koneksi.execute(
            """
            UPDATE pinjaman
            SET status = ?,
            catatan_admin = ?
            WHERE id = ?
            AND status = 'diajukan'
            """,
            (
                status_baru,
                catatan,
                id_pinjaman
            )
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_setelah_pencairan(pinjaman, koneksi):
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
            UPDATE pinjaman
            SET status = ?,
                cicilan_tetap = ?,
                tanggal_pencairan = ?,
                tanggal_jatuh_tempo = ?
            WHERE id = ?
            AND status = 'disetujui'
            """,
            (
                pinjaman.status.value,
                pinjaman.cicilan_tetap,
                tanggal_pencairan,
                tanggal_jatuh_tempo,
                pinjaman.ID
            )
        )

        return cursor.rowcount

    @staticmethod
    def perbarui_setelah_pembayaran(pinjaman, koneksi):
        tanggal_jatuh_tempo = (
            pinjaman.tanggal_jatuh_tempo.isoformat()
            if pinjaman.tanggal_jatuh_tempo is not None
            else None
        )

        cursor = koneksi.execute(
            """
            UPDATE pinjaman
            SET cicilan_terbayar = ?,
                sisa_pokok = ?,
                status = ?,
                tanggal_jatuh_tempo = ?
            WHERE id = ?
            AND status = 'aktif'
            """,
            (
                pinjaman.cicilan_terbayar,
                pinjaman.sisa_pokok,
                pinjaman.status.value,
                tanggal_jatuh_tempo,
                pinjaman.ID
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





