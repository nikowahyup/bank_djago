from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.utils.utility import Utilitas
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository

data_rekening = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")

if data_rekening:
    for data in data_rekening:
        print(data["norek"])
        print(data["nik_pemilik"])
        print("Rp",Utilitas.format_rupiah(data["saldo"]))
        print(data["level"])
        print(data["status"])


print()

sesudah = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")

# # if sesudah:
# #     print("Sesudah")
# #     for data in sesudah:
# #         print(data["saldo"])
#
#
# print("sebelum")
#
# riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     "2001934876207884"
# )
#
# audit = AuditRepository.cari_audit_dengan_norek(
#     "2001934876207884"
# )
#
#
#
# if riwayat:
#     print("jumlah riwayat    :", len(riwayat))
#
# if audit:
#
#     print("Jumlah audit  :", len(audit))
#
# print("sesudah")
#
# rekening = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
# riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     "2001934876207884"
# )
#
# audit = AuditRepository.cari_audit_dengan_norek(
#     "2001934876207884"
# )
#
#
# if riwayat:
#     print("jumlah riwayat    :", len(riwayat))
#
# if audit:
#     print("Jumlah audit  :", len(audit))
#
# for data in rekening:
#     print("uang setelah pengujian",data["saldo"])



# rekening = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
# riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     "2001934876207884"
# )
#
# audit = AuditRepository.cari_audit_dengan_norek(
#     "2001934876207884"
# )
#
#
# if riwayat:
#     print("jumlah riwayat    :", len(riwayat))
#
# if audit:
#     print("Jumlah audit  :", len(audit))
#
# for data in rekening:
#     print("uang setelah pengujian",data["saldo"])



# rekening = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
# riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     "2001934876207884"
# )
#
# audit = AuditRepository.cari_audit_dengan_norek(
#     "2001934876207884"
# )
#
#
# if riwayat:
#     print("jumlah riwayat    :", len(riwayat))
#
# if audit:
#     print("Jumlah audit  :", len(audit))
#
# for data in rekening:
#     print("uang setelah pengujian",data["saldo"])




# rekening = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
# riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     "2001934876207884"
# )
#
# audit = AuditRepository.cari_audit_dengan_norek(
#     "2001934876207884"
# )
#
#
# if riwayat:
#     print("jumlah riwayat    :", len(riwayat))
#
# if audit:
#     print("Jumlah audit  :", len(audit))
#
# for data in rekening:
#     print("uang setelah pengujian",data["saldo"])



# rekening = RekeningRepository.cari_rekening_dengan_nik("9999999999999999")
# riwayat = RiwayatRepository.cari_seluruh_riwayat(
#     "2001934876207884"
# )
#
# audit = AuditRepository.cari_audit_dengan_norek(
#     "2001934876207884"
# )
#
#
# if riwayat:
#     print("jumlah riwayat    :", len(riwayat))
#
# if audit:
#     print("Jumlah audit  :", len(audit))
#
# for data in rekening:
#     print("uang setelah pengujian",data["saldo"])




# nasabah = NasabahRepository.cari_nasabah_dengan_nik("2222333344445555")
#
# rekening = RekeningRepository.cari_rekening_dengan_nik("2222333344445555")
#
# print(f"nama : {nasabah["nama"]}")
# print(f"nama : {nasabah["alamat"]}")
# print(f"nama : {nasabah["nik"]}")
#
#
# for data in rekening:
#     print(f'norek :{data["norek"]}')
#     print(f'saldo :{data["saldo"]}')
#     print(f'level :{data["level"]}')
#     print(f'status :{data["status"]}')

from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository


NOREK = "4001518075450587"

data_rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(NOREK)
daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)

if data_rekening is None:
    raise AssertionError("Rekening tidak ditemukan")

print("STATE REKENING SETELAH DOWNGRADE")
print("Norek                   :", data_rekening["norek"])
print("Level                   :", data_rekening["level"])
print("Saldo                   :", data_rekening["saldo"])
print("Status                  :", data_rekening["status"])
print("Limit tersisa           :", data_rekening["limit_sisa"])
print("Reset                   :", data_rekening["reset"])
print("Dapat bunga             :", data_rekening["dapat_bunga"])
print("Waktu bayar admin       :", data_rekening["waktu_bayar_admin"])
print("Terakhir ubah rekening  :", data_rekening["terakhir_ubah_rekening"])

print()
print("RIWAYAT TERBARU")

if daftar_riwayat:
    riwayat_terbaru = daftar_riwayat[0]

    print("Kategori :", riwayat_terbaru["kategori"])
    print("Jenis    :", riwayat_terbaru["jenis"])
    print("Waktu    :", riwayat_terbaru["waktu"])
    print("Log      :", riwayat_terbaru["log"])
else:
    print("Riwayat tidak ditemukan")

print()
print("AUDIT TERBARU")

if daftar_audit:
    audit_terbaru = daftar_audit[0]

    print("Kategori :", audit_terbaru["kategori"])
    print("Jenis    :", audit_terbaru["jenis"])
    print("Waktu    :", audit_terbaru["waktu"])
    print("Log      :", audit_terbaru["log"])
    print("Nama     :", audit_terbaru["nama"])
    print("NIK      :", audit_terbaru["nik"])
    print("Norek    :", audit_terbaru["norek"])
else:
    print("Audit tidak ditemukan")

assert data_rekening["norek"] == NOREK
assert data_rekening["level"] == 1
assert data_rekening["saldo"] == 10_000_000
assert data_rekening["limit_sisa"] == 5_000_000
assert data_rekening["status"] == "aktif"

assert daftar_riwayat
assert daftar_audit

assert daftar_riwayat[0]["jenis"] == "perubahan"
assert "Prioritas" in daftar_riwayat[0]["log"]
assert "Reguler" in daftar_riwayat[0]["log"]

assert daftar_audit[0]["jenis"] == "downgrade"
assert daftar_audit[0]["norek"] == NOREK

print()
print("✅ Seluruh state rekening sesuai setelah downgrade")
print("✅ Riwayat dan audit downgrade berhasil disimpan")

# daftar_audit = AuditRepository.cari_audit_dengan_nik(
#     "2222333344445555"
# )
#
# print("Jumlah audit:", len(daftar_audit))
#
# for nomor, audit in enumerate(daftar_audit, start=1):
#     print()
#     print(f"AUDIT KE-{nomor}")
#     print("Kategori :", audit["kategori"])
#     print("Jenis    :", audit["jenis"])
#     print("Log      :", audit["log"])
#     print("Nama     :", audit["nama"])
#     print("NIK      :", audit["nik"])
#     print("Norek    :", audit["norek"])



import datetime

from bank_djago.penyimpanan.sqlite.database import buat_koneksi


NOREK = "4001518075450587"
KEMARIN = datetime.date.today() - datetime.timedelta(days=1)

koneksi = buat_koneksi()

try:
    koneksi.execute(
        """
        UPDATE rekening
        SET terakhir_ubah_rekening = ?
        WHERE norek = ?
        """,
        (KEMARIN.isoformat(), NOREK)
    )
    koneksi.commit()
finally:
    koneksi.close()

print("Tanggal perubahan rekening dimundurkan ke:", KEMARIN)