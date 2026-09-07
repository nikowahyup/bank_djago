"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_repo_transaksi.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

import datetime

from bank_djago.penyimpanan.repositories.transaksi_repository import (
    TransaksiRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NOREK_PENGUJIAN = "3001781978899033"
NOMINAL_PENGUJIAN = 10_000


koneksi = buat_koneksi()

try:
    data_rekening = koneksi.execute(
        """
        SELECT norek, saldo
        FROM rekening
        WHERE norek = ?
        """,
        (NOREK_PENGUJIAN,)
    ).fetchone()

    if data_rekening is None:
        raise ValueError(
            "Rekening pengujian tidak ditemukan"
        )

    jumlah_sebelum = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM transaksi
        """
    ).fetchone()["jumlah"]

    saldo_sebelum = data_rekening["saldo"]
    saldo_sesudah = saldo_sebelum + NOMINAL_PENGUJIAN
    waktu_pengujian = datetime.datetime.now()

    transaksi = {
        "jenis": JenisTransaksi.SETOR_TUNAI,
        "norek_tujuan": NOREK_PENGUJIAN,
        "nominal": NOMINAL_PENGUJIAN,
        "saldo_tujuan_sebelum": saldo_sebelum,
        "saldo_tujuan_sesudah": saldo_sesudah,
        "waktu": waktu_pengujian
    }

    id_transaksi = TransaksiRepository.tambah_transaksi(
        transaksi=transaksi,
        koneksi=koneksi
    )

    data_transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE id = ?
        """,
        (id_transaksi,)
    ).fetchone()

    if data_transaksi is None:
        raise ValueError(
            "Transaksi tidak berhasil ditambahkan"
        )

    print("HASIL PENGUJIAN TRANSAKSI REPOSITORY")
    print("ID                    :", data_transaksi["id"])
    print("Jenis                 :", data_transaksi["jenis"])
    print("Norek sumber          :", data_transaksi["norek_sumber"])
    print("Norek tujuan          :", data_transaksi["norek_tujuan"])
    print("Nominal               :", data_transaksi["nominal"])
    print("Biaya                 :", data_transaksi["biaya"])
    print(
        "Saldo tujuan sebelum :",
        data_transaksi["saldo_tujuan_sebelum"]
    )
    print(
        "Saldo tujuan sesudah :",
        data_transaksi["saldo_tujuan_sesudah"]
    )
    print("Waktu                 :", data_transaksi["waktu"])

    assert (
        data_transaksi["jenis"]
        == JenisTransaksi.SETOR_TUNAI.value
    )
    print("✅ Enum jenis transaksi tersimpan sebagai string")

    assert data_transaksi["norek_sumber"] is None
    assert data_transaksi["norek_tujuan"] == NOREK_PENGUJIAN
    print("✅ Rekening sumber dan tujuan tersimpan benar")

    assert data_transaksi["nominal"] == NOMINAL_PENGUJIAN
    assert data_transaksi["biaya"] == 0
    print("✅ Nominal dan biaya tersimpan benar")

    assert (
        data_transaksi["saldo_tujuan_sebelum"]
        == saldo_sebelum
    )
    assert (
        data_transaksi["saldo_tujuan_sesudah"]
        == saldo_sesudah
    )
    print("✅ Snapshot saldo tersimpan benar")

    assert data_transaksi["saldo_sumber_sebelum"] is None
    assert data_transaksi["saldo_sumber_sesudah"] is None
    assert data_transaksi["jenis_referensi"] is None
    assert data_transaksi["id_referensi"] is None
    print("✅ Kolom opsional tersimpan sebagai NULL")

    assert (
        datetime.datetime.fromisoformat(
            data_transaksi["waktu"]
        )
        == waktu_pengujian
    )
    print("✅ Waktu tersimpan dalam format datetime ISO")

    # Membatalkan insert pengujian.
    koneksi.rollback()

    jumlah_setelah_rollback = koneksi.execute(
        """
        SELECT COUNT(*) AS jumlah
        FROM transaksi
        """
    ).fetchone()["jumlah"]

    assert jumlah_setelah_rollback == jumlah_sebelum
    print("✅ Rollback menghapus transaksi pengujian")

    print(
        "\n✅ TransaksiRepository.tambah_transaksi() "
        "berhasil diuji"
    )

except Exception:
    koneksi.rollback()
    raise

finally:
    koneksi.close()
