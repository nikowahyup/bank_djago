def uji_save_load_pinjaman_menunggak():
    """
    Menguji konsistensi pinjaman menunggak setelah proses
    penyimpanan dan pemuatan ulang JSON.

    Pengujian memastikan:
    - Data asli tidak ditimpa.
    - Tanggal jatuh tempo tetap sama.
    - Status pinjaman tetap AKTIF.
    - Jumlah cicilan terbayar tetap sama.
    - Relasi nasabah dan rekening tetap menggunakan objek
      yang terdaftar di bank.
    - Hari keterlambatan dan denda dapat dihitung kembali.
    - Notifikasi tunggakan tetap mempunyai referensi objek.
    """

    # Muat data awal dari penyimpanan asli.
    bank = JsonStorage.muat_bank()

    # Ambil satu pinjaman aktif.
    pinjaman = next(
        (
            item
            for item in bank.daftar_pinjaman
            if item.status == StatusPinjaman.AKTIF
        ),
        None
    )

    if pinjaman is None:
        print("Tidak ada pinjaman aktif untuk diuji.")
        return

    # Simpan identitas objek yang akan dicari kembali
    # setelah proses pemuatan JSON.
    id_pinjaman = pinjaman.ID
    nik_pemilik = pinjaman.pemilik.NIK
    nomor_rekening = pinjaman.rekening.norek

    # Gunakan hari pertama setelah masa toleransi.
    hari_uji = (
        pinjaman.tanggal_jatuh_tempo
        + datetime.timedelta(
            days=(
                PinjamanService.BATAS_HARI_TUNGGAKAN
                + 1
            )
        )
    )

    # Jalankan scheduler agar notifikasi tunggakan dibuat.
    Scheduler.jalankan(bank, hari_uji)

    # Simpan state sebelum proses save/load.
    jatuh_tempo_sebelum = pinjaman.tanggal_jatuh_tempo
    status_sebelum = pinjaman.status
    cicilan_terbayar_sebelum = pinjaman.cicilan_terbayar
    sisa_pokok_sebelum = pinjaman.sisa_pokok

    hari_terlambat_sebelum = (
        PinjamanService.hitung_hari_terlambat(
            pinjaman,
            hari_uji
        )
    )

    denda_sebelum = PinjamanService.hitung_denda(
        pinjaman,
        hari_uji
    )

    # Simpan seluruh lokasi file asli agar dapat
    # dikembalikan setelah pengujian.
    lokasi_asli = {
        "file_rek": JsonStorage.file_rek,
        "file_nasabah": JsonStorage.file_nasabah,
        "file_audit": JsonStorage.file_audit,
        "file_depo": JsonStorage.file_depo,
        "file_pinjaman": JsonStorage.file_pinjaman
    }

    try:
        # Buat direktori sementara yang otomatis dihapus
        # setelah pengujian selesai.
        with tempfile.TemporaryDirectory() as direktori:
            direktori = Path(direktori)

            # Arahkan JsonStorage ke file sementara agar
            # data JSON asli tidak berubah.
            JsonStorage.file_rek = str(
                direktori / "rekening.json"
            )

            JsonStorage.file_nasabah = str(
                direktori / "nasabah.json"
            )

            JsonStorage.file_audit = str(
                direktori / "audit.json"
            )

            JsonStorage.file_depo = str(
                direktori / "deposito.json"
            )

            JsonStorage.file_pinjaman = str(
                direktori / "pinjaman.json"
            )

            # Simpan bank ke seluruh file sementara.
            JsonStorage.simpan_bank(bank)

            # Muat kembali bank dari file sementara.
            bank_hasil = JsonStorage.muat_bank()

            # Cari pinjaman yang sama berdasarkan ID
            # dan NIK pemiliknya.
            pinjaman_hasil = next(
                (
                    item
                    for item in bank_hasil.daftar_pinjaman
                    if (
                        item.ID == id_pinjaman
                        and item.pemilik.NIK == nik_pemilik
                    )
                ),
                None
            )

            assert pinjaman_hasil is not None, (
                "Pinjaman tidak ditemukan setelah load"
            )

            # Hitung ulang keterlambatan dan denda
            # berdasarkan data hasil load.
            hari_terlambat_hasil = (
                PinjamanService.hitung_hari_terlambat(
                    pinjaman_hasil,
                    hari_uji
                )
            )

            denda_hasil = PinjamanService.hitung_denda(
                pinjaman_hasil,
                hari_uji
            )

            # Pastikan state utama pinjaman tetap sama.
            assert (
                pinjaman_hasil.tanggal_jatuh_tempo
                == jatuh_tempo_sebelum
            ), "Jatuh tempo berubah setelah save/load"

            assert (
                pinjaman_hasil.status
                == status_sebelum
            ), "Status pinjaman berubah setelah save/load"

            assert (
                pinjaman_hasil.cicilan_terbayar
                == cicilan_terbayar_sebelum
            ), (
                "Jumlah cicilan terbayar berubah "
                "setelah save/load"
            )

            assert math.isclose(
                pinjaman_hasil.sisa_pokok,
                sisa_pokok_sebelum,
                rel_tol=1e-9
            ), "Sisa pokok berubah setelah save/load"

            # Pastikan hasil perhitungan waktu tetap sama.
            assert (
                hari_terlambat_hasil
                == hari_terlambat_sebelum
            ), (
                "Hari keterlambatan berubah "
                "setelah save/load"
            )

            assert denda_hasil == denda_sebelum, (
                "Nominal denda berubah setelah save/load"
            )

            # Pastikan relasi pemilik menunjuk objek nasabah
            # yang tersimpan dalam bank hasil load.
            assert (
                pinjaman_hasil.pemilik
                is bank_hasil.data_nasabah[nik_pemilik]
            ), "Relasi pinjaman dengan nasabah tidak valid"

            # Pastikan relasi rekening menunjuk objek rekening
            # yang tersimpan dalam indeks bank.
            assert (
                pinjaman_hasil.rekening
                is bank_hasil.rekening_index[nomor_rekening]
            ), "Relasi pinjaman dengan rekening tidak valid"

            # Cari notifikasi yang merujuk pinjaman tersebut.
            notifikasi_pinjaman = [
                notifikasi
                for notifikasi
                in pinjaman_hasil.pemilik.notifikasi
                if (
                    notifikasi.referensi_id
                    == JenisReferensiID.PINJAMAN
                    and notifikasi.id_objek == id_pinjaman
                )
            ]

            assert notifikasi_pinjaman, (
                "Notifikasi tunggakan tidak ditemukan "
                "setelah save/load"
            )

            # Jalankan scheduler kembali pada tanggal yang sama.
            Scheduler.jalankan(
                bank_hasil,
                hari_uji
            )

            # Pastikan repeated scheduler tidak membuat
            # notifikasi pinjaman menjadi ganda.
            notifikasi_setelah_scheduler = [
                notifikasi
                for notifikasi
                in pinjaman_hasil.pemilik.notifikasi
                if (
                    notifikasi.referensi_id
                    == JenisReferensiID.PINJAMAN
                    and notifikasi.id_objek == id_pinjaman
                )
            ]

            assert (
                len(notifikasi_setelah_scheduler) == 1
            ), (
                "Repeated scheduler menghasilkan "
                "notifikasi pinjaman ganda"
            )

            print()
            print("=" * 60)
            print("✅ SAVE/LOAD PINJAMAN MENUNGGAK BERHASIL")
            print(f"Pinjaman          : #{id_pinjaman}")
            print(f"Jatuh tempo       : {jatuh_tempo_sebelum}")
            print(f"Tanggal simulasi  : {hari_uji}")
            print(
                "Hari terlambat    : "
                f"{hari_terlambat_hasil}"
            )
            print(
                "Denda sebelum     : "
                f"Rp{Utilitas.format_rupiah(denda_sebelum)}"
            )
            print(
                "Denda setelah load: "
                f"Rp{Utilitas.format_rupiah(denda_hasil)}"
            )
            print(
                "Notifikasi        : "
                f"{len(notifikasi_setelah_scheduler)}"
            )
            print("=" * 60)

    finally:
        # Kembalikan seluruh lokasi penyimpanan asli,
        # termasuk ketika salah satu assert gagal.
        JsonStorage.file_rek = lokasi_asli["file_rek"]
        JsonStorage.file_nasabah = lokasi_asli["file_nasabah"]
        JsonStorage.file_audit = lokasi_asli["file_audit"]
        JsonStorage.file_depo = lokasi_asli["file_depo"]
        JsonStorage.file_pinjaman = lokasi_asli["file_pinjaman"]

# -----------------------------------------------------------------------------------------------------------------


def uji_pelunasan_dengan_denda():
    """
    Menguji pelunasan pinjaman dengan membayar seluruh cicilan
    sebelumnya secara normal, kemudian membayar cicilan terakhir
    setelah masa toleransi berakhir.

    Pengujian memastikan:
    - Lifecycle pinjaman bergerak secara konsisten.
    - Cicilan terakhir dikenai denda.
    - Denda ikut dipotong dari saldo.
    - Denda tidak mengurangi pokok pinjaman.
    - Status akhir menjadi LUNAS.
    - Referensi pinjaman aktif milik nasabah dibersihkan.
    - Riwayat dan notifikasi pelunasan dibuat.
    """

    # Muat data baru agar pengujian tidak dipengaruhi
    # oleh pengujian sebelumnya.
    bank = JsonStorage.muat_bank()

    # Ambil satu pinjaman yang masih aktif.
    pinjaman = next(
        (
            item
            for item in bank.daftar_pinjaman
            if item.status == StatusPinjaman.AKTIF
        ),
        None
    )

    if pinjaman is None:
        print("Tidak ada pinjaman aktif untuk diuji.")
        return

    nasabah = pinjaman.pemilik
    rekening = pinjaman.rekening

    # Hitung jumlah cicilan yang masih harus dibayar.
    sisa_cicilan = (
        pinjaman.tenor
        - pinjaman.cicilan_terbayar
    )

    if sisa_cicilan < 1:
        print("Pinjaman tidak memiliki cicilan tersisa.")
        return

    # Siapkan saldo untuk membayar seluruh cicilan tersisa
    # dan kemungkinan denda maksimal pada cicilan terakhir.
    maksimal_denda = (
        pinjaman.cicilan_tetap
        * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
    )

    saldo_dibutuhkan = (
        rekening.saldosetor_min
        + pinjaman.cicilan_tetap * sisa_cicilan
        + maksimal_denda
    )

    if rekening.saldo < saldo_dibutuhkan:
        rekening.tambah_saldo(
            saldo_dibutuhkan - rekening.saldo
        )

    print()
    print("=" * 60)
    print("PENGUJIAN PELUNASAN DENGAN DENDA")
    print(f"Pinjaman            : #{pinjaman.ID}")
    print(f"Tenor               : {pinjaman.tenor} bulan")
    print(
        "Cicilan terbayar    : "
        f"{pinjaman.cicilan_terbayar}"
    )
    print(
        "Cicilan tersisa     : "
        f"{sisa_cicilan}"
    )
    print(
        "Jatuh tempo awal    : "
        f"{pinjaman.tanggal_jatuh_tempo}"
    )
    print("=" * 60)

    # Bayar seluruh cicilan sebelum cicilan terakhir
    # tepat pada tanggal jatuh temponya.
    while (
        pinjaman.cicilan_terbayar
        < pinjaman.tenor - 1
    ):
        jatuh_tempo_sebelum = (
            pinjaman.tanggal_jatuh_tempo
        )

        cicilan_terbayar_sebelum = (
            pinjaman.cicilan_terbayar
        )

        PinjamanService.bayar_cicilan(
            bank,
            pinjaman,
            jatuh_tempo_sebelum
        )

        # Pastikan satu pembayaran hanya menyelesaikan
        # satu cicilan.
        assert (
            pinjaman.cicilan_terbayar
            == cicilan_terbayar_sebelum + 1
        ), "Jumlah cicilan terbayar tidak bertambah satu"

        # Pastikan jatuh tempo maju satu bulan dari
        # jadwal sebelumnya.
        jatuh_tempo_diharapkan = (
            Utilitas.tambah_bulan(
                jatuh_tempo_sebelum,
                1
            )
        )

        assert (
            pinjaman.tanggal_jatuh_tempo
            == jatuh_tempo_diharapkan
        ), "Jatuh tempo tidak maju sesuai jadwal"

        # Pastikan pinjaman belum lunas sebelum
        # pembayaran cicilan terakhir.
        assert (
            pinjaman.status == StatusPinjaman.AKTIF
        ), "Pinjaman lunas sebelum cicilan terakhir"

        print(
            f"Cicilan ke-{pinjaman.cicilan_terbayar} "
            f"dibayar pada {jatuh_tempo_sebelum}"
        )

    # Pastikan sekarang hanya tersisa satu cicilan.
    assert (
        pinjaman.cicilan_terbayar
        == pinjaman.tenor - 1
    ), "Pinjaman seharusnya menyisakan satu cicilan"

    # Tentukan pembayaran terakhir pada hari pertama
    # setelah masa toleransi berakhir.
    jatuh_tempo_terakhir = pinjaman.tanggal_jatuh_tempo

    hari_uji = (
        jatuh_tempo_terakhir
        + datetime.timedelta(
            days=(
                PinjamanService.BATAS_HARI_TUNGGAKAN
                + 1
            )
        )
    )

    # Hitung denda cicilan terakhir.
    hari_terlambat = (
        PinjamanService.hitung_hari_terlambat(
            pinjaman,
            hari_uji
        )
    )

    denda = PinjamanService.hitung_denda(
        pinjaman,
        hari_uji
    )

    denda_harian_diharapkan = round(
        pinjaman.cicilan_tetap
        * PinjamanService.PERSENTASE_DENDA_HARIAN
    )

    assert (
        hari_terlambat
        == PinjamanService.BATAS_HARI_TUNGGAKAN + 1
    ), "Jumlah hari keterlambatan tidak sesuai"

    assert denda == denda_harian_diharapkan, (
        "Denda cicilan terakhir tidak sesuai"
    )

    total_bayar = pinjaman.cicilan_tetap + denda

    # Simpan state sebelum pembayaran terakhir.
    saldo_sebelum = rekening.saldo
    riwayat_sebelum = len(rekening.riwayat)

    # Bayar cicilan terakhir beserta dendanya.
    PinjamanService.bayar_cicilan(
        bank,
        pinjaman,
        hari_uji
    )

    # Pastikan saldo dipotong sebesar cicilan dan denda.
    assert math.isclose(
        rekening.saldo,
        saldo_sebelum - total_bayar,
        rel_tol=1e-9
    ), "Pemotongan saldo pelunasan tidak sesuai"

    # Pastikan seluruh pokok telah dibayar.
    assert math.isclose(
        pinjaman.sisa_pokok,
        0,
        abs_tol=1e-6
    ), "Sisa pokok seharusnya nol"

    # Pastikan lifecycle pinjaman telah selesai.
    assert (
        pinjaman.status == StatusPinjaman.LUNAS
    ), "Status pinjaman seharusnya LUNAS"

    # Pastikan seluruh cicilan telah dibayar.
    assert (
        pinjaman.cicilan_terbayar
        == pinjaman.tenor
    ), "Jumlah cicilan terbayar seharusnya sama dengan tenor"

    # Pastikan riwayat pelunasan ditambahkan.
    assert (
        len(rekening.riwayat)
        == riwayat_sebelum + 1
    ), "Riwayat pelunasan belum ditambahkan"

    riwayat_terakhir = str(rekening.riwayat[-1])

    assert "PELUNASAN" in riwayat_terakhir.upper(), (
        "Riwayat terakhir belum mencatat pelunasan"
    )

    assert "DENDA" in riwayat_terakhir.upper(), (
        "Riwayat pelunasan belum mencatat denda"
    )

    # Pastikan referensi pinjaman aktif dibersihkan.
    assert nasabah.pinjaman is None, (
        "Referensi pinjaman aktif belum dibersihkan"
    )

    # Pastikan notifikasi pelunasan tersedia.
    notifikasi_pelunasan = [
        notifikasi
        for notifikasi in nasabah.notifikasi
        if (
            notifikasi.referensi_id
            == JenisReferensiID.PINJAMAN
            and "lunas" in notifikasi.pesan.lower()
        )
    ]

    assert notifikasi_pelunasan, (
        "Notifikasi pelunasan belum dibuat"
    )

    print()
    print("=" * 60)
    print("✅ Pelunasan dengan denda berhasil")
    print(f"Jatuh tempo terakhir : {jatuh_tempo_terakhir}")
    print(f"Tanggal pembayaran   : {hari_uji}")
    print(f"Hari terlambat       : {hari_terlambat}")
    print(
        "Cicilan terakhir    : "
        f"Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}"
    )
    print(
        "Denda               : "
        f"Rp{Utilitas.format_rupiah(denda)}"
    )
    print(
        "Total pembayaran    : "
        f"Rp{Utilitas.format_rupiah(round(total_bayar))}"
    )
    print(f"Status               : {pinjaman.status.value}")
    print(
        "Cicilan terbayar     : "
        f"{pinjaman.cicilan_terbayar}/{pinjaman.tenor}"
    )
    print("=" * 60)

 # -----------------------------------------------------------------------------------


def uji_mengejar_tiga_cicilan_tertunggak():
    """
    Menguji pembayaran tiga cicilan tertunggak pada tanggal
    # yang sama.
    #
Pengujian memastikan:
- Setiap pembayaran menyelesaikan satu cicilan.
- Denda dihitung ulang berdasarkan jatuh tempo aktif.
- Jatuh tempo maju satu bulan per pembayaran.
- Denda tidak mengurangi sisa pokok.
- Setelah tiga pembayaran, pinjaman kembali mengikuti jadwal.
"""

# Muat data baru agar pengujian tidak menggunakan
# perubahan dari pengujian sebelumnya.
bank = JsonStorage.muat_bank()

# Cari pinjaman aktif yang masih memiliki sedikitnya
# tiga cicilan tersisa.
pinjaman = next(
    (
        item
        for item in bank.daftar_pinjaman
        if (
            item.status == StatusPinjaman.AKTIF
            and (
                item.tenor - item.cicilan_terbayar
                >= 3
            )
        )
    ),
    None
)

if pinjaman is None:
    print(
        "Tidak ada pinjaman aktif dengan "
        "minimal tiga cicilan tersisa."
    )
    return

rekening = pinjaman.rekening
jatuh_tempo_awal = pinjaman.tanggal_jatuh_tempo

# Tentukan jatuh tempo periode ketiga.
jatuh_tempo_periode_ketiga = (
    Utilitas.tambah_bulan(
        Utilitas.tambah_bulan(
            jatuh_tempo_awal,
            1
        ),
        1
    )
)

# Pembayaran dilakukan tiga hari setelah jatuh tempo
# periode ketiga.
hari_uji = (
    jatuh_tempo_periode_ketiga
    + datetime.timedelta(days=3)
)

# Siapkan saldo yang cukup untuk tiga cicilan beserta
# kemungkinan denda maksimal.
maksimal_denda_per_cicilan = (
    pinjaman.cicilan_tetap
    * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
)

saldo_dibutuhkan = (
    rekening.saldosetor_min
    + (
        pinjaman.cicilan_tetap
        + maksimal_denda_per_cicilan
    ) * 3
)

if rekening.saldo < saldo_dibutuhkan:
    rekening.tambah_saldo(
        saldo_dibutuhkan - rekening.saldo
    )

# Jalankan scheduler untuk menghasilkan kondisi tunggakan
# pada tanggal pengujian.
Scheduler.jalankan(bank, hari_uji)

saldo_awal = rekening.saldo
cicilan_terbayar_awal = pinjaman.cicilan_terbayar
total_seluruh_pembayaran = 0

print()
print("=" * 60)
print("PENGUJIAN PEMBAYARAN CICILAN TERTUNGGAK")
print(f"Jatuh tempo awal : {jatuh_tempo_awal}")
print(f"Tanggal pembayaran: {hari_uji}")
print("=" * 60)

# Bayar tiga cicilan secara berurutan pada tanggal yang sama.
for urutan in range(1, 4):
    jatuh_tempo_sebelum = pinjaman.tanggal_jatuh_tempo
    saldo_sebelum = rekening.saldo
    sisa_pokok_sebelum = pinjaman.sisa_pokok
    cicilan_sebelum = pinjaman.cicilan_terbayar

    # Hitung kondisi cicilan yang sedang dibayar.
    hari_terlambat = (
        PinjamanService.hitung_hari_terlambat(
            pinjaman,
            hari_uji
        )
    )

    denda = PinjamanService.hitung_denda(
        pinjaman,
        hari_uji
    )

    total_bayar = pinjaman.cicilan_tetap + denda

    # Hitung perubahan pokok yang diharapkan.
    persentase_bunga = pinjaman.bunga / 12

    bunga_bulanan = (
        sisa_pokok_sebelum
        * persentase_bunga
    )

    pokok_dibayar = (
        pinjaman.cicilan_tetap
        - bunga_bulanan
    )

    sisa_pokok_diharapkan = max(
        0,
        sisa_pokok_sebelum - pokok_dibayar
    )

    # Proses satu pembayaran cicilan.
    PinjamanService.bayar_cicilan(
        bank,
        pinjaman,
        hari_uji
    )

    total_seluruh_pembayaran += total_bayar

    # Pastikan saldo dipotong sebesar cicilan dan denda.
    assert math.isclose(
        rekening.saldo,
        saldo_sebelum - total_bayar,
        rel_tol=1e-9
    ), (
        f"Pemotongan saldo pembayaran ke-{urutan} "
        "tidak sesuai"
    )

    # Pastikan denda tidak mengurangi sisa pokok.
    assert math.isclose(
        pinjaman.sisa_pokok,
        sisa_pokok_diharapkan,
        rel_tol=1e-9
    ), (
        f"Perubahan pokok pembayaran ke-{urutan} "
        "tidak sesuai"
    )

    # Pastikan jumlah cicilan terbayar bertambah satu.
    assert (
        pinjaman.cicilan_terbayar
        == cicilan_sebelum + 1
    ), (
        f"Cicilan terbayar pada pembayaran "
        f"ke-{urutan} tidak bertambah"
    )

    # Pastikan jatuh tempo maju dari jadwal sebelumnya.
    if pinjaman.status == StatusPinjaman.AKTIF:
        jatuh_tempo_diharapkan = (
            Utilitas.tambah_bulan(
                jatuh_tempo_sebelum,
                1
            )
        )

        assert (
            pinjaman.tanggal_jatuh_tempo
            == jatuh_tempo_diharapkan
        ), (
            f"Jatuh tempo setelah pembayaran "
            f"ke-{urutan} tidak sesuai"
        )

    print()
    print(f"Pembayaran ke-{urutan}")
    print(f"  Cicilan untuk jatuh tempo : {jatuh_tempo_sebelum}")
    print(f"  Hari terlambat            : {hari_terlambat}")
    print(
        "  Denda                     : "
        f"Rp{Utilitas.format_rupiah(denda)}"
    )
    print(
        "  Total pembayaran          : "
        f"Rp{Utilitas.format_rupiah(round(total_bayar))}"
    )
    print(
        "  Jatuh tempo berikutnya    : "
        f"{pinjaman.tanggal_jatuh_tempo}"
    )

# Pastikan tiga pembayaran telah tercatat.
assert (
    pinjaman.cicilan_terbayar
    == cicilan_terbayar_awal + 3
), "Jumlah seluruh cicilan terbayar tidak sesuai"

# Pastikan jumlah seluruh potongan saldo sesuai.
assert math.isclose(
    rekening.saldo,
    saldo_awal - total_seluruh_pembayaran,
    rel_tol=1e-9
), "Total pemotongan saldo tidak sesuai"

# Setelah tiga pembayaran, jatuh tempo harus berada
# satu periode setelah tanggal pengujian.
jatuh_tempo_akhir_diharapkan = (
    Utilitas.tambah_bulan(
        jatuh_tempo_periode_ketiga,
        1
    )
)

assert (
    pinjaman.tanggal_jatuh_tempo
    == jatuh_tempo_akhir_diharapkan
), "Pinjaman belum kembali ke jadwal yang benar"

# Pastikan cicilan berikutnya tidak lagi terlambat.
hari_terlambat_akhir = (
    PinjamanService.hitung_hari_terlambat(
        pinjaman,
        hari_uji
    )
)

assert hari_terlambat_akhir == 0, (
    "Pinjaman seharusnya sudah kembali mengikuti jadwal"
)

print()
print("=" * 60)
print("✅ Tiga cicilan tertunggak berhasil dikejar")
print(
    "Total pembayaran: "
    f"Rp{Utilitas.format_rupiah(round(total_seluruh_pembayaran))}"
)
print(
    "Jatuh tempo akhir: "
    f"{pinjaman.tanggal_jatuh_tempo}"
)
print("=" * 60)


# --------------------------------------------------
def uji_pembayaran_denda_saldo_tidak_cukup():
    """
    Memastikan kegagalan pembayaran tidak mengubah state
    rekening maupun pinjaman.
    """

    bank = JsonStorage.muat_bank()

    pinjaman = next(
        (
            item
            for item in bank.daftar_pinjaman
            if item.status == StatusPinjaman.AKTIF
        ),
        None
    )

    if pinjaman is None:
        print("Tidak ada pinjaman aktif untuk diuji.")
        return

    rekening = pinjaman.rekening

    hari_uji = (
        pinjaman.tanggal_jatuh_tempo
        + datetime.timedelta(
            days=(
                PinjamanService.BATAS_HARI_TUNGGAKAN
                + 1
            )
        )
    )

    # Buat saldo tidak cukup untuk membayar cicilan dan denda.
    rekening.set_saldo(rekening.saldosetor_min)

    # Simpan state sebelum percobaan pembayaran.
    saldo_sebelum = rekening.saldo
    sisa_pokok_sebelum = pinjaman.sisa_pokok
    cicilan_terbayar_sebelum = pinjaman.cicilan_terbayar
    jatuh_tempo_sebelum = pinjaman.tanggal_jatuh_tempo

    try:
        PinjamanService.bayar_cicilan(
            bank,
            pinjaman,
            hari_uji
        )

        assert False, (
            "Pembayaran seharusnya ditolak karena saldo tidak cukup"
        )

    except ValueError as error:
        print("Pembayaran ditolak:", error)

    # Pastikan seluruh state keuangan tetap sama.
    assert rekening.saldo == saldo_sebelum
    assert pinjaman.sisa_pokok == sisa_pokok_sebelum
    assert (
        pinjaman.cicilan_terbayar
        == cicilan_terbayar_sebelum
    )
    assert (
        pinjaman.tanggal_jatuh_tempo
        == jatuh_tempo_sebelum
    )

    print("✅ Kegagalan pembayaran tidak mengubah state")


--------------------------------------------------------------------------
def uji_pembayaran_dengan_denda():
    """
    Menguji pembayaran cicilan pada hari pertama denda.

    Pengujian memastikan:
    - Denda ikut dipotong dari saldo.
    - Denda tidak mengurangi sisa pokok.
    - Cicilan terbayar bertambah.
    - Jatuh tempo maju dari tanggal sebelumnya.
    - Notifikasi tunggakan dihapus.
    """

    # Muat data baru agar pengujian tidak dipengaruhi
    # oleh skenario sebelumnya.
    bank = JsonStorage.muat_bank()

    # Ambil satu pinjaman yang masih aktif.
    pinjaman = next(
        (
            item
            for item in bank.daftar_pinjaman
            if item.status == StatusPinjaman.AKTIF
        ),
        None
    )

    if pinjaman is None:
        print("Tidak ada pinjaman aktif untuk diuji.")
        return

    rekening = pinjaman.rekening
    jatuh_tempo_lama = pinjaman.tanggal_jatuh_tempo

    # Gunakan H+8 sebagai hari pertama pengenaan denda.
    hari_uji = (
        jatuh_tempo_lama
        + datetime.timedelta(
            days=(
                PinjamanService.BATAS_HARI_TUNGGAKAN
                + 1
            )
        )
    )

    # Jalankan scheduler untuk membuat notifikasi tunggakan.
    Scheduler.jalankan(bank, hari_uji)

    # Hitung denda dan total pembayaran yang diharapkan.
    denda = PinjamanService.hitung_denda(
        pinjaman,
        hari_uji
    )

    total_bayar = pinjaman.cicilan_tetap + denda

    # Pastikan saldo pengujian mencukupi.
    saldo_minimal_dibutuhkan = (
        total_bayar
        + rekening.saldosetor_min
    )

    if rekening.saldo < saldo_minimal_dibutuhkan:
        tambahan_saldo = (
            saldo_minimal_dibutuhkan
            - rekening.saldo
        )

        rekening.tambah_saldo(tambahan_saldo)

    # Simpan state sebelum pembayaran.
    saldo_sebelum = rekening.saldo
    sisa_pokok_sebelum = pinjaman.sisa_pokok
    cicilan_terbayar_sebelum = pinjaman.cicilan_terbayar

    # Hitung perubahan pokok yang diharapkan.
    persentase_bunga = pinjaman.bunga / 12

    bunga_bulanan = (
        sisa_pokok_sebelum
        * persentase_bunga
    )

    pokok_dibayar = (
        pinjaman.cicilan_tetap
        - bunga_bulanan
    )

    sisa_pokok_diharapkan = max(
        0,
        sisa_pokok_sebelum - pokok_dibayar
    )

    # Proses pembayaran pada tanggal simulasi.
    PinjamanService.bayar_cicilan(
        bank,
        pinjaman,
        hari_uji
    )

    # Pastikan saldo dipotong sebesar cicilan dan denda.
    saldo_diharapkan = saldo_sebelum - total_bayar

    assert math.isclose(
        rekening.saldo,
        saldo_diharapkan,
        rel_tol=1e-9
    ), "Pemotongan saldo tidak sesuai"

    # Pastikan denda tidak mengurangi pokok pinjaman.
    assert math.isclose(
        pinjaman.sisa_pokok,
        sisa_pokok_diharapkan,
        rel_tol=1e-9
    ), "Perubahan sisa pokok tidak sesuai"

    # Pastikan jumlah cicilan terbayar bertambah satu.
    assert (
        pinjaman.cicilan_terbayar
        == cicilan_terbayar_sebelum + 1
    ), "Jumlah cicilan terbayar tidak bertambah"

    # Periksa jatuh tempo jika pinjaman belum lunas.
    if pinjaman.status == StatusPinjaman.AKTIF:
        jatuh_tempo_diharapkan = Utilitas.tambah_bulan(
            jatuh_tempo_lama,
            1
        )

        assert (
            pinjaman.tanggal_jatuh_tempo
            == jatuh_tempo_diharapkan
        ), "Jatuh tempo berikutnya tidak sesuai"

    # Pastikan notifikasi tunggakan sudah dihapus.
    notifikasi_tunggakan = [
        notifikasi
        for notifikasi in pinjaman.pemilik.notifikasi
        if (
            notifikasi.referensi_id
            == JenisReferensiID.PINJAMAN
            and notifikasi.id_objek == pinjaman.ID
            and "terlambat" in notifikasi.pesan.lower()
        )
    ]

    assert not notifikasi_tunggakan, (
        "Notifikasi tunggakan belum dihapus"
    )

    print()
    print("✅ Pembayaran dengan denda berhasil")
    print(
        "Saldo dipotong      : "
        f"Rp{Utilitas.format_rupiah(round(total_bayar))}"
    )
    print(
        "Cicilan            : "
        f"Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}"
    )
    print(
        "Denda              : "
        f"Rp{Utilitas.format_rupiah(denda)}"
    )
    print(
        "Sisa pokok         : "
        f"Rp{Utilitas.format_rupiah(round(pinjaman.sisa_pokok))}"
    )
    print(
        "Jatuh tempo berikut: "
        f"{pinjaman.tanggal_jatuh_tempo}"
    )

-----------------------------------------------------------------------------


def uji_notifikasi_tunggakan():
    """
    Menguji notifikasi dan perhitungan denda pada beberapa
    tanggal relatif terhadap jatuh tempo pinjaman.

    Data dimuat ulang untuk setiap skenario agar perubahan
    dari satu pengujian tidak memengaruhi pengujian berikutnya.
    """

    # Muat data awal untuk mendapatkan tanggal jatuh tempo.
    bank_awal = JsonStorage.muat_bank()

    pinjaman_awal = next(
        (
            pinjaman
            for pinjaman in bank_awal.daftar_pinjaman
            if pinjaman.status == StatusPinjaman.AKTIF
        ),
        None
    )

    if pinjaman_awal is None:
        print("Tidak ada pinjaman aktif untuk diuji.")
        return

    jatuh_tempo = pinjaman_awal.tanggal_jatuh_tempo
    batas = PinjamanService.BATAS_HARI_TUNGGAKAN

    # Tentukan tanggal-tanggal penting dalam lifecycle tunggakan.
    skenario = [
        (
            "Sehari sebelum jatuh tempo",
            jatuh_tempo - datetime.timedelta(days=1)
        ),
        (
            "Tepat pada jatuh tempo",
            jatuh_tempo
        ),
        (
            "Hari pertama tunggakan",
            jatuh_tempo + datetime.timedelta(days=1)
        ),
        (
            "Hari terakhir masa toleransi",
            jatuh_tempo + datetime.timedelta(days=batas)
        ),
        (
            "Hari pertama denda",
            jatuh_tempo + datetime.timedelta(days=batas + 1)
        ),
        (
            "Tiga hari terkena denda",
            jatuh_tempo + datetime.timedelta(days=batas + 3)
        )
    ]

    for nama_skenario, hari_uji in skenario:
        # Muat ulang data agar setiap skenario dimulai
        # dari state yang sama.
        bank = JsonStorage.muat_bank()

        pinjaman = next(
            (
                item
                for item in bank.daftar_pinjaman
                if item.status == StatusPinjaman.AKTIF
            ),
            None
        )

        if pinjaman is None:
            print("Pinjaman aktif tidak ditemukan.")
            return

        # Jalankan seluruh proses scheduler pada tanggal simulasi.
        Scheduler.jalankan(bank, hari_uji)

        # Hitung hasil yang perlu diverifikasi.
        hari_terlambat = (
            PinjamanService.hitung_hari_terlambat(
                pinjaman,
                hari_uji
            )
        )

        denda = PinjamanService.hitung_denda(
            pinjaman,
            hari_uji
        )

        # Cari notifikasi pinjaman yang dihasilkan scheduler.
        notifikasi_pinjaman = [
            notifikasi
            for notifikasi in pinjaman.pemilik.notifikasi
            if (
                notifikasi.referensi_id
                == JenisReferensiID.PINJAMAN
            )
        ]

        print()
        print("=" * 60)
        print(f"Skenario        : {nama_skenario}")
        print(f"Jatuh tempo     : {jatuh_tempo}")
        print(f"Tanggal simulasi: {hari_uji}")
        print(f"Hari terlambat  : {hari_terlambat}")
        print(
            "Denda            : "
            f"Rp{Utilitas.format_rupiah(denda)}"
        )

        if notifikasi_pinjaman:
            print(
                "Notifikasi       : "
                f"{notifikasi_pinjaman[-1].pesan}"
            )
        else:
            print("Notifikasi       : Tidak ada")


---------------------------------------------------------------


# def uji_pembulatan_cicilan_terakhir(bank):
#     # Mengambil satu-satunya pinjaman aktif.
#     pinjaman = next(
#         (
#             item
#             for item in bank.daftar_pinjaman
#             if item.status == StatusPinjaman.AKTIF
#         ),
#         None
#     )
#
#     assert pinjaman is not None, (
#         "Tidak ditemukan pinjaman aktif"
#     )
#
#     assert pinjaman.cicilan_terbayar == 1, (
#         "Pengujian mengharapkan satu cicilan sudah dibayar"
#     )
#
#     # Menyiapkan saldo agar seluruh cicilan simulasi dapat dibayar.
#     pinjaman.rekening.set_saldo(100_000_000)
#
#     print("KONDISI AWAL")
#     print("ID pinjaman      :", pinjaman.ID)
#     print("Tenor            :", pinjaman.tenor)
#     print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
#     print("Cicilan tersisa  :", (
#         pinjaman.tenor - pinjaman.cicilan_terbayar
#     ))
#     print("Cicilan tetap    :", pinjaman.cicilan_tetap)
#     print("Sisa pokok       :", pinjaman.sisa_pokok)
#     print()
#
#     # Membayar cicilan normal sampai tersisa satu cicilan.
#     while pinjaman.cicilan_terbayar < pinjaman.tenor - 1:
#         nomor_cicilan = pinjaman.cicilan_terbayar + 1
#         hari_bayar = pinjaman.tanggal_jatuh_tempo
#
#         PinjamanService.bayar_cicilan(
#             bank,
#             pinjaman,
#             hari_ini=hari_bayar
#         )
#
#         print(
#             f"Cicilan ke-{nomor_cicilan} dibayar pada "
#             f"{hari_bayar} | "
#             f"Sisa pokok: Rp"
#             f"{Utilitas.format_rupiah(pinjaman.sisa_pokok)}"
#         )
#
#     assert pinjaman.cicilan_terbayar == pinjaman.tenor - 1
#     assert pinjaman.status == StatusPinjaman.AKTIF
#
#     # Menghitung komponen cicilan terakhir menurut rumus normal.
#     persentase_bunga = pinjaman.bunga / 12
#
#     bunga_terakhir = round(
#         pinjaman.sisa_pokok * persentase_bunga
#     )
#
#     pokok_normal = (
#         pinjaman.cicilan_tetap - bunga_terakhir
#     )
#
#     sisa_pokok_sebelum = pinjaman.sisa_pokok
#
#     # Pembayaran yang tepat untuk melunasi seluruh sisa pokok.
#     cicilan_terakhir_tepat = (
#         sisa_pokok_sebelum + bunga_terakhir
#     )
#
#     # Selisih antara cicilan tetap dan kebutuhan sebenarnya.
#     selisih_pembayaran = (
#         pinjaman.cicilan_tetap
#         - cicilan_terakhir_tepat
#     )
#
#     print()
#     print("SEBELUM CICILAN TERAKHIR")
#     print("Sisa pokok             :", sisa_pokok_sebelum)
#     print("Bunga terakhir         :", bunga_terakhir)
#     print("Pokok menurut cicilan  :", pokok_normal)
#     print("Cicilan tetap          :", pinjaman.cicilan_tetap)
#     print("Cicilan yang tepat     :", cicilan_terakhir_tepat)
#     print("Selisih pembayaran     :", selisih_pembayaran)
#
#     saldo_sebelum = pinjaman.rekening.saldo
#     hari_pelunasan = pinjaman.tanggal_jatuh_tempo
#
#     # Membayar cicilan terakhir menggunakan implementasi saat ini.
#     PinjamanService.bayar_cicilan(
#         bank,
#         pinjaman,
#         hari_ini=hari_pelunasan
#     )
#
#     saldo_setelah = pinjaman.rekening.saldo
#     saldo_terpotong = saldo_sebelum - saldo_setelah
#
#     print()
#     print("SETELAH CICILAN TERAKHIR")
#     print("Tanggal pelunasan :", hari_pelunasan)
#     print("Saldo terpotong   :", saldo_terpotong)
#     print("Sisa pokok        :", pinjaman.sisa_pokok)
#     print("Status            :", pinjaman.status.value)
#     print(
#         "Cicilan terbayar :",
#         f"{pinjaman.cicilan_terbayar}/{pinjaman.tenor}"
#     )
#
#     assert pinjaman.status == StatusPinjaman.LUNAS
#     assert pinjaman.sisa_pokok == 0
#     assert pinjaman.cicilan_terbayar == pinjaman.tenor
#
#     if selisih_pembayaran > 0:
#         print(
#             f"⚠ Nasabah membayar lebih "
#             f"Rp{Utilitas.format_rupiah(selisih_pembayaran)}"
#         )
#     elif selisih_pembayaran < 0:
#         print(
#             f"⚠ Terdapat kekurangan pembayaran "
#             f"Rp{Utilitas.format_rupiah(abs(selisih_pembayaran))}"
#         )
#     else:
#         print("✅ Cicilan tetap tepat melunasi sisa pinjaman")
#
#     print("✅ Simulasi pinjaman hingga akhir berhasil")
#
#
# bank = JsonStorage.muat_bank()
#
#
# if __name__=="__main__":
#     uji_pembulatan_cicilan_terakhir(bank)





--------------------------------------------------------------
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

if __name__ = "__main__":
    siapkan_dua_pinjaman_untuk_uji()
nasabah_uji, pinjaman_lunas, pinjaman_aktif = (
    siapkan_dua_pinjaman_untuk_uji(bank)


---------------------------------------------------------------
def uji_save_load_dua_pinjaman(
    bank,
    nasabah,
    pinjaman_lunas,
    pinjaman_aktif
):
    nik = nasabah.NIK

    lokasi_asli = {
        "rekening": JsonStorage.file_rek,
        "nasabah": JsonStorage.file_nasabah,
        "audit": JsonStorage.file_audit,
        "deposito": JsonStorage.file_depo,
        "pinjaman": JsonStorage.file_pinjaman
    }

    try:
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

            # Menyimpan seluruh Bank ke JSON sementara.
            JsonStorage.simpan_bank(bank)

            data_pinjaman_json = JsonStorage.muat_json(
                JsonStorage.file_pinjaman,
                {}
            )

            # Memastikan NIK menjadi key utama.
            assert nik in data_pinjaman_json, (
                "NIK nasabah tidak ditemukan dalam pinjaman.json"
            )

            pinjaman_milik_nasabah = data_pinjaman_json[nik]

            # Memastikan ID menjadi key cabang.
            assert str(pinjaman_lunas.ID) in pinjaman_milik_nasabah, (
                "Pinjaman lunas tidak tersimpan berdasarkan ID"
            )

            assert str(pinjaman_aktif.ID) in pinjaman_milik_nasabah, (
                "Pinjaman aktif tidak tersimpan berdasarkan ID"
            )

            assert len(pinjaman_milik_nasabah) == 2, (
                "Jumlah pinjaman dalam JSON tidak sesuai"
            )

            print("STRUKTUR JSON")
            print("NIK               :", nik)
            print(
                "ID yang tersimpan :",
                list(pinjaman_milik_nasabah.keys())
            )

            # Memuat JSON menjadi objek Bank baru.
            bank_hasil_load = JsonStorage.muat_bank()
            nasabah_hasil_load = (
                bank_hasil_load.data_nasabah[nik]
            )

            daftar_hasil_load = [
                pinjaman
                for pinjaman in bank_hasil_load.daftar_pinjaman
                if pinjaman.pemilik is nasabah_hasil_load
            ]

            assert len(daftar_hasil_load) == 2, (
                "Tidak semua pinjaman dimuat ke daftar Bank"
            )

            pinjaman_lunas_hasil = next(
                pinjaman
                for pinjaman in daftar_hasil_load
                if pinjaman.ID == pinjaman_lunas.ID
            )

            pinjaman_aktif_hasil = next(
                pinjaman
                for pinjaman in daftar_hasil_load
                if pinjaman.ID == pinjaman_aktif.ID
            )

            assert (
                pinjaman_lunas_hasil.status
                == StatusPinjaman.LUNAS
            ), "Status pinjaman lama berubah setelah load"

            assert (
                pinjaman_aktif_hasil.status
                == StatusPinjaman.AKTIF
            ), "Status pinjaman baru berubah setelah load"

            # Nasabah hanya menunjuk pinjaman berjalan.
            assert (
                nasabah_hasil_load.pinjaman
                is pinjaman_aktif_hasil
            ), (
                "Nasabah tidak menunjuk pinjaman aktif "
                "hasil load"
            )

            assert (
                nasabah_hasil_load.pinjaman
                is not pinjaman_lunas_hasil
            ), (
                "Nasabah masih menunjuk pinjaman yang lunas"
            )

            # Kedua pinjaman harus menunjuk nasabah hasil load.
            assert (
                pinjaman_lunas_hasil.pemilik
                is nasabah_hasil_load
            )

            assert (
                pinjaman_aktif_hasil.pemilik
                is nasabah_hasil_load
            )

            # Kedua pinjaman harus menggunakan objek rekening Bank.
            assert (
                pinjaman_lunas_hasil.rekening
                is bank_hasil_load.rekening_index[
                    pinjaman_lunas_hasil.rekening.norek
                ]
            )

            assert (
                pinjaman_aktif_hasil.rekening
                is bank_hasil_load.rekening_index[
                    pinjaman_aktif_hasil.rekening.norek
                ]
            )

            assert nasabah_hasil_load.jumlah_pinjaman == 2, (
                "Penghitung jumlah pinjaman tidak dipulihkan"
            )

            print()
            print("SETELAH LOAD")

            for pinjaman in daftar_hasil_load:
                print(
                    f"- Pinjaman #{pinjaman.ID} | "
                    f"Status: {pinjaman.status.value} | "
                    f"Objek: {id(pinjaman)}"
                )

            print(
                "Pinjaman aktif nasabah:",
                nasabah_hasil_load.pinjaman.ID
            )
            print(
                "Jumlah pinjaman nasabah:",
                nasabah_hasil_load.jumlah_pinjaman
            )
            print()
            print(
                "✅ Save/load dua pinjaman berhasil"
            )

    finally:
        JsonStorage.file_rek = lokasi_asli["rekening"]
        JsonStorage.file_nasabah = lokasi_asli["nasabah"]
        JsonStorage.file_audit = lokasi_asli["audit"]
        JsonStorage.file_depo = lokasi_asli["deposito"]
        JsonStorage.file_pinjaman = lokasi_asli["pinjaman"]


uji_save_load_dua_pinjaman(
    bank,
    nasabah_uji,
    pinjaman_lunas,
    pinjaman_aktif



----------------------------------------------------------------
jatuh_tempo = pinjaman.tanggal_jatuh_tempo
batas = PinjamanService.BATAS_HARI_TUNGGAKAN
# percobaan hari terakhir toleransi
hari_uji = (jatuh_tempo + timedelta(days=batas))
denda = PinjamanService.hitung_denda(pinjaman, hari_uji)
assert denda == 0, (
    "Hari terakhir masa toleransi seharusnya belum didenda"
)
print("✅Hari terakhir toleransi")

hari_uji = (jatuh_tempo + timedelta(days=batas + 1))
denda = PinjamanService.hitung_denda(pinjaman, hari_uji)
denda_harian = round(
    pinjaman.cicilan_tetap
    * PinjamanService.PERSENTASE_DENDA_HARIAN
)

assert denda == denda_harian, (
    "Denda hari pertama tidak sesuai"
)

print("✅ Denda hari pertama valid")

hari_uji = (
        jatuh_tempo
        + datetime.timedelta(days=1000)
)

denda = PinjamanService.hitung_denda(
    pinjaman,
    hari_uji
)

maksimal_denda = round(
    pinjaman.cicilan_tetap
    * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
)

assert denda == maksimal_denda, (
    "Denda seharusnya berhenti pada batas maksimal"
)

print("✅ Batas maksimal denda valid")

------------------------------------------
pinjaman = next((item for item in bank.daftar_pinjaman if item.status == StatusPinjaman.AKTIF), None)
if pinjaman is not None:
    hari_uji = (
            pinjaman.tanggal_jatuh_tempo
            + datetime.timedelta(days=1)
    )

    hari_terlambat = (
        PinjamanService.perbarui_status_pembayaran(
            pinjaman,
            hari_uji
        )
    )

    print("Jatuh tempo       :", pinjaman.tanggal_jatuh_tempo)
    print("Tanggal pengujian :", hari_uji)
    print("Hari terlambat    :", hari_terlambat)
    print("Status pembayaran :", pinjaman.status_pembayaran.value)

    assert hari_terlambat == 1, (
        "Keterlambatan seharusnya satu hari"
    )

    assert (
            pinjaman.status_pembayaran
            == StatusPembayaran.MENUNGGAK
    ), "Status seharusnya MENUNGGAK"

    print("✅ Pengujian keterlambatan berhasil")


nasabah = bank.data_nasabah["3510152602082002"]
pinjaman = nasabah.pinjaman
# PinjamanService.cairkan_pinjaman(bank,pinjaman,datetime.date(2027,1,31))
PinjamanService.bayar_cicilan(
    bank,
    pinjaman,
    datetime.date(2027, 2, 20)
)

print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
print("Jatuh tempo baru :", pinjaman.tanggal_jatuh_tempo)
print(
    "Boleh bayar lagi :",
    PinjamanService.tanggal_boleh_bayar(pinjaman)
)


print("Tanggal pencairan :", pinjaman.tanggal_pencairan)
print("Jatuh tempo       :", pinjaman.tanggal_jatuh_tempo)

PinjamanService.bayar_cicilan(
    bank,
    pinjaman,
    datetime.date(2027, 3, 1)
)

print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
print("Jatuh tempo baru :", pinjaman.tanggal_jatuh_tempo)
print(
    "Boleh bayar lagi :",
    PinjamanService.tanggal_boleh_bayar(pinjaman))

hari_ini = datetime.date(2026,9,18)
# Scheduler.jalankan(bank,hari_ini)
#
# hari_ini = datetime.date(2026, 9, 18)
# Scheduler.jalankan(bank, hari_ini
nasabah = bank.data_nasabah["3150152602002002"]
pinjaman = nasabah.pinjaman
# PinjamanService.bayar_cicilan(bank,pinjaman,hari_ini)
#
tanggal_test = [
    datetime.date(2026, 9, 5),  # cicilan 1
    datetime.date(2026, 9, 18),  # cicilan 2
    datetime.date(2026, 10, 18),  # cicilan 3
    datetime.date(2026, 11, 18),  # cicilan 4
    datetime.date(2026, 12, 18),  # cicilan 5
    datetime.date(2027, 1, 18),  # cicilan 6
]

for tanggal in tanggal_test:
    PinjamanService.bayar_cicilan(
        bank,
        pinjaman,
        tanggal
    )

    print(
        tanggal,
        pinjaman.cicilan_terbayar,
        pinjaman.sisa_pokok,
        pinjaman.status
    )
PinjamanService.bayar_cicilan(bank,pinjaman,datetime.date(2027,2,18))



---------------------------------------------------------------------------


# def uji_serialisasi_integer_pinjaman(bank):
#     data_pinjaman = JsonStorage.buat_data_pinjaman(bank)
#
#     for nik, daftar_pinjaman in data_pinjaman.items():
#         for id_pinjaman, data in daftar_pinjaman.items():
#             assert isinstance(data["nominal_pinjaman"], int)
#             assert isinstance(data["cicilan_tetap"], int)
#             assert isinstance(data["sisa_pokok"], int)
#             assert isinstance(data["bunga_bulanan"], int)
#
#             print(
#                 f"✅ Pinjaman {id_pinjaman} milik {nik} "
#                 f"siap disimpan sebagai integer"
#             )
#
# bank = JsonStorage.muat_bank()
#
#
#
# if __name__=="__main__":
#     uji_integer_pembayaran_pinjaman(bank)
#     uji_serialisasi_integer_pinjaman(bank)


-------------------------------------------------------------------------
# def uji_integer_pembayaran_pinjaman(bank):
#     # Mengambil satu pinjaman aktif yang belum memasuki cicilan terakhir.
#     pinjaman = next(
#         (
#             item
#             for item in bank.daftar_pinjaman
#             if item.status == StatusPinjaman.AKTIF
#             and item.cicilan_terbayar < item.tenor - 1
#         ),
#         None
#     )
#
#     assert pinjaman is not None, (
#         "Tidak ditemukan pinjaman aktif untuk pengujian"
#     )
#
#     # Menggunakan hari kedelapan setelah jatuh tempo agar denda
#     # telah berjalan selama satu hari setelah masa toleransi.
#     hari_uji = (
#         pinjaman.tanggal_jatuh_tempo
#         + datetime.timedelta(
#             days=PinjamanService.BATAS_HARI_TUNGGAKAN + 1
#         )
#     )
#
#     # Menyiapkan saldo agar pembayaran dapat dilakukan.
#     pinjaman.rekening.set_saldo(100_000_000)
#
#     # Menghitung nilai yang juga akan digunakan oleh service.
#     denda = PinjamanService.hitung_denda(
#         pinjaman,
#         hari_uji
#     )
#
#     total_bayar = pinjaman.cicilan_tetap + denda
#     saldo_sebelum = pinjaman.rekening.saldo
#
#     print("Sebelum pembayaran:")
#     print("Cicilan tetap :", pinjaman.cicilan_tetap)
#     print("Sisa pokok    :", pinjaman.sisa_pokok)
#     print("Bunga bulanan :", pinjaman.bunga_bulanan)
#     print("Denda         :", denda)
#     print("Total bayar   :", total_bayar)
#
#     # Memastikan seluruh nominal pembayaran sudah berupa integer.
#     assert isinstance(pinjaman.cicilan_tetap, int)
#     assert isinstance(pinjaman.sisa_pokok, int)
#     assert isinstance(pinjaman.bunga_bulanan, int)
#     assert isinstance(denda, int)
#     assert isinstance(total_bayar, int)
#
#     PinjamanService.bayar_cicilan(
#         bank,
#         pinjaman,
#         hari_ini=hari_uji
#     )
#
#     saldo_setelah = pinjaman.rekening.saldo
#     saldo_terpotong = saldo_sebelum - saldo_setelah
#
#     # Membuktikan service memotong cicilan dan denda yang sama.
#     assert saldo_terpotong == total_bayar
#
#     # Memastikan hasil perhitungan cicilan tetap berupa integer.
#     assert isinstance(pinjaman.sisa_pokok, int)
#     assert isinstance(pinjaman.bunga_bulanan, int)
#     assert isinstance(pinjaman.rekening.saldo, int)
#
#     print("\nSetelah pembayaran:")
#     print("Saldo terpotong:", saldo_terpotong)
#     print("Sisa pokok     :", pinjaman.sisa_pokok)
#     print("Bunga bulanan  :", pinjaman.bunga_bulanan)
#     print("✅ Seluruh nominal pinjaman sudah berupa integer")