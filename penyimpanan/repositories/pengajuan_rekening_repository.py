from fileinput import close

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
import datetime

class PengajuanRepository:

    @staticmethod
    def tambah_pengajuan( norek,jenis,alasan,waktu_pengajuan, koneksi):
        if isinstance(waktu_pengajuan, (datetime.date, datetime.datetime)):
            waktu_pengajuan = waktu_pengajuan.isoformat()

        cursor =koneksi.execute("""INSERT INTO pengajuan_rekening (norek, jenis, alasan, waktu_pengajuan)
                            VALUES (?,?,?,?)
        """,(norek,jenis,alasan,waktu_pengajuan))

        return cursor.lastrowid


    @staticmethod
    def cari_pengajuan_aktif(norek, jenis, koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""SELECT * 
                FROM pengajuan_rekening
                WHERE norek = ?
                AND jenis = ?
                AND status = 'diajukan'
                ORDER BY id DESC
                LIMIT 1""",(norek,jenis))

            return cursor.fetchone()
        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def cari_semua_pengajuan_diajukan():
        koneksi = buat_koneksi()
        try:
            cursor = koneksi.execute("""SELECT * 
            FROM pengajuan_rekening
            WHERE status = 'diajukan'
            ORDER BY id ASC""")

            return cursor.fetchall()

        finally:
            koneksi.close()


    @staticmethod
    def cari_pengajuan_dengan_id(id_pengajuan,koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
             cursor = koneksi.execute("""SELECT *
             FROM pengajuan_rekening
             WHERE id = ?""",(id_pengajuan,))

             return cursor.fetchone()
        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def perbarui_pengajuan(id_pengajuan, status_baru, waktu_proses, catatan, koneksi):

        if isinstance(waktu_proses, (datetime.date, datetime.datetime)):
            waktu_proses = waktu_proses.isoformat()


        cursor = koneksi.execute("""UPDATE pengajuan_rekening
            SET status = ?,
            waktu_diproses = ?,
            catatan_admin = ?
            WHERE id = ? 
            AND status = 'diajukan'
            """,(status_baru,waktu_proses,catatan,id_pengajuan))

        return cursor.rowcount


    @staticmethod
    def cari_penutupan_disetujui(norek,koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""SELECT *
            FROM pengajuan_rekening
            WHERE norek = ?
            AND jenis = 'tutup'
            AND status = 'disetujui'
            ORDER BY id DESC
            LIMIT 1""",(norek,))

            return cursor.fetchone()
        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def cari_penutupan_terbaru(norek, koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM pengajuan_rekening
                WHERE norek = ?
                  AND jenis = 'tutup'
                ORDER BY id DESC
                LIMIT 1
                """,
                (norek,)
            )

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()