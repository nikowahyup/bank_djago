"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_load_untuk_biayaadmin.py` (urutan 3).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NOREK_PENGUJIAN = "4001701216150609"

BIAYA_ADMIN_YANG_DIHARAPKAN = 2_000
SALDO_SEBELUM_YANG_DIHARAPKAN = 512_000
SALDO_SESUDAH_YANG_DIHARAPKAN = 510_000


koneksi = buat_koneksi()

try:
    # Mengambil transaksi biaya admin terbaru milik
    # rekening yang sedang kita uji.
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_sumber = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.BIAYA_ADMIN.value,
            NOREK_PENGUJIAN
        )
    ).fetchone()

    if transaksi is None:
        raise AssertionError(
            "Transaksi biaya admin tidak ditemukan"
        )

    id_transaksi = transaksi["id"]

    # Mengambil seluruh riwayat yang terhubung
    # dengan transaksi biaya admin tersebut.
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    # Mengambil seluruh audit yang terhubung
    # dengan transaksi biaya admin yang sama.
    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

finally:
    koneksi.close()


print("=== DATA TRANSAKSI BIAYA ADMIN ===")
print("ID transaksi          :", transaksi["id"])
print("Jenis transaksi       :", transaksi["jenis"])
print("Rekening sumber       :", transaksi["norek_sumber"])
print("Rekening tujuan       :", transaksi["norek_tujuan"])
print("Nominal               :", transaksi["nominal"])
print(
    "Saldo sumber sebelum :",
    transaksi["saldo_sumber_sebelum"]
)
print(
    "Saldo sumber sesudah :",
    transaksi["saldo_sumber_sesudah"]
)
print("Jenis referensi       :", transaksi["jenis_referensi"])
print("ID referensi          :", transaksi["id_referensi"])
print("Waktu                 :", transaksi["waktu"])
print()


# Memastikan data utama transaksi sudah benar.
assert transaksi["jenis"] == JenisTransaksi.BIAYA_ADMIN.value, (
    "Jenis transaksi bukan biaya admin"
)

assert transaksi["norek_sumber"] == NOREK_PENGUJIAN, (
    "Nomor rekening sumber tidak sesuai"
)

assert transaksi["norek_tujuan"] is None, (
    "Transaksi biaya admin tidak boleh memiliki rekening tujuan"
)

assert transaksi["nominal"] == BIAYA_ADMIN_YANG_DIHARAPKAN, (
    "Nominal transaksi biaya admin tidak sesuai"
)

assert (
    transaksi["saldo_sumber_sebelum"]
    == SALDO_SEBELUM_YANG_DIHARAPKAN
), "Saldo sumber sebelum transaksi tidak sesuai"

assert (
    transaksi["saldo_sumber_sesudah"]
    == SALDO_SESUDAH_YANG_DIHARAPKAN
), "Saldo sumber sesudah transaksi tidak sesuai"

assert transaksi["jenis_referensi"] is None, (
    "Biaya admin tidak membutuhkan jenis referensi"
)

assert transaksi["id_referensi"] is None, (
    "Biaya admin tidak membutuhkan ID referensi"
)

assert transaksi["waktu"] is not None, (
    "Waktu transaksi tidak tersimpan"
)

print("✅ Data transaksi biaya admin tersimpan dengan benar")
print()


print("=== RIWAYAT TERHUBUNG ===")

assert len(daftar_riwayat) == 1, (
    f"Seharusnya ada tepat satu riwayat, "
    f"tetapi ditemukan {len(daftar_riwayat)}"
)

for riwayat in daftar_riwayat:
    print(
        f"ID {riwayat['id']} | "
        f"Transaksi {riwayat['transaksi_id']} | "
        f"Rekening {riwayat['norek']} | "
        f"{riwayat['jenis']} | "
        f"{riwayat['log']}"
    )

    assert riwayat["transaksi_id"] == id_transaksi, (
        "Riwayat terhubung dengan transaksi yang salah"
    )

    assert riwayat["norek"] == NOREK_PENGUJIAN, (
        "Riwayat tersimpan pada rekening yang salah"
    )

print("✅ Riwayat terhubung dengan transaksi biaya admin")
print()


print("=== AUDIT TERHUBUNG ===")

assert len(daftar_audit) == 1, (
    f"Seharusnya ada tepat satu audit, "
    f"tetapi ditemukan {len(daftar_audit)}"
)

for audit in daftar_audit:
    print(
        f"ID {audit['id']} | "
        f"Transaksi {audit['transaksi_id']} | "
        f"Rekening {audit['norek']} | "
        f"{audit['jenis']} | "
        f"{audit['log']}"
    )

    assert audit["transaksi_id"] == id_transaksi, (
        "Audit terhubung dengan transaksi yang salah"
    )

    assert audit["norek"] == NOREK_PENGUJIAN, (
        "Audit tersimpan pada rekening yang salah"
    )

print("✅ Audit terhubung dengan transaksi biaya admin")
print()


print(
    "✅ PENCATATAN BIAYA ADMIN BERHASIL: "
    "transaksi, riwayat, dan audit terhubung "
    "melalui transaksi_id yang sama"
)
