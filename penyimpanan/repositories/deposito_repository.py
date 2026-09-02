from bank_djago.penyimpanan.sqlite.database import buat_koneksi


#method-method penghubung program ke database
class DepositoRepository:

    @staticmethod
    def tambah_deposito(deposito, koneksi):

            proses_aro = (
                deposito.proses_aro.isoformat()
                if deposito.proses_aro is not None
                else None
            )

            cursor = koneksi.execute(
                """
                INSERT INTO deposito (
                    norek,
                    nominal,
                    bunga,
                    lama_bulan,
                    tanggal_buka,
                    jatuh_tempo,
                    status,
                    jenis_aro,
                    lama_aro,
                    proses_aro
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    deposito.rekening.norek,
                    deposito.nominal,
                    deposito.bunga,
                    deposito.lama_bulan,
                    deposito.tanggal_buka.isoformat(),
                    deposito.jatuh_tempo.isoformat(),
                    deposito.status,
                    deposito.jenis_aro,
                    deposito.lama_aro,
                    proses_aro
                )
            )

            return  cursor.lastrowid





    @staticmethod
    def cari_deposito_dengan_id(id_deposito):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM deposito
                WHERE id = ?
                """,
                (id_deposito,)
            )

            return cursor.fetchone()

        finally:
            koneksi.close()

    @staticmethod
    def cari_deposito_dengan_norek(norek):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT *
                FROM deposito
                WHERE norek = ?
                ORDER BY id
                """,
                (norek,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()

    @staticmethod
    def cari_deposito_dengan_nik(nik):
        koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT deposito.*
                FROM deposito
                JOIN rekening
                    ON deposito.norek = rekening.norek
                WHERE rekening.nik_pemilik = ?
                ORDER BY deposito.id
                """,
                (nik,)
            )

            return cursor.fetchall()

        finally:
            koneksi.close()

    @staticmethod
    def cari_deposito_aktif(norek, koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute("""SELECT *
            FROM deposito
            WHERE norek = ?
            AND status IN ('aktif','jatuh tempo')
             ORDER BY id DESC
             LIMIT 1""",(norek,))

            return cursor.fetchone()

        finally:
            if kelola_koneksi:
                koneksi.close()

    @staticmethod
    def perbarui_status_deposito(id_deposito, status_baru, koneksi):

        cursor = koneksi.execute("""UPDATE deposito
                                SET status = ?
                                WHERE id = ?
                                """,(status_baru, id_deposito))

        return cursor.rowcount



    @staticmethod
    def perbarui_setelah_aro( id_deposito,
                             nominal_baru,
                             bunga_baru,
                             lama_bulan_baru,
                             tanggal_buka_baru,
                             jatuh_tempo_baru,
                             status_baru,
                             proses_aro,
                              koneksi):

        tanggal_buka_baru = tanggal_buka_baru.isoformat()
        jatuh_tempo_baru = jatuh_tempo_baru.isoformat()

        proses_aro = (
            proses_aro.isoformat()
            if proses_aro is not None
            else None
        )

        cursor = koneksi.execute("""UPDATE deposito
        SET nominal = ?,
        bunga = ?,
        lama_bulan = ?,
        tanggal_buka = ?,
        jatuh_tempo = ?,
        status = ?,
        proses_aro = ?
        WHERE id = ?
        """,(nominal_baru,
             bunga_baru,
             lama_bulan_baru,
             tanggal_buka_baru,
             jatuh_tempo_baru,
             status_baru,
             proses_aro,
             id_deposito))

        return cursor.rowcount


    @staticmethod
    def cari_semua_deposito_aktif(koneksi=None):
        from bank_djago.services.deposito.deposito_service import StatusDeposito
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()
        try:
            cursor = koneksi.execute("""SELECT *
            FROM deposito
            WHERE status = ?
            ORDER BY id
            """,(StatusDeposito.AKTIF,))

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()