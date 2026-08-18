# pinjaman = next((item for item in bank.daftar_pinjaman if item.status == StatusPinjaman.AKTIF), None)
# if pinjaman is not None:
#     hari_uji = (
#             pinjaman.tanggal_jatuh_tempo
#             + datetime.timedelta(days=1)
#     )
#
#     hari_terlambat = (
#         PinjamanService.perbarui_status_pembayaran(
#             pinjaman,
#             hari_uji
#         )
#     )
#
#     print("Jatuh tempo       :", pinjaman.tanggal_jatuh_tempo)
#     print("Tanggal pengujian :", hari_uji)
#     print("Hari terlambat    :", hari_terlambat)
#     print("Status pembayaran :", pinjaman.status_pembayaran.value)
#
#     assert hari_terlambat == 1, (
#         "Keterlambatan seharusnya satu hari"
#     )
#
#     assert (
#             pinjaman.status_pembayaran
#             == StatusPembayaran.MENUNGGAK
#     ), "Status seharusnya MENUNGGAK"
#
#     print("✅ Pengujian keterlambatan berhasil")


# nasabah = bank.data_nasabah["3510152602082002"]
# pinjaman = nasabah.pinjaman
# # PinjamanService.cairkan_pinjaman(bank,pinjaman,datetime.date(2027,1,31))
# PinjamanService.bayar_cicilan(
#     bank,
#     pinjaman,
#     datetime.date(2027, 2, 20)
# )
#
# print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
# print("Jatuh tempo baru :", pinjaman.tanggal_jatuh_tempo)
# print(
#     "Boleh bayar lagi :",
#     PinjamanService.tanggal_boleh_bayar(pinjaman)
# )
#
#
# print("Tanggal pencairan :", pinjaman.tanggal_pencairan)
# print("Jatuh tempo       :", pinjaman.tanggal_jatuh_tempo)
#
# PinjamanService.bayar_cicilan(
#     bank,
#     pinjaman,
#     datetime.date(2027, 3, 1)
# )
#
# print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
# print("Jatuh tempo baru :", pinjaman.tanggal_jatuh_tempo)
# print(
#     "Boleh bayar lagi :",
#     PinjamanService.tanggal_boleh_bayar(pinjaman))

# hari_ini = datetime.date(2026,9,18)
# # Scheduler.jalankan(bank,hari_ini)
# #
# # hari_ini = datetime.date(2026, 9, 18)
# # Scheduler.jalankan(bank, hari_ini
# nasabah = bank.data_nasabah["3150152602002002"]
# pinjaman = nasabah.pinjaman
# # PinjamanService.bayar_cicilan(bank,pinjaman,hari_ini)
# #
# tanggal_test = [
#     datetime.date(2026, 9, 5),  # cicilan 1
#     datetime.date(2026, 9, 18),  # cicilan 2
#     datetime.date(2026, 10, 18),  # cicilan 3
#     datetime.date(2026, 11, 18),  # cicilan 4
#     datetime.date(2026, 12, 18),  # cicilan 5
#     datetime.date(2027, 1, 18),  # cicilan 6
# ]
#
# for tanggal in tanggal_test:
#     PinjamanService.bayar_cicilan(
#         bank,
#         pinjaman,
#         tanggal
#     )
#
#     print(
#         tanggal,
#         pinjaman.cicilan_terbayar,
#         pinjaman.sisa_pokok,
#         pinjaman.status
#     )
# PinjamanService.bayar_cicilan(bank,pinjaman,datetime.date(2027,2,18))
# bank.proses_harian()

# -----------------------------------------------------------------------------------------------------------------------
# error = BankService.cek_integritas_rekening(bank)
#
# if not error:
#     print("✅ Integritas rekening valid.")
# else:
#     print("❌ Ditemukan masalah:")
#     for item in error:
#         print("-", item)
# error = BankService.cek_integritas_deposito(bank)
#
# if not error:
#     print("✅ Integritas deposito valid.")
# else:
#     print("❌ Ditemukan masalah:")
#
#     for item in error:
#         print("-", item)
#
# error = BankService.cek_integritas_pinjaman(bank)
#
# if not error:
#     print("✅ Integritas pinjaman valid.")
# else:
#     print("❌ Ditemukan masalah:")
#
#     for item in error:
#         print("-", item)
# #
# error = BankService.cek_integritas_notifikasi(bank)
#
# if not error:
#     print("✅ Integritas notifikasi valid.")
# else:
#     print("❌ Ditemukan masalah:")
#     for item in error:
#         print("-", item)


# -------------------------------------------------------------------------------------------------------------------------------

# jatuh_tempo = pinjaman.tanggal_jatuh_tempo
# batas = PinjamanService.BATAS_HARI_TUNGGAKAN
# # percobaan hari terakhir toleransi
# hari_uji = (jatuh_tempo + timedelta(days=batas))
# denda = PinjamanService.hitung_denda(pinjaman, hari_uji)
# assert denda == 0, (
#     "Hari terakhir masa toleransi seharusnya belum didenda"
# )
# print("✅Hari terakhir toleransi")
#
# hari_uji = (jatuh_tempo + timedelta(days=batas + 1))
# denda = PinjamanService.hitung_denda(pinjaman, hari_uji)
# denda_harian = round(
#     pinjaman.cicilan_tetap
#     * PinjamanService.PERSENTASE_DENDA_HARIAN
# )
#
# assert denda == denda_harian, (
#     "Denda hari pertama tidak sesuai"
# )
#
# print("✅ Denda hari pertama valid")
#
# hari_uji = (
#         jatuh_tempo
#         + datetime.timedelta(days=1000)
# )
#
# denda = PinjamanService.hitung_denda(
#     pinjaman,
#     hari_uji
# )
#
# maksimal_denda = round(
#     pinjaman.cicilan_tetap
#     * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
# )
#
# assert denda == maksimal_denda, (
#     "Denda seharusnya berhenti pada batas maksimal"
# )
#
# print("✅ Batas maksimal denda valid")

# ----------------------------------------------------------------------------------------------------------------------
# def uji_save_load_pinjaman_menunggak():
#     """
#     Menguji konsistensi pinjaman menunggak setelah proses
#     penyimpanan dan pemuatan ulang JSON.
#
#     Pengujian memastikan:
#     - Data asli tidak ditimpa.
#     - Tanggal jatuh tempo tetap sama.
#     - Status pinjaman tetap AKTIF.
#     - Jumlah cicilan terbayar tetap sama.
#     - Relasi nasabah dan rekening tetap menggunakan objek
#       yang terdaftar di bank.
#     - Hari keterlambatan dan denda dapat dihitung kembali.
#     - Notifikasi tunggakan tetap mempunyai referensi objek.
#     """
#
#     # Muat data awal dari penyimpanan asli.
#     bank = JsonStorage.muat_bank()
#
#     # Ambil satu pinjaman aktif.
#     pinjaman = next(
#         (
#             item
#             for item in bank.daftar_pinjaman
#             if item.status == StatusPinjaman.AKTIF
#         ),
#         None
#     )
#
#     if pinjaman is None:
#         print("Tidak ada pinjaman aktif untuk diuji.")
#         return
#
#     # Simpan identitas objek yang akan dicari kembali
#     # setelah proses pemuatan JSON.
#     id_pinjaman = pinjaman.ID
#     nik_pemilik = pinjaman.pemilik.NIK
#     nomor_rekening = pinjaman.rekening.norek
#
#     # Gunakan hari pertama setelah masa toleransi.
#     hari_uji = (
#         pinjaman.tanggal_jatuh_tempo
#         + datetime.timedelta(
#             days=(
#                 PinjamanService.BATAS_HARI_TUNGGAKAN
#                 + 1
#             )
#         )
#     )
#
#     # Jalankan scheduler agar notifikasi tunggakan dibuat.
#     Scheduler.jalankan(bank, hari_uji)
#
#     # Simpan state sebelum proses save/load.
#     jatuh_tempo_sebelum = pinjaman.tanggal_jatuh_tempo
#     status_sebelum = pinjaman.status
#     cicilan_terbayar_sebelum = pinjaman.cicilan_terbayar
#     sisa_pokok_sebelum = pinjaman.sisa_pokok
#
#     hari_terlambat_sebelum = (
#         PinjamanService.hitung_hari_terlambat(
#             pinjaman,
#             hari_uji
#         )
#     )
#
#     denda_sebelum = PinjamanService.hitung_denda(
#         pinjaman,
#         hari_uji
#     )
#
#     # Simpan seluruh lokasi file asli agar dapat
#     # dikembalikan setelah pengujian.
#     lokasi_asli = {
#         "file_rek": JsonStorage.file_rek,
#         "file_nasabah": JsonStorage.file_nasabah,
#         "file_audit": JsonStorage.file_audit,
#         "file_depo": JsonStorage.file_depo,
#         "file_pinjaman": JsonStorage.file_pinjaman
#     }
#
#     try:
#         # Buat direktori sementara yang otomatis dihapus
#         # setelah pengujian selesai.
#         with tempfile.TemporaryDirectory() as direktori:
#             direktori = Path(direktori)
#
#             # Arahkan JsonStorage ke file sementara agar
#             # data JSON asli tidak berubah.
#             JsonStorage.file_rek = str(
#                 direktori / "rekening.json"
#             )
#
#             JsonStorage.file_nasabah = str(
#                 direktori / "nasabah.json"
#             )
#
#             JsonStorage.file_audit = str(
#                 direktori / "audit.json"
#             )
#
#             JsonStorage.file_depo = str(
#                 direktori / "deposito.json"
#             )
#
#             JsonStorage.file_pinjaman = str(
#                 direktori / "pinjaman.json"
#             )
#
#             # Simpan bank ke seluruh file sementara.
#             JsonStorage.simpan_bank(bank)
#
#             # Muat kembali bank dari file sementara.
#             bank_hasil = JsonStorage.muat_bank()
#
#             # Cari pinjaman yang sama berdasarkan ID
#             # dan NIK pemiliknya.
#             pinjaman_hasil = next(
#                 (
#                     item
#                     for item in bank_hasil.daftar_pinjaman
#                     if (
#                         item.ID == id_pinjaman
#                         and item.pemilik.NIK == nik_pemilik
#                     )
#                 ),
#                 None
#             )
#
#             assert pinjaman_hasil is not None, (
#                 "Pinjaman tidak ditemukan setelah load"
#             )
#
#             # Hitung ulang keterlambatan dan denda
#             # berdasarkan data hasil load.
#             hari_terlambat_hasil = (
#                 PinjamanService.hitung_hari_terlambat(
#                     pinjaman_hasil,
#                     hari_uji
#                 )
#             )
#
#             denda_hasil = PinjamanService.hitung_denda(
#                 pinjaman_hasil,
#                 hari_uji
#             )
#
#             # Pastikan state utama pinjaman tetap sama.
#             assert (
#                 pinjaman_hasil.tanggal_jatuh_tempo
#                 == jatuh_tempo_sebelum
#             ), "Jatuh tempo berubah setelah save/load"
#
#             assert (
#                 pinjaman_hasil.status
#                 == status_sebelum
#             ), "Status pinjaman berubah setelah save/load"
#
#             assert (
#                 pinjaman_hasil.cicilan_terbayar
#                 == cicilan_terbayar_sebelum
#             ), (
#                 "Jumlah cicilan terbayar berubah "
#                 "setelah save/load"
#             )
#
#             assert math.isclose(
#                 pinjaman_hasil.sisa_pokok,
#                 sisa_pokok_sebelum,
#                 rel_tol=1e-9
#             ), "Sisa pokok berubah setelah save/load"
#
#             # Pastikan hasil perhitungan waktu tetap sama.
#             assert (
#                 hari_terlambat_hasil
#                 == hari_terlambat_sebelum
#             ), (
#                 "Hari keterlambatan berubah "
#                 "setelah save/load"
#             )
#
#             assert denda_hasil == denda_sebelum, (
#                 "Nominal denda berubah setelah save/load"
#             )
#
#             # Pastikan relasi pemilik menunjuk objek nasabah
#             # yang tersimpan dalam bank hasil load.
#             assert (
#                 pinjaman_hasil.pemilik
#                 is bank_hasil.data_nasabah[nik_pemilik]
#             ), "Relasi pinjaman dengan nasabah tidak valid"
#
#             # Pastikan relasi rekening menunjuk objek rekening
#             # yang tersimpan dalam indeks bank.
#             assert (
#                 pinjaman_hasil.rekening
#                 is bank_hasil.rekening_index[nomor_rekening]
#             ), "Relasi pinjaman dengan rekening tidak valid"
#
#             # Cari notifikasi yang merujuk pinjaman tersebut.
#             notifikasi_pinjaman = [
#                 notifikasi
#                 for notifikasi
#                 in pinjaman_hasil.pemilik.notifikasi
#                 if (
#                     notifikasi.referensi_id
#                     == JenisReferensiID.PINJAMAN
#                     and notifikasi.id_objek == id_pinjaman
#                 )
#             ]
#
#             assert notifikasi_pinjaman, (
#                 "Notifikasi tunggakan tidak ditemukan "
#                 "setelah save/load"
#             )
#
#             # Jalankan scheduler kembali pada tanggal yang sama.
#             Scheduler.jalankan(
#                 bank_hasil,
#                 hari_uji
#             )
#
#             # Pastikan repeated scheduler tidak membuat
#             # notifikasi pinjaman menjadi ganda.
#             notifikasi_setelah_scheduler = [
#                 notifikasi
#                 for notifikasi
#                 in pinjaman_hasil.pemilik.notifikasi
#                 if (
#                     notifikasi.referensi_id
#                     == JenisReferensiID.PINJAMAN
#                     and notifikasi.id_objek == id_pinjaman
#                 )
#             ]
#
#             assert (
#                 len(notifikasi_setelah_scheduler) == 1
#             ), (
#                 "Repeated scheduler menghasilkan "
#                 "notifikasi pinjaman ganda"
#             )
#
#             print()
#             print("=" * 60)
#             print("✅ SAVE/LOAD PINJAMAN MENUNGGAK BERHASIL")
#             print(f"Pinjaman          : #{id_pinjaman}")
#             print(f"Jatuh tempo       : {jatuh_tempo_sebelum}")
#             print(f"Tanggal simulasi  : {hari_uji}")
#             print(
#                 "Hari terlambat    : "
#                 f"{hari_terlambat_hasil}"
#             )
#             print(
#                 "Denda sebelum     : "
#                 f"Rp{Utilitas.format_rupiah(denda_sebelum)}"
#             )
#             print(
#                 "Denda setelah load: "
#                 f"Rp{Utilitas.format_rupiah(denda_hasil)}"
#             )
#             print(
#                 "Notifikasi        : "
#                 f"{len(notifikasi_setelah_scheduler)}"
#             )
#             print("=" * 60)
#
#     finally:
#         # Kembalikan seluruh lokasi penyimpanan asli,
#         # termasuk ketika salah satu assert gagal.
#         JsonStorage.file_rek = lokasi_asli["file_rek"]
#         JsonStorage.file_nasabah = lokasi_asli["file_nasabah"]
#         JsonStorage.file_audit = lokasi_asli["file_audit"]
#         JsonStorage.file_depo = lokasi_asli["file_depo"]
#         JsonStorage.file_pinjaman = lokasi_asli["file_pinjaman"]


# ----------------------------------------------------------------------------------------------------------------------
# def uji_pelunasan_dengan_denda():
#     """
#     Menguji pelunasan pinjaman dengan membayar seluruh cicilan
#     sebelumnya secara normal, kemudian membayar cicilan terakhir
#     setelah masa toleransi berakhir.
#
#     Pengujian memastikan:
#     - Lifecycle pinjaman bergerak secara konsisten.
#     - Cicilan terakhir dikenai denda.
#     - Denda ikut dipotong dari saldo.
#     - Denda tidak mengurangi pokok pinjaman.
#     - Status akhir menjadi LUNAS.
#     - Referensi pinjaman aktif milik nasabah dibersihkan.
#     - Riwayat dan notifikasi pelunasan dibuat.
#     """
#
#     # Muat data baru agar pengujian tidak dipengaruhi
#     # oleh pengujian sebelumnya.
#     bank = JsonStorage.muat_bank()
#
#     # Ambil satu pinjaman yang masih aktif.
#     pinjaman = next(
#         (
#             item
#             for item in bank.daftar_pinjaman
#             if item.status == StatusPinjaman.AKTIF
#         ),
#         None
#     )
#
#     if pinjaman is None:
#         print("Tidak ada pinjaman aktif untuk diuji.")
#         return
#
#     nasabah = pinjaman.pemilik
#     rekening = pinjaman.rekening
#
#     # Hitung jumlah cicilan yang masih harus dibayar.
#     sisa_cicilan = (
#         pinjaman.tenor
#         - pinjaman.cicilan_terbayar
#     )
#
#     if sisa_cicilan < 1:
#         print("Pinjaman tidak memiliki cicilan tersisa.")
#         return
#
#     # Siapkan saldo untuk membayar seluruh cicilan tersisa
#     # dan kemungkinan denda maksimal pada cicilan terakhir.
#     maksimal_denda = (
#         pinjaman.cicilan_tetap
#         * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
#     )
#
#     saldo_dibutuhkan = (
#         rekening.saldosetor_min
#         + pinjaman.cicilan_tetap * sisa_cicilan
#         + maksimal_denda
#     )
#
#     if rekening.saldo < saldo_dibutuhkan:
#         rekening.tambah_saldo(
#             saldo_dibutuhkan - rekening.saldo
#         )
#
#     print()
#     print("=" * 60)
#     print("PENGUJIAN PELUNASAN DENGAN DENDA")
#     print(f"Pinjaman            : #{pinjaman.ID}")
#     print(f"Tenor               : {pinjaman.tenor} bulan")
#     print(
#         "Cicilan terbayar    : "
#         f"{pinjaman.cicilan_terbayar}"
#     )
#     print(
#         "Cicilan tersisa     : "
#         f"{sisa_cicilan}"
#     )
#     print(
#         "Jatuh tempo awal    : "
#         f"{pinjaman.tanggal_jatuh_tempo}"
#     )
#     print("=" * 60)
#
#     # Bayar seluruh cicilan sebelum cicilan terakhir
#     # tepat pada tanggal jatuh temponya.
#     while (
#         pinjaman.cicilan_terbayar
#         < pinjaman.tenor - 1
#     ):
#         jatuh_tempo_sebelum = (
#             pinjaman.tanggal_jatuh_tempo
#         )
#
#         cicilan_terbayar_sebelum = (
#             pinjaman.cicilan_terbayar
#         )
#
#         PinjamanService.bayar_cicilan(
#             bank,
#             pinjaman,
#             jatuh_tempo_sebelum
#         )
#
#         # Pastikan satu pembayaran hanya menyelesaikan
#         # satu cicilan.
#         assert (
#             pinjaman.cicilan_terbayar
#             == cicilan_terbayar_sebelum + 1
#         ), "Jumlah cicilan terbayar tidak bertambah satu"
#
#         # Pastikan jatuh tempo maju satu bulan dari
#         # jadwal sebelumnya.
#         jatuh_tempo_diharapkan = (
#             Utilitas.tambah_bulan(
#                 jatuh_tempo_sebelum,
#                 1
#             )
#         )
#
#         assert (
#             pinjaman.tanggal_jatuh_tempo
#             == jatuh_tempo_diharapkan
#         ), "Jatuh tempo tidak maju sesuai jadwal"
#
#         # Pastikan pinjaman belum lunas sebelum
#         # pembayaran cicilan terakhir.
#         assert (
#             pinjaman.status == StatusPinjaman.AKTIF
#         ), "Pinjaman lunas sebelum cicilan terakhir"
#
#         print(
#             f"Cicilan ke-{pinjaman.cicilan_terbayar} "
#             f"dibayar pada {jatuh_tempo_sebelum}"
#         )
#
#     # Pastikan sekarang hanya tersisa satu cicilan.
#     assert (
#         pinjaman.cicilan_terbayar
#         == pinjaman.tenor - 1
#     ), "Pinjaman seharusnya menyisakan satu cicilan"
#
#     # Tentukan pembayaran terakhir pada hari pertama
#     # setelah masa toleransi berakhir.
#     jatuh_tempo_terakhir = pinjaman.tanggal_jatuh_tempo
#
#     hari_uji = (
#         jatuh_tempo_terakhir
#         + datetime.timedelta(
#             days=(
#                 PinjamanService.BATAS_HARI_TUNGGAKAN
#                 + 1
#             )
#         )
#     )
#
#     # Hitung denda cicilan terakhir.
#     hari_terlambat = (
#         PinjamanService.hitung_hari_terlambat(
#             pinjaman,
#             hari_uji
#         )
#     )
#
#     denda = PinjamanService.hitung_denda(
#         pinjaman,
#         hari_uji
#     )
#
#     denda_harian_diharapkan = round(
#         pinjaman.cicilan_tetap
#         * PinjamanService.PERSENTASE_DENDA_HARIAN
#     )
#
#     assert (
#         hari_terlambat
#         == PinjamanService.BATAS_HARI_TUNGGAKAN + 1
#     ), "Jumlah hari keterlambatan tidak sesuai"
#
#     assert denda == denda_harian_diharapkan, (
#         "Denda cicilan terakhir tidak sesuai"
#     )
#
#     total_bayar = pinjaman.cicilan_tetap + denda
#
#     # Simpan state sebelum pembayaran terakhir.
#     saldo_sebelum = rekening.saldo
#     riwayat_sebelum = len(rekening.riwayat)
#
#     # Bayar cicilan terakhir beserta dendanya.
#     PinjamanService.bayar_cicilan(
#         bank,
#         pinjaman,
#         hari_uji
#     )
#
#     # Pastikan saldo dipotong sebesar cicilan dan denda.
#     assert math.isclose(
#         rekening.saldo,
#         saldo_sebelum - total_bayar,
#         rel_tol=1e-9
#     ), "Pemotongan saldo pelunasan tidak sesuai"
#
#     # Pastikan seluruh pokok telah dibayar.
#     assert math.isclose(
#         pinjaman.sisa_pokok,
#         0,
#         abs_tol=1e-6
#     ), "Sisa pokok seharusnya nol"
#
#     # Pastikan lifecycle pinjaman telah selesai.
#     assert (
#         pinjaman.status == StatusPinjaman.LUNAS
#     ), "Status pinjaman seharusnya LUNAS"
#
#     # Pastikan seluruh cicilan telah dibayar.
#     assert (
#         pinjaman.cicilan_terbayar
#         == pinjaman.tenor
#     ), "Jumlah cicilan terbayar seharusnya sama dengan tenor"
#
#     # Pastikan riwayat pelunasan ditambahkan.
#     assert (
#         len(rekening.riwayat)
#         == riwayat_sebelum + 1
#     ), "Riwayat pelunasan belum ditambahkan"
#
#     riwayat_terakhir = str(rekening.riwayat[-1])
#
#     assert "PELUNASAN" in riwayat_terakhir.upper(), (
#         "Riwayat terakhir belum mencatat pelunasan"
#     )
#
#     assert "DENDA" in riwayat_terakhir.upper(), (
#         "Riwayat pelunasan belum mencatat denda"
#     )
#
#     # Pastikan referensi pinjaman aktif dibersihkan.
#     assert nasabah.pinjaman is None, (
#         "Referensi pinjaman aktif belum dibersihkan"
#     )
#
#     # Pastikan notifikasi pelunasan tersedia.
#     notifikasi_pelunasan = [
#         notifikasi
#         for notifikasi in nasabah.notifikasi
#         if (
#             notifikasi.referensi_id
#             == JenisReferensiID.PINJAMAN
#             and "lunas" in notifikasi.pesan.lower()
#         )
#     ]
#
#     assert notifikasi_pelunasan, (
#         "Notifikasi pelunasan belum dibuat"
#     )
#
#     print()
#     print("=" * 60)
#     print("✅ Pelunasan dengan denda berhasil")
#     print(f"Jatuh tempo terakhir : {jatuh_tempo_terakhir}")
#     print(f"Tanggal pembayaran   : {hari_uji}")
#     print(f"Hari terlambat       : {hari_terlambat}")
#     print(
#         "Cicilan terakhir    : "
#         f"Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}"
#     )
#     print(
#         "Denda               : "
#         f"Rp{Utilitas.format_rupiah(denda)}"
#     )
#     print(
#         "Total pembayaran    : "
#         f"Rp{Utilitas.format_rupiah(round(total_bayar))}"
#     )
#     print(f"Status               : {pinjaman.status.value}")
#     print(
#         "Cicilan terbayar     : "
#         f"{pinjaman.cicilan_terbayar}/{pinjaman.tenor}"
#     )
#     print("=" * 60)

# ---------------------------------------------------------------------------------------------------------------------

# def uji_mengejar_tiga_cicilan_tertunggak():
#     """
#     Menguji pembayaran tiga cicilan tertunggak pada tanggal
#     # yang sama.
#     #
    # Pengujian memastikan:
    # - Setiap pembayaran menyelesaikan satu cicilan.
    # - Denda dihitung ulang berdasarkan jatuh tempo aktif.
    # - Jatuh tempo maju satu bulan per pembayaran.
    # - Denda tidak mengurangi sisa pokok.
    # - Setelah tiga pembayaran, pinjaman kembali mengikuti jadwal.
    # """
    #
    # # Muat data baru agar pengujian tidak menggunakan
    # # perubahan dari pengujian sebelumnya.
    # bank = JsonStorage.muat_bank()
    #
    # # Cari pinjaman aktif yang masih memiliki sedikitnya
    # # tiga cicilan tersisa.
    # pinjaman = next(
    #     (
    #         item
    #         for item in bank.daftar_pinjaman
    #         if (
    #             item.status == StatusPinjaman.AKTIF
    #             and (
    #                 item.tenor - item.cicilan_terbayar
    #                 >= 3
    #             )
    #         )
    #     ),
    #     None
    # )
    #
    # if pinjaman is None:
    #     print(
    #         "Tidak ada pinjaman aktif dengan "
    #         "minimal tiga cicilan tersisa."
    #     )
    #     return
    #
    # rekening = pinjaman.rekening
    # jatuh_tempo_awal = pinjaman.tanggal_jatuh_tempo
    #
    # # Tentukan jatuh tempo periode ketiga.
    # jatuh_tempo_periode_ketiga = (
    #     Utilitas.tambah_bulan(
    #         Utilitas.tambah_bulan(
    #             jatuh_tempo_awal,
    #             1
    #         ),
    #         1
    #     )
    # )
    #
    # # Pembayaran dilakukan tiga hari setelah jatuh tempo
    # # periode ketiga.
    # hari_uji = (
    #     jatuh_tempo_periode_ketiga
    #     + datetime.timedelta(days=3)
    # )
    #
    # # Siapkan saldo yang cukup untuk tiga cicilan beserta
    # # kemungkinan denda maksimal.
    # maksimal_denda_per_cicilan = (
    #     pinjaman.cicilan_tetap
    #     * PinjamanService.MAKSIMAL_PERSENTASE_DENDA
    # )
    #
    # saldo_dibutuhkan = (
    #     rekening.saldosetor_min
    #     + (
    #         pinjaman.cicilan_tetap
    #         + maksimal_denda_per_cicilan
    #     ) * 3
    # )
    #
    # if rekening.saldo < saldo_dibutuhkan:
    #     rekening.tambah_saldo(
    #         saldo_dibutuhkan - rekening.saldo
    #     )
    #
    # # Jalankan scheduler untuk menghasilkan kondisi tunggakan
    # # pada tanggal pengujian.
    # Scheduler.jalankan(bank, hari_uji)
    #
    # saldo_awal = rekening.saldo
    # cicilan_terbayar_awal = pinjaman.cicilan_terbayar
    # total_seluruh_pembayaran = 0
    #
    # print()
    # print("=" * 60)
    # print("PENGUJIAN PEMBAYARAN CICILAN TERTUNGGAK")
    # print(f"Jatuh tempo awal : {jatuh_tempo_awal}")
    # print(f"Tanggal pembayaran: {hari_uji}")
    # print("=" * 60)
    #
    # # Bayar tiga cicilan secara berurutan pada tanggal yang sama.
    # for urutan in range(1, 4):
    #     jatuh_tempo_sebelum = pinjaman.tanggal_jatuh_tempo
    #     saldo_sebelum = rekening.saldo
    #     sisa_pokok_sebelum = pinjaman.sisa_pokok
    #     cicilan_sebelum = pinjaman.cicilan_terbayar
    #
    #     # Hitung kondisi cicilan yang sedang dibayar.
    #     hari_terlambat = (
    #         PinjamanService.hitung_hari_terlambat(
    #             pinjaman,
    #             hari_uji
    #         )
    #     )
    #
    #     denda = PinjamanService.hitung_denda(
    #         pinjaman,
    #         hari_uji
    #     )
    #
    #     total_bayar = pinjaman.cicilan_tetap + denda
    #
    #     # Hitung perubahan pokok yang diharapkan.
    #     persentase_bunga = pinjaman.bunga / 12
    #
    #     bunga_bulanan = (
    #         sisa_pokok_sebelum
    #         * persentase_bunga
    #     )
    #
    #     pokok_dibayar = (
    #         pinjaman.cicilan_tetap
    #         - bunga_bulanan
    #     )
    #
    #     sisa_pokok_diharapkan = max(
    #         0,
    #         sisa_pokok_sebelum - pokok_dibayar
    #     )
    #
    #     # Proses satu pembayaran cicilan.
    #     PinjamanService.bayar_cicilan(
    #         bank,
    #         pinjaman,
    #         hari_uji
    #     )
    #
    #     total_seluruh_pembayaran += total_bayar
    #
    #     # Pastikan saldo dipotong sebesar cicilan dan denda.
    #     assert math.isclose(
    #         rekening.saldo,
    #         saldo_sebelum - total_bayar,
    #         rel_tol=1e-9
    #     ), (
    #         f"Pemotongan saldo pembayaran ke-{urutan} "
    #         "tidak sesuai"
    #     )
    #
    #     # Pastikan denda tidak mengurangi sisa pokok.
    #     assert math.isclose(
    #         pinjaman.sisa_pokok,
    #         sisa_pokok_diharapkan,
    #         rel_tol=1e-9
    #     ), (
    #         f"Perubahan pokok pembayaran ke-{urutan} "
    #         "tidak sesuai"
    #     )
    #
    #     # Pastikan jumlah cicilan terbayar bertambah satu.
    #     assert (
    #         pinjaman.cicilan_terbayar
    #         == cicilan_sebelum + 1
    #     ), (
    #         f"Cicilan terbayar pada pembayaran "
    #         f"ke-{urutan} tidak bertambah"
    #     )
    #
    #     # Pastikan jatuh tempo maju dari jadwal sebelumnya.
    #     if pinjaman.status == StatusPinjaman.AKTIF:
    #         jatuh_tempo_diharapkan = (
    #             Utilitas.tambah_bulan(
    #                 jatuh_tempo_sebelum,
    #                 1
    #             )
    #         )
    #
    #         assert (
    #             pinjaman.tanggal_jatuh_tempo
    #             == jatuh_tempo_diharapkan
    #         ), (
    #             f"Jatuh tempo setelah pembayaran "
    #             f"ke-{urutan} tidak sesuai"
    #         )
    #
    #     print()
    #     print(f"Pembayaran ke-{urutan}")
    #     print(f"  Cicilan untuk jatuh tempo : {jatuh_tempo_sebelum}")
    #     print(f"  Hari terlambat            : {hari_terlambat}")
    #     print(
    #         "  Denda                     : "
    #         f"Rp{Utilitas.format_rupiah(denda)}"
    #     )
    #     print(
    #         "  Total pembayaran          : "
    #         f"Rp{Utilitas.format_rupiah(round(total_bayar))}"
    #     )
    #     print(
    #         "  Jatuh tempo berikutnya    : "
    #         f"{pinjaman.tanggal_jatuh_tempo}"
    #     )
    #
    # # Pastikan tiga pembayaran telah tercatat.
    # assert (
    #     pinjaman.cicilan_terbayar
    #     == cicilan_terbayar_awal + 3
    # ), "Jumlah seluruh cicilan terbayar tidak sesuai"
    #
    # # Pastikan jumlah seluruh potongan saldo sesuai.
    # assert math.isclose(
    #     rekening.saldo,
    #     saldo_awal - total_seluruh_pembayaran,
    #     rel_tol=1e-9
    # ), "Total pemotongan saldo tidak sesuai"
    #
    # # Setelah tiga pembayaran, jatuh tempo harus berada
    # # satu periode setelah tanggal pengujian.
    # jatuh_tempo_akhir_diharapkan = (
    #     Utilitas.tambah_bulan(
    #         jatuh_tempo_periode_ketiga,
    #         1
    #     )
    # )
    #
    # assert (
    #     pinjaman.tanggal_jatuh_tempo
    #     == jatuh_tempo_akhir_diharapkan
    # ), "Pinjaman belum kembali ke jadwal yang benar"
    #
    # # Pastikan cicilan berikutnya tidak lagi terlambat.
    # hari_terlambat_akhir = (
    #     PinjamanService.hitung_hari_terlambat(
    #         pinjaman,
    #         hari_uji
    #     )
    # )
    #
    # assert hari_terlambat_akhir == 0, (
    #     "Pinjaman seharusnya sudah kembali mengikuti jadwal"
    # )
    #
    # print()
    # print("=" * 60)
    # print("✅ Tiga cicilan tertunggak berhasil dikejar")
    # print(
    #     "Total pembayaran: "
    #     f"Rp{Utilitas.format_rupiah(round(total_seluruh_pembayaran))}"
    # )
    # print(
    #     "Jatuh tempo akhir: "
    #     f"{pinjaman.tanggal_jatuh_tempo}"
    # )
    # print("=" * 60)
# ------------------------------------------------------------------------------------------------------------------------



# def uji_pembayaran_denda_saldo_tidak_cukup():
#     """
#     Memastikan kegagalan pembayaran tidak mengubah state
#     rekening maupun pinjaman.
#     """
#
#     bank = JsonStorage.muat_bank()
#
#     pinjaman = next(
#         (
#             item
#             for item in bank.daftar_pinjaman
#             if item.status == StatusPinjaman.AKTIF
#         ),
#         None
#     )
#
#     if pinjaman is None:
#         print("Tidak ada pinjaman aktif untuk diuji.")
#         return
#
#     rekening = pinjaman.rekening
#
#     hari_uji = (
#         pinjaman.tanggal_jatuh_tempo
#         + datetime.timedelta(
#             days=(
#                 PinjamanService.BATAS_HARI_TUNGGAKAN
#                 + 1
#             )
#         )
#     )
#
#     # Buat saldo tidak cukup untuk membayar cicilan dan denda.
#     rekening.set_saldo(rekening.saldosetor_min)
#
#     # Simpan state sebelum percobaan pembayaran.
#     saldo_sebelum = rekening.saldo
#     sisa_pokok_sebelum = pinjaman.sisa_pokok
#     cicilan_terbayar_sebelum = pinjaman.cicilan_terbayar
#     jatuh_tempo_sebelum = pinjaman.tanggal_jatuh_tempo
#
#     try:
#         PinjamanService.bayar_cicilan(
#             bank,
#             pinjaman,
#             hari_uji
#         )
#
#         assert False, (
#             "Pembayaran seharusnya ditolak karena saldo tidak cukup"
#         )
#
#     except ValueError as error:
#         print("Pembayaran ditolak:", error)
#
#     # Pastikan seluruh state keuangan tetap sama.
#     assert rekening.saldo == saldo_sebelum
#     assert pinjaman.sisa_pokok == sisa_pokok_sebelum
#     assert (
#         pinjaman.cicilan_terbayar
#         == cicilan_terbayar_sebelum
#     )
#     assert (
#         pinjaman.tanggal_jatuh_tempo
#         == jatuh_tempo_sebelum
#     )
#
#     print("✅ Kegagalan pembayaran tidak mengubah state")
# -----------------------------------------------------------------------------------------------------------------------

# def uji_pembayaran_dengan_denda():
#     """
#     Menguji pembayaran cicilan pada hari pertama denda.
#
#     Pengujian memastikan:
#     - Denda ikut dipotong dari saldo.
#     - Denda tidak mengurangi sisa pokok.
#     - Cicilan terbayar bertambah.
#     - Jatuh tempo maju dari tanggal sebelumnya.
#     - Notifikasi tunggakan dihapus.
#     """
#
#     # Muat data baru agar pengujian tidak dipengaruhi
#     # oleh skenario sebelumnya.
#     bank = JsonStorage.muat_bank()
#
#     # Ambil satu pinjaman yang masih aktif.
#     pinjaman = next(
#         (
#             item
#             for item in bank.daftar_pinjaman
#             if item.status == StatusPinjaman.AKTIF
#         ),
#         None
#     )
#
#     if pinjaman is None:
#         print("Tidak ada pinjaman aktif untuk diuji.")
#         return
#
#     rekening = pinjaman.rekening
#     jatuh_tempo_lama = pinjaman.tanggal_jatuh_tempo
#
#     # Gunakan H+8 sebagai hari pertama pengenaan denda.
#     hari_uji = (
#         jatuh_tempo_lama
#         + datetime.timedelta(
#             days=(
#                 PinjamanService.BATAS_HARI_TUNGGAKAN
#                 + 1
#             )
#         )
#     )
#
#     # Jalankan scheduler untuk membuat notifikasi tunggakan.
#     Scheduler.jalankan(bank, hari_uji)
#
#     # Hitung denda dan total pembayaran yang diharapkan.
#     denda = PinjamanService.hitung_denda(
#         pinjaman,
#         hari_uji
#     )
#
#     total_bayar = pinjaman.cicilan_tetap + denda
#
#     # Pastikan saldo pengujian mencukupi.
#     saldo_minimal_dibutuhkan = (
#         total_bayar
#         + rekening.saldosetor_min
#     )
#
#     if rekening.saldo < saldo_minimal_dibutuhkan:
#         tambahan_saldo = (
#             saldo_minimal_dibutuhkan
#             - rekening.saldo
#         )
#
#         rekening.tambah_saldo(tambahan_saldo)
#
#     # Simpan state sebelum pembayaran.
#     saldo_sebelum = rekening.saldo
#     sisa_pokok_sebelum = pinjaman.sisa_pokok
#     cicilan_terbayar_sebelum = pinjaman.cicilan_terbayar
#
#     # Hitung perubahan pokok yang diharapkan.
#     persentase_bunga = pinjaman.bunga / 12
#
#     bunga_bulanan = (
#         sisa_pokok_sebelum
#         * persentase_bunga
#     )
#
#     pokok_dibayar = (
#         pinjaman.cicilan_tetap
#         - bunga_bulanan
#     )
#
#     sisa_pokok_diharapkan = max(
#         0,
#         sisa_pokok_sebelum - pokok_dibayar
#     )
#
#     # Proses pembayaran pada tanggal simulasi.
#     PinjamanService.bayar_cicilan(
#         bank,
#         pinjaman,
#         hari_uji
#     )
#
#     # Pastikan saldo dipotong sebesar cicilan dan denda.
#     saldo_diharapkan = saldo_sebelum - total_bayar
#
#     assert math.isclose(
#         rekening.saldo,
#         saldo_diharapkan,
#         rel_tol=1e-9
#     ), "Pemotongan saldo tidak sesuai"
#
#     # Pastikan denda tidak mengurangi pokok pinjaman.
#     assert math.isclose(
#         pinjaman.sisa_pokok,
#         sisa_pokok_diharapkan,
#         rel_tol=1e-9
#     ), "Perubahan sisa pokok tidak sesuai"
#
#     # Pastikan jumlah cicilan terbayar bertambah satu.
#     assert (
#         pinjaman.cicilan_terbayar
#         == cicilan_terbayar_sebelum + 1
#     ), "Jumlah cicilan terbayar tidak bertambah"
#
#     # Periksa jatuh tempo jika pinjaman belum lunas.
#     if pinjaman.status == StatusPinjaman.AKTIF:
#         jatuh_tempo_diharapkan = Utilitas.tambah_bulan(
#             jatuh_tempo_lama,
#             1
#         )
#
#         assert (
#             pinjaman.tanggal_jatuh_tempo
#             == jatuh_tempo_diharapkan
#         ), "Jatuh tempo berikutnya tidak sesuai"
#
#     # Pastikan notifikasi tunggakan sudah dihapus.
#     notifikasi_tunggakan = [
#         notifikasi
#         for notifikasi in pinjaman.pemilik.notifikasi
#         if (
#             notifikasi.referensi_id
#             == JenisReferensiID.PINJAMAN
#             and notifikasi.id_objek == pinjaman.ID
#             and "terlambat" in notifikasi.pesan.lower()
#         )
#     ]
#
#     assert not notifikasi_tunggakan, (
#         "Notifikasi tunggakan belum dihapus"
#     )
#
#     print()
#     print("✅ Pembayaran dengan denda berhasil")
#     print(
#         "Saldo dipotong      : "
#         f"Rp{Utilitas.format_rupiah(round(total_bayar))}"
#     )
#     print(
#         "Cicilan            : "
#         f"Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))}"
#     )
#     print(
#         "Denda              : "
#         f"Rp{Utilitas.format_rupiah(denda)}"
#     )
#     print(
#         "Sisa pokok         : "
#         f"Rp{Utilitas.format_rupiah(round(pinjaman.sisa_pokok))}"
#     )
#     print(
#         "Jatuh tempo berikut: "
#         f"{pinjaman.tanggal_jatuh_tempo}"
#     )

# ------------------------------------------------------------------------------------------------------------------------

# def uji_notifikasi_tunggakan():
#     """
#     Menguji notifikasi dan perhitungan denda pada beberapa
#     tanggal relatif terhadap jatuh tempo pinjaman.
#
#     Data dimuat ulang untuk setiap skenario agar perubahan
#     dari satu pengujian tidak memengaruhi pengujian berikutnya.
#     """
#
#     # Muat data awal untuk mendapatkan tanggal jatuh tempo.
#     bank_awal = JsonStorage.muat_bank()
#
#     pinjaman_awal = next(
#         (
#             pinjaman
#             for pinjaman in bank_awal.daftar_pinjaman
#             if pinjaman.status == StatusPinjaman.AKTIF
#         ),
#         None
#     )
#
#     if pinjaman_awal is None:
#         print("Tidak ada pinjaman aktif untuk diuji.")
#         return
#
#     jatuh_tempo = pinjaman_awal.tanggal_jatuh_tempo
#     batas = PinjamanService.BATAS_HARI_TUNGGAKAN
#
#     # Tentukan tanggal-tanggal penting dalam lifecycle tunggakan.
#     skenario = [
#         (
#             "Sehari sebelum jatuh tempo",
#             jatuh_tempo - datetime.timedelta(days=1)
#         ),
#         (
#             "Tepat pada jatuh tempo",
#             jatuh_tempo
#         ),
#         (
#             "Hari pertama tunggakan",
#             jatuh_tempo + datetime.timedelta(days=1)
#         ),
#         (
#             "Hari terakhir masa toleransi",
#             jatuh_tempo + datetime.timedelta(days=batas)
#         ),
#         (
#             "Hari pertama denda",
#             jatuh_tempo + datetime.timedelta(days=batas + 1)
#         ),
#         (
#             "Tiga hari terkena denda",
#             jatuh_tempo + datetime.timedelta(days=batas + 3)
#         )
#     ]
#
#     for nama_skenario, hari_uji in skenario:
#         # Muat ulang data agar setiap skenario dimulai
#         # dari state yang sama.
#         bank = JsonStorage.muat_bank()
#
#         pinjaman = next(
#             (
#                 item
#                 for item in bank.daftar_pinjaman
#                 if item.status == StatusPinjaman.AKTIF
#             ),
#             None
#         )
#
#         if pinjaman is None:
#             print("Pinjaman aktif tidak ditemukan.")
#             return
#
#         # Jalankan seluruh proses scheduler pada tanggal simulasi.
#         Scheduler.jalankan(bank, hari_uji)
#
#         # Hitung hasil yang perlu diverifikasi.
#         hari_terlambat = (
#             PinjamanService.hitung_hari_terlambat(
#                 pinjaman,
#                 hari_uji
#             )
#         )
#
#         denda = PinjamanService.hitung_denda(
#             pinjaman,
#             hari_uji
#         )
#
#         # Cari notifikasi pinjaman yang dihasilkan scheduler.
#         notifikasi_pinjaman = [
#             notifikasi
#             for notifikasi in pinjaman.pemilik.notifikasi
#             if (
#                 notifikasi.referensi_id
#                 == JenisReferensiID.PINJAMAN
#             )
#         ]
#
#         print()
#         print("=" * 60)
#         print(f"Skenario        : {nama_skenario}")
#         print(f"Jatuh tempo     : {jatuh_tempo}")
#         print(f"Tanggal simulasi: {hari_uji}")
#         print(f"Hari terlambat  : {hari_terlambat}")
#         print(
#             "Denda            : "
#             f"Rp{Utilitas.format_rupiah(denda)}"
#         )
#
#         if notifikasi_pinjaman:
#             print(
#                 "Notifikasi       : "
#                 f"{notifikasi_pinjaman[-1].pesan}"
#             )
#         else:
#             print("Notifikasi       : Tidak ada")




# ----------------------------------------------------------------------------------------------------------------
from bank_djago.utils.utililty import JenisReferensiID

class BankService:

    @staticmethod
    def cek_integritas_rekening(bank):
        error = []

        # 1. Setiap rekening harus punya pemilik
        for norek, rekening in bank.rekening_index.items():
            if rekening.pemilik is None:
                error.append(
                    f"Rekening {norek} tidak memiliki pemilik."
                )

        # 2. Setiap rekening milik nasabah harus ada di rekening_index
        # 3. Setiap rekening hanya boleh dimiliki satu nasabah
        pemilik_rekening = {}

        for nik, nasabah in bank.data_nasabah.items():
            for rekening in nasabah.rekening:
                norek = rekening.norek

                if norek not in bank.rekening_index:
                    error.append(
                        f"Rekening {norek} milik nasabah {nik} "
                        f"tidak ditemukan di rekening_index."
                    )

                if norek in pemilik_rekening:
                    error.append(
                        f"Rekening {norek} dimiliki lebih dari satu nasabah: "
                        f"{pemilik_rekening[norek]} dan {nik}."
                    )
                else:
                    pemilik_rekening[norek] = nik

                # 4. Pemilik pada objek rekening harus sesuai
                if rekening.pemilik is not nasabah:
                    pemilik = (
                        rekening.pemilik.NIK
                        if rekening.pemilik is not None
                        else "None"
                    )

                    error.append(
                        f"Rekening {norek}: "
                        f"pemilik pada objek = {pemilik}, "
                        f"tetapi tercantum pada nasabah = {nik}."
                    )

        return error

    @staticmethod
    def cek_integritas_deposito(bank):
        error = []

        for nik, nasabah in bank.data_nasabah.items():

            id_deposito = set()

            for deposito in nasabah.deposito:

                # 1. Deposito harus punya pemilik
                if deposito.pemilik is None:
                    error.append(
                        f"Deposito {deposito.ID} tidak memiliki pemilik."
                    )

                # 2. Pemilik harus sesuai dengan nasabah
                elif deposito.pemilik is not nasabah:
                    error.append(
                        f"Deposito {deposito.ID} milik {nik} "
                        f"tetapi deposito.pemilik menunjuk ke "
                        f"{deposito.pemilik.NIK}."
                    )

                # 3. ID harus unik dalam satu nasabah
                if deposito.ID in id_deposito:
                    error.append(
                        f"Nasabah {nik} memiliki ID deposito "
                        f"duplikat: {deposito.ID}."
                    )
                else:
                    id_deposito.add(deposito.ID)

                # 4. Rekening harus ada
                if deposito.rekening is None:
                    error.append(
                        f"Deposito {deposito.ID} tidak memiliki rekening."
                    )
                else:
                    if deposito.rekening.norek not in bank.rekening_index:
                        error.append(
                            f"Deposito {deposito.ID} menggunakan rekening "
                            f"{deposito.rekening.norek} yang tidak ditemukan."
                        )

                    # 5. Rekening harus punya pemilik yang benar
                    if deposito.rekening.pemilik is not nasabah:
                        pemilik = (
                            deposito.rekening.pemilik.NIK
                            if deposito.rekening.pemilik
                            else "None"
                        )

                        error.append(
                            f"Deposito {deposito.ID} milik {nik} "
                            f"menggunakan rekening {deposito.rekening.norek} "
                            f"yang pemiliknya adalah {pemilik}."
                        )

        return error

    @staticmethod
    def cek_integritas_pinjaman(bank):
        error = []
        pemilik_pinjaman = {}

        for pinjaman in bank.daftar_pinjaman:

            # 1. Pemilik harus ada
            if pinjaman.pemilik is None:
                error.append(
                    f"Pinjaman {pinjaman.ID} tidak memiliki pemilik."
                )
                continue

            nasabah = pinjaman.pemilik
            nik = nasabah.NIK

            # 2. NIK pemilik harus terdaftar di bank
            if nik not in bank.data_nasabah:
                error.append(
                    f"Pinjaman {pinjaman.ID} memiliki pemilik "
                    f"dengan NIK {nik} yang tidak terdaftar."
                )

            # 3. Pemilik pinjaman harus menunjuk ke nasabah yang benar
            if bank.data_nasabah.get(nik) is not nasabah:
                error.append(
                    f"Pinjaman {pinjaman.ID} menunjuk ke objek "
                    f"nasabah yang tidak sesuai dengan NIK {nik}."
                )

            # 4. Satu nasabah hanya punya satu pinjaman
            if nik in pemilik_pinjaman:
                error.append(
                    f"Nasabah {nik} memiliki lebih dari satu pinjaman: "
                    f"{pemilik_pinjaman[nik]} dan {pinjaman.ID}."
                )
            else:
                pemilik_pinjaman[nik] = pinjaman.ID

            # 5. Rekening harus ada
            if pinjaman.rekening is None:
                error.append(
                    f"Pinjaman {pinjaman.ID} tidak memiliki rekening."
                )
                continue

            norek = pinjaman.rekening.norek

            # 6. Rekening harus ada di index
            if norek not in bank.rekening_index:
                error.append(
                    f"Pinjaman {pinjaman.ID} menggunakan rekening "
                    f"{norek} yang tidak ditemukan."
                )

            # 7. Rekening harus dimiliki nasabah yang sama
            if pinjaman.rekening.pemilik is not nasabah:
                pemilik_rekening = (
                    pinjaman.rekening.pemilik.NIK
                    if pinjaman.rekening.pemilik is not None
                    else "None"
                )

                error.append(
                    f"Pinjaman {pinjaman.ID} milik nasabah {nik} "
                    f"menggunakan rekening {norek} yang dimiliki "
                    f"oleh {pemilik_rekening}."
                )

        return error

    @staticmethod
    def cek_integritas_notifikasi(bank):
        error = []

        for nik, nasabah in bank.data_nasabah.items():

            for notifikasi in nasabah.notifikasi:

                referensi = notifikasi.referensi_id
                id_objek = notifikasi.id_objek

                # Notifikasi umum tidak wajib memiliki objek
                if referensi is None:
                    if id_objek is not None:
                        error.append(
                            f"Notifikasi umum milik nasabah {nik} "
                            f"memiliki id_objek={id_objek}."
                        )
                    continue

                # =========================
                # NOTIFIKASI DEPOSITO
                # =========================
                if referensi == JenisReferensiID.DEPOSITO:

                    if id_objek is None:
                        error.append(
                            f"Notifikasi deposito milik nasabah {nik} "
                            f"tidak memiliki id_objek."
                        )
                        continue

                    deposito_ditemukan = any(
                        deposito.ID == id_objek
                        for deposito in nasabah.deposito
                    )

                    if not deposito_ditemukan:
                        error.append(
                            f"Notifikasi deposito milik nasabah {nik} "
                            f"menunjuk ke deposito ID {id_objek} "
                            f"yang tidak ditemukan pada nasabah tersebut."
                        )

                # =========================
                # NOTIFIKASI PINJAMAN
                # =========================
                elif referensi == JenisReferensiID.PINJAMAN:

                    if id_objek is None:
                        continue

                    pinjaman_ditemukan = any(
                        pinjaman.ID == id_objek
                        and pinjaman.pemilik is nasabah
                        for pinjaman in bank.daftar_pinjaman
                    )

                    if not pinjaman_ditemukan:
                        error.append(
                            f"Notifikasi pinjaman milik nasabah {nik} "
                            f"menunjuk ke pinjaman ID {id_objek} "
                            f"yang tidak ditemukan atau bukan milik nasabah tersebut."
                        )

                # =========================
                # REFERENSI YANG BELUM DIKENAL
                # =========================
                else:
                    error.append(
                        f"Notifikasi milik nasabah {nik} "
                        f"memiliki referensi tidak dikenal: {referensi}."
                    )

        return error

# ----------------------------------------------------------------------------------------------------------------------

# def uji_relasi_downgrade_rekening(bank):
#     # Mengambil satu-satunya nasabah dalam dataset.
#     nasabah = next(iter(bank.data_nasabah.values()))
#
#     # Mencari rekening Platinum milik nasabah.
#     rekening_platinum = next(
#         (
#             rekening
#             for rekening in nasabah.rekening
#             if rekening.level == 3
#         ),
#         None
#     )
#
#     if rekening_platinum is None:
#         raise ValueError(
#             "Nasabah tidak memiliki rekening gold untuk diuji"
#         )
#
#     # Menyimpan objek deposito yang menggunakan rekening Platinum.
#     deposito_terkait = [
#         deposito
#         for deposito in nasabah.deposito
#         if deposito.rekening is rekening_platinum
#     ]
#
#     # Menyimpan objek pinjaman yang menggunakan rekening Platinum.
#     pinjaman_terkait = [
#         pinjaman
#         for pinjaman in bank.daftar_pinjaman
#         if pinjaman.rekening is rekening_platinum
#     ]
#
#     print("Sebelum downgrade:")
#     print("Nasabah          :", nasabah.nama)
#     print("Nomor rekening   :", rekening_platinum.norek)
#     print("Objek rekening   :", id(rekening_platinum))
#     print("Level rekening   :", rekening_platinum.level)
#     print("Jenis rekening   :", RekeningService.level[rekening_platinum.level])
#     print("Jumlah deposito  :", len(deposito_terkait))
#     print("Jumlah pinjaman  :", len(pinjaman_terkait))
#
#     # Melakukan downgrade dari Platinum ke Gold.
#     rekening_gold = RekeningService.downgrade_rekening(
#         bank,
#         rekening_platinum,
#         target_level=2
#     )
#
#     # Memastikan downgrade menghasilkan objek rekening baru.
#     assert rekening_gold is not rekening_platinum, (
#         "Downgrade tidak menghasilkan objek rekening baru"
#     )
#
#     assert rekening_gold.level == 2, (
#         "Rekening hasil downgrade seharusnya Gold"
#     )
#
#     # Nomor rekening harus tetap sama.
#     assert rekening_gold.norek == rekening_platinum.norek, (
#         "Nomor rekening berubah setelah downgrade"
#     )
#
#     # Bank harus menunjuk objek Gold.
#     assert bank.rekening_index[rekening_gold.norek] is rekening_gold, (
#         "Bank masih menunjuk rekening Platinum"
#     )
#
#     # Nasabah harus menyimpan objek Gold.
#     assert rekening_gold in nasabah.rekening, (
#         "Daftar rekening nasabah belum menyimpan rekening Gold"
#     )
#
#     assert rekening_platinum not in nasabah.rekening, (
#         "Rekening Platinum lama masih tersimpan pada nasabah"
#     )
#
#     # Semua deposito harus menunjuk rekening Gold.
#     for deposito in deposito_terkait:
#         assert deposito.rekening is rekening_gold, (
#             f"Deposito #{deposito.id} masih menunjuk rekening Platinum"
#         )
#
#     # Semua pinjaman harus menunjuk rekening Gold.
#     for pinjaman in pinjaman_terkait:
#         assert pinjaman.rekening is rekening_gold, (
#             f"Pinjaman #{pinjaman.ID} masih menunjuk rekening Platinum"
#         )
#
#     print()
#     print("Setelah downgrade:")
#     print("Nomor rekening   :", rekening_gold.norek)
#     print("Objek rekening   :", id(rekening_gold))
#     print("Level rekening   :", rekening_gold.level)
#     print("Jenis rekening   :", RekeningService.level[rekening_gold.level])
#     print("Deposito terhubung:", len(deposito_terkait))
#     print("Pinjaman terhubung:", len(pinjaman_terkait))
#     print("✅ Relasi downgrade rekening berhasil")

# - ----------------------------------------------------------------------------------------------------------------------

# def uji_relasi_upgrade_rekening(bank):
#     rekening_lama = None
#     nasabah = None
#
#     # Mencari rekening yang digunakan oleh deposito dan pinjaman sekaligus.
#     for kandidat in bank.rekening_index.values():
#         pemilik = kandidat.pemilik
#
#         deposito_terkait = [
#             deposito
#             for deposito in pemilik.deposito
#             if deposito.rekening is kandidat
#         ]
#
#         pinjaman_terkait = [
#             pinjaman
#             for pinjaman in bank.daftar_pinjaman
#             if pinjaman.rekening is kandidat
#         ]
#
#         if deposito_terkait and pinjaman_terkait:
#             rekening_lama = kandidat
#             nasabah = pemilik
#             break
#
#     if rekening_lama is None:
#         raise ValueError(
#             "Tidak ditemukan rekening yang terhubung dengan "
#             "deposito dan pinjaman sekaligus"
#         )
#
#     deposito_terkait = [
#         deposito
#         for deposito in nasabah.deposito
#         if deposito.rekening is rekening_lama
#     ]
#
#     pinjaman_terkait = [
#         pinjaman
#         for pinjaman in bank.daftar_pinjaman
#         if pinjaman.rekening is rekening_lama
#     ]
#
#     print("Sebelum upgrade:")
#     print("Nasabah          :", nasabah.nama)
#     print("Nomor rekening   :", rekening_lama.norek)
#     print("Objek rekening   :", id(rekening_lama))
#     print("Level rekening   :", rekening_lama.level)
#     print("Jumlah deposito  :", len(deposito_terkait))
#     print("Jumlah pinjaman  :", len(pinjaman_terkait))
#
#     # Menyiapkan rekening Gold agar memenuhi syarat upgrade ke Platinum.
#     rekening_lama.set_saldo(200_000_000)
#
#     rekening_baru = RekeningService.upgrade_rekening(
#         bank,
#         rekening_lama,
#         target_level=4
#     )
#
#     # Memastikan upgrade benar-benar menghasilkan objek baru.
#     assert rekening_baru is not rekening_lama, (
#         "Upgrade tidak menghasilkan objek rekening baru"
#     )
#
#     assert rekening_baru.level == 4, (
#         "Rekening hasil upgrade seharusnya Platinum"
#     )
#
#     assert rekening_baru.norek == rekening_lama.norek, (
#         "Nomor rekening berubah setelah upgrade"
#     )
#
#     # Memastikan Bank dan Nasabah menggunakan rekening baru.
#     assert bank.rekening_index[rekening_baru.norek] is rekening_baru, (
#         "Bank masih menunjuk rekening lama"
#     )
#
#     assert rekening_baru in nasabah.rekening, (
#         "Nasabah belum menyimpan rekening baru"
#     )
#
#     assert rekening_lama not in nasabah.rekening, (
#         "Rekening lama masih tersimpan pada nasabah"
#     )
#
#     # Memastikan semua deposito terkait berpindah ke rekening baru.
#     for deposito in deposito_terkait:
#         assert deposito.rekening is rekening_baru, (
#             f"Deposito #{deposito.id} masih menunjuk rekening lama"
#         )
#
#     # Memastikan semua pinjaman terkait berpindah ke rekening baru.
#     for pinjaman in pinjaman_terkait:
#         assert pinjaman.rekening is rekening_baru, (
#             f"Pinjaman #{pinjaman.ID} masih menunjuk rekening lama"
#         )
#
#     print()
#     print("Setelah upgrade:")
#     print("Objek rekening   :", id(rekening_baru))
#     print("Level rekening   :", rekening_baru.level)
#     print("Jenis rekening   :", RekeningService.level[rekening_baru.level])
#     print("Deposito terhubung:", len(deposito_terkait))
#     print("Pinjaman terhubung:", len(pinjaman_terkait))
#     print("✅ Relasi rekening, deposito, dan pinjaman berhasil")

# ----------------------------------------------------------------------------------------------------------------------

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
# ---------------------------------------------------------------------------------------------------------------------




bank = JsonStorage.muat_bank()
# def uji_integritas_upgrade_rekening(bank):
#     # Mengambil rekening awal yang akan diuji.
#     rekening_lama = next(iter(bank.rekening_index.values()))
#     nasabah = rekening_lama.pemilik
#
#     print("Sebelum upgrade:")
#     print("Objek rekening:", id(rekening_lama))
#     print("Level:", rekening_lama.level)
#
#     # Menambahkan saldo agar memenuhi persyaratan upgrade.
#     rekening_lama.set_saldo(200_000_000)
#
#     # Melakukan upgrade dan menerima objek rekening pengganti.
#     rekening_baru = RekeningService.upgrade_rekening(
#         bank,
#         rekening_lama,
#         target_level=4
#     )
#
#     print()
#     print("Setelah upgrade:")
#     print("Objek rekening:", id(rekening_baru))
#     print("Level:", rekening_baru.level)
#     print("Jenis:", RekeningService.level[rekening_baru.level])
#
#
#     # Memastikan bank menyimpan objek rekening baru.
#     assert rekening_baru is bank.rekening_index[rekening_baru.norek], (
#         "Bank masih menyimpan objek rekening lama"
#     )
#
#     assert rekening_baru is not rekening_lama, (
#         "Service tidak membuat objek rekening pengganti"
#     )
#
#     assert rekening_baru.level == 4, (
#         "Rekening baru seharusnya Platinum"
#     )
#
#     assert rekening_baru.norek == rekening_lama.norek, (
#         "Nomor rekening berubah setelah upgrade"
#     )
#     # Memastikan nasabah juga menyimpan objek rekening baru.
#     assert rekening_baru in nasabah.rekening, (
#         "Daftar rekening nasabah belum menyimpan rekening baru"
#     )
#
#     indeks = nasabah.rekening.index(rekening_baru)
#
#     assert rekening_baru is nasabah.rekening[indeks], (
#         "Referensi rekening milik nasabah tidak sama"
#     )
#
#     # Memastikan objek lama tidak lagi berada pada relasi utama.
#     assert rekening_lama is not bank.rekening_index[rekening_baru.norek], (
#         "Bank masih menunjuk objek rekening lama"
#     )
#
#     assert rekening_lama not in nasabah.rekening, (
#         "Objek rekening lama masih tersimpan pada nasabah"
#     )
#
#     print("✅ Integritas upgrade rekening berhasil")



# ---------------------------------------------------------------------------------------
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
#
#
# uji_save_load_dua_pinjaman(
#     bank,
#     nasabah_uji,
#     pinjaman_lunas,
#     pinjaman_aktif
# )


# ----------------------------------------------------------------------------------






# def siapkan_dua_pinjaman_untuk_uji(bank):
#     nik = input("Masukkan NIK nasabah yang akan diuji: ").strip()
#
#     nasabah = bank.cari_nasabah(nik)
#
#     if nasabah is None:
#         raise ValueError("NIK nasabah tidak ditemukan")
#
#     pinjaman_lama = nasabah.pinjaman
#
#     if pinjaman_lama is None:
#         raise ValueError(
#             "Nasabah tidak memiliki pinjaman berjalan"
#         )
#
#     if pinjaman_lama.status != StatusPinjaman.AKTIF:
#         raise ValueError(
#             "Pinjaman nasabah belum berstatus aktif"
#         )
#
#     rekening = pinjaman_lama.rekening
#
#     print()
#     print("DATA PINJAMAN LAMA")
#     print("Nasabah          :", nasabah.nama)
#     print("ID pinjaman      :", pinjaman_lama.ID)
#     print("Status           :", pinjaman_lama.status.value)
#     print("Tenor            :", pinjaman_lama.tenor)
#     print("Cicilan terbayar :", pinjaman_lama.cicilan_terbayar)
#     print(
#         "Cicilan tersisa  :",
#         pinjaman_lama.tenor
#         - pinjaman_lama.cicilan_terbayar
#     )
#     print()
#
#     cicilan_tersisa = (
#         pinjaman_lama.tenor
#         - pinjaman_lama.cicilan_terbayar
#     )
#
#     tanggal_pelunasan = None
#
#     # Melunasi seluruh cicilan yang masih tersisa.
#     for _ in range(cicilan_tersisa):
#         tanggal_bayar = pinjaman_lama.tanggal_jatuh_tempo
#         tanggal_pelunasan = tanggal_bayar
#
#         denda = PinjamanService.hitung_denda(
#             pinjaman_lama,
#             tanggal_bayar
#         )
#
#         total_bayar = (
#             pinjaman_lama.cicilan_tetap
#             + denda
#         )
#
#         saldo_minimum = (
#             total_bayar
#             + rekening.saldosetor_min
#         )
#
#         # Menambahkan saldo pengujian jika saldo tidak mencukupi.
#         if rekening.saldo < saldo_minimum:
#             kekurangan = saldo_minimum - rekening.saldo
#             rekening.tambah_saldo(kekurangan)
#
#         nomor_cicilan = (
#             pinjaman_lama.cicilan_terbayar
#             + 1
#         )
#
#         PinjamanService.bayar_cicilan(
#             bank,
#             pinjaman_lama,
#             hari_ini=tanggal_bayar
#         )
#
#         print(
#             f"Cicilan ke-{nomor_cicilan} dibayar "
#             f"pada {tanggal_bayar}"
#         )
#
#     assert pinjaman_lama.status == StatusPinjaman.LUNAS, (
#         "Pinjaman lama seharusnya sudah lunas"
#     )
#
#     assert pinjaman_lama.sisa_pokok == 0, (
#         "Sisa pokok pinjaman lama seharusnya nol"
#     )
#
#     assert nasabah.pinjaman is None, (
#         "Nasabah masih menunjuk pinjaman lama"
#     )
#
#     assert pinjaman_lama in bank.daftar_pinjaman, (
#         "Pinjaman lama hilang dari daftar pinjaman Bank"
#     )
#
#     print()
#     print("✅ Pinjaman lama berhasil dilunasi")
#     print("ID pinjaman :", pinjaman_lama.ID)
#     print("Status      :", pinjaman_lama.status.value)
#     print()
#
#     # Pinjaman baru dimulai sehari setelah pelunasan.
#     tanggal_pencairan_baru = (
#         tanggal_pelunasan
#         + datetime.timedelta(days=1)
#     )
#
#     pinjaman_baru = PinjamanService.ajukan_pinjaman(
#         bank=bank,
#         nasabah=nasabah,
#         rekening=rekening,
#         nominal=1_000_000,
#         tenor=6
#     )
#
#     PinjamanService.setujui_pinjaman(
#         bank,
#         pinjaman_baru
#     )
#
#     PinjamanService.cairkan_pinjaman(
#         bank,
#         pinjaman_baru,
#         hari_ini=tanggal_pencairan_baru
#     )
#
#     assert pinjaman_baru.status == StatusPinjaman.AKTIF, (
#         "Pinjaman baru seharusnya berstatus aktif"
#     )
#
#     assert nasabah.pinjaman is pinjaman_baru, (
#         "Nasabah tidak menunjuk pinjaman baru"
#     )
#
#     assert pinjaman_baru in bank.daftar_pinjaman, (
#         "Pinjaman baru belum masuk daftar pinjaman Bank"
#     )
#
#     assert pinjaman_baru is not pinjaman_lama, (
#         "Pinjaman baru dan lama merupakan objek yang sama"
#     )
#
#     assert pinjaman_baru.ID > pinjaman_lama.ID, (
#         "ID pinjaman baru tidak melanjutkan ID sebelumnya"
#     )
#
#     daftar_pinjaman_nasabah = [
#         pinjaman
#         for pinjaman in bank.daftar_pinjaman
#         if pinjaman.pemilik is nasabah
#     ]
#
#     assert len(daftar_pinjaman_nasabah) >= 2, (
#         "Bank belum menyimpan kedua pinjaman nasabah"
#     )
#
#     print("DATA PINJAMAN SETELAH PERSIAPAN")
#     print("Nasabah              :", nasabah.nama)
#     print("Pinjaman lama        :", pinjaman_lama.ID)
#     print("Status pinjaman lama :", pinjaman_lama.status.value)
#     print("Pinjaman baru        :", pinjaman_baru.ID)
#     print("Status pinjaman baru :", pinjaman_baru.status.value)
#     print(
#         "Jumlah pinjaman Bank :",
#         len(daftar_pinjaman_nasabah)
#     )
#     print(
#         "Pinjaman aktif       :",
#         nasabah.pinjaman.ID
#     )
#     print()
#     print("✅ Dataset dua pinjaman siap diuji")
#
#     return nasabah, pinjaman_lama, pinjaman_baru
#
# if __name__ = "__main__":
#     siapkan_dua_pinjaman_untuk_uji()
# nasabah_uji, pinjaman_lunas, pinjaman_aktif = (
#     siapkan_dua_pinjaman_untuk_uji(bank)
# )


# -------------------------------------------------------------------------


# def uji_save_load_notifikasi(bank):
#     nasabah = next(iter(bank.data_nasabah.values()))
#
#     if not nasabah.deposito:
#         raise ValueError(
#             "Nasabah tidak memiliki deposito untuk pengujian"
#         )
#
#     deposito = nasabah.deposito[0]
#     nik = nasabah.NIK
#
#     # Menyimpan daftar notifikasi asli.
#     notifikasi_asli = nasabah.notifikasi
#
#     # Menyimpan lokasi file JSON utama.
#     lokasi_asli = {
#         "rekening": JsonStorage.file_rek,
#         "nasabah": JsonStorage.file_nasabah,
#         "audit": JsonStorage.file_audit,
#         "deposito": JsonStorage.file_depo,
#         "pinjaman": JsonStorage.file_pinjaman
#     }
#
#     try:
#         notifikasi_deposito = Notifikasi(
#             jenis="deposito",
#             pesan="Uji save/load deposito",
#             referensi_id=JenisReferensiID.DEPOSITO,
#             id_objek=deposito.ID
#         )
#
#         notifikasi_pinjaman = Notifikasi(
#             jenis="pinjaman",
#             pesan="Uji save/load pinjaman",
#             referensi_id=JenisReferensiID.PINJAMAN
#         )
#
#         notifikasi_umum = Notifikasi(
#             jenis="rekening",
#             pesan="Uji save/load rekening"
#         )
#
#         # Menggunakan notifikasi sementara.
#         nasabah.notifikasi = [
#             notifikasi_deposito,
#             notifikasi_pinjaman,
#             notifikasi_umum
#         ]
#
#         print("Sebelum save/load:")
#
#         for notifikasi in nasabah.notifikasi:
#             print(
#                 "-",
#                 notifikasi.jenis,
#                 "| Referensi:",
#                 notifikasi.referensi_id,
#                 "| ID:",
#                 notifikasi.id_objek
#             )
#
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
#             # Menyimpan seluruh objek bank ke JSON sementara.
#             JsonStorage.simpan_bank(bank)
#
#             # Membuat Bank baru dari JSON sementara.
#             bank_hasil_load = JsonStorage.muat_bank()
#             nasabah_hasil_load = bank_hasil_load.data_nasabah[nik]
#
#             notifikasi_hasil = {
#                 notifikasi.pesan: notifikasi
#                 for notifikasi in nasabah_hasil_load.notifikasi
#             }
#
#             assert len(notifikasi_hasil) == 3, (
#                 "Jumlah notifikasi berubah setelah save/load"
#             )
#
#             deposito_hasil = notifikasi_hasil[
#                 "Uji save/load deposito"
#             ]
#
#             pinjaman_hasil = notifikasi_hasil[
#                 "Uji save/load pinjaman"
#             ]
#
#             umum_hasil = notifikasi_hasil[
#                 "Uji save/load rekening"
#             ]
#
#             # Memeriksa notifikasi deposito.
#             assert deposito_hasil.jenis == "deposito"
#             assert (
#                 deposito_hasil.referensi_id
#                 == JenisReferensiID.DEPOSITO
#             )
#             assert deposito_hasil.id_objek == deposito.ID
#
#             # Memeriksa notifikasi pinjaman.
#             assert pinjaman_hasil.jenis == "pinjaman"
#             assert (
#                 pinjaman_hasil.referensi_id
#                 == JenisReferensiID.PINJAMAN
#             )
#             assert pinjaman_hasil.id_objek is None
#
#             # Memeriksa notifikasi tanpa referensi.
#             assert umum_hasil.jenis == "rekening"
#             assert umum_hasil.referensi_id is None
#             assert umum_hasil.id_objek is None
#
#             print()
#             print("Setelah save/load:")
#
#             for notifikasi in nasabah_hasil_load.notifikasi:
#                 print(
#                     "-",
#                     notifikasi.jenis,
#                     "| Referensi:",
#                     notifikasi.referensi_id,
#                     "| ID:",
#                     notifikasi.id_objek
#                 )
#
#             print()
#             print("✅ Integritas save/load notifikasi berhasil")
#
#     finally:
#         # Mengembalikan notifikasi asli.
#         nasabah.notifikasi = notifikasi_asli
#
#         # Mengembalikan seluruh lokasi JSON utama.
#         JsonStorage.file_rek = lokasi_asli["rekening"]
#         JsonStorage.file_nasabah = lokasi_asli["nasabah"]
#         JsonStorage.file_audit = lokasi_asli["audit"]
#         JsonStorage.file_depo = lokasi_asli["deposito"]
#         JsonStorage.file_pinjaman = lokasi_asli["pinjaman"]
#
# if __name__ == "__main__":
#     uji_save_load_notifikasi(bank)

# ------------------------------------------------------------------------------



# def uji_isolasi_notifikasi(bank):
#     nasabah = next(iter(bank.data_nasabah.values()))
#
#     if not nasabah.deposito:
#         raise ValueError(
#             "Nasabah tidak memiliki deposito untuk pengujian"
#         )
#
#     deposito = nasabah.deposito[0]
#
#     # Menyimpan list notifikasi asli agar dapat dikembalikan.
#     notifikasi_asli = nasabah.notifikasi
#
#     try:
#         notifikasi_deposito_target = Notifikasi(
#             jenis="deposito",
#             pesan="Notifikasi deposito target",
#             referensi_id=JenisReferensiID.DEPOSITO,
#             id_objek=deposito.ID
#         )
#
#         notifikasi_deposito_lain = Notifikasi(
#             jenis="deposito",
#             pesan="Notifikasi deposito lain",
#             referensi_id=JenisReferensiID.DEPOSITO,
#             id_objek=deposito.ID + 999
#         )
#
#         notifikasi_pinjaman = Notifikasi(
#             jenis="pinjaman",
#             pesan="Notifikasi pinjaman",
#             referensi_id=JenisReferensiID.PINJAMAN
#         )
#
#         notifikasi_umum = Notifikasi(
#             jenis="rekening",
#             pesan="Notifikasi umum rekening"
#         )
#
#         # Menggunakan daftar sementara agar data asli tidak berubah.
#         nasabah.notifikasi = [
#             notifikasi_deposito_target,
#             notifikasi_deposito_lain,
#             notifikasi_pinjaman,
#             notifikasi_umum
#         ]
#
#         print("Sebelum penghapusan:")
#         for notifikasi in nasabah.notifikasi:
#             print(
#                 "-",
#                 notifikasi.jenis,
#                 "| ID:",
#                 notifikasi.id_objek,
#                 "|",
#                 notifikasi.pesan
#             )
#
#         # Menghapus notifikasi deposito target.
#         DepositoService.hapus_notifikasi_deposito(
#             nasabah,
#             deposito
#         )
#
#         assert notifikasi_deposito_target not in nasabah.notifikasi, (
#             "Notifikasi deposito target belum terhapus"
#         )
#
#         assert notifikasi_deposito_lain in nasabah.notifikasi, (
#             "Notifikasi deposito lain ikut terhapus"
#         )
#
#         assert notifikasi_pinjaman in nasabah.notifikasi, (
#             "Notifikasi pinjaman ikut terhapus oleh deposito"
#         )
#
#         assert notifikasi_umum in nasabah.notifikasi, (
#             "Notifikasi umum ikut terhapus oleh deposito"
#         )
#
#         print()
#         print("✅ Penghapusan notifikasi deposito terisolasi")
#
#         # Menghapus satu-satunya notifikasi pinjaman.
#         PinjamanService.hapus_notif_pinjaman(nasabah)
#
#         assert notifikasi_pinjaman not in nasabah.notifikasi, (
#             "Notifikasi pinjaman belum terhapus"
#         )
#
#         assert notifikasi_deposito_lain in nasabah.notifikasi, (
#             "Notifikasi deposito ikut terhapus oleh pinjaman"
#         )
#
#         assert notifikasi_umum in nasabah.notifikasi, (
#             "Notifikasi umum ikut terhapus oleh pinjaman"
#         )
#
#         print("✅ Penghapusan notifikasi pinjaman terisolasi")
#
#         assert len(nasabah.notifikasi) == 2, (
#             "Jumlah akhir notifikasi tidak sesuai"
#         )
#
#         print()
#         print("Notifikasi yang tersisa:")
#         for notifikasi in nasabah.notifikasi:
#             print(
#                 "-",
#                 notifikasi.jenis,
#                 "| ID:",
#                 notifikasi.id_objek,
#                 "|",
#                 notifikasi.pesan
#             )
#
#         print()
#         print("✅ Integritas isolasi notifikasi berhasil")
#
#     finally:
#         # Mengembalikan list notifikasi asli milik nasabah.
#         nasabah.notifikasi = notifikasi_asli