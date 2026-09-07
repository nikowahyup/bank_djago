"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 11).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import (
    JenisReferensi,
    JenisTransaksi
)


ID_DEPOSITO = 14


koneksi = buat_koneksi()

try:
    # Mengambil semua transaksi kapitalisasi untuk deposito 14.
    daftar_transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND jenis_referensi = ?
          AND id_referensi = ?
        ORDER BY id
        """,
        (
            JenisTransaksi.KAPITALISASI_BUNGA_DEPOSITO.value,
            JenisReferensi.DEPOSITO.value,
            ID_DEPOSITO
        )
    ).fetchall()

    # Harus hanya ada satu transaksi karena ARO ID 14
    # hanya dijalankan satu kali.
    assert len(daftar_transaksi) == 1, (
        f"Seharusnya hanya ada satu transaksi ARO, "
        f"tetapi ditemukan {len(daftar_transaksi)}"
    )

    transaksi = daftar_transaksi[0]
    id_transaksi = transaksi["id"]

    # Mengambil catatan yang terhubung ke transaksi ARO.
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id
        """,
        (id_transaksi,)
    ).fetchall()

    print("=== DATA TRANSAKSI ===")
    print("ID transaksi      :", transaksi["id"])
    print("Jenis             :", transaksi["jenis"])
    print("Rekening sumber   :", transaksi["norek_sumber"])
    print("Rekening tujuan   :", transaksi["norek_tujuan"])
    print("Nominal           :", transaksi["nominal"])
    print("Biaya             :", transaksi["biaya"])
    print(
        "Saldo sumber awal :",
        transaksi["saldo_sumber_sebelum"]
    )
    print(
        "Saldo sumber akhir:",
        transaksi["saldo_sumber_sesudah"]
    )
    print(
        "Saldo tujuan awal :",
        transaksi["saldo_tujuan_sebelum"]
    )
    print(
        "Saldo tujuan akhir:",
        transaksi["saldo_tujuan_sesudah"]
    )
    print(
        "Jenis referensi   :",
        transaksi["jenis_referensi"]
    )
    print("ID referensi      :", transaksi["id_referensi"])
    print("Waktu             :", transaksi["waktu"])
    print()

    # Kapitalisasi tidak memindahkan saldo antar-rekening.
    assert transaksi["norek_sumber"] is None
    assert transaksi["norek_tujuan"] is None
    assert transaksi["saldo_sumber_sebelum"] is None
    assert transaksi["saldo_sumber_sesudah"] is None
    assert transaksi["saldo_tujuan_sebelum"] is None
    assert transaksi["saldo_tujuan_sesudah"] is None
    print("✅ Seluruh kolom perpindahan saldo bernilai NULL")

    assert transaksi["biaya"] == 0, (
        "Kapitalisasi deposito seharusnya tidak memiliki biaya"
    )
    print("✅ Kapitalisasi tidak memiliki biaya")

    assert transaksi["nominal"] == 2_500, (
        "Nominal transaksi kapitalisasi bukan Rp2.500"
    )
    print("✅ Nominal kapitalisasi sesuai bunga periode pertama")

    assert transaksi["jenis_referensi"] == (
        JenisReferensi.DEPOSITO.value
    ), "Jenis referensi transaksi bukan deposito"
    print("✅ Jenis referensi tersimpan sebagai 'deposito'")

    assert transaksi["id_referensi"] == ID_DEPOSITO, (
        "ID referensi tidak menunjuk deposito ID 14"
    )
    print("✅ ID referensi menunjuk deposito ID 14")

    assert transaksi["waktu"] is not None, (
        "Waktu transaksi tidak tersimpan"
    )
    print("✅ Waktu transaksi berhasil disimpan")

    # Memeriksa dua riwayat yang dibuat oleh proses ARO.
    assert len(daftar_riwayat) == 2, (
        f"Seharusnya ada dua riwayat, "
        f"tetapi ditemukan {len(daftar_riwayat)}"
    )

    jenis_riwayat = {
        riwayat["jenis"]
        for riwayat in daftar_riwayat
    }

    assert "kapitalisasi bunga deposito" in jenis_riwayat
    assert "perpanjang deposito" in jenis_riwayat
    print("✅ Dua riwayat terhubung ke transaksi yang sama")

    # Memeriksa satu audit perpanjangan.
    assert len(daftar_audit) == 1, (
        f"Seharusnya ada satu audit, "
        f"tetapi ditemukan {len(daftar_audit)}"
    )

    assert daftar_audit[0]["jenis"] == "perpanjang deposito"
    print("✅ Audit perpanjangan terhubung ke transaksi yang sama")

    print("\n=== RIWAYAT TERHUBUNG ===")

    for riwayat in daftar_riwayat:
        print(
            f"ID {riwayat['id']} | "
            f"Transaksi {riwayat['transaksi_id']} | "
            f"{riwayat['jenis']} | "
            f"{riwayat['log']}"
        )

    print("\n=== AUDIT TERHUBUNG ===")

    for audit in daftar_audit:
        print(
            f"ID {audit['id']} | "
            f"Transaksi {audit['transaksi_id']} | "
            f"{audit['jenis']} | "
            f"{audit['log']}"
        )

finally:
    koneksi.close()


print()
print(
    "✅ ARO POKOK+BUNGA ID 14 TERSIMPAN DENGAN BENAR "
    "DAN TIDAK DIPROSES GANDA"
)
