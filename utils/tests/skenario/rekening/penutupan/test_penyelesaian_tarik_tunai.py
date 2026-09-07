"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_penutupan.py` (urutan 1).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
    PengajuanRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository)
# # )
# #
# #
# # id_pengajuan = 6
# # norek = "3001327791680308"
# #
# # koneksi = buat_koneksi()
# #
# # try:
# #     pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
# #         id_pengajuan=id_pengajuan,
# #         koneksi=koneksi
# #     )
# #
# #     rekening = RekeningRepository.cari_rekening_dengan_norek(
# #         norek=norek,
# #         koneksi=koneksi
# #     )
# #
# #     if pengajuan is None:
# #         raise ValueError("Pengajuan tidak ditemukan")
# #
# #     if rekening is None:
# #         raise ValueError("Rekening tidak ditemukan")
# #
# #     print("=== DATA PENGAJUAN ===")
# #     print(f"ID pengajuan      : {pengajuan['id']}")
# #     print(f"Nomor rekening    : {pengajuan['norek']}")
# #     print(f"Jenis             : {pengajuan['jenis']}")
# #     print(f"Alasan            : {pengajuan['alasan']}")
# #     print(f"Status            : {pengajuan['status']}")
# #     print(f"Waktu pengajuan   : {pengajuan['waktu_pengajuan']}")
# #     print(f"Waktu diproses    : {pengajuan['waktu_diproses']}")
# #     print(f"Catatan admin     : {pengajuan['catatan_admin']}")
# #
# #     print("\n=== DATA REKENING ===")
# #     print(f"Nomor rekening    : {rekening['norek']}")
# #     print(f"Saldo             : {rekening['saldo']}")
# #     print(f"Status rekening   : {rekening['status']}")
# #
# #     assert pengajuan["status"] == "disetujui"
# #     assert pengajuan["waktu_diproses"] is not None
# #     assert pengajuan["catatan_admin"] is not None
# #
# #     # Persetujuan belum boleh langsung menutup rekening.
# #     assert rekening["saldo"] == 10_000_000
# #     assert rekening["status"] == "aktif"
# #
# #     print("\n✅ Persetujuan penutupan tersimpan dengan benar")
# #
# # finally:
# #     koneksi.close()
#
#
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
#
#
# norek = "3001327791680308"
# saldo_awal = 10_000_000
#
# koneksi = buat_koneksi()
#
# try:
#     # 1. Periksa rekening
#     rekening = koneksi.execute(
#         """
#         SELECT *
#         FROM rekening
#         WHERE norek = ?
#         """,
#         (norek,)
#     ).fetchone()
#
#     if rekening is None:
#         raise ValueError("Rekening tidak ditemukan")
#
#     # 2. Cari transaksi penutupan terbaru
#     transaksi = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE norek_sumber = ?
#           AND jenis = 'penarikan_saldo_penutupan'
#         ORDER BY id DESC
#         LIMIT 1
#         """,
#         (norek,)
#     ).fetchone()
#
#     if transaksi is None:
#         raise ValueError(
#             "Transaksi penarikan saldo penutupan tidak ditemukan"
#         )
#
#     id_transaksi = transaksi["id"]
#
#     # 3. Cari riwayat yang terhubung
#     daftar_riwayat = koneksi.execute(
#         """
#         SELECT *
#         FROM riwayat
#         WHERE transaksi_id = ?
#         ORDER BY id ASC
#         """,
#         (id_transaksi,)
#     ).fetchall()
#
#     # 4. Cari audit yang terhubung
#     daftar_audit = koneksi.execute(
#         """
#         SELECT *
#         FROM audit
#         WHERE transaksi_id = ?
#         ORDER BY id ASC
#         """,
#         (id_transaksi,)
#     ).fetchall()
#
#     print("=== DATA REKENING ===")
#     print(f"Nomor rekening       : {rekening['norek']}")
#     print(f"Saldo                : {rekening['saldo']}")
#     print(f"Status               : {rekening['status']}")
#
#     print("\n=== DATA TRANSAKSI ===")
#     print(f"ID transaksi         : {transaksi['id']}")
#     print(f"Jenis                : {transaksi['jenis']}")
#     print(f"Rekening sumber      : {transaksi['norek_sumber']}")
#     print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
#     print(f"Nominal              : {transaksi['nominal']}")
#     print(
#         f"Saldo sumber sebelum : "
#         f"{transaksi['saldo_sumber_sebelum']}"
#     )
#     print(
#         f"Saldo sumber sesudah : "
#         f"{transaksi['saldo_sumber_sesudah']}"
#     )
#     print(f"Waktu                : {transaksi['waktu']}")
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
#     # Pemeriksaan otomatis rekening
#     assert rekening["saldo"] == 0
#     assert rekening["status"] == "tutup"
#
#     # Pemeriksaan otomatis transaksi
#     assert transaksi["jenis"] == (
#         "penarikan_saldo_penutupan"
#     )
#     assert transaksi["norek_sumber"] == norek
#     assert transaksi["norek_tujuan"] is None
#     assert transaksi["nominal"] == saldo_awal
#     assert transaksi["saldo_sumber_sebelum"] == saldo_awal
#     assert transaksi["saldo_sumber_sesudah"] == 0
#     assert transaksi["saldo_tujuan_sebelum"] is None
#     assert transaksi["saldo_tujuan_sesudah"] is None
#
#     # Metode tarik menghasilkan satu riwayat dan satu audit
#     assert len(daftar_riwayat) == 1
#     assert len(daftar_audit) == 1
#
#     assert daftar_riwayat[0]["transaksi_id"] == id_transaksi
#     assert daftar_audit[0]["transaksi_id"] == id_transaksi
#
#     print(
#         "\n✅ Penutupan dengan metode tarik "
#         "tersimpan dengan benar"
#     )
#
# finally:
#     koneksi.close()
# from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
#
# koneksi = buat_koneksi()
#
# rekening = RekeningRepository.cari_rekening_dengan_norek("2001842427316253")
#
# print(f'saldo ',rekening["saldo"])


id_pengajuan = 7
norek = "3001327791680308"

koneksi = buat_koneksi()

try:
    pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
        id_pengajuan=id_pengajuan,
        koneksi=koneksi
    )

    rekening = RekeningRepository.cari_rekening_dengan_norek(
        norek=norek,
        koneksi=koneksi
    )

    if pengajuan is None:
        raise ValueError("Pengajuan tidak ditemukan")

    if rekening is None:
        raise ValueError("Rekening tidak ditemukan")

    print("=== DATA PENGAJUAN ===")
    print(f"ID pengajuan      : {pengajuan['id']}")
    print(f"Nomor rekening    : {pengajuan['norek']}")
    print(f"Jenis             : {pengajuan['jenis']}")
    print(f"Alasan            : {pengajuan['alasan']}")
    print(f"Status            : {pengajuan['status']}")
    print(f"Waktu pengajuan   : {pengajuan['waktu_pengajuan']}")
    print(f"Waktu diproses    : {pengajuan['waktu_diproses']}")
    print(f"Catatan admin     : {pengajuan['catatan_admin']}")

    print("\n=== DATA REKENING ===")
    print(f"Nomor rekening    : {rekening['norek']}")
    print(f"Saldo             : {rekening['saldo']}")
    print(f"Status rekening   : {rekening['status']}")

    assert pengajuan["status"] == "disetujui"
    assert pengajuan["waktu_diproses"] is not None
    assert pengajuan["catatan_admin"] is not None

    # Persetujuan belum boleh langsung menutup rekening.
    assert rekening["saldo"] == 1000
    assert rekening["status"] == "aktif"

    print("\n✅ Persetujuan penutupan tersimpan dengan benar")

finally:
    koneksi.close()
