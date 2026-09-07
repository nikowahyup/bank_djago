import datetime

from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.rekening import RekeningReguler
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.penyimpanan.repositories.riwayat_repository import (
    RiwayatRepository
)


def buat_riwayat(kategori, jenis, waktu, log):
    # Membuat dictionary riwayat sesuai format RiwayatTemplate.
    return {
        "kategori": kategori,
        "jenis": jenis,
        "waktu": waktu,
        "log": log
    }


def hapus_data_pengujian(daftar_nik, daftar_norek):
    koneksi = buat_koneksi()

    try:
        # Riwayat harus dihapus sebelum rekening karena memiliki foreign key.
        for norek in daftar_norek:
            koneksi.execute(
                """
                DELETE FROM riwayat
                WHERE norek = ?
                """,
                (norek,)
            )

        for norek in daftar_norek:
            koneksi.execute(
                """
                DELETE FROM rekening
                WHERE norek = ?
                """,
                (norek,)
            )

        for nik in daftar_nik:
            koneksi.execute(
                """
                DELETE FROM nasabah
                WHERE nik = ?
                """,
                (nik,)
            )

        koneksi.commit()

    finally:
        koneksi.close()


def uji_repository_riwayat():
    nik_pertama = "TEST-RIWAYAT-001"
    nik_kedua = "TEST-RIWAYAT-002"

    norek_pertama = "REKENING-RIWAYAT-001"
    norek_kedua = "REKENING-RIWAYAT-002"
    norek_tidak_terdaftar = "REKENING-TIDAK-TERDAFTAR"

    daftar_nik = [
        nik_pertama,
        nik_kedua
    ]

    daftar_norek = [
        norek_pertama,
        norek_kedua
    ]

    # Membersihkan sisa data jika pengujian pernah dijalankan.
    hapus_data_pengujian(daftar_nik, daftar_norek)

    try:
        nasabah_pertama = Nasabahh(
            nama="Nasabah Riwayat Pertama",
            alamat="Banyuwangi",
            nik=nik_pertama
        )

        nasabah_kedua = Nasabahh(
            nama="Nasabah Riwayat Kedua",
            alamat="Malang",
            nik=nik_kedua
        )

        rekening_pertama = RekeningReguler(
            norek=norek_pertama,
            pin="111111",
            pemilik=nasabah_pertama
        )

        rekening_kedua = RekeningReguler(
            norek=norek_kedua,
            pin="222222",
            pemilik=nasabah_kedua
        )

        # Membuat riwayat yang mencoba memakai rekening tidak terdaftar.
        riwayat_tanpa_rekening = buat_riwayat(
            kategori="transaksi",
            jenis="setor uang",
            waktu=datetime.datetime(2026, 8, 24, 8, 0, 0),
            log="SETOR UANG | +Rp1.000.000"
        )

        hasil_gagal = RiwayatRepository.tambah_riwayat(
            norek_tidak_terdaftar,
            riwayat_tanpa_rekening
        )

        assert hasil_gagal is None, (
            "Riwayat dengan rekening tidak terdaftar seharusnya ditolak"
        )

        print("✅ Riwayat tanpa rekening terdaftar berhasil ditolak")

        # Menyimpan nasabah sebelum rekening karena hubungan foreign key.
        assert NasabahRepository.tambah_nasabah(nasabah_pertama), (
            "Nasabah pertama gagal disimpan"
        )

        assert NasabahRepository.tambah_nasabah(nasabah_kedua), (
            "Nasabah kedua gagal disimpan"
        )

        print("✅ Dua nasabah pengujian berhasil disimpan")

        assert RekeningRepository.tambah_rekening(rekening_pertama), (
            "Rekening pertama gagal disimpan"
        )

        assert RekeningRepository.tambah_rekening(rekening_kedua), (
            "Rekening kedua gagal disimpan"
        )

        print("✅ Dua rekening pengujian berhasil disimpan")

        # Rekening pertama mempunyai tiga riwayat.
        riwayat_setor_pertama = buat_riwayat(
            kategori="transaksi",
            jenis="setor uang",
            waktu=datetime.datetime(2026, 8, 24, 8, 1, 0),
            log="SETOR UANG | +Rp2.000.000"
        )

        riwayat_transfer_pertama = buat_riwayat(
            kategori="transaksi",
            jenis="transfer",
            waktu=datetime.datetime(2026, 8, 24, 8, 2, 0),
            log="TRANSFER | -Rp500.000"
        )

        riwayat_pinjaman_pertama = buat_riwayat(
            kategori="transaksi",
            jenis="pinjaman",
            waktu=datetime.datetime(2026, 8, 24, 8, 3, 0),
            log="PEMBAYARAN CICILAN | Rp100.000"
        )

        # Rekening kedua mempunyai dua riwayat.
        riwayat_setor_kedua = buat_riwayat(
            kategori="transaksi",
            jenis="setor uang",
            waktu=datetime.datetime(2026, 8, 24, 8, 4, 0),
            log="SETOR UANG | +Rp3.000.000"
        )

        riwayat_transfer_kedua = buat_riwayat(
            kategori="transaksi",
            jenis="transfer",
            waktu=datetime.datetime(2026, 8, 24, 8, 5, 0),
            log="TRANSFER | -Rp750.000"
        )

        id_setor_pertama = RiwayatRepository.tambah_riwayat(
            norek_pertama,
            riwayat_setor_pertama
        )

        id_transfer_pertama = RiwayatRepository.tambah_riwayat(
            norek_pertama,
            riwayat_transfer_pertama
        )

        id_pinjaman_pertama = RiwayatRepository.tambah_riwayat(
            norek_pertama,
            riwayat_pinjaman_pertama
        )

        id_setor_kedua = RiwayatRepository.tambah_riwayat(
            norek_kedua,
            riwayat_setor_kedua
        )

        id_transfer_kedua = RiwayatRepository.tambah_riwayat(
            norek_kedua,
            riwayat_transfer_kedua
        )

        seluruh_id = {
            id_setor_pertama,
            id_transfer_pertama,
            id_pinjaman_pertama,
            id_setor_kedua,
            id_transfer_kedua
        }

        assert None not in seluruh_id, (
            "Ada riwayat yang gagal disimpan"
        )

        print("✅ Lima riwayat berhasil disimpan")

        assert len(seluruh_id) == 5, (
            "Setiap riwayat seharusnya mempunyai ID global berbeda"
        )

        print("✅ Seluruh riwayat mempunyai ID global berbeda")

        # Mengambil seluruh riwayat rekening pertama.
        hasil_pertama = RiwayatRepository.cari_seluruh_riwayat(
            norek_pertama
        )

        assert len(hasil_pertama) == 3, (
            "Rekening pertama seharusnya mempunyai tiga riwayat"
        )

        assert all(
            riwayat["norek"] == norek_pertama
            for riwayat in hasil_pertama
        ), "Riwayat rekening pertama tercampur"

        print("✅ Riwayat rekening pertama berhasil dipisahkan")

        # Mengambil seluruh riwayat rekening kedua.
        hasil_kedua = RiwayatRepository.cari_seluruh_riwayat(
            norek_kedua
        )

        assert len(hasil_kedua) == 2, (
            "Rekening kedua seharusnya mempunyai dua riwayat"
        )

        assert all(
            riwayat["norek"] == norek_kedua
            for riwayat in hasil_kedua
        ), "Riwayat rekening kedua tercampur"

        print("✅ Riwayat rekening kedua berhasil dipisahkan")

        # ORDER BY id DESC harus memberikan ID terbaru terlebih dahulu.
        id_hasil_pertama = [
            riwayat["id"]
            for riwayat in hasil_pertama
        ]

        assert id_hasil_pertama == [
            id_pinjaman_pertama,
            id_transfer_pertama,
            id_setor_pertama
        ], "Riwayat rekening pertama tidak diurutkan dari terbaru"

        id_hasil_kedua = [
            riwayat["id"]
            for riwayat in hasil_kedua
        ]

        assert id_hasil_kedua == [
            id_transfer_kedua,
            id_setor_kedua
        ], "Riwayat rekening kedua tidak diurutkan dari terbaru"

        print("✅ Riwayat berhasil diurutkan berdasarkan ID terbaru")

        # Mencari riwayat transfer milik rekening pertama.
        transfer_pertama = (
            RiwayatRepository.cari_riwayat_berdasarkan_jenis(
                norek_pertama,
                "transfer"
            )
        )

        assert len(transfer_pertama) == 1
        assert transfer_pertama[0]["id"] == id_transfer_pertama
        assert transfer_pertama[0]["norek"] == norek_pertama
        assert transfer_pertama[0]["jenis"] == "transfer"

        print("✅ Pencarian jenis riwayat rekening pertama berhasil")

        # Jenis yang sama milik rekening kedua harus tetap terpisah.
        transfer_kedua = (
            RiwayatRepository.cari_riwayat_berdasarkan_jenis(
                norek_kedua,
                "transfer"
            )
        )

        assert len(transfer_kedua) == 1
        assert transfer_kedua[0]["id"] == id_transfer_kedua
        assert transfer_kedua[0]["norek"] == norek_kedua

        print("✅ Pencarian jenis riwayat antar-rekening terisolasi")

        # Jenis yang tidak tersedia menghasilkan list kosong.
        jenis_tidak_ada = (
            RiwayatRepository.cari_riwayat_berdasarkan_jenis(
                norek_pertama,
                "deposito"
            )
        )

        assert jenis_tidak_ada == []

        # Nomor rekening yang tidak terdaftar juga menghasilkan list kosong.
        rekening_tidak_ada = (
            RiwayatRepository.cari_seluruh_riwayat(
                norek_tidak_terdaftar
            )
        )

        assert rekening_tidak_ada == []

        print("✅ Pencarian data tidak tersedia menghasilkan list kosong")
        print("✅ Repository riwayat bekerja sesuai rancangan")

    finally:
        # Data pengujian tetap dibersihkan ketika assert gagal.
        hapus_data_pengujian(daftar_nik, daftar_norek)


if __name__ == "__main__":
    uji_repository_riwayat()