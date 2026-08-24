import datetime
import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class AuditRepository:

    @staticmethod
    def tambah_audit(audit):
        koneksi = buat_koneksi()

        try:
            waktu = audit["waktu"]

            # Mengubah date atau datetime menjadi teks ISO.
            if isinstance(waktu, (datetime.date, datetime.datetime)):
                waktu = waktu.isoformat()

            cursor = koneksi.execute(
                """
                INSERT INTO audit (
                    kategori,
                    jenis,
                    waktu,
                    log,
                    nama,
                    nik,
                    norek
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit["kategori"],
                    audit["jenis"],
                    waktu,
                    audit["log"],
                    audit.get("nama"),
                    audit.get("nik"),
                    audit.get("norek")
                )
            )

            id_audit = cursor.lastrowid

            koneksi.commit()
            return id_audit

        except sqlite3.IntegrityError as error:
            koneksi.rollback()
            print(f"Gagal menyimpan audit: {error}")
            return None

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menyimpan audit: {error}")
            return None

        finally:
            koneksi.close()

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
    def cari_audit_dengan_jenis(jenis):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM audit
                WHERE jenis = ?
                ORDER BY id DESC
                """,
                (jenis,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()