"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from datetime import datetime

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


NOREK_PENGUJIAN = "3001781978899033"


koneksi = buat_koneksi()

try:
    data_rekening = koneksi.execute(
        """
        SELECT
            norek,
            nik_pemilik,
            status,
            waktu_dibuat
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

finally:
    koneksi.close()


if data_rekening is None:
    raise ValueError("Rekening baru tidak ditemukan")


print("HASIL PENGUJIAN WAKTU PEMBUKAAN")
print("Norek        :", data_rekening["norek"])
print("NIK pemilik  :", data_rekening["nik_pemilik"])
print("Status       :", data_rekening["status"])
print("Waktu dibuat :", data_rekening["waktu_dibuat"])


assert data_rekening["waktu_dibuat"] is not None
print("✅ waktu_dibuat berhasil disimpan")


waktu_dibuat = datetime.fromisoformat(
    data_rekening["waktu_dibuat"]
)

assert isinstance(waktu_dibuat, datetime)
print("✅ waktu_dibuat tersimpan dalam format datetime ISO")


selisih = datetime.now() - waktu_dibuat

assert 0 <= selisih.total_seconds() < 300
print("✅ waktu_dibuat sesuai dengan waktu pengujian")


print("\n✅ Pembukaan rekening baru berhasil diuji")
