# from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
#
#
# nasabah = NasabahLoader.muat_nasabah("1111222233334444")
#
# print("Jumlah notifikasi:", len(nasabah.notifikasi))
#
# for notifikasi in nasabah.notifikasi:
#     print("Jenis             :", notifikasi.jenis)
#     print("Pesan             :", notifikasi.pesan)
#     print("Jenis referensi   :", notifikasi.jenis_referensi)
#     print("ID objek          :", notifikasi.id_objek)
#     print()



import datetime

from bank_djago.penyimpanan.storage import JsonStorage
from bank_djago.penyimpanan.loaders.nasabah_loader import NasabahLoader
from bank_djago.penyimpanan.repositories.notifikasi_repository import (
    NotifikasiRepository
)
from bank_djago.services.scheduler import Scheduler
from bank_djago.services.deposito.deposito_service import (
    StatusDeposito
)
from bank_djago.core.deposito import JenisAro
from bank_djago.utils.utility import JenisReferensiID


NIK_PENGUJIAN = "1111222233334444"
JATUH_TEMPO = datetime.date(2026, 9, 29)
H_MINUS_4 = datetime.date(2026, 9, 25)
H_MINUS_3 = datetime.date(2026, 9, 26)


def cari_deposito_pengujian(nasabah):
    kandidat = [
        deposito
        for deposito in nasabah.deposito
        if (
            deposito.nominal == 10_000_000
            and deposito.jatuh_tempo == JATUH_TEMPO
            and deposito.jenis_aro == JenisAro.TIDAK
            and deposito.status == StatusDeposito.AKTIF
        )
    ]

    if not kandidat:
        raise ValueError("Deposito pengujian tidak ditemukan")

    # Ambil deposito terbaru jika ada lebih dari satu data yang cocok.
    return max(kandidat, key=lambda deposito: deposito.ID)


def ambil_notifikasi_deposito(id_deposito):
    semua_notifikasi = (
        NotifikasiRepository.cari_notifikasi_nasabah(
            NIK_PENGUJIAN
        )
    )

    return [
        data
        for data in semua_notifikasi
        if (
            data["jenis_referensi"]
            == JenisReferensiID.DEPOSITO.value
            and data["id_objek"] == id_deposito
        )
    ]


bank = JsonStorage.muat_bank()
nasabah = NasabahLoader.muat_nasabah(NIK_PENGUJIAN)
deposito = cari_deposito_pengujian(nasabah)

print("DATA DEPOSITO PENGUJIAN")
print("ID            :", deposito.ID)
print("Nominal       :", deposito.nominal)
print("Jenis ARO     :", deposito.jenis_aro)
print("Status        :", deposito.status)
print("Jatuh tempo   :", deposito.jatuh_tempo)


# --------------------------------------------------
# KONDISI AWAL
# --------------------------------------------------

notifikasi_awal = ambil_notifikasi_deposito(deposito.ID)

print("\nKONDISI AWAL")
print("Jumlah notifikasi deposito:", len(notifikasi_awal))

assert len(notifikasi_awal) == 0
print("✅ Belum ada notifikasi untuk deposito pengujian")


# --------------------------------------------------
# PENGUJIAN H-4
# --------------------------------------------------

Scheduler.jalankan(
    bank=bank,
    hari_ini=H_MINUS_4
)

notifikasi_h4 = ambil_notifikasi_deposito(deposito.ID)

print("\nSETELAH SCHEDULER H-4")
print("Tanggal pengujian :", H_MINUS_4)
print("Jumlah notifikasi :", len(notifikasi_h4))

assert len(notifikasi_h4) == 0
print("✅ H-4 belum menghasilkan reminder")


# --------------------------------------------------
# PENGUJIAN H-3
# --------------------------------------------------

Scheduler.jalankan(
    bank=bank,
    hari_ini=H_MINUS_3
)

notifikasi_h3 = ambil_notifikasi_deposito(deposito.ID)

print("\nSETELAH SCHEDULER H-3")
print("Tanggal pengujian :", H_MINUS_3)
print("Jumlah notifikasi :", len(notifikasi_h3))

assert len(notifikasi_h3) == 1
print("✅ H-3 menghasilkan tepat satu reminder")

print("Pesan:")
print(notifikasi_h3[0]["pesan"])


# --------------------------------------------------
# JALANKAN LAGI PADA HARI YANG SAMA
# --------------------------------------------------

Scheduler.jalankan(
    bank=bank,
    hari_ini=H_MINUS_3
)

notifikasi_h3_kedua = ambil_notifikasi_deposito(
    deposito.ID
)

print("\nSETELAH SCHEDULER H-3 DIJALANKAN LAGI")
print("Jumlah notifikasi :", len(notifikasi_h3_kedua))

assert len(notifikasi_h3_kedua) == 1
print("✅ Scheduler tidak menggandakan reminder")


# --------------------------------------------------
# UJI LOADER NOTIFIKASI
# --------------------------------------------------

nasabah_dimuat_ulang = NasabahLoader.muat_nasabah(
    NIK_PENGUJIAN
)

notifikasi_objek = [
    notifikasi
    for notifikasi in nasabah_dimuat_ulang.notifikasi
    if (
        notifikasi.jenis_referensi
        == JenisReferensiID.DEPOSITO
        and notifikasi.id_objek == deposito.ID
    )
]

assert len(notifikasi_objek) == 1
print("✅ Notifikasi berhasil dimuat kembali dari SQLite")

print("\n✅ Reminder H-3 non-ARO bekerja sesuai rancangan")


HARI_JATUH_TEMPO = datetime.date(2026, 9, 29)


def cari_deposito_dengan_id(nasabah, id_deposito):
    for deposito in nasabah.deposito:
        if deposito.ID == id_deposito:
            return deposito

    raise ValueError(
        f"Deposito dengan ID {id_deposito} tidak ditemukan"
    )


# Simpan ID karena objek deposito akan dimuat ulang.
id_deposito = deposito.ID


# --------------------------------------------------
# PENGUJIAN HARI JATUH TEMPO
# --------------------------------------------------

Scheduler.jalankan(
    bank=bank,
    hari_ini=HARI_JATUH_TEMPO
)

nasabah_setelah_jatuh_tempo = NasabahLoader.muat_nasabah(
    NIK_PENGUJIAN
)

deposito_setelah = cari_deposito_dengan_id(
    nasabah_setelah_jatuh_tempo,
    id_deposito
)

notifikasi_jatuh_tempo = ambil_notifikasi_deposito(
    id_deposito
)

print("\nSETELAH SCHEDULER HARI JATUH TEMPO")
print("Tanggal pengujian :", HARI_JATUH_TEMPO)
print("ID deposito       :", deposito_setelah.ID)
print("Status deposito   :", deposito_setelah.status)
print("Jumlah notifikasi :", len(notifikasi_jatuh_tempo))

assert (
    deposito_setelah.status
    == StatusDeposito.JATUH_TEMPO
)
print("✅ Status deposito berubah menjadi jatuh tempo")

assert len(notifikasi_jatuh_tempo) == 1
print("✅ Reminder lama berhasil diganti, bukan ditambah")

pesan_jatuh_tempo = notifikasi_jatuh_tempo[0]["pesan"]

print("Pesan:")
print(pesan_jatuh_tempo)

assert "telah jatuh tempo" in pesan_jatuh_tempo.lower()
assert "pencairan" in pesan_jatuh_tempo.lower()

print("✅ Pesan notifikasi meminta nasabah melakukan pencairan")


# --------------------------------------------------
# PENGECEKAN LOADER NOTIFIKASI
# --------------------------------------------------

notifikasi_objek = [
    notifikasi
    for notifikasi
    in nasabah_setelah_jatuh_tempo.notifikasi
    if (
        notifikasi.jenis_referensi
        == JenisReferensiID.DEPOSITO
        and notifikasi.id_objek == id_deposito
    )
]

assert len(notifikasi_objek) == 1
print("✅ Notifikasi jatuh tempo dimuat kembali dari SQLite")

assert (
    notifikasi_objek[0].pesan
    == pesan_jatuh_tempo
)
print("✅ Pesan objek sama dengan pesan yang tersimpan di SQLite")


# --------------------------------------------------
# JALANKAN SCHEDULER LAGI PADA TANGGAL SAMA
# --------------------------------------------------

Scheduler.jalankan(
    bank=bank,
    hari_ini=HARI_JATUH_TEMPO
)

notifikasi_setelah_scheduler_kedua = (
    ambil_notifikasi_deposito(id_deposito)
)

assert len(notifikasi_setelah_scheduler_kedua) == 1
print("✅ Scheduler kedua tidak menggandakan notifikasi")


print(
    "\n✅ Perubahan reminder menjadi notifikasi "
    "jatuh tempo bekerja sesuai rancangan"
)