# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # #
# # # def petakan_audit_lama(kategori_lama, jenis_lama):
# # #
# # #     # =========================================================
# # #     # KATEGORI LAMA: NASABAH
# # #     # =========================================================
# # #
# # #     if kategori_lama == "nasabah":
# # #
# # #         if jenis_lama == "pendaftaran nasabah":
# # #             return (
# # #                 "administratif",
# # #                 "nasabah",
# # #                 "pendaftaran_nasabah"
# # #             )
# # #
# # #     # =========================================================
# # #     # KATEGORI LAMA: REKENING
# # #     # =========================================================
# # #
# # #     elif kategori_lama == "rekening":
# # #
# # #         if jenis_lama == "pembukaan":
# # #             return (
# # #                 "administratif",
# # #                 "rekening",
# # #                 "pembukaan_rekening"
# # #             )
# # #
# # #         elif jenis_lama == "upgrade":
# # #             return (
# # #                 "administratif",
# # #                 "rekening",
# # #                 "peningkatan_level_rekening"
# # #             )
# # #
# # #         elif jenis_lama == "downgrade":
# # #             return (
# # #                 "administratif",
# # #                 "rekening",
# # #                 "penurunan_level_rekening"
# # #             )
# # #
# # #         elif jenis_lama == "pengajuan penutupan":
# # #             return (
# # #                 "administratif",
# # #                 "rekening",
# # #                 "pengajuan_penutupan_rekening"
# # #             )
# # #
# # #         elif jenis_lama == "persetujuan pengajuan":
# # #             return (
# # #                 "administratif",
# # #                 "rekening",
# # #                 "persetujuan_penutupan_rekening"
# # #             )
# # #
# # #         elif jenis_lama == "penolakan pengajuan":
# # #             return (
# # #                 "administratif",
# # #                 "rekening",
# # #                 "penolakan_penutupan_rekening"
# # #             )
# # #
# # #         elif jenis_lama == "penutupan tarik saldo":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "penarikan_saldo_penutupan"
# # #             )
# # #
# # #         elif jenis_lama == "penutupan transfer saldo":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "pemindahan_saldo_penutupan"
# # #             )
# # #
# # #     # =========================================================
# # #     # KATEGORI LAMA: TRANSAKSI
# # #     # =========================================================
# # #
# # #     elif kategori_lama == "transaksi":
# # #
# # #         if jenis_lama == "setor uang":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "setor_tunai"
# # #             )
# # #
# # #         elif jenis_lama == "tarik uang":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "tarik_tunai"
# # #             )
# # #
# # #         elif jenis_lama == "transfer":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "transfer_keluar"
# # #             )
# # #
# # #         elif jenis_lama == "terima saldo":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "penerimaan_transfer"
# # #             )
# # #
# # #         elif jenis_lama == "dapat bunga":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "pemberian_bunga_tabungan"
# # #             )
# # #
# # #         elif jenis_lama == "biaya admin":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "pemotongan_biaya_admin"
# # #             )
# # #
# # #         elif jenis_lama == "bayar biaya admin":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "pemotongan_biaya_admin"
# # #             )
# # #
# # #         elif jenis_lama == "terima saldo penutupan":
# # #             return (
# # #                 "finansial",
# # #                 "rekening",
# # #                 "penerimaan_saldo_penutupan"
# # #             )
# # #
# # #         elif jenis_lama == "deposito":
# # #             return (
# # #                 "finansial",
# # #                 "deposito",
# # #                 "pembukaan_deposito"
# # #             )
# # #
# # #         elif jenis_lama == "pencairan deposito":
# # #             return (
# # #                 "finansial",
# # #                 "deposito",
# # #                 "pencairan_deposito"
# # #             )
# # #
# # #         elif jenis_lama == "perpanjang deposito":
# # #             return (
# # #                 "finansial",
# # #                 "deposito",
# # #                 "perpanjangan_deposito_aro"
# # #             )
# # #
# # #         elif jenis_lama == "pengajuan pinjaman":
# # #             return (
# # #                 "administratif",
# # #                 "pinjaman",
# # #                 "pengajuan_pinjaman"
# # #             )
# # #
# # #         elif jenis_lama == "persetujuan pinjaman":
# # #             return (
# # #                 "administratif",
# # #                 "pinjaman",
# # #                 "persetujuan_pinjaman"
# # #             )
# # #
# # #         elif jenis_lama == "penolakan pinjaman":
# # #             return (
# # #                 "administratif",
# # #                 "pinjaman",
# # #                 "penolakan_pinjaman"
# # #             )
# # #
# # #         elif jenis_lama == "pencairan pinjaman":
# # #             return (
# # #                 "finansial",
# # #                 "pinjaman",
# # #                 "pencairan_pinjaman"
# # #             )
# # #
# # #         elif jenis_lama == "pembayaran cicilan":
# # #             return (
# # #                 "finansial",
# # #                 "pinjaman",
# # #                 "pembayaran_cicilan_pinjaman"
# # #             )
# # #
# # #     # =========================================================
# # #     # Tidak ditemukan dalam peta migrasi
# # #     # =========================================================
# # #
# # #     raise ValueError(
# # #         f"Audit tidak memiliki pemetaan: "
# # #         f"kategori='{kategori_lama}', "
# # #         f"jenis='{jenis_lama}'"
# # #     )
# # # # #
# # # # # def cek_pemetaan_semua_audit():
# # # # #     koneksi = buat_koneksi()
# # # # #
# # # # #     try:
# # # # #         daftar_audit = koneksi.execute(
# # # # #             """
# # # # #             SELECT *
# # # # #             FROM audit
# # # # #             ORDER BY id
# # # # #             """
# # # # #         ).fetchall()
# # # # #
# # # # #         for audit_lama in daftar_audit:
# # # # #
# # # # #             kategori_lama = audit_lama["kategori"]
# # # # #             jenis_lama = audit_lama["jenis"]
# # # # #
# # # # #             kategori_baru, objek, aksi = petakan_audit_lama(
# # # # #                 kategori_lama,
# # # # #                 jenis_lama
# # # # #             )
# # # # #
# # # # #             print(
# # # # #                 f"ID {audit_lama['id']} | "
# # # # #                 f"{kategori_lama} → {jenis_lama}"
# # # # #             )
# # # # #
# # # # #             print(
# # # # #                 f"      ↓ "
# # # # #                 f"{kategori_baru} → {objek} → {aksi}"
# # # # #             )
# # # # #
# # # # #     finally:
# # # # #         koneksi.close()
# # # # #
# # # # # if __name__ == "__main__":
# # # # #     cek_pemetaan_semua_audit()
# # # #
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # #
# # # # koneksi = buat_koneksi()
# # # #
# # # # hasil_lama = koneksi.execute(
# # # #     """
# # # #     SELECT COUNT(*) AS total
# # # #     FROM audit
# # # #     """
# # # # ).fetchone()
# # # #
# # # # hasil_baru = koneksi.execute(
# # # #     """
# # # #     SELECT COUNT(*) AS total
# # # #     FROM audit_baru
# # # #     """
# # # # ).fetchone()
# # # #
# # # # print("Audit lama :", hasil_lama["total"])
# # # # print("Audit baru :", hasil_baru["total"])
# # #
# # #
# # #
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # #
# # # #
# # # # def cari_id_audit_yang_hilang():
# # # #     koneksi = buat_koneksi()
# # # #
# # # #     try:
# # # #         daftar_id = koneksi.execute(
# # # #             """
# # # #             SELECT id
# # # #             FROM audit
# # # #             ORDER BY id
# # # #             """
# # # #         ).fetchall()
# # # #
# # # #         id_yang_ada = []
# # # #
# # # #         for baris in daftar_id:
# # # #             id_yang_ada.append(baris["id"])
# # # #
# # # #         id_terbesar = id_yang_ada[-1]
# # # #
# # # #         print("ID terbesar :", id_terbesar)
# # # #         print("Jumlah audit:", len(id_yang_ada))
# # # #
# # # #         print()
# # # #         print("ID YANG HILANG:")
# # # #
# # # #         for id_audit in range(1, id_terbesar + 1):
# # # #
# # # #             if id_audit not in id_yang_ada:
# # # #                 print(id_audit)
# # # #
# # # #     finally:
# # # #         koneksi.close()
# # # #
# # # #
# # # # if __name__ == "__main__":
# # # #     cari_id_audit_yang_hilang()
# # #
# # #
# # #
# # # def pindahkan_audit_lama():
# # #     koneksi = buat_koneksi()
# # #
# # #     try:
# # #         # =========================================================
# # #         # 1. Pastikan audit_baru masih kosong
# # #         # =========================================================
# # #         hasil_jumlah_baru = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS total
# # #             FROM audit_baru
# # #             """
# # #         ).fetchone()
# # #
# # #         jumlah_baru_sebelum = hasil_jumlah_baru["total"]
# # #
# # #         if jumlah_baru_sebelum != 0:
# # #             raise ValueError(
# # #                 "Tabel audit_baru tidak kosong. "
# # #                 "Migrasi dibatalkan."
# # #             )
# # #
# # #         # =========================================================
# # #         # 2. Ambil seluruh audit lama
# # #         # =========================================================
# # #         daftar_audit_lama = koneksi.execute(
# # #             """
# # #             SELECT
# # #                 id,
# # #                 kategori,
# # #                 jenis,
# # #                 waktu,
# # #                 log,
# # #                 nama,
# # #                 nik,
# # #                 norek,
# # #                 transaksi_id
# # #             FROM audit
# # #             ORDER BY id
# # #             """
# # #         ).fetchall()
# # #
# # #         jumlah_audit_lama = len(daftar_audit_lama)
# # #
# # #         print("Jumlah audit lama :", jumlah_audit_lama)
# # #
# # #         # =========================================================
# # #         # 3. Mulai proses pemindahan
# # #         # =========================================================
# # #         for audit_lama in daftar_audit_lama:
# # #
# # #             kategori_lama = audit_lama["kategori"]
# # #             jenis_lama = audit_lama["jenis"]
# # #
# # #             # Terjemahkan format lama ke format baru
# # #             kategori_baru, objek, aksi = petakan_audit_lama(
# # #                 kategori_lama,
# # #                 jenis_lama
# # #             )
# # #
# # #             # Masukkan ke tabel baru
# # #             koneksi.execute(
# # #                 """
# # #                 INSERT INTO audit_baru (
# # #                     id,
# # #                     kategori,
# # #                     objek,
# # #                     aksi,
# # #                     waktu,
# # #                     log,
# # #                     nama,
# # #                     nik,
# # #                     norek,
# # #                     transaksi_id
# # #                 )
# # #                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
# # #                 """,
# # #                 (
# # #                     audit_lama["id"],
# # #                     kategori_baru,
# # #                     objek,
# # #                     aksi,
# # #                     audit_lama["waktu"],
# # #                     audit_lama["log"],
# # #                     audit_lama["nama"],
# # #                     audit_lama["nik"],
# # #                     audit_lama["norek"],
# # #                     audit_lama["transaksi_id"]
# # #                 )
# # #             )
# # #
# # #         # =========================================================
# # #         # 4. Hitung hasil migrasi
# # #         # =========================================================
# # #         hasil_jumlah_baru = koneksi.execute(
# # #             """
# # #             SELECT COUNT(*) AS total
# # #             FROM audit_baru
# # #             """
# # #         ).fetchone()
# # #
# # #         jumlah_audit_baru = hasil_jumlah_baru["total"]
# # #
# # #         print("Jumlah audit baru :", jumlah_audit_baru)
# # #
# # #         # =========================================================
# # #         # 5. Pastikan jumlah tidak berubah
# # #         # =========================================================
# # #         if jumlah_audit_lama != jumlah_audit_baru:
# # #             raise ValueError(
# # #                 "Jumlah audit lama dan baru tidak sama."
# # #             )
# # #
# # #         # =========================================================
# # #         # 6. Bandingkan ID terbesar
# # #         # =========================================================
# # #         hasil_id_lama = koneksi.execute(
# # #             """
# # #             SELECT MAX(id) AS id_terbesar
# # #             FROM audit
# # #             """
# # #         ).fetchone()
# # #
# # #         hasil_id_baru = koneksi.execute(
# # #             """
# # #             SELECT MAX(id) AS id_terbesar
# # #             FROM audit_baru
# # #             """
# # #         ).fetchone()
# # #
# # #         id_terbesar_lama = hasil_id_lama["id_terbesar"]
# # #         id_terbesar_baru = hasil_id_baru["id_terbesar"]
# # #
# # #         print("ID terbesar lama :", id_terbesar_lama)
# # #         print("ID terbesar baru :", id_terbesar_baru)
# # #
# # #         if id_terbesar_lama != id_terbesar_baru:
# # #             raise ValueError(
# # #                 "ID terbesar audit lama dan baru tidak sama."
# # #             )
# # #
# # #         # =========================================================
# # #         # 7. Semua pengecekan berhasil
# # #         # =========================================================
# # #         koneksi.commit()
# # #
# # #         print()
# # #         print("✅ MIGRASI DATA AUDIT BERHASIL")
# # #
# # #     except Exception:
# # #         koneksi.rollback()
# # #         print()
# # #         print("❌ MIGRASI DATA AUDIT GAGAL")
# # #         raise
# # #
# # #     finally:
# # #         koneksi.close()
# # #
# # #
# # # if __name__ == "__main__":
# # #     pindahkan_audit_lama()
# #
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# #
# # def cek_hasil_migrasi_audit():
# #     koneksi = buat_koneksi()
# #
# #     try:
# #         hasil = koneksi.execute(
# #             """
# #             SELECT
# #                 kategori,
# #                 objek,
# #                 aksi,
# #                 COUNT(*) AS jumlah
# #             FROM audit_baru
# #             GROUP BY kategori, objek, aksi
# #             ORDER BY kategori, objek, aksi
# #             """
# #         ).fetchall()
# #
# #         print("=" * 80)
# #         print("HASIL MIGRASI AUDIT BARU")
# #         print("=" * 80)
# #
# #         for baris in hasil:
# #             print(
# #                 f"{baris['kategori']} "
# #                 f"→ {baris['objek']} "
# #                 f"→ {baris['aksi']} "
# #                 f"| Jumlah: {baris['jumlah']}"
# #             )
# #
# #     finally:
# #         koneksi.close()
# #
# #
# # if __name__ == "__main__":
# #     cek_hasil_migrasi_audit()
#
#
#
# def ganti_tabel_audit():
#     koneksi = buat_koneksi()
#
#     try:
#         # =========================================================
#         # 1. Hitung data sebelum pergantian tabel
#         # =========================================================
#         hasil_lama = koneksi.execute(
#             """
#             SELECT COUNT(*) AS total
#             FROM audit
#             """
#         ).fetchone()
#
#         hasil_baru = koneksi.execute(
#             """
#             SELECT COUNT(*) AS total
#             FROM audit_baru
#             """
#         ).fetchone()
#
#         jumlah_lama = hasil_lama["total"]
#         jumlah_baru = hasil_baru["total"]
#
#         print("Audit lama :", jumlah_lama)
#         print("Audit baru :", jumlah_baru)
#
#         # Jangan lanjut kalau jumlahnya berbeda
#         if jumlah_lama != jumlah_baru:
#             raise ValueError(
#                 "Jumlah audit lama dan audit baru berbeda."
#             )
#
#         # =========================================================
#         # 2. Hapus tabel audit lama
#         # =========================================================
#         koneksi.execute(
#             """
#             DROP TABLE audit
#             """
#         )
#
#         print("✅ Tabel audit lama dihapus")
#
#         # =========================================================
#         # 3. Ganti nama audit_baru menjadi audit
#         # =========================================================
#         koneksi.execute(
#             """
#             ALTER TABLE audit_baru
#             RENAME TO audit
#             """
#         )
#
#         print("✅ audit_baru diubah menjadi audit")
#
#         # =========================================================
#         # 4. Pastikan jumlah data tetap benar
#         # =========================================================
#         hasil_setelah = koneksi.execute(
#             """
#             SELECT COUNT(*) AS total
#             FROM audit
#             """
#         ).fetchone()
#
#         jumlah_setelah = hasil_setelah["total"]
#
#         print("Jumlah setelah pergantian :", jumlah_setelah)
#
#         if jumlah_setelah != jumlah_lama:
#             raise ValueError(
#                 "Jumlah audit berubah setelah pergantian tabel."
#             )
#
#         # =========================================================
#         # 5. Periksa ID terbesar
#         # =========================================================
#         hasil_id = koneksi.execute(
#             """
#             SELECT MAX(id) AS id_terbesar
#             FROM audit
#             """
#         ).fetchone()
#
#         id_terbesar = hasil_id["id_terbesar"]
#
#         print("ID terbesar :", id_terbesar)
#
#         if id_terbesar != 142:
#             raise ValueError(
#                 "ID terbesar audit tidak sesuai."
#             )
#
#         # =========================================================
#         # 6. Periksa struktur tabel baru
#         # =========================================================
#         daftar_kolom = koneksi.execute(
#             """
#             PRAGMA table_info(audit)
#             """
#         ).fetchall()
#
#         nama_kolom = []
#
#         for kolom in daftar_kolom:
#             nama_kolom.append(kolom["name"])
#
#         kolom_yang_diharapkan = [
#             "id",
#             "kategori",
#             "objek",
#             "aksi",
#             "waktu",
#             "log",
#             "nama",
#             "nik",
#             "norek",
#             "transaksi_id"
#         ]
#
#         if nama_kolom != kolom_yang_diharapkan:
#             raise ValueError(
#                 "Struktur tabel audit tidak sesuai."
#             )
#
#         print("✅ Struktur tabel audit sesuai")
#
#         # =========================================================
#         # 7. Semua pengecekan berhasil
#         # =========================================================
#         koneksi.commit()
#
#         print()
#         print("=" * 60)
#         print("✅ PERGANTIAN TABEL AUDIT BERHASIL")
#         print("=" * 60)
#
#     except Exception:
#         koneksi.rollback()
#
#         print()
#         print("❌ PERGANTIAN TABEL AUDIT GAGAL")
#         print("Semua perubahan dibatalkan.")
#
#         raise
#
#     finally:
#         koneksi.close()
#
#
# if __name__ == "__main__":
#     ganti_tabel_audit()



import datetime

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository


def tes_tambah_audit_baru():
    koneksi = buat_koneksi()

    try:
        # =========================================================
        # 1. Hitung jumlah audit sebelum test
        # =========================================================
        hasil_sebelum = koneksi.execute(
            """
            SELECT COUNT(*) AS total
            FROM audit
            """
        ).fetchone()

        jumlah_sebelum = hasil_sebelum["total"]

        print("Jumlah audit sebelum :", jumlah_sebelum)

        # =========================================================
        # 2. Buat audit dengan struktur BARU
        # =========================================================
        audit = {
            "kategori": "administratif",
            "objek": "rekening",
            "aksi": "pembukaan_rekening",
            "waktu": datetime.datetime.now(),
            "log": "Pengujian repository audit baru",
            "nama": "Nasabah Testing",
            "nik": "5555666677778888",
            "norek": None
        }

        # =========================================================
        # 3. Simpan melalui AuditRepository
        # =========================================================
        id_audit = AuditRepository.tambah_audit(
            audit,
            koneksi
        )

        print("ID audit testing :", id_audit)

        # =========================================================
        # 4. Ambil kembali audit yang baru dimasukkan
        # =========================================================
        hasil = koneksi.execute(
            """
            SELECT *
            FROM audit
            WHERE id = ?
            """,
            (id_audit,)
        ).fetchone()

        print()
        print("HASIL AUDIT:")
        print("Kategori :", hasil["kategori"])
        print("Objek    :", hasil["objek"])
        print("Aksi     :", hasil["aksi"])
        print("Log      :", hasil["log"])

        # =========================================================
        # 5. Verifikasi nilai
        # =========================================================
        assert hasil["kategori"] == "administratif"
        assert hasil["objek"] == "rekening"
        assert hasil["aksi"] == "pembukaan_rekening"

        print()
        print("✅ Audit format baru berhasil disimpan")

        # =========================================================
        # 6. Rollback agar test tidak meninggalkan data
        # =========================================================
        koneksi.rollback()

        hasil_sesudah = koneksi.execute(
            """
            SELECT COUNT(*) AS total
            FROM audit
            """
        ).fetchone()

        jumlah_sesudah = hasil_sesudah["total"]

        print()
        print("Jumlah audit sesudah rollback :", jumlah_sesudah)

        if jumlah_sebelum == jumlah_sesudah:
            print("✅ Test tidak meninggalkan data")
        else:
            print("❌ Ada data testing yang tertinggal")

    finally:
        koneksi.close()


if __name__ == "__main__":
    tes_tambah_audit_baru()