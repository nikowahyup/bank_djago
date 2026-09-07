"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.py` (urutan 12).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.loaders.nasabah_loader import (
    NasabahLoader
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.pinjaman.pinjaman_service import (
    PinjamanService
)


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"


def ambil_snapshot_database():
    """
    Mengambil kondisi penting dari database.

    Seluruh nilai ini akan dibandingkan sebelum dan setelah
    percobaan pembayaran yang seharusnya ditolak.
    """
    koneksi = buat_koneksi()

    try:
        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            ID_PINJAMAN,
            koneksi
        )

        data_rekening = RekeningRepository.cari_rekening_dengan_norek(
            NOREK_PENGUJIAN,
            koneksi
        )

        if data_pinjaman is None:
            raise AssertionError("Pinjaman ID 8 tidak ditemukan")

        if data_rekening is None:
            raise AssertionError("Rekening pengujian tidak ditemukan")

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            """
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            """
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            """
        ).fetchone()["jumlah"]

        jumlah_pembayaran_pinjaman = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis = 'pembayaran_cicilan'
              AND jenis_referensi = 'pinjaman'
              AND id_referensi = ?
            """,
            (ID_PINJAMAN,)
        ).fetchone()["jumlah"]

        return {
            "pinjaman": dict(data_pinjaman),
            "rekening": dict(data_rekening),
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "jumlah_pembayaran_pinjaman": (
                jumlah_pembayaran_pinjaman
            )
        }

    finally:
        koneksi.close()


# ============================================================
# 1. MEMUAT OBJEK NASABAH
# ============================================================

nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)

if nasabah is None:
    raise AssertionError("Nasabah pengujian tidak ditemukan")


rekening = next(
    (
        rekening
        for rekening in nasabah.rekening
        if rekening.norek == NOREK_PENGUJIAN
    ),
    None
)

if rekening is None:
    raise AssertionError("Objek rekening tidak ditemukan")


pinjaman = next(
    (
        pinjaman
        for pinjaman in nasabah.daftar_pinjaman
        if pinjaman.ID == ID_PINJAMAN
    ),
    None
)

if pinjaman is None:
    raise AssertionError("Objek pinjaman ID 8 tidak ditemukan")


# ============================================================
# 2. MENYIMPAN KONDISI AWAL
# ============================================================

snapshot_sebelum = ambil_snapshot_database()

data_pinjaman = snapshot_sebelum["pinjaman"]

assert data_pinjaman["status"] == "aktif", (
    "Pinjaman ID 8 tidak berstatus aktif"
)

assert data_pinjaman["cicilan_terbayar"] == 1, (
    "Pinjaman ID 8 bukan berada setelah cicilan pertama"
)


tanggal_pencairan = datetime.date.fromisoformat(
    data_pinjaman["tanggal_pencairan"]
)

tanggal_boleh_bayar = PinjamanService.tanggal_boleh_bayar(
    cicilan_terbayar=data_pinjaman["cicilan_terbayar"],
    tanggal_pencairan=tanggal_pencairan
)

# Mengambil satu hari sebelum tanggal yang diperbolehkan.
# Berdasarkan data saat ini, kemungkinan tanggal ini adalah
# tanggal jatuh tempo periode sebelumnya.
hari_pengujian = (
    tanggal_boleh_bayar - datetime.timedelta(days=1)
)


snapshot_objek_sebelum = {
    "status": pinjaman.status,
    "cicilan_terbayar": pinjaman.cicilan_terbayar,
    "sisa_pokok": pinjaman.sisa_pokok,
    "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
    "saldo": rekening.saldo,
    "jumlah_riwayat": len(rekening.riwayat)
}


print("=== PENGUJIAN PEMBAYARAN TERLALU AWAL ===")
print("ID pinjaman         :", ID_PINJAMAN)
print("Cicilan terbayar    :", data_pinjaman["cicilan_terbayar"])
print("Hari pengujian      :", hari_pengujian)
print("Baru boleh membayar :", tanggal_boleh_bayar)
print("Saldo sebelum       :", snapshot_sebelum["rekening"]["saldo"])
print()


# ============================================================
# 3. MENCOBA MEMBAYAR TERLALU AWAL
# ============================================================

try:
    PinjamanService.bayar_cicilan(
        id_pinjaman=ID_PINJAMAN,
        nasabah=nasabah,
        hari_ini=hari_pengujian
    )

except ValueError as error:
    # Memastikan kegagalan benar-benar berasal dari validasi tanggal,
    # bukan dari masalah lain seperti saldo atau objek yang hilang.
    assert str(error).startswith(
        "Cicilan selanjutnya baru boleh dibayar mulai"
    ), (
        "Pembayaran gagal karena alasan yang tidak diharapkan: "
        f"{error}"
    )

    print("✅ Pembayaran terlalu awal berhasil ditolak")
    print("Pesan error:", error)

else:
    raise AssertionError(
        "Pembayaran cicilan terlalu awal justru berhasil"
    )


# ============================================================
# 4. MEMERIKSA DATABASE SETELAH PENOLAKAN
# ============================================================

snapshot_setelah = ambil_snapshot_database()

snapshot_objek_setelah = {
    "status": pinjaman.status,
    "cicilan_terbayar": pinjaman.cicilan_terbayar,
    "sisa_pokok": pinjaman.sisa_pokok,
    "tanggal_jatuh_tempo": pinjaman.tanggal_jatuh_tempo,
    "saldo": rekening.saldo,
    "jumlah_riwayat": len(rekening.riwayat)
}


# Data pinjaman harus tetap sama persis.
assert (
    snapshot_setelah["pinjaman"]
    == snapshot_sebelum["pinjaman"]
), "Data pinjaman berubah setelah pembayaran ditolak"

# Saldo dan seluruh data rekening harus tetap sama.
assert (
    snapshot_setelah["rekening"]
    == snapshot_sebelum["rekening"]
), "Data rekening berubah setelah pembayaran ditolak"

assert (
    snapshot_setelah["jumlah_transaksi"]
    == snapshot_sebelum["jumlah_transaksi"]
), "Transaksi baru muncul setelah pembayaran ditolak"

assert (
    snapshot_setelah["jumlah_riwayat"]
    == snapshot_sebelum["jumlah_riwayat"]
), "Riwayat baru muncul setelah pembayaran ditolak"

assert (
    snapshot_setelah["jumlah_audit"]
    == snapshot_sebelum["jumlah_audit"]
), "Audit baru muncul setelah pembayaran ditolak"

assert (
    snapshot_setelah["jumlah_pembayaran_pinjaman"]
    == snapshot_sebelum["jumlah_pembayaran_pinjaman"]
), "Jumlah transaksi cicilan ID 8 berubah"

# Karena kegagalan terjadi sebelum commit, objek Python
# juga harus tetap berada pada kondisi awal.
assert snapshot_objek_setelah == snapshot_objek_sebelum, (
    "Objek Python berubah setelah pembayaran ditolak"
)


print()
print("=== KONDISI SETELAH PENOLAKAN ===")
print("Status pinjaman    :", snapshot_setelah["pinjaman"]["status"])
print(
    "Cicilan terbayar   :",
    snapshot_setelah["pinjaman"]["cicilan_terbayar"]
)
print(
    "Sisa pokok         :",
    snapshot_setelah["pinjaman"]["sisa_pokok"]
)
print(
    "Saldo rekening     :",
    snapshot_setelah["rekening"]["saldo"]
)
print(
    "Jumlah pembayaran  :",
    snapshot_setelah["jumlah_pembayaran_pinjaman"]
)

print()
print(
    "✅ VALIDASI WAKTU BERHASIL: pembayaran terlalu awal "
    "ditolak dan seluruh state tetap sama"
)
