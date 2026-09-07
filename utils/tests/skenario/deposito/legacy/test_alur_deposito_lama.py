"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 2).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

print("-----------------------------------------------------------------------------------------")

# print("TES PENCAIRAN DEPOSITO")
#
#
#
# from bank_djago.penyimpanan.sqlite.database import (
#     buat_koneksi
# )
# from bank_djago.penyimpanan.loaders.nasabah_loader import (
#     NasabahLoader
# )
# from bank_djago.penyimpanan.repositories.deposito_repository import (
#     DepositoRepository
# )
# from bank_djago.penyimpanan.repositories.rekening_repository import (
#     RekeningRepository
# )
# from bank_djago.penyimpanan.repositories.riwayat_repository import (
#     RiwayatRepository
# )
# from bank_djago.penyimpanan.repositories.audit_repository import (
#     AuditRepository
# )
# from bank_djago.services.deposito.deposito_service import (
#     DepositoService,
#     StatusDeposito
# )
# from bank_djago.utils.utility import Utilitas
#
#
# NIK_PENGUJIAN = "1111222233334444"
# NOREK_PENGUJIAN = "2001569043650499"
# ID_DEPOSITO = 5
#
#
# # =========================================================
# # KONDISI SEBELUM PENCAIRAN
# # =========================================================
#
# rekening_sebelum = (
#     RekeningRepository.cari_rekening_dengan_norek(
#         NOREK_PENGUJIAN
#     )
# )
#
# deposito_sebelum = (
#     DepositoRepository.cari_deposito_dengan_id(
#         ID_DEPOSITO
#     )
# )
#
# riwayat_sebelum = (
#     RiwayatRepository.cari_seluruh_riwayat(
#         NOREK_PENGUJIAN
#     )
# )
#
# audit_sebelum = (
#     AuditRepository.cari_audit_dengan_norek(
#         NOREK_PENGUJIAN
#     )
# )
#
# assert rekening_sebelum is not None, (
#     "Rekening pengujian tidak ditemukan"
# )
#
# assert deposito_sebelum is not None, (
#     "Deposito pengujian tidak ditemukan"
# )
#
# if deposito_sebelum["status"] == StatusDeposito.DICAIRKAN:
#     raise ValueError(
#         "Deposito ID 5 sudah dicairkan. "
#         "Pengujian ini tidak boleh dijalankan kembali."
#     )
#
# saldo_sebelum = rekening_sebelum["saldo"]
# jumlah_riwayat_sebelum = len(riwayat_sebelum)
# jumlah_audit_sebelum = len(audit_sebelum)
#
# print("KONDISI SEBELUM PENCAIRAN")
# print(f"ID deposito       : {deposito_sebelum['id']}")
# print(f"Status deposito   : {deposito_sebelum['status']}")
# print(
#     f"Saldo rekening    : Rp"
#     f"{Utilitas.format_rupiah(saldo_sebelum)}"
# )
# print(
#     f"Nominal deposito  : Rp"
#     f"{Utilitas.format_rupiah(deposito_sebelum['nominal'])}"
# )
# print(f"Jumlah riwayat    : {jumlah_riwayat_sebelum}")
# print(f"Jumlah audit      : {jumlah_audit_sebelum}")
# print()
#
#
# # =========================================================
# # MENYIAPKAN STATUS JATUH TEMPO
# # =========================================================
#
# if deposito_sebelum["status"] != StatusDeposito.JATUH_TEMPO:
#     koneksi = buat_koneksi()
#
#     try:
#         jumlah_baris = (
#             DepositoRepository.perbarui_status_deposito(
#                 id_deposito=ID_DEPOSITO,
#                 status_baru=StatusDeposito.JATUH_TEMPO,
#                 koneksi=koneksi
#             )
#         )
#
#         if jumlah_baris != 1:
#             raise ValueError(
#                 "Gagal menyiapkan status jatuh tempo"
#             )
#
#         koneksi.commit()
#
#     except Exception:
#         koneksi.rollback()
#         raise
#
#     finally:
#         koneksi.close()
#
# print("✅ Status deposito disiapkan menjadi jatuh tempo")
#
#
# # =========================================================
# # MEMUAT ULANG OBJEK DARI SQLITE
# # =========================================================
#
# nasabah = NasabahLoader.muat_nasabah(
#     NIK_PENGUJIAN
# )
#
# assert nasabah is not None, (
#     "Nasabah gagal dimuat"
# )
#
# deposito = next(
#     (
#         item
#         for item in nasabah.deposito
#         if item.ID == ID_DEPOSITO
#     ),
#     None
# )
#
# assert deposito is not None, (
#     "Objek deposito ID 5 gagal dimuat"
# )
#
# assert deposito.status == StatusDeposito.JATUH_TEMPO, (
#     "Objek deposito tidak memuat status jatuh tempo"
# )
#
# assert deposito.rekening.norek == NOREK_PENGUJIAN, (
#     "Deposito terhubung dengan rekening yang salah"
# )
#
# total_yang_diharapkan = deposito.total_pencairan
# saldo_yang_diharapkan = (
#     saldo_sebelum + total_yang_diharapkan
# )
#
# print()
# print("DATA PENCAIRAN")
# print(f"Tanggal buka      : {deposito.tanggal_buka}")
# print(f"Jatuh tempo       : {deposito.jatuh_tempo}")
# print(f"Bunga             : {deposito.bunga:.1%}")
# print(
#     f"Total pencairan   : Rp"
#     f"{Utilitas.format_rupiah(total_yang_diharapkan)}"
# )
# print()
#
#
# # =========================================================
# # MENJALANKAN PENCAIRAN
# # =========================================================
#
# total_pencairan = (
#     DepositoService.cairkan_deposito(
#         deposito=deposito,
#         hari_ini=deposito.jatuh_tempo
#     )
# )
#
#
# # =========================================================
# # MENGAMBIL KONDISI SETELAH PENCAIRAN
# # =========================================================
#
# rekening_setelah = (
#     RekeningRepository.cari_rekening_dengan_norek(
#         NOREK_PENGUJIAN
#     )
# )
#
# deposito_setelah = (
#     DepositoRepository.cari_deposito_dengan_id(
#         ID_DEPOSITO
#     )
# )
#
# riwayat_setelah = (
#     RiwayatRepository.cari_seluruh_riwayat(
#         NOREK_PENGUJIAN
#     )
# )
#
# audit_setelah = (
#     AuditRepository.cari_audit_dengan_norek(
#         NOREK_PENGUJIAN
#     )
# )
#
# riwayat_pencairan = [
#     item
#     for item in riwayat_setelah
#     if item["jenis"] == "pencairan deposito"
# ]
#
# audit_pencairan = [
#     item
#     for item in audit_setelah
#     if item["jenis"] == "pencairan deposito"
# ]
#
# assert riwayat_pencairan, (
#     "Riwayat pencairan tidak ditemukan"
# )
#
# assert audit_pencairan, (
#     "Audit pencairan tidak ditemukan"
# )
#
# riwayat_terbaru = riwayat_pencairan[0]
# audit_terbaru = audit_pencairan[0]
#
#
# # =========================================================
# # MENAMPILKAN KONDISI SETELAH
# # =========================================================
#
# print("KONDISI SETELAH PENCAIRAN")
# print(
#     f"Saldo rekening    : Rp"
#     f"{Utilitas.format_rupiah(rekening_setelah['saldo'])}"
# )
# print(f"Status deposito   : {deposito_setelah['status']}")
# print(f"Jumlah riwayat    : {len(riwayat_setelah)}")
# print(f"Jumlah audit      : {len(audit_setelah)}")
# print()
#
# print("RIWAYAT PENCAIRAN")
# print(f"ID                : {riwayat_terbaru['id']}")
# print(f"Jenis             : {riwayat_terbaru['jenis']}")
# print(f"Waktu             : {riwayat_terbaru['waktu']}")
# print(f"Log               : {riwayat_terbaru['log']}")
# print()
#
# print("AUDIT PENCAIRAN")
# print(f"ID                : {audit_terbaru['id']}")
# print(f"Jenis             : {audit_terbaru['jenis']}")
# print(f"Waktu             : {audit_terbaru['waktu']}")
# print(f"Log               : {audit_terbaru['log']}")
# print(f"Nama              : {audit_terbaru['nama']}")
# print(f"NIK               : {audit_terbaru['nik']}")
# print(f"Norek             : {audit_terbaru['norek']}")
# print()
#
#
# # =========================================================
# # PEMERIKSAAN HASIL
# # =========================================================
#
# assert total_pencairan == total_yang_diharapkan, (
#     "Nilai yang dikembalikan service tidak sesuai"
# )
#
# assert rekening_setelah["saldo"] == saldo_yang_diharapkan, (
#     "Saldo SQLite tidak bertambah sesuai total pencairan"
# )
#
# assert deposito_setelah["status"] == StatusDeposito.DICAIRKAN, (
#     "Status deposito SQLite tidak berubah menjadi dicairkan"
# )
#
# assert deposito.rekening.saldo == saldo_yang_diharapkan, (
#     "Saldo objek rekening tidak berhasil disinkronkan"
# )
#
# assert deposito.status == StatusDeposito.DICAIRKAN, (
#     "Status objek deposito tidak berhasil disinkronkan"
# )
#
# assert len(riwayat_setelah) == jumlah_riwayat_sebelum + 1, (
#     "Jumlah riwayat tidak bertambah tepat satu"
# )
#
# assert len(audit_setelah) == jumlah_audit_sebelum + 1, (
#     "Jumlah audit tidak bertambah tepat satu"
# )
#
# assert riwayat_terbaru["norek"] == NOREK_PENGUJIAN, (
#     "Riwayat pencairan tersimpan pada rekening yang salah"
# )
#
# assert audit_terbaru["nik"] == NIK_PENGUJIAN, (
#     "Audit pencairan memiliki NIK yang salah"
# )
#
# assert audit_terbaru["norek"] == NOREK_PENGUJIAN, (
#     "Audit pencairan memiliki norek yang salah"
# )
#
#
# print("✅ Status jatuh tempo berhasil disiapkan")
# print("✅ Total pencairan berhasil dihitung")
# print("✅ Saldo rekening SQLite berhasil ditambahkan")
# print("✅ Status deposito berubah menjadi dicairkan")
# print("✅ Objek rekening dan deposito berhasil disinkronkan")
# print("✅ Riwayat pencairan bertambah tepat satu")
# print("✅ Audit pencairan bertambah tepat satu")
# print("✅ Pencairan deposito SQLite bekerja sesuai rancangan")




# print("---------------------------------------------------------------------")
#
# from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# from bank_djago.core.deposito import JenisAro
# from bank_djago.utils.utility import Utilitas
# from bank_djago.services.deposito.deposito_service import StatusDeposito
#
# NIK_PENGUJIAN = "1111222233334444"
# NOMINAL_DEPOSITO = 1_000_000
# SALDO_SEBELUM = 109_002_500
#
#
# nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# if nasabah is None:
#     raise AssertionError("Nasabah pengujian tidak ditemukan")
#
#
# deposito_aktif = [
#     deposito
#     for deposito in nasabah.deposito
#     if deposito.status == StatusDeposito.AKTIF
# ]
#
# deposito_aktif.sort(key=lambda deposito: deposito.ID)
#
# if len(deposito_aktif) < 2:
#     raise AssertionError(
#         "Dibutuhkan minimal dua deposito aktif untuk pengujian ARO"
#     )
#
#
# deposito_pokok = deposito_aktif[-2]
# deposito_pokok_bunga = deposito_aktif[-1]
#
# rekening = deposito_pokok.rekening
# saldo_seharusnya = SALDO_SEBELUM - (NOMINAL_DEPOSITO * 2)
#
#
# print("KONDISI AWAL PENGUJIAN ARO")
# print()
#
# print("DATA NASABAH")
# print("NIK             :", nasabah.NIK)
# print("Nama            :", nasabah.nama)
# print()
#
# print("DATA REKENING")
# print("Norek           :", rekening.norek)
# print(
#     "Saldo           : Rp"
#     + Utilitas.format_rupiah(rekening.saldo)
# )
# print()
#
# print("DEPOSITO ARO POKOK")
# print("ID              :", deposito_pokok.ID)
# print(
#     "Nominal         : Rp"
#     + Utilitas.format_rupiah(deposito_pokok.nominal)
# )
# print("Status          :", deposito_pokok.status)
# print("Jenis ARO       :", deposito_pokok.jenis_aro)
# print("Lama ARO        :", deposito_pokok.lama_aro)
# print("Tanggal buka    :", deposito_pokok.tanggal_buka)
# print("Jatuh tempo     :", deposito_pokok.jatuh_tempo)
# print("Proses ARO      :", deposito_pokok.proses_aro)
# print()
#
# print("DEPOSITO ARO POKOK + BUNGA")
# print("ID              :", deposito_pokok_bunga.ID)
# print(
#     "Nominal         : Rp"
#     + Utilitas.format_rupiah(deposito_pokok_bunga.nominal)
# )
# print("Status          :", deposito_pokok_bunga.status)
# print("Jenis ARO       :", deposito_pokok_bunga.jenis_aro)
# print("Lama ARO        :", deposito_pokok_bunga.lama_aro)
# print("Tanggal buka    :", deposito_pokok_bunga.tanggal_buka)
# print("Jatuh tempo     :", deposito_pokok_bunga.jatuh_tempo)
# print("Proses ARO      :", deposito_pokok_bunga.proses_aro)
# print()
#
#
# assert deposito_pokok.ID != deposito_pokok_bunga.ID
# print("✅ Kedua deposito mempunyai ID global berbeda")
#
# assert deposito_pokok.jenis_aro == JenisAro.POKOK
# print("✅ Deposito pertama menggunakan ARO pokok")
#
# assert deposito_pokok_bunga.jenis_aro == JenisAro.POKOK_BUNGA
# print("✅ Deposito kedua menggunakan ARO pokok + bunga")
#
# assert deposito_pokok.status == StatusDeposito.AKTIF
# assert deposito_pokok_bunga.status == StatusDeposito.AKTIF
# print("✅ Kedua deposito masih aktif")
#
# assert deposito_pokok.lama_aro in (1, 3, 6, 12)
# assert deposito_pokok_bunga.lama_aro in (1, 3, 6, 12)
# print("✅ Tenor ARO kedua deposito tersimpan")
#
# assert deposito_pokok.rekening is rekening
# assert deposito_pokok_bunga.rekening is rekening
# print("✅ Kedua deposito menunjuk objek rekening yang sama")
#
# assert deposito_pokok.pemilik is nasabah
# assert deposito_pokok_bunga.pemilik is nasabah
# print("✅ Kedua deposito menunjuk objek nasabah yang sama")
#
# assert rekening.saldo == saldo_seharusnya
# print("✅ Saldo rekening telah dipotong sesuai dua deposito")
#
# print()
# print("Data awal pengujian ARO siap digunakan")




# from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.services.deposito.deposito_service import DepositoService
# from bank_djago.core.deposito import JenisAro
# from bank_djago.utils.utility import Utilitas
# from bank_djago.services.deposito.deposito_service import StatusDeposito
#
# NIK_PENGUJIAN = "1111222233334444"
# ID_DEPOSITO = 6
#
#
# def hitung_data_pendukung(norek):
#     koneksi = buat_koneksi()
#
#     try:
#         jumlah_riwayat = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM riwayat
#             WHERE norek = ?
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         jumlah_audit = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM audit
#             WHERE norek = ?
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         return jumlah_riwayat, jumlah_audit
#
#     finally:
#         koneksi.close()
#
#
# nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# if nasabah is None:
#     raise AssertionError("Nasabah pengujian tidak ditemukan")
#
#
# deposito_pokok = next(
#     (
#         deposito
#         for deposito in nasabah.deposito
#         if deposito.ID == ID_DEPOSITO
#     ),
#     None
# )
#
# if deposito_pokok is None:
#     raise AssertionError(
#         f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
#     )
#
#
# rekening = deposito_pokok.rekening
#
# saldo_sebelum = rekening.saldo
# nominal_sebelum = deposito_pokok.nominal
# bunga_sebelum = deposito_pokok.bunga
# tanggal_buka_sebelum = deposito_pokok.tanggal_buka
# jatuh_tempo_sebelum = deposito_pokok.jatuh_tempo
# lama_aro = deposito_pokok.lama_aro
#
# total_pencairan = deposito_pokok.total_pencairan
# bunga_diterima = total_pencairan - nominal_sebelum
#
# saldo_seharusnya = saldo_sebelum + bunga_diterima
# tanggal_buka_seharusnya = jatuh_tempo_sebelum
# jatuh_tempo_seharusnya = Utilitas.tambah_bulan(
#     tanggal_buka_seharusnya,
#     lama_aro
# )
# bunga_baru_seharusnya = DepositoService.JANGKA_WAKTU[
#     lama_aro
# ]
#
# riwayat_sebelum, audit_sebelum = hitung_data_pendukung(
#     rekening.norek
# )
#
#
# print("KONDISI SEBELUM ARO POKOK")
# print()
#
# print("ID deposito       :", deposito_pokok.ID)
# print("Jenis ARO         :", deposito_pokok.jenis_aro)
# print(
#     "Nominal           : Rp"
#     + Utilitas.format_rupiah(nominal_sebelum)
# )
# print(f"Bunga lama        : {bunga_sebelum:.1%}")
# print("Tenor lama        :", deposito_pokok.lama_bulan, "bulan")
# print("Tenor ARO         :", lama_aro, "bulan")
# print("Tanggal buka      :", tanggal_buka_sebelum)
# print("Jatuh tempo       :", jatuh_tempo_sebelum)
# print("Proses ARO        :", deposito_pokok.proses_aro)
# print(
#     "Saldo rekening    : Rp"
#     + Utilitas.format_rupiah(saldo_sebelum)
# )
# print(
#     "Bunga diterima    : Rp"
#     + Utilitas.format_rupiah(bunga_diterima)
# )
# print("Jumlah riwayat    :", riwayat_sebelum)
# print("Jumlah audit      :", audit_sebelum)
# print()
#
#
# assert deposito_pokok.jenis_aro == JenisAro.POKOK
# assert deposito_pokok.status == StatusDeposito.AKTIF
#
# DepositoService.perpanjangan(
#     deposito=deposito_pokok,
#     hari_ini=jatuh_tempo_sebelum
# )
#
#
# # Memuat ulang data agar hasil yang diperiksa benar-benar berasal dari SQLite.
# nasabah_sesudah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# deposito_sesudah = next(
#     deposito
#     for deposito in nasabah_sesudah.deposito
#     if deposito.ID == ID_DEPOSITO
# )
#
# rekening_sesudah = deposito_sesudah.rekening
#
# riwayat_sesudah, audit_sesudah = hitung_data_pendukung(
#     rekening_sesudah.norek
# )
#
#
# print("KONDISI SETELAH ARO POKOK")
# print()
#
# print("ID deposito       :", deposito_sesudah.ID)
# print("Jenis ARO         :", deposito_sesudah.jenis_aro)
# print(
#     "Nominal           : Rp"
#     + Utilitas.format_rupiah(deposito_sesudah.nominal)
# )
# print(f"Bunga baru        : {deposito_sesudah.bunga:.1%}")
# print("Tenor baru        :", deposito_sesudah.lama_bulan, "bulan")
# print("Tanggal buka baru :", deposito_sesudah.tanggal_buka)
# print("Jatuh tempo baru  :", deposito_sesudah.jatuh_tempo)
# print("Proses ARO        :", deposito_sesudah.proses_aro)
# print(
#     "Saldo rekening    : Rp"
#     + Utilitas.format_rupiah(rekening_sesudah.saldo)
# )
# print("Jumlah riwayat    :", riwayat_sesudah)
# print("Jumlah audit      :", audit_sesudah)
# print()
#
#
# assert deposito_sesudah.nominal == nominal_sebelum
# print("✅ Pokok deposito tidak berubah")
#
# assert rekening_sesudah.saldo == saldo_seharusnya
# print("✅ Bunga deposito masuk ke saldo rekening")
#
# assert deposito_sesudah.bunga == bunga_baru_seharusnya
# print("✅ Bunga periode baru mengikuti tenor ARO")
#
# assert deposito_sesudah.lama_bulan == lama_aro
# print("✅ Tenor deposito berubah mengikuti lama ARO")
#
# assert deposito_sesudah.tanggal_buka == tanggal_buka_seharusnya
# print("✅ Tanggal buka periode baru sesuai jatuh tempo sebelumnya")
#
# assert deposito_sesudah.jatuh_tempo == jatuh_tempo_seharusnya
# print("✅ Jatuh tempo periode baru berhasil dihitung")
#
# assert deposito_sesudah.proses_aro == jatuh_tempo_sebelum
# print("✅ Tanggal proses ARO berhasil disimpan")
#
# assert deposito_sesudah.status == StatusDeposito.AKTIF
# print("✅ Deposito tetap aktif setelah diperpanjang")
#
# assert riwayat_sesudah == riwayat_sebelum + 2
# print("✅ Riwayat bunga dan perpanjangan bertambah tepat dua")
#
# assert audit_sesudah == audit_sebelum + 1
# print("✅ Audit perpanjangan bertambah tepat satu")
#
# print()
# print("✅ ARO pokok bekerja sesuai rancangan")




from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)
from bank_djago.core.deposito import JenisAro
from bank_djago.utils.utility import Utilitas


# NIK_PENGUJIAN = "1111222233334444"
# ID_DEPOSITO = 7
#
#
# def hitung_data_pendukung(norek):
#     koneksi = buat_koneksi()
#
#     try:
#         jumlah_riwayat = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM riwayat
#             WHERE norek = ?
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         jumlah_audit = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM audit
#             WHERE norek = ?
#             """,
#             (norek,)
#         ).fetchone()["jumlah"]
#
#         return jumlah_riwayat, jumlah_audit
#
#     finally:
#         koneksi.close()
#
#
# nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# if nasabah is None:
#     raise AssertionError("Nasabah pengujian tidak ditemukan")
#
#
# deposito_aro = next(
#     (
#         deposito
#         for deposito in nasabah.deposito
#         if deposito.ID == ID_DEPOSITO
#     ),
#     None
# )
#
# if deposito_aro is None:
#     raise AssertionError(
#         f"Deposito ID {ID_DEPOSITO} tidak ditemukan"
#     )
#
#
# rekening = deposito_aro.rekening
#
# saldo_sebelum = rekening.saldo
# nominal_sebelum = deposito_aro.nominal
# bunga_sebelum = deposito_aro.bunga
# tenor_sebelum = deposito_aro.lama_bulan
# tanggal_buka_sebelum = deposito_aro.tanggal_buka
# jatuh_tempo_sebelum = deposito_aro.jatuh_tempo
# lama_aro = deposito_aro.lama_aro
#
# total_pencairan = deposito_aro.total_pencairan
# nominal_baru_seharusnya = total_pencairan
# saldo_seharusnya = saldo_sebelum
#
# tanggal_buka_seharusnya = jatuh_tempo_sebelum
# jatuh_tempo_seharusnya = Utilitas.tambah_bulan(
#     tanggal_buka_seharusnya,
#     lama_aro
# )
#
# bunga_baru_seharusnya = DepositoService.JANGKA_WAKTU[
#     lama_aro
# ]
#
# riwayat_sebelum, audit_sebelum = hitung_data_pendukung(
#     rekening.norek
# )
#
#
# print("KONDISI SEBELUM ARO POKOK + BUNGA")
# print()
#
# print("ID deposito       :", deposito_aro.ID)
# print("Jenis ARO         :", deposito_aro.jenis_aro)
# print(
#     "Nominal lama      : Rp"
#     + Utilitas.format_rupiah(nominal_sebelum)
# )
# print(f"Bunga lama        : {bunga_sebelum:.1%}")
# print("Tenor lama        :", tenor_sebelum, "bulan")
# print("Tenor ARO         :", lama_aro, "bulan")
# print("Tanggal buka      :", tanggal_buka_sebelum)
# print("Jatuh tempo       :", jatuh_tempo_sebelum)
# print("Proses ARO        :", deposito_aro.proses_aro)
# print(
#     "Total pencairan   : Rp"
#     + Utilitas.format_rupiah(total_pencairan)
# )
# print(
#     "Saldo rekening    : Rp"
#     + Utilitas.format_rupiah(saldo_sebelum)
# )
# print("Jumlah riwayat    :", riwayat_sebelum)
# print("Jumlah audit      :", audit_sebelum)
# print()
#
#
# assert deposito_aro.jenis_aro == JenisAro.POKOK_BUNGA
# assert deposito_aro.status == StatusDeposito.AKTIF
#
# DepositoService.perpanjangan(
#     deposito=deposito_aro,
#     hari_ini=jatuh_tempo_sebelum
# )
#
#
# # Muat ulang agar hasil benar-benar diperiksa dari SQLite.
# nasabah_sesudah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
#
# deposito_sesudah = next(
#     deposito
#     for deposito in nasabah_sesudah.deposito
#     if deposito.ID == ID_DEPOSITO
# )
#
# rekening_sesudah = deposito_sesudah.rekening
#
# riwayat_sesudah, audit_sesudah = hitung_data_pendukung(
#     rekening_sesudah.norek
# )
#
#
# print("KONDISI SETELAH ARO POKOK + BUNGA")
# print()
#
# print("ID deposito       :", deposito_sesudah.ID)
# print("Jenis ARO         :", deposito_sesudah.jenis_aro)
# print(
#     "Nominal baru      : Rp"
#     + Utilitas.format_rupiah(deposito_sesudah.nominal)
# )
# print(f"Bunga baru        : {deposito_sesudah.bunga:.1%}")
# print("Tenor baru        :", deposito_sesudah.lama_bulan, "bulan")
# print("Tanggal buka baru :", deposito_sesudah.tanggal_buka)
# print("Jatuh tempo baru  :", deposito_sesudah.jatuh_tempo)
# print("Proses ARO        :", deposito_sesudah.proses_aro)
# print(
#     "Saldo rekening    : Rp"
#     + Utilitas.format_rupiah(rekening_sesudah.saldo)
# )
# print("Jumlah riwayat    :", riwayat_sesudah)
# print("Jumlah audit      :", audit_sesudah)
# print()
#
#
# assert deposito_sesudah.nominal == nominal_baru_seharusnya
# print("✅ Pokok dan bunga menjadi nominal deposito baru")
#
# assert deposito_sesudah.nominal > nominal_sebelum
# print("✅ Nominal deposito bertambah sebesar bunga")
#
# assert rekening_sesudah.saldo == saldo_seharusnya
# print("✅ Saldo rekening tidak berubah")
#
# assert deposito_sesudah.bunga == bunga_baru_seharusnya
# print("✅ Bunga periode baru mengikuti tenor ARO")
#
# assert deposito_sesudah.lama_bulan == lama_aro
# print("✅ Tenor deposito berubah mengikuti lama ARO")
#
# assert deposito_sesudah.tanggal_buka == tanggal_buka_seharusnya
# print("✅ Tanggal buka baru sesuai jatuh tempo sebelumnya")
#
# assert deposito_sesudah.jatuh_tempo == jatuh_tempo_seharusnya
# print("✅ Jatuh tempo periode baru berhasil dihitung")
#
# assert deposito_sesudah.proses_aro == jatuh_tempo_sebelum
# print("✅ Tanggal proses ARO berhasil disimpan")
#
# assert deposito_sesudah.status == StatusDeposito.AKTIF
# print("✅ Deposito tetap aktif setelah diperpanjang")
#
# assert riwayat_sesudah == riwayat_sebelum + 1
# print("✅ Riwayat perpanjangan bertambah tepat satu")
#
# assert audit_sesudah == audit_sebelum + 1
# print("✅ Audit perpanjangan bertambah tepat satu")
#
# print()
# print("✅ ARO pokok + bunga bekerja sesuai rancangan")



# from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
# from bank_djago.services.deposito.deposito_service import StatusDeposito
# from bank_djago.utils.utility import Utilitas
#
#
# daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()
#
# print("HASIL PEMUATAN DEPOSITO AKTIF")
# print("Jumlah deposito aktif:", len(daftar_deposito))
# print()
#
# if not daftar_deposito:
#     raise AssertionError("Tidak ada deposito aktif yang berhasil dimuat")
#
#
# for deposito in daftar_deposito:
#     print(f"DEPOSITO ID {deposito.ID}")
#     print("NIK pemilik      :", deposito.pemilik.NIK)
#     print("Nama pemilik     :", deposito.pemilik.nama)
#     print("Norek            :", deposito.rekening.norek)
#     print(
#         "Nominal          : Rp"
#         + Utilitas.format_rupiah(deposito.nominal)
#     )
#     print("Status           :", deposito.status)
#     print("Jenis ARO        :", deposito.jenis_aro)
#     print("Lama ARO         :", deposito.lama_aro)
#     print("Tanggal buka     :", deposito.tanggal_buka)
#     print("Jatuh tempo      :", deposito.jatuh_tempo)
#     print("Proses ARO       :", deposito.proses_aro)
#     print("ID objek nasabah :", id(deposito.pemilik))
#     print("ID objek rekening:", id(deposito.rekening))
#     print()
#
#
# assert all(
#     deposito.status == StatusDeposito.AKTIF
#     for deposito in daftar_deposito
# )
# print("✅ Loader hanya mengembalikan deposito aktif")
#
#
# daftar_id = [
#     deposito.ID
#     for deposito in daftar_deposito
# ]
#
# assert len(daftar_id) == len(set(daftar_id))
# print("✅ Tidak ada deposito yang dimuat dua kali")
#
#
# for deposito in daftar_deposito:
#     assert deposito.rekening.pemilik is deposito.pemilik
#
# print("✅ Setiap rekening menunjuk objek nasabah yang benar")
#
#
# deposito_6 = next(
#     (
#         deposito
#         for deposito in daftar_deposito
#         if deposito.ID == 6
#     ),
#     None
# )
#
# deposito_7 = next(
#     (
#         deposito
#         for deposito in daftar_deposito
#         if deposito.ID == 7
#     ),
#     None
# )
#
# if deposito_6 is None or deposito_7 is None:
#     raise AssertionError(
#         "Deposito ID 6 atau ID 7 tidak ditemukan dalam daftar aktif"
#     )
#
#
# assert deposito_6.pemilik is deposito_7.pemilik
# print("✅ Deposito ID 6 dan 7 memakai objek nasabah yang sama")
#
# assert deposito_6.rekening is deposito_7.rekening
# print("✅ Deposito ID 6 dan 7 memakai objek rekening yang sama")
#
# assert deposito_6 in deposito_6.pemilik.deposito
# assert deposito_7 in deposito_7.pemilik.deposito
# print("✅ Kedua deposito tersimpan dalam list deposito nasabah")
#
# assert deposito_6.rekening in deposito_6.pemilik.rekening
# print("✅ Rekening tersimpan dalam list rekening nasabah")
#
# print()
# print("✅ DepositoLoader bekerja sesuai rancangan identity map")


#
# import datetime
#
# from bank_djago.penyimpanan.storage import JsonStorage
# from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
# from bank_djago.services.scheduler import Scheduler
# from bank_djago.utils.utility import Utilitas
#
#
# ID_ARO_POKOK = 6
# ID_ARO_POKOK_BUNGA = 7
# HARI_PENGUJIAN = datetime.date(2026, 12, 28)
#
#
# def cari_deposito(daftar_deposito, id_deposito):
#     for deposito in daftar_deposito:
#         if deposito.ID == id_deposito:
#             return deposito
#
#     raise ValueError(
#         f"Deposito dengan ID {id_deposito} tidak ditemukan"
#     )
#
#
# # Scheduler masih membutuhkan objek bank karena pinjaman belum dimigrasikan.
# bank = JsonStorage.muat_bank()
#
# # --------------------------------------------------
# # KONDISI SEBELUM SCHEDULER
# # --------------------------------------------------
#
# daftar_sebelum = DepositoLoader.muat_semua_deposito_aktif()
#
# aro_pokok_sebelum = cari_deposito(
#     daftar_sebelum,
#     ID_ARO_POKOK
# )
#
# aro_pokok_bunga_sebelum = cari_deposito(
#     daftar_sebelum,
#     ID_ARO_POKOK_BUNGA
# )
#
# saldo_sebelum = aro_pokok_sebelum.rekening.saldo
#
# nominal_pokok_sebelum = aro_pokok_sebelum.nominal
# nominal_pokok_bunga_sebelum = aro_pokok_bunga_sebelum.nominal
#
# total_pokok = aro_pokok_sebelum.total_pencairan
# total_pokok_bunga = aro_pokok_bunga_sebelum.total_pencairan
#
# bunga_pokok_diterima = total_pokok - nominal_pokok_sebelum
#
# jatuh_tempo_pokok_sebelum = aro_pokok_sebelum.jatuh_tempo
# jatuh_tempo_pokok_bunga_sebelum = (
#     aro_pokok_bunga_sebelum.jatuh_tempo
# )
#
# print("KONDISI SEBELUM SCHEDULER\n")
#
# print("Saldo rekening       :",
#       f"Rp{Utilitas.format_rupiah(saldo_sebelum)}")
#
# print("\nARO POKOK")
# print("ID                   :", aro_pokok_sebelum.ID)
# print("Nominal              :",
#       f"Rp{Utilitas.format_rupiah(nominal_pokok_sebelum)}")
# print("Jatuh tempo          :", jatuh_tempo_pokok_sebelum)
# print("Proses ARO           :", aro_pokok_sebelum.proses_aro)
#
# print("\nARO POKOK + BUNGA")
# print("ID                   :", aro_pokok_bunga_sebelum.ID)
# print("Nominal              :",
#       f"Rp{Utilitas.format_rupiah(nominal_pokok_bunga_sebelum)}")
# print("Jatuh tempo          :", jatuh_tempo_pokok_bunga_sebelum)
# print("Proses ARO           :", aro_pokok_bunga_sebelum.proses_aro)
#
#
# # --------------------------------------------------
# # JALANKAN SCHEDULER DENGAN WAKTU BUATAN
# # --------------------------------------------------
#
# print("\nMenjalankan scheduler pada", HARI_PENGUJIAN)
#
# Scheduler.jalankan(
#     bank=bank,
#     hari_ini=HARI_PENGUJIAN
# )
#
#
# # --------------------------------------------------
# # MUAT ULANG DARI SQLITE
# # --------------------------------------------------
#
# daftar_sesudah = DepositoLoader.muat_semua_deposito_aktif()
#
# aro_pokok_sesudah = cari_deposito(
#     daftar_sesudah,
#     ID_ARO_POKOK
# )
#
# aro_pokok_bunga_sesudah = cari_deposito(
#     daftar_sesudah,
#     ID_ARO_POKOK_BUNGA
# )
#
# saldo_sesudah = aro_pokok_sesudah.rekening.saldo
#
# print("\nKONDISI SETELAH SCHEDULER\n")
#
# print("Saldo rekening       :",
#       f"Rp{Utilitas.format_rupiah(saldo_sesudah)}")
#
# print("\nARO POKOK")
# print("Nominal baru         :",
#       f"Rp{Utilitas.format_rupiah(aro_pokok_sesudah.nominal)}")
# print("Tanggal buka baru    :", aro_pokok_sesudah.tanggal_buka)
# print("Jatuh tempo baru     :", aro_pokok_sesudah.jatuh_tempo)
# print("Proses ARO           :", aro_pokok_sesudah.proses_aro)
#
# print("\nARO POKOK + BUNGA")
# print("Nominal baru         :",
#       f"Rp{Utilitas.format_rupiah(aro_pokok_bunga_sesudah.nominal)}")
# print("Tanggal buka baru    :", aro_pokok_bunga_sesudah.tanggal_buka)
# print("Jatuh tempo baru     :", aro_pokok_bunga_sesudah.jatuh_tempo)
# print("Proses ARO           :", aro_pokok_bunga_sesudah.proses_aro)
#
#
# # --------------------------------------------------
# # PENGECEKAN HASIL
# # --------------------------------------------------
#
# saldo_yang_diharapkan = saldo_sebelum + bunga_pokok_diterima
#
# assert aro_pokok_sesudah.nominal == nominal_pokok_sebelum
# print("\n✅ Nominal ARO pokok tidak berubah")
#
# assert aro_pokok_bunga_sesudah.nominal == total_pokok_bunga
# print("✅ Bunga ARO pokok+bunga masuk ke nominal baru")
#
# assert saldo_sesudah == saldo_yang_diharapkan
# print("✅ Hanya bunga ARO pokok yang masuk ke saldo rekening")
#
# assert (
#     aro_pokok_sesudah.tanggal_buka
#     == jatuh_tempo_pokok_sebelum
# )
# print("✅ Periode baru ARO pokok dimulai dari jatuh tempo lama")
#
# assert (
#     aro_pokok_bunga_sesudah.tanggal_buka
#     == jatuh_tempo_pokok_bunga_sebelum
# )
# print("✅ Periode baru ARO pokok+bunga dimulai dari jatuh tempo lama")
#
# assert aro_pokok_sesudah.proses_aro == HARI_PENGUJIAN
# assert aro_pokok_bunga_sesudah.proses_aro == HARI_PENGUJIAN
# print("✅ Tanggal proses kedua ARO berhasil disimpan")
#
# assert (
#     aro_pokok_sesudah.rekening
#     is aro_pokok_bunga_sesudah.rekening
# )
# print("✅ Kedua deposito memakai objek rekening yang sama")
#
# assert (
#     aro_pokok_sesudah.pemilik
#     is aro_pokok_bunga_sesudah.pemilik
# )
# print("✅ Kedua deposito memakai objek nasabah yang sama")
#
# print("\n✅ Scheduler deposito bekerja sesuai rancangan")



from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import JenisReferensiID


norek = "3001781978899033"
nominal_deposito = 1_000_000
tenor = 1

koneksi = buat_koneksi()

try:
    # ==========================================================
    # 1. Cari transaksi pembukaan deposito terbaru
    # ==========================================================
    transaksi = koneksi.execute(
        """
        SELECT *
        FROM transaksi
        WHERE norek_sumber = ?
          AND jenis = 'pembukaan_deposito'
        ORDER BY id DESC
        LIMIT 1
        """,
        (norek,)
    ).fetchone()

    if transaksi is None:
        raise ValueError(
            "Transaksi pembukaan deposito tidak ditemukan"
        )

    id_transaksi = transaksi["id"]
    id_deposito = transaksi["id_referensi"]

    # ==========================================================
    # 2. Ambil rekening dan deposito terkait
    # ==========================================================
    rekening = koneksi.execute(
        """
        SELECT *
        FROM rekening
        WHERE norek = ?
        """,
        (norek,)
    ).fetchone()

    deposito = koneksi.execute(
        """
        SELECT *
        FROM deposito
        WHERE id = ?
        """,
        (id_deposito,)
    ).fetchone()

    if rekening is None:
        raise ValueError("Rekening tidak ditemukan")

    if deposito is None:
        raise ValueError(
            "Deposito yang dirujuk transaksi tidak ditemukan"
        )

    # ==========================================================
    # 3. Ambil audit dan riwayat terkait
    # ==========================================================
    daftar_riwayat = koneksi.execute(
        """
        SELECT *
        FROM riwayat
        WHERE transaksi_id = ?
        ORDER BY id ASC
        """,
        (id_transaksi,)
    ).fetchall()

    daftar_audit = koneksi.execute(
        """
        SELECT *
        FROM audit
        WHERE transaksi_id = ?
        ORDER BY id ASC
        """,
        (id_transaksi,)
    ).fetchall()

    # ==========================================================
    # Tampilkan rekening
    # ==========================================================
    print("=== DATA REKENING ===")
    print(f"Nomor rekening       : {rekening['norek']}")
    print(f"Saldo sekarang       : {rekening['saldo']}")
    print(f"Status               : {rekening['status']}")

    # ==========================================================
    # Tampilkan deposito
    # ==========================================================
    print("\n=== DATA DEPOSITO ===")
    print(f"ID deposito          : {deposito['id']}")
    print(f"Nomor rekening       : {deposito['norek']}")
    print(f"Nominal              : {deposito['nominal']}")
    print(f"Tenor                : {deposito['lama_bulan']}")
    print(f"Jenis ARO            : {deposito['jenis_aro']}")
    print(f"Status               : {deposito['status']}")
    print(f"Tanggal buka         : {deposito['tanggal_buka']}")
    print(f"Jatuh tempo          : {deposito['jatuh_tempo']}")

    # ==========================================================
    # Tampilkan transaksi
    # ==========================================================
    print("\n=== DATA TRANSAKSI ===")
    print(f"ID transaksi         : {transaksi['id']}")
    print(f"Jenis                : {transaksi['jenis']}")
    print(f"Rekening sumber      : {transaksi['norek_sumber']}")
    print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
    print(f"Nominal              : {transaksi['nominal']}")
    print(
        f"Saldo sumber sebelum : "
        f"{transaksi['saldo_sumber_sebelum']}"
    )
    print(
        f"Saldo sumber sesudah : "
        f"{transaksi['saldo_sumber_sesudah']}"
    )
    print(
        f"Jenis referensi      : "
        f"{transaksi['jenis_referensi']}"
    )
    print(f"ID referensi         : {transaksi['id_referensi']}")
    print(f"Waktu                : {transaksi['waktu']}")

    print("\n=== RIWAYAT TERHUBUNG ===")

    for riwayat in daftar_riwayat:
        print(
            f"ID {riwayat['id']} | "
            f"Transaksi {riwayat['transaksi_id']} | "
            f"{riwayat['jenis']} | "
            f"{riwayat['log']}"
        )

    print("\n=== AUDIT TERHUBUNG ===")

    for audit in daftar_audit:
        print(
            f"ID {audit['id']} | "
            f"Transaksi {audit['transaksi_id']} | "
            f"{audit['jenis']} | "
            f"{audit['log']}"
        )

    # ==========================================================
    # 4. Periksa data deposito
    # ==========================================================
    assert deposito["norek"] == norek
    assert deposito["nominal"] == nominal_deposito
    assert deposito["lama_bulan"] == tenor
    assert deposito["jenis_aro"] == "tidak"
    assert deposito["status"] == "aktif"

    # ==========================================================
    # 5. Periksa transaksi
    # ==========================================================
    assert transaksi["jenis"] == "pembukaan_deposito"
    assert transaksi["norek_sumber"] == norek
    assert transaksi["norek_tujuan"] is None
    assert transaksi["nominal"] == nominal_deposito

    assert transaksi["saldo_sumber_sebelum"] - nominal_deposito == (
        transaksi["saldo_sumber_sesudah"]
    )

    assert rekening["saldo"] == (
        transaksi["saldo_sumber_sesudah"]
    )

    assert str(transaksi["jenis_referensi"]) == str(
        JenisReferensiID.DEPOSITO.value
    )

    assert transaksi["id_referensi"] == deposito["id"]
    assert transaksi["waktu"] is not None

    # ==========================================================
    # 6. Periksa hubungan audit dan riwayat
    # ==========================================================
    assert len(daftar_riwayat) == 1
    assert len(daftar_audit) == 1

    assert daftar_riwayat[0]["norek"] == norek
    assert daftar_riwayat[0]["transaksi_id"] == id_transaksi

    assert daftar_audit[0]["norek"] == norek
    assert daftar_audit[0]["transaksi_id"] == id_transaksi

    print(
        "\n✅ Pembukaan deposito dan transaksi "
        "tersimpan dengan benar"
    )

finally:
    koneksi.close()
