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
            f"Deposito #{deposito.ID} masih menunjuk rekening Platinum"
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
            f"Deposito #{deposito.ID} masih menunjuk rekening lama"
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

- ----------------------------------------------------------------



from bank_djago.penyimpanan.storage import JsonStorage
from bank_djago.utils.utility import Utilitas


def uji_save_load_waktu_bunga(bank):
    rekening = next(iter(bank.rekening_index.values()))

    # Menyimpan tanggal asli agar dataset dapat dikembalikan.
    tanggal_asli = rekening.dapat_bunga

    print("Sebelum debug :", rekening.dapat_bunga)

    Utilitas.debug_bunga(bank, 6)

    tanggal_debug = rekening.dapat_bunga
    print("Setelah debug :", tanggal_debug)

    # Menyimpan rekening tanpa menjalankan scheduler.
    JsonStorage.simpan_bank(bank)

    # Memuat bank baru dari data yang baru disimpan.
    bank_baru = JsonStorage.muat_bank()
    rekening_baru = bank_baru.cari_rekening(rekening.norek)

    print("Setelah load  :", rekening_baru.dapat_bunga)

    assert rekening_baru.dapat_bunga == tanggal_debug, (
        "Tanggal bunga berubah setelah save/load"
    )

    print("✅ Save/load waktu bunga berhasil")

    # Mengembalikan tanggal asli agar dataset pengujian tidak tertinggal.
    rekening_baru.dapat_bunga = tanggal_asli
    JsonStorage.simpan_bank(bank_baru)

------------------------------------------------------








-----------------------------------------------------------------------------------
import datetime

from bank_djago.services.scheduler import Scheduler


def uji_scheduler_rekening_dua_kali(bank):
    # Mengambil satu rekening untuk pengujian.
    rekening = next(iter(bank.rekening_index.values()))

    hari_uji = datetime.date(2026, 10, 23)

    # Menyiapkan keadaan agar bunga dan biaya admin sudah jatuh tempo.
    rekening.dapat_bunga = datetime.date(2026, 9, 23)
    rekening.waktu_bayar_admin = datetime.date(2026, 9, 23)

    # Reset limit belum dilakukan pada hari pengujian.
    rekening.reset = datetime.date(2026, 10, 22)
    rekening.limit_sisa = 1

    # Memastikan saldo cukup untuk menerima bunga dan membayar admin.
    rekening.set_saldo(100_000_000)

    print("SEBELUM SCHEDULER")
    print("Saldo             :", rekening.saldo)
    print("Dapat bunga       :", rekening.dapat_bunga)
    print("Bayar admin       :", rekening.waktu_bayar_admin)
    print("Reset limit       :", rekening.reset)
    print("Limit tersisa     :", rekening.limit_sisa)

    # Pemanggilan pertama harus memproses ketiga kegiatan.
    Scheduler.jalankan(bank, hari_uji)

    saldo_setelah_pertama = rekening.saldo
    bunga_setelah_pertama = rekening.dapat_bunga
    admin_setelah_pertama = rekening.waktu_bayar_admin
    reset_setelah_pertama = rekening.reset
    limit_setelah_pertama = rekening.limit_sisa
    jumlah_riwayat_setelah_pertama = len(rekening.riwayat)

    print()
    print("SETELAH PEMANGGILAN PERTAMA")
    print("Saldo             :", saldo_setelah_pertama)
    print("Dapat bunga       :", bunga_setelah_pertama)
    print("Bayar admin       :", admin_setelah_pertama)
    print("Reset limit       :", reset_setelah_pertama)
    print("Limit tersisa     :", limit_setelah_pertama)
    print("Jumlah riwayat    :", jumlah_riwayat_setelah_pertama)

    # Pemanggilan kedua menggunakan tanggal yang sama.
    Scheduler.jalankan(bank, hari_uji)

    print()
    print("SETELAH PEMANGGILAN KEDUA")
    print("Saldo             :", rekening.saldo)
    print("Dapat bunga       :", rekening.dapat_bunga)
    print("Bayar admin       :", rekening.waktu_bayar_admin)
    print("Reset limit       :", rekening.reset)
    print("Limit tersisa     :", rekening.limit_sisa)
    print("Jumlah riwayat    :", len(rekening.riwayat))

    # Pemanggilan kedua tidak boleh mengubah saldo.
    assert rekening.saldo == saldo_setelah_pertama, (
        "Saldo berubah ketika scheduler dipanggil ulang pada hari yang sama"
    )

    # Ketiga penanda waktu tidak boleh bergerak lagi.
    assert rekening.dapat_bunga == bunga_setelah_pertama, (
        "Bunga diberikan lebih dari sekali"
    )

    assert rekening.waktu_bayar_admin == admin_setelah_pertama, (
        "Biaya admin dipotong lebih dari sekali"
    )

    assert rekening.reset == reset_setelah_pertama, (
        "Limit direset lebih dari sekali"
    )

    assert rekening.limit_sisa == limit_setelah_pertama, (
        "Jumlah limit berubah pada pemanggilan kedua"
    )

    # Tidak boleh ada riwayat rekening baru dari pemanggilan kedua.
    assert len(rekening.riwayat) == jumlah_riwayat_setelah_pertama, (
        "Scheduler menambahkan riwayat lagi pada pemanggilan kedua"
    )

    # Memastikan ketiga jadwal sudah diproses menuju tanggal yang benar.
    assert rekening.dapat_bunga == hari_uji, (
        "Penanda bunga tidak sampai pada periode yang diharapkan"
    )

    assert rekening.waktu_bayar_admin == hari_uji, (
        "Penanda biaya admin tidak sampai pada periode yang diharapkan"
    )

    assert rekening.reset == hari_uji, (
        "Tanggal reset limit tidak sesuai hari pengujian"
    )

    assert rekening.limit_sisa == rekening.limit_harian, (
        "Limit tersisa tidak dikembalikan ke limit harian"
    )

    print()
    print("✅ Bunga hanya diberikan satu kali")
    print("✅ Biaya admin hanya dipotong satu kali")
    print("✅ Limit hanya direset satu kali")
    print("✅ Scheduler rekening bersifat idempoten")

bank = JsonStorage.muat_bank()

if __name__=="__main__":
    uji_scheduler_rekening_dua_kali(bank)


-------------------------------------------------------------------------
def uji_state_perubahan_level(
    bank,
    nik,
    pin,
    target_level
):
    # Mencari rekening aktif milik nasabah yang akan diuji.
    rekening_lama = next(
        (
            rekening
            for rekening in bank.rekening_index.values()
            if rekening.pemilik.NIK == nik
            and rekening.status == "aktif"
        ),
        None
    )

    if rekening_lama is None:
        raise ValueError(
            "Nasabah tidak ditemukan atau tidak mempunyai rekening aktif"
        )

    nasabah = rekening_lama.pemilik
    level_awal = rekening_lama.level

    if target_level == level_awal:
        raise ValueError(
            "Target level harus berbeda dari level rekening sekarang"
        )

    # Menyiapkan saldo agar memenuhi persyaratan perubahan level.
    rekening_lama.set_saldo(250_000_000)

    # Menyimpan state yang wajib dipertahankan.
    norek_sebelum = rekening_lama.norek
    saldo_sebelum = rekening_lama.saldo
    pemilik_sebelum = rekening_lama.pemilik
    riwayat_sebelum = list(rekening_lama.riwayat)

    waktu_bunga_sebelum = rekening_lama.dapat_bunga
    waktu_admin_sebelum = rekening_lama.waktu_bayar_admin

    objek_lama = id(rekening_lama)

    print("SEBELUM PERUBAHAN LEVEL")
    print(f"Objek rekening   : {objek_lama}")
    print(f"Nomor rekening   : {norek_sebelum}")
    print(f"Level            : {level_awal}")
    print(f"Saldo            : {saldo_sebelum}")
    print(f"Limit harian     : {rekening_lama.limit_harian}")
    print(f"Limit tersisa    : {rekening_lama.limit_sisa}")
    print(f"Waktu bunga      : {waktu_bunga_sebelum}")
    print(f"Waktu admin      : {waktu_admin_sebelum}")
    print(f"Jumlah riwayat   : {len(riwayat_sebelum)}")

    # Menjalankan upgrade atau downgrade berdasarkan target level.
    if target_level > level_awal:
        rekening_baru = RekeningService.upgrade_rekening(
            bank,
            rekening_lama,
            target_level
        )
        jenis_perubahan = "upgrade"

    else:
        rekening_baru = RekeningService.downgrade_rekening(
            bank,
            rekening_lama,
            target_level
        )
        jenis_perubahan = "downgrade"

    print("\nSETELAH PERUBAHAN LEVEL")
    print(f"Jenis perubahan  : {jenis_perubahan}")
    print(f"Objek rekening   : {id(rekening_baru)}")
    print(f"Nomor rekening   : {rekening_baru.norek}")
    print(f"Level            : {rekening_baru.level}")
    print(f"Saldo            : {rekening_baru.saldo}")
    print(f"Limit harian     : {rekening_baru.limit_harian}")
    print(f"Limit tersisa    : {rekening_baru.limit_sisa}")
    print(f"Waktu bunga      : {rekening_baru.dapat_bunga}")
    print(f"Waktu admin      : {rekening_baru.waktu_bayar_admin}")
    print(f"Jumlah riwayat   : {len(rekening_baru.riwayat)}")

    # Memastikan perubahan menghasilkan objek rekening baru.
    assert rekening_baru is not rekening_lama, (
        "Perubahan level tidak menghasilkan objek rekening baru"
    )

    # Memastikan identitas bisnis rekening tetap dipertahankan.
    assert rekening_baru.norek == norek_sebelum, (
        "Nomor rekening berubah setelah perubahan level"
    )

    assert rekening_baru.pemilik is pemilik_sebelum, (
        "Pemilik rekening berubah setelah perubahan level"
    )

    assert rekening_baru.cek_pin(pin), (
        "PIN rekening tidak ikut dipertahankan"
    )

    # Memastikan state keuangan tetap dipertahankan.
    assert rekening_baru.saldo == saldo_sebelum, (
        "Saldo berubah ketika rekening diganti"
    )

    # Seluruh riwayat lama harus tetap tersedia.
    for riwayat in riwayat_sebelum:
        assert riwayat in rekening_baru.riwayat, (
            "Terdapat riwayat lama yang tidak ikut dipindahkan"
        )

    # Jadwal bunga dan biaya admin tidak boleh dimulai ulang.
    assert rekening_baru.dapat_bunga == waktu_bunga_sebelum, (
        "Jadwal pemberian bunga berubah"
    )

    assert rekening_baru.waktu_bayar_admin == waktu_admin_sebelum, (
        "Jadwal pembayaran biaya admin berubah"
    )

    # Level harus mengikuti pilihan perubahan.
    assert rekening_baru.level == target_level, (
        "Level rekening baru tidak sesuai target"
    )

    # Rekening baru harus tetap dapat digunakan.
    assert rekening_baru.status == "aktif", (
        "Rekening baru tidak berstatus aktif"
    )

    # Limit tersisa sengaja dimulai ulang.
    assert rekening_baru.limit_sisa == rekening_baru.limit_harian, (
        "Limit tersisa tidak di-reset sesuai jenis rekening baru"
    )

    # Bank harus menunjuk objek rekening baru.
    assert bank.rekening_index[norek_sebelum] is rekening_baru, (
        "Indeks rekening bank belum diperbarui"
    )

    # Nasabah harus menyimpan objek rekening baru.
    assert rekening_baru in nasabah.rekening, (
        "Rekening baru tidak ditemukan pada daftar rekening nasabah"
    )

    assert rekening_lama not in nasabah.rekening, (
        "Rekening lama masih tersimpan pada nasabah"
    )

    # Waktu perubahan level harus tercatat agar tidak bisa diubah berulang.
    assert rekening_baru.boleh_ubah_level is not None, (
        "Waktu pembatas perubahan level belum disimpan"
    )

    print(
        "\n✅ Seluruh state rekening sesuai setelah "
        f"{jenis_perubahan}"
    )

    return rekening_baru

bank = JsonStorage.muat_bank()


rekening_hasil = uji_state_perubahan_level(
    bank,
    nik="3510152602082002",
    pin="111111",
    target_level=4
)

rekening = uji_state_perubahan_level(
    bank,
    nik="3510152602082002",
    pin="111111",
    target_level=3
)
