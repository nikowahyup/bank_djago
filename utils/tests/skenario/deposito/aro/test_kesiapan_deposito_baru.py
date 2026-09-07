"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 9).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.repositories.deposito_repository import (
    DepositoRepository
)


ID_DEPOSITO = 14
NOREK_PENGUJIAN = "3001781978899033"


# Mengambil data mentah deposito langsung dari SQLite.
deposito = DepositoRepository.cari_deposito_dengan_id(
    ID_DEPOSITO
)

if deposito is None:
    raise AssertionError(
        f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
    )


# Menampilkan konfigurasi deposito sebelum pengujian ARO.
print("=== DATA DEPOSITO BARU ===")
print("ID deposito    :", deposito["id"])
print("Nomor rekening :", deposito["norek"])
print("Nominal        :", deposito["nominal"])
print("Tenor awal     :", deposito["lama_bulan"])
print("Jenis ARO      :", deposito["jenis_aro"])
print("Lama ARO       :", deposito["lama_aro"])
print("Tanggal buka   :", deposito["tanggal_buka"])
print("Jatuh tempo    :", deposito["jatuh_tempo"])
print("Proses ARO     :", deposito["proses_aro"])
print("Status         :", deposito["status"])
print()


# Memastikan deposito yang dibuat sesuai rencana pengujian.
assert deposito["id"] == ID_DEPOSITO, (
    "ID deposito tidak sesuai"
)

assert deposito["norek"] == NOREK_PENGUJIAN, (
    "Deposito terhubung dengan rekening yang salah"
)

assert deposito["nominal"] == 1_000_000, (
    "Nominal deposito bukan Rp1.000.000"
)

assert deposito["lama_bulan"] == 1, (
    "Tenor awal deposito bukan satu bulan"
)

assert deposito["jenis_aro"] == "pokok_bunga", (
    "Jenis ARO bukan pokok+bunga"
)

assert deposito["lama_aro"] == 1, (
    "Lama perpanjangan ARO bukan satu bulan"
)

assert deposito["proses_aro"] is None, (
    "Deposito ini ternyata sudah pernah diproses ARO"
)

assert deposito["status"] == "aktif", (
    "Status deposito bukan aktif"
)


print("✅ Deposito ID 14 siap diuji untuk ARO pokok+bunga")
