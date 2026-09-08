# import datetime
#
# from bank_djago.core.nasabah import Nasabahh
# from bank_djago.core.rekening import (
#     RekeningReguler,
#     RekeningPrioritas,
#     RekeningGold,
#     RekeningPlatinum
# )
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# from bank_djago.services.rekening.rekening_service import RekeningService
#
#
# NOREK_UJI = "3001781978899033"
# ALASAN_UJI = "Pengujian blokir darurat"
#
#
# def muat_rekening_uji(norek):
#
#     koneksi = buat_koneksi()
#
#     try:
#         data = koneksi.execute(
#             """
#             SELECT
#                 rekening.*,
#                 nasabah.nama AS nama_pemilik,
#                 nasabah.alamat AS alamat_pemilik
#             FROM rekening
#             JOIN nasabah
#                 ON nasabah.nik = rekening.nik_pemilik
#             WHERE rekening.norek = ?
#             """,
#             (norek,)
#         ).fetchone()
#
#         if data is None:
#             raise ValueError(
#                 "Rekening pengujian tidak ditemukan"
#             )
#
#         # =========================================
#         # BUAT OBJEK NASABAH
#         # =========================================
#
#         nasabah = Nasabahh(
#             nama=data["nama_pemilik"],
#             alamat=data["alamat_pemilik"],
#             nik=data["nik_pemilik"]
#         )
#
#         # =========================================
#         # TENTUKAN KELAS REKENING
#         # =========================================
#
#         if data["level"] == 1:
#             kelas_rekening = RekeningReguler
#
#         elif data["level"] == 2:
#             kelas_rekening = RekeningPrioritas
#
#         elif data["level"] == 3:
#             kelas_rekening = RekeningGold
#
#         elif data["level"] == 4:
#             kelas_rekening = RekeningPlatinum
#
#         else:
#             raise ValueError(
#                 "Level rekening tidak dikenal"
#             )
#
#         waktu_dibuat = None
#
#         if data["waktu_dibuat"] is not None:
#             waktu_dibuat = datetime.datetime.fromisoformat(
#                 data["waktu_dibuat"]
#             )
#
#         # =========================================
#         # BUAT OBJEK REKENING
#         # =========================================
#
#         rekening = kelas_rekening(
#             norek=data["norek"],
#             pin=data["pin"],
#             pemilik=nasabah,
#             waktu_dibuat=waktu_dibuat
#         )
#
#         rekening.set_saldo(
#             data["saldo"]
#         )
#
#         rekening.status = data["status"]
#
#         rekening.alasan_blokir = (
#             data["alasan_blokir"]
#         )
#
#         nasabah.rekening.append(
#             rekening
#         )
#
#         return rekening
#
#     finally:
#         koneksi.close()
#
#
# def ambil_audit_blokir_terakhir(norek):
#
#     koneksi = buat_koneksi()
#
#     try:
#         audit = koneksi.execute(
#             """
#             SELECT
#                 id,
#                 kategori,
#                 objek,
#                 aksi,
#                 log,
#                 nama,
#                 nik,
#                 norek
#             FROM audit
#             WHERE norek = ?
#             AND aksi = 'pemblokiran_rekening'
#             ORDER BY id DESC
#             LIMIT 1
#             """,
#             (norek,)
#         ).fetchone()
#
#         return audit
#
#     finally:
#         koneksi.close()
#
#
# def hitung_audit_blokir(norek):
#
#     koneksi = buat_koneksi()
#
#     try:
#         hasil = koneksi.execute(
#             """
#             SELECT COUNT(*) AS jumlah
#             FROM audit
#             WHERE norek = ?
#             AND aksi = 'pemblokiran_rekening'
#             """,
#             (norek,)
#         ).fetchone()
#
#         return hasil["jumlah"]
#
#     finally:
#         koneksi.close()
#
#
# def test_blokir_rekening():
#
#     print("=" * 70)
#     print("TEST BLOKIR REKENING")
#     print("=" * 70)
#
#     # =========================================
#     # 1. MUAT REKENING DARI SQLITE
#     # =========================================
#
#     rekening = muat_rekening_uji(
#         NOREK_UJI
#     )
#
#     print()
#     print(
#         "Status SQLite :",
#         rekening.status
#     )
#
#     print(
#         "Alasan blokir :",
#         rekening.alasan_blokir
#     )
#
#     assert rekening.status == "blokir"
#
#     assert (
#         rekening.alasan_blokir
#         == ALASAN_UJI
#     )
#
#     print(
#         "✅ Status dan alasan tersimpan di SQLite"
#     )
#
#     # =========================================
#     # 2. PERIKSA AUDIT
#     # =========================================
#
#     audit = ambil_audit_blokir_terakhir(
#         NOREK_UJI
#     )
#
#     assert audit is not None
#
#     assert (
#         audit["kategori"]
#         == "administratif"
#     )
#
#     assert (
#         audit["objek"]
#         == "rekening"
#     )
#
#     assert (
#         audit["aksi"]
#         == "pemblokiran_rekening"
#     )
#
#     assert (
#         audit["norek"]
#         == NOREK_UJI
#     )
#
#     print()
#     print("Audit ditemukan:")
#     print(
#         "Kategori :",
#         audit["kategori"]
#     )
#     print(
#         "Objek    :",
#         audit["objek"]
#     )
#     print(
#         "Aksi     :",
#         audit["aksi"]
#     )
#     print(
#         "Log      :",
#         audit["log"]
#     )
#
#     print(
#         "✅ Audit pemblokiran tersimpan dengan benar"
#     )
#
#     # =========================================
#     # 3. CATAT JUMLAH AUDIT SEBELUM BLOKIR KEDUA
#     # =========================================
#
#     jumlah_audit_sebelum = (
#         hitung_audit_blokir(
#             NOREK_UJI
#         )
#     )
#
#     # =========================================
#     # 4. COBA BLOKIR REKENING YANG SUDAH DIBLOKIR
#     # =========================================
#
#     print()
#     print(
#         "Mencoba memblokir rekening "
#         "untuk kedua kalinya..."
#     )
#
#     try:
#         RekeningService.blokir_rekening(
#             rekening=rekening,
#             alasan="Percobaan blokir kedua"
#         )
#
#         raise AssertionError(
#             "Rekening yang sudah diblokir "
#             "ternyata masih bisa diblokir lagi"
#         )
#
#     except ValueError as error:
#         print(
#             "✅ Blokir kedua ditolak:"
#         )
#         print(error)
#
#     # =========================================
#     # 5. PASTIKAN BLOKIR GAGAL TIDAK MEMBUAT AUDIT
#     # =========================================
#
#     jumlah_audit_sesudah = (
#         hitung_audit_blokir(
#             NOREK_UJI
#         )
#     )
#
#     assert (
#         jumlah_audit_sebelum
#         == jumlah_audit_sesudah
#     )
#
#     print()
#     print(
#         "✅ Blokir kedua tidak menghasilkan "
#         "audit tambahan"
#     )
#
#     print()
#     print("=" * 70)
#     print("SEMUA TEST BLOKIR REKENING BERHASIL")
#     print("=" * 70)
#
#
# if __name__ == "__main__":
#     test_blokir_rekening()