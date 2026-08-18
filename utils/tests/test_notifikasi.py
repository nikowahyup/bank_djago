def uji_isolasi_notifikasi(bank):
    nasabah = next(iter(bank.data_nasabah.values()))

    if not nasabah.deposito:
        raise ValueError(
            "Nasabah tidak memiliki deposito untuk pengujian"
        )

    deposito = nasabah.deposito[0]

    # Menyimpan list notifikasi asli agar dapat dikembalikan.
    notifikasi_asli = nasabah.notifikasi

    try:
        notifikasi_deposito_target = Notifikasi(
            jenis="deposito",
            pesan="Notifikasi deposito target",
            referensi_id=JenisReferensiID.DEPOSITO,
            id_objek=deposito.ID
        )

        notifikasi_deposito_lain = Notifikasi(
            jenis="deposito",
            pesan="Notifikasi deposito lain",
            referensi_id=JenisReferensiID.DEPOSITO,
            id_objek=deposito.ID + 999
        )

        notifikasi_pinjaman = Notifikasi(
            jenis="pinjaman",
            pesan="Notifikasi pinjaman",
            referensi_id=JenisReferensiID.PINJAMAN
        )

        notifikasi_umum = Notifikasi(
            jenis="rekening",
            pesan="Notifikasi umum rekening"
        )

        # Menggunakan daftar sementara agar data asli tidak berubah.
        nasabah.notifikasi = [
            notifikasi_deposito_target,
            notifikasi_deposito_lain,
            notifikasi_pinjaman,
            notifikasi_umum
        ]

        print("Sebelum penghapusan:")
        for notifikasi in nasabah.notifikasi:
            print(
                "-",
                notifikasi.jenis,
                "| ID:",
                notifikasi.id_objek,
                "|",
                notifikasi.pesan
            )

        # Menghapus notifikasi deposito target.
        DepositoService.hapus_notifikasi_deposito(
            nasabah,
            deposito
        )

        assert notifikasi_deposito_target not in nasabah.notifikasi, (
            "Notifikasi deposito target belum terhapus"
        )

        assert notifikasi_deposito_lain in nasabah.notifikasi, (
            "Notifikasi deposito lain ikut terhapus"
        )

        assert notifikasi_pinjaman in nasabah.notifikasi, (
            "Notifikasi pinjaman ikut terhapus oleh deposito"
        )

        assert notifikasi_umum in nasabah.notifikasi, (
            "Notifikasi umum ikut terhapus oleh deposito"
        )

        print()
        print("✅ Penghapusan notifikasi deposito terisolasi")

        # Menghapus satu-satunya notifikasi pinjaman.
        PinjamanService.hapus_notif_pinjaman(nasabah)

        assert notifikasi_pinjaman not in nasabah.notifikasi, (
            "Notifikasi pinjaman belum terhapus"
        )

        assert notifikasi_deposito_lain in nasabah.notifikasi, (
            "Notifikasi deposito ikut terhapus oleh pinjaman"
        )

        assert notifikasi_umum in nasabah.notifikasi, (
            "Notifikasi umum ikut terhapus oleh pinjaman"
        )

        print("✅ Penghapusan notifikasi pinjaman terisolasi")

        assert len(nasabah.notifikasi) == 2, (
            "Jumlah akhir notifikasi tidak sesuai"
        )

        print()
        print("Notifikasi yang tersisa:")
        for notifikasi in nasabah.notifikasi:
            print(
                "-",
                notifikasi.jenis,
                "| ID:",
                notifikasi.id_objek,
                "|",
                notifikasi.pesan
            )

        print()
        print("✅ Integritas isolasi notifikasi berhasil")

    finally:
        # Mengembalikan list notifikasi asli milik nasabah.
        nasabah.notifikasi = notifikasi_asli

-------------------------------------------------------------------

def uji_save_load_notifikasi(bank):
    nasabah = next(iter(bank.data_nasabah.values()))

    if not nasabah.deposito:
        raise ValueError(
            "Nasabah tidak memiliki deposito untuk pengujian"
        )

    deposito = nasabah.deposito[0]
    nik = nasabah.NIK

    # Menyimpan daftar notifikasi asli.
    notifikasi_asli = nasabah.notifikasi

    # Menyimpan lokasi file JSON utama.
    lokasi_asli = {
        "rekening": JsonStorage.file_rek,
        "nasabah": JsonStorage.file_nasabah,
        "audit": JsonStorage.file_audit,
        "deposito": JsonStorage.file_depo,
        "pinjaman": JsonStorage.file_pinjaman
    }

    try:
        notifikasi_deposito = Notifikasi(
            jenis="deposito",
            pesan="Uji save/load deposito",
            referensi_id=JenisReferensiID.DEPOSITO,
            id_objek=deposito.ID
        )

        notifikasi_pinjaman = Notifikasi(
            jenis="pinjaman",
            pesan="Uji save/load pinjaman",
            referensi_id=JenisReferensiID.PINJAMAN
        )

        notifikasi_umum = Notifikasi(
            jenis="rekening",
            pesan="Uji save/load rekening"
        )

        # Menggunakan notifikasi sementara.
        nasabah.notifikasi = [
            notifikasi_deposito,
            notifikasi_pinjaman,
            notifikasi_umum
        ]

        print("Sebelum save/load:")

        for notifikasi in nasabah.notifikasi:
            print(
                "-",
                notifikasi.jenis,
                "| Referensi:",
                notifikasi.referensi_id,
                "| ID:",
                notifikasi.id_objek
            )

        with tempfile.TemporaryDirectory() as folder_uji:
            JsonStorage.file_rek = os.path.join(
                folder_uji,
                "rekening.json"
            )
            JsonStorage.file_nasabah = os.path.join(
                folder_uji,
                "nasabah.json"
            )
            JsonStorage.file_audit = os.path.join(
                folder_uji,
                "audit.json"
            )
            JsonStorage.file_depo = os.path.join(
                folder_uji,
                "deposito.json"
            )
            JsonStorage.file_pinjaman = os.path.join(
                folder_uji,
                "pinjaman.json"
            )

            # Menyimpan seluruh objek bank ke JSON sementara.
            JsonStorage.simpan_bank(bank)

            # Membuat Bank baru dari JSON sementara.
            bank_hasil_load = JsonStorage.muat_bank()
            nasabah_hasil_load = bank_hasil_load.data_nasabah[nik]

            notifikasi_hasil = {
                notifikasi.pesan: notifikasi
                for notifikasi in nasabah_hasil_load.notifikasi
            }

            assert len(notifikasi_hasil) == 3, (
                "Jumlah notifikasi berubah setelah save/load"
            )

            deposito_hasil = notifikasi_hasil[
                "Uji save/load deposito"
            ]

            pinjaman_hasil = notifikasi_hasil[
                "Uji save/load pinjaman"
            ]

            umum_hasil = notifikasi_hasil[
                "Uji save/load rekening"
            ]

            # Memeriksa notifikasi deposito.
            assert deposito_hasil.jenis == "deposito"
            assert (
                deposito_hasil.referensi_id
                == JenisReferensiID.DEPOSITO
            )
            assert deposito_hasil.id_objek == deposito.ID

            # Memeriksa notifikasi pinjaman.
            assert pinjaman_hasil.jenis == "pinjaman"
            assert (
                pinjaman_hasil.referensi_id
                == JenisReferensiID.PINJAMAN
            )
            assert pinjaman_hasil.id_objek is None

            # Memeriksa notifikasi tanpa referensi.
            assert umum_hasil.jenis == "rekening"
            assert umum_hasil.referensi_id is None
            assert umum_hasil.id_objek is None

            print()
            print("Setelah save/load:")

            for notifikasi in nasabah_hasil_load.notifikasi:
                print(
                    "-",
                    notifikasi.jenis,
                    "| Referensi:",
                    notifikasi.referensi_id,
                    "| ID:",
                    notifikasi.id_objek
                )

            print()
            print("✅ Integritas save/load notifikasi berhasil")

    finally:
        # Mengembalikan notifikasi asli.
        nasabah.notifikasi = notifikasi_asli

        # Mengembalikan seluruh lokasi JSON utama.
        JsonStorage.file_rek = lokasi_asli["rekening"]
        JsonStorage.file_nasabah = lokasi_asli["nasabah"]
        JsonStorage.file_audit = lokasi_asli["audit"]
        JsonStorage.file_depo = lokasi_asli["deposito"]
        JsonStorage.file_pinjaman = lokasi_asli["pinjaman"]

if __name__ == "__main__":
    uji_save_load_notifikasi(bank)



-----------------------------------------------------

