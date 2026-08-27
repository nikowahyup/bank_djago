import sqlite3

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


SQL_TAMBAH_REKENING = """
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
        waktu_bayar_admin
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def pastikan_ditolak(koneksi, nama_pengujian, data):
    try:
        koneksi.execute(SQL_TAMBAH_REKENING, data)

    except sqlite3.IntegrityError as error:
        print(f"✅ {nama_pengujian} ditolak")
        print(f"   Penyebab: {error}")

    else:
        raise AssertionError(
            f"{nama_pengujian} seharusnya ditolak SQLite"
        )


def uji_constraint_rekening():
    koneksi = buat_koneksi()

    try:
        # Seluruh data pengujian dimasukkan dalam satu transaksi.
        koneksi.execute("BEGIN")

        # Membuat nasabah valid sebagai pemilik rekening pengujian.
        koneksi.execute("""
            INSERT INTO nasabah (nik, nama, alamat)
            VALUES (?, ?, ?)
        """, (
            "NIK-TEST",
            "Nasabah Pengujian",
            "Alamat Pengujian"
        ))

        pastikan_ditolak(
            koneksi,
            "Foreign key tidak terdaftar",
            (
                "REK-INVALID-FK",
                "NIK-TIDAK-ADA",
                "123456",
                1_000_000,
                1,
                "aktif",
                5_000_000,
                "2026-08-23",
                "2026-08-23",
                "2026-08-23"
            )
        )

        pastikan_ditolak(
            koneksi,
            "Saldo negatif",
            (
                "REK-INVALID-SALDO",
                "NIK-TEST",
                "123456",
                -1,
                1,
                "aktif",
                5_000_000,
                "2026-08-23",
                "2026-08-23",
                "2026-08-23"
            )
        )

        pastikan_ditolak(
            koneksi,
            "Level tidak valid",
            (
                "REK-INVALID-LEVEL",
                "NIK-TEST",
                "123456",
                1_000_000,
                9,
                "aktif",
                5_000_000,
                "2026-08-23",
                "2026-08-23",
                "2026-08-23"
            )
        )

        pastikan_ditolak(
            koneksi,
            "Status tidak valid",
            (
                "REK-INVALID-STATUS",
                "NIK-TEST",
                "123456",
                1_000_000,
                1,
                "menghilang",
                5_000_000,
                "2026-08-23",
                "2026-08-23",
                "2026-08-23"
            )
        )

        pastikan_ditolak(
            koneksi,
            "Limit tersisa negatif",
            (
                "REK-INVALID-LIMIT",
                "NIK-TEST",
                "123456",
                1_000_000,
                1,
                "aktif",
                -1,
                "2026-08-23",
                "2026-08-23",
                "2026-08-23"
            )
        )

        # Memastikan rekening dengan seluruh data valid dapat disimpan.
        koneksi.execute(
            SQL_TAMBAH_REKENING,
            (
                "REK-VALID",
                "NIK-TEST",
                "123456",
                1_000_000,
                1,
                "aktif",
                5_000_000,
                "2026-08-23",
                "2026-08-23",
                "2026-08-23"
            )
        )

        rekening = koneksi.execute("""
            SELECT *
            FROM rekening
            WHERE norek = ?
        """, ("REK-VALID",)).fetchone()

        assert rekening is not None, (
            "Rekening valid seharusnya berhasil disimpan"
        )

        assert rekening["saldo"] == 1_000_000
        assert rekening["level"] == 1
        assert rekening["status"] == "aktif"

        print("✅ Data rekening yang valid berhasil diterima")
        print("✅ Seluruh constraint rekening bekerja")

    finally:
        # Seluruh data pengujian dibatalkan agar database tetap bersih.
        koneksi.rollback()
        koneksi.close()


if __name__ == "__main__":
    uji_constraint_rekening()