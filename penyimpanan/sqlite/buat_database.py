from bank_djago.penyimpanan.sqlite.database import (
    buat_database,
    buat_koneksi
)
#
#
def buat_tabel_nasabah():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS nasabah (
                nik TEXT NOT NULL PRIMARY KEY,
                nama TEXT NOT NULL,
                alamat TEXT NOT NULL
            )
        """)

        koneksi.commit()
        print("Tabel nasabah berhasil dibuat")

    finally:
        koneksi.close()


def buat_tabel_rekening():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS rekening (
                norek TEXT NOT NULL PRIMARY KEY,
                nik_pemilik TEXT NOT NULL,
                pin TEXT NOT NULL,
                saldo INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'aktif',
                waktu_dibuat TEXT NOT NULL,
                limit_sisa INTEGER,
                reset TEXT NOT NULL,
                dapat_bunga TEXT NOT NULL,
                waktu_bayar_admin TEXT NOT NULL,
                terakhir_ubah_rekening TEXT,
                alasan_blokir TEXT,

                CHECK (saldo >= 0),
                CHECK (level IN (1, 2, 3, 4)),
                CHECK (status IN ('aktif', 'blokir', 'tutup')),
                CHECK (limit_sisa IS NULL OR limit_sisa >= 0),

                FOREIGN KEY (nik_pemilik)
                REFERENCES nasabah(nik)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
        """)

        koneksi.commit()
        print("Tabel rekening berhasil dibuat")

    finally:
        koneksi.close()


def buat_tabel_deposito():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS deposito (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norek TEXT NOT NULL,
                nominal INTEGER NOT NULL,
                bunga REAL NOT NULL,
                lama_bulan INTEGER NOT NULL,
                tanggal_buka TEXT NOT NULL,
                jatuh_tempo TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'aktif',
                jenis_aro TEXT NOT NULL DEFAULT 'tidak',
                lama_aro INTEGER,
                proses_aro TEXT,

                CHECK (nominal > 0),
                CHECK (bunga >= 0),
                CHECK (lama_bulan IN (1, 3, 6, 12)),
                CHECK (
                    status IN (
                        'aktif',
                        'jatuh tempo',
                        'dicairkan',
                        'selesai'
                    )
                ),
                CHECK (
                    jenis_aro IN (
                        'tidak',
                        'pokok',
                        'pokok_bunga'
                    )
                ),
                CHECK (
                    lama_aro IS NULL
                    OR lama_aro IN (1, 3, 6, 12)
                ),

                FOREIGN KEY (norek)
                REFERENCES rekening(norek)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
        """)

        koneksi.commit()
        print("Tabel deposito berhasil dibuat")

    finally:
        koneksi.close()


def buat_tabel_pinjaman():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS pinjaman (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norek TEXT NOT NULL,
                nominal_pinjaman INTEGER NOT NULL,
                bunga REAL NOT NULL,
                tenor INTEGER NOT NULL,
                cicilan_tetap INTEGER NOT NULL DEFAULT 0,
                sisa_pokok INTEGER NOT NULL,
                cicilan_terbayar INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'diajukan',
                catatan_admin TEXT,
                tanggal_pencairan TEXT,
                tanggal_jatuh_tempo TEXT,

                CHECK (nominal_pinjaman > 0),
                CHECK (bunga >= 0),
                CHECK (tenor IN (6, 12, 18, 24)),
                CHECK (cicilan_tetap >= 0),
                CHECK (sisa_pokok >= 0),
                CHECK (
                    cicilan_terbayar >= 0
                    AND cicilan_terbayar <= tenor
                ),
                CHECK (
                    status IN (
                        'diajukan',
                        'ditolak',
                        'disetujui',
                        'aktif',
                        'lunas'
                    )
                ),

                FOREIGN KEY (norek)
                REFERENCES rekening(norek)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
        """)

        koneksi.commit()
        print("Tabel pinjaman berhasil dibuat")

    finally:
        koneksi.close()


def buat_tabel_notifikasi():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS notifikasi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nik_pemilik TEXT NOT NULL,
                jenis TEXT NOT NULL,
                pesan TEXT NOT NULL,
                jenis_referensi INTEGER,
                id_objek INTEGER,

                CHECK (
                    jenis_referensi IS NULL
                    OR jenis_referensi IN (1, 2, 3)
                ),

                FOREIGN KEY (nik_pemilik)
                REFERENCES nasabah(nik)
                ON UPDATE CASCADE
                ON DELETE CASCADE
            )
        """)

        koneksi.commit()
        print("Tabel notifikasi berhasil dibuat")

    finally:
        koneksi.close()


def buat_tabel_riwayat():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS riwayat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norek TEXT NOT NULL,
                kategori TEXT NOT NULL,
                jenis TEXT NOT NULL,
                waktu TEXT NOT NULL,
                log TEXT NOT NULL,

                FOREIGN KEY (norek)
                REFERENCES rekening(norek)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
        """)

        koneksi.commit()
        print("Tabel riwayat berhasil dibuat")

    finally:
        koneksi.close()


def buat_tabel_audit():
    koneksi = buat_koneksi()

    try:
        koneksi.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kategori TEXT NOT NULL,
                jenis TEXT NOT NULL,
                waktu TEXT NOT NULL,
                log TEXT NOT NULL,
                nama TEXT,
                nik TEXT,
                norek TEXT
            )
        """)

        koneksi.commit()
        print("Tabel audit berhasil dibuat")

    finally:
        koneksi.close()

def buat_tabel_pengajuan_rekening():
    koneksi = buat_koneksi()

    try:
        koneksi.execute(
            """
            CREATE TABLE IF NOT EXISTS pengajuan_rekening (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                norek TEXT NOT NULL,
                jenis TEXT NOT NULL,
                alasan TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'diajukan',
                waktu_pengajuan TEXT NOT NULL,
                waktu_diproses TEXT,
                catatan_admin TEXT,

                CHECK (jenis IN (
                    'blokir',
                    'buka_blokir',
                    'tutup'
                )),

                CHECK (status IN (
                    'diajukan',
                    'disetujui',
                    'ditolak'
                )),

                FOREIGN KEY (norek)
                REFERENCES rekening(norek)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
            """
        )

        koneksi.commit()
        print("Tabel pengajuan rekening berhasil dibuat")

    finally:
        koneksi.close()

def buat_kolom_waktu_dibuat_rekening():
    koneksi = buat_koneksi()

    try:
        daftar_kolom = koneksi.execute(
            "PRAGMA table_info(rekening)"
        ).fetchall()

        nama_kolom = {
            kolom["name"]
            for kolom in daftar_kolom
        }

        if "waktu_dibuat" not in nama_kolom:
            koneksi.execute(
                """
                ALTER TABLE rekening
                ADD COLUMN waktu_dibuat TEXT
                """
            )

            koneksi.commit()
            print(
                "Kolom waktu_dibuat berhasil ditambahkan"
            )

        else:
            print(
                "Kolom waktu_dibuat sudah tersedia"
            )

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()


def tambah_kolom_catatan_admin_pinjaman():
    koneksi = buat_koneksi()

    try:
        daftar_kolom = koneksi.execute(
            "PRAGMA table_info(pinjaman)"
        ).fetchall()

        nama_kolom = {
            kolom["name"]
            for kolom in daftar_kolom
        }

        if "catatan_admin" not in nama_kolom:
            koneksi.execute(
                """
                ALTER TABLE pinjaman
                ADD COLUMN catatan_admin TEXT
                """
            )

            koneksi.commit()
            print("Kolom catatan_admin berhasil ditambahkan")

        else:
            print("Kolom catatan_admin sudah tersedia")

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()



def buat_tabel_transaksi():
    koneksi = buat_koneksi()

    try:
        koneksi.execute(
            """
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                jenis TEXT NOT NULL,

                norek_sumber TEXT,
                norek_tujuan TEXT,

                nominal INTEGER NOT NULL,
                biaya INTEGER NOT NULL DEFAULT 0,

                saldo_sumber_sebelum INTEGER,
                saldo_sumber_sesudah INTEGER,

                saldo_tujuan_sebelum INTEGER,
                saldo_tujuan_sesudah INTEGER,

                jenis_referensi TEXT,
                id_referensi INTEGER,

                waktu TEXT NOT NULL,

                CHECK (nominal > 0),
                CHECK (biaya >= 0),

                CHECK (
                    saldo_sumber_sebelum IS NULL
                    OR saldo_sumber_sebelum >= 0
                ),

                CHECK (
                    saldo_sumber_sesudah IS NULL
                    OR saldo_sumber_sesudah >= 0
                ),

                CHECK (
                    saldo_tujuan_sebelum IS NULL
                    OR saldo_tujuan_sebelum >= 0
                ),

                CHECK (
                    saldo_tujuan_sesudah IS NULL
                    OR saldo_tujuan_sesudah >= 0
                ),

                CHECK (
                    norek_sumber IS NOT NULL
                    OR norek_tujuan IS NOT NULL
                    OR id_referensi IS NOT NULL
                ),

                CHECK (
                    norek_sumber IS NULL
                    OR norek_tujuan IS NULL
                    OR norek_sumber != norek_tujuan
                ),

                FOREIGN KEY (norek_sumber)
                REFERENCES rekening(norek)
                ON UPDATE CASCADE
                ON DELETE RESTRICT,

                FOREIGN KEY (norek_tujuan)
                REFERENCES rekening(norek)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
            )
            """
        )

        koneksi.commit()
        print("Tabel transaksi berhasil dibuat")

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()



def tambah_kolom_transaksi_id_riwayat():
    koneksi = buat_koneksi()

    try:
        daftar_kolom = koneksi.execute(
            "PRAGMA table_info(riwayat)"
        ).fetchall()

        nama_kolom = {
            kolom["name"]
            for kolom in daftar_kolom
        }

        if "transaksi_id" not in nama_kolom:
            koneksi.execute(
                """
                ALTER TABLE riwayat
                ADD COLUMN transaksi_id INTEGER
                REFERENCES transaksi(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
                """
            )

            koneksi.commit()
            print(
                "Kolom transaksi_id pada riwayat "
                "berhasil ditambahkan"
            )
        else:
            print(
                "Kolom transaksi_id pada riwayat "
                "sudah tersedia"
            )

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()

def tambah_kolom_transaksi_id_audit():
    koneksi = buat_koneksi()

    try:
        daftar_kolom = koneksi.execute(
            "PRAGMA table_info(audit)"
        ).fetchall()

        nama_kolom = {
            kolom["name"]
            for kolom in daftar_kolom
        }

        if "transaksi_id" not in nama_kolom:
            koneksi.execute(
                """
                ALTER TABLE audit
                ADD COLUMN transaksi_id INTEGER
                REFERENCES transaksi(id)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
                """
            )

            koneksi.commit()
            print(
                "Kolom transaksi_id pada audit "
                "berhasil ditambahkan"
            )
        else:
            print(
                "Kolom transaksi_id pada audit "
                "sudah tersedia"
            )

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()


def inisialisasi_database():
    buat_database()
    buat_tabel_nasabah()
    buat_tabel_rekening()
    buat_tabel_deposito()
    buat_tabel_pinjaman()
    buat_tabel_notifikasi()
    buat_tabel_riwayat()
    buat_tabel_audit()
    buat_tabel_pengajuan_rekening()
    buat_tabel_transaksi()
    tambah_kolom_transaksi_id_audit()
    tambah_kolom_transaksi_id_riwayat()



if __name__ == "__main__":
    inisialisasi_database()



def lihat_daftar_tabel():
    koneksi = buat_koneksi()

    try:
        cursor = koneksi.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
        """)

        return cursor.fetchall()

    finally:
        koneksi.close()



for tabel in lihat_daftar_tabel():
    print(tabel["name"])