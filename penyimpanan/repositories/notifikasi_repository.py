import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class NotifikasiRepository:

    @staticmethod
    def tambah_notifikasi(nik_pemilik, notifikasi):
        koneksi = buat_koneksi()

        try:
            # Enum disimpan menggunakan nilai aslinya.
            jenis_referensi = (
                notifikasi.referensi_id.value
                if notifikasi.referensi_id is not None
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

            id_notifikasi = cursor.lastrowid

            koneksi.commit()
            return id_notifikasi

        except sqlite3.IntegrityError as error:
            koneksi.rollback()
            print(f"Gagal menyimpan notifikasi: {error}")
            return None

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menyimpan notifikasi: {error}")
            return None

        finally:
            koneksi.close()

    @staticmethod
    def cari_notifikasi_dengan_id(id_notifikasi):
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
                WHERE id = ?
                """,
                (id_notifikasi,)
            )

            return cursor.fetchone()

        finally:
            koneksi.close()

    @staticmethod
    def cari_notifikasi_nasabah(nik_pemilik):
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
            koneksi.close()

    @staticmethod
    def hapus_notifikasi_dengan_id(id_notifikasi, nik_pemilik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                DELETE FROM notifikasi
                WHERE id = ?
                  AND nik_pemilik = ?
                """,
                (
                    id_notifikasi,
                    nik_pemilik
                )
            )

            if cursor.rowcount == 0:
                koneksi.rollback()
                return False

            koneksi.commit()
            return True

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menghapus notifikasi: {error}")
            return False

        finally:
            koneksi.close()

    @staticmethod
    def hapus_notifikasi_dengan_referensi(
            nik_pemilik,
            jenis_referensi,
            id_objek
    ):
        koneksi = buat_koneksi()

        try:
            # Parameter dapat berupa Enum ataupun nilai biasa.
            nilai_referensi = (
                jenis_referensi.value
                if hasattr(jenis_referensi, "value")
                else jenis_referensi
            )

            cursor = koneksi.execute(
                """
                DELETE FROM notifikasi
                WHERE nik_pemilik = ?
                  AND jenis_referensi = ?
                  AND id_objek = ?
                """,
                (
                    nik_pemilik,
                    nilai_referensi,
                    id_objek
                )
            )

            if cursor.rowcount == 0:
                koneksi.rollback()
                return False

            koneksi.commit()
            return True

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menghapus notifikasi berdasarkan referensi: {error}")
            return False

        finally:
            koneksi.close()

    @staticmethod
    def hapus_semua_notifikasi_nasabah(nik_pemilik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                DELETE FROM notifikasi
                WHERE nik_pemilik = ?
                """,
                (nik_pemilik,)
            )

            koneksi.commit()
            return cursor.rowcount

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Gagal menghapus seluruh notifikasi nasabah: {error}")
            return 0

        finally:
            koneksi.close()