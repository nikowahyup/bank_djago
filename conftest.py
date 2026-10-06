# conftest.py
import datetime

import pytest
import sqlite3
import uuid
import bank_djago.penyimpanan.sqlite.database as db_module
from bank_djago.penyimpanan.sqlite.buat_database import inisialisasi_database


@pytest.fixture
def koneksi_test(monkeypatch):
    nama_db = f"file:testdb_{uuid.uuid4().hex}?mode=memory&cache=shared"

    def buat_koneksi_versi_test():
        koneksi = sqlite3.connect(nama_db, uri=True)
        koneksi.execute("PRAGMA foreign_keys = ON")
        koneksi.row_factory = sqlite3.Row
        return koneksi

    monkeypatch.setattr(db_module, "buat_koneksi", buat_koneksi_versi_test)

    koneksi_jangkar = buat_koneksi_versi_test()
    inisialisasi_database()

    yield koneksi_jangkar
    koneksi_jangkar.close()


@pytest.fixture
def siapkan_data_rekening_dan_nasabah(koneksi_test):

    koneksi_test.execute(
        """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
        ("Pengujian", "jln.ninjaku", "987654321"),
    )

    koneksi_test.execute(
        """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin, limit_sisa, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            "123456",
            "987654321",
            10_000_000,
            "1234",
            5_000_000,
            "2026-01-19",
            datetime.date.today().isoformat(),
            "2026-02-23",
            "2026-02-23",
        ),
    )
    koneksi_test.commit()

    return {"norek": "123456", "nik": "987654321"}


@pytest.fixture
def siapkan_data_rekening_penerima(koneksi_test):
    koneksi_test.execute(
        """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
        ("Pengujian", "jln.ninjaku", "123456789"),
    )

    koneksi_test.execute(
        """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin,limit_sisa, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            "000111222333",
            "123456789",
            10_000_000,
            "1234",
            5_000_000,
            "2026-01-19",
            datetime.date.today().isoformat(),
            "2026-02-23",
            "2026-02-23",
        ),
    )
    koneksi_test.commit()

    return {"nik": "123456789", "norek": "000111222333"}


@pytest.fixture
def siapkan_rekening_siap_diturunkan(koneksi_test):
    koneksi_test.execute(
        """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
        ("Pengujian", "jln.ninjaku", "123456789"),
    )

    koneksi_test.execute(
        """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin,limit_sisa, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin,level)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            "000111222333",
            "123456789",
            100_000_000,
            "1234",
            200_000_000,
            "2026-01-19",
            datetime.date.today().isoformat(),
            "2026-02-23",
            "2026-02-23",
            3,
        ),
    )
    koneksi_test.commit()

    return {"nik": "123456789", "norek": "000111222333"}
