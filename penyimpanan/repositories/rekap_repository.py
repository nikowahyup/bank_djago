from bank_djago.penyimpanan.sqlite.database import buat_koneksi


class RekapRepository:

    @staticmethod
    def rekap_umum():
        koneksi = buat_koneksi()

        try:
            hasil_nasabah = koneksi.execute(
            """SELECT COUNT (*) 
            AS total_nasabah 
            FROM nasabah
            """
            ).fetchone()

            total_nasabah = hasil_nasabah['total_nasabah']

            hasil_rekening = koneksi.execute(
            """SELECT COUNT (*)
             AS total_rekening,
             COALESCE(SUM(saldo), 0)
             AS total_saldo
            FROM rekening
            """
            ).fetchone()

            total_rekening = hasil_rekening['total_rekening']
            total_saldo = hasil_rekening['total_saldo']

            return total_nasabah,total_rekening,total_saldo

        finally:
            koneksi.close()

    @staticmethod
    def jumlah_tiap_jenis_rekening():
        koneksi = buat_koneksi()


        try:
            jumlah_rekening = koneksi.execute(
            """SELECT
                level,
                 COUNT (*) AS total_rekening 
                FROM rekening
                GROUP BY level 
                ORDER BY level
            """
            ).fetchall()

            reguler = 0
            prioritas = 0
            gold = 0
            platinum = 0

            for baris in jumlah_rekening:
                level = baris["level"]
                total_rekening = baris["total_rekening"]

                if level == 1:
                    reguler = total_rekening

                elif level == 2:
                    prioritas = total_rekening

                elif level == 3:
                    gold = total_rekening

                elif level == 4:
                    platinum = total_rekening

            return reguler, prioritas, gold, platinum

        finally:
            koneksi.close()

    @staticmethod
    def rekap_status_rekening():

        koneksi = buat_koneksi()

        try:
            status_rekening = koneksi.execute(
                """SELECT 
                    status,
                    COUNT (*) AS total_rekening 
                    FROM rekening
                    GROUP BY status
                    ORDER BY status
                """
            ).fetchall()


            aktif = 0
            blokir = 0
            tutup = 0

            for baris in status_rekening:
                status = baris['status']
                jumlah_rekening = baris['total_rekening']

                if status == "aktif":
                    aktif = jumlah_rekening

                elif status == "blokir":
                    blokir = jumlah_rekening

                elif status == "tutup":
                    tutup = jumlah_rekening

            return aktif,blokir,tutup

        finally:
            koneksi.close()

    @staticmethod
    def total_saldo_tiap_jenis_rekening():

        koneksi = buat_koneksi()

        try:
            jumlah_saldo = koneksi.execute(
                """SELECT
                    level, 
                    SUM(saldo) AS total_saldo 
                    FROM rekening
                    GROUP BY level 
                    ORDER BY level
                """
            ).fetchall()

            reguler = 0
            prioritas = 0
            gold = 0
            platinum = 0

            for baris in jumlah_saldo:
                level = baris['level']
                saldo = baris['total_saldo']

                if level == 1:
                    reguler = saldo

                elif level == 2:
                    prioritas = saldo

                elif level == 3:
                    gold = saldo

                elif level == 4:
                    platinum = saldo

            return reguler,prioritas,gold,platinum

        finally:
            koneksi.close()


    @staticmethod
    def cari_saldo_terbesar():

        koneksi = buat_koneksi()

        try:
            saldo_terbesar = koneksi.execute(
                """SELECT
                    nasabah.nama AS nama,
                    rekening.saldo AS saldo
                    FROM rekening
                    JOIN nasabah
                    ON rekening.nik_pemilik = nasabah.nik
                    ORDER BY rekening.saldo DESC
                    LIMIT 1
                """
            ).fetchone()


            return saldo_terbesar

        finally:
            koneksi.close()

    @staticmethod
    def cari_saldo_terkecil():

        koneksi = buat_koneksi()

        try:
            saldo_terkecil = koneksi.execute(
                """SELECT
                    nasabah.nama AS nama,
                    rekening.saldo AS saldo
                    FROM rekening
                    JOIN nasabah
                    ON rekening.nik_pemilik = nasabah.nik
                    ORDER BY rekening.saldo ASC
                    LIMIT 1
                """
            ).fetchone()

            return saldo_terkecil

        finally:
            koneksi.close()