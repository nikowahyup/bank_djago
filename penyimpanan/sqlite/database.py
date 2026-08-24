import sqlite3

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





