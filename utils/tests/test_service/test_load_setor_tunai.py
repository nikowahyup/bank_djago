from bank_djago.penyimpanan.sqlite.database import (
    buat_koneksi,
    lokasi_database
)


NOREK = "4001701216150609"

koneksi = buat_koneksi()

try:
    # Mengambil saldo rekening pengujian.
    rekening = koneksi.execute(
        """
        SELECT
            norek,
            saldo,
            status,
            waktu_bayar_admin
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK,)
    ).fetchone()

    # Mengambil seluruh transaksi setor tunai terbaru,
    # tanpa membatasi nomor rekening.
    transaksi_setor = koneksi.execute(
        """
        SELECT
            id,
            jenis,
            norek_tujuan,
            nominal,
            saldo_tujuan_sebelum,
            saldo_tujuan_sesudah,
            waktu
        FROM transaksi
        WHERE jenis = 'setor_tunai'
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

finally:
    koneksi.close()


print("=== LOKASI DATABASE ===")
print(lokasi_database.resolve())
print()

print("=== DATA REKENING PENGUJIAN ===")
print(dict(rekening) if rekening else None)
print()

print("=== TRANSAKSI SETOR TUNAI TERBARU ===")

if not transaksi_setor:
    print("Tidak ditemukan transaksi setor tunai")
else:
    for transaksi in transaksi_setor:
        print(dict(transaksi))