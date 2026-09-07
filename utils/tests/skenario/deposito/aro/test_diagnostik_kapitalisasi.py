"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 8).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


ID_DEPOSITO = 13

koneksi = buat_koneksi()

try:
    deposito = koneksi.execute(
        """
        SELECT
            id,
            nominal,
            bunga,
            lama_bulan,
            tanggal_buka,
            jatuh_tempo,
            proses_aro,
            status
        FROM deposito
        WHERE id = ?
        """,
        (ID_DEPOSITO,)
    ).fetchone()

    transaksi_aro = koneksi.execute(
        """
        SELECT
            id,
            jenis,
            nominal,
            jenis_referensi,
            id_referensi,
            waktu
        FROM transaksi
        WHERE jenis = ?
          AND jenis_referensi = ?
          AND id_referensi = ?
        ORDER BY id
        """,
        (
            "kapitalisasi_bunga_deposito",
            2,
            ID_DEPOSITO
        )
    ).fetchall()

    print("=== KONDISI DEPOSITO ===")
    print(dict(deposito) if deposito else "Deposito tidak ditemukan")

    print("\n=== TRANSAKSI KAPITALISASI ===")

    for transaksi in transaksi_aro:
        print(dict(transaksi))

    print("\nJumlah transaksi:", len(transaksi_aro))

finally:
    koneksi.close()


from bank_djago.penyimpanan.sqlite.database import buat_koneksi


ID_TRANSAKSI_AWAL = 19
ID_TRANSAKSI_AKHIR = 23

koneksi = buat_koneksi()

try:
    daftar_riwayat = koneksi.execute(
        """
        SELECT id, transaksi_id, norek, jenis, log
        FROM riwayat
        WHERE transaksi_id BETWEEN ? AND ?
        ORDER BY transaksi_id, id
        """,
        (
            ID_TRANSAKSI_AWAL,
            ID_TRANSAKSI_AKHIR
        )
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT id, transaksi_id, norek, jenis, log
        FROM audit
        WHERE transaksi_id BETWEEN ? AND ?
        ORDER BY transaksi_idpppppppooo, id
        """,
        (
            ID_TRANSAKSI_AWAL,
            ID_TRANSAKSI_AKHIR
        )
    ).fetchall()

    print("=== RIWAYAT YANG AKAN DIPULIHKAN ===")

    for riwayat in daftar_riwayat:
        print(dict(riwayat))

    print("\nJumlah riwayat:", len(daftar_riwayat))

    print("\n=== AUDIT YANG AKAN DIPULIHKAN ===")

    for audit in daftar_audit:
        print(dict(audit))

    print("\nJumlah audit:", len(daftar_audit))

finally:
    koneksi.close()
