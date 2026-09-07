"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_penutupan.py` (urutan 2).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


norek_sumber = "4001319935443781"
norek_penerima = "2001842427316253"

saldo_awal_sumber = 1_000_000
saldo_awal_penerima = 100_000_000
saldo_akhir_penerima = 101_000_000

koneksi = buat_koneksi()

try:
    # ==========================================================
    # 1. Periksaahkan kedua rekening
    # ==========================================================
    rekening_sumber = koneksi.execute(
        """
        SELECT *
        FROM rekening
        WHERE norek = ?
        """,
        (norek_sumber,)
    ).fetchone()

    rekening_penerima = koneksi.execute(
        """
        SELECT *
        FROM rekening
        WHERE norek = ?
        """,
        (norek_penerima,)
    ).fetchone()

    if rekening_sumber is None:
        raise ValueError("Rekening sumber tidak ditemukan")

    if rekening_penerima is None:
        raise ValueError("Rekening penerima tidak ditemukan")

    # ==========================================================
    # 2. Cari transaksi pemindahan saldo penutupan
    # ==========================================================
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE norek_sumber = ?
          AND norek_tujuan = ?
          AND jenis = 'pemindahan_saldo_penutupan'
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            norek_sumber,
            norek_penerima
        )
    ).fetchone()

    if transaksi is None:
        raise ValueError(
            "Transaksi pemindahan saldo penutupan "
            "tidak ditemukan"
        )

    id_transaksi = transaksi["id"]

    # ==========================================================
    # 3. Cari seluruh riwayat yang terhubung
    # ==========================================================
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id ASC
        """,
        (id_transaksi,)
    ).fetchall()

    # ==========================================================
    # 4. Cari seluruh audit yang terhubung
    # ==========================================================
    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id ASC
        """,
        (id_transaksi,)
    ).fetchall()

    # ==========================================================
    # Tampilkan hasil
    # ==========================================================
    print("=== REKENING SUMBER ===")
    print(f"Nomor rekening : {rekening_sumber['norek']}")
    print(f"Saldo          : {rekening_sumber['saldo']}")
    print(f"Status         : {rekening_sumber['status']}")

    print("\n=== REKENING PENERIMA ===")
    print(f"Nomor rekening : {rekening_penerima['norek']}")
    print(f"Saldo          : {rekening_penerima['saldo']}")
    print(f"Status         : {rekening_penerima['status']}")

    print("\n=== DATA TRANSAKSI ===")
    print(f"ID transaksi         : {transaksi['id']}")
    print(f"Jenis                : {transaksi['jenis']}")
    print(f"Rekening sumber      : {transaksi['norek_sumber']}")
    print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
    print(f"Nominal              : {transaksi['nominal']}")
    print(
        f"Saldo sumber sebelum : "
        f"{transaksi['saldo_sumber_sebelum']}"
    )
    print(
        f"Saldo sumber sesudah : "
        f"{transaksi['saldo_sumber_sesudah']}"
    )
    print(
        f"Saldo tujuan sebelum : "
        f"{transaksi['saldo_tujuan_sebelum']}"
    )
    print(
        f"Saldo tujuan sesudah : "
        f"{transaksi['saldo_tujuan_sesudah']}"
    )
    print(f"Waktu                : {transaksi['waktu']}")

    print("\n=== RIWAYAT TERHUBUNG ===")

    for riwayat in daftar_riwayat:
        print(
            f"ID {riwayat['id']} | "
            f"Rekening {riwayat['norek']} | "
            f"Transaksi {riwayat['transaksi_id']} | "
            f"{riwayat['jenis']} | "
            f"{riwayat['log']}"
        )

    print("\n=== AUDIT TERHUBUNG ===")

    for audit in daftar_audit:
        print(
            f"ID {audit['id']} | "
            f"Rekening {audit['norek']} | "
            f"Transaksi {audit['transaksi_id']} | "
            f"{audit['jenis']} | "
            f"{audit['log']}"
        )

    # ==========================================================
    # Assertions rekening
    # ==========================================================
    assert rekening_sumber["saldo"] == 0
    assert rekening_sumber["status"] == "tutup"

    assert rekening_penerima["saldo"] == saldo_akhir_penerima
    assert rekening_penerima["status"] == "aktif"

    # ==========================================================
    # Assertions transaksi
    # ==========================================================
    assert transaksi["jenis"] == (
        "pemindahan_saldo_penutupan"
    )

    assert transaksi["norek_sumber"] == norek_sumber
    assert transaksi["norek_tujuan"] == norek_penerima
    assert transaksi["nominal"] == saldo_awal_sumber

    assert transaksi["saldo_sumber_sebelum"] == (
        saldo_awal_sumber
    )
    assert transaksi["saldo_sumber_sesudah"] == 0

    assert transaksi["saldo_tujuan_sebelum"] == (
        saldo_awal_penerima
    )
    assert transaksi["saldo_tujuan_sesudah"] == (
        saldo_akhir_penerima
    )

    # ==========================================================
    # Assertions hubungan
    # ==========================================================
    assert len(daftar_riwayat) == 2
    assert len(daftar_audit) == 2

    norek_dalam_riwayat = {
        riwayat["norek"]
        for riwayat in daftar_riwayat
    }

    norek_dalam_audit = {
        audit["norek"]
        for audit in daftar_audit
    }

    assert norek_dalam_riwayat == {
        norek_sumber,
        norek_penerima
    }

    assert norek_dalam_audit == {
        norek_sumber,
        norek_penerima
    }

    assert all(
        riwayat["transaksi_id"] == id_transaksi
        for riwayat in daftar_riwayat
    )

    assert all(
        audit["transaksi_id"] == id_transaksi
        for audit in daftar_audit
    )

    print(
        "\n✅ Penutupan dengan metode transfer "
        "tersimpan dengan benar"
    )

finally:
    koneksi.close()
