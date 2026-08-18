def uji_relasi_downgrade_rekening(bank):
    # Mengambil satu-satunya nasabah dalam dataset.
    nasabah = next(iter(bank.data_nasabah.values()))

    # Mencari rekening Platinum milik nasabah.
    rekening_platinum = next(
        (
            rekening
            for rekening in nasabah.rekening
            if rekening.level == 3
        ),
        None
    )

    if rekening_platinum is None:
        raise ValueError(
            "Nasabah tidak memiliki rekening gold untuk diuji"
        )

    # Menyimpan objek deposito yang menggunakan rekening Platinum.
    deposito_terkait = [
        deposito
        for deposito in nasabah.deposito
        if deposito.rekening is rekening_platinum
    ]

    # Menyimpan objek pinjaman yang menggunakan rekening Platinum.
    pinjaman_terkait = [
        pinjaman
        for pinjaman in bank.daftar_pinjaman
        if pinjaman.rekening is rekening_platinum
    ]

    print("Sebelum downgrade:")
    print("Nasabah          :", nasabah.nama)
    print("Nomor rekening   :", rekening_platinum.norek)
    print("Objek rekening   :", id(rekening_platinum))
    print("Level rekening   :", rekening_platinum.level)
    print("Jenis rekening   :", RekeningService.level[rekening_platinum.level])
    print("Jumlah deposito  :", len(deposito_terkait))
    print("Jumlah pinjaman  :", len(pinjaman_terkait))

    # Melakukan downgrade dari Platinum ke Gold.
    rekening_gold = RekeningService.downgrade_rekening(
        bank,
        rekening_platinum,
        target_level=2
    )

    # Memastikan downgrade menghasilkan objek rekening baru.
    assert rekening_gold is not rekening_platinum, (
        "Downgrade tidak menghasilkan objek rekening baru"
    )

    assert rekening_gold.level == 2, (
        "Rekening hasil downgrade seharusnya Gold"
    )

    # Nomor rekening harus tetap sama.
    assert rekening_gold.norek == rekening_platinum.norek, (
        "Nomor rekening berubah setelah downgrade"
    )

    # Bank harus menunjuk objek Gold.
    assert bank.rekening_index[rekening_gold.norek] is rekening_gold, (
        "Bank masih menunjuk rekening Platinum"
    )

    # Nasabah harus menyimpan objek Gold.
    assert rekening_gold in nasabah.rekening, (
        "Daftar rekening nasabah belum menyimpan rekening Gold"
    )

    assert rekening_platinum not in nasabah.rekening, (
        "Rekening Platinum lama masih tersimpan pada nasabah"
    )

    # Semua deposito harus menunjuk rekening Gold.
    for deposito in deposito_terkait:
        assert deposito.rekening is rekening_gold, (
            f"Deposito #{deposito.id} masih menunjuk rekening Platinum"
        )

    # Semua pinjaman harus menunjuk rekening Gold.
    for pinjaman in pinjaman_terkait:
        assert pinjaman.rekening is rekening_gold, (
            f"Pinjaman #{pinjaman.ID} masih menunjuk rekening Platinum"
        )

    print()
    print("Setelah downgrade:")
    print("Nomor rekening   :", rekening_gold.norek)
    print("Objek rekening   :", id(rekening_gold))
    print("Level rekening   :", rekening_gold.level)
    print("Jenis rekening   :", RekeningService.level[rekening_gold.level])
    print("Deposito terhubung:", len(deposito_terkait))
    print("Pinjaman terhubung:", len(pinjaman_terkait))
    print("✅ Relasi downgrade rekening berhasil")


-----------------------------------------------------------------------


def uji_relasi_upgrade_rekening(bank):
    rekening_lama = None
    nasabah = None

    # Mencari rekening yang digunakan oleh deposito dan pinjaman sekaligus.
    for kandidat in bank.rekening_index.values():
        pemilik = kandidat.pemilik

        deposito_terkait = [
            deposito
            for deposito in pemilik.deposito
            if deposito.rekening is kandidat
        ]

        pinjaman_terkait = [
            pinjaman
            for pinjaman in bank.daftar_pinjaman
            if pinjaman.rekening is kandidat
        ]

        if deposito_terkait and pinjaman_terkait:
            rekening_lama = kandidat
            nasabah = pemilik
            break

    if rekening_lama is None:
        raise ValueError(
            "Tidak ditemukan rekening yang terhubung dengan "
            "deposito dan pinjaman sekaligus"
        )

    deposito_terkait = [
        deposito
        for deposito in nasabah.deposito
        if deposito.rekening is rekening_lama
    ]

    pinjaman_terkait = [
        pinjaman
        for pinjaman in bank.daftar_pinjaman
        if pinjaman.rekening is rekening_lama
    ]

    print("Sebelum upgrade:")
    print("Nasabah          :", nasabah.nama)
    print("Nomor rekening   :", rekening_lama.norek)
    print("Objek rekening   :", id(rekening_lama))
    print("Level rekening   :", rekening_lama.level)
    print("Jumlah deposito  :", len(deposito_terkait))
    print("Jumlah pinjaman  :", len(pinjaman_terkait))

    # Menyiapkan rekening Gold agar memenuhi syarat upgrade ke Platinum.
    rekening_lama.set_saldo(200_000_000)

    rekening_baru = RekeningService.upgrade_rekening(
        bank,
        rekening_lama,
        target_level=4
    )

    # Memastikan upgrade benar-benar menghasilkan objek baru.
    assert rekening_baru is not rekening_lama, (
        "Upgrade tidak menghasilkan objek rekening baru"
    )

    assert rekening_baru.level == 4, (
        "Rekening hasil upgrade seharusnya Platinum"
    )

    assert rekening_baru.norek == rekening_lama.norek, (
        "Nomor rekening berubah setelah upgrade"
    )

    # Memastikan Bank dan Nasabah menggunakan rekening baru.
    assert bank.rekening_index[rekening_baru.norek] is rekening_baru, (
        "Bank masih menunjuk rekening lama"
    )

    assert rekening_baru in nasabah.rekening, (
        "Nasabah belum menyimpan rekening baru"
    )

    assert rekening_lama not in nasabah.rekening, (
        "Rekening lama masih tersimpan pada nasabah"
    )

    # Memastikan semua deposito terkait berpindah ke rekening baru.
    for deposito in deposito_terkait:
        assert deposito.rekening is rekening_baru, (
            f"Deposito #{deposito.id} masih menunjuk rekening lama"
        )

    # Memastikan semua pinjaman terkait berpindah ke rekening baru.
    for pinjaman in pinjaman_terkait:
        assert pinjaman.rekening is rekening_baru, (
            f"Pinjaman #{pinjaman.ID} masih menunjuk rekening lama"
        )

    print()
    print("Setelah upgrade:")
    print("Objek rekening   :", id(rekening_baru))
    print("Level rekening   :", rekening_baru.level)
    print("Jenis rekening   :", RekeningService.level[rekening_baru.level])
    print("Deposito terhubung:", len(deposito_terkait))
    print("Pinjaman terhubung:", len(pinjaman_terkait))
    print("✅ Relasi rekening, deposito, dan pinjaman berhasil")


----------------------------------------------------------------------------

def uji_save_load_relasi_rekening(bank):
    # Mengambil satu-satunya nasabah dan rekening yang memiliki relasi.
    nasabah_awal = next(iter(bank.data_nasabah.values()))

    rekening_awal = next(
        (
            rekening
            for rekening in nasabah_awal.rekening
            if any(
                deposito.rekening is rekening
                for deposito in nasabah_awal.deposito
            )
            and any(
                pinjaman.rekening is rekening
                for pinjaman in bank.daftar_pinjaman
            )
        ),
        None
    )

    if rekening_awal is None:
        raise ValueError(
            "Tidak ditemukan rekening yang terhubung dengan "
            "deposito dan pinjaman sekaligus"
        )

    nik = nasabah_awal.NIK
    norek = rekening_awal.norek
    level = rekening_awal.level

    print("Sebelum save/load:")
    print("Nasabah         :", nasabah_awal.nama)
    print("Nomor rekening  :", norek)
    print("Objek rekening  :", id(rekening_awal))
    print("Level rekening  :", level)
    print("Jenis rekening  :", RekeningService.level[level])

    # Menyimpan lokasi file JSON utama agar dapat dikembalikan.
    lokasi_asli = {
        "rekening": JsonStorage.file_rek,
        "nasabah": JsonStorage.file_nasabah,
        "audit": JsonStorage.file_audit,
        "deposito": JsonStorage.file_depo,
        "pinjaman": JsonStorage.file_pinjaman
    }

    try:
        # TemporaryDirectory otomatis dihapus setelah pengujian selesai.
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

            # Menyimpan bank ke file pengujian sementara.
            JsonStorage.simpan_bank(bank)

            # Membuat objek Bank baru dari file pengujian.
            bank_hasil_load = JsonStorage.muat_bank()

            nasabah_hasil_load = bank_hasil_load.data_nasabah[nik]
            rekening_hasil_load = bank_hasil_load.rekening_index[norek]

            deposito_hasil_load = [
                deposito
                for deposito in nasabah_hasil_load.deposito
                if deposito.rekening.norek == norek
            ]

            pinjaman_hasil_load = [
                pinjaman
                for pinjaman in bank_hasil_load.daftar_pinjaman
                if pinjaman.rekening.norek == norek
            ]

            # Objek hasil load memang harus berbeda dari objek sebelumnya.
            assert rekening_hasil_load is not rekening_awal, (
                "Save/load seharusnya membuat objek rekening baru di memori"
            )

            # Data penting rekening harus tetap sama.
            assert rekening_hasil_load.norek == norek, (
                "Nomor rekening berubah setelah save/load"
            )

            assert rekening_hasil_load.level == level, (
                "Level rekening berubah setelah save/load"
            )

            # Nasabah harus menunjuk objek rekening dari index Bank.
            rekening_milik_nasabah = next(
                rekening
                for rekening in nasabah_hasil_load.rekening
                if rekening.norek == norek
            )

            assert rekening_milik_nasabah is rekening_hasil_load, (
                "Nasabah dan Bank menunjuk objek rekening yang berbeda"
            )

            assert deposito_hasil_load, (
                "Deposito tidak ditemukan setelah load"
            )

            assert pinjaman_hasil_load, (
                "Pinjaman tidak ditemukan setelah load"
            )

            # Semua deposito harus menunjuk objek rekening yang sama.
            for deposito in deposito_hasil_load:
                assert deposito.rekening is rekening_hasil_load, (
                    f"Deposito #{deposito.ID} menunjuk objek rekening berbeda"
                )

            # Semua pinjaman harus menunjuk objek rekening yang sama.
            for pinjaman in pinjaman_hasil_load:
                assert pinjaman.rekening is rekening_hasil_load, (
                    f"Pinjaman #{pinjaman.ID} menunjuk objek rekening berbeda"
                )

            print()
            print("Setelah save/load:")
            print("Objek rekening   :", id(rekening_hasil_load))
            print("Level rekening   :", rekening_hasil_load.level)
            print(
                "Jenis rekening   :",
                RekeningService.level[rekening_hasil_load.level]
            )
            print("Deposito terhubung:", len(deposito_hasil_load))
            print("Pinjaman terhubung:", len(pinjaman_hasil_load))
            print("✅ Integritas relasi setelah save/load berhasil")

    finally:
        # Mengembalikan semua lokasi JSON utama.
        JsonStorage.file_rek = lokasi_asli["rekening"]
        JsonStorage.file_nasabah = lokasi_asli["nasabah"]
        JsonStorage.file_audit = lokasi_asli["audit"]
        JsonStorage.file_depo = lokasi_asli["deposito"]
        JsonStorage.file_pinjaman = lokasi_asli["pinjaman"]


----------------------------------------------------------------------------
bank = JsonStorage.muat_bank()
def uji_integritas_upgrade_rekening(bank):
    # Mengambil rekening awal yang akan diuji.
    rekening_lama = next(iter(bank.rekening_index.values()))
    nasabah = rekening_lama.pemilik

    print("Sebelum upgrade:")
    print("Objek rekening:", id(rekening_lama))
    print("Level:", rekening_lama.level)

    # Menambahkan saldo agar memenuhi persyaratan upgrade.
    rekening_lama.set_saldo(200_000_000)

    # Melakukan upgrade dan menerima objek rekening pengganti.
    rekening_baru = RekeningService.upgrade_rekening(
        bank,
        rekening_lama,
        target_level=4
    )

    print()
    print("Setelah upgrade:")
    print("Objek rekening:", id(rekening_baru))
    print("Level:", rekening_baru.level)
    print("Jenis:", RekeningService.level[rekening_baru.level])


    # Memastikan bank menyimpan objek rekening baru.
    assert rekening_baru is bank.rekening_index[rekening_baru.norek], (
        "Bank masih menyimpan objek rekening lama"
    )

    assert rekening_baru is not rekening_lama, (
        "Service tidak membuat objek rekening pengganti"
    )

    assert rekening_baru.level == 4, (
        "Rekening baru seharusnya Platinum"
    )

    assert rekening_baru.norek == rekening_lama.norek, (
        "Nomor rekening berubah setelah upgrade"
    )
    # Memastikan nasabah juga menyimpan objek rekening baru.
    assert rekening_baru in nasabah.rekening, (
        "Daftar rekening nasabah belum menyimpan rekening baru"
    )

    indeks = nasabah.rekening.index(rekening_baru)

    assert rekening_baru is nasabah.rekening[indeks], (
        "Referensi rekening milik nasabah tidak sama"
    )

    # Memastikan objek lama tidak lagi berada pada relasi utama.
    assert rekening_lama is not bank.rekening_index[rekening_baru.norek], (
        "Bank masih menunjuk objek rekening lama"
    )

    assert rekening_lama not in nasabah.rekening, (
        "Objek rekening lama masih tersimpan pada nasabah"
    )

    print("✅ Integritas upgrade rekening berhasil")
- ----------------------------------------------------------------



