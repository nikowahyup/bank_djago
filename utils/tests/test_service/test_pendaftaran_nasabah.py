from bank_djago.penyimpanan.sqlite.database import buat_koneksi


NIK_PENGUJIAN = "9999999999999999"


def cek_hasil_pendaftaran(nik):
    koneksi = buat_koneksi()

    try:
        nasabah = koneksi.execute(
            """
            SELECT nik, nama, alamat
            FROM nasabah
            WHERE nik = ?
            """,
            (nik,)
        ).fetchone()

        daftar_rekening = koneksi.execute(
            """
            SELECT
                norek,
                nik_pemilik,
                saldo,
                level,
                status
            FROM rekening
            WHERE nik_pemilik = ?
            ORDER BY norek
            """,
            (nik,)
        ).fetchall()

        assert nasabah is not None, (
            "Nasabah hasil pendaftaran tidak ditemukan"
        )

        assert daftar_rekening, (
            "Nasabah ditemukan, tetapi rekeningnya tidak ada"
        )

        print("DATA NASABAH")
        print("NIK    :", nasabah["nik"])
        print("Nama   :", nasabah["nama"])
        print("Alamat :", nasabah["alamat"])

        print("\nDAFTAR REKENING")

        for nomor, rekening in enumerate(
            daftar_rekening,
            start=1
        ):
            print(f"\nRekening ke-{nomor}")
            print("Nomor  :", rekening["norek"])
            print("Pemilik:", rekening["nik_pemilik"])
            print("Saldo  :", rekening["saldo"])
            print("Level  :", rekening["level"])
            print("Status :", rekening["status"])

            assert rekening["nik_pemilik"] == nasabah["nik"], (
                "Foreign key rekening tidak sesuai dengan NIK nasabah"
            )

        print("\n✅ Pendaftaran melalui UI tersimpan di SQLite")
        print("✅ Relasi nasabah dan rekening sesuai")

    finally:
        koneksi.close()


if __name__ == "__main__":
    cek_hasil_pendaftaran(NIK_PENGUJIAN)