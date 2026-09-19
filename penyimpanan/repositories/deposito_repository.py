
from bank_djago.penyimpanan.sqlite.database import buat_koneksi, buat_koneksi_tulis, buat_koneksi_baca


#method-method penghubung program ke database
class DepositoRepository:


    # untuk menyimpan data
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
    def cari_deposito_dengan_id(id_deposito, koneksi=None):
        kelola_koneksi = koneksi is None

        if kelola_koneksi:
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
            if kelola_koneksi:
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


    #untuk menu lihat deposito
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



    #untuk pengajuan penutupan rekening
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

    #untuk proses deposito(cairkan,jatuh tempo)
    @staticmethod
    def perbarui_status_deposito(
            id_deposito,
            status_baru,
            status_lama,
            koneksi
    ):
        sql = """UPDATE deposito
        SET status = ?
        WHERE id = ? AND status = ?"""

        cursor = koneksi.execute(
            sql,
            (
                status_baru,
                id_deposito,
                status_lama
            )
        )

        return cursor.rowcount


    # untuk scheduler
    @staticmethod
    def perbarui_setelah_aro(
            id_deposito,
            nominal_baru,
            bunga_baru,
            lama_bulan_baru,
            tanggal_buka_baru,
            jatuh_tempo_baru,
            status_baru,
            proses_aro,
            jatuh_tempo_lama,
            koneksi
    ):
        tanggal_buka_baru = tanggal_buka_baru.isoformat()
        jatuh_tempo_baru = jatuh_tempo_baru.isoformat()
        jatuh_tempo_lama = jatuh_tempo_lama.isoformat()
        proses_aro = proses_aro.isoformat() if proses_aro is not None else None

        sql = """UPDATE deposito
        SET nominal = ?,
            bunga = ?,
            lama_bulan = ?,
            tanggal_buka = ?,
            jatuh_tempo = ?,
            status = ?,
            proses_aro = ?
        WHERE id = ? AND jatuh_tempo = ?"""

        cursor = koneksi.execute(
            sql,
            (
                nominal_baru,
                bunga_baru,
                lama_bulan_baru,
                tanggal_buka_baru,
                jatuh_tempo_baru,
                status_baru,
                proses_aro,
                id_deposito,
                jatuh_tempo_lama
            )
        )

        return cursor.rowcount


    #untuk daftar deposito yang masih aktif dan diproses ARO
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


    #untuk menu cairkan deposito
    @staticmethod
    def cari_deposito_jatuh_tempo_dengan_norek(norek, koneksi=None):


        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()
        try:
            cursor = koneksi.execute(
                """
                SELECT *
                from deposito 
                WHERE norek = ?
                AND status = 'jatuh tempo'
                """,(
                    norek,
                )
            )

            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def cari_deposito_aro_aktif_dengan_norek(norek ,koneksi=None):

        kelola_koneksi = koneksi is None

        if kelola_koneksi:
            koneksi = buat_koneksi()

        try:
            cursor = koneksi.execute(
                """
                SELECT * 
                FROM deposito
                WHERE norek = ?
                AND  status = 'aktif'
                AND jenis_aro IN ('pokok','pokok_bunga')
            ORDER BY id""",
                (norek,)
            )


            return cursor.fetchall()

        finally:
            if kelola_koneksi:
                koneksi.close()


    @staticmethod
    def hentikan_aro(id_deposito, koneksi):



            sql = """UPDATE deposito
            SET jenis_aro = 'tidak'
            WHERE id = ? 
            AND status = 'aktif' 
            AND jenis_aro IN ('pokok', 'pokok_bunga')"""


            cursor = koneksi.execute(sql,(id_deposito,))


            return cursor.rowcount
