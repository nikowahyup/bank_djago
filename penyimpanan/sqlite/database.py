import sqlite3
from contextlib import closing
from contextlib import contextmanager
from pathlib import Path

lokasi_database = Path(__file__).parent / "bank_djago.db"


def buat_database():
    koneksi = sqlite3.connect(lokasi_database)
    koneksi.close()
    print("berhasil buat database")


def buat_koneksi():
    koneksi = sqlite3.connect(lokasi_database)
    koneksi.execute("PRAGMA foreign_keys = ON")
    koneksi.row_factory = sqlite3.Row
    return koneksi


def buat_koneksi_baca():
    return closing(buat_koneksi())


@contextmanager
def buat_koneksi_tulis():
    koneksi = buat_koneksi()
    try:
        yield koneksi
        koneksi.commit()
    except Exception:
        koneksi.rollback()
        raise
    finally:
        koneksi.close()
