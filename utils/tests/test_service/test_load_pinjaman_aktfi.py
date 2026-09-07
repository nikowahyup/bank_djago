import datetime

from bank_djago.penyimpanan.loaders.pinjaman_loader import (
    PinjamanLoader
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import (
    PinjamanRepository
)
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.utils.utility import StatusPinjaman, Utilitas


# Mengambil data mentah sebagai pembanding.
koneksi = buat_koneksi()

try:
    data_pinjaman_aktif = (
        PinjamanRepository.cari_semua_pinjaman_aktif(
            koneksi=koneksi
        )
    )
finally:
    koneksi.close()


# Memuat dan merangkai seluruh pinjaman aktif.
daftar_pinjaman = (
    PinjamanLoader.muat_semua_pinjaman_aktif()
)


if data_pinjaman_aktif is None:
    data_pinjaman_aktif = []

if daftar_pinjaman is None:
    raise AssertionError(
        "Loader sebaiknya mengembalikan list kosong, bukan None"
    )


print("=== HASIL LOADER PINJAMAN AKTIF ===")
print(
    "Jumlah data SQLite :",
    len(data_pinjaman_aktif)
)
print(
    "Jumlah objek       :",
    len(daftar_pinjaman)
)
print()


# Jumlah objek harus sama dengan jumlah baris dari SQLite.
assert (
    len(daftar_pinjaman)
    == len(data_pinjaman_aktif)
), (
    "Jumlah objek pinjaman tidak sama "
    "dengan jumlah data SQLite"
)


# Membuat indeks data mentah berdasarkan ID pinjaman.
data_index = {
    data["id"]: data
    for data in data_pinjaman_aktif
}

# Memastikan loader tidak menghasilkan ID ganda.
id_objek = [
    pinjaman.ID
    for pinjaman in daftar_pinjaman
]

assert len(id_objek) == len(set(id_objek)), (
    "Loader menghasilkan objek pinjaman dengan ID ganda"
)

assert set(id_objek) == set(data_index), (
    "ID pinjaman hasil loader tidak sesuai dengan SQLite"
)


# Digunakan untuk menguji apakah identitas objek dipakai kembali.
objek_nasabah_per_nik = {}
objek_rekening_per_norek = {}


for pinjaman in daftar_pinjaman:
    if pinjaman.ID not in data_index:
        raise AssertionError(
            f"Pinjaman ID {pinjaman.ID} tidak ditemukan "
            "pada data mentah"
        )

    data = data_index[pinjaman.ID]

    print(f"--- PINJAMAN ID {pinjaman.ID} ---")
    print("NIK pemilik      :", pinjaman.pemilik.NIK)
    print("Nama pemilik     :", pinjaman.pemilik.nama)
    print("Nomor rekening   :", pinjaman.rekening.norek)
    print(
        "Nominal pinjaman :",
        f"Rp{Utilitas.format_rupiah(
            pinjaman.nominal_pinjaman
        )}"
    )
    print("Tenor             :", pinjaman.tenor)
    print(
        "Bunga            :",
        f"{pinjaman.bunga * 100:.1f}% / tahun"
    )
    print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
    print(
        "Sisa pokok       :",
        f"Rp{Utilitas.format_rupiah(
            pinjaman.sisa_pokok
        )}"
    )
    print("Status            :", pinjaman.status.value)
    print("Tanggal cair      :", pinjaman.tanggal_pencairan)
    print("Jatuh tempo       :", pinjaman.tanggal_jatuh_tempo)
    print()

    # Repository hanya boleh memberikan pinjaman aktif.
    assert data["status"] == StatusPinjaman.AKTIF.value, (
        f"Repository memuat pinjaman ID {pinjaman.ID} "
        "yang tidak aktif"
    )

    assert pinjaman.status == StatusPinjaman.AKTIF, (
        f"Status objek pinjaman ID {pinjaman.ID} "
        "bukan aktif"
    )

    # Memeriksa hubungan dengan rekening.
    assert pinjaman.rekening.norek == data["norek"], (
        f"Rekening pinjaman ID {pinjaman.ID} tidak sesuai"
    )

    # Memeriksa hubungan dengan nasabah.
    assert pinjaman.pemilik.NIK == data["nik_pemilik"], (
        f"Pemilik pinjaman ID {pinjaman.ID} tidak sesuai"
    )

    # Pemilik rekening dan pemilik pinjaman harus merupakan
    # objek Python yang sama, bukan hanya memiliki NIK sama.
    assert pinjaman.rekening.pemilik is pinjaman.pemilik, (
        f"Pinjaman ID {pinjaman.ID} dan rekeningnya "
        "memakai objek nasabah yang berbeda"
    )

    # Hubungan balik nasabah -> rekening harus tersedia.
    assert any(
        rekening is pinjaman.rekening
        for rekening in pinjaman.pemilik.rekening
    ), (
        f"Rekening pinjaman ID {pinjaman.ID} "
        "belum dimasukkan ke daftar rekening nasabah"
    )

    # Hubungan balik nasabah -> pinjaman juga harus tersedia.
    assert any(
        data_pinjaman is pinjaman
        for data_pinjaman
        in pinjaman.pemilik.daftar_pinjaman
    ), (
        f"Pinjaman ID {pinjaman.ID} belum dimasukkan "
        "ke daftar pinjaman nasabah"
    )

    # Memeriksa state utama pinjaman.
    assert (
        pinjaman.nominal_pinjaman
        == data["nominal_pinjaman"]
    ), f"Nominal pinjaman ID {pinjaman.ID} tidak sesuai"

    assert pinjaman.bunga == data["bunga"], (
        f"Bunga pinjaman ID {pinjaman.ID} tidak sesuai"
    )

    assert pinjaman.tenor == data["tenor"], (
        f"Tenor pinjaman ID {pinjaman.ID} tidak sesuai"
    )

    assert (
        pinjaman.cicilan_tetap
        == data["cicilan_tetap"]
    ), f"Cicilan tetap pinjaman ID {pinjaman.ID} tidak sesuai"

    assert (
        pinjaman.cicilan_terbayar
        == data["cicilan_terbayar"]
    ), f"Cicilan terbayar pinjaman ID {pinjaman.ID} tidak sesuai"

    assert pinjaman.sisa_pokok == data["sisa_pokok"], (
        f"Sisa pokok pinjaman ID {pinjaman.ID} tidak sesuai"
    )

    # Pinjaman aktif seharusnya sudah pernah dicairkan
    # dan memiliki jadwal pembayaran.
    tanggal_pencairan = datetime.date.fromisoformat(
        data["tanggal_pencairan"]
    )

    tanggal_jatuh_tempo = datetime.date.fromisoformat(
        data["tanggal_jatuh_tempo"]
    )

    assert (
        pinjaman.tanggal_pencairan
        == tanggal_pencairan
    ), f"Tanggal pencairan pinjaman ID {pinjaman.ID} tidak sesuai"

    assert (
        pinjaman.tanggal_jatuh_tempo
        == tanggal_jatuh_tempo
    ), f"Jatuh tempo pinjaman ID {pinjaman.ID} tidak sesuai"

    # Mengumpulkan identitas objek berdasarkan identitas database.
    objek_nasabah_per_nik.setdefault(
        pinjaman.pemilik.NIK,
        set()
    ).add(id(pinjaman.pemilik))

    objek_rekening_per_norek.setdefault(
        pinjaman.rekening.norek,
        set()
    ).add(id(pinjaman.rekening))


# Satu NIK harus selalu menunjuk satu objek nasabah.
for nik, kumpulan_objek in objek_nasabah_per_nik.items():
    assert len(kumpulan_objek) == 1, (
        f"Nasabah {nik} dirangkai menjadi "
        f"{len(kumpulan_objek)} objek berbeda"
    )


# Satu nomor rekening harus selalu menunjuk satu objek rekening.
for norek, kumpulan_objek in objek_rekening_per_norek.items():
    assert len(kumpulan_objek) == 1, (
        f"Rekening {norek} dirangkai menjadi "
        f"{len(kumpulan_objek)} objek berbeda"
    )


print("=== PEMERIKSAAN IDENTITAS OBJEK ===")

for nik, kumpulan_objek in objek_nasabah_per_nik.items():
    print(
        f"NIK {nik} | "
        f"Jumlah objek nasabah: {len(kumpulan_objek)}"
    )

for norek, kumpulan_objek in objek_rekening_per_norek.items():
    print(
        f"Rekening {norek} | "
        f"Jumlah objek rekening: {len(kumpulan_objek)}"
    )


print()
print(
    "✅ LOADER PINJAMAN AKTIF BERHASIL: "
    "jumlah data sesuai, seluruh state berhasil dirangkai, "
    "hubungan nasabah-rekening-pinjaman konsisten, "
    "serta identitas objek tidak digandakan"
)