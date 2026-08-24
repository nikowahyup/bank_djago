import datetime

from bank_djago.core.deposito import Deposito
from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.rekening import RekeningReguler
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.deposito_repository import (
    DepositoRepository
)
from bank_djago.penyimpanan.repositories.nasabah_repository import (
    NasabahRepository
)
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.utils.utility import JenisAro


NIK_PERTAMA = "TEST-DEPOSITO-NASABAH-1"
NIK_KEDUA = "TEST-DEPOSITO-NASABAH-2"

NOREK_PERTAMA = "REK-DEPOSITO-001"
NOREK_KEDUA = "REK-DEPOSITO-002"
NOREK_KETIGA = "REK-DEPOSITO-003"
NOREK_TIDAK_TERDAFTAR = "REK-DEPOSITO-TIDAK-ADA"


def bersihkan_data_uji():
    koneksi = buat_koneksi()

    try:
        # Deposito harus dihapus terlebih dahulu karena
        # mempunyai foreign key menuju rekening.
        koneksi.execute(
            """
            DELETE FROM deposito
            WHERE norek IN (?, ?, ?)
            """,
            (
                NOREK_PERTAMA,
                NOREK_KEDUA,
                NOREK_KETIGA
            )
        )

        # Rekening dihapus setelah seluruh deposito
        # yang menggunakannya sudah dihapus.
        koneksi.execute(
            """
            DELETE FROM rekening
            WHERE norek IN (?, ?, ?)
            """,
            (
                NOREK_PERTAMA,
                NOREK_KEDUA,
                NOREK_KETIGA
            )
        )

        # Nasabah menjadi data terakhir yang dihapus.
        koneksi.execute(
            """
            DELETE FROM nasabah
            WHERE nik IN (?, ?)
            """,
            (
                NIK_PERTAMA,
                NIK_KEDUA
            )
        )

        koneksi.commit()

    finally:
        koneksi.close()


def buat_data_uji():
    # Nasabah pertama mempunyai dua rekening.
    nasabah_pertama = Nasabahh(
        nama="Nasabah Deposito Pertama",
        alamat="Banyuwangi",
        nik=NIK_PERTAMA
    )

    rekening_pertama = RekeningReguler(
        norek=NOREK_PERTAMA,
        pin="111111",
        pemilik=nasabah_pertama
    )

    rekening_kedua = RekeningReguler(
        norek=NOREK_KEDUA,
        pin="222222",
        pemilik=nasabah_pertama
    )

    # Nasabah kedua mempunyai satu rekening.
    nasabah_kedua = Nasabahh(
        nama="Nasabah Deposito Kedua",
        alamat="Jember",
        nik=NIK_KEDUA
    )

    rekening_ketiga = RekeningReguler(
        norek=NOREK_KETIGA,
        pin="333333",
        pemilik=nasabah_kedua
    )

    tanggal_buka = datetime.date(2026, 8, 23)

    deposito_pertama = Deposito(
        pemilik=nasabah_pertama,
        rekening=rekening_pertama,
        nominal=1_000_000,
        bunga=0.03,
        id=1,
        lama_bulan=1,
        tanggal_buka=tanggal_buka,
        tanggal_jatuh_tempo=datetime.date(2026, 9, 23)
    )

    deposito_pertama.jenis_aro = JenisAro.TIDAK
    deposito_pertama.lama_aro = None
    deposito_pertama.proses_aro = None

    deposito_kedua = Deposito(
        pemilik=nasabah_pertama,
        rekening=rekening_pertama,
        nominal=3_000_000,
        bunga=0.035,
        id=2,
        lama_bulan=3,
        tanggal_buka=tanggal_buka,
        tanggal_jatuh_tempo=datetime.date(2026, 11, 23)
    )

    deposito_kedua.jenis_aro = JenisAro.POKOK
    deposito_kedua.lama_aro = 3
    deposito_kedua.proses_aro = datetime.date(2026, 8, 23)

    deposito_ketiga = Deposito(
        pemilik=nasabah_pertama,
        rekening=rekening_kedua,
        nominal=6_000_000,
        bunga=0.04,
        id=3,
        lama_bulan=6,
        tanggal_buka=tanggal_buka,
        tanggal_jatuh_tempo=datetime.date(2027, 2, 23)
    )

    deposito_ketiga.jenis_aro = JenisAro.POKOK_BUNGA
    deposito_ketiga.lama_aro = 6
    deposito_ketiga.proses_aro = None

    deposito_keempat = Deposito(
        pemilik=nasabah_kedua,
        rekening=rekening_ketiga,
        nominal=12_000_000,
        bunga=0.045,
        id=1,
        lama_bulan=12,
        tanggal_buka=tanggal_buka,
        tanggal_jatuh_tempo=datetime.date(2027, 8, 23)
    )

    deposito_keempat.jenis_aro = JenisAro.TIDAK
    deposito_keempat.lama_aro = None
    deposito_keempat.proses_aro = None

    return {
        "nasabah": [
            nasabah_pertama,
            nasabah_kedua
        ],
        "rekening": [
            rekening_pertama,
            rekening_kedua,
            rekening_ketiga
        ],
        "deposito": [
            deposito_pertama,
            deposito_kedua,
            deposito_ketiga,
            deposito_keempat
        ]
    }


def uji_repository_deposito():
    bersihkan_data_uji()

    data_uji = buat_data_uji()

    nasabah_pertama, nasabah_kedua = data_uji["nasabah"]

    (
        rekening_pertama,
        rekening_kedua,
        rekening_ketiga
    ) = data_uji["rekening"]

    (
        deposito_pertama,
        deposito_kedua,
        deposito_ketiga,
        deposito_keempat
    ) = data_uji["deposito"]

    try:
        # Deposito belum boleh disimpan karena rekening
        # dan nasabah pemilik belum tersimpan.
        hasil_tanpa_rekening = (
            DepositoRepository.tambah_deposito(
                deposito_pertama
            )
        )

        assert hasil_tanpa_rekening is None, (
            "Deposito tanpa rekening terdaftar seharusnya ditolak"
        )

        print("✅ Deposito tanpa rekening terdaftar berhasil ditolak")

        # Menyimpan kedua nasabah sebagai data induk.
        assert (
            NasabahRepository.tambah_nasabah(
                nasabah_pertama
            )
            is True
        )

        assert (
            NasabahRepository.tambah_nasabah(
                nasabah_kedua
            )
            is True
        )

        print("✅ Nasabah pengujian berhasil disimpan")

        # Menyimpan ketiga rekening setelah nasabah tersedia.
        assert (
            RekeningRepository.tambah_rekening(
                rekening_pertama
            )
            is True
        )

        assert (
            RekeningRepository.tambah_rekening(
                rekening_kedua
            )
            is True
        )

        assert (
            RekeningRepository.tambah_rekening(
                rekening_ketiga
            )
            is True
        )

        print("✅ Rekening pengujian berhasil disimpan")

        # Menyimpan deposito dan menerima ID global
        # yang dibuat oleh SQLite.
        id_pertama = DepositoRepository.tambah_deposito(
            deposito_pertama
        )

        id_kedua = DepositoRepository.tambah_deposito(
            deposito_kedua
        )

        id_ketiga = DepositoRepository.tambah_deposito(
            deposito_ketiga
        )

        id_keempat = DepositoRepository.tambah_deposito(
            deposito_keempat
        )

        seluruh_id = {
            id_pertama,
            id_kedua,
            id_ketiga,
            id_keempat
        }

        assert all(
            isinstance(id_deposito, int)
            for id_deposito in seluruh_id
        ), "Seluruh ID deposito seharusnya berupa integer"

        assert len(seluruh_id) == 4, (
            "Setiap deposito seharusnya mempunyai ID global berbeda"
        )

        print("✅ Empat deposito berhasil disimpan")
        print("✅ Seluruh deposito mempunyai ID global berbeda")

        # Mengambil tepat satu deposito menggunakan ID global.
        hasil_id = (
            DepositoRepository.cari_deposito_dengan_id(
                id_kedua
            )
        )

        assert hasil_id is not None
        assert hasil_id["id"] == id_kedua
        assert hasil_id["norek"] == NOREK_PERTAMA
        assert hasil_id["nominal"] == deposito_kedua.nominal
        assert hasil_id["bunga"] == deposito_kedua.bunga
        assert hasil_id["lama_bulan"] == deposito_kedua.lama_bulan
        assert hasil_id["status"] == deposito_kedua.status
        assert hasil_id["jenis_aro"] == deposito_kedua.jenis_aro
        assert hasil_id["lama_aro"] == deposito_kedua.lama_aro

        assert (
            hasil_id["tanggal_buka"]
            == deposito_kedua.tanggal_buka.isoformat()
        )

        assert (
            hasil_id["jatuh_tempo"]
            == deposito_kedua.jatuh_tempo.isoformat()
        )

        assert (
            hasil_id["proses_aro"]
            == deposito_kedua.proses_aro.isoformat()
        )

        print("✅ Pencarian deposito berdasarkan ID berhasil")

        # Rekening pertama mempunyai dua deposito.
        hasil_rekening_pertama = (
            DepositoRepository.cari_deposito_dengan_norek(
                NOREK_PERTAMA
            )
        )

        assert len(hasil_rekening_pertama) == 2, (
            "Rekening pertama seharusnya mempunyai dua deposito"
        )

        assert all(
            deposito["norek"] == NOREK_PERTAMA
            for deposito in hasil_rekening_pertama
        )

        print("✅ Pencarian deposito berdasarkan rekening berhasil")

        # Nasabah pertama mempunyai tiga deposito pada
        # dua rekening yang berbeda.
        hasil_nasabah_pertama = (
            DepositoRepository.cari_deposito_dengan_nik(
                NIK_PERTAMA
            )
        )

        assert len(hasil_nasabah_pertama) == 3, (
            "Nasabah pertama seharusnya mempunyai tiga deposito"
        )

        norek_deposito_nasabah = {
            deposito["norek"]
            for deposito in hasil_nasabah_pertama
        }

        assert norek_deposito_nasabah == {
            NOREK_PERTAMA,
            NOREK_KEDUA
        }, (
            "Pencarian NIK belum mencakup seluruh rekening nasabah"
        )

        print(
            "✅ Pencarian NIK mencakup deposito "
            "dari seluruh rekening nasabah"
        )

        # Nasabah kedua hanya mempunyai satu deposito.
        hasil_nasabah_kedua = (
            DepositoRepository.cari_deposito_dengan_nik(
                NIK_KEDUA
            )
        )

        assert len(hasil_nasabah_kedua) == 1
        assert hasil_nasabah_kedua[0]["id"] == id_keempat
        assert hasil_nasabah_kedua[0]["norek"] == NOREK_KETIGA

        print("✅ Deposito antar-nasabah berhasil dipisahkan")

        # Pencarian data yang tidak terdaftar.
        hasil_id_kosong = (
            DepositoRepository.cari_deposito_dengan_id(
                -999
            )
        )

        hasil_rekening_kosong = (
            DepositoRepository.cari_deposito_dengan_norek(
                NOREK_TIDAK_TERDAFTAR
            )
        )

        hasil_nasabah_kosong = (
            DepositoRepository.cari_deposito_dengan_nik(
                "NIK-TIDAK-TERDAFTAR"
            )
        )

        assert hasil_id_kosong is None
        assert hasil_rekening_kosong == []
        assert hasil_nasabah_kosong == []

        print("✅ Pencarian data tidak terdaftar menghasilkan data kosong")
        print("✅ Repository deposito bekerja sesuai rancangan")

    finally:
        bersihkan_data_uji()


if __name__ == "__main__":
    uji_repository_deposito()