import datetime


import pytest

from bank_djago import DepositoService, JenisAro
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis
from bank_djago.services.deposito.deposito_service import StatusDeposito
from bank_djago.services.exceptions import (
    NikTidakSesuai,
    RekeningTidakDitemukan,
    StatusTidakValid,
    InputTidakValid,
    JenisAroTidakValid,
    RekeningTidakSesuai,
    DepositoTidakDitemukan,
    PerbaruiStatusGagal,
    PenambahanSaldoGagal,
)
import bank_djago.penyimpanan.repositories.riwayat_repository as riwayat_repo_module
import bank_djago.penyimpanan.repositories.deposito_repository as deposito_repo_module
import bank_djago.penyimpanan.repositories.rekening_repository as rekening_repo_module
from bank_djago.services.scheduler import Scheduler


class TestBukaDeposito:

    def test_buka_deposito_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        DepositoService.buka_deposito(
            nik=nik,
            norek=norek,
            nominal=1_000_000,
            lama_bulan=3,
            jenis_aro=JenisAro.TIDAK,
            lama_aro=None,
        )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        assert saldo_sesudah == saldo_sebelum - 1_000_000
        assert data_deposito is not None
        assert data_deposito["norek"] == norek
        assert data_deposito["jenis_aro"] == JenisAro.TIDAK
        assert data_deposito["status"] == StatusDeposito.AKTIF
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["lama_bulan"] == 3
        assert data_deposito["lama_aro"] is None

    def test_buka_deposito_dengan_nik_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = "8812"
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(NikTidakSesuai) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=1_000_000,
                lama_bulan=3,
                jenis_aro=JenisAro.TIDAK,
                lama_aro=None,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        assert "NIK ini tidak terdaftar" in str(info_error.value)

    def test_buka_deposito_dengan_norek_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = "000"
        norek_asli = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=1_000_000,
                lama_bulan=3,
                jenis_aro=JenisAro.TIDAK,
                lama_aro=None,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        assert "tidak terdaftar" in str(info_error.value)

    def test_buka_deposito_dengan_nominal_diatas_minimal_saldo(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=10_000_000,
                lama_bulan=3,
                jenis_aro=JenisAro.TIDAK,
                lama_aro=None,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        assert "Saldo rekening akan kurang" in str(info_error.value)

    def test_buka_deposito_dengan_lama_bulan_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=10_000_000,
                lama_bulan=5,
                jenis_aro=JenisAro.TIDAK,
                lama_aro=None,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        assert "waktu deposito tidak tersedia" in str(info_error.value)

    def test_buka_deposito_dengan_jenis_aro_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(JenisAroTidakValid) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=10_000_000,
                lama_bulan=3,
                jenis_aro="jenis apa saja",
                lama_aro=None,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()
        print(f"pesan error ; {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        assert " tidak tersedia" in str(info_error.value)

    def test_buka_deposito_non_aro_tapi_ada_lama_aronya(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=10_000_000,
                lama_bulan=3,
                jenis_aro=JenisAro.TIDAK,
                lama_aro=3,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()
        print(f"pesan error ; {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"

        print(f"pesan error : {info_error.value}")
        assert "membutuhkan lama perpanjangan" in str(info_error.value)

    def test_buka_deposito_aro_tapi_lama_aronya_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(JenisAroTidakValid) as info_error:
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=10_000_000,
                lama_bulan=3,
                jenis_aro=JenisAro.POKOK,
                lama_aro=2,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()
        print(f"pesan error ; {info_error.value}")
        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"

        print(f"pesan error : {info_error.value}")
        assert "perpanjangan tidak tersedia" in str(info_error.value)

    def test_rollback_deposito_saat_hampir_saja_selesai_dibuat(
        self, koneksi_test, monkeypatch, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        tambah_method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def tambah_riwyat_lalu_gagal(**kwargs):
            tambah_method_asli(**kwargs)
            raise RuntimeError("Simulasi gagal setelah riwayat tersimpan")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository,
            "tambah_riwayat",
            tambah_riwyat_lalu_gagal,
        )

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(RuntimeError):
            DepositoService.buka_deposito(
                nik=nik,
                norek=norek,
                nominal=1_000_000,
                lama_bulan=1,
                jenis_aro=JenisAro.TIDAK,
                lama_aro=None,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        deposito_baru = koneksi_test.execute(
            """SELECT COUNT (*) AS jumlah FROM deposito WHERE norek = ?""",
            (norek,),
        ).fetchone()

        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"

        assert deposito_baru["jumlah"] == 0, "seharusnya tidak ada deposito yang dibuat"


class TestCairkanDeposito:

    @pytest.fixture
    def deposito_siap_dicairkan(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        koneksi_test.execute(
            """INSERT INTO deposito
        (id,norek,nominal, bunga, lama_bulan,tanggal_buka, jatuh_tempo, status)
         VALUES (?,?,?,?,?,?,?,?)""",
            (
                1,
                "123456",
                1_000_000,
                0.03,
                1,
                "2026-09-23",
                "2026-10-23",
                StatusDeposito.JATUH_TEMPO,
            ),
        )

        koneksi_test.commit()

        return {"id_deposito": 1}

    def test_cairkan_deposito_happy_path(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = datetime.date(2026, 10, 24)

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        DepositoService.cairkan_deposito(
            nik=nik,
            norek_pencairan=norek,
            id_deposito=id_deposito,
            hari_ini=hari_ini,
        )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        assert data_deposito is not None
        assert data_deposito["norek"] == norek
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["status"] == StatusDeposito.DICAIRKAN
        assert saldo_sesudah == saldo_sebelum + 1_002_500

    def test_cairkan_deposito_belum_jatuh_tempo(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        koneksi_test.execute(
            "UPDATE deposito SET status = 'aktif' WHERE id = ?", (id_deposito,)
        )
        koneksi_test.commit()
        hari_ini = datetime.date(2026, 10, 20)

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.AKTIF
        assert saldo_sesudah == saldo_sebelum
        assert "tidak dapat dicairkan" in str(info_error.value)

    def test_cairkan_deposito_tepat_jatuh_tempo(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        DepositoService.cairkan_deposito(
            nik=nik,
            norek_pencairan=norek,
            id_deposito=id_deposito,
            hari_ini=hari_ini,
        )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        assert data_deposito is not None
        assert data_deposito["norek"] == norek
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["status"] == StatusDeposito.DICAIRKAN
        assert saldo_sesudah == saldo_sebelum + 1_002_500

    def test_cairkan_deposito_dengan_nik_salah(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = "87654"
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(NikTidakSesuai) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.JATUH_TEMPO
        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "NIK ini tidak terdaftar" in str(info_error.value)

    def test_cairkan_deposito_dengan_norek_salah(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = "5678"
        norek_asli = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )
        with pytest.raises(RekeningTidakSesuai) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.JATUH_TEMPO
        assert saldo_sesudah == saldo_sebelum

        print(f"pesan error : {info_error.value}")
        assert "ini tidak terdaftar" in str(info_error.value)

    def test_cairkan_deposito_id_deposito_berupa_huruf(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = "abc"
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.JATUH_TEMPO
        assert saldo_sesudah == saldo_sebelum

        print(f"pesan error : {info_error.value}")
        assert "berupa angka" in str(info_error.value)

    def test_cairkan_deposito_id_deposito_berupa_negatif(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):
        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = -9
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.JATUH_TEMPO
        assert saldo_sesudah == saldo_sebelum

        print(f"pesan error : {info_error.value}")
        assert "tidak valid" in str(info_error.value)

    def test_cairkan_deposito_id_deposito_tidak_terdaftar(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = 99
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(DepositoTidakDitemukan) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.JATUH_TEMPO
        assert saldo_sesudah == saldo_sebelum

        print(f"pesan error : {info_error.value}")
        assert "tidak ditemukan" in str(info_error.value)

    @pytest.mark.parametrize("status_salah", ["aktif", "dicairkan"])
    def test_cairkan_deposito_dengan_status_selain_jatuh_tempo(
        self,
        koneksi_test,
        status_salah,
        siapkan_data_rekening_dan_nasabah,
        deposito_siap_dicairkan,
    ):
        id_deposito = deposito_siap_dicairkan["id_deposito"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]

        koneksi_test.execute(
            "UPDATE deposito SET status = ? WHERE id = ?", (status_salah, id_deposito)
        )
        koneksi_test.commit()

        hari_ini = datetime.date(2026, 10, 23)

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert saldo_sesudah == saldo_sebelum

        print(f"pesan error : {info_error.value}")
        assert "tidak dapat dicairkan" in str(info_error.value)

    @pytest.mark.parametrize("status_rekening_salah", ["blokir", "tutup"])
    def test_cairkan_deposito_rekening_tidak_aktif(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_siap_dicairkan,
        status_rekening_salah,
    ):

        koneksi_test.execute(
            """UPDATE rekening SET status = ? WHERE norek = ?""",
            (status_rekening_salah, siapkan_data_rekening_dan_nasabah["norek"]),
        )
        koneksi_test.commit()

        hari_ini = datetime.date(2026, 10, 23)

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        print(f"pesan error : {info_error.value}")
        assert data_deposito is not None
        assert data_deposito["status"] == StatusDeposito.JATUH_TEMPO
        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error: {info_error.value}")

    def test_rollback_pencairan_deposito(
        self,
        koneksi_test,
        deposito_siap_dicairkan,
        siapkan_data_rekening_dan_nasabah,
        monkeypatch,
    ):

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def method_untuk_uji_rollback(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulai rollback pencairan deposito")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository,
            "tambah_riwayat",
            method_untuk_uji_rollback,
        )

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(RuntimeError):
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=datetime.date(2026, 10, 24),
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )
        status = data_deposito["status"]

        assert saldo_sesudah == saldo_sebelum, "saldo seharusnya tidak bertambah"
        assert (
            status == StatusDeposito.JATUH_TEMPO
        ), "status seharusnya masih jatuh tempo"

    def test_cairkan_deposito_dalam_race_condition(
        self,
        koneksi_test,
        deposito_siap_dicairkan,
        siapkan_data_rekening_dan_nasabah,
        monkeypatch,
    ):

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        method_asli = deposito_repo_module.DepositoRepository.perbarui_status_deposito

        def method_penggagal_perbarui_status(**kwargs):

            koneksi_test.execute(
                """UPDATE deposito SET status = ?
                WHERE id = ?""",
                (StatusDeposito.DICAIRKAN, deposito_siap_dicairkan["id_deposito"]),
            )
            koneksi_test.commit()
            return method_asli(**kwargs)

        monkeypatch.setattr(
            deposito_repo_module.DepositoRepository,
            "perbarui_status_deposito",
            method_penggagal_perbarui_status,
        )

        with pytest.raises(PerbaruiStatusGagal):
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=datetime.date(2026, 10, 24),
            )

    def test_cairkan_deposito_dua_kali(
        self, deposito_siap_dicairkan, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        hari_ini = datetime.date(2026, 10, 23)

        DepositoService.cairkan_deposito(
            nik=nik, norek_pencairan=norek, id_deposito=id_deposito, hari_ini=hari_ini
        )

        saldo_setelah_pencairan_pertama = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        data_deposito_pencairan_pertama = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )
        status_setelah_pencairan_pertama = data_deposito_pencairan_pertama["status"]

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )

        saldo_setelah_pencairan_kedua = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        print(f"pesan error : {info_error.value}")
        assert saldo_setelah_pencairan_kedua == saldo_setelah_pencairan_pertama
        assert status_setelah_pencairan_pertama == StatusDeposito.DICAIRKAN
        assert "tidak dapat dicairkan" in str(info_error.value)

    @pytest.mark.skip(
        reason="saldo_lama dihapus dari tambah_saldo, skenario ini perlu didesain ulang"
    )
    def test_cairkan_deposito_gagal_karena_saldo_berubah_saat_proses(
        self, koneksi_test, deposito_siap_dicairkan, monkeypatch
    ):
        method_asli = rekening_repo_module.RekeningRepository.tambah_saldo

        def ubah_saldo_lalu_panggil_asli(**kwargs):
            # simulasikan race condition: saldo berubah duluan oleh proses lain
            koneksi_test.execute(
                "UPDATE rekening SET saldo = saldo + ? WHERE norek = ?",
                (500_000, deposito_siap_dicairkan["norek"]),
            )
            koneksi_test.commit()

            return method_asli(**kwargs)

        monkeypatch.setattr(
            rekening_repo_module.RekeningRepository,
            "tambah_saldo",
            ubah_saldo_lalu_panggil_asli,
        )

        with pytest.raises(PenambahanSaldoGagal):
            DepositoService.cairkan_deposito(
                nik=deposito_siap_dicairkan["nik"],
                norek_pencairan=deposito_siap_dicairkan["norek"],
                id_deposito=deposito_siap_dicairkan["id_deposito"],
                hari_ini=datetime.date(2026, 10, 24),
            )


class DepositoPalsu:
    def __init__(self, id):
        self.ID = id


class TestAroPokokDeposito:

    @pytest.fixture
    def deposito_siap_diperpanjang(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        koneksi_test.execute(
            """INSERT INTO deposito(id, norek, nominal, bunga, lama_bulan, tanggal_buka, jatuh_tempo, status, jenis_aro, lama_aro) 
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                1_000_000,
                0.03,
                1,
                "2026-09-24",
                "2026-10-24",
                StatusDeposito.AKTIF,
                JenisAro.POKOK,
                1,
            ),
        )

        koneksi_test.commit()

        return {"id_deposito": 1}

    def test_perpanjang_deposito_happy_path(
        self,
        koneksi_test,
        deposito_siap_diperpanjang,
        siapkan_data_rekening_dan_nasabah,
    ):

        deposito_dummy = DepositoPalsu(id=deposito_siap_diperpanjang["id_deposito"])
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_dummy.ID

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        hari_ini = datetime.date(2026, 10, 24)
        hasil = DepositoService.perpanjangan(
            deposito=deposito_dummy,
            koneksi=koneksi_test,
            hari_ini=hari_ini,
        )

        saldo_setelah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        assert hasil is True
        assert saldo_setelah == saldo_sebelum + 2_500
        assert data_deposito["status"] == StatusDeposito.AKTIF
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["tanggal_buka"] == "2026-10-24"
        assert data_deposito["jatuh_tempo"] == "2026-11-24"

    def test_perpannjang_deposito_tapi_rekeningnya_tutup(
        self,
        koneksi_test,
        deposito_siap_diperpanjang,
        siapkan_data_rekening_dan_nasabah,
    ):

        norek = siapkan_data_rekening_dan_nasabah["norek"]
        deposito_dummy = DepositoPalsu(id=deposito_siap_diperpanjang["id_deposito"])
        id_deposito = deposito_dummy.ID

        koneksi_test.execute(
            """UPDATE rekening SET status = 'tutup' WHERE norek = ?""",
            (norek,),
        )
        koneksi_test.commit()

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        hari_ini = datetime.date(2026, 10, 24)
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                deposito=deposito_dummy,
                koneksi=koneksi_test,
                hari_ini=hari_ini,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        assert data_deposito["jatuh_tempo"] == "2026-10-24"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        print(f"pesan error : {info_error.value}")
        assert "tidak dapat diperpanjang" in str(info_error.value)

    @pytest.mark.parametrize(
        "kolom, nilai_baru,pesan_error",
        [
            ("status", "dicairkan", "tidak dapat diperpanjang"),
            ("jatuh_tempo", "2026-12-31", "belum jatuh tempo"),
        ],
    )
    def test_perpanjangan_aro_kondisi_tidak_valid(
        self,
        koneksi_test,
        deposito_siap_diperpanjang,
        kolom,
        nilai_baru,
        pesan_error,
        siapkan_data_rekening_dan_nasabah,
    ):

        deposito_dummy = DepositoPalsu(id=deposito_siap_diperpanjang["id_deposito"])
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_dummy.ID

        koneksi_test.execute(
            f"UPDATE deposito SET {kolom} = ? WHERE id = ?",
            (nilai_baru, id_deposito),
        )
        koneksi_test.commit()

        hari_ini = datetime.date(2026, 10, 24)

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                deposito=deposito_dummy, koneksi=koneksi_test, hari_ini=hari_ini
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        print(f"pesan error: {info_error.value}")
        assert pesan_error in str(info_error.value)

    def test_rollback_perpanjangan_aro_saat_hampir_selesai(
        self,
        koneksi_test,
        deposito_siap_diperpanjang,
        monkeypatch,
        siapkan_data_rekening_dan_nasabah,
    ):

        deposito_dummy = DepositoPalsu(id=deposito_siap_diperpanjang["id_deposito"])
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_dummy.ID

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def tambah_riwayat_lalu_gagal(**kwargs):
            method_asli(**kwargs)
            raise RuntimeError("Simulasi gagal setelah riwayat tersimpan")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository,
            "tambah_riwayat",
            tambah_riwayat_lalu_gagal,
        )

        hari_ini = datetime.date(2026, 10, 24)

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(RuntimeError):
            with buat_koneksi_tulis() as koneksi:
                DepositoService.perpanjangan(
                    deposito=deposito_dummy,
                    koneksi=koneksi,
                    hari_ini=hari_ini,
                )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        assert (
            saldo_sesudah == saldo_sebelum
        ), "saldo seharusnya tidak berubah setelah rollback"

        assert (
            data_deposito["nominal"] == 1_000_000
        ), "nominal seharusnya tidak berubah setelah rollback"
        assert (
            data_deposito["jatuh_tempo"] == "2026-10-24"
        ), "jatuh tempo seharusnya tidak berubah setelah rollback"
        assert (
            data_deposito["status"] == StatusDeposito.AKTIF
        ), "status seharusnya tetap AKTIF (bukan berubah lalu batal)"

    def test_scheduler_memproses_aro_deposito(
        self, koneksi_test, deposito_siap_diperpanjang
    ):

        hari_ini = datetime.date(2026, 10, 24)
        Scheduler.jalankan(hari_ini)

        data_deposito = koneksi_test.execute(
            """SELECT * FROM deposito WHERE id = ?""",
            (deposito_siap_diperpanjang["id_deposito"],),
        ).fetchone()
        pesan = koneksi_test.execute(
            """SELECT pesan FROM notifikasi WHERE id_objek = ?""",
            (deposito_siap_diperpanjang["id_deposito"],),
        ).fetchone()

        assert pesan is not None, "seharusnya ada pesan utuk jatuh tempo deposito ini"
        assert (
            data_deposito["status"] == StatusDeposito.AKTIF
        ), "seharusnya status deposito masih aktif"
        assert data_deposito["tanggal_buka"] == "2026-10-24"
        assert data_deposito["jatuh_tempo"] == "2026-11-24"
        assert data_deposito["proses_aro"] == "2026-10-24"
        assert data_deposito["nominal"] == 1_000_000


class TestAroPokokBungaDeposito:

    @pytest.fixture
    def deposito_pokok_bunga_siap_diperpanjang(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        koneksi_test.execute(
            """INSERT INTO deposito(id, norek, nominal, bunga, lama_bulan, tanggal_buka, jatuh_tempo, status, jenis_aro, lama_aro) 
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                1_000_000,
                0.03,
                1,
                "2026-09-24",
                "2026-10-24",
                StatusDeposito.AKTIF,
                JenisAro.POKOK_BUNGA,
                1,
            ),
        )

        koneksi_test.commit()

        return {"id_deposito": 1}

    def test_perpanjang_deposito_happy_path(
        self,
        koneksi_test,
        deposito_pokok_bunga_siap_diperpanjang,
        siapkan_data_rekening_dan_nasabah,
    ):

        norek = siapkan_data_rekening_dan_nasabah["norek"]
        deposito_dummy = DepositoPalsu(
            id=deposito_pokok_bunga_siap_diperpanjang["id_deposito"]
        )
        id_deposito = deposito_dummy.ID

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        hari_ini = datetime.date(2026, 10, 24)

        hasil = DepositoService.perpanjangan(
            deposito=deposito_dummy,
            koneksi=koneksi_test,
            hari_ini=hari_ini,
        )

        data_deposito = koneksi_test.execute(
            """SELECT * FROM deposito WHERE id = ?""",
            (id_deposito,),
        ).fetchone()

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        assert hasil is True
        assert saldo_sesudah == saldo_sebelum
        assert data_deposito["tanggal_buka"] == "2026-10-24"
        assert data_deposito["jatuh_tempo"] == "2026-11-24"
        assert data_deposito["status"] == StatusDeposito.AKTIF

    def test_perpanjang_deposito_tapi_rekeningnya_tutup(
        self,
        koneksi_test,
        deposito_pokok_bunga_siap_diperpanjang,
        siapkan_data_rekening_dan_nasabah,
    ):
        deposito_dummy = DepositoPalsu(
            id=deposito_pokok_bunga_siap_diperpanjang["id_deposito"]
        )

        id_deposito = deposito_dummy.ID
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        koneksi_test.execute(
            """UPDATE rekening SET status = 'tutup' WHERE norek = ?""",
            (norek,),
        )
        koneksi_test.commit()

        hari_ini = datetime.date(2026, 10, 24)

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                deposito=deposito_dummy,
                koneksi=koneksi_test,
                hari_ini=hari_ini,
            )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        print(f"pesan error : {info_error.value}")
        assert data_deposito["jatuh_tempo"] == "2026-10-24"
        assert "tidak dapat diperpanjang" in str(info_error.value)

    def test_rollback_aro_saat_hampir_selesai(
        self,
        koneksi_test,
        deposito_pokok_bunga_siap_diperpanjang,
        siapkan_data_rekening_dan_nasabah,
        monkeypatch,
    ):

        deposito_dummy = DepositoPalsu(
            deposito_pokok_bunga_siap_diperpanjang["id_deposito"]
        )
        id_deposito = deposito_dummy.ID

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def penggagal_aro(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulasi rollback aro pokok + bunga")

        hari_ini = datetime.date(2026, 10, 24)
        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository, "tambah_riwayat", penggagal_aro
        )

        with pytest.raises(RuntimeError):
            with buat_koneksi_tulis() as koneksi:
                DepositoService.perpanjangan(
                    deposito=deposito_dummy, koneksi=koneksi, hari_ini=hari_ini
                )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        assert (
            data_deposito["nominal"] == 1_000_000
        ), "nominal seharusnya tidak berubah setelah rollback"
        assert (
            data_deposito["jatuh_tempo"] == "2026-10-24"
        ), "jatuh tempo seharusnya tidak berubah setelah rollback"

    def test_shceduler_memproses_aro_pokok_dan_bunga(
        self, koneksi_test, deposito_pokok_bunga_siap_diperpanjang
    ):

        id_deposito = deposito_pokok_bunga_siap_diperpanjang["id_deposito"]

        hari_ini = datetime.date(2026, 10, 24)
        Scheduler.jalankan(hari_ini)

        data_deposito = koneksi_test.execute(
            """SELECT * FROM deposito WHERE id = ?""",
            (id_deposito,),
        ).fetchone()
        pesan = koneksi_test.execute(
            """SELECT pesan FROM notifikasi WHERE id_objek = ?""",
            (id_deposito,),
        ).fetchone()

        assert pesan is not None, "seharusnya ada pesan utuk jatuh tempo deposito ini"
        assert (
            data_deposito["status"] == StatusDeposito.AKTIF
        ), "seharusnya status deposito masih aktif"
        assert data_deposito["tanggal_buka"] == "2026-10-24"
        assert data_deposito["jatuh_tempo"] == "2026-11-24"
        assert data_deposito["proses_aro"] == "2026-10-24"
        assert data_deposito["nominal"] == 1_002_500
