import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class PinjamanRepository:

    @staticmethod
    def tambah_pinjaman(pinjaman):
        koneksi = buat_koneksi()

        try:
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

            id_pinjaman = cursor.lastrowid

            koneksi.commit()
            return id_pinjaman

        except sqlite3.IntegrityError as error:
            koneksi.rollback()
            print(f"Gagal menyimpan pinjaman: {error}")
            return None

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menyimpan pinjaman: {error}")
            return None

        finally:
            koneksi.close()

    @staticmethod
    def cari_pinjaman_dengan_id(id_pinjaman):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM pinjaman
                WHERE id = ?
                """,
                (id_pinjaman,)
            )

            return cursor.fetchone()

        finally:
            koneksi.close()

    @staticmethod
    def cari_pinjaman_berjalan(nik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT pinjaman.*
                FROM pinjaman
                JOIN rekening
                    ON rekening.norek = pinjaman.norek
                WHERE rekening.nik_pemilik = ?
                  AND pinjaman.status IN (
                      'diajukan',
                      'disetujui',
                      'aktif'
                  )
                ORDER BY pinjaman.id DESC
                LIMIT 1
                """,
                (nik,)
            )

            return cursor.fetchone()

        finally:
            koneksi.close()

    @staticmethod
    def cari_riwayat_semua_pinjaman(nik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT pinjaman.*
                FROM pinjaman
                JOIN rekening
                    ON pinjaman.norek = rekening.norek
                WHERE rekening.nik_pemilik = ?
                  AND pinjaman.status IN (
                      'ditolak',
                      'lunas'
                  )
                ORDER BY pinjaman.id DESC
                """,
                (nik,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()


    @staticmethod
    def cari_semua_pengajuan():
        koneksi = buat_koneksi()
        try:
            cursor = koneksi.execute("""SELECT *
            FROM pinjaman
            WHERE status = 'diajukan'
            ORDER BY id""")

            return cursor.fetchall()

        finally:
            koneksi.close()


    @staticmethod
    def cari_pinjaman_aktif(norek,koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""SELECT *
            FROM pinjaman
            WHERE norek = ?
            AND status IN ('diajukan','disetujui','aktif')
            ORDER BY id DESC
            LIMIT 1""",(norek,))

            return cursor.fetchone()
        finally:
            if kelola_koneksi:
                koneksi.close()