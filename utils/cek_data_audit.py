from bank_djago.penyimpanan.sqlite.database import buat_koneksi


def cek_kombinasi_audit():

    koneksi = buat_koneksi()

    try:
        hasil = koneksi.execute(
            """
            SELECT
                kategori,
                jenis,
                COUNT(*) AS jumlah
            FROM audit
            GROUP BY kategori, jenis
            ORDER BY kategori, jenis
            """
        ).fetchall()

        print("=" * 70)
        print("DAFTAR KOMBINASI AUDIT YANG TERSIMPAN")
        print("=" * 70)

        for baris in hasil:
            kategori = baris["kategori"]
            jenis = baris["jenis"]
            jumlah = baris["jumlah"]

            print(
                f"Kategori : {kategori} | "
                f"Jenis : {jenis} | "
                f"Jumlah : {jumlah}"
            )

    finally:
        koneksi.close()


if __name__ == "__main__":
    cek_kombinasi_audit()