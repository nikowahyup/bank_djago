# # # # # # # # # # # from bank_djago.penyimpanan.repositories.nasabah_repository import (
# # # # # # # # # # #     NasabahRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # # # # # #     RekeningRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.deposito_repository import (
# # # # # # # # # # #     DepositoRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.riwayat_repository import (
# # # # # # # # # # #     RiwayatRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # # # # # #     AuditRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # NOREK_PENGUJIAN = "2001569043650499"
# # # # # # # # # # #
# # # # # # # # # # # NOMINAL_DEPOSITO = 1_000_000
# # # # # # # # # # # SALDO_SEBELUM = 109_000_000
# # # # # # # # # # # SALDO_SESUDAH = SALDO_SEBELUM - NOMINAL_DEPOSITO
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENGAMBIL DATA DARI SQLITE
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # nasabah = NasabahRepository.cari_nasabah_dengan_nik(
# # # # # # # # # # #     NIK_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # # # # # #     NOREK_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # daftar_deposito = DepositoRepository.cari_deposito_dengan_norek(
# # # # # # # # # # #     NOREK_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(
# # # # # # # # # # #     NOREK_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # daftar_audit = AuditRepository.cari_audit_dengan_norek(
# # # # # # # # # # #     NOREK_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MEMASTIKAN DATA UTAMA DITEMUKAN
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # assert nasabah is not None, "Nasabah tidak ditemukan"
# # # # # # # # # # # assert rekening is not None, "Rekening tidak ditemukan"
# # # # # # # # # # # assert daftar_deposito, "Deposito tidak ditemukan"
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # Repository mengurutkan deposito berdasarkan ID dari kecil
# # # # # # # # # # # # ke besar, sehingga elemen terakhir adalah deposito terbaru.
# # # # # # # # # # # deposito_terbaru = daftar_deposito[-1]
# # # # # # # # # # #
# # # # # # # # # # # riwayat_deposito = [
# # # # # # # # # # #     riwayat
# # # # # # # # # # #     for riwayat in daftar_riwayat
# # # # # # # # # # #     if riwayat["jenis"] == "deposito"
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # audit_deposito = [
# # # # # # # # # # #     audit
# # # # # # # # # # #     for audit in daftar_audit
# # # # # # # # # # #     if audit["jenis"] == "deposito"
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # assert riwayat_deposito, "Riwayat pembukaan deposito tidak ditemukan"
# # # # # # # # # # # assert audit_deposito, "Audit pembukaan deposito tidak ditemukan"
# # # # # # # # # # #
# # # # # # # # # # # # Riwayat dan audit diurutkan berdasarkan ID terbaru.
# # # # # # # # # # # riwayat_terbaru = riwayat_deposito[0]
# # # # # # # # # # # audit_terbaru = audit_deposito[0]
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENAMPILKAN HASIL
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # print("DATA NASABAH")
# # # # # # # # # # # print(f"NIK     : {nasabah['nik']}")
# # # # # # # # # # # print(f"Nama    : {nasabah['nama']}")
# # # # # # # # # # # print(f"Alamat  : {nasabah['alamat']}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI REKENING")
# # # # # # # # # # # print(f"Norek   : {rekening['norek']}")
# # # # # # # # # # # print(f"Status  : {rekening['status']}")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Saldo   : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(rekening['saldo'])}"
# # # # # # # # # # # )
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DEPOSITO TERBARU")
# # # # # # # # # # # print(f"ID             : {deposito_terbaru['id']}")
# # # # # # # # # # # print(f"Norek          : {deposito_terbaru['norek']}")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Nominal        : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(deposito_terbaru['nominal'])}"
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Bunga          : {deposito_terbaru['bunga']:.1%}")
# # # # # # # # # # # print(f"Tenor          : {deposito_terbaru['lama_bulan']} bulan")
# # # # # # # # # # # print(f"Tanggal buka   : {deposito_terbaru['tanggal_buka']}")
# # # # # # # # # # # print(f"Jatuh tempo    : {deposito_terbaru['jatuh_tempo']}")
# # # # # # # # # # # print(f"Status         : {deposito_terbaru['status']}")
# # # # # # # # # # # print(f"Jenis ARO      : {deposito_terbaru['jenis_aro']}")
# # # # # # # # # # # print(f"Lama ARO       : {deposito_terbaru['lama_aro']}")
# # # # # # # # # # # print(f"Proses ARO     : {deposito_terbaru['proses_aro']}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("RIWAYAT TERBARU")
# # # # # # # # # # # print(f"ID        : {riwayat_terbaru['id']}")
# # # # # # # # # # # print(f"Kategori  : {riwayat_terbaru['kategori']}")
# # # # # # # # # # # print(f"Jenis     : {riwayat_terbaru['jenis']}")
# # # # # # # # # # # print(f"Waktu     : {riwayat_terbaru['waktu']}")
# # # # # # # # # # # print(f"Log       : {riwayat_terbaru['log']}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("AUDIT TERBARU")
# # # # # # # # # # # print(f"ID        : {audit_terbaru['id']}")
# # # # # # # # # # # print(f"Kategori  : {audit_terbaru['kategori']}")
# # # # # # # # # # # print(f"Jenis     : {audit_terbaru['jenis']}")
# # # # # # # # # # # print(f"Waktu     : {audit_terbaru['waktu']}")
# # # # # # # # # # # print(f"Log       : {audit_terbaru['log']}")
# # # # # # # # # # # print(f"Nama      : {audit_terbaru['nama']}")
# # # # # # # # # # # print(f"NIK       : {audit_terbaru['nik']}")
# # # # # # # # # # # print(f"Norek     : {audit_terbaru['norek']}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # PEMERIKSAAN INTEGRITAS
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # assert rekening["saldo"] == SALDO_SESUDAH, (
# # # # # # # # # # #     "Saldo rekening tidak berkurang sesuai nominal deposito"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["norek"] == NOREK_PENGUJIAN, (
# # # # # # # # # # #     "Foreign key deposito tidak mengarah ke rekening pengujian"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["nominal"] == NOMINAL_DEPOSITO, (
# # # # # # # # # # #     "Nominal deposito tidak sesuai"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["bunga"] == 0.03, (
# # # # # # # # # # #     "Bunga deposito tenor satu bulan tidak sesuai"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["lama_bulan"] == 1, (
# # # # # # # # # # #     "Tenor deposito tidak sesuai"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["status"] == "aktif", (
# # # # # # # # # # #     "Status awal deposito bukan aktif"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["jenis_aro"] == "tidak", (
# # # # # # # # # # #     "Jenis ARO deposito tidak sesuai"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["lama_aro"] is None, (
# # # # # # # # # # #     "Deposito tanpa ARO seharusnya tidak memiliki lama ARO"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_terbaru["proses_aro"] is None, (
# # # # # # # # # # #     "Deposito baru seharusnya belum memiliki tanggal proses ARO"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert riwayat_terbaru["norek"] == NOREK_PENGUJIAN, (
# # # # # # # # # # #     "Riwayat tersimpan pada rekening yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert audit_terbaru["nik"] == NIK_PENGUJIAN, (
# # # # # # # # # # #     "Audit tersimpan dengan NIK yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert audit_terbaru["norek"] == NOREK_PENGUJIAN, (
# # # # # # # # # # #     "Audit tersimpan dengan nomor rekening yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("✅ Saldo rekening berhasil dikurangi")
# # # # # # # # # # # print("✅ Deposito berhasil disimpan dengan ID global")
# # # # # # # # # # # print("✅ Foreign key deposito mengarah ke rekening yang benar")
# # # # # # # # # # # print("✅ Tenor, bunga, status, dan ARO tersimpan sesuai pilihan")
# # # # # # # # # # # print("✅ Riwayat pembukaan deposito berhasil disimpan")
# # # # # # # # # # # print("✅ Audit pembukaan deposito berhasil disimpan")
# # # # # # # # # # # print("✅ Pembukaan deposito SQLite bekerja sesuai rancangan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # # import datetime
# # # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # # # # # # # # #     NasabahLoader
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # NOREK_DEPOSITO = "2001569043650499"
# # # # # # # # # # # ID_DEPOSITO = 5
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MEMUAT NASABAH DARI SQLITE
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # assert nasabah is not None, (
# # # # # # # # # # #     "Nasabah pengujian tidak berhasil dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert nasabah.rekening, (
# # # # # # # # # # #     "Daftar rekening nasabah tidak berhasil dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert nasabah.deposito, (
# # # # # # # # # # #     "Daftar deposito nasabah tidak berhasil dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENCARI OBJEK REKENING DAN DEPOSITO
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # rekening_deposito = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         rekening
# # # # # # # # # # #         for rekening in nasabah.rekening
# # # # # # # # # # #         if rekening.norek == NOREK_DEPOSITO
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # deposito = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         deposito
# # # # # # # # # # #         for deposito in nasabah.deposito
# # # # # # # # # # #         if deposito.ID == ID_DEPOSITO
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert rekening_deposito is not None, (
# # # # # # # # # # #     "Rekening milik deposito tidak berhasil dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito is not None, (
# # # # # # # # # # #     f"Deposito ID {ID_DEPOSITO} tidak berhasil dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENAMPILKAN HASIL LOADER
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # print("DATA NASABAH")
# # # # # # # # # # # print(f"NIK              : {nasabah.NIK}")
# # # # # # # # # # # print(f"Nama             : {nasabah.nama}")
# # # # # # # # # # # print(f"Jumlah rekening  : {len(nasabah.rekening)}")
# # # # # # # # # # # print(f"Jumlah deposito  : {len(nasabah.deposito)}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DATA REKENING DEPOSITO")
# # # # # # # # # # # print(f"Norek            : {rekening_deposito.norek}")
# # # # # # # # # # # print(f"Status           : {rekening_deposito.status}")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Saldo            : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(rekening_deposito.saldo)}"
# # # # # # # # # # # )
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DATA DEPOSITO")
# # # # # # # # # # # print(f"ID               : {deposito.ID}")
# # # # # # # # # # # print(f"Norek            : {deposito.rekening.norek}")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Nominal          : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(deposito.nominal)}"
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Bunga            : {deposito.bunga:.1%}")
# # # # # # # # # # # print(f"Tenor            : {deposito.lama_bulan} bulan")
# # # # # # # # # # # print(f"Tanggal buka     : {deposito.tanggal_buka}")
# # # # # # # # # # # print(f"Jatuh tempo      : {deposito.jatuh_tempo}")
# # # # # # # # # # # print(f"Status           : {deposito.status}")
# # # # # # # # # # # print(f"Jenis ARO        : {deposito.jenis_aro}")
# # # # # # # # # # # print(f"Lama ARO         : {deposito.lama_aro}")
# # # # # # # # # # # print(f"Proses ARO       : {deposito.proses_aro}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MEMERIKSA DATA YANG DIPULIHKAN
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.nominal == 1_000_000, (
# # # # # # # # # # #     "Nominal deposito tidak berhasil dipulihkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.bunga == 0.03, (
# # # # # # # # # # #     "Bunga deposito tidak berhasil dipulihkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.lama_bulan == 1, (
# # # # # # # # # # #     "Tenor deposito tidak berhasil dipulihkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.status == "aktif", (
# # # # # # # # # # #     "Status deposito tidak berhasil dipulihkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.jenis_aro == "tidak", (
# # # # # # # # # # #     "Jenis ARO tidak berhasil dipulihkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.lama_aro is None, (
# # # # # # # # # # #     "Lama ARO seharusnya None"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.proses_aro is None, (
# # # # # # # # # # #     "Proses ARO seharusnya None"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert isinstance(
# # # # # # # # # # #     deposito.tanggal_buka,
# # # # # # # # # # #     datetime.date
# # # # # # # # # # # ), "Tanggal buka belum dikembalikan menjadi datetime.date"
# # # # # # # # # # #
# # # # # # # # # # # assert isinstance(
# # # # # # # # # # #     deposito.jatuh_tempo,
# # # # # # # # # # #     datetime.date
# # # # # # # # # # # ), "Jatuh tempo belum dikembalikan menjadi datetime.date"
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MEMERIKSA RELASI OBJEK
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # assert rekening_deposito.pemilik is nasabah, (
# # # # # # # # # # #     "Pemilik rekening bukan objek nasabah yang dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.pemilik is nasabah, (
# # # # # # # # # # #     "Pemilik deposito bukan objek nasabah yang dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.rekening is rekening_deposito, (
# # # # # # # # # # #     "Deposito tidak menunjuk objek rekening yang sama"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.rekening in nasabah.rekening, (
# # # # # # # # # # #     "Rekening deposito tidak berada dalam daftar rekening nasabah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito in nasabah.deposito, (
# # # # # # # # # # #     "Deposito tidak berada dalam daftar deposito nasabah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("✅ Nasabah berhasil dimuat dari SQLite")
# # # # # # # # # # # print("✅ Seluruh rekening nasabah berhasil dimuat")
# # # # # # # # # # # print("✅ Deposito ID 5 berhasil dimuat")
# # # # # # # # # # # print("✅ Seluruh tanggal kembali menjadi datetime.date")
# # # # # # # # # # # print("✅ Deposito menunjuk objek nasabah yang benar")
# # # # # # # # # # # print("✅ Deposito menunjuk objek rekening yang sama")
# # # # # # # # # # # print("✅ DepositoLoader bekerja sesuai rancangan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # print("-----------------------------------------------------------------------------------------")
# # # # # # # # # #
# # # # # # # # # # # print("TES PENCAIRAN DEPOSITO")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import (
# # # # # # # # # # #     buat_koneksi
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import (
# # # # # # # # # # #     NasabahLoader
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.deposito_repository import (
# # # # # # # # # # #     DepositoRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # # # # # #     RekeningRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.riwayat_repository import (
# # # # # # # # # # #     RiwayatRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # # # # # #     AuditRepository
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.services.deposito.deposito_service import (
# # # # # # # # # # #     DepositoService,
# # # # # # # # # # #     StatusDeposito
# # # # # # # # # # # )
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # NOREK_PENGUJIAN = "2001569043650499"
# # # # # # # # # # # ID_DEPOSITO = 5
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # KONDISI SEBELUM PENCAIRAN
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # rekening_sebelum = (
# # # # # # # # # # #     RekeningRepository.cari_rekening_dengan_norek(
# # # # # # # # # # #         NOREK_PENGUJIAN
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # deposito_sebelum = (
# # # # # # # # # # #     DepositoRepository.cari_deposito_dengan_id(
# # # # # # # # # # #         ID_DEPOSITO
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # riwayat_sebelum = (
# # # # # # # # # # #     RiwayatRepository.cari_seluruh_riwayat(
# # # # # # # # # # #         NOREK_PENGUJIAN
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # audit_sebelum = (
# # # # # # # # # # #     AuditRepository.cari_audit_dengan_norek(
# # # # # # # # # # #         NOREK_PENGUJIAN
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert rekening_sebelum is not None, (
# # # # # # # # # # #     "Rekening pengujian tidak ditemukan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sebelum is not None, (
# # # # # # # # # # #     "Deposito pengujian tidak ditemukan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # if deposito_sebelum["status"] == StatusDeposito.DICAIRKAN:
# # # # # # # # # # #     raise ValueError(
# # # # # # # # # # #         "Deposito ID 5 sudah dicairkan. "
# # # # # # # # # # #         "Pengujian ini tidak boleh dijalankan kembali."
# # # # # # # # # # #     )
# # # # # # # # # # #
# # # # # # # # # # # saldo_sebelum = rekening_sebelum["saldo"]
# # # # # # # # # # # jumlah_riwayat_sebelum = len(riwayat_sebelum)
# # # # # # # # # # # jumlah_audit_sebelum = len(audit_sebelum)
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SEBELUM PENCAIRAN")
# # # # # # # # # # # print(f"ID deposito       : {deposito_sebelum['id']}")
# # # # # # # # # # # print(f"Status deposito   : {deposito_sebelum['status']}")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Saldo rekening    : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(saldo_sebelum)}"
# # # # # # # # # # # )
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Nominal deposito  : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(deposito_sebelum['nominal'])}"
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Jumlah riwayat    : {jumlah_riwayat_sebelum}")
# # # # # # # # # # # print(f"Jumlah audit      : {jumlah_audit_sebelum}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENYIAPKAN STATUS JATUH TEMPO
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # if deposito_sebelum["status"] != StatusDeposito.JATUH_TEMPO:
# # # # # # # # # # #     koneksi = buat_koneksi()
# # # # # # # # # # #
# # # # # # # # # # #     try:
# # # # # # # # # # #         jumlah_baris = (
# # # # # # # # # # #             DepositoRepository.perbarui_status_deposito(
# # # # # # # # # # #                 id_deposito=ID_DEPOSITO,
# # # # # # # # # # #                 status_baru=StatusDeposito.JATUH_TEMPO,
# # # # # # # # # # #                 koneksi=koneksi
# # # # # # # # # # #             )
# # # # # # # # # # #         )
# # # # # # # # # # #
# # # # # # # # # # #         if jumlah_baris != 1:
# # # # # # # # # # #             raise ValueError(
# # # # # # # # # # #                 "Gagal menyiapkan status jatuh tempo"
# # # # # # # # # # #             )
# # # # # # # # # # #
# # # # # # # # # # #         koneksi.commit()
# # # # # # # # # # #
# # # # # # # # # # #     except Exception:
# # # # # # # # # # #         koneksi.rollback()
# # # # # # # # # # #         raise
# # # # # # # # # # #
# # # # # # # # # # #     finally:
# # # # # # # # # # #         koneksi.close()
# # # # # # # # # # #
# # # # # # # # # # # print("✅ Status deposito disiapkan menjadi jatuh tempo")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MEMUAT ULANG OBJEK DARI SQLITE
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(
# # # # # # # # # # #     NIK_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert nasabah is not None, (
# # # # # # # # # # #     "Nasabah gagal dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # deposito = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         item
# # # # # # # # # # #         for item in nasabah.deposito
# # # # # # # # # # #         if item.ID == ID_DEPOSITO
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito is not None, (
# # # # # # # # # # #     "Objek deposito ID 5 gagal dimuat"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.status == StatusDeposito.JATUH_TEMPO, (
# # # # # # # # # # #     "Objek deposito tidak memuat status jatuh tempo"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.rekening.norek == NOREK_PENGUJIAN, (
# # # # # # # # # # #     "Deposito terhubung dengan rekening yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # total_yang_diharapkan = deposito.total_pencairan
# # # # # # # # # # # saldo_yang_diharapkan = (
# # # # # # # # # # #     saldo_sebelum + total_yang_diharapkan
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # print()
# # # # # # # # # # # print("DATA PENCAIRAN")
# # # # # # # # # # # print(f"Tanggal buka      : {deposito.tanggal_buka}")
# # # # # # # # # # # print(f"Jatuh tempo       : {deposito.jatuh_tempo}")
# # # # # # # # # # # print(f"Bunga             : {deposito.bunga:.1%}")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Total pencairan   : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(total_yang_diharapkan)}"
# # # # # # # # # # # )
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENJALANKAN PENCAIRAN
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # total_pencairan = (
# # # # # # # # # # #     DepositoService.cairkan_deposito(
# # # # # # # # # # #         deposito=deposito,
# # # # # # # # # # #         hari_ini=deposito.jatuh_tempo
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENGAMBIL KONDISI SETELAH PENCAIRAN
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # rekening_setelah = (
# # # # # # # # # # #     RekeningRepository.cari_rekening_dengan_norek(
# # # # # # # # # # #         NOREK_PENGUJIAN
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # deposito_setelah = (
# # # # # # # # # # #     DepositoRepository.cari_deposito_dengan_id(
# # # # # # # # # # #         ID_DEPOSITO
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # riwayat_setelah = (
# # # # # # # # # # #     RiwayatRepository.cari_seluruh_riwayat(
# # # # # # # # # # #         NOREK_PENGUJIAN
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # audit_setelah = (
# # # # # # # # # # #     AuditRepository.cari_audit_dengan_norek(
# # # # # # # # # # #         NOREK_PENGUJIAN
# # # # # # # # # # #     )
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # riwayat_pencairan = [
# # # # # # # # # # #     item
# # # # # # # # # # #     for item in riwayat_setelah
# # # # # # # # # # #     if item["jenis"] == "pencairan deposito"
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # audit_pencairan = [
# # # # # # # # # # #     item
# # # # # # # # # # #     for item in audit_setelah
# # # # # # # # # # #     if item["jenis"] == "pencairan deposito"
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # assert riwayat_pencairan, (
# # # # # # # # # # #     "Riwayat pencairan tidak ditemukan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert audit_pencairan, (
# # # # # # # # # # #     "Audit pencairan tidak ditemukan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # riwayat_terbaru = riwayat_pencairan[0]
# # # # # # # # # # # audit_terbaru = audit_pencairan[0]
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # MENAMPILKAN KONDISI SETELAH
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SETELAH PENCAIRAN")
# # # # # # # # # # # print(
# # # # # # # # # # #     f"Saldo rekening    : Rp"
# # # # # # # # # # #     f"{Utilitas.format_rupiah(rekening_setelah['saldo'])}"
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Status deposito   : {deposito_setelah['status']}")
# # # # # # # # # # # print(f"Jumlah riwayat    : {len(riwayat_setelah)}")
# # # # # # # # # # # print(f"Jumlah audit      : {len(audit_setelah)}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("RIWAYAT PENCAIRAN")
# # # # # # # # # # # print(f"ID                : {riwayat_terbaru['id']}")
# # # # # # # # # # # print(f"Jenis             : {riwayat_terbaru['jenis']}")
# # # # # # # # # # # print(f"Waktu             : {riwayat_terbaru['waktu']}")
# # # # # # # # # # # print(f"Log               : {riwayat_terbaru['log']}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("AUDIT PENCAIRAN")
# # # # # # # # # # # print(f"ID                : {audit_terbaru['id']}")
# # # # # # # # # # # print(f"Jenis             : {audit_terbaru['jenis']}")
# # # # # # # # # # # print(f"Waktu             : {audit_terbaru['waktu']}")
# # # # # # # # # # # print(f"Log               : {audit_terbaru['log']}")
# # # # # # # # # # # print(f"Nama              : {audit_terbaru['nama']}")
# # # # # # # # # # # print(f"NIK               : {audit_terbaru['nik']}")
# # # # # # # # # # # print(f"Norek             : {audit_terbaru['norek']}")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # =========================================================
# # # # # # # # # # # # PEMERIKSAAN HASIL
# # # # # # # # # # # # =========================================================
# # # # # # # # # # #
# # # # # # # # # # # assert total_pencairan == total_yang_diharapkan, (
# # # # # # # # # # #     "Nilai yang dikembalikan service tidak sesuai"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert rekening_setelah["saldo"] == saldo_yang_diharapkan, (
# # # # # # # # # # #     "Saldo SQLite tidak bertambah sesuai total pencairan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_setelah["status"] == StatusDeposito.DICAIRKAN, (
# # # # # # # # # # #     "Status deposito SQLite tidak berubah menjadi dicairkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.rekening.saldo == saldo_yang_diharapkan, (
# # # # # # # # # # #     "Saldo objek rekening tidak berhasil disinkronkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert deposito.status == StatusDeposito.DICAIRKAN, (
# # # # # # # # # # #     "Status objek deposito tidak berhasil disinkronkan"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert len(riwayat_setelah) == jumlah_riwayat_sebelum + 1, (
# # # # # # # # # # #     "Jumlah riwayat tidak bertambah tepat satu"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert len(audit_setelah) == jumlah_audit_sebelum + 1, (
# # # # # # # # # # #     "Jumlah audit tidak bertambah tepat satu"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert riwayat_terbaru["norek"] == NOREK_PENGUJIAN, (
# # # # # # # # # # #     "Riwayat pencairan tersimpan pada rekening yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert audit_terbaru["nik"] == NIK_PENGUJIAN, (
# # # # # # # # # # #     "Audit pencairan memiliki NIK yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # assert audit_terbaru["norek"] == NOREK_PENGUJIAN, (
# # # # # # # # # # #     "Audit pencairan memiliki norek yang salah"
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("✅ Status jatuh tempo berhasil disiapkan")
# # # # # # # # # # # print("✅ Total pencairan berhasil dihitung")
# # # # # # # # # # # print("✅ Saldo rekening SQLite berhasil ditambahkan")
# # # # # # # # # # # print("✅ Status deposito berubah menjadi dicairkan")
# # # # # # # # # # # print("✅ Objek rekening dan deposito berhasil disinkronkan")
# # # # # # # # # # # print("✅ Riwayat pencairan bertambah tepat satu")
# # # # # # # # # # # print("✅ Audit pencairan bertambah tepat satu")
# # # # # # # # # # # print("✅ Pencairan deposito SQLite bekerja sesuai rancangan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # # print("---------------------------------------------------------------------")
# # # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # # # # from bank_djago.core.deposito import JenisAro
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # # from bank_djago.services.deposito.deposito_service import StatusDeposito
# # # # # # # # # # #
# # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # NOMINAL_DEPOSITO = 1_000_000
# # # # # # # # # # # SALDO_SEBELUM = 109_002_500
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # if nasabah is None:
# # # # # # # # # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # deposito_aktif = [
# # # # # # # # # # #     deposito
# # # # # # # # # # #     for deposito in nasabah.deposito
# # # # # # # # # # #     if deposito.status == StatusDeposito.AKTIF
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # deposito_aktif.sort(key=lambda deposito: deposito.ID)
# # # # # # # # # # #
# # # # # # # # # # # if len(deposito_aktif) < 2:
# # # # # # # # # # #     raise AssertionError(
# # # # # # # # # # #         "Dibutuhkan minimal dua deposito aktif untuk pengujian ARO"
# # # # # # # # # # #     )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # deposito_pokok = deposito_aktif[-2]
# # # # # # # # # # # deposito_pokok_bunga = deposito_aktif[-1]
# # # # # # # # # # #
# # # # # # # # # # # rekening = deposito_pokok.rekening
# # # # # # # # # # # saldo_seharusnya = SALDO_SEBELUM - (NOMINAL_DEPOSITO * 2)
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI AWAL PENGUJIAN ARO")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DATA NASABAH")
# # # # # # # # # # # print("NIK             :", nasabah.NIK)
# # # # # # # # # # # print("Nama            :", nasabah.nama)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DATA REKENING")
# # # # # # # # # # # print("Norek           :", rekening.norek)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Saldo           : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(rekening.saldo)
# # # # # # # # # # # )
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DEPOSITO ARO POKOK")
# # # # # # # # # # # print("ID              :", deposito_pokok.ID)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Nominal         : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(deposito_pokok.nominal)
# # # # # # # # # # # )
# # # # # # # # # # # print("Status          :", deposito_pokok.status)
# # # # # # # # # # # print("Jenis ARO       :", deposito_pokok.jenis_aro)
# # # # # # # # # # # print("Lama ARO        :", deposito_pokok.lama_aro)
# # # # # # # # # # # print("Tanggal buka    :", deposito_pokok.tanggal_buka)
# # # # # # # # # # # print("Jatuh tempo     :", deposito_pokok.jatuh_tempo)
# # # # # # # # # # # print("Proses ARO      :", deposito_pokok.proses_aro)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("DEPOSITO ARO POKOK + BUNGA")
# # # # # # # # # # # print("ID              :", deposito_pokok_bunga.ID)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Nominal         : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(deposito_pokok_bunga.nominal)
# # # # # # # # # # # )
# # # # # # # # # # # print("Status          :", deposito_pokok_bunga.status)
# # # # # # # # # # # print("Jenis ARO       :", deposito_pokok_bunga.jenis_aro)
# # # # # # # # # # # print("Lama ARO        :", deposito_pokok_bunga.lama_aro)
# # # # # # # # # # # print("Tanggal buka    :", deposito_pokok_bunga.tanggal_buka)
# # # # # # # # # # # print("Jatuh tempo     :", deposito_pokok_bunga.jatuh_tempo)
# # # # # # # # # # # print("Proses ARO      :", deposito_pokok_bunga.proses_aro)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.ID != deposito_pokok_bunga.ID
# # # # # # # # # # # print("✅ Kedua deposito mempunyai ID global berbeda")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.jenis_aro == JenisAro.POKOK
# # # # # # # # # # # print("✅ Deposito pertama menggunakan ARO pokok")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok_bunga.jenis_aro == JenisAro.POKOK_BUNGA
# # # # # # # # # # # print("✅ Deposito kedua menggunakan ARO pokok + bunga")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.status == StatusDeposito.AKTIF
# # # # # # # # # # # assert deposito_pokok_bunga.status == StatusDeposito.AKTIF
# # # # # # # # # # # print("✅ Kedua deposito masih aktif")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.lama_aro in (1, 3, 6, 12)
# # # # # # # # # # # assert deposito_pokok_bunga.lama_aro in (1, 3, 6, 12)
# # # # # # # # # # # print("✅ Tenor ARO kedua deposito tersimpan")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.rekening is rekening
# # # # # # # # # # # assert deposito_pokok_bunga.rekening is rekening
# # # # # # # # # # # print("✅ Kedua deposito menunjuk objek rekening yang sama")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.pemilik is nasabah
# # # # # # # # # # # assert deposito_pokok_bunga.pemilik is nasabah
# # # # # # # # # # # print("✅ Kedua deposito menunjuk objek nasabah yang sama")
# # # # # # # # # # #
# # # # # # # # # # # assert rekening.saldo == saldo_seharusnya
# # # # # # # # # # # print("✅ Saldo rekening telah dipotong sesuai dua deposito")
# # # # # # # # # # #
# # # # # # # # # # # print()
# # # # # # # # # # # print("Data awal pengujian ARO siap digunakan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # # from bank_djago.services.deposito.deposito_service import DepositoService
# # # # # # # # # # # from bank_djago.core.deposito import JenisAro
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # # from bank_djago.services.deposito.deposito_service import StatusDeposito
# # # # # # # # # # #
# # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # ID_DEPOSITO = 6
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # def hitung_data_pendukung(norek):
# # # # # # # # # # #     koneksi = buat_koneksi()
# # # # # # # # # # #
# # # # # # # # # # #     try:
# # # # # # # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # # # # # # #             """
# # # # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # # # #             FROM riwayat
# # # # # # # # # # #             WHERE norek = ?
# # # # # # # # # # #             """,
# # # # # # # # # # #             (norek,)
# # # # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # # # #
# # # # # # # # # # #         jumlah_audit = koneksi.execute(
# # # # # # # # # # #             """
# # # # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # # # #             FROM audit
# # # # # # # # # # #             WHERE norek = ?
# # # # # # # # # # #             """,
# # # # # # # # # # #             (norek,)
# # # # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # # # #
# # # # # # # # # # #         return jumlah_riwayat, jumlah_audit
# # # # # # # # # # #
# # # # # # # # # # #     finally:
# # # # # # # # # # #         koneksi.close()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # if nasabah is None:
# # # # # # # # # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # deposito_pokok = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         deposito
# # # # # # # # # # #         for deposito in nasabah.deposito
# # # # # # # # # # #         if deposito.ID == ID_DEPOSITO
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # if deposito_pokok is None:
# # # # # # # # # # #     raise AssertionError(
# # # # # # # # # # #         f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
# # # # # # # # # # #     )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # rekening = deposito_pokok.rekening
# # # # # # # # # # #
# # # # # # # # # # # saldo_sebelum = rekening.saldo
# # # # # # # # # # # nominal_sebelum = deposito_pokok.nominal
# # # # # # # # # # # bunga_sebelum = deposito_pokok.bunga
# # # # # # # # # # # tanggal_buka_sebelum = deposito_pokok.tanggal_buka
# # # # # # # # # # # jatuh_tempo_sebelum = deposito_pokok.jatuh_tempo
# # # # # # # # # # # lama_aro = deposito_pokok.lama_aro
# # # # # # # # # # #
# # # # # # # # # # # total_pencairan = deposito_pokok.total_pencairan
# # # # # # # # # # # bunga_diterima = total_pencairan - nominal_sebelum
# # # # # # # # # # #
# # # # # # # # # # # saldo_seharusnya = saldo_sebelum + bunga_diterima
# # # # # # # # # # # tanggal_buka_seharusnya = jatuh_tempo_sebelum
# # # # # # # # # # # jatuh_tempo_seharusnya = Utilitas.tambah_bulan(
# # # # # # # # # # #     tanggal_buka_seharusnya,
# # # # # # # # # # #     lama_aro
# # # # # # # # # # # )
# # # # # # # # # # # bunga_baru_seharusnya = DepositoService.JANGKA_WAKTU[
# # # # # # # # # # #     lama_aro
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # riwayat_sebelum, audit_sebelum = hitung_data_pendukung(
# # # # # # # # # # #     rekening.norek
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SEBELUM ARO POKOK")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("ID deposito       :", deposito_pokok.ID)
# # # # # # # # # # # print("Jenis ARO         :", deposito_pokok.jenis_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Nominal           : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(nominal_sebelum)
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Bunga lama        : {bunga_sebelum:.1%}")
# # # # # # # # # # # print("Tenor lama        :", deposito_pokok.lama_bulan, "bulan")
# # # # # # # # # # # print("Tenor ARO         :", lama_aro, "bulan")
# # # # # # # # # # # print("Tanggal buka      :", tanggal_buka_sebelum)
# # # # # # # # # # # print("Jatuh tempo       :", jatuh_tempo_sebelum)
# # # # # # # # # # # print("Proses ARO        :", deposito_pokok.proses_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Saldo rekening    : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(saldo_sebelum)
# # # # # # # # # # # )
# # # # # # # # # # # print(
# # # # # # # # # # #     "Bunga diterima    : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(bunga_diterima)
# # # # # # # # # # # )
# # # # # # # # # # # print("Jumlah riwayat    :", riwayat_sebelum)
# # # # # # # # # # # print("Jumlah audit      :", audit_sebelum)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_pokok.jenis_aro == JenisAro.POKOK
# # # # # # # # # # # assert deposito_pokok.status == StatusDeposito.AKTIF
# # # # # # # # # # #
# # # # # # # # # # # DepositoService.perpanjangan(
# # # # # # # # # # #     deposito=deposito_pokok,
# # # # # # # # # # #     hari_ini=jatuh_tempo_sebelum
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # Memuat ulang data agar hasil yang diperiksa benar-benar berasal dari SQLite.
# # # # # # # # # # # nasabah_sesudah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # deposito_sesudah = next(
# # # # # # # # # # #     deposito
# # # # # # # # # # #     for deposito in nasabah_sesudah.deposito
# # # # # # # # # # #     if deposito.ID == ID_DEPOSITO
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # rekening_sesudah = deposito_sesudah.rekening
# # # # # # # # # # #
# # # # # # # # # # # riwayat_sesudah, audit_sesudah = hitung_data_pendukung(
# # # # # # # # # # #     rekening_sesudah.norek
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SETELAH ARO POKOK")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("ID deposito       :", deposito_sesudah.ID)
# # # # # # # # # # # print("Jenis ARO         :", deposito_sesudah.jenis_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Nominal           : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(deposito_sesudah.nominal)
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Bunga baru        : {deposito_sesudah.bunga:.1%}")
# # # # # # # # # # # print("Tenor baru        :", deposito_sesudah.lama_bulan, "bulan")
# # # # # # # # # # # print("Tanggal buka baru :", deposito_sesudah.tanggal_buka)
# # # # # # # # # # # print("Jatuh tempo baru  :", deposito_sesudah.jatuh_tempo)
# # # # # # # # # # # print("Proses ARO        :", deposito_sesudah.proses_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Saldo rekening    : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(rekening_sesudah.saldo)
# # # # # # # # # # # )
# # # # # # # # # # # print("Jumlah riwayat    :", riwayat_sesudah)
# # # # # # # # # # # print("Jumlah audit      :", audit_sesudah)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.nominal == nominal_sebelum
# # # # # # # # # # # print("✅ Pokok deposito tidak berubah")
# # # # # # # # # # #
# # # # # # # # # # # assert rekening_sesudah.saldo == saldo_seharusnya
# # # # # # # # # # # print("✅ Bunga deposito masuk ke saldo rekening")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.bunga == bunga_baru_seharusnya
# # # # # # # # # # # print("✅ Bunga periode baru mengikuti tenor ARO")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.lama_bulan == lama_aro
# # # # # # # # # # # print("✅ Tenor deposito berubah mengikuti lama ARO")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.tanggal_buka == tanggal_buka_seharusnya
# # # # # # # # # # # print("✅ Tanggal buka periode baru sesuai jatuh tempo sebelumnya")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.jatuh_tempo == jatuh_tempo_seharusnya
# # # # # # # # # # # print("✅ Jatuh tempo periode baru berhasil dihitung")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.proses_aro == jatuh_tempo_sebelum
# # # # # # # # # # # print("✅ Tanggal proses ARO berhasil disimpan")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.status == StatusDeposito.AKTIF
# # # # # # # # # # # print("✅ Deposito tetap aktif setelah diperpanjang")
# # # # # # # # # # #
# # # # # # # # # # # assert riwayat_sesudah == riwayat_sebelum + 2
# # # # # # # # # # # print("✅ Riwayat bunga dan perpanjangan bertambah tepat dua")
# # # # # # # # # # #
# # # # # # # # # # # assert audit_sesudah == audit_sebelum + 1
# # # # # # # # # # # print("✅ Audit perpanjangan bertambah tepat satu")
# # # # # # # # # # #
# # # # # # # # # # # print()
# # # # # # # # # # # print("✅ ARO pokok bekerja sesuai rancangan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # from bank_djago.services.deposito.deposito_service import (
# # # # # # # # # #     DepositoService,
# # # # # # # # # #     StatusDeposito
# # # # # # # # # # )
# # # # # # # # # # from bank_djago.core.deposito import JenisAro
# # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # # NIK_PENGUJIAN = "1111222233334444"
# # # # # # # # # # # ID_DEPOSITO = 7
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # def hitung_data_pendukung(norek):
# # # # # # # # # # #     koneksi = buat_koneksi()
# # # # # # # # # # #
# # # # # # # # # # #     try:
# # # # # # # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # # # # # # #             """
# # # # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # # # #             FROM riwayat
# # # # # # # # # # #             WHERE norek = ?
# # # # # # # # # # #             """,
# # # # # # # # # # #             (norek,)
# # # # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # # # #
# # # # # # # # # # #         jumlah_audit = koneksi.execute(
# # # # # # # # # # #             """
# # # # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # # # #             FROM audit
# # # # # # # # # # #             WHERE norek = ?
# # # # # # # # # # #             """,
# # # # # # # # # # #             (norek,)
# # # # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # # # #
# # # # # # # # # # #         return jumlah_riwayat, jumlah_audit
# # # # # # # # # # #
# # # # # # # # # # #     finally:
# # # # # # # # # # #         koneksi.close()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # if nasabah is None:
# # # # # # # # # # #     raise AssertionError("Nasabah pengujian tidak ditemukan")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # deposito_aro = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         deposito
# # # # # # # # # # #         for deposito in nasabah.deposito
# # # # # # # # # # #         if deposito.ID == ID_DEPOSITO
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # if deposito_aro is None:
# # # # # # # # # # #     raise AssertionError(
# # # # # # # # # # #         f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
# # # # # # # # # # #     )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # rekening = deposito_aro.rekening
# # # # # # # # # # #
# # # # # # # # # # # saldo_sebelum = rekening.saldo
# # # # # # # # # # # nominal_sebelum = deposito_aro.nominal
# # # # # # # # # # # bunga_sebelum = deposito_aro.bunga
# # # # # # # # # # # tenor_sebelum = deposito_aro.lama_bulan
# # # # # # # # # # # tanggal_buka_sebelum = deposito_aro.tanggal_buka
# # # # # # # # # # # jatuh_tempo_sebelum = deposito_aro.jatuh_tempo
# # # # # # # # # # # lama_aro = deposito_aro.lama_aro
# # # # # # # # # # #
# # # # # # # # # # # total_pencairan = deposito_aro.total_pencairan
# # # # # # # # # # # nominal_baru_seharusnya = total_pencairan
# # # # # # # # # # # saldo_seharusnya = saldo_sebelum
# # # # # # # # # # #
# # # # # # # # # # # tanggal_buka_seharusnya = jatuh_tempo_sebelum
# # # # # # # # # # # jatuh_tempo_seharusnya = Utilitas.tambah_bulan(
# # # # # # # # # # #     tanggal_buka_seharusnya,
# # # # # # # # # # #     lama_aro
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # bunga_baru_seharusnya = DepositoService.JANGKA_WAKTU[
# # # # # # # # # # #     lama_aro
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # riwayat_sebelum, audit_sebelum = hitung_data_pendukung(
# # # # # # # # # # #     rekening.norek
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SEBELUM ARO POKOK + BUNGA")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("ID deposito       :", deposito_aro.ID)
# # # # # # # # # # # print("Jenis ARO         :", deposito_aro.jenis_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Nominal lama      : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(nominal_sebelum)
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Bunga lama        : {bunga_sebelum:.1%}")
# # # # # # # # # # # print("Tenor lama        :", tenor_sebelum, "bulan")
# # # # # # # # # # # print("Tenor ARO         :", lama_aro, "bulan")
# # # # # # # # # # # print("Tanggal buka      :", tanggal_buka_sebelum)
# # # # # # # # # # # print("Jatuh tempo       :", jatuh_tempo_sebelum)
# # # # # # # # # # # print("Proses ARO        :", deposito_aro.proses_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Total pencairan   : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(total_pencairan)
# # # # # # # # # # # )
# # # # # # # # # # # print(
# # # # # # # # # # #     "Saldo rekening    : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(saldo_sebelum)
# # # # # # # # # # # )
# # # # # # # # # # # print("Jumlah riwayat    :", riwayat_sebelum)
# # # # # # # # # # # print("Jumlah audit      :", audit_sebelum)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_aro.jenis_aro == JenisAro.POKOK_BUNGA
# # # # # # # # # # # assert deposito_aro.status == StatusDeposito.AKTIF
# # # # # # # # # # #
# # # # # # # # # # # DepositoService.perpanjangan(
# # # # # # # # # # #     deposito=deposito_aro,
# # # # # # # # # # #     hari_ini=jatuh_tempo_sebelum
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # Muat ulang agar hasil benar-benar diperiksa dari SQLite.
# # # # # # # # # # # nasabah_sesudah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # deposito_sesudah = next(
# # # # # # # # # # #     deposito
# # # # # # # # # # #     for deposito in nasabah_sesudah.deposito
# # # # # # # # # # #     if deposito.ID == ID_DEPOSITO
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # rekening_sesudah = deposito_sesudah.rekening
# # # # # # # # # # #
# # # # # # # # # # # riwayat_sesudah, audit_sesudah = hitung_data_pendukung(
# # # # # # # # # # #     rekening_sesudah.norek
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SETELAH ARO POKOK + BUNGA")
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # print("ID deposito       :", deposito_sesudah.ID)
# # # # # # # # # # # print("Jenis ARO         :", deposito_sesudah.jenis_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Nominal baru      : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(deposito_sesudah.nominal)
# # # # # # # # # # # )
# # # # # # # # # # # print(f"Bunga baru        : {deposito_sesudah.bunga:.1%}")
# # # # # # # # # # # print("Tenor baru        :", deposito_sesudah.lama_bulan, "bulan")
# # # # # # # # # # # print("Tanggal buka baru :", deposito_sesudah.tanggal_buka)
# # # # # # # # # # # print("Jatuh tempo baru  :", deposito_sesudah.jatuh_tempo)
# # # # # # # # # # # print("Proses ARO        :", deposito_sesudah.proses_aro)
# # # # # # # # # # # print(
# # # # # # # # # # #     "Saldo rekening    : Rp"
# # # # # # # # # # #     + Utilitas.format_rupiah(rekening_sesudah.saldo)
# # # # # # # # # # # )
# # # # # # # # # # # print("Jumlah riwayat    :", riwayat_sesudah)
# # # # # # # # # # # print("Jumlah audit      :", audit_sesudah)
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.nominal == nominal_baru_seharusnya
# # # # # # # # # # # print("✅ Pokok dan bunga menjadi nominal deposito baru")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.nominal > nominal_sebelum
# # # # # # # # # # # print("✅ Nominal deposito bertambah sebesar bunga")
# # # # # # # # # # #
# # # # # # # # # # # assert rekening_sesudah.saldo == saldo_seharusnya
# # # # # # # # # # # print("✅ Saldo rekening tidak berubah")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.bunga == bunga_baru_seharusnya
# # # # # # # # # # # print("✅ Bunga periode baru mengikuti tenor ARO")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.lama_bulan == lama_aro
# # # # # # # # # # # print("✅ Tenor deposito berubah mengikuti lama ARO")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.tanggal_buka == tanggal_buka_seharusnya
# # # # # # # # # # # print("✅ Tanggal buka baru sesuai jatuh tempo sebelumnya")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.jatuh_tempo == jatuh_tempo_seharusnya
# # # # # # # # # # # print("✅ Jatuh tempo periode baru berhasil dihitung")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.proses_aro == jatuh_tempo_sebelum
# # # # # # # # # # # print("✅ Tanggal proses ARO berhasil disimpan")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_sesudah.status == StatusDeposito.AKTIF
# # # # # # # # # # # print("✅ Deposito tetap aktif setelah diperpanjang")
# # # # # # # # # # #
# # # # # # # # # # # assert riwayat_sesudah == riwayat_sebelum + 1
# # # # # # # # # # # print("✅ Riwayat perpanjangan bertambah tepat satu")
# # # # # # # # # # #
# # # # # # # # # # # assert audit_sesudah == audit_sebelum + 1
# # # # # # # # # # # print("✅ Audit perpanjangan bertambah tepat satu")
# # # # # # # # # # #
# # # # # # # # # # # print()
# # # # # # # # # # # print("✅ ARO pokok + bunga bekerja sesuai rancangan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
# # # # # # # # # # # from bank_djago.services.deposito.deposito_service import StatusDeposito
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()
# # # # # # # # # # #
# # # # # # # # # # # print("HASIL PEMUATAN DEPOSITO AKTIF")
# # # # # # # # # # # print("Jumlah deposito aktif:", len(daftar_deposito))
# # # # # # # # # # # print()
# # # # # # # # # # #
# # # # # # # # # # # if not daftar_deposito:
# # # # # # # # # # #     raise AssertionError("Tidak ada deposito aktif yang berhasil dimuat")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # for deposito in daftar_deposito:
# # # # # # # # # # #     print(f"DEPOSITO ID {deposito.ID}")
# # # # # # # # # # #     print("NIK pemilik      :", deposito.pemilik.NIK)
# # # # # # # # # # #     print("Nama pemilik     :", deposito.pemilik.nama)
# # # # # # # # # # #     print("Norek            :", deposito.rekening.norek)
# # # # # # # # # # #     print(
# # # # # # # # # # #         "Nominal          : Rp"
# # # # # # # # # # #         + Utilitas.format_rupiah(deposito.nominal)
# # # # # # # # # # #     )
# # # # # # # # # # #     print("Status           :", deposito.status)
# # # # # # # # # # #     print("Jenis ARO        :", deposito.jenis_aro)
# # # # # # # # # # #     print("Lama ARO         :", deposito.lama_aro)
# # # # # # # # # # #     print("Tanggal buka     :", deposito.tanggal_buka)
# # # # # # # # # # #     print("Jatuh tempo      :", deposito.jatuh_tempo)
# # # # # # # # # # #     print("Proses ARO       :", deposito.proses_aro)
# # # # # # # # # # #     print("ID objek nasabah :", id(deposito.pemilik))
# # # # # # # # # # #     print("ID objek rekening:", id(deposito.rekening))
# # # # # # # # # # #     print()
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert all(
# # # # # # # # # # #     deposito.status == StatusDeposito.AKTIF
# # # # # # # # # # #     for deposito in daftar_deposito
# # # # # # # # # # # )
# # # # # # # # # # # print("✅ Loader hanya mengembalikan deposito aktif")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # daftar_id = [
# # # # # # # # # # #     deposito.ID
# # # # # # # # # # #     for deposito in daftar_deposito
# # # # # # # # # # # ]
# # # # # # # # # # #
# # # # # # # # # # # assert len(daftar_id) == len(set(daftar_id))
# # # # # # # # # # # print("✅ Tidak ada deposito yang dimuat dua kali")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # for deposito in daftar_deposito:
# # # # # # # # # # #     assert deposito.rekening.pemilik is deposito.pemilik
# # # # # # # # # # #
# # # # # # # # # # # print("✅ Setiap rekening menunjuk objek nasabah yang benar")
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # deposito_6 = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         deposito
# # # # # # # # # # #         for deposito in daftar_deposito
# # # # # # # # # # #         if deposito.ID == 6
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # deposito_7 = next(
# # # # # # # # # # #     (
# # # # # # # # # # #         deposito
# # # # # # # # # # #         for deposito in daftar_deposito
# # # # # # # # # # #         if deposito.ID == 7
# # # # # # # # # # #     ),
# # # # # # # # # # #     None
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # if deposito_6 is None or deposito_7 is None:
# # # # # # # # # # #     raise AssertionError(
# # # # # # # # # # #         "Deposito ID 6 atau ID 7 tidak ditemukan dalam daftar aktif"
# # # # # # # # # # #     )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_6.pemilik is deposito_7.pemilik
# # # # # # # # # # # print("✅ Deposito ID 6 dan 7 memakai objek nasabah yang sama")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_6.rekening is deposito_7.rekening
# # # # # # # # # # # print("✅ Deposito ID 6 dan 7 memakai objek rekening yang sama")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_6 in deposito_6.pemilik.deposito
# # # # # # # # # # # assert deposito_7 in deposito_7.pemilik.deposito
# # # # # # # # # # # print("✅ Kedua deposito tersimpan dalam list deposito nasabah")
# # # # # # # # # # #
# # # # # # # # # # # assert deposito_6.rekening in deposito_6.pemilik.rekening
# # # # # # # # # # # print("✅ Rekening tersimpan dalam list rekening nasabah")
# # # # # # # # # # #
# # # # # # # # # # # print()
# # # # # # # # # # # print("✅ DepositoLoader bekerja sesuai rancangan identity map")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # import datetime
# # # # # # # # # # #
# # # # # # # # # # # from bank_djago.penyimpanan.storage import JsonStorage
# # # # # # # # # # # from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
# # # # # # # # # # # from bank_djago.services.scheduler import Scheduler
# # # # # # # # # # # from bank_djago.utils.utility import Utilitas
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # ID_ARO_POKOK = 6
# # # # # # # # # # # ID_ARO_POKOK_BUNGA = 7
# # # # # # # # # # # HARI_PENGUJIAN = datetime.date(2026, 12, 28)
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # def cari_deposito(daftar_deposito, id_deposito):
# # # # # # # # # # #     for deposito in daftar_deposito:
# # # # # # # # # # #         if deposito.ID == id_deposito:
# # # # # # # # # # #             return deposito
# # # # # # # # # # #
# # # # # # # # # # #     raise ValueError(
# # # # # # # # # # #         f"Deposito dengan ID {id_deposito} tidak ditemukan"
# # # # # # # # # # #     )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # Scheduler masih membutuhkan objek bank karena pinjaman belum dimigrasikan.
# # # # # # # # # # # bank = JsonStorage.muat_bank()
# # # # # # # # # # #
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # KONDISI SEBELUM SCHEDULER
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # #
# # # # # # # # # # # daftar_sebelum = DepositoLoader.muat_semua_deposito_aktif()
# # # # # # # # # # #
# # # # # # # # # # # aro_pokok_sebelum = cari_deposito(
# # # # # # # # # # #     daftar_sebelum,
# # # # # # # # # # #     ID_ARO_POKOK
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # aro_pokok_bunga_sebelum = cari_deposito(
# # # # # # # # # # #     daftar_sebelum,
# # # # # # # # # # #     ID_ARO_POKOK_BUNGA
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # saldo_sebelum = aro_pokok_sebelum.rekening.saldo
# # # # # # # # # # #
# # # # # # # # # # # nominal_pokok_sebelum = aro_pokok_sebelum.nominal
# # # # # # # # # # # nominal_pokok_bunga_sebelum = aro_pokok_bunga_sebelum.nominal
# # # # # # # # # # #
# # # # # # # # # # # total_pokok = aro_pokok_sebelum.total_pencairan
# # # # # # # # # # # total_pokok_bunga = aro_pokok_bunga_sebelum.total_pencairan
# # # # # # # # # # #
# # # # # # # # # # # bunga_pokok_diterima = total_pokok - nominal_pokok_sebelum
# # # # # # # # # # #
# # # # # # # # # # # jatuh_tempo_pokok_sebelum = aro_pokok_sebelum.jatuh_tempo
# # # # # # # # # # # jatuh_tempo_pokok_bunga_sebelum = (
# # # # # # # # # # #     aro_pokok_bunga_sebelum.jatuh_tempo
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # print("KONDISI SEBELUM SCHEDULER\n")
# # # # # # # # # # #
# # # # # # # # # # # print("Saldo rekening       :",
# # # # # # # # # # #       f"Rp{Utilitas.format_rupiah(saldo_sebelum)}")
# # # # # # # # # # #
# # # # # # # # # # # print("\nARO POKOK")
# # # # # # # # # # # print("ID                   :", aro_pokok_sebelum.ID)
# # # # # # # # # # # print("Nominal              :",
# # # # # # # # # # #       f"Rp{Utilitas.format_rupiah(nominal_pokok_sebelum)}")
# # # # # # # # # # # print("Jatuh tempo          :", jatuh_tempo_pokok_sebelum)
# # # # # # # # # # # print("Proses ARO           :", aro_pokok_sebelum.proses_aro)
# # # # # # # # # # #
# # # # # # # # # # # print("\nARO POKOK + BUNGA")
# # # # # # # # # # # print("ID                   :", aro_pokok_bunga_sebelum.ID)
# # # # # # # # # # # print("Nominal              :",
# # # # # # # # # # #       f"Rp{Utilitas.format_rupiah(nominal_pokok_bunga_sebelum)}")
# # # # # # # # # # # print("Jatuh tempo          :", jatuh_tempo_pokok_bunga_sebelum)
# # # # # # # # # # # print("Proses ARO           :", aro_pokok_bunga_sebelum.proses_aro)
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # JALANKAN SCHEDULER DENGAN WAKTU BUATAN
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # #
# # # # # # # # # # # print("\nMenjalankan scheduler pada", HARI_PENGUJIAN)
# # # # # # # # # # #
# # # # # # # # # # # Scheduler.jalankan(
# # # # # # # # # # #     bank=bank,
# # # # # # # # # # #     hari_ini=HARI_PENGUJIAN
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # MUAT ULANG DARI SQLITE
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # #
# # # # # # # # # # # daftar_sesudah = DepositoLoader.muat_semua_deposito_aktif()
# # # # # # # # # # #
# # # # # # # # # # # aro_pokok_sesudah = cari_deposito(
# # # # # # # # # # #     daftar_sesudah,
# # # # # # # # # # #     ID_ARO_POKOK
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # aro_pokok_bunga_sesudah = cari_deposito(
# # # # # # # # # # #     daftar_sesudah,
# # # # # # # # # # #     ID_ARO_POKOK_BUNGA
# # # # # # # # # # # )
# # # # # # # # # # #
# # # # # # # # # # # saldo_sesudah = aro_pokok_sesudah.rekening.saldo
# # # # # # # # # # #
# # # # # # # # # # # print("\nKONDISI SETELAH SCHEDULER\n")
# # # # # # # # # # #
# # # # # # # # # # # print("Saldo rekening       :",
# # # # # # # # # # #       f"Rp{Utilitas.format_rupiah(saldo_sesudah)}")
# # # # # # # # # # #
# # # # # # # # # # # print("\nARO POKOK")
# # # # # # # # # # # print("Nominal baru         :",
# # # # # # # # # # #       f"Rp{Utilitas.format_rupiah(aro_pokok_sesudah.nominal)}")
# # # # # # # # # # # print("Tanggal buka baru    :", aro_pokok_sesudah.tanggal_buka)
# # # # # # # # # # # print("Jatuh tempo baru     :", aro_pokok_sesudah.jatuh_tempo)
# # # # # # # # # # # print("Proses ARO           :", aro_pokok_sesudah.proses_aro)
# # # # # # # # # # #
# # # # # # # # # # # print("\nARO POKOK + BUNGA")
# # # # # # # # # # # print("Nominal baru         :",
# # # # # # # # # # #       f"Rp{Utilitas.format_rupiah(aro_pokok_bunga_sesudah.nominal)}")
# # # # # # # # # # # print("Tanggal buka baru    :", aro_pokok_bunga_sesudah.tanggal_buka)
# # # # # # # # # # # print("Jatuh tempo baru     :", aro_pokok_bunga_sesudah.jatuh_tempo)
# # # # # # # # # # # print("Proses ARO           :", aro_pokok_bunga_sesudah.proses_aro)
# # # # # # # # # # #
# # # # # # # # # # #
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # # # PENGECEKAN HASIL
# # # # # # # # # # # # --------------------------------------------------
# # # # # # # # # # #
# # # # # # # # # # # saldo_yang_diharapkan = saldo_sebelum + bunga_pokok_diterima
# # # # # # # # # # #
# # # # # # # # # # # assert aro_pokok_sesudah.nominal == nominal_pokok_sebelum
# # # # # # # # # # # print("\n✅ Nominal ARO pokok tidak berubah")
# # # # # # # # # # #
# # # # # # # # # # # assert aro_pokok_bunga_sesudah.nominal == total_pokok_bunga
# # # # # # # # # # # print("✅ Bunga ARO pokok+bunga masuk ke nominal baru")
# # # # # # # # # # #
# # # # # # # # # # # assert saldo_sesudah == saldo_yang_diharapkan
# # # # # # # # # # # print("✅ Hanya bunga ARO pokok yang masuk ke saldo rekening")
# # # # # # # # # # #
# # # # # # # # # # # assert (
# # # # # # # # # # #     aro_pokok_sesudah.tanggal_buka
# # # # # # # # # # #     == jatuh_tempo_pokok_sebelum
# # # # # # # # # # # )
# # # # # # # # # # # print("✅ Periode baru ARO pokok dimulai dari jatuh tempo lama")
# # # # # # # # # # #
# # # # # # # # # # # assert (
# # # # # # # # # # #     aro_pokok_bunga_sesudah.tanggal_buka
# # # # # # # # # # #     == jatuh_tempo_pokok_bunga_sebelum
# # # # # # # # # # # )
# # # # # # # # # # # print("✅ Periode baru ARO pokok+bunga dimulai dari jatuh tempo lama")
# # # # # # # # # # #
# # # # # # # # # # # assert aro_pokok_sesudah.proses_aro == HARI_PENGUJIAN
# # # # # # # # # # # assert aro_pokok_bunga_sesudah.proses_aro == HARI_PENGUJIAN
# # # # # # # # # # # print("✅ Tanggal proses kedua ARO berhasil disimpan")
# # # # # # # # # # #
# # # # # # # # # # # assert (
# # # # # # # # # # #     aro_pokok_sesudah.rekening
# # # # # # # # # # #     is aro_pokok_bunga_sesudah.rekening
# # # # # # # # # # # )
# # # # # # # # # # # print("✅ Kedua deposito memakai objek rekening yang sama")
# # # # # # # # # # #
# # # # # # # # # # # assert (
# # # # # # # # # # #     aro_pokok_sesudah.pemilik
# # # # # # # # # # #     is aro_pokok_bunga_sesudah.pemilik
# # # # # # # # # # # )
# # # # # # # # # # # print("✅ Kedua deposito memakai objek nasabah yang sama")
# # # # # # # # # # #
# # # # # # # # # # # print("\n✅ Scheduler deposito bekerja sesuai rancangan")
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # # from bank_djago.utils.utility import JenisReferensiID
# # # # # # # # # #
# # # # # # # # # #
# # # # # # # # # # norek = "3001781978899033"
# # # # # # # # # # nominal_deposito = 1_000_000
# # # # # # # # # # tenor = 1
# # # # # # # # # #
# # # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # #
# # # # # # # # # # try:
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # 1. Cari transaksi pembukaan deposito terbaru
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     transaksi = koneksi.execute(
# # # # # # # # # #         """
# # # # # # # # # #         SELECT *
# # # # # # # # # #         FROM transaksi
# # # # # # # # # #         WHERE norek_sumber = ?
# # # # # # # # # #           AND jenis = 'pembukaan_deposito'
# # # # # # # # # #         ORDER BY id DESC
# # # # # # # # # #         LIMIT 1
# # # # # # # # # #         """,
# # # # # # # # # #         (norek,)
# # # # # # # # # #     ).fetchone()
# # # # # # # # # #
# # # # # # # # # #     if transaksi is None:
# # # # # # # # # #         raise ValueError(
# # # # # # # # # #             "Transaksi pembukaan deposito tidak ditemukan"
# # # # # # # # # #         )
# # # # # # # # # #
# # # # # # # # # #     id_transaksi = transaksi["id"]
# # # # # # # # # #     id_deposito = transaksi["id_referensi"]
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # 2. Ambil rekening dan deposito terkait
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     rekening = koneksi.execute(
# # # # # # # # # #         """
# # # # # # # # # #         SELECT *
# # # # # # # # # #         FROM rekening
# # # # # # # # # #         WHERE norek = ?
# # # # # # # # # #         """,
# # # # # # # # # #         (norek,)
# # # # # # # # # #     ).fetchone()
# # # # # # # # # #
# # # # # # # # # #     deposito = koneksi.execute(
# # # # # # # # # #         """
# # # # # # # # # #         SELECT *
# # # # # # # # # #         FROM deposito
# # # # # # # # # #         WHERE id = ?
# # # # # # # # # #         """,
# # # # # # # # # #         (id_deposito,)
# # # # # # # # # #     ).fetchone()
# # # # # # # # # #
# # # # # # # # # #     if rekening is None:
# # # # # # # # # #         raise ValueError("Rekening tidak ditemukan")
# # # # # # # # # #
# # # # # # # # # #     if deposito is None:
# # # # # # # # # #         raise ValueError(
# # # # # # # # # #             "Deposito yang dirujuk transaksi tidak ditemukan"
# # # # # # # # # #         )
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # 3. Ambil audit dan riwayat terkait
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     daftar_riwayat = koneksi.execute(
# # # # # # # # # #         """
# # # # # # # # # #         SELECT *
# # # # # # # # # #         FROM riwayat
# # # # # # # # # #         WHERE transaksi_id = ?
# # # # # # # # # #         ORDER BY id ASC
# # # # # # # # # #         """,
# # # # # # # # # #         (id_transaksi,)
# # # # # # # # # #     ).fetchall()
# # # # # # # # # #
# # # # # # # # # #     daftar_audit = koneksi.execute(
# # # # # # # # # #         """
# # # # # # # # # #         SELECT *
# # # # # # # # # #         FROM audit
# # # # # # # # # #         WHERE transaksi_id = ?
# # # # # # # # # #         ORDER BY id ASC
# # # # # # # # # #         """,
# # # # # # # # # #         (id_transaksi,)
# # # # # # # # # #     ).fetchall()
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # Tampilkan rekening
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     print("=== DATA REKENING ===")
# # # # # # # # # #     print(f"Nomor rekening       : {rekening['norek']}")
# # # # # # # # # #     print(f"Saldo sekarang       : {rekening['saldo']}")
# # # # # # # # # #     print(f"Status               : {rekening['status']}")
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # Tampilkan deposito
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     print("\n=== DATA DEPOSITO ===")
# # # # # # # # # #     print(f"ID deposito          : {deposito['id']}")
# # # # # # # # # #     print(f"Nomor rekening       : {deposito['norek']}")
# # # # # # # # # #     print(f"Nominal              : {deposito['nominal']}")
# # # # # # # # # #     print(f"Tenor                : {deposito['lama_bulan']}")
# # # # # # # # # #     print(f"Jenis ARO            : {deposito['jenis_aro']}")
# # # # # # # # # #     print(f"Status               : {deposito['status']}")
# # # # # # # # # #     print(f"Tanggal buka         : {deposito['tanggal_buka']}")
# # # # # # # # # #     print(f"Jatuh tempo          : {deposito['jatuh_tempo']}")
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # Tampilkan transaksi
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     print("\n=== DATA TRANSAKSI ===")
# # # # # # # # # #     print(f"ID transaksi         : {transaksi['id']}")
# # # # # # # # # #     print(f"Jenis                : {transaksi['jenis']}")
# # # # # # # # # #     print(f"Rekening sumber      : {transaksi['norek_sumber']}")
# # # # # # # # # #     print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
# # # # # # # # # #     print(f"Nominal              : {transaksi['nominal']}")
# # # # # # # # # #     print(
# # # # # # # # # #         f"Saldo sumber sebelum : "
# # # # # # # # # #         f"{transaksi['saldo_sumber_sebelum']}"
# # # # # # # # # #     )
# # # # # # # # # #     print(
# # # # # # # # # #         f"Saldo sumber sesudah : "
# # # # # # # # # #         f"{transaksi['saldo_sumber_sesudah']}"
# # # # # # # # # #     )
# # # # # # # # # #     print(
# # # # # # # # # #         f"Jenis referensi      : "
# # # # # # # # # #         f"{transaksi['jenis_referensi']}"
# # # # # # # # # #     )
# # # # # # # # # #     print(f"ID referensi         : {transaksi['id_referensi']}")
# # # # # # # # # #     print(f"Waktu                : {transaksi['waktu']}")
# # # # # # # # # #
# # # # # # # # # #     print("\n=== RIWAYAT TERHUBUNG ===")
# # # # # # # # # #
# # # # # # # # # #     for riwayat in daftar_riwayat:
# # # # # # # # # #         print(
# # # # # # # # # #             f"ID {riwayat['id']} | "
# # # # # # # # # #             f"Transaksi {riwayat['transaksi_id']} | "
# # # # # # # # # #             f"{riwayat['jenis']} | "
# # # # # # # # # #             f"{riwayat['log']}"
# # # # # # # # # #         )
# # # # # # # # # #
# # # # # # # # # #     print("\n=== AUDIT TERHUBUNG ===")
# # # # # # # # # #
# # # # # # # # # #     for audit in daftar_audit:
# # # # # # # # # #         print(
# # # # # # # # # #             f"ID {audit['id']} | "
# # # # # # # # # #             f"Transaksi {audit['transaksi_id']} | "
# # # # # # # # # #             f"{audit['jenis']} | "
# # # # # # # # # #             f"{audit['log']}"
# # # # # # # # # #         )
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # 4. Periksa data deposito
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     assert deposito["norek"] == norek
# # # # # # # # # #     assert deposito["nominal"] == nominal_deposito
# # # # # # # # # #     assert deposito["lama_bulan"] == tenor
# # # # # # # # # #     assert deposito["jenis_aro"] == "tidak"
# # # # # # # # # #     assert deposito["status"] == "aktif"
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # 5. Periksa transaksi
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     assert transaksi["jenis"] == "pembukaan_deposito"
# # # # # # # # # #     assert transaksi["norek_sumber"] == norek
# # # # # # # # # #     assert transaksi["norek_tujuan"] is None
# # # # # # # # # #     assert transaksi["nominal"] == nominal_deposito
# # # # # # # # # #
# # # # # # # # # #     assert transaksi["saldo_sumber_sebelum"] - nominal_deposito == (
# # # # # # # # # #         transaksi["saldo_sumber_sesudah"]
# # # # # # # # # #     )
# # # # # # # # # #
# # # # # # # # # #     assert rekening["saldo"] == (
# # # # # # # # # #         transaksi["saldo_sumber_sesudah"]
# # # # # # # # # #     )
# # # # # # # # # #
# # # # # # # # # #     assert str(transaksi["jenis_referensi"]) == str(
# # # # # # # # # #         JenisReferensiID.DEPOSITO.value
# # # # # # # # # #     )
# # # # # # # # # #
# # # # # # # # # #     assert transaksi["id_referensi"] == deposito["id"]
# # # # # # # # # #     assert transaksi["waktu"] is not None
# # # # # # # # # #
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     # 6. Periksa hubungan audit dan riwayat
# # # # # # # # # #     # ==========================================================
# # # # # # # # # #     assert len(daftar_riwayat) == 1
# # # # # # # # # #     assert len(daftar_audit) == 1
# # # # # # # # # #
# # # # # # # # # #     assert daftar_riwayat[0]["norek"] == norek
# # # # # # # # # #     assert daftar_riwayat[0]["transaksi_id"] == id_transaksi
# # # # # # # # # #
# # # # # # # # # #     assert daftar_audit[0]["norek"] == norek
# # # # # # # # # #     assert daftar_audit[0]["transaksi_id"] == id_transaksi
# # # # # # # # # #
# # # # # # # # # #     print(
# # # # # # # # # #         "\n✅ Pembukaan deposito dan transaksi "
# # # # # # # # # #         "tersimpan dengan benar"
# # # # # # # # # #     )
# # # # # # # # # #
# # # # # # # # # # finally:
# # # # # # # # # #     koneksi.close()
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # from unittest.mock import patch
# # # # # # # # #
# # # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # # from bank_djago.penyimpanan.loaders.rekening_loaders import (
# # # # # # # # #     RekeningLoader
# # # # # # # # # )
# # # # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # # # #     AuditRepository
# # # # # # # # # )
# # # # # # # # # from bank_djago.services.deposito.deposito_service import (
# # # # # # # # #     DepositoService,
# # # # # # # # #     JenisAro
# # # # # # # # # )
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # norek = "3001781978899033"
# # # # # # # # # nominal_deposito = 1_000_000
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # def ambil_kondisi_database():
# # # # # # # # #     koneksi = buat_koneksi()
# # # # # # # # #
# # # # # # # # #     try:
# # # # # # # # #         rekening = koneksi.execute(
# # # # # # # # #             """
# # # # # # # # #             SELECT saldo, status
# # # # # # # # #             FROM rekening
# # # # # # # # #             WHERE norek = ?
# # # # # # # # #             """,
# # # # # # # # #             (norek,)
# # # # # # # # #         ).fetchone()
# # # # # # # # #
# # # # # # # # #         jumlah_deposito = koneksi.execute(
# # # # # # # # #             """
# # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # #             FROM deposito
# # # # # # # # #             WHERE norek = ?
# # # # # # # # #             """,
# # # # # # # # #             (norek,)
# # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # #
# # # # # # # # #         jumlah_transaksi = koneksi.execute(
# # # # # # # # #             """
# # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # #             FROM transaksi
# # # # # # # # #             """
# # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # #
# # # # # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # # # # #             """
# # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # #             FROM riwayat
# # # # # # # # #             """
# # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # #
# # # # # # # # #         jumlah_audit = koneksi.execute(
# # # # # # # # #             """
# # # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # # #             FROM audit
# # # # # # # # #             """
# # # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # # #
# # # # # # # # #         return {
# # # # # # # # #             "saldo": rekening["saldo"],
# # # # # # # # #             "status": rekening["status"],
# # # # # # # # #             "jumlah_deposito": jumlah_deposito,
# # # # # # # # #             "jumlah_transaksi": jumlah_transaksi,
# # # # # # # # #             "jumlah_riwayat": jumlah_riwayat,
# # # # # # # # #             "jumlah_audit": jumlah_audit
# # # # # # # # #         }
# # # # # # # # #
# # # # # # # # #     finally:
# # # # # # # # #         koneksi.close()
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # ==========================================================
# # # # # # # # # # 1. Simpan kondisi sebelum pengujian
# # # # # # # # # # ==========================================================
# # # # # # # # # kondisi_sebelum = ambil_kondisi_database()
# # # # # # # # #
# # # # # # # # # print("=== KONDISI SEBELUM ===")
# # # # # # # # # print(kondisi_sebelum)
# # # # # # # # #
# # # # # # # # # assert kondisi_sebelum["saldo"] == 7_890_011
# # # # # # # # # assert kondisi_sebelum["status"] == "aktif"
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # koneksi = buat_koneksi()
# # # # # # # # # # ==========================================================
# # # # # # # # # # 2. Muat objek rekening
# # # # # # # # # # ==========================================================
# # # # # # # # # rekening = RekeningLoader.muat_rekening(norek,koneksi)
# # # # # # # # #
# # # # # # # # # saldo_objek_sebelum = rekening.saldo
# # # # # # # # # jumlah_deposito_objek_sebelum = len(
# # # # # # # # #     rekening.pemilik.deposito
# # # # # # # # # )
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # ==========================================================
# # # # # # # # # # 3. Paksa penyimpanan audit gagal
# # # # # # # # # # ==========================================================
# # # # # # # # # try:
# # # # # # # # #     with patch.object(
# # # # # # # # #         AuditRepository,
# # # # # # # # #         "tambah_audit",
# # # # # # # # #         side_effect=RuntimeError(
# # # # # # # # #             "Kegagalan audit untuk menguji rollback deposito"
# # # # # # # # #         )
# # # # # # # # #     ):
# # # # # # # # #         DepositoService.buka_deposito(
# # # # # # # # #             rekening=rekening,
# # # # # # # # #             nominal=nominal_deposito,
# # # # # # # # #             lama_bulan=1,
# # # # # # # # #             jenis_aro=JenisAro.TIDAK
# # # # # # # # #         )
# # # # # # # # #
# # # # # # # # #     raise AssertionError(
# # # # # # # # #         "Pembukaan deposito seharusnya gagal"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # # except RuntimeError as error:
# # # # # # # # #     assert str(error) == (
# # # # # # # # #         "Kegagalan audit untuk menguji rollback deposito"
# # # # # # # # #     )
# # # # # # # # #
# # # # # # # # #     print("\n✅ Kegagalan buatan berhasil dipicu")
# # # # # # # # #     print(f"Pesan error: {error}")
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # ==========================================================
# # # # # # # # # # 4. Ambil kondisi setelah rollback
# # # # # # # # # # ==========================================================
# # # # # # # # # kondisi_sesudah = ambil_kondisi_database()
# # # # # # # # #
# # # # # # # # # print("\n=== KONDISI SETELAH ROLLBACK ===")
# # # # # # # # # print(kondisi_sesudah)
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # ==========================================================
# # # # # # # # # # 5. Pastikan database tidak berubah
# # # # # # # # # # ==========================================================
# # # # # # # # # assert kondisi_sesudah == kondisi_sebelum
# # # # # # # # #
# # # # # # # # #
# # # # # # # # # # ==========================================================
# # # # # # # # # # 6. Pastikan objek Python tidak berubah
# # # # # # # # # # ==========================================================
# # # # # # # # # assert rekening.saldo == saldo_objek_sebelum
# # # # # # # # #
# # # # # # # # # assert len(rekening.pemilik.deposito) == (
# # # # # # # # #     jumlah_deposito_objek_sebelum
# # # # # # # # # )
# # # # # # # # #
# # # # # # # # # print(
# # # # # # # # #     "\n✅ ROLLBACK DEPOSITO BERHASIL: saldo, deposito, "
# # # # # # # # #     "transaksi, riwayat, audit, dan objek tidak berubah"
# # # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # #
# # # # # # # #
# # # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # # from bank_djago.penyimpanan.loaders.deposito_loader import (
# # # # # # # #     DepositoLoader
# # # # # # # # )
# # # # # # # # from bank_djago.services.deposito.deposito_service import (
# # # # # # # #     DepositoService,
# # # # # # # #     StatusDeposito
# # # # # # # # )
# # # # # # # # from bank_djago.utils.utility import JenisReferensiID
# # # # # # # #
# # # # # # # #
# # # # # # # # ID_DEPOSITO = 10
# # # # # # # # NOREK = "3001781978899033"
# # # # # # # #
# # # # # # # #
# # # # # # # # def ambil_kondisi_database():
# # # # # # # #     """
# # # # # # # #     Mengambil kondisi terbaru langsung dari SQLite.
# # # # # # # #
# # # # # # # #     Data ini digunakan untuk membandingkan kondisi rekening
# # # # # # # #     dan deposito sebelum serta sesudah pencairan.
# # # # # # # #     """
# # # # # # # #     koneksi = buat_koneksi()
# # # # # # # #
# # # # # # # #     try:
# # # # # # # #         rekening = koneksi.execute(
# # # # # # # #             """
# # # # # # # #             SELECT norek, saldo, status
# # # # # # # #             FROM rekening
# # # # # # # #             WHERE norek = ?
# # # # # # # #             """,
# # # # # # # #             (NOREK,)
# # # # # # # #         ).fetchone()
# # # # # # # #
# # # # # # # #         deposito = koneksi.execute(
# # # # # # # #             """
# # # # # # # #             SELECT *
# # # # # # # #             FROM deposito
# # # # # # # #             WHERE id = ?
# # # # # # # #             """,
# # # # # # # #             (ID_DEPOSITO,)
# # # # # # # #         ).fetchone()
# # # # # # # #
# # # # # # # #         jumlah_transaksi = koneksi.execute(
# # # # # # # #             """
# # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # #             FROM transaksi
# # # # # # # #             WHERE id_referensi = ?
# # # # # # # #               AND jenis_referensi = ?
# # # # # # # #             """,
# # # # # # # #             (
# # # # # # # #                 ID_DEPOSITO,
# # # # # # # #                 JenisReferensiID.DEPOSITO.value
# # # # # # # #             )
# # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # #
# # # # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # # # #             """
# # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # #             FROM riwayat
# # # # # # # #             WHERE norek = ?
# # # # # # # #             """,
# # # # # # # #             (NOREK,)
# # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # #
# # # # # # # #         jumlah_audit = koneksi.execute(
# # # # # # # #             """
# # # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # # #             FROM audit
# # # # # # # #             WHERE norek = ?
# # # # # # # #             """,
# # # # # # # #             (NOREK,)
# # # # # # # #         ).fetchone()["jumlah"]
# # # # # # # #
# # # # # # # #         return {
# # # # # # # #             "rekening": rekening,
# # # # # # # #             "deposito": deposito,
# # # # # # # #             "jumlah_transaksi": jumlah_transaksi,
# # # # # # # #             "jumlah_riwayat": jumlah_riwayat,
# # # # # # # #             "jumlah_audit": jumlah_audit
# # # # # # # #         }
# # # # # # # #
# # # # # # # #     finally:
# # # # # # # #         koneksi.close()
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 1. Muat deposito aktif dari SQLite
# # # # # # # # # ==========================================================
# # # # # # # # # Loader membentuk kembali objek deposito beserta rekening
# # # # # # # # # dan nasabahnya tanpa melewati main.py.
# # # # # # # # daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()
# # # # # # # #
# # # # # # # # deposito = next(
# # # # # # # #     (
# # # # # # # #         item
# # # # # # # #         for item in daftar_deposito
# # # # # # # #         if item.ID == ID_DEPOSITO
# # # # # # # #     ),
# # # # # # # #     None
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert deposito is not None, (
# # # # # # # #     f"Deposito ber-ID {ID_DEPOSITO} tidak ditemukan "
# # # # # # # #     "dalam daftar deposito aktif"
# # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 2. Simpan kondisi awal
# # # # # # # # # ==========================================================
# # # # # # # # kondisi_sebelum = ambil_kondisi_database()
# # # # # # # #
# # # # # # # # rekening_sebelum = kondisi_sebelum["rekening"]
# # # # # # # # deposito_sebelum = kondisi_sebelum["deposito"]
# # # # # # # #
# # # # # # # # assert rekening_sebelum is not None, (
# # # # # # # #     "Rekening pengujian tidak ditemukan"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert deposito_sebelum is not None, (
# # # # # # # #     "Deposito pengujian tidak ditemukan"
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert deposito_sebelum["status"] == StatusDeposito.AKTIF, (
# # # # # # # #     "Deposito sudah tidak aktif. "
# # # # # # # #     "Gunakan deposito aktif yang belum pernah dicairkan."
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert deposito_sebelum["jenis_aro"] == "tidak", (
# # # # # # # #     "Pengujian ini khusus deposito non-ARO"
# # # # # # # # )
# # # # # # # #
# # # # # # # # saldo_sebelum = rekening_sebelum["saldo"]
# # # # # # # #
# # # # # # # # # Properti total_pencairan menghitung pokok ditambah bunga.
# # # # # # # # total_pencairan_yang_diharapkan = deposito.total_pencairan
# # # # # # # # saldo_sesudah_yang_diharapkan = (
# # # # # # # #     saldo_sebelum + total_pencairan_yang_diharapkan
# # # # # # # # )
# # # # # # # #
# # # # # # # # print("=== KONDISI SEBELUM ===")
# # # # # # # # print(f"ID deposito       : {deposito.ID}")
# # # # # # # # print(f"Status deposito   : {deposito.status}")
# # # # # # # # print(f"Tanggal buka      : {deposito.tanggal_buka}")
# # # # # # # # print(f"Jatuh tempo       : {deposito.jatuh_tempo}")
# # # # # # # # print(f"Nominal deposito  : {deposito.nominal}")
# # # # # # # # print(f"Total pencairan   : {total_pencairan_yang_diharapkan}")
# # # # # # # # print(f"Saldo rekening    : {saldo_sebelum}")
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 3. Manipulasi waktu di dalam file pengujian
# # # # # # # # # ==========================================================
# # # # # # # # # Kita menggunakan tanggal jatuh tempo milik deposito sebagai
# # # # # # # # # hari simulasi. Tanggal sistem dan main.py tidak berubah.
# # # # # # # # hari_simulasi = deposito.jatuh_tempo
# # # # # # # #
# # # # # # # # print("\n=== WAKTU SIMULASI ===")
# # # # # # # # print(f"Hari simulasi     : {hari_simulasi}")
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 4. Ubah deposito dari aktif menjadi jatuh tempo
# # # # # # # # # ==========================================================
# # # # # # # # # Ini meniru tindakan scheduler saat tanggal jatuh tempo tiba.
# # # # # # # # DepositoService.tandai_jatuh_tempo(
# # # # # # # #     deposito=deposito,
# # # # # # # #     hari_ini=hari_simulasi
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert deposito.status == StatusDeposito.JATUH_TEMPO, (
# # # # # # # #     "Status objek deposito gagal berubah menjadi jatuh tempo"
# # # # # # # # )
# # # # # # # #
# # # # # # # # # Periksa SQLite juga, bukan hanya objek Python.
# # # # # # # # koneksi = buat_koneksi()
# # # # # # # #
# # # # # # # # try:
# # # # # # # #     status_database = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT status
# # # # # # # #         FROM deposito
# # # # # # # #         WHERE id = ?
# # # # # # # #         """,
# # # # # # # #         (ID_DEPOSITO,)
# # # # # # # #     ).fetchone()["status"]
# # # # # # # #
# # # # # # # # finally:
# # # # # # # #     koneksi.close()
# # # # # # # #
# # # # # # # # assert status_database == StatusDeposito.JATUH_TEMPO, (
# # # # # # # #     "Status deposito dalam database belum jatuh tempo"
# # # # # # # # )
# # # # # # # #
# # # # # # # # print(
# # # # # # # #     "\n✅ Deposito berhasil ditandai jatuh tempo "
# # # # # # # #     "menggunakan tanggal simulasi"
# # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 5. Cairkan deposito pada hari simulasi
# # # # # # # # # ==========================================================
# # # # # # # # hasil_pencairan = DepositoService.cairkan_deposito(
# # # # # # # #     deposito=deposito,
# # # # # # # #     hari_ini=hari_simulasi
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert hasil_pencairan == total_pencairan_yang_diharapkan, (
# # # # # # # #     "Nilai yang dikembalikan service tidak sesuai "
# # # # # # # #     "dengan total pencairan"
# # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 6. Ambil kondisi setelah pencairan
# # # # # # # # # ==========================================================
# # # # # # # # kondisi_sesudah = ambil_kondisi_database()
# # # # # # # #
# # # # # # # # rekening_sesudah = kondisi_sesudah["rekening"]
# # # # # # # # deposito_sesudah = kondisi_sesudah["deposito"]
# # # # # # # #
# # # # # # # #
# # # # # # # # # Cari transaksi pencairan yang merujuk deposito ID 10.
# # # # # # # # koneksi = buat_koneksi()
# # # # # # # #
# # # # # # # # try:
# # # # # # # #     transaksi = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM transaksi
# # # # # # # #         WHERE jenis = 'pencairan_deposito'
# # # # # # # #           AND jenis_referensi = ?
# # # # # # # #           AND id_referensi = ?
# # # # # # # #         ORDER BY id DESC
# # # # # # # #         LIMIT 1
# # # # # # # #         """,
# # # # # # # #         (
# # # # # # # #             JenisReferensiID.DEPOSITO.value,
# # # # # # # #             ID_DEPOSITO
# # # # # # # #         )
# # # # # # # #     ).fetchone()
# # # # # # # #
# # # # # # # #     assert transaksi is not None, (
# # # # # # # #         "Transaksi pencairan deposito tidak ditemukan"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #     id_transaksi = transaksi["id"]
# # # # # # # #
# # # # # # # #     daftar_riwayat = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM riwayat
# # # # # # # #         WHERE transaksi_id = ?
# # # # # # # #         ORDER BY id
# # # # # # # #         """,
# # # # # # # #         (id_transaksi,)
# # # # # # # #     ).fetchall()
# # # # # # # #
# # # # # # # #     daftar_audit = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT *
# # # # # # # #         FROM audit
# # # # # # # #         WHERE transaksi_id = ?
# # # # # # # #         ORDER BY id
# # # # # # # #         """,
# # # # # # # #         (id_transaksi,)
# # # # # # # #     ).fetchall()
# # # # # # # #
# # # # # # # #     # Setelah pencairan, tidak boleh ada notifikasi yang masih
# # # # # # # #     # menunjuk deposito tersebut.
# # # # # # # #     jumlah_notifikasi = koneksi.execute(
# # # # # # # #         """
# # # # # # # #         SELECT COUNT(*) AS jumlah
# # # # # # # #         FROM notifikasi
# # # # # # # #         WHERE jenis_referensi = ?
# # # # # # # #           AND id_objek = ?
# # # # # # # #         """,
# # # # # # # #         (
# # # # # # # #             JenisReferensiID.DEPOSITO.value,
# # # # # # # #             ID_DEPOSITO
# # # # # # # #         )
# # # # # # # #     ).fetchone()["jumlah"]
# # # # # # # #
# # # # # # # # finally:
# # # # # # # #     koneksi.close()
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 7. Tampilkan hasil pencairan
# # # # # # # # # ==========================================================
# # # # # # # # print("\n=== KONDISI SETELAH PENCAIRAN ===")
# # # # # # # # print(f"Status deposito       : {deposito_sesudah['status']}")
# # # # # # # # print(f"Saldo rekening        : {rekening_sesudah['saldo']}")
# # # # # # # #
# # # # # # # # print("\n=== DATA TRANSAKSI ===")
# # # # # # # # print(f"ID transaksi          : {transaksi['id']}")
# # # # # # # # print(f"Jenis                 : {transaksi['jenis']}")
# # # # # # # # print(f"Rekening sumber       : {transaksi['norek_sumber']}")
# # # # # # # # print(f"Rekening tujuan       : {transaksi['norek_tujuan']}")
# # # # # # # # print(f"Nominal               : {transaksi['nominal']}")
# # # # # # # # print(
# # # # # # # #     f"Saldo tujuan sebelum  : "
# # # # # # # #     f"{transaksi['saldo_tujuan_sebelum']}"
# # # # # # # # )
# # # # # # # # print(
# # # # # # # #     f"Saldo tujuan sesudah  : "
# # # # # # # #     f"{transaksi['saldo_tujuan_sesudah']}"
# # # # # # # # )
# # # # # # # # print(
# # # # # # # #     f"Jenis referensi       : "
# # # # # # # #     f"{transaksi['jenis_referensi']}"
# # # # # # # # )
# # # # # # # # print(f"ID referensi          : {transaksi['id_referensi']}")
# # # # # # # # print(f"Waktu                 : {transaksi['waktu']}")
# # # # # # # #
# # # # # # # # print("\n=== RIWAYAT TERHUBUNG ===")
# # # # # # # #
# # # # # # # # for riwayat in daftar_riwayat:
# # # # # # # #     print(
# # # # # # # #         f"ID {riwayat['id']} | "
# # # # # # # #         f"Transaksi {riwayat['transaksi_id']} | "
# # # # # # # #         f"{riwayat['jenis']} | "
# # # # # # # #         f"{riwayat['log']}"
# # # # # # # #     )
# # # # # # # #
# # # # # # # # print("\n=== AUDIT TERHUBUNG ===")
# # # # # # # #
# # # # # # # # for audit in daftar_audit:
# # # # # # # #     print(
# # # # # # # #         f"ID {audit['id']} | "
# # # # # # # #         f"Transaksi {audit['transaksi_id']} | "
# # # # # # # #         f"{audit['jenis']} | "
# # # # # # # #         f"{audit['log']}"
# # # # # # # #     )
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 8. Periksa perubahan rekening dan deposito
# # # # # # # # # ==========================================================
# # # # # # # # assert deposito_sesudah["status"] == (
# # # # # # # #     StatusDeposito.DICAIRKAN
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert rekening_sesudah["saldo"] == (
# # # # # # # #     saldo_sesudah_yang_diharapkan
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert deposito.status == StatusDeposito.DICAIRKAN
# # # # # # # # assert deposito.rekening.saldo == saldo_sesudah_yang_diharapkan
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 9. Periksa isi transaksi
# # # # # # # # # ==========================================================
# # # # # # # # assert transaksi["jenis"] == "pencairan_deposito"
# # # # # # # #
# # # # # # # # # Pencairan merupakan uang masuk, sehingga rekening berada
# # # # # # # # # pada kolom tujuan dan kolom sumber harus kosong.
# # # # # # # # assert transaksi["norek_sumber"] is None
# # # # # # # # assert transaksi["norek_tujuan"] == NOREK
# # # # # # # #
# # # # # # # # assert transaksi["nominal"] == (
# # # # # # # #     total_pencairan_yang_diharapkan
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum
# # # # # # # # assert transaksi["saldo_tujuan_sesudah"] == (
# # # # # # # #     saldo_sesudah_yang_diharapkan
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert transaksi["saldo_sumber_sebelum"] is None
# # # # # # # # assert transaksi["saldo_sumber_sesudah"] is None
# # # # # # # #
# # # # # # # # assert str(transaksi["jenis_referensi"]) == str(
# # # # # # # #     JenisReferensiID.DEPOSITO.value
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert transaksi["id_referensi"] == ID_DEPOSITO
# # # # # # # # assert transaksi["waktu"] is not None
# # # # # # # #
# # # # # # # #
# # # # # # # # # ==========================================================
# # # # # # # # # 10. Periksa audit, riwayat, dan notifikasi
# # # # # # # # # ==========================================================
# # # # # # # # assert len(daftar_riwayat) == 1
# # # # # # # # assert len(daftar_audit) == 1
# # # # # # # #
# # # # # # # # assert daftar_riwayat[0]["norek"] == NOREK
# # # # # # # # assert daftar_riwayat[0]["transaksi_id"] == id_transaksi
# # # # # # # #
# # # # # # # # assert daftar_audit[0]["norek"] == NOREK
# # # # # # # # assert daftar_audit[0]["transaksi_id"] == id_transaksi
# # # # # # # #
# # # # # # # # assert jumlah_notifikasi == 0, (
# # # # # # # #     "Notifikasi deposito belum terhapus setelah pencairan"
# # # # # # # # )
# # # # # # # #
# # # # # # # #
# # # # # # # # # Pembukaan sudah menghasilkan satu transaksi. Pencairan
# # # # # # # # # harus menambahkan tepat satu transaksi lagi untuk deposito.
# # # # # # # # assert kondisi_sesudah["jumlah_transaksi"] == (
# # # # # # # #     kondisi_sebelum["jumlah_transaksi"] + 1
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert kondisi_sesudah["jumlah_riwayat"] == (
# # # # # # # #     kondisi_sebelum["jumlah_riwayat"] + 1
# # # # # # # # )
# # # # # # # #
# # # # # # # # assert kondisi_sesudah["jumlah_audit"] == (
# # # # # # # #     kondisi_sebelum["jumlah_audit"] + 1
# # # # # # # # )
# # # # # # # #
# # # # # # # # print(
# # # # # # # #     "\n✅ Pencairan deposito dengan waktu simulasi "
# # # # # # # #     "tersimpan dengan benar"
# # # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # # from unittest.mock import patch
# # # # # # #
# # # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # # from bank_djago.penyimpanan.loaders.deposito_loader import (
# # # # # # #     DepositoLoader
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # #     AuditRepository
# # # # # # # )
# # # # # # # from bank_djago.services.deposito.deposito_service import (
# # # # # # #     DepositoService,
# # # # # # #     StatusDeposito
# # # # # # # )
# # # # # # # from bank_djago.utils.utility import JenisReferensiID
# # # # # # #
# # # # # # #
# # # # # # # NOREK = "3001781978899033"
# # # # # # # NOMINAL_DEPOSITO = 1_000_000
# # # # # # # TENOR_DEPOSITO = 1
# # # # # # #
# # # # # # #
# # # # # # # def cari_deposito_pengujian():
# # # # # # #     """
# # # # # # #     Mencari deposito terbaru yang sesuai dengan data pengujian.
# # # # # # #
# # # # # # #     Filter lengkap digunakan agar pengujian tidak salah memilih
# # # # # # #     deposito aktif lain yang kebetulan baru dibuat.
# # # # # # #     """
# # # # # # #     koneksi = buat_koneksi()
# # # # # # #
# # # # # # #     try:
# # # # # # #         return koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT *
# # # # # # #             FROM deposito
# # # # # # #             WHERE norek = ?
# # # # # # #               AND nominal = ?
# # # # # # #               AND lama_bulan = ?
# # # # # # #               AND jenis_aro = 'tidak'
# # # # # # #               AND status = 'aktif'
# # # # # # #             ORDER BY id DESC
# # # # # # #             LIMIT 1
# # # # # # #             """,
# # # # # # #             (
# # # # # # #                 NOREK,
# # # # # # #                 NOMINAL_DEPOSITO,
# # # # # # #                 TENOR_DEPOSITO
# # # # # # #             )
# # # # # # #         ).fetchone()
# # # # # # #
# # # # # # #     finally:
# # # # # # #         koneksi.close()
# # # # # # #
# # # # # # #
# # # # # # # def ambil_kondisi_database(id_deposito):
# # # # # # #     """
# # # # # # #     Mengambil kondisi yang harus tetap sama apabila
# # # # # # #     pencairan deposito mengalami rollback.
# # # # # # #     """
# # # # # # #     koneksi = buat_koneksi()
# # # # # # #
# # # # # # #     try:
# # # # # # #         rekening = koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT saldo, status
# # # # # # #             FROM rekening
# # # # # # #             WHERE norek = ?
# # # # # # #             """,
# # # # # # #             (NOREK,)
# # # # # # #         ).fetchone()
# # # # # # #
# # # # # # #         deposito = koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT
# # # # # # #                 status,
# # # # # # #                 nominal,
# # # # # # #                 lama_bulan,
# # # # # # #                 jenis_aro,
# # # # # # #                 jatuh_tempo
# # # # # # #             FROM deposito
# # # # # # #             WHERE id = ?
# # # # # # #             """,
# # # # # # #             (id_deposito,)
# # # # # # #         ).fetchone()
# # # # # # #
# # # # # # #         # Untuk deposito ini seharusnya sudah ada satu transaksi
# # # # # # #         # pembukaan. Transaksi pencairan yang gagal tidak boleh
# # # # # # #         # menambah jumlah tersebut.
# # # # # # #         jumlah_transaksi = koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # #             FROM transaksi
# # # # # # #             WHERE jenis_referensi = ?
# # # # # # #               AND id_referensi = ?
# # # # # # #             """,
# # # # # # #             (
# # # # # # #                 JenisReferensiID.DEPOSITO.value,
# # # # # # #                 id_deposito
# # # # # # #             )
# # # # # # #         ).fetchone()["jumlah"]
# # # # # # #
# # # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # #             FROM riwayat
# # # # # # #             WHERE norek = ?
# # # # # # #             """,
# # # # # # #             (NOREK,)
# # # # # # #         ).fetchone()["jumlah"]
# # # # # # #
# # # # # # #         jumlah_audit = koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # #             FROM audit
# # # # # # #             WHERE norek = ?
# # # # # # #             """,
# # # # # # #             (NOREK,)
# # # # # # #         ).fetchone()["jumlah"]
# # # # # # #
# # # # # # #         jumlah_notifikasi = koneksi.execute(
# # # # # # #             """
# # # # # # #             SELECT COUNT(*) AS jumlah
# # # # # # #             FROM notifikasi
# # # # # # #             WHERE jenis_referensi = ?
# # # # # # #               AND id_objek = ?
# # # # # # #             """,
# # # # # # #             (
# # # # # # #                 JenisReferensiID.DEPOSITO.value,
# # # # # # #                 id_deposito
# # # # # # #             )
# # # # # # #         ).fetchone()["jumlah"]
# # # # # # #
# # # # # # #         return {
# # # # # # #             "saldo": rekening["saldo"],
# # # # # # #             "status_rekening": rekening["status"],
# # # # # # #             "status_deposito": deposito["status"],
# # # # # # #             "nominal_deposito": deposito["nominal"],
# # # # # # #             "tenor_deposito": deposito["lama_bulan"],
# # # # # # #             "jenis_aro": deposito["jenis_aro"],
# # # # # # #             "jatuh_tempo": deposito["jatuh_tempo"],
# # # # # # #             "jumlah_transaksi": jumlah_transaksi,
# # # # # # #             "jumlah_riwayat": jumlah_riwayat,
# # # # # # #             "jumlah_audit": jumlah_audit,
# # # # # # #             "jumlah_notifikasi": jumlah_notifikasi
# # # # # # #         }
# # # # # # #
# # # # # # #     finally:
# # # # # # #         koneksi.close()
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 1. Cari deposito baru berdasarkan data yang diketahui
# # # # # # # # ==========================================================
# # # # # # # data_deposito = cari_deposito_pengujian()
# # # # # # #
# # # # # # # assert data_deposito is not None, (
# # # # # # #     "Deposito aktif non-ARO sebesar Rp1.000.000 "
# # # # # # #     "dengan tenor 3 bulan tidak ditemukan"
# # # # # # # )
# # # # # # #
# # # # # # # id_deposito = data_deposito["id"]
# # # # # # #
# # # # # # # print("=== DEPOSITO YANG DITEMUKAN ===")
# # # # # # # print(f"ID deposito      : {id_deposito}")
# # # # # # # print(f"Nomor rekening   : {data_deposito['norek']}")
# # # # # # # print(f"Nominal          : {data_deposito['nominal']}")
# # # # # # # print(f"Tenor            : {data_deposito['lama_bulan']} bulan")
# # # # # # # print(f"Jenis ARO        : {data_deposito['jenis_aro']}")
# # # # # # # print(f"Status           : {data_deposito['status']}")
# # # # # # # print(f"Jatuh tempo      : {data_deposito['jatuh_tempo']}")
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 2. Muat objek deposito dari SQLite
# # # # # # # # ==========================================================
# # # # # # # daftar_deposito_aktif = (
# # # # # # #     DepositoLoader.muat_semua_deposito_aktif()
# # # # # # # )
# # # # # # #
# # # # # # # deposito = next(
# # # # # # #     (
# # # # # # #         item
# # # # # # #         for item in daftar_deposito_aktif
# # # # # # #         if item.ID == id_deposito
# # # # # # #     ),
# # # # # # #     None
# # # # # # # )
# # # # # # #
# # # # # # # assert deposito is not None, (
# # # # # # #     f"Objek deposito ID {id_deposito} gagal dimuat"
# # # # # # # )
# # # # # # #
# # # # # # # assert deposito.rekening.norek == NOREK
# # # # # # # assert deposito.nominal == NOMINAL_DEPOSITO
# # # # # # # assert deposito.lama_bulan == TENOR_DEPOSITO
# # # # # # # assert deposito.jenis_aro == "tidak"
# # # # # # # assert deposito.status == StatusDeposito.AKTIF
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 3. Simulasikan tibanya tanggal jatuh tempo
# # # # # # # # ==========================================================
# # # # # # # # Kita tidak mengubah tanggal komputer atau main.py.
# # # # # # # # Tanggal jatuh tempo hanya diberikan sebagai argumen.
# # # # # # # hari_simulasi = deposito.jatuh_tempo
# # # # # # #
# # # # # # # DepositoService.tandai_jatuh_tempo(
# # # # # # #     deposito=deposito,
# # # # # # #     hari_ini=hari_simulasi
# # # # # # # )
# # # # # # #
# # # # # # # assert deposito.status == StatusDeposito.JATUH_TEMPO
# # # # # # #
# # # # # # # print("\n=== SETELAH PENANDAAN JATUH TEMPO ===")
# # # # # # # print(f"Hari simulasi    : {hari_simulasi}")
# # # # # # # print(f"Status objek     : {deposito.status}")
# # # # # # # print("✅ Deposito berhasil ditandai jatuh tempo")
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 4. Rekam kondisi sebelum mencoba pencairan
# # # # # # # # ==========================================================
# # # # # # # # Status jatuh tempo sudah di-commit sebagai proses terpisah.
# # # # # # # # Kondisi inilah yang harus dipertahankan setelah rollback.
# # # # # # # kondisi_sebelum = ambil_kondisi_database(id_deposito)
# # # # # # #
# # # # # # # saldo_objek_sebelum = deposito.rekening.saldo
# # # # # # # status_objek_sebelum = deposito.status
# # # # # # #
# # # # # # # jumlah_riwayat_objek_sebelum = len(
# # # # # # #     deposito.rekening.riwayat
# # # # # # # )
# # # # # # #
# # # # # # # print("\n=== KONDISI SEBELUM PENCAIRAN ===")
# # # # # # # print(kondisi_sebelum)
# # # # # # #
# # # # # # # assert kondisi_sebelum["status_deposito"] == (
# # # # # # #     StatusDeposito.JATUH_TEMPO
# # # # # # # )
# # # # # # # assert kondisi_sebelum["status_rekening"] == "aktif"
# # # # # # # assert kondisi_sebelum["nominal_deposito"] == (
# # # # # # #     NOMINAL_DEPOSITO
# # # # # # # )
# # # # # # # assert kondisi_sebelum["tenor_deposito"] == (
# # # # # # #     TENOR_DEPOSITO
# # # # # # # )
# # # # # # # assert kondisi_sebelum["jenis_aro"] == "tidak"
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 5. Buat pencairan gagal setelah beberapa query berjalan
# # # # # # # # ==========================================================
# # # # # # # # AuditRepository sementara diganti dengan fungsi yang selalu
# # # # # # # # menghasilkan error.
# # # # # # # #
# # # # # # # # Sebelum mencapai audit, service telah mencoba:
# # # # # # # # - mengubah status deposito menjadi dicairkan;
# # # # # # # # - menambahkan hasil pencairan ke saldo rekening;
# # # # # # # # - membuat transaksi pencairan;
# # # # # # # # - membuat riwayat pencairan.
# # # # # # # #
# # # # # # # # Seluruh perubahan itu menggunakan koneksi yang sama dan
# # # # # # # # belum di-commit, sehingga harus dibatalkan oleh rollback.
# # # # # # # try:
# # # # # # #     with patch.object(
# # # # # # #         AuditRepository,
# # # # # # #         "tambah_audit",
# # # # # # #         side_effect=RuntimeError(
# # # # # # #             "Kegagalan audit untuk menguji rollback pencairan"
# # # # # # #         )
# # # # # # #     ):
# # # # # # #         DepositoService.cairkan_deposito(
# # # # # # #             deposito=deposito,
# # # # # # #             hari_ini=hari_simulasi
# # # # # # #         )
# # # # # # #
# # # # # # #     # Jika baris ini tercapai, berarti pencairan justru berhasil
# # # # # # #     # meskipun audit sudah dibuat gagal.
# # # # # # #     raise AssertionError(
# # # # # # #         "Pencairan deposito seharusnya gagal"
# # # # # # #     )
# # # # # # #
# # # # # # # except RuntimeError as error:
# # # # # # #     assert str(error) == (
# # # # # # #         "Kegagalan audit untuk menguji rollback pencairan"
# # # # # # #     )
# # # # # # #
# # # # # # #     print("\n✅ Kegagalan buatan berhasil dipicu")
# # # # # # #     print(f"Pesan error: {error}")
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 6. Ambil kondisi setelah rollback
# # # # # # # # ==========================================================
# # # # # # # kondisi_sesudah = ambil_kondisi_database(id_deposito)
# # # # # # #
# # # # # # # print("\n=== KONDISI SETELAH ROLLBACK ===")
# # # # # # # print(kondisi_sesudah)
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 7. Periksa kondisi database
# # # # # # # # ==========================================================
# # # # # # # # Seluruh kondisi harus identik dengan keadaan setelah
# # # # # # # # deposito ditandai jatuh tempo.
# # # # # # # assert kondisi_sesudah == kondisi_sebelum
# # # # # # #
# # # # # # # # Penandaan jatuh tempo sudah menjadi transaksi terpisah,
# # # # # # # # sehingga status ini tidak boleh kembali menjadi aktif.
# # # # # # # assert kondisi_sesudah["status_deposito"] == (
# # # # # # #     StatusDeposito.JATUH_TEMPO
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # # ==========================================================
# # # # # # # # 8. Periksa kondisi objek Python
# # # # # # # # ==========================================================
# # # # # # # # Pembaruan objek dalam cairkan_deposito dilakukan setelah
# # # # # # # # commit. Karena commit tidak tercapai, objek harus tetap sama.
# # # # # # # assert deposito.rekening.saldo == saldo_objek_sebelum
# # # # # # # assert deposito.status == status_objek_sebelum
# # # # # # #
# # # # # # # assert len(deposito.rekening.riwayat) == (
# # # # # # #     jumlah_riwayat_objek_sebelum
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # print(
# # # # # # #     "\n✅ ROLLBACK PENCAIRAN BERHASIL: saldo tetap, "
# # # # # # #     "deposito tetap jatuh tempo, transaksi tidak bertambah, "
# # # # # # #     "dan tidak ada riwayat atau audit pencairan yang tersisa"
# # # # # #
# # # # # #
# # # # # #
# # # # # # # )
# # # # # #
# # # # # #
# # # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # # from bank_djago.penyimpanan.loaders.deposito_loader import (
# # # # # #     DepositoLoader
# # # # # # )
# # # # # # from bank_djago.services.deposito.deposito_service import (
# # # # # #     DepositoService,
# # # # # #     StatusDeposito
# # # # # # )
# # # # # # from bank_djago.utils.utility import (
# # # # # #     JenisAro,
# # # # # #     JenisReferensiID,
# # # # # #     Utilitas
# # # # # # )
# # # # # #
# # # # # #
# # # # # # ID_DEPOSITO = 12
# # # # # # NOREK = "3001781978899033"
# # # # # # NOMINAL_DEPOSITO = 1_000_000
# # # # # #
# # # # # #
# # # # # # def ambil_kondisi_database():
# # # # # #     """
# # # # # #     Mengambil kondisi rekening, deposito, serta jumlah catatan
# # # # # #     yang terkait dengan deposito pengujian.
# # # # # #     """
# # # # # #     koneksi = buat_koneksi()
# # # # # #
# # # # # #     try:
# # # # # #         rekening = koneksi.execute(
# # # # # #             """
# # # # # #             SELECT saldo, status
# # # # # #             FROM rekening
# # # # # #             WHERE norek = ?
# # # # # #             """,
# # # # # #             (NOREK,)
# # # # # #         ).fetchone()
# # # # # #
# # # # # #         deposito = koneksi.execute(
# # # # # #             """
# # # # # #             SELECT *
# # # # # #             FROM deposito
# # # # # #             WHERE id = ?
# # # # # #             """,
# # # # # #             (ID_DEPOSITO,)
# # # # # #         ).fetchone()
# # # # # #
# # # # # #         jumlah_transaksi = koneksi.execute(
# # # # # #             """
# # # # # #             SELECT COUNT(*) AS jumlah
# # # # # #             FROM transaksi
# # # # # #             WHERE jenis_referensi = ?
# # # # # #               AND id_referensi = ?
# # # # # #             """,
# # # # # #             (
# # # # # #                 JenisReferensiID.DEPOSITO.value,
# # # # # #                 ID_DEPOSITO
# # # # # #             )
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         jumlah_riwayat = koneksi.execute(
# # # # # #             """
# # # # # #             SELECT COUNT(*) AS jumlah
# # # # # #             FROM riwayat
# # # # # #             WHERE norek = ?
# # # # # #             """,
# # # # # #             (NOREK,)
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         jumlah_audit = koneksi.execute(
# # # # # #             """
# # # # # #             SELECT COUNT(*) AS jumlah
# # # # # #             FROM audit
# # # # # #             WHERE norek = ?
# # # # # #             """,
# # # # # #             (NOREK,)
# # # # # #         ).fetchone()["jumlah"]
# # # # # #
# # # # # #         return {
# # # # # #             "rekening": rekening,
# # # # # #             "deposito": deposito,
# # # # # #             "jumlah_transaksi": jumlah_transaksi,
# # # # # #             "jumlah_riwayat": jumlah_riwayat,
# # # # # #             "jumlah_audit": jumlah_audit
# # # # # #         }
# # # # # #
# # # # # #     finally:
# # # # # #         koneksi.close()
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 1. Muat deposito aktif dari SQLite
# # # # # # # ==========================================================
# # # # # # daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()
# # # # # #
# # # # # # deposito = next(
# # # # # #     (
# # # # # #         item
# # # # # #         for item in daftar_deposito
# # # # # #         if item.ID == ID_DEPOSITO
# # # # # #     ),
# # # # # #     None
# # # # # # )
# # # # # #
# # # # # # assert deposito is not None, (
# # # # # #     f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
# # # # # # )
# # # # # #
# # # # # # # Pastikan tes tidak salah memilih jenis deposito.
# # # # # # assert deposito.rekening.norek == NOREK
# # # # # # assert deposito.nominal == NOMINAL_DEPOSITO
# # # # # # assert deposito.status == StatusDeposito.AKTIF
# # # # # # assert deposito.jenis_aro == JenisAro.POKOK
# # # # # # assert deposito.lama_bulan == 1
# # # # # # assert deposito.lama_aro == 1
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 2. Simpan kondisi sebelum ARO diproses
# # # # # # # ==========================================================
# # # # # # kondisi_sebelum = ambil_kondisi_database()
# # # # # #
# # # # # # rekening_sebelum = kondisi_sebelum["rekening"]
# # # # # # deposito_sebelum = kondisi_sebelum["deposito"]
# # # # # #
# # # # # # assert rekening_sebelum is not None
# # # # # # assert deposito_sebelum is not None
# # # # # #
# # # # # # saldo_sebelum = rekening_sebelum["saldo"]
# # # # # # nominal_sebelum = deposito_sebelum["nominal"]
# # # # # # tanggal_buka_sebelum = deposito.tanggal_buka
# # # # # # jatuh_tempo_sebelum = deposito.jatuh_tempo
# # # # # #
# # # # # # # Untuk ARO pokok, bunga periode lama masuk ke rekening.
# # # # # # bunga_yang_diharapkan = (
# # # # # #     deposito.total_pencairan - deposito.nominal
# # # # # # )
# # # # # #
# # # # # # saldo_yang_diharapkan = (
# # # # # #     saldo_sebelum + bunga_yang_diharapkan
# # # # # # )
# # # # # #
# # # # # # # Pokok deposito harus tetap sama.
# # # # # # nominal_yang_diharapkan = nominal_sebelum
# # # # # #
# # # # # # # Periode baru dimulai dari jatuh tempo periode sebelumnya.
# # # # # # tanggal_buka_yang_diharapkan = jatuh_tempo_sebelum
# # # # # #
# # # # # # jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
# # # # # #     tanggal_buka_yang_diharapkan,
# # # # # #     deposito.lama_aro
# # # # # # )
# # # # # #
# # # # # # print("=== KONDISI SEBELUM ARO ===")
# # # # # # print(f"ID deposito          : {deposito.ID}")
# # # # # # print(f"Nominal deposito     : {nominal_sebelum}")
# # # # # # print(f"Saldo rekening       : {saldo_sebelum}")
# # # # # # print(f"Bunga yang diterima  : {bunga_yang_diharapkan}")
# # # # # # print(f"Tanggal buka         : {tanggal_buka_sebelum}")
# # # # # # print(f"Jatuh tempo          : {jatuh_tempo_sebelum}")
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 3. Jalankan ARO menggunakan tanggal simulasi
# # # # # # # ==========================================================
# # # # # # # Hari simulasi dibuat sama dengan tanggal jatuh tempo.
# # # # # # # Tanggal sistem dan main.py tidak berubah.
# # # # # # hari_simulasi = jatuh_tempo_sebelum
# # # # # #
# # # # # # hasil = DepositoService.perpanjangan(
# # # # # #     deposito=deposito,
# # # # # #     hari_ini=hari_simulasi
# # # # # # )
# # # # # #
# # # # # # assert hasil is True
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 4. Ambil kondisi setelah ARO
# # # # # # # ==========================================================
# # # # # # kondisi_sesudah = ambil_kondisi_database()
# # # # # #
# # # # # # rekening_sesudah = kondisi_sesudah["rekening"]
# # # # # # deposito_sesudah = kondisi_sesudah["deposito"]
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 5. Cari transaksi ARO yang baru dibuat
# # # # # # # ==========================================================
# # # # # # koneksi = buat_koneksi()
# # # # # #
# # # # # # try:
# # # # # #     transaksi = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM transaksi
# # # # # #         WHERE jenis = 'bunga_deposito'
# # # # # #           AND jenis_referensi = ?
# # # # # #           AND id_referensi = ?
# # # # # #         ORDER BY id DESC
# # # # # #         LIMIT 1
# # # # # #         """,
# # # # # #         (
# # # # # #             JenisReferensiID.DEPOSITO.value,
# # # # # #             ID_DEPOSITO
# # # # # #         )
# # # # # #     ).fetchone()
# # # # # #
# # # # # #     assert transaksi is not None, (
# # # # # #         "Transaksi bunga deposito tidak ditemukan"
# # # # # #     )
# # # # # #
# # # # # #     id_transaksi = transaksi["id"]
# # # # # #
# # # # # #     # Satu kejadian ARO pokok menghasilkan dua riwayat:
# # # # # #     # riwayat bunga dan riwayat perpanjangan.
# # # # # #     daftar_riwayat = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM riwayat
# # # # # #         WHERE transaksi_id = ?
# # # # # #         ORDER BY id
# # # # # #         """,
# # # # # #         (id_transaksi,)
# # # # # #     ).fetchall()
# # # # # #
# # # # # #     # Audit perpanjangan menunjuk transaksi bunga yang sama.
# # # # # #     daftar_audit = koneksi.execute(
# # # # # #         """
# # # # # #         SELECT *
# # # # # #         FROM audit
# # # # # #         WHERE transaksi_id = ?
# # # # # #         ORDER BY id
# # # # # #         """,
# # # # # #         (id_transaksi,)
# # # # # #     ).fetchall()
# # # # # #
# # # # # # finally:
# # # # # #     koneksi.close()
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 6. Tampilkan hasil
# # # # # # # ==========================================================
# # # # # # print("\n=== KONDISI SETELAH ARO ===")
# # # # # # print(f"Nominal deposito     : {deposito_sesudah['nominal']}")
# # # # # # print(f"Saldo rekening       : {rekening_sesudah['saldo']}")
# # # # # # print(f"Tanggal buka baru    : {deposito_sesudah['tanggal_buka']}")
# # # # # # print(f"Jatuh tempo baru     : {deposito_sesudah['jatuh_tempo']}")
# # # # # # print(f"Status deposito      : {deposito_sesudah['status']}")
# # # # # # print(f"Tanggal proses ARO   : {deposito_sesudah['proses_aro']}")
# # # # # #
# # # # # # print("\n=== DATA TRANSAKSI ===")
# # # # # # print(f"ID transaksi         : {transaksi['id']}")
# # # # # # print(f"Jenis                : {transaksi['jenis']}")
# # # # # # print(f"Rekening sumber      : {transaksi['norek_sumber']}")
# # # # # # print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
# # # # # # print(f"Nominal              : {transaksi['nominal']}")
# # # # # # print(
# # # # # #     f"Saldo tujuan sebelum : "
# # # # # #     f"{transaksi['saldo_tujuan_sebelum']}"
# # # # # # )
# # # # # # print(
# # # # # #     f"Saldo tujuan sesudah : "
# # # # # #     f"{transaksi['saldo_tujuan_sesudah']}"
# # # # # # )
# # # # # # print(f"Jenis referensi      : {transaksi['jenis_referensi']}")
# # # # # # print(f"ID referensi         : {transaksi['id_referensi']}")
# # # # # # print(f"Waktu                : {transaksi['waktu']}")
# # # # # #
# # # # # # print("\n=== RIWAYAT TERHUBUNG ===")
# # # # # #
# # # # # # for riwayat in daftar_riwayat:
# # # # # #     print(
# # # # # #         f"ID {riwayat['id']} | "
# # # # # #         f"Transaksi {riwayat['transaksi_id']} | "
# # # # # #         f"{riwayat['jenis']} | "
# # # # # #         f"{riwayat['log']}"
# # # # # #     )
# # # # # #
# # # # # # print("\n=== AUDIT TERHUBUNG ===")
# # # # # #
# # # # # # for audit in daftar_audit:
# # # # # #     print(
# # # # # #         f"ID {audit['id']} | "
# # # # # #         f"Transaksi {audit['transaksi_id']} | "
# # # # # #         f"{audit['jenis']} | "
# # # # # #         f"{audit['log']}"
# # # # # #     )
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 7. Periksa perubahan rekening
# # # # # # # ==========================================================
# # # # # # assert rekening_sesudah["saldo"] == (
# # # # # #     saldo_yang_diharapkan
# # # # # # )
# # # # # # assert rekening_sesudah["status"] == "aktif"
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 8. Periksa perubahan deposito
# # # # # # # ==========================================================
# # # # # # # Pada ARO pokok, nominal deposito tidak bertambah.
# # # # # # assert deposito_sesudah["nominal"] == (
# # # # # #     nominal_yang_diharapkan
# # # # # # )
# # # # # #
# # # # # # assert deposito_sesudah["lama_bulan"] == 1
# # # # # # assert deposito_sesudah["bunga"] == 0.03
# # # # # # assert deposito_sesudah["status"] == StatusDeposito.AKTIF
# # # # # #
# # # # # # assert deposito_sesudah["tanggal_buka"] == (
# # # # # #     tanggal_buka_yang_diharapkan.isoformat()
# # # # # # )
# # # # # #
# # # # # # assert deposito_sesudah["jatuh_tempo"] == (
# # # # # #     jatuh_tempo_yang_diharapkan.isoformat()
# # # # # # )
# # # # # #
# # # # # # assert deposito_sesudah["proses_aro"] == (
# # # # # #     hari_simulasi.isoformat()
# # # # # # )
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 9. Periksa transaksi bunga
# # # # # # # ==========================================================
# # # # # # assert transaksi["jenis"] == "bunga_deposito"
# # # # # # assert transaksi["norek_sumber"] is None
# # # # # # assert transaksi["norek_tujuan"] == NOREK
# # # # # # assert transaksi["nominal"] == bunga_yang_diharapkan
# # # # # #
# # # # # # assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum
# # # # # # assert transaksi["saldo_tujuan_sesudah"] == (
# # # # # #     saldo_yang_diharapkan
# # # # # # )
# # # # # #
# # # # # # assert transaksi["saldo_sumber_sebelum"] is None
# # # # # # assert transaksi["saldo_sumber_sesudah"] is None
# # # # # #
# # # # # # assert str(transaksi["jenis_referensi"]) == str(
# # # # # #     JenisReferensiID.DEPOSITO.value
# # # # # # )
# # # # # #
# # # # # # assert transaksi["id_referensi"] == ID_DEPOSITO
# # # # # # assert transaksi["waktu"] is not None
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 10. Periksa hubungan audit dan riwayat
# # # # # # # ==========================================================
# # # # # # assert len(daftar_riwayat) == 2
# # # # # # assert len(daftar_audit) == 1
# # # # # #
# # # # # # assert all(
# # # # # #     riwayat["transaksi_id"] == id_transaksi
# # # # # #     for riwayat in daftar_riwayat
# # # # # # )
# # # # # #
# # # # # # assert daftar_audit[0]["transaksi_id"] == id_transaksi
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 11. Periksa jumlah data yang bertambah
# # # # # # # ==========================================================
# # # # # # assert kondisi_sesudah["jumlah_transaksi"] == (
# # # # # #     kondisi_sebelum["jumlah_transaksi"] + 1
# # # # # # )
# # # # # #
# # # # # # assert kondisi_sesudah["jumlah_riwayat"] == (
# # # # # #     kondisi_sebelum["jumlah_riwayat"] + 2
# # # # # # )
# # # # # #
# # # # # # assert kondisi_sesudah["jumlah_audit"] == (
# # # # # #     kondisi_sebelum["jumlah_audit"] + 1
# # # # # # )
# # # # # #
# # # # # #
# # # # # # # ==========================================================
# # # # # # # 12. Periksa state objek Python
# # # # # # # ==========================================================
# # # # # # assert deposito.rekening.saldo == saldo_yang_diharapkan
# # # # # # assert deposito.nominal == nominal_yang_diharapkan
# # # # # # assert deposito.tanggal_buka == tanggal_buka_yang_diharapkan
# # # # # # assert deposito.jatuh_tempo == jatuh_tempo_yang_diharapkan
# # # # # # assert deposito.status == StatusDeposito.AKTIF
# # # # # # assert deposito.proses_aro == hari_simulasi
# # # # # #
# # # # # #
# # # # # # print(
# # # # # #     "\n✅ ARO POKOK BERHASIL: bunga masuk ke rekening, "
# # # # # #     "pokok tetap, periode diperpanjang, dan seluruh catatan "
# # # # # #     "terhubung ke transaksi yang sama"
# # # # # # )
# # # # #
# # # # #
# # # # # from bank_djago.penyimpanan.loaders.deposito_loader import (
# # # # #     DepositoLoader
# # # # # )
# # # # # from bank_djago.penyimpanan.sqlite.database import (
# # # # #     buat_koneksi
# # # # # )
# # # # # from bank_djago.services.deposito.deposito_service import (
# # # # #     DepositoService,
# # # # #     StatusDeposito
# # # # # )
# # # # # from bank_djago.core.deposito import JenisAro
# # # # # from bank_djago.utils.utility import Utilitas,JenisReferensiID,JenisTransaksi
# # # # #
# # # # #
# # # # # ID_DEPOSITO = 13
# # # # # NOREK_PENGUJIAN = "3001781978899033"
# # # # #
# # # # # JENIS_TRANSAKSI = "kapitalisasi_bunga_deposito"
# # # # # JENIS_REFERENSI_DEPOSITO = 2
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MENGHITUNG JUMLAH DATA SEBELUM DAN SETELAH PROSES
# # # # # # ============================================================
# # # # #
# # # # # def hitung_jumlah_data():
# # # # #     """
# # # # #     Menghitung seluruh transaksi, riwayat, dan audit.
# # # # #
# # # # #     Nilai ini akan dibandingkan sebelum dan setelah ARO
# # # # #     untuk memastikan jumlah data bertambah dengan benar.
# # # # #     """
# # # # #     koneksi = buat_koneksi()
# # # # #
# # # # #     try:
# # # # #         jumlah_transaksi = koneksi.execute(
# # # # #             """
# # # # #             SELECT COUNT(*) AS jumlah
# # # # #             FROM transaksi
# # # # #             """
# # # # #         ).fetchone()["jumlah"]
# # # # #
# # # # #         jumlah_riwayat = koneksi.execute(
# # # # #             """
# # # # #             SELECT COUNT(*) AS jumlah
# # # # #             FROM riwayat
# # # # #             """
# # # # #         ).fetchone()["jumlah"]
# # # # #
# # # # #         jumlah_audit = koneksi.execute(
# # # # #             """
# # # # #             SELECT COUNT(*) AS jumlah
# # # # #             FROM audit
# # # # #             """
# # # # #         ).fetchone()["jumlah"]
# # # # #
# # # # #         return {
# # # # #             "transaksi": jumlah_transaksi,
# # # # #             "riwayat": jumlah_riwayat,
# # # # #             "audit": jumlah_audit
# # # # #         }
# # # # #
# # # # #     finally:
# # # # #         koneksi.close()
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MEMUAT DEPOSITO AKTIF DARI SQLITE
# # # # # # ============================================================
# # # # #
# # # # # # DepositoLoader mengembalikan objek deposito yang sudah
# # # # # # terhubung dengan objek rekening dan nasabahnya.
# # # # # daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()
# # # # #
# # # # # deposito = next(
# # # # #     (
# # # # #         item
# # # # #         for item in daftar_deposito
# # # # #         if item.ID == ID_DEPOSITO
# # # # #     ),
# # # # #     None
# # # # # )
# # # # #
# # # # # if deposito is None:
# # # # #     raise AssertionError(
# # # # #         f"Deposito aktif dengan ID {ID_DEPOSITO} tidak ditemukan"
# # # # #     )
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MEMERIKSA IDENTITAS DAN KONDISI AWAL DEPOSITO
# # # # # # ============================================================
# # # # #
# # # # # assert deposito.rekening.norek == NOREK_PENGUJIAN, (
# # # # #     "Deposito terhubung dengan rekening yang salah"
# # # # # )
# # # # #
# # # # # assert deposito.jenis_aro == JenisAro.POKOK_BUNGA, (
# # # # #     f"Jenis ARO seharusnya {JenisAro.POKOK_BUNGA}, "
# # # # #     f"tetapi ditemukan {deposito.jenis_aro}"
# # # # # )
# # # # #
# # # # # assert deposito.status == StatusDeposito.AKTIF, (
# # # # #     f"Status deposito seharusnya aktif, "
# # # # #     f"tetapi ditemukan {deposito.status}"
# # # # # )
# # # # #
# # # # # assert deposito.lama_aro in DepositoService.JANGKA_WAKTU, (
# # # # #     "Lama perpanjangan deposito tidak valid"
# # # # # )
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MENYIMPAN KONDISI SEBELUM ARO
# # # # # # ============================================================
# # # # #
# # # # # rekening = deposito.rekening
# # # # #
# # # # # saldo_sebelum = rekening.saldo
# # # # # nominal_sebelum = deposito.nominal
# # # # # bunga_sebelum = deposito.bunga
# # # # # tenor_sebelum = deposito.lama_bulan
# # # # # lama_aro = deposito.lama_aro
# # # # # tanggal_buka_sebelum = deposito.tanggal_buka
# # # # # jatuh_tempo_sebelum = deposito.jatuh_tempo
# # # # #
# # # # # # total_pencairan berisi pokok ditambah bunga periode lama.
# # # # # total_pencairan = deposito.total_pencairan
# # # # #
# # # # # # Pada ARO pokok+bunga, nilai ini tidak masuk ke rekening.
# # # # # # Nilainya ditambahkan ke nominal deposito.
# # # # # bunga_dihasilkan = total_pencairan - nominal_sebelum
# # # # #
# # # # # nominal_yang_diharapkan = (
# # # # #     nominal_sebelum + bunga_dihasilkan
# # # # # )
# # # # #
# # # # # saldo_yang_diharapkan = saldo_sebelum
# # # # #
# # # # # tanggal_buka_yang_diharapkan = jatuh_tempo_sebelum
# # # # #
# # # # # jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
# # # # #     tanggal_buka_yang_diharapkan,
# # # # #     lama_aro
# # # # # )
# # # # #
# # # # # bunga_baru_yang_diharapkan = (
# # # # #     DepositoService.JANGKA_WAKTU[lama_aro]
# # # # # )
# # # # #
# # # # # jumlah_sebelum = hitung_jumlah_data()
# # # # #
# # # # #
# # # # # print("=== KONDISI SEBELUM ARO POKOK + BUNGA ===")
# # # # # print()
# # # # # print("ID deposito       :", deposito.ID)
# # # # # print("Nomor rekening    :", rekening.norek)
# # # # # print("Jenis ARO         :", deposito.jenis_aro)
# # # # # print(
# # # # #     "Nominal lama      : Rp"
# # # # #     + Utilitas.format_rupiah(nominal_sebelum)
# # # # # )
# # # # # print(
# # # # #     "Bunga dihasilkan  : Rp"
# # # # #     + Utilitas.format_rupiah(bunga_dihasilkan)
# # # # # )
# # # # # print(
# # # # #     "Total periode     : Rp"
# # # # #     + Utilitas.format_rupiah(total_pencairan)
# # # # # )
# # # # # print(
# # # # #     "Saldo rekening    : Rp"
# # # # #     + Utilitas.format_rupiah(saldo_sebelum)
# # # # # )
# # # # # print(f"Bunga lama        : {bunga_sebelum:.1%}")
# # # # # print("Tenor lama        :", tenor_sebelum, "bulan")
# # # # # print("Tenor ARO         :", lama_aro, "bulan")
# # # # # print("Tanggal buka      :", tanggal_buka_sebelum)
# # # # # print("Jatuh tempo       :", jatuh_tempo_sebelum)
# # # # # print("Proses ARO        :", deposito.proses_aro)
# # # # # print("Jumlah transaksi  :", jumlah_sebelum["transaksi"])
# # # # # print("Jumlah riwayat    :", jumlah_sebelum["riwayat"])
# # # # # print("Jumlah audit      :", jumlah_sebelum["audit"])
# # # # # print()
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MENJALANKAN ARO DENGAN TANGGAL SIMULASI
# # # # # # ============================================================
# # # # #
# # # # # # Tanggal jatuh tempo dipakai sebagai hari simulasi.
# # # # # # Kita tidak perlu mengubah waktu komputer ataupun main.
# # # # # hasil = DepositoService.perpanjangan(
# # # # #     deposito=deposito,
# # # # #     hari_ini=jatuh_tempo_sebelum
# # # # # )
# # # # #
# # # # # assert hasil is True, (
# # # # #     "Method perpanjangan tidak mengembalikan True"
# # # # # )
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MEMUAT ULANG HASIL DARI SQLITE
# # # # # # ============================================================
# # # # #
# # # # # # Kita tidak hanya mempercayai perubahan pada objek lama.
# # # # # # Data dimuat ulang agar terbukti sudah tersimpan di SQLite.
# # # # # daftar_deposito_sesudah = (
# # # # #     DepositoLoader.muat_semua_deposito_aktif()
# # # # # )
# # # # #
# # # # # deposito_sesudah = next(
# # # # #     (
# # # # #         item
# # # # #         for item in daftar_deposito_sesudah
# # # # #         if item.ID == ID_DEPOSITO
# # # # #     ),
# # # # #     None
# # # # # )
# # # # #
# # # # # if deposito_sesudah is None:
# # # # #     raise AssertionError(
# # # # #         f"Deposito ID {ID_DEPOSITO} tidak ditemukan setelah ARO"
# # # # #     )
# # # # #
# # # # # rekening_sesudah = deposito_sesudah.rekening
# # # # # jumlah_sesudah = hitung_jumlah_data()
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MENGAMBIL TRANSAKSI KAPITALISASI
# # # # # # ============================================================
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     transaksi = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM transaksi
# # # # #         WHERE jenis = ?
# # # # #           AND jenis_referensi = ?
# # # # #           AND id_referensi = ?
# # # # #         ORDER BY id DESC
# # # # #         LIMIT 1
# # # # #         """,
# # # # #         (
# # # # #             JENIS_TRANSAKSI,
# # # # #             JENIS_REFERENSI_DEPOSITO,
# # # # #             ID_DEPOSITO
# # # # #         )
# # # # #     ).fetchone()
# # # # #
# # # # #     assert transaksi is not None, (
# # # # #         "Transaksi kapitalisasi bunga tidak ditemukan"
# # # # #     )
# # # # #
# # # # #     id_transaksi = transaksi["id"]
# # # # #
# # # # #     # Seluruh riwayat proses ARO harus menunjuk
# # # # #     # ke transaksi kapitalisasi yang sama.
# # # # #     daftar_riwayat = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM riwayat
# # # # #         WHERE transaksi_id = ?
# # # # #         ORDER BY id
# # # # #         """,
# # # # #         (id_transaksi,)
# # # # #     ).fetchall()
# # # # #
# # # # #     # Audit perpanjangan juga harus menunjuk
# # # # #     # ke transaksi kapitalisasi tersebut.
# # # # #     daftar_audit = koneksi.execute(
# # # # #         """
# # # # #         SELECT *
# # # # #         FROM audit
# # # # #         WHERE transaksi_id = ?
# # # # #         ORDER BY id
# # # # #         """,
# # # # #         (id_transaksi,)
# # # # #     ).fetchall()
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MENAMPILKAN KONDISI SETELAH ARO
# # # # # # ============================================================
# # # # #
# # # # # print("=== KONDISI SETELAH ARO POKOK + BUNGA ===")
# # # # # print()
# # # # # print("ID deposito       :", deposito_sesudah.ID)
# # # # # print("Jenis ARO         :", deposito_sesudah.jenis_aro)
# # # # # print(
# # # # #     "Nominal baru      : Rp"
# # # # #     + Utilitas.format_rupiah(deposito_sesudah.nominal)
# # # # # )
# # # # # print(
# # # # #     "Saldo rekening    : Rp"
# # # # #     + Utilitas.format_rupiah(rekening_sesudah.saldo)
# # # # # )
# # # # # print(f"Bunga baru        : {deposito_sesudah.bunga:.1%}")
# # # # # print(
# # # # #     "Tenor baru        :",
# # # # #     deposito_sesudah.lama_bulan,
# # # # #     "bulan"
# # # # # )
# # # # # print("Tanggal buka baru :", deposito_sesudah.tanggal_buka)
# # # # # print("Jatuh tempo baru  :", deposito_sesudah.jatuh_tempo)
# # # # # print("Status deposito   :", deposito_sesudah.status)
# # # # # print("Proses ARO        :", deposito_sesudah.proses_aro)
# # # # # print()
# # # # #
# # # # #
# # # # # print("=== DATA TRANSAKSI ===")
# # # # # print()
# # # # # print("ID transaksi      :", transaksi["id"])
# # # # # print("Jenis             :", transaksi["jenis"])
# # # # # print("Rekening sumber   :", transaksi["norek_sumber"])
# # # # # print("Rekening tujuan   :", transaksi["norek_tujuan"])
# # # # # print(
# # # # #     "Nominal bunga     : Rp"
# # # # #     + Utilitas.format_rupiah(transaksi["nominal"])
# # # # # )
# # # # # print("Saldo sumber awal :", transaksi["saldo_sumber_sebelum"])
# # # # # print("Saldo sumber akhir:", transaksi["saldo_sumber_sesudah"])
# # # # # print("Saldo tujuan awal :", transaksi["saldo_tujuan_sebelum"])
# # # # # print("Saldo tujuan akhir:", transaksi["saldo_tujuan_sesudah"])
# # # # # print("Jenis referensi   :", transaksi["jenis_referensi"])
# # # # # print("ID referensi      :", transaksi["id_referensi"])
# # # # # print("Waktu             :", transaksi["waktu"])
# # # # # print()
# # # # #
# # # # #
# # # # # print("=== RIWAYAT TERHUBUNG ===")
# # # # #
# # # # # for riwayat in daftar_riwayat:
# # # # #     print(
# # # # #         f"ID {riwayat['id']} | "
# # # # #         f"Transaksi {riwayat['transaksi_id']} | "
# # # # #         f"{riwayat['jenis']} | "
# # # # #         f"{riwayat['log']}"
# # # # #     )
# # # # #
# # # # # print()
# # # # #
# # # # # print("=== AUDIT TERHUBUNG ===")
# # # # #
# # # # # for audit in daftar_audit:
# # # # #     print(
# # # # #         f"ID {audit['id']} | "
# # # # #         f"Transaksi {audit['transaksi_id']} | "
# # # # #         f"{audit['jenis']} | "
# # # # #         f"{audit['log']}"
# # # # #     )
# # # # #
# # # # # print()
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MEMERIKSA HASIL PERPANJANGAN DEPOSITO
# # # # # # ============================================================
# # # # #
# # # # # assert deposito_sesudah.nominal == nominal_yang_diharapkan, (
# # # # #     "Pokok dan bunga tidak menjadi nominal deposito baru"
# # # # # )
# # # # # print("✅ Pokok dan bunga menjadi nominal deposito baru")
# # # # #
# # # # # assert deposito_sesudah.nominal > nominal_sebelum, (
# # # # #     "Nominal deposito tidak bertambah"
# # # # # )
# # # # # print("✅ Nominal deposito bertambah sebesar bunga")
# # # # #
# # # # # assert rekening_sesudah.saldo == saldo_yang_diharapkan, (
# # # # #     "Saldo rekening berubah pada ARO pokok+bunga"
# # # # # )
# # # # # print("✅ Saldo rekening tidak berubah")
# # # # #
# # # # # assert deposito_sesudah.bunga == bunga_baru_yang_diharapkan, (
# # # # #     "Bunga periode baru tidak mengikuti tenor ARO"
# # # # # )
# # # # # print("✅ Bunga periode baru mengikuti tenor ARO")
# # # # #
# # # # # assert deposito_sesudah.lama_bulan == lama_aro, (
# # # # #     "Tenor baru tidak mengikuti lama ARO"
# # # # # )
# # # # # print("✅ Tenor baru mengikuti lama ARO")
# # # # #
# # # # # assert (
# # # # #     deposito_sesudah.tanggal_buka
# # # # #     == tanggal_buka_yang_diharapkan
# # # # # ), "Tanggal buka periode baru tidak sesuai"
# # # # # print("✅ Tanggal buka baru sesuai jatuh tempo sebelumnya")
# # # # #
# # # # # assert (
# # # # #     deposito_sesudah.jatuh_tempo
# # # # #     == jatuh_tempo_yang_diharapkan
# # # # # ), "Jatuh tempo periode baru tidak sesuai"
# # # # # print("✅ Jatuh tempo periode baru berhasil dihitung")
# # # # #
# # # # # assert deposito_sesudah.proses_aro == jatuh_tempo_sebelum, (
# # # # #     "Tanggal proses ARO tidak sesuai tanggal simulasi"
# # # # # )
# # # # # print("✅ Tanggal proses ARO berhasil disimpan")
# # # # #
# # # # # assert deposito_sesudah.status == StatusDeposito.AKTIF, (
# # # # #     "Deposito tidak aktif setelah perpanjangan"
# # # # # )
# # # # # print("✅ Deposito tetap aktif setelah diperpanjang")
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MEMERIKSA TRANSAKSI KAPITALISASI
# # # # # # ============================================================
# # # # #
# # # # # assert jumlah_sesudah["transaksi"] == (
# # # # #     jumlah_sebelum["transaksi"] + 1
# # # # # ), "Transaksi seharusnya bertambah tepat satu"
# # # # # print("✅ Transaksi bertambah tepat satu")
# # # # #
# # # # # assert transaksi["jenis"] == JENIS_TRANSAKSI, (
# # # # #     "Jenis transaksi kapitalisasi tidak sesuai"
# # # # # )
# # # # # print("✅ Jenis transaksi kapitalisasi sesuai")
# # # # #
# # # # # assert transaksi["nominal"] == bunga_dihasilkan, (
# # # # #     "Nominal transaksi tidak sama dengan bunga yang dihasilkan"
# # # # # )
# # # # # print("✅ Nominal transaksi berisi bunga yang dikapitalisasi")
# # # # #
# # # # # assert transaksi["norek_sumber"] is None, (
# # # # #     "Kapitalisasi seharusnya tidak memiliki rekening sumber"
# # # # # )
# # # # #
# # # # # assert transaksi["norek_tujuan"] is None, (
# # # # #     "Kapitalisasi seharusnya tidak memiliki rekening tujuan"
# # # # # )
# # # # # print("✅ Kapitalisasi tidak mencatat perpindahan antar-rekening")
# # # # #
# # # # # assert transaksi["saldo_sumber_sebelum"] is None
# # # # # assert transaksi["saldo_sumber_sesudah"] is None
# # # # # assert transaksi["saldo_tujuan_sebelum"] is None
# # # # # assert transaksi["saldo_tujuan_sesudah"] is None
# # # # # print("✅ Snapshot saldo rekening kosong karena saldo tidak berubah")
# # # # #
# # # # # assert (
# # # # #     transaksi["jenis_referensi"]
# # # # #     == JenisReferensiID.DEPOSITO
# # # # # ), "Jenis referensi transaksi bukan deposito"
# # # # #
# # # # # assert transaksi["id_referensi"] == ID_DEPOSITO, (
# # # # #     "ID referensi tidak menunjuk deposito ID 13"
# # # # # )
# # # # # print("✅ Transaksi terhubung ke deposito melalui referensi")
# # # # #
# # # # # assert transaksi["waktu"] is not None, (
# # # # #     "Waktu transaksi tidak tersimpan"
# # # # # )
# # # # # print("✅ Waktu transaksi berhasil tersimpan")
# # # # #
# # # # #
# # # # # # ============================================================
# # # # # # MEMERIKSA RIWAYAT DAN AUDIT
# # # # # # ============================================================
# # # # #
# # # # # assert jumlah_sesudah["riwayat"] == (
# # # # #     jumlah_sebelum["riwayat"] + 2
# # # # # ), "Riwayat seharusnya bertambah tepat dua"
# # # # #
# # # # # assert len(daftar_riwayat) == 2, (
# # # # #     "Harus ada dua riwayat yang terhubung ke transaksi"
# # # # # )
# # # # # print("✅ Dua riwayat terhubung ke transaksi yang sama")
# # # # #
# # # # # assert jumlah_sesudah["audit"] == (
# # # # #     jumlah_sebelum["audit"] + 1
# # # # # ), "Audit seharusnya bertambah tepat satu"
# # # # #
# # # # # assert len(daftar_audit) == 1, (
# # # # #     "Harus ada satu audit yang terhubung ke transaksi"
# # # # # )
# # # # # print("✅ Audit perpanjangan terhubung ke transaksi yang sama")
# # # # #
# # # # #
# # # # # print()
# # # # # print(
# # # # #     "✅ ARO POKOK + BUNGA BERHASIL: bunga dikapitalisasi, "
# # # # #     "saldo rekening tetap, periode diperpanjang, dan seluruh "
# # # # #     "catatan terhubung ke transaksi yang sama"
# # # # # )
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # #
# # # #
# # # # ID_DEPOSITO = 13
# # # #
# # # # koneksi = buat_koneksi()
# # # #
# # # # try:
# # # #     deposito = koneksi.execute(
# # # #         """
# # # #         SELECT
# # # #             id,
# # # #             nominal,
# # # #             bunga,
# # # #             lama_bulan,
# # # #             tanggal_buka,
# # # #             jatuh_tempo,
# # # #             proses_aro,
# # # #             status
# # # #         FROM deposito
# # # #         WHERE id = ?
# # # #         """,
# # # #         (ID_DEPOSITO,)
# # # #     ).fetchone()
# # # #
# # # #     transaksi_aro = koneksi.execute(
# # # #         """
# # # #         SELECT
# # # #             id,
# # # #             jenis,
# # # #             nominal,
# # # #             jenis_referensi,
# # # #             id_referensi,
# # # #             waktu
# # # #         FROM transaksi
# # # #         WHERE jenis = ?
# # # #           AND jenis_referensi = ?
# # # #           AND id_referensi = ?
# # # #         ORDER BY id
# # # #         """,
# # # #         (
# # # #             "kapitalisasi_bunga_deposito",
# # # #             2,
# # # #             ID_DEPOSITO
# # # #         )
# # # #     ).fetchall()
# # # #
# # # #     print("=== KONDISI DEPOSITO ===")
# # # #     print(dict(deposito) if deposito else "Deposito tidak ditemukan")
# # # #
# # # #     print("\n=== TRANSAKSI KAPITALISASI ===")
# # # #
# # # #     for transaksi in transaksi_aro:
# # # #         print(dict(transaksi))
# # # #
# # # #     print("\nJumlah transaksi:", len(transaksi_aro))
# # # #
# # # # finally:
# # # #     koneksi.close()
# # #
# # #
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # #
# # # #
# # # # ID_TRANSAKSI_AWAL = 19
# # # # ID_TRANSAKSI_AKHIR = 23
# # # #
# # # # koneksi = buat_koneksi()
# # # #
# # # # try:
# # # #     daftar_riwayat = koneksi.execute(
# # # #         """
# # # #         SELECT id, transaksi_id, norek, jenis, log
# # # #         FROM riwayat
# # # #         WHERE transaksi_id BETWEEN ? AND ?
# # # #         ORDER BY transaksi_id, id
# # # #         """,
# # # #         (
# # # #             ID_TRANSAKSI_AWAL,
# # # #             ID_TRANSAKSI_AKHIR
# # # #         )
# # # #     ).fetchall()
# # # #
# # # #     daftar_audit = koneksi.execute(
# # # #         """
# # # #         SELECT id, transaksi_id, norek, jenis, log
# # # #         FROM audit
# # # #         WHERE transaksi_id BETWEEN ? AND ?
# # # #         ORDER BY transaksi_idpppppppooo, id
# # # #         """,
# # # #         (
# # # #             ID_TRANSAKSI_AWAL,
# # # #             ID_TRANSAKSI_AKHIR
# # # #         )
# # # #     ).fetchall()
# # # #
# # # #     print("=== RIWAYAT YANG AKAN DIPULIHKAN ===")
# # # #
# # # #     for riwayat in daftar_riwayat:
# # # #         print(dict(riwayat))
# # # #
# # # #     print("\nJumlah riwayat:", len(daftar_riwayat))
# # # #
# # # #     print("\n=== AUDIT YANG AKAN DIPULIHKAN ===")
# # # #
# # # #     for audit in daftar_audit:
# # # #         print(dict(audit))
# # # #
# # # #     print("\nJumlah audit:", len(daftar_audit))
# # # #
# # # # finally:
# # # #     koneksi.close()
# # #
# # #
# # #
# #
# # # from bank_djago.penyimpanan.repositories.deposito_repository import (
# # #     DepositoRepository
# # # )
# # #
# # #
# # # ID_DEPOSITO = 14
# # # NOREK_PENGUJIAN = "3001781978899033"
# # #
# # #
# # # # Mengambil data mentah deposito langsung dari SQLite.
# # # deposito = DepositoRepository.cari_deposito_dengan_id(
# # #     ID_DEPOSITO
# # # )
# # #
# # # if deposito is None:
# # #     raise AssertionError(
# # #         f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
# # #     )
# # #
# # #
# # # # Menampilkan konfigurasi deposito sebelum pengujian ARO.
# # # print("=== DATA DEPOSITO BARU ===")
# # # print("ID deposito    :", deposito["id"])
# # # print("Nomor rekening :", deposito["norek"])
# # # print("Nominal        :", deposito["nominal"])
# # # print("Tenor awal     :", deposito["lama_bulan"])
# # # print("Jenis ARO      :", deposito["jenis_aro"])
# # # print("Lama ARO       :", deposito["lama_aro"])
# # # print("Tanggal buka   :", deposito["tanggal_buka"])
# # # print("Jatuh tempo    :", deposito["jatuh_tempo"])
# # # print("Proses ARO     :", deposito["proses_aro"])
# # # print("Status         :", deposito["status"])
# # # print()
# # #
# # #
# # # # Memastikan deposito yang dibuat sesuai rencana pengujian.
# # # assert deposito["id"] == ID_DEPOSITO, (
# # #     "ID deposito tidak sesuai"
# # # )
# # #
# # # assert deposito["norek"] == NOREK_PENGUJIAN, (
# # #     "Deposito terhubung dengan rekening yang salah"
# # # )
# # #
# # # assert deposito["nominal"] == 1_000_000, (
# # #     "Nominal deposito bukan Rp1.000.000"
# # # )
# # #
# # # assert deposito["lama_bulan"] == 1, (
# # #     "Tenor awal deposito bukan satu bulan"
# # # )
# # #
# # # assert deposito["jenis_aro"] == "pokok_bunga", (
# # #     "Jenis ARO bukan pokok+bunga"
# # # )
# # #
# # # assert deposito["lama_aro"] == 1, (
# # #     "Lama perpanjangan ARO bukan satu bulan"
# # # )
# # #
# # # assert deposito["proses_aro"] is None, (
# # #     "Deposito ini ternyata sudah pernah diproses ARO"
# # # )
# # #
# # # assert deposito["status"] == "aktif", (
# # #     "Status deposito bukan aktif"
# # # )
# # #
# # #
# # # print("✅ Deposito ID 14 siap diuji untuk ARO pokok+bunga")
# #
# #
# #
# #
# # import datetime
# #
# # from bank_djago.penyimpanan.loaders.deposito_loader import (
# #     DepositoLoader
# # )
# # from bank_djago.penyimpanan.sqlite.database import (
# #     buat_koneksi
# # )
# # from bank_djago.services.deposito.deposito_service import (
# #     DepositoService,
# #     StatusDeposito
# # )
# # from bank_djago.core.deposito import JenisAro
# # from bank_djago.utils.utility import (
# #     JenisReferensi,
# #     JenisTransaksi,
# #     Utilitas
# # )
# #
# #
# # ID_DEPOSITO = 14
# # NOREK_PENGUJIAN = "3001781978899033"
# #
# # TANGGAL_BUKA_AWAL = datetime.date(2026, 9, 4)
# # JATUH_TEMPO_AWAL = datetime.date(2026, 10, 4)
# #
# #
# # def cari_deposito_aktif(id_deposito):
# #     """
# #     Memuat seluruh deposito aktif, lalu mencari objek deposito
# #     berdasarkan ID.
# #     """
# #     daftar_deposito = (
# #         DepositoLoader.muat_semua_deposito_aktif()
# #     )
# #
# #     return next(
# #         (
# #             deposito
# #             for deposito in daftar_deposito
# #             if deposito.ID == id_deposito
# #         ),
# #         None
# #     )
# #
# #
# # def hitung_jumlah_data():
# #     """
# #     Menghitung jumlah transaksi, riwayat, dan audit sebelum
# #     serta setelah proses ARO.
# #     """
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         return {
# #             "transaksi": koneksi.execute(
# #                 "SELECT COUNT(*) AS jumlah FROM transaksi"
# #             ).fetchone()["jumlah"],
# #
# #             "riwayat": koneksi.execute(
# #                 "SELECT COUNT(*) AS jumlah FROM riwayat"
# #             ).fetchone()["jumlah"],
# #
# #             "audit": koneksi.execute(
# #                 "SELECT COUNT(*) AS jumlah FROM audit"
# #             ).fetchone()["jumlah"]
# #         }
# #
# #     finally:
# #         koneksi.close()
# #
# #
# # # ============================================================
# # # 1. MEMUAT DEPOSITO YANG AKAN DIPROSES
# # # ============================================================
# #
# # deposito = cari_deposito_aktif(ID_DEPOSITO)
# #
# # if deposito is None:
# #     raise AssertionError(
# #         f"Deposito aktif ID {ID_DEPOSITO} tidak ditemukan"
# #     )
# #
# # rekening = deposito.rekening
# #
# #
# # # ============================================================
# # # 2. PENGAMAN SEBELUM PERPANJANGAN
# # # ============================================================
# # #
# # # Semua assertion ini berjalan sebelum service dipanggil.
# # # Jika pengujian dijalankan lagi, kondisi deposito sudah berubah
# # # sehingga proses akan berhenti di sini.
# # # ============================================================
# #
# # assert rekening.norek == NOREK_PENGUJIAN, (
# #     "Deposito terhubung dengan rekening yang salah"
# # )
# #
# # assert deposito.nominal == 1_000_000, (
# #     "Nominal deposito bukan nominal awal Rp1.000.000. "
# #     "Kemungkinan pengujian sudah pernah dijalankan."
# # )
# #
# # assert deposito.jenis_aro == JenisAro.POKOK_BUNGA, (
# #     "Jenis ARO deposito bukan pokok+bunga"
# # )
# #
# # assert deposito.lama_bulan == 1, (
# #     "Tenor awal deposito bukan satu bulan"
# # )
# #
# # assert deposito.lama_aro == 1, (
# #     "Lama perpanjangan bukan satu bulan"
# # )
# #
# # assert deposito.tanggal_buka == TANGGAL_BUKA_AWAL, (
# #     "Tanggal buka sudah berubah. "
# #     "Kemungkinan deposito pernah diperpanjang."
# # )
# #
# # assert deposito.jatuh_tempo == JATUH_TEMPO_AWAL, (
# #     "Jatuh tempo sudah berubah. "
# #     "Kemungkinan deposito pernah diperpanjang."
# # )
# #
# # assert deposito.proses_aro is None, (
# #     "Deposito sudah pernah diproses ARO"
# # )
# #
# # assert deposito.status == StatusDeposito.AKTIF, (
# #     "Status deposito bukan aktif"
# # )
# #
# # print("✅ Pengaman kondisi awal berhasil dilewati")
# #
# #
# # # ============================================================
# # # 3. MENYIAPKAN NILAI YANG DIHARAPKAN
# # # ============================================================
# #
# # saldo_sebelum = rekening.saldo
# # nominal_sebelum = deposito.nominal
# # total_periode = deposito.total_pencairan
# #
# # # Total periode berisi pokok beserta bunga.
# # bunga_dihasilkan = total_periode - nominal_sebelum
# #
# # nominal_yang_diharapkan = total_periode
# # saldo_yang_diharapkan = saldo_sebelum
# #
# # tanggal_buka_yang_diharapkan = JATUH_TEMPO_AWAL
# #
# # jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
# #     tanggal_buka_yang_diharapkan,
# #     deposito.lama_aro
# # )
# #
# # bunga_baru_yang_diharapkan = (
# #     DepositoService.JANGKA_WAKTU[deposito.lama_aro]
# # )
# #
# # jumlah_sebelum = hitung_jumlah_data()
# #
# #
# # print("\n=== KONDISI SEBELUM ARO ===")
# # print("ID deposito       :", deposito.ID)
# # print("Nomor rekening    :", rekening.norek)
# # print(
# #     "Nominal lama      : Rp"
# #     + Utilitas.format_rupiah(nominal_sebelum)
# # )
# # print(
# #     "Bunga dihasilkan  : Rp"
# #     + Utilitas.format_rupiah(bunga_dihasilkan)
# # )
# # print(
# #     "Saldo rekening    : Rp"
# #     + Utilitas.format_rupiah(saldo_sebelum)
# # )
# # print("Tanggal buka      :", deposito.tanggal_buka)
# # print("Jatuh tempo       :", deposito.jatuh_tempo)
# # print("Jenis ARO         :", deposito.jenis_aro)
# # print("Lama ARO          :", deposito.lama_aro)
# # print("Proses ARO        :", deposito.proses_aro)
# #
# #
# # # ============================================================
# # # 4. MENJALANKAN PERPANJANGAN
# # # ============================================================
# #
# # hasil = DepositoService.perpanjangan(
# #     deposito=deposito,
# #     hari_ini=JATUH_TEMPO_AWAL
# # )
# #
# # assert hasil is True, (
# #     "Service perpanjangan tidak mengembalikan True"
# # )
# #
# #
# # # ============================================================
# # # 5. MEMUAT ULANG HASIL DARI SQLITE
# # # ============================================================
# # #
# # # Kita memuat objek baru agar yang diperiksa benar-benar hasil
# # # penyimpanan SQLite, bukan hanya perubahan objek di memori.
# # # ============================================================
# #
# # deposito_sesudah = cari_deposito_aktif(ID_DEPOSITO)
# #
# # if deposito_sesudah is None:
# #     raise AssertionError(
# #         f"Deposito ID {ID_DEPOSITO} tidak ditemukan setelah ARO"
# #     )
# #
# # rekening_sesudah = deposito_sesudah.rekening
# # jumlah_sesudah = hitung_jumlah_data()
# #
# #
# # # ============================================================
# # # 6. MENGAMBIL TRANSAKSI, RIWAYAT, DAN AUDIT
# # # ============================================================
# #
# # koneksi = buat_koneksi()
# #
# # try:
# #     transaksi = koneksi.execute(
# #         """
# #         SELECT *
# #         FROM transaksi
# #         WHERE jenis = ?
# #           AND jenis_referensi = ?
# #           AND id_referensi = ?
# #         ORDER BY id DESC
# #         LIMIT 1
# #         """,
# #         (
# #             JenisTransaksi.KAPITALISASI_BUNGA_DEPOSITO.value,
# #             JenisReferensi.DEPOSITO.value,
# #             ID_DEPOSITO
# #         )
# #     ).fetchone()
# #
# #     assert transaksi is not None, (
# #         "Transaksi kapitalisasi bunga tidak ditemukan"
# #     )
# #
# #     id_transaksi = transaksi["id"]
# #
# #     daftar_riwayat = koneksi.execute(
# #         """
# #         SELECT *
# #         FROM riwayat
# #         WHERE transaksi_id = ?
# #         ORDER BY id
# #         """,
# #         (id_transaksi,)
# #     ).fetchall()
# #
# #     daftar_audit = koneksi.execute(
# #         """
# #         SELECT *
# #         FROM audit
# #         WHERE transaksi_id = ?
# #         ORDER BY id
# #         """,
# #         (id_transaksi,)
# #     ).fetchall()
# #
# # finally:
# #     koneksi.close()
# #
# #
# # # ============================================================
# # # 7. MEMERIKSA HASIL DEPOSITO
# # # ============================================================
# #
# # assert deposito_sesudah.nominal == nominal_yang_diharapkan, (
# #     f"Nominal seharusnya {nominal_yang_diharapkan}, "
# #     f"tetapi ditemukan {deposito_sesudah.nominal}"
# # )
# # print("✅ Pokok dan bunga menjadi nominal deposito baru")
# #
# # assert deposito_sesudah.nominal == (
# #     nominal_sebelum + bunga_dihasilkan
# # ), "Kenaikan nominal tidak sama dengan bunga"
# # print("✅ Nominal deposito bertambah sebesar bunga")
# #
# # assert rekening_sesudah.saldo == saldo_yang_diharapkan, (
# #     "Saldo rekening berubah pada ARO pokok+bunga"
# # )
# # print("✅ Saldo rekening tidak berubah")
# #
# # assert (
# #     deposito_sesudah.tanggal_buka
# #     == tanggal_buka_yang_diharapkan
# # ), "Tanggal buka periode baru tidak sesuai"
# # print("✅ Tanggal buka baru sesuai jatuh tempo lama")
# #
# # assert (
# #     deposito_sesudah.jatuh_tempo
# #     == jatuh_tempo_yang_diharapkan
# # ), "Jatuh tempo periode baru tidak sesuai"
# # print("✅ Jatuh tempo baru berhasil dihitung")
# #
# # assert deposito_sesudah.lama_bulan == deposito.lama_aro, (
# #     "Tenor periode baru tidak mengikuti lama ARO"
# # )
# # print("✅ Tenor periode baru mengikuti lama ARO")
# #
# # assert (
# #     deposito_sesudah.bunga
# #     == bunga_baru_yang_diharapkan
# # ), "Bunga periode baru tidak sesuai tenor ARO"
# # print("✅ Bunga periode baru sesuai tenor ARO")
# #
# # assert deposito_sesudah.proses_aro == JATUH_TEMPO_AWAL, (
# #     "Tanggal proses ARO tidak sesuai"
# # )
# # print("✅ Tanggal proses ARO berhasil disimpan")
# #
# # assert deposito_sesudah.status == StatusDeposito.AKTIF, (
# #     "Deposito tidak aktif setelah diperpanjang"
# # )
# # print("✅ Deposito tetap aktif setelah diperpanjang")
# #
# #
# # # ============================================================
# # # 8. MEMERIKSA TRANSAKSI KAPITALISASI
# # # ============================================================
# #
# # assert jumlah_sesudah["transaksi"] == (
# #     jumlah_sebelum["transaksi"] + 1
# # ), "Transaksi seharusnya bertambah tepat satu"
# # print("✅ Transaksi bertambah tepat satu")
# #
# # assert transaksi["jenis"] == (
# #     JenisTransaksi.KAPITALISASI_BUNGA_DEPOSITO.value
# # ), "Jenis transaksi tidak sesuai"
# # print("✅ Jenis transaksi kapitalisasi sesuai")
# #
# # assert transaksi["nominal"] == bunga_dihasilkan, (
# #     "Nominal transaksi tidak sama dengan bunga kapitalisasi"
# # )
# # print("✅ Nominal transaksi berisi bunga kapitalisasi")
# #
# # assert transaksi["biaya"] == 0, (
# #     "Kapitalisasi deposito seharusnya tidak memiliki biaya"
# # )
# # print("✅ Kapitalisasi tidak memiliki biaya")
# #
# # assert transaksi["norek_sumber"] is None, (
# #     "Kapitalisasi tidak memiliki rekening sumber"
# # )
# #
# # assert transaksi["norek_tujuan"] is None, (
# #     "Kapitalisasi tidak memiliki rekening tujuan"
# # )
# # print("✅ Tidak tercatat perpindahan antar-rekening")
# #
# # assert transaksi["saldo_sumber_sebelum"] is None
# # assert transaksi["saldo_sumber_sesudah"] is None
# # assert transaksi["saldo_tujuan_sebelum"] is None
# # assert transaksi["saldo_tujuan_sesudah"] is None
#
#
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.utils.utility import (
#     JenisReferensi,
#     JenisTransaksi
# )
#
#
# ID_DEPOSITO = 14
#
#
# koneksi = buat_koneksi()
#
# try:
#     # Mengambil semua transaksi kapitalisasi untuk deposito 14.
#     daftar_transaksi = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE jenis = ?
#           AND jenis_referensi = ?
#           AND id_referensi = ?
#         ORDER BY id
#         """,
#         (
#             JenisTransaksi.KAPITALISASI_BUNGA_DEPOSITO.value,
#             JenisReferensi.DEPOSITO.value,
#             ID_DEPOSITO
#         )
#     ).fetchall()
#
#     # Harus hanya ada satu transaksi karena ARO ID 14
#     # hanya dijalankan satu kali.
#     assert len(daftar_transaksi) == 1, (
#         f"Seharusnya hanya ada satu transaksi ARO, "
#         f"tetapi ditemukan {len(daftar_transaksi)}"
#     )
#
#     transaksi = daftar_transaksi[0]
#     id_transaksi = transaksi["id"]
#
#     # Mengambil catatan yang terhubung ke transaksi ARO.
#     daftar_riwayat = koneksi.execute(
#         """
#         SELECT *
#         FROM riwayat
#         WHERE transaksi_id = ?
#         ORDER BY id
#         """,
#         (id_transaksi,)
#     ).fetchall()
#
#     daftar_audit = koneksi.execute(
#         """
#         SELECT *
#         FROM audit
#         WHERE transaksi_id = ?
#         ORDER BY id
#         """,
#         (id_transaksi,)
#     ).fetchall()
#
#     print("=== DATA TRANSAKSI ===")
#     print("ID transaksi      :", transaksi["id"])
#     print("Jenis             :", transaksi["jenis"])
#     print("Rekening sumber   :", transaksi["norek_sumber"])
#     print("Rekening tujuan   :", transaksi["norek_tujuan"])
#     print("Nominal           :", transaksi["nominal"])
#     print("Biaya             :", transaksi["biaya"])
#     print(
#         "Saldo sumber awal :",
#         transaksi["saldo_sumber_sebelum"]
#     )
#     print(
#         "Saldo sumber akhir:",
#         transaksi["saldo_sumber_sesudah"]
#     )
#     print(
#         "Saldo tujuan awal :",
#         transaksi["saldo_tujuan_sebelum"]
#     )
#     print(
#         "Saldo tujuan akhir:",
#         transaksi["saldo_tujuan_sesudah"]
#     )
#     print(
#         "Jenis referensi   :",
#         transaksi["jenis_referensi"]
#     )
#     print("ID referensi      :", transaksi["id_referensi"])
#     print("Waktu             :", transaksi["waktu"])
#     print()
#
#     # Kapitalisasi tidak memindahkan saldo antar-rekening.
#     assert transaksi["norek_sumber"] is None
#     assert transaksi["norek_tujuan"] is None
#     assert transaksi["saldo_sumber_sebelum"] is None
#     assert transaksi["saldo_sumber_sesudah"] is None
#     assert transaksi["saldo_tujuan_sebelum"] is None
#     assert transaksi["saldo_tujuan_sesudah"] is None
#     print("✅ Seluruh kolom perpindahan saldo bernilai NULL")
#
#     assert transaksi["biaya"] == 0, (
#         "Kapitalisasi deposito seharusnya tidak memiliki biaya"
#     )
#     print("✅ Kapitalisasi tidak memiliki biaya")
#
#     assert transaksi["nominal"] == 2_500, (
#         "Nominal transaksi kapitalisasi bukan Rp2.500"
#     )
#     print("✅ Nominal kapitalisasi sesuai bunga periode pertama")
#
#     assert transaksi["jenis_referensi"] == (
#         JenisReferensi.DEPOSITO.value
#     ), "Jenis referensi transaksi bukan deposito"
#     print("✅ Jenis referensi tersimpan sebagai 'deposito'")
#
#     assert transaksi["id_referensi"] == ID_DEPOSITO, (
#         "ID referensi tidak menunjuk deposito ID 14"
#     )
#     print("✅ ID referensi menunjuk deposito ID 14")
#
#     assert transaksi["waktu"] is not None, (
#         "Waktu transaksi tidak tersimpan"
#     )
#     print("✅ Waktu transaksi berhasil disimpan")
#
#     # Memeriksa dua riwayat yang dibuat oleh proses ARO.
#     assert len(daftar_riwayat) == 2, (
#         f"Seharusnya ada dua riwayat, "
#         f"tetapi ditemukan {len(daftar_riwayat)}"
#     )
#
#     jenis_riwayat = {
#         riwayat["jenis"]
#         for riwayat in daftar_riwayat
#     }
#
#     assert "kapitalisasi bunga deposito" in jenis_riwayat
#     assert "perpanjang deposito" in jenis_riwayat
#     print("✅ Dua riwayat terhubung ke transaksi yang sama")
#
#     # Memeriksa satu audit perpanjangan.
#     assert len(daftar_audit) == 1, (
#         f"Seharusnya ada satu audit, "
#         f"tetapi ditemukan {len(daftar_audit)}"
#     )
#
#     assert daftar_audit[0]["jenis"] == "perpanjang deposito"
#     print("✅ Audit perpanjangan terhubung ke transaksi yang sama")
#
#     print("\n=== RIWAYAT TERHUBUNG ===")
#
#     for riwayat in daftar_riwayat:
#         print(
#             f"ID {riwayat['id']} | "
#             f"Transaksi {riwayat['transaksi_id']} | "
#             f"{riwayat['jenis']} | "
#             f"{riwayat['log']}"
#         )
#
#     print("\n=== AUDIT TERHUBUNG ===")
#
#     for audit in daftar_audit:
#         print(
#             f"ID {audit['id']} | "
#             f"Transaksi {audit['transaksi_id']} | "
#             f"{audit['jenis']} | "
#             f"{audit['log']}"
#         )
#
# finally:
#     koneksi.close()
#
#
# print()
# print(
#     "✅ ARO POKOK+BUNGA ID 14 TERSIMPAN DENGAN BENAR "
#     "DAN TIDAK DIPROSES GANDA"
# )



import datetime
from unittest.mock import patch

from bank_djago.core.deposito import JenisAro
from bank_djago.penyimpanan.loaders.deposito_loader import (
    DepositoLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)


ID_DEPOSITO = 15
NOREK_PENGUJIAN = "3001781978899033"

TANGGAL_BUKA_AWAL = datetime.date(2026, 9, 4)
JATUH_TEMPO_AWAL = datetime.date(2026, 10, 4)

PESAN_ERROR = (
    "Kegagalan audit untuk menguji rollback ARO pokok+bunga"
)


def cari_deposito_aktif():
    """
    Memuat deposito aktif, kemudian mencari deposito ID 15.
    """
    daftar_deposito = (
        DepositoLoader.muat_semua_deposito_aktif()
    )

    return next(
        (
            deposito
            for deposito in daftar_deposito
            if deposito.ID == ID_DEPOSITO
        ),
        None
    )


def ambil_kondisi_database():
    """
    Mengambil kondisi penting dari SQLite.

    Kondisi sebelum dan setelah kegagalan harus sama persis
    apabila rollback bekerja dengan benar.
    """
    koneksi = buat_koneksi()

    try:
        deposito = koneksi.execute(
            """
            SELECT *
            FROM deposito
            WHERE id = ?
            """,
            (ID_DEPOSITO,)
        ).fetchone()

        rekening = koneksi.execute(
            """
            SELECT *
            FROM rekening
            WHERE norek = ?
            """,
            (NOREK_PENGUJIAN,)
        ).fetchone()

        jumlah_transaksi = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM transaksi"
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM riwayat"
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            "SELECT COUNT(*) AS jumlah FROM audit"
        ).fetchone()["jumlah"]

        transaksi_deposito = koneksi.execute(
            """
            SELECT *
            FROM transaksi
            WHERE jenis_referensi = 'deposito'
              AND id_referensi = ?
            ORDER BY id
            """,
            (ID_DEPOSITO,)
        ).fetchall()

        return {
            "deposito": dict(deposito),
            "rekening": dict(rekening),
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "transaksi_deposito": [
                dict(transaksi)
                for transaksi in transaksi_deposito
            ]
        }

    finally:
        koneksi.close()


def ambil_kondisi_objek(deposito):
    """
    Mengambil kondisi objek deposito dan rekening di memori.
    """
    return {
        "nominal": deposito.nominal,
        "bunga": deposito.bunga,
        "lama_bulan": deposito.lama_bulan,
        "tanggal_buka": deposito.tanggal_buka,
        "jatuh_tempo": deposito.jatuh_tempo,
        "status": deposito.status,
        "proses_aro": deposito.proses_aro,
        "saldo_rekening": deposito.rekening.saldo,
        "jumlah_riwayat_objek": len(
            deposito.rekening.riwayat
        )
    }


# ============================================================
# 1. MEMUAT DAN MEMERIKSA DEPOSITO
# ============================================================

deposito = cari_deposito_aktif()

if deposito is None:
    raise AssertionError(
        f"Deposito aktif ID {ID_DEPOSITO} tidak ditemukan"
    )

# Pemeriksaan ini mencegah deposito yang salah ikut diuji.
assert deposito.rekening.norek == NOREK_PENGUJIAN
assert deposito.nominal == 1_000_000
assert deposito.jenis_aro == JenisAro.POKOK_BUNGA
assert deposito.lama_bulan == 1
assert deposito.lama_aro == 1
assert deposito.tanggal_buka == TANGGAL_BUKA_AWAL
assert deposito.jatuh_tempo == JATUH_TEMPO_AWAL
assert deposito.proses_aro is None
assert deposito.status == StatusDeposito.AKTIF

print("✅ Deposito ID 15 siap untuk pengujian rollback")


# ============================================================
# 2. MENYIMPAN KONDISI SEBELUM PENGUJIAN
# ============================================================

database_sebelum = ambil_kondisi_database()
objek_sebelum = ambil_kondisi_objek(deposito)

print("\n=== KONDISI SEBELUM ===")
print(database_sebelum)


# ============================================================
# 3. MEMAKSA PENYIMPANAN AUDIT GAGAL
# ============================================================
#
# Audit berada dekat bagian akhir transaksi database.
# Saat audit gagal, perubahan deposito, transaksi, dan riwayat
# yang sebelumnya sudah dicoba harus ikut dibatalkan.
# ============================================================

error_dipicu = False

with patch.object(
    AuditRepository,
    "tambah_audit",
    side_effect=RuntimeError(PESAN_ERROR)
):
    try:
        DepositoService.perpanjangan(
            deposito=deposito,
            hari_ini=JATUH_TEMPO_AWAL
        )

    except RuntimeError as error:
        # Memastikan RuntimeError berasal dari kegagalan buatan.
        assert str(error) == PESAN_ERROR, (
            f"RuntimeError yang muncul berbeda: {error}"
        )

        error_dipicu = True

        print("\n✅ Kegagalan buatan berhasil dipicu")
        print("Pesan error:", error)


assert error_dipicu, (
    "Kegagalan audit tidak terjadi sehingga rollback belum diuji"
)


# ============================================================
# 4. MENGAMBIL KONDISI SETELAH ROLLBACK
# ============================================================

database_setelah = ambil_kondisi_database()
objek_setelah = ambil_kondisi_objek(deposito)

print("\n=== KONDISI SETELAH ROLLBACK ===")
print(database_setelah)


# ============================================================
# 5. MEMERIKSA DATABASE
# ============================================================

assert database_setelah["deposito"] == (
    database_sebelum["deposito"]
), "Data deposito berubah setelah rollback"

print("✅ Data deposito tidak berubah")


assert database_setelah["rekening"] == (
    database_sebelum["rekening"]
), "Data rekening berubah setelah rollback"

print("✅ Data dan saldo rekening tidak berubah")


assert database_setelah["jumlah_transaksi"] == (
    database_sebelum["jumlah_transaksi"]
), "Transaksi kapitalisasi masih tersimpan"

print("✅ Transaksi kapitalisasi tidak tersisa")


assert database_setelah["jumlah_riwayat"] == (
    database_sebelum["jumlah_riwayat"]
), "Riwayat ARO masih tersimpan"

print("✅ Riwayat ARO tidak tersisa")


assert database_setelah["jumlah_audit"] == (
    database_sebelum["jumlah_audit"]
), "Jumlah audit berubah setelah rollback"

print("✅ Audit tidak bertambah")


assert database_setelah["transaksi_deposito"] == (
    database_sebelum["transaksi_deposito"]
), "Daftar transaksi deposito ID 15 berubah"

print("✅ Transaksi deposito ID 15 tetap seperti semula")


# ============================================================
# 6. MEMERIKSA OBJEK DI MEMORI
# ============================================================
#
# Service memperbarui objek setelah commit berhasil.
# Karena terjadi error, objek seharusnya tidak berubah.
# ============================================================

assert objek_setelah == objek_sebelum, (
    "Objek deposito atau rekening berubah setelah rollback"
)

print("✅ Objek deposito dan rekening tidak berubah")


# ============================================================
# 7. MEMUAT ULANG HASIL DARI SQLITE
# ============================================================

deposito_muat_ulang = cari_deposito_aktif()

if deposito_muat_ulang is None:
    raise AssertionError(
        "Deposito ID 15 tidak ditemukan setelah rollback"
    )

assert deposito_muat_ulang.nominal == 1_000_000
assert deposito_muat_ulang.tanggal_buka == TANGGAL_BUKA_AWAL
assert deposito_muat_ulang.jatuh_tempo == JATUH_TEMPO_AWAL
assert deposito_muat_ulang.proses_aro is None
assert deposito_muat_ulang.status == StatusDeposito.AKTIF

print("✅ Data hasil pemuatan ulang tetap seperti kondisi awal")

print()
print(
    "✅ ROLLBACK ARO POKOK+BUNGA BERHASIL: "
    "deposito, rekening, transaksi, riwayat, audit, "
    "dan objek tidak berubah"
)