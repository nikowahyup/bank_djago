# conftest.py
import datetime

import pytest
import sqlite3
import uuid
import bank_djago.penyimpanan.sqlite.database as db_module
from bank_djago.penyimpanan.sqlite.buat_database import inisialisasi_database
from bank_djago.utils.validator import Validator

PIN_UJI = "123456"
HASH_PIN_UJI = Validator.buat_hash(PIN_UJI, rounds=4)
PIN_PENERIMA = "654321"
HASH_PIN_PENERIMA = Validator.buat_hash(PIN_PENERIMA, rounds=4)


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
        ("Pengujian", "jln.ninjaku", "1000200030004000"),
    )

    koneksi_test.execute(
        """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin, limit_sisa, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            "0011002200330044",
            "1000200030004000",
            10_000_000,
            HASH_PIN_UJI,
            5_000_000,
            "2026-01-19",
            datetime.date.today().isoformat(),
            "2026-02-23",
            "2026-02-23",
        ),
    )
    koneksi_test.commit()

    return {"norek": "0011002200330044", "nik": "1000200030004000", "pin": PIN_UJI}


@pytest.fixture
def siapkan_data_rekening_penerima(koneksi_test):
    koneksi_test.execute(
        """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
        ("Pengujian", "jln.ninjaku", "7890098765433456"),
    )

    koneksi_test.execute(
        """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin,limit_sisa, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?,?)""",
        (
            "1111000099998888",
            "7890098765433456",
            10_000_000,
            HASH_PIN_PENERIMA,
            5_000_000,
            "2026-01-19",
            datetime.date.today().isoformat(),
            "2026-02-23",
            "2026-02-23",
        ),
    )
    koneksi_test.commit()

    return {"nik": "7890098765433456", "norek": "1111000099998888", "pin": PIN_PENERIMA}


@pytest.fixture
def siapkan_rekening_siap_diturunkan(koneksi_test):
    koneksi_test.execute(
        """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
        ("Pengujian", "jln.ninjaku", "1010202002020101"),
    )

    koneksi_test.execute(
        """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin,limit_sisa, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin,level)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (
            "1975197591759175",
            "1010202002020101",
            100_000_000,
            HASH_PIN_UJI,
            200_000_000,
            "2026-01-19",
            datetime.date.today().isoformat(),
            "2026-02-23",
            "2026-02-23",
            3,
        ),
    )
    koneksi_test.commit()

    return {"nik": "1010202002020101", "norek": "1975197591759175", "pin": PIN_UJI}
