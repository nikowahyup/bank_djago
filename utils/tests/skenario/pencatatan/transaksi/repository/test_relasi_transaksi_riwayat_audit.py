"""Skenario manual yang dipulihkan dari `utils/tests/test_repo/test_repo_transaksi.py` (urutan 6).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisTransaksi


NOREK_PENGIRIM = "3001781978899033"
NOREK_PENERIMA = "2001569043650499"
NOMINAL = 999_999


koneksi = buat_koneksi()

try:
    transaksi_setor = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_tujuan = ?
          AND nominal = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.SETOR_TUNAI.value,
            NOREK_PENGIRIM,
            NOMINAL
        )
    ).fetchone()

    transaksi_tarik = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_sumber = ?
          AND nominal = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.TARIK_TUNAI.value,
            NOREK_PENGIRIM,
            NOMINAL
        )
    ).fetchone()

    transaksi_transfer = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE jenis = ?
          AND norek_sumber = ?
          AND norek_tujuan = ?
          AND nominal = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            JenisTransaksi.TRANSFER.value,
            NOREK_PENGIRIM,
            NOREK_PENERIMA,
            NOMINAL
        )
    ).fetchone()

    if None in (
        transaksi_setor,
        transaksi_tarik,
        transaksi_transfer
    ):
        raise ValueError(
            "Salah satu transaksi pengujian tidak ditemukan"
        )

    daftar_transaksi = {
        "SETOR": transaksi_setor,
        "TARIK": transaksi_tarik,
        "TRANSFER": transaksi_transfer
    }

    for nama, transaksi in daftar_transaksi.items():
        riwayat = koneksi.execute(
            """
            SELECT *
            FROM riwayat
            WHERE transaksi_id = ?
            ORDER BY id
            """,
            (transaksi["id"],)
        ).fetchall()

        audit = koneksi.execute(
            """
            SELECT *
            FROM audit
            WHERE transaksi_id = ?
            ORDER BY id
            """,
            (transaksi["id"],)
        ).fetchall()

        print(f"\n{nama}")
        print("ID transaksi :", transaksi["id"])
        print("Jenis        :", transaksi["jenis"])
        print("Jumlah riwayat:", len(riwayat))
        print("Jumlah audit :", len(audit))

        for data in riwayat:
            print(
                "Riwayat:",
                data["norek"],
                "|",
                data["log"]
            )

        for data in audit:
            print(
                "Audit:",
                data["norek"],
                "|",
                data["log"]
            )

        jumlah_yang_diharapkan = (
            2 if nama == "TRANSFER" else 1
        )

        assert len(riwayat) == jumlah_yang_diharapkan
        assert len(audit) == jumlah_yang_diharapkan

        assert all(
            data["transaksi_id"] == transaksi["id"]
            for data in riwayat
        )

        assert all(
            data["transaksi_id"] == transaksi["id"]
            for data in audit
        )

        print(
            f"✅ Seluruh audit dan riwayat {nama.lower()} "
            f"terhubung ke transaksi ID {transaksi['id']}"
        )

    # Setor: saldo tujuan bertambah.
    assert (
        transaksi_setor["saldo_tujuan_sesudah"]
        == transaksi_setor["saldo_tujuan_sebelum"]
        + NOMINAL
    )

    print("✅ Snapshot setor tunai benar")

    # Tarik: saldo sumber berkurang.
    assert (
        transaksi_tarik["saldo_sumber_sesudah"]
        == transaksi_tarik["saldo_sumber_sebelum"]
        - NOMINAL
    )

    print("✅ Snapshot tarik tunai benar")

    # Transfer: pengirim membayar nominal + biaya.
    assert (
        transaksi_transfer["saldo_sumber_sesudah"]
        == transaksi_transfer["saldo_sumber_sebelum"]
        - transaksi_transfer["nominal"]
        - transaksi_transfer["biaya"]
    )

    assert (
        transaksi_transfer["saldo_tujuan_sesudah"]
        == transaksi_transfer["saldo_tujuan_sebelum"]
        + transaksi_transfer["nominal"]
    )

    print("✅ Kedua snapshot saldo transfer benar")

    # Memastikan dua sisi transfer memiliki norek yang tepat.
    riwayat_transfer = koneksi.execute(
        """
        SELECT norek
        FROM riwayat
        WHERE transaksi_id = ?
        """,
        (transaksi_transfer["id"],)
    ).fetchall()

    audit_transfer = koneksi.execute(
        """
        SELECT norek
        FROM audit
        WHERE transaksi_id = ?
        """,
        (transaksi_transfer["id"],)
    ).fetchall()

    assert {
        data["norek"]
        for data in riwayat_transfer
    } == {
        NOREK_PENGIRIM,
        NOREK_PENERIMA
    }

    assert {
        data["norek"]
        for data in audit_transfer
    } == {
        NOREK_PENGIRIM,
        NOREK_PENERIMA
    }

    print("✅ Dua sisi transfer terhubung ke rekening yang tepat")

    # Urutan transaksi sesuai tindakan pengujian.
    assert (
        transaksi_setor["id"]
        < transaksi_tarik["id"]
        < transaksi_transfer["id"]
    )

    print("✅ Urutan transaksi setor, tarik, dan transfer benar")

finally:
    koneksi.close()


print(
    "\n✅ Setor, tarik, dan transfer memiliki hubungan "
    "transaksi–riwayat–audit yang konsisten"
)
