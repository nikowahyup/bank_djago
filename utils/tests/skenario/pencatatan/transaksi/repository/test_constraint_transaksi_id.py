"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_repo_transaksi.py` (urutan 5).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


DAFTAR_TABEL = (
    "riwayat",
    "audit"
)


koneksi = buat_koneksi()

try:
    for nama_tabel in DAFTAR_TABEL:
        print(f"\nPEMERIKSAAN TABEL {nama_tabel.upper()}")

        daftar_kolom = koneksi.execute(
            f"PRAGMA table_info({nama_tabel})"
        ).fetchall()

        kolom_transaksi = next(
            (
                kolom
                for kolom in daftar_kolom
                if kolom["name"] == "transaksi_id"
            ),
            None
        )

        assert kolom_transaksi is not None, (
            f"Kolom transaksi_id tidak ditemukan "
            f"pada tabel {nama_tabel}"
        )

        print("✅ Kolom transaksi_id tersedia")
        print("Tipe data :", kolom_transaksi["type"])
        print("Not null  :", kolom_transaksi["notnull"])

        assert kolom_transaksi["type"] == "INTEGER"
        print("✅ Tipe transaksi_id adalah INTEGER")

        assert kolom_transaksi["notnull"] == 0
        print("✅ transaksi_id dapat menerima NULL")

        daftar_foreign_key = koneksi.execute(
            f"PRAGMA foreign_key_list({nama_tabel})"
        ).fetchall()

        foreign_key_transaksi = next(
            (
                foreign_key
                for foreign_key in daftar_foreign_key
                if (
                    foreign_key["from"] == "transaksi_id"
                    and foreign_key["table"] == "transaksi"
                    and foreign_key["to"] == "id"
                )
            ),
            None
        )

        assert foreign_key_transaksi is not None, (
            f"Foreign key transaksi_id pada "
            f"{nama_tabel} tidak ditemukan"
        )

        print("✅ Foreign key transaksi_id tersedia")
        print(
            "Relasi    :",
            f"{nama_tabel}.transaksi_id "
            f"→ transaksi.id"
        )
        print(
            "ON UPDATE :",
            foreign_key_transaksi["on_update"]
        )
        print(
            "ON DELETE :",
            foreign_key_transaksi["on_delete"]
        )

        assert (
            foreign_key_transaksi["on_update"]
            == "CASCADE"
        )

        assert (
            foreign_key_transaksi["on_delete"]
            == "RESTRICT"
        )

        print("✅ Aturan foreign key sesuai rancangan")

    status_foreign_key = koneksi.execute(
        "PRAGMA foreign_keys"
    ).fetchone()[0]

    print("\nSTATUS FOREIGN KEY:", status_foreign_key)

    assert status_foreign_key == 1
    print("✅ Pemeriksaan foreign key aktif")

finally:
    koneksi.close()


print(
    "\n✅ Kolom transaksi_id pada audit dan riwayat "
    "berhasil diverifikasi"
)
