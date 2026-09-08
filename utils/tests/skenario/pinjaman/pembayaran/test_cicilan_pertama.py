"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_pinjaman.txt` (urutan 11).

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
from bank_djago.utils.utility import StatusPinjaman, Utilitas


ID_PINJAMAN = 8
NIK_PENGUJIAN = "0000111122223333"
NOREK_PENGUJIAN = "3001781978899033"


# ============================================================
# 1. MEMUAT OBJEK NASABAH, REKENING, DAN PINJAMAN
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
# 2. MENGAMBIL KONDISI DATABASE SEBELUM PEMBAYARAN
# ============================================================

koneksi = buat_koneksi()

try:
    data_pinjaman_sebelum = dict(
        PinjamanRepository.cari_pinjaman_dengan_id(
            ID_PINJAMAN,
            koneksi
        )
    )

    data_rekening_sebelum = dict(
        RekeningRepository.cari_rekening_dengan_norek(
            NOREK_PENGUJIAN,
            koneksi
        )
    )

    jumlah_transaksi_sebelum = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM transaksi
        WHERE jenis = 'pembayaran_cicilan'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        """,
        (ID_PINJAMAN,)
    ).fetchone()["jumlah"]

finally:
    koneksi.close()


assert (
    data_pinjaman_sebelum["status"]
    == StatusPinjaman.AKTIF.value
), "Pinjaman ID 8 tidak berstatus aktif"

assert data_pinjaman_sebelum["cicilan_terbayar"] == 0, (
    "Pinjaman ID 8 ternyata sudah pernah membayar cicilan"
)


# Menggunakan tanggal pencairan sebagai tanggal pengujian.
# Berdasarkan aturan saat ini, cicilan pertama boleh dibayar
# mulai tanggal pencairan.
hari_pengujian = datetime.date.fromisoformat(
    data_pinjaman_sebelum["tanggal_pencairan"]
)

saldo_sebelum = data_rekening_sebelum["saldo"]
sisa_pokok_sebelum = data_pinjaman_sebelum["sisa_pokok"]
cicilan_tetap = data_pinjaman_sebelum["cicilan_tetap"]
bunga = data_pinjaman_sebelum["bunga"]

persentase_bunga = bunga / 12

bunga_bulanan = round(
    sisa_pokok_sebelum * persentase_bunga
)

pokok_dibayar = cicilan_tetap - bunga_bulanan

sisa_pokok_diharapkan = (
    sisa_pokok_sebelum - pokok_dibayar
)

# Karena pembayaran dilakukan pada tanggal pencairan,
# belum ada keterlambatan dan denda.
denda_diharapkan = 0
total_bayar_diharapkan = cicilan_tetap
saldo_diharapkan = saldo_sebelum - total_bayar_diharapkan

jatuh_tempo_lama = datetime.date.fromisoformat(
    data_pinjaman_sebelum["tanggal_jatuh_tempo"]
)

jatuh_tempo_diharapkan = Utilitas.tambah_bulan(
    jatuh_tempo_lama,
    1
)


print("=== KONDISI SEBELUM PEMBAYARAN ===")
print("ID pinjaman       :", ID_PINJAMAN)
print("Saldo rekening    :", saldo_sebelum)
print("Cicilan tetap     :", cicilan_tetap)
print("Bunga bulan ini   :", bunga_bulanan)
print("Pokok dibayar     :", pokok_dibayar)
print("Sisa pokok        :", sisa_pokok_sebelum)
print("Cicilan terbayar  :", 0)
print("Hari pembayaran   :", hari_pengujian)
print()


# ============================================================
# 3. MENJALANKAN PEMBAYARAN CICILAN
# ============================================================

pinjaman_hasil = PinjamanService.bayar_cicilan(
    id_pinjaman=ID_PINJAMAN,
    nasabah=nasabah,
    hari_ini=hari_pengujian
)


# ============================================================
# 4. MEMERIKSA STATE OBJEK PYTHON
# ============================================================

assert pinjaman_hasil is pinjaman, (
    "Service mengembalikan objek pinjaman yang berbeda"
)

assert pinjaman_hasil.status == StatusPinjaman.AKTIF, (
    "Pinjaman seharusnya masih aktif setelah cicilan pertama"
)

assert pinjaman_hasil.cicilan_terbayar == 1, (
    "Jumlah cicilan terbayar pada objek bukan satu"
)

assert pinjaman_hasil.sisa_pokok == sisa_pokok_diharapkan, (
    "Sisa pokok pada objek tidak sesuai"
)

assert (
    pinjaman_hasil.tanggal_jatuh_tempo
    == jatuh_tempo_diharapkan
), "Jatuh tempo pada objek tidak sesuai"

assert rekening.saldo == saldo_diharapkan, (
    "Saldo objek rekening tidak sesuai"
)

print("✅ State objek Python berhasil diperbarui")


# ============================================================
# 5. MEMBACA ULANG HASIL DARI SQLITE
# ============================================================

koneksi = buat_koneksi()

try:
    data_pinjaman_setelah = PinjamanRepository.cari_pinjaman_dengan_id(
        ID_PINJAMAN,
        koneksi
    )

    data_rekening_setelah = RekeningRepository.cari_rekening_dengan_norek(
        NOREK_PENGUJIAN,
        koneksi
    )

    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = 'pembayaran_cicilan'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (ID_PINJAMAN,)
    ).fetchone()

    if transaksi is None:
        raise AssertionError(
            "Transaksi pembayaran cicilan tidak ditemukan"
        )

    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (transaksi["id"],)
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (transaksi["id"],)
    ).fetchall()


    print()
    print("=== KONDISI SETELAH PEMBAYARAN ===")
    print("Status pinjaman   :", data_pinjaman_setelah["status"])
    print("Cicilan terbayar  :", data_pinjaman_setelah["cicilan_terbayar"])
    print("Sisa pokok        :", data_pinjaman_setelah["sisa_pokok"])
    print("Jatuh tempo baru  :", data_pinjaman_setelah["tanggal_jatuh_tempo"])
    print("Saldo rekening    :", data_rekening_setelah["saldo"])
    print()

    print("=== DATA TRANSAKSI ===")
    print("ID transaksi      :", transaksi["id"])
    print("Jenis             :", transaksi["jenis"])
    print("Rekening sumber   :", transaksi["norek_sumber"])
    print("Nominal cicilan   :", transaksi["nominal"])
    print("Denda             :", transaksi["biaya"])
    print("Saldo awal        :", transaksi["saldo_sumber_sebelum"])
    print("Saldo akhir       :", transaksi["saldo_sumber_sesudah"])
    print("Jenis referensi   :", transaksi["jenis_referensi"])
    print("ID referensi      :", transaksi["id_referensi"])
    print("Waktu             :", transaksi["waktu"])
    print()

    print("=== RIWAYAT TERHUBUNG ===")
    for riwayat in daftar_riwayat:
        print(
            f"ID {riwayat['id']} | "
            f"Transaksi {riwayat['transaksi_id']} | "
            f"{riwayat['jenis']} | "
            f"{riwayat['log']}"
        )

    print()
    print("=== AUDIT TERHUBUNG ===")
    for audit in daftar_audit:
        print(
            f"ID {audit['id']} | "
            f"Transaksi {audit['transaksi_id']} | "
            f"{audit['jenis']} | "
            f"{audit['log']}"
        )


    # ========================================================
    # 6. MEMASTIKAN HASIL DATABASE
    # ========================================================

    assert data_pinjaman_setelah["status"] == "aktif", (
        "Pinjaman tidak lagi berstatus aktif"
    )

    assert data_pinjaman_setelah["cicilan_terbayar"] == 1, (
        "Jumlah cicilan terbayar di database bukan satu"
    )

    assert (
        data_pinjaman_setelah["sisa_pokok"]
        == sisa_pokok_diharapkan
    ), "Sisa pokok di database tidak sesuai"

    assert (
        data_pinjaman_setelah["tanggal_jatuh_tempo"]
        == jatuh_tempo_diharapkan.isoformat()
    ), "Tanggal jatuh tempo baru tidak sesuai"

    assert data_rekening_setelah["saldo"] == saldo_diharapkan, (
        "Saldo rekening di database tidak sesuai"
    )

    assert transaksi["norek_sumber"] == NOREK_PENGUJIAN, (
        "Rekening sumber transaksi salah"
    )

    assert transaksi["nominal"] == cicilan_tetap, (
        "Nominal transaksi tidak sama dengan cicilan tetap"
    )

    assert transaksi["biaya"] == denda_diharapkan, (
        "Denda transaksi seharusnya nol"
    )

    assert transaksi["saldo_sumber_sebelum"] == saldo_sebelum, (
        "Snapshot saldo sebelum pembayaran salah"
    )

    assert transaksi["saldo_sumber_sesudah"] == saldo_diharapkan, (
        "Snapshot saldo setelah pembayaran salah"
    )

    assert transaksi["jenis_referensi"] == "pinjaman", (
        "Jenis referensi transaksi bukan pinjaman"
    )

    assert transaksi["id_referensi"] == ID_PINJAMAN, (
        "ID referensi transaksi tidak sesuai"
    )

    assert len(daftar_riwayat) == 1, (
        "Jumlah riwayat terhubung bukan satu"
    )

    assert len(daftar_audit) == 1, (
        "Jumlah audit terhubung bukan satu"
    )

    jumlah_transaksi_setelah = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM transaksi
        WHERE jenis = 'pembayaran_cicilan'
          AND jenis_referensi = 'pinjaman'
          AND id_referensi = ?
        """,
        (ID_PINJAMAN,)
    ).fetchone()["jumlah"]

    assert jumlah_transaksi_setelah == (
        jumlah_transaksi_sebelum + 1
    ), "Jumlah transaksi pembayaran tidak bertambah tepat satu"

finally:
    koneksi.close()


print()
print(
    "✅ PEMBAYARAN CICILAN PERTAMA BERHASIL: "
    "saldo, sisa pokok, jadwal, transaksi, riwayat, "
    "audit, dan objek Python tersimpan dengan benar"
)
