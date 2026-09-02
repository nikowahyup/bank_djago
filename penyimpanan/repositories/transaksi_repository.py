
import datetime

from bank_djago.utils.utility import JenisTransaksi


class TransaksiRepository:

    @staticmethod
    def tambah_transaksi(transaksi, koneksi):
        jenis = transaksi["jenis"]

        if not isinstance(jenis, JenisTransaksi):
            raise ValueError(
                "Jenis transaksi harus menggunakan JenisTransaksi"
            )

        waktu = transaksi["waktu"]

        if isinstance(
            waktu,
            (datetime.date, datetime.datetime)
        ):
            waktu = waktu.isoformat()

        jenis_referensi = transaksi.get("jenis_referensi")

        if jenis_referensi is not None:
            jenis_referensi = jenis_referensi.value

        cursor = koneksi.execute(
            """
            INSERT INTO transaksi (
                jenis,
                norek_sumber,
                norek_tujuan,
                nominal,
                biaya,
                saldo_sumber_sebelum,
                saldo_sumber_sesudah,
                saldo_tujuan_sebelum,
                saldo_tujuan_sesudah,
                jenis_referensi,
                id_referensi,
                waktu
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                jenis.value,
                transaksi.get("norek_sumber"),
                transaksi.get("norek_tujuan"),
                transaksi["nominal"],
                transaksi.get("biaya", 0),
                transaksi.get("saldo_sumber_sebelum"),
                transaksi.get("saldo_sumber_sesudah"),
                transaksi.get("saldo_tujuan_sebelum"),
                transaksi.get("saldo_tujuan_sesudah"),
                jenis_referensi,
                transaksi.get("id_referensi"),
                waktu
            )
        )

        return cursor.lastrowid