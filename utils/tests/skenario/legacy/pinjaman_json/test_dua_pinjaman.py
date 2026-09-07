"""Skenario manual yang dipulihkan dari `utils/tests/test_pinjaman.py` (urutan 2).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

def siapkan_dua_pinjaman_untuk_uji(bank):
    nik = input("Masukkan NIK nasabah yang akan diuji: ").strip()

    nasabah = bank.cari_nasabah(nik)

    if nasabah is None:
        raise ValueError("NIK nasabah tidak ditemukan")

    pinjaman_lama = nasabah.pinjaman

    if pinjaman_lama is None:
        raise ValueError(
            "Nasabah tidak memiliki pinjaman berjalan"
        )

    if pinjaman_lama.status != StatusPinjaman.AKTIF:
        raise ValueError(
            "Pinjaman nasabah belum berstatus aktif"
        )

    rekening = pinjaman_lama.rekening

    print()
    print("DATA PINJAMAN LAMA")
    print("Nasabah          :", nasabah.nama)
    print("ID pinjaman      :", pinjaman_lama.ID)
    print("Status           :", pinjaman_lama.status.value)
    print("Tenor            :", pinjaman_lama.tenor)
    print("Cicilan terbayar :", pinjaman_lama.cicilan_terbayar)
    print(
        "Cicilan tersisa  :",
        pinjaman_lama.tenor
        - pinjaman_lama.cicilan_terbayar
    )
    print()

    cicilan_tersisa = (
        pinjaman_lama.tenor
        - pinjaman_lama.cicilan_terbayar
    )

    tanggal_pelunasan = None

    # Melunasi seluruh cicilan yang masih tersisa.
    for _ in range(cicilan_tersisa):
        tanggal_bayar = pinjaman_lama.tanggal_jatuh_tempo
        tanggal_pelunasan = tanggal_bayar

        denda = PinjamanService.hitung_denda(
            pinjaman_lama,
            tanggal_bayar
        )

        total_bayar = (
            pinjaman_lama.cicilan_tetap
            + denda
        )

        saldo_minimum = (
            total_bayar
            + rekening.saldosetor_min
        )

        # Menambahkan saldo pengujian jika saldo tidak mencukupi.
        if rekening.saldo < saldo_minimum:
            kekurangan = saldo_minimum - rekening.saldo
            rekening.tambah_saldo(kekurangan)

        nomor_cicilan = (
            pinjaman_lama.cicilan_terbayar
            + 1
        )

        PinjamanService.bayar_cicilan(
            bank,
            pinjaman_lama,
            hari_ini=tanggal_bayar
        )

        print(
            f"Cicilan ke-{nomor_cicilan} dibayar "
            f"pada {tanggal_bayar}"
        )

    assert pinjaman_lama.status == StatusPinjaman.LUNAS, (
        "Pinjaman lama seharusnya sudah lunas"
    )

    assert pinjaman_lama.sisa_pokok == 0, (
        "Sisa pokok pinjaman lama seharusnya nol"
    )

    assert nasabah.pinjaman is None, (
        "Nasabah masih menunjuk pinjaman lama"
    )

    assert pinjaman_lama in bank.daftar_pinjaman, (
        "Pinjaman lama hilang dari daftar pinjaman Bank"
    )

    print()
    print("✅ Pinjaman lama berhasil dilunasi")
    print("ID pinjaman :", pinjaman_lama.ID)
    print("Status      :", pinjaman_lama.status.value)
    print()

    # Pinjaman baru dimulai sehari setelah pelunasan.
    tanggal_pencairan_baru = (
        tanggal_pelunasan
        + datetime.timedelta(days=1)
    )

    pinjaman_baru = PinjamanService.ajukan_pinjaman(
        bank=bank,
        nasabah=nasabah,
        rekening=rekening,
        nominal=1_000_000,
        tenor=6
    )

    PinjamanService.setujui_pinjaman(
        bank,
        pinjaman_baru
    )

    PinjamanService.cairkan_pinjaman(
        bank,
        pinjaman_baru,
        hari_ini=tanggal_pencairan_baru
    )

    assert pinjaman_baru.status == StatusPinjaman.AKTIF, (
        "Pinjaman baru seharusnya berstatus aktif"
    )

    assert nasabah.pinjaman is pinjaman_baru, (
        "Nasabah tidak menunjuk pinjaman baru"
    )

    assert pinjaman_baru in bank.daftar_pinjaman, (
        "Pinjaman baru belum masuk daftar pinjaman Bank"
    )

    assert pinjaman_baru is not pinjaman_lama, (
        "Pinjaman baru dan lama merupakan objek yang sama"
    )

    assert pinjaman_baru.ID > pinjaman_lama.ID, (
        "ID pinjaman baru tidak melanjutkan ID sebelumnya"
    )

    daftar_pinjaman_nasabah = [
        pinjaman
        for pinjaman in bank.daftar_pinjaman
        if pinjaman.pemilik is nasabah
    ]

    assert len(daftar_pinjaman_nasabah) >= 2, (
        "Bank belum menyimpan kedua pinjaman nasabah"
    )

    print("DATA PINJAMAN SETELAH PERSIAPAN")
    print("Nasabah              :", nasabah.nama)
    print("Pinjaman lama        :", pinjaman_lama.ID)
    print("Status pinjaman lama :", pinjaman_lama.status.value)
    print("Pinjaman baru        :", pinjaman_baru.ID)
    print("Status pinjaman baru :", pinjaman_baru.status.value)
    print(
        "Jumlah pinjaman Bank :",
        len(daftar_pinjaman_nasabah)
    )
    print(
        "Pinjaman aktif       :",
        nasabah.pinjaman.ID
    )
    print()
    print("✅ Dataset dua pinjaman siap diuji")

    return nasabah, pinjaman_lama, pinjaman_baru


# ---------------------------------------------------------------
# def uji_save_load_dua_pinjaman(
#     bank,
#     nasabah,
#     pinjaman_lunas,
#     pinjaman_aktif
# ):
#     nik = nasabah.NIK
#
#     lokasi_asli = {
#         "rekening": JsonStorage.file_rek,
#         "nasabah": JsonStorage.file_nasabah,
#         "audit": JsonStorage.file_audit,
#         "deposito": JsonStorage.file_depo,
#         "pinjaman": JsonStorage.file_pinjaman
#     }
#
#     try:
#         with tempfile.TemporaryDirectory() as folder_uji:
#             JsonStorage.file_rek = os.path.join(
#                 folder_uji,
#                 "rekening.json"
#             )
#             JsonStorage.file_nasabah = os.path.join(
#                 folder_uji,
#                 "nasabah.json"
#             )
#             JsonStorage.file_audit = os.path.join(
#                 folder_uji,
#                 "audit.json"
#             )
#             JsonStorage.file_depo = os.path.join(
#                 folder_uji,
#                 "deposito.json"
#             )
#             JsonStorage.file_pinjaman = os.path.join(
#                 folder_uji,
#                 "pinjaman.json"
#             )
#
#             # Menyimpan seluruh Bank ke JSON sementara.
#             JsonStorage.simpan_bank(bank)
#
#             data_pinjaman_json = JsonStorage.muat_json(
#                 JsonStorage.file_pinjaman,
#                 {}
#             )
#
#             # Memastikan NIK menjadi key utama.
#             assert nik in data_pinjaman_json, (
#                 "NIK nasabah tidak ditemukan dalam pinjaman.json"
#             )
#
#             pinjaman_milik_nasabah = data_pinjaman_json[nik]
#
#             # Memastikan ID menjadi key cabang.
#             assert str(pinjaman_lunas.ID) in pinjaman_milik_nasabah, (
#                 "Pinjaman lunas tidak tersimpan berdasarkan ID"
#             )
#
#             assert str(pinjaman_aktif.ID) in pinjaman_milik_nasabah, (
#                 "Pinjaman aktif tidak tersimpan berdasarkan ID"
#             )
#
#             assert len(pinjaman_milik_nasabah) == 2, (
#                 "Jumlah pinjaman dalam JSON tidak sesuai"
#             )
#
#             print("STRUKTUR JSON")
#             print("NIK               :", nik)
#             print(
#                 "ID yang tersimpan :",
#                 list(pinjaman_milik_nasabah.keys())
#             )
#
#             # Memuat JSON menjadi objek Bank baru.
#             bank_hasil_load = JsonStorage.muat_bank()
#             nasabah_hasil_load = (
#                 bank_hasil_load.data_nasabah[nik]
#             )
#
#             daftar_hasil_load = [
#                 pinjaman
#                 for pinjaman in bank_hasil_load.daftar_pinjaman
#                 if pinjaman.pemilik is nasabah_hasil_load
#             ]
#
#             assert len(daftar_hasil_load) == 2, (
#                 "Tidak semua pinjaman dimuat ke daftar Bank"
#             )
#
#             pinjaman_lunas_hasil = next(
#                 pinjaman
#                 for pinjaman in daftar_hasil_load
#                 if pinjaman.ID == pinjaman_lunas.ID
#             )
#
#             pinjaman_aktif_hasil = next(
#                 pinjaman
#                 for pinjaman in daftar_hasil_load
#                 if pinjaman.ID == pinjaman_aktif.ID
#             )
#
#             assert (
#                 pinjaman_lunas_hasil.status
#                 == StatusPinjaman.LUNAS
#             ), "Status pinjaman lama berubah setelah load"
#
#             assert (
#                 pinjaman_aktif_hasil.status
#                 == StatusPinjaman.AKTIF
#             ), "Status pinjaman baru berubah setelah load"
#
#             # Nasabah hanya menunjuk pinjaman berjalan.
#             assert (
#                 nasabah_hasil_load.pinjaman
#                 is pinjaman_aktif_hasil
#             ), (
#                 "Nasabah tidak menunjuk pinjaman aktif "
#                 "hasil load"
#             )
#
#             assert (
#                 nasabah_hasil_load.pinjaman
#                 is not pinjaman_lunas_hasil
#             ), (
#                 "Nasabah masih menunjuk pinjaman yang lunas"
#             )
#
#             # Kedua pinjaman harus menunjuk nasabah hasil load.
#             assert (
#                 pinjaman_lunas_hasil.pemilik
#                 is nasabah_hasil_load
#             )
#
#             assert (
#                 pinjaman_aktif_hasil.pemilik
#                 is nasabah_hasil_load
#             )
#
#             # Kedua pinjaman harus menggunakan objek rekening Bank.
#             assert (
#                 pinjaman_lunas_hasil.rekening
#                 is bank_hasil_load.rekening_index[
#                     pinjaman_lunas_hasil.rekening.norek
#                 ]
#             )
#
#             assert (
#                 pinjaman_aktif_hasil.rekening
#                 is bank_hasil_load.rekening_index[
#                     pinjaman_aktif_hasil.rekening.norek
#                 ]
#             )
#
#             assert nasabah_hasil_load.jumlah_pinjaman == 2, (
#                 "Penghitung jumlah pinjaman tidak dipulihkan"
#             )
#
#             print()
#             print("SETELAH LOAD")
#
#             for pinjaman in daftar_hasil_load:
#                 print(
#                     f"- Pinjaman #{pinjaman.ID} | "
#                     f"Status: {pinjaman.status.value} | "
#                     f"Objek: {id(pinjaman)}"
#                 )
#
#             print(
#                 "Pinjaman aktif nasabah:",
#                 nasabah_hasil_load.pinjaman.ID
#             )
#             print(
#                 "Jumlah pinjaman nasabah:",
#                 nasabah_hasil_load.jumlah_pinjaman
#             )
#             print()
#             print(
#                 "✅ Save/load dua pinjaman berhasil"
#             )
#
#     finally:
#         JsonStorage.file_rek = lokasi_asli["rekening"]
#         JsonStorage.file_nasabah = lokasi_asli["nasabah"]
#         JsonStorage.file_audit = lokasi_asli["audit"]
#         JsonStorage.file_depo = lokasi_asli["deposito"]
#         JsonStorage.file_pinjaman = lokasi_asli["pinjaman"]





# ----------------------------------------------------------------
def uji_integritas_pinjaman():
    # Memuat dataset utama sebagai objek bank.
    bank = JsonStorage.muat_bank()

    # Helper ini membutuhkan satu pinjaman aktif.
    # Pinjaman tersebut akan dilunasi, lalu dibuatkan
    # pinjaman aktif baru untuk nasabah yang sama.
    nasabah, pinjaman_lunas, pinjaman_aktif = (
        siapkan_dua_pinjaman_untuk_uji(bank)
    )

    # Memastikan dataset pengujian benar-benar siap.
    pinjaman_milik_nasabah = [
        pinjaman
        for pinjaman in bank.daftar_pinjaman
        if pinjaman.pemilik is nasabah
    ]

    assert pinjaman_lunas in pinjaman_milik_nasabah, (
        "Pinjaman lunas tidak ditemukan dalam daftar bank"
    )

    assert pinjaman_aktif in pinjaman_milik_nasabah, (
        "Pinjaman aktif tidak ditemukan dalam daftar bank"
    )

    assert pinjaman_lunas.status == StatusPinjaman.LUNAS, (
        "Pinjaman lama belum berstatus lunas"
    )

    assert pinjaman_aktif.status == StatusPinjaman.AKTIF, (
        "Pinjaman baru belum berstatus aktif"
    )

    assert nasabah.pinjaman is pinjaman_aktif, (
        "Nasabah tidak menunjuk pinjaman aktif"
    )

    # Menjalankan pemeriksaan umum seluruh relasi pinjaman.
    daftar_error = cek_integritas_pinjaman(bank)

    if daftar_error:
        print("\nMASALAH INTEGRITAS PINJAMAN:")

        for nomor, error in enumerate(daftar_error, start=1):
            print(f"{nomor}. {error}")

        raise AssertionError(
            f"Ditemukan {len(daftar_error)} masalah integritas"
        )

    print()
    print("RINGKASAN PENGUJIAN")
    print("Nasabah          :", nasabah.nama)
    print("Jumlah historis  :", len(pinjaman_milik_nasabah))
    print("Pinjaman lunas   :", pinjaman_lunas.ID)
    print("Pinjaman aktif   :", pinjaman_aktif.ID)
    print("Referensi aktif  :", nasabah.pinjaman.ID)
    print()
    print("✅ Integritas pinjaman tidak menemukan masalah")
