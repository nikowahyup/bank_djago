import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class RekeningRepository:

    @staticmethod
    def tambah_rekening(rekening):
        koneksi = buat_koneksi()

        try:
            terakhir_ubah = (
                rekening.terakhir_ubah_rekening.isoformat()
                if rekening.terakhir_ubah_rekening is not None
                else None
            )

            koneksi.execute("""
                INSERT INTO rekening (
                    norek,
                    nik_pemilik,
                    pin,
                    saldo,
                    level,
                    status,
                    limit_sisa,
                    reset,
                    dapat_bunga,
                    waktu_bayar_admin,
                    terakhir_ubah_rekening,
                    alasan_blokir
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rekening.norek,
                rekening.pemilik.NIK,
                rekening.pin,
                rekening.saldo,
                rekening.level,
                rekening.status,
                rekening.limit_sisa,
                rekening.reset.isoformat(),
                rekening.dapat_bunga.isoformat(),
                rekening.waktu_bayar_admin.isoformat(),
                terakhir_ubah,
                rekening.alasan_blokir
            ))

            koneksi.commit()
            return True

        except sqlite3.IntegrityError as error:
            koneksi.rollback()
            print(f"Gagal menyimpan rekening: {error}")
            return False

        except sqlite3.Error as error:
            koneksi.rollback()
            print(f"Terjadi kesalahan database: {error}")
            return False

        finally:
            koneksi.close()

    @staticmethod
    def cari_rekening_dengan_norek(norek):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""
                SELECT *
                FROM rekening
                WHERE norek = ?
            """, (norek,))

            return cursor.fetchone()

        finally:
            koneksi.close()