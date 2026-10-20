import datetime


import pytest

from bank_djago import DepositoService, JenisAro, JenisTransaksi
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis
from bank_djago.services.deposito.deposito_service import StatusDeposito
from bank_djago.services.exceptions import (
    RekeningTidakDitemukan,
    StatusTidakValid,
    InputTidakValid,
    JenisAroTidakValid,
    RekeningTidakSesuai,
    DepositoTidakDitemukan,
    PerbaruiStatusGagal,
    PinTidakCocok,
    RekeningTerkunci,
)
from bank_djago.services.rekening.rekening_service import RekeningService
import bank_djago.penyimpanan.repositories.riwayat_repository as riwayat_repo_module
import bank_djago.penyimpanan.repositories.deposito_repository as deposito_repo_module
from bank_djago.services.scheduler import Scheduler


class TestBukaDeposito:

    @staticmethod
    def _ambil_kondisi_deposito(koneksi, norek):
        return {
            "deposito": koneksi.execute(
                "SELECT COUNT(*) FROM deposito WHERE norek = ?", (norek,)
            ).fetchone()[0],
            "saldo": RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi),
            "transaksi": koneksi.execute(
                "SELECT COUNT(*) FROM transaksi WHERE norek_sumber = ? AND jenis = ?",
                (norek, JenisTransaksi.PEMBUKAAN_DEPOSITO.value),
            ).fetchone()[0],
            "riwayat": koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pembukaan deposito'",
                (norek,),
            ).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pembukaan_deposito'",
                (norek,),
            ).fetchone()[0],
        }

    @staticmethod
    def _kwargs_valid(data):
        return {
            "nik": data["nik"],
            "norek": data["norek"],
            "pin": data["pin"],
            "nominal": 1_000_000,
            "lama_bulan": 3,
            "jenis_aro": JenisAro.TIDAK,
            "lama_aro": None,
        }

    def test_buka_deposito_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        nominal = 1_000_000

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        DepositoService.buka_deposito(
            nik=nik,
            norek=norek,
            nominal=nominal,
            lama_bulan=3,
            jenis_aro=JenisAro.TIDAK,
            lama_aro=None,
            pin=pin,
        )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()
        assert transaksi is not None
        assert transaksi["jenis"] == JenisTransaksi.PEMBUKAAN_DEPOSITO.value
        assert transaksi["nominal"] == nominal
        id_transaksi = transaksi["id"]

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pembukaan_deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()

        assert saldo_sesudah == saldo_sebelum - 1_000_000
        assert data_deposito is not None
        assert data_deposito["norek"] == norek
        assert data_deposito["jenis_aro"] == JenisAro.TIDAK
        assert data_deposito["status"] == StatusDeposito.AKTIF
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["lama_bulan"] == 3
        assert data_deposito["lama_aro"] is None
        assert riwayat is not None
        assert audit is not None

    def test_buka_deposito_dengan_nominal_diatas_minimal_saldo(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

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
                pin=pin,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        assert (
            data_deposito is None
        ), "seharusnya tidak ada deposito yang berhasil dibuat"
        assert saldo_sesudah == saldo_sebelum, "seharusnya saldo rekening tidak berubah"
        assert "Saldo rekening akan kurang" in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah, pesan_error",
        [
            # NIK
            pytest.param({"nik": None}, "NIK tidak boleh kosong", id="nik None"),
            pytest.param({"nik": ""}, "NIK tidak boleh kosong", id="nik kosong"),
            pytest.param({"nik": " "}, "NIK tidak boleh kosong", id="nik spasi"),
            pytest.param(
                {"nik": "12345abcde123456"},
                "NIK tidak boleh mengandung huruf",
                id="nik ada huruf",
            ),
            pytest.param(
                {"nik": "3" * 15}, "Jumlah digit NIK tidak valid", id="nik 15 digit"
            ),
            pytest.param(
                {"nik": "3" * 17}, "Jumlah digit NIK tidak valid", id="nik 17 digit"
            ),
            # norek
            pytest.param(
                {"norek": None}, "Nomor rekening tidak boleh kosong", id="norek None"
            ),
            pytest.param(
                {"norek": ""}, "Nomor rekening tidak boleh kosong", id="norek kosong"
            ),
            pytest.param(
                {"norek": " "}, "Nomor rekening tidak boleh kosong", id="norek spasi"
            ),
            pytest.param(
                {"norek": "12345abcde123456"},
                "Nomor rekening tidak boleh mengandung huruf",
                id="norek ada huruf",
            ),
            pytest.param(
                {"norek": "2" * 15},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 15 digit",
            ),
            pytest.param(
                {"norek": "2" * 17},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 17 digit",
            ),
            # PIN
            pytest.param({"pin": None}, "PIN tidak boleh kosong", id="pin None"),
            pytest.param({"pin": ""}, "PIN tidak boleh kosong", id="pin kosong"),
            pytest.param({"pin": " "}, "PIN tidak boleh kosong", id="pin spasi"),
            pytest.param(
                {"pin": "1234"}, "PIN harus berupa 6 digit angka", id="pin kurang"
            ),
            pytest.param(
                {"pin": "12345q"}, "PIN harus berupa 6 digit angka", id="pin ada huruf"
            ),
            # nominal
            pytest.param(
                {"nominal": None}, "Nominal harus berupa angka", id="nominal None"
            ),
            pytest.param(
                {"nominal": "abc"}, "Nominal harus berupa angka", id="nominal huruf"
            ),
            pytest.param(
                {"nominal": 0}, "Nominal deposito tidak memenuhi syarat", id="nominal 0"
            ),
            pytest.param(
                {"nominal": -1_000_000},
                "Nominal deposito tidak memenuhi syarat",
                id="nominal minus",
            ),
            pytest.param(
                {"nominal": 999_999},
                "Nominal deposito tidak memenuhi syarat",
                id="nominal kurang",
            ),
            # lama bulan
            pytest.param(
                {"lama_bulan": None},
                "Lama deposito harus berupa angka",
                id="bulan None",
            ),
            pytest.param(
                {"lama_bulan": "abc"},
                "Lama deposito harus berupa angka",
                id="bulan huruf",
            ),
            pytest.param(
                {"lama_bulan": 5},
                "Jangka waktu deposito tidak tersedia",
                id="bulan tidak tersedia",
            ),
            pytest.param(
                {"lama_bulan": 0},
                "Jangka waktu deposito tidak tersedia",
                id="bulan nol",
            ),
            # lama ARO
            pytest.param(
                {"jenis_aro": JenisAro.TIDAK, "lama_aro": 3},
                "tidak membutuhkan lama perpanjangan",
                id="non aro ada lama aro",
            ),
            pytest.param(
                {"jenis_aro": JenisAro.POKOK, "lama_aro": None},
                "Lama ARO harus berupa angka",
                id="aro pokok lama aro None",
            ),
            pytest.param(
                {"jenis_aro": JenisAro.POKOK_BUNGA, "lama_aro": "abc"},
                "Lama ARO harus berupa angka",
                id="aro pokok bunga lama aro huruf",
            ),
            # bukti urutan: cek murah sebelum PIN, jadi PIN salah tidak sempat dihitung
            pytest.param(
                {"nominal": 999_999, "pin": "123457"},
                "Nominal deposito tidak memenuhi syarat",
                id="nominal cacat dan pin salah",
            ),
            pytest.param(
                {"lama_bulan": 5, "pin": "123457"},
                "Jangka waktu deposito tidak tersedia",
                id="bulan cacat dan pin salah",
            ),
            pytest.param(
                {"norek": "2" * 15, "pin": "123457"},
                "Jumlah digit nomor rekening tidak valid",
                id="norek cacat dan pin salah",
            ),
        ],
    )
    def test_buka_deposito_dengan_input_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah, pesan_error
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi_test, norek)

        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.buka_deposito(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert self._ambil_kondisi_deposito(koneksi_test, norek) == kondisi_sebelum
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah, pesan_error",
        [
            pytest.param(
                {"jenis_aro": "jenis apa saja"},
                "Jenis ARO tidak tersedia",
                id="jenis aro sembarang",
            ),
            pytest.param(
                {"jenis_aro": JenisAro.POKOK, "lama_aro": 2},
                "Jangka waktu perpanjangan tidak tersedia",
                id="aro pokok lama aro 2",
            ),
            pytest.param(
                {"jenis_aro": JenisAro.POKOK_BUNGA, "lama_aro": 24},
                "Jangka waktu perpanjangan tidak tersedia",
                id="aro pokok bunga lama aro 24",
            ),
        ],
    )
    def test_buka_deposito_dengan_jenis_aro_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah, pesan_error
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi_test, norek)

        with pytest.raises(JenisAroTidakValid) as info_error:
            DepositoService.buka_deposito(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert self._ambil_kondisi_deposito(koneksi_test, norek) == kondisi_sebelum
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_buka_deposito_dengan_identitas_tidak_ditemukan(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi_test, norek)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            DepositoService.buka_deposito(**kwargs)

        assert self._ambil_kondisi_deposito(koneksi_test, norek) == kondisi_sebelum
        assert "Rekening tidak terdaftar" in str(info_error.value)

    def test_buka_deposito_pin_salah_mencatat_percobaan_gagal(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs["pin"] = "123457"

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi_test, norek)

        with pytest.raises(PinTidakCocok) as info_error:
            DepositoService.buka_deposito(**kwargs)

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert self._ambil_kondisi_deposito(koneksi_test, norek) == kondisi_sebelum
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_buka_deposito_rekening_terkunci_dengan_pin_benar(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)

        waktu_kunci = (
            datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat()
        koneksi_test.execute(
            "UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",
            (waktu_kunci, norek),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi_test, norek)

        with pytest.raises(RekeningTerkunci) as info_error:
            DepositoService.buka_deposito(**kwargs)

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert self._ambil_kondisi_deposito(koneksi_test, norek) == kondisi_sebelum
        assert RekeningService.PESAN_REKENING_TERKUNCI in str(info_error.value)

    def test_rollback_deposito_saat_hampir_saja_selesai_dibuat(
        self, koneksi_test, monkeypatch, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
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
                pin=pin,
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
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        koneksi_test.execute(
            """INSERT INTO deposito
        (id,norek,nominal, bunga, lama_bulan,tanggal_buka, jatuh_tempo, status)
         VALUES (?,?,?,?,?,?,?,?)""",
            (
                1,
                norek,
                1_000_000,
                0.03,
                1,
                datetime.date.today().isoformat(),
                (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                StatusDeposito.JATUH_TEMPO,
            ),
        )

        koneksi_test.commit()

        return {
            "id_deposito": 1,
            "jatuh tempo": datetime.date.today() + datetime.timedelta(days=30),
        }

    @staticmethod
    def _ambil_kondisi_pencairan_deposito(koneksi, norek, id_deposito):
        deposito = koneksi.execute(
            "SELECT status FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()
        return {
            "deposito": tuple(deposito) if deposito else None,
            "saldo": RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi),
            "transaksi": koneksi.execute(
                "SELECT COUNT(*) FROM transaksi WHERE jenis_referensi = 'deposito' AND id_referensi = ?",
                (id_deposito,),
            ).fetchone()[0],
            "riwayat": koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pencairan deposito'",
                (norek,),
            ).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pencairan_deposito'",
                (norek,),
            ).fetchone()[0],
        }

    def test_cairkan_deposito_happy_path(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = deposito_siap_dicairkan["jatuh tempo"] + datetime.timedelta(
            days=10
        )  # bebas berapa pun asalkan waktunya ditambahkan dengan jatuh tempo

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        DepositoService.cairkan_deposito(
            nik=nik,
            norek_pencairan=norek,
            id_deposito=id_deposito,
            hari_ini=hari_ini,
            pin=pin,
        )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_tujuan = ?", (norek,)
        ).fetchone()
        assert transaksi is not None
        assert transaksi["jenis"] == JenisTransaksi.PENCAIRAN_DEPOSITO.value
        assert transaksi["nominal"] == saldo_sesudah - saldo_sebelum
        id_transaksi = transaksi["id"]

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pencairan deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pencairan_deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()

        assert data_deposito is not None
        assert data_deposito["norek"] == norek
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["status"] == StatusDeposito.DICAIRKAN
        assert saldo_sesudah == saldo_sebelum + 1_002_500
        assert riwayat is not None
        assert audit is not None

    def test_cairkan_deposito_belum_jatuh_tempo(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        hari_ini = deposito_siap_dicairkan["jatuh tempo"] - datetime.timedelta(days=1)

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
                pin=pin,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum
        )
        assert "Deposito belum jatuh tempo" in str(info_error.value)

    def test_cairkan_deposito_tepat_jatuh_tempo(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        DepositoService.cairkan_deposito(
            nik=nik,
            norek_pencairan=norek,
            id_deposito=id_deposito,
            hari_ini=hari_ini,
            pin=pin,
        )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_tujuan = ?", (norek,)
        ).fetchone()
        assert transaksi is not None
        assert transaksi["jenis"] == JenisTransaksi.PENCAIRAN_DEPOSITO.value
        assert transaksi["nominal"] == saldo_sesudah - saldo_sebelum
        id_transaksi = transaksi["id"]

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pencairan deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pencairan_deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        )

        assert data_deposito is not None
        assert data_deposito["norek"] == norek
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["status"] == StatusDeposito.DICAIRKAN
        assert saldo_sesudah == saldo_sebelum + 1_002_500
        assert riwayat is not None
        assert audit is not None

    @pytest.mark.parametrize(
        "kwargs_salah, pesan_error",
        [
            # NIK
            pytest.param({"nik": None}, "NIK tidak boleh kosong", id="nik None"),
            pytest.param({"nik": ""}, "NIK tidak boleh kosong", id="nik kosong"),
            pytest.param({"nik": " "}, "NIK tidak boleh kosong", id="nik spasi"),
            pytest.param(
                {"nik": "12345abcde123456"},
                "NIK tidak boleh mengandung huruf",
                id="nik ada huruf",
            ),
            pytest.param(
                {"nik": "3" * 15}, "Jumlah digit NIK tidak valid", id="nik 15 digit"
            ),
            pytest.param(
                {"nik": "3" * 17}, "Jumlah digit NIK tidak valid", id="nik 17 digit"
            ),
            # norek pencairan
            pytest.param(
                {"norek_pencairan": None},
                "Nomor rekening tidak boleh kosong",
                id="norek None",
            ),
            pytest.param(
                {"norek_pencairan": ""},
                "Nomor rekening tidak boleh kosong",
                id="norek kosong",
            ),
            pytest.param(
                {"norek_pencairan": " "},
                "Nomor rekening tidak boleh kosong",
                id="norek spasi",
            ),
            pytest.param(
                {"norek_pencairan": "12345abcde123456"},
                "Nomor rekening tidak boleh mengandung huruf",
                id="norek ada huruf",
            ),
            pytest.param(
                {"norek_pencairan": "2" * 15},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 15 digit",
            ),
            pytest.param(
                {"norek_pencairan": "2" * 17},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 17 digit",
            ),
            # PIN
            pytest.param({"pin": None}, "PIN tidak boleh kosong", id="pin None"),
            pytest.param({"pin": ""}, "PIN tidak boleh kosong", id="pin kosong"),
            pytest.param({"pin": " "}, "PIN tidak boleh kosong", id="pin spasi"),
            pytest.param(
                {"pin": "1234"}, "PIN harus berupa 6 digit angka", id="pin kurang"
            ),
            pytest.param(
                {"pin": "12345q"}, "PIN harus berupa 6 digit angka", id="pin ada huruf"
            ),
            # ID deposito
            pytest.param(
                {"id_deposito": None}, "ID deposito harus berupa angka", id="id None"
            ),
            pytest.param(
                {"id_deposito": "abc"}, "ID deposito harus berupa angka", id="id huruf"
            ),
            pytest.param(
                {"id_deposito": 1.5}, "ID deposito harus berupa angka", id="id desimal"
            ),
            pytest.param(
                {"id_deposito": True}, "ID deposito harus berupa angka", id="id bool"
            ),
            pytest.param({"id_deposito": 0}, "ID deposito tidak valid", id="id nol"),
            pytest.param(
                {"id_deposito": -9}, "ID deposito tidak valid", id="id negatif"
            ),
            # bukti urutan: cek murah sebelum PIN, jadi PIN salah tidak sempat dihitung
            pytest.param(
                {"id_deposito": -9, "pin": "123457"},
                "ID deposito tidak valid",
                id="id cacat dan pin salah",
            ),
            pytest.param(
                {"norek_pencairan": "2" * 15, "pin": "123457"},
                "Jumlah digit nomor rekening tidak valid",
                id="norek cacat dan pin salah",
            ),
        ],
    )
    def test_cairkan_deposito_dengan_input_tidak_valid(
        self,
        koneksi_test,
        deposito_siap_dicairkan,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
        pesan_error,
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_siap_dicairkan["id_deposito"]

        kwargs = {
            "nik": siapkan_data_rekening_dan_nasabah["nik"],
            "norek_pencairan": norek,
            "pin": siapkan_data_rekening_dan_nasabah["pin"],
            "id_deposito": id_deposito,
            "hari_ini": datetime.date.today() + datetime.timedelta(days=30),
        }
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.cairkan_deposito(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert (
            self._ambil_kondisi_pencairan_deposito(koneksi_test, norek, id_deposito)
            == kondisi_sebelum
        )
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek_pencairan": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_cairkan_deposito_dengan_identitas_tidak_ditemukan(
        self,
        koneksi_test,
        deposito_siap_dicairkan,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_siap_dicairkan["id_deposito"]

        kwargs = {
            "nik": siapkan_data_rekening_dan_nasabah["nik"],
            "norek_pencairan": norek,
            "pin": siapkan_data_rekening_dan_nasabah["pin"],
            "id_deposito": id_deposito,
            "hari_ini": datetime.date.today() + datetime.timedelta(days=30),
        }
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            DepositoService.cairkan_deposito(**kwargs)

        assert (
            self._ambil_kondisi_pencairan_deposito(koneksi_test, norek, id_deposito)
            == kondisi_sebelum
        )
        assert "Rekening tidak terdaftar" in str(info_error.value)

    def test_cairkan_deposito_id_deposito_tidak_terdaftar(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        id_deposito = 99
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )
        with pytest.raises(DepositoTidakDitemukan) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
                pin=pin,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum
        )
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
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]

        koneksi_test.execute(
            "UPDATE deposito SET status = ? WHERE id = ?", (status_salah, id_deposito)
        )
        koneksi_test.commit()

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
                pin=pin,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum
        )
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

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
                pin=pin,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum
        )
        assert f"Rekening Anda saat ini sedang di{status_rekening_salah}" in str(
            info_error.value
        )

    def test_cairkan_deposito_pin_salah_mencatat_percobaan_gagal(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_siap_dicairkan["id_deposito"]
        hari_ini = deposito_siap_dicairkan["jatuh tempo"]
        pin_salah = "123457"

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(PinTidakCocok) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                pin=pin_salah,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert (
            self._ambil_kondisi_pencairan_deposito(koneksi_test, norek, id_deposito)
            == kondisi_sebelum
        )
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_cairkan_deposito_rekening_terkunci_dengan_pin_benar(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin_benar = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_siap_dicairkan["id_deposito"]
        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        waktu_kunci = (
            datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat()
        koneksi_test.execute(
            "UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",
            (waktu_kunci, norek),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RekeningTerkunci) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                pin=pin_benar,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert (
            self._ambil_kondisi_pencairan_deposito(koneksi_test, norek, id_deposito)
            == kondisi_sebelum
        )
        assert RekeningService.PESAN_REKENING_TERKUNCI in str(info_error.value)

    def test_cairkan_deposito_dengan_norek_bukan_pemilik_deposito(
        self,
        koneksi_test,
        deposito_siap_dicairkan,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        norek_pemilik = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_siap_dicairkan["id_deposito"]
        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        nik = siapkan_data_rekening_penerima["nik"]
        norek = siapkan_data_rekening_penerima["norek"]
        pin = siapkan_data_rekening_penerima["pin"]

        kondisi_pemilik_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek_pemilik, id_deposito
        )
        kondisi_pemanggil_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RekeningTidakSesuai) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                pin=pin,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi_test, norek_pemilik, id_deposito
            )
            == kondisi_pemilik_sebelum
        )
        assert (
            self._ambil_kondisi_pencairan_deposito(koneksi_test, norek, id_deposito)
            == kondisi_pemanggil_sebelum
        )
        assert "tidak terdaftar sebagai pemilik deposito" in str(info_error.value)

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
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def method_untuk_uji_rollback(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulai rollback pencairan deposito")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository,
            "tambah_riwayat",
            method_untuk_uji_rollback,
        )

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]
        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )
        with pytest.raises(RuntimeError):
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
                pin=pin,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum
        )

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
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]
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

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(PerbaruiStatusGagal):
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                pin=pin,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
            )

        kondisi_sesudah = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        assert kondisi_sesudah["saldo"] == saldo_sebelum
        assert kondisi_sesudah["transaksi"] == 0
        assert kondisi_sesudah["riwayat"] == 0
        assert kondisi_sesudah["audit"] == 0
        assert kondisi_sesudah["deposito"] == (StatusDeposito.DICAIRKAN,)

    def test_cairkan_deposito_dua_kali(
        self, deposito_siap_dicairkan, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        id_deposito = deposito_siap_dicairkan["id_deposito"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        DepositoService.cairkan_deposito(
            nik=nik,
            norek_pencairan=norek,
            id_deposito=id_deposito,
            hari_ini=hari_ini,
            pin=pin,
        )

        kondisi_sebelum_pencairan_kedua = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                nik=nik,
                norek_pencairan=norek,
                id_deposito=id_deposito,
                hari_ini=hari_ini,
                pin=pin,
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum_pencairan_kedua
        )
        assert "tidak dapat dicairkan" in str(info_error.value)


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


class TestHentikanAro:

    @pytest.fixture
    def deposito_aro_siap_dihentikan(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        koneksi_test.execute(
            """INSERT INTO deposito
        (id,norek,nominal, bunga, lama_bulan,tanggal_buka, jatuh_tempo, status,jenis_aro,lama_aro)
         VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                norek,
                1_000_000,
                0.03,
                1,
                datetime.date.today().isoformat(),
                (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                StatusDeposito.AKTIF,
                JenisAro.POKOK,
                1,
            ),
        )

        koneksi_test.commit()
        return {
            "id_deposito": 1,
            "jatuh tempo": datetime.date.today() + datetime.timedelta(days=30),
        }

    @staticmethod
    def _ambil_kondisi_deposito_sebelum_dihentikan(koneksi, norek, id_deposito):
        deposito = koneksi.execute(
            "SELECT status, jenis_aro, lama_aro, nominal FROM deposito WHERE id = ?",
            (id_deposito,),
        ).fetchone()
        return {
            "deposito": tuple(deposito) if deposito else None,
            "saldo": RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi),
            "riwayat": koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'penghentian aro deposito'",
                (norek,),
            ).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'penghentian_aro_deposito'",
                (norek,),
            ).fetchone()[0],
        }

    @pytest.mark.parametrize(
        "kwargs_salah, pesan_error",
        [
            # NIK
            pytest.param({"nik": None}, "NIK tidak boleh kosong", id="nik None"),
            pytest.param({"nik": ""}, "NIK tidak boleh kosong", id="nik kosong"),
            pytest.param({"nik": " "}, "NIK tidak boleh kosong", id="nik spasi"),
            pytest.param(
                {"nik": "12345abcde123456"},
                "NIK tidak boleh mengandung huruf",
                id="nik ada huruf",
            ),
            pytest.param(
                {"nik": "3" * 15}, "Jumlah digit NIK tidak valid", id="nik 15 digit"
            ),
            pytest.param(
                {"nik": "3" * 17}, "Jumlah digit NIK tidak valid", id="nik 17 digit"
            ),
            # norek pencairan
            pytest.param(
                {"norek_pemberhentian": None},
                "Nomor rekening tidak boleh kosong",
                id="norek None",
            ),
            pytest.param(
                {"norek_pemberhentian": ""},
                "Nomor rekening tidak boleh kosong",
                id="norek kosong",
            ),
            pytest.param(
                {"norek_pemberhentian": " "},
                "Nomor rekening tidak boleh kosong",
                id="norek spasi",
            ),
            pytest.param(
                {"norek_pemberhentian": "12345abcde123456"},
                "Nomor rekening tidak boleh mengandung huruf",
                id="norek ada huruf",
            ),
            pytest.param(
                {"norek_pemberhentian": "2" * 15},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 15 digit",
            ),
            pytest.param(
                {"norek_pemberhentian": "2" * 17},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 17 digit",
            ),
            # PIN
            pytest.param({"pin": None}, "PIN tidak boleh kosong", id="pin None"),
            pytest.param({"pin": ""}, "PIN tidak boleh kosong", id="pin kosong"),
            pytest.param({"pin": " "}, "PIN tidak boleh kosong", id="pin spasi"),
            pytest.param(
                {"pin": "1234"}, "PIN harus berupa 6 digit angka", id="pin kurang"
            ),
            pytest.param(
                {"pin": "12345q"}, "PIN harus berupa 6 digit angka", id="pin ada huruf"
            ),
            # ID deposito
            pytest.param(
                {"id_deposito": None}, "ID deposito harus berupa angka", id="id None"
            ),
            pytest.param(
                {"id_deposito": "abc"}, "ID deposito harus berupa angka", id="id huruf"
            ),
            pytest.param(
                {"id_deposito": 1.5}, "ID deposito harus berupa angka", id="id desimal"
            ),
            pytest.param(
                {"id_deposito": True}, "ID deposito harus berupa angka", id="id bool"
            ),
            pytest.param({"id_deposito": 0}, "ID deposito tidak valid", id="id nol"),
            pytest.param(
                {"id_deposito": -9}, "ID deposito tidak valid", id="id negatif"
            ),
            # bukti urutan: cek murah sebelum PIN, jadi PIN salah tidak sempat dihitung
            pytest.param(
                {"id_deposito": -9, "pin": "123457"},
                "ID deposito tidak valid",
                id="id cacat dan pin salah",
            ),
            pytest.param(
                {"norek_pemberhentian": "2" * 15, "pin": "123457"},
                "Jumlah digit nomor rekening tidak valid",
                id="norek cacat dan pin salah",
            ),
        ],
    )
    def test_hentikan_aro_deposito_dengan_input_tidak_valid(
        self,
        koneksi_test,
        deposito_aro_siap_dihentikan,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
        pesan_error,
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        kwargs = {
            "nik": siapkan_data_rekening_dan_nasabah["nik"],
            "norek_pemberhentian": norek,
            "pin": siapkan_data_rekening_dan_nasabah["pin"],
            "id_deposito": id_deposito,
        }
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(InputTidakValid) as info_error:
            DepositoService.hentikan_aro(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek_pemberhentian": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_hentikan_aro_deposito_dengan_identitas_tidak_ditemukan(
        self,
        koneksi_test,
        deposito_aro_siap_dihentikan,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        kwargs = {
            "nik": siapkan_data_rekening_dan_nasabah["nik"],
            "norek_pemberhentian": norek,
            "pin": siapkan_data_rekening_dan_nasabah["pin"],
            "id_deposito": id_deposito,
        }
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            DepositoService.hentikan_aro(**kwargs)

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert "Rekening tidak terdaftar" in str(info_error.value)

    def test_hentikan_aro_deposito_dengan_status_rekening_tutup(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        koneksi_test.execute(
            "UPDATE rekening SET status = 'tutup' WHERE norek = ?", (norek,)
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.hentikan_aro(
                nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=id_deposito
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert "ARO tidak dapat dihentikan karena rekening telah ditutup" in str(
            info_error.value
        )

    def test_hentikan_aro_deposito_dengan_norek_bukan_pemilik_deposito(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
        deposito_aro_siap_dihentikan,
    ):
        norek_pemilik = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]
        nik = siapkan_data_rekening_penerima["nik"]
        norek = siapkan_data_rekening_penerima["norek"]
        pin = siapkan_data_rekening_penerima["pin"]

        kondisi_pemilik_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek_pemilik, id_deposito
        )
        kondisi_pemanggil_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RekeningTidakSesuai) as info_error:
            DepositoService.hentikan_aro(
                nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=id_deposito
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek_pemilik, id_deposito
            )
            == kondisi_pemilik_sebelum
        )
        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_pemanggil_sebelum
        )
        assert "Rekening ini tidak terdaftar sebagai pemilik deposito" in str(
            info_error.value
        )

    @pytest.mark.parametrize("jenis_aro", [JenisAro.POKOK, JenisAro.POKOK_BUNGA])
    def test_hentikan_aro_deposito_happy_path_semua_jenis_aro(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
        jenis_aro,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        koneksi_test.execute(
            "UPDATE deposito SET jenis_aro = ? WHERE id = ?", (jenis_aro, id_deposito)
        )
        koneksi_test.commit()
        sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        hasil = DepositoService.hentikan_aro(
            nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=id_deposito
        )

        sesudah = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )
        status, jenis, lama, nominal = sesudah["deposito"]

        assert hasil == id_deposito
        assert jenis == JenisAro.TIDAK
        assert lama is None
        assert status == StatusDeposito.AKTIF
        assert nominal == sebelum["deposito"][3]
        assert sesudah["saldo"] == sebelum["saldo"]
        assert sesudah["riwayat"] == sebelum["riwayat"] + 1
        assert sesudah["audit"] == sebelum["audit"] + 1

    def test_hentikan_aro_deposito_yang_sudah_non_aro(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        koneksi_test.execute(
            "UPDATE deposito SET jenis_aro = ?, lama_aro = NULL WHERE id = ?",
            (JenisAro.TIDAK, id_deposito),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(JenisAroTidakValid) as info_error:
            DepositoService.hentikan_aro(
                nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=id_deposito
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert "tidak menggunakan ARO" in str(info_error.value)

    @pytest.mark.parametrize("status_salah", ["jatuh tempo", "dicairkan"])
    def test_hentikan_aro_deposito_dengan_status_deposito_bukan_aktif(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
        status_salah,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        koneksi_test.execute(
            "UPDATE deposito SET status = ? WHERE id = ?", (status_salah, id_deposito)
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.hentikan_aro(
                nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=id_deposito
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert "hanya dapat dihentikan pada deposito aktif" in str(info_error.value)

    def test_hentikan_aro_deposito_id_tidak_terdaftar(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        id_asli = deposito_aro_siap_dihentikan["id_deposito"]

        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_asli
        )

        with pytest.raises(DepositoTidakDitemukan) as info_error:
            DepositoService.hentikan_aro(
                nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=99
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_asli
            )
            == kondisi_sebelum
        )
        assert "Deposito tidak ditemukan" in str(info_error.value)

    def test_rollback_hentikan_aro(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
        monkeypatch,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def tambah_riwayat_lalu_gagal(**kwargs):
            method_asli(**kwargs)
            raise RuntimeError("Simulasi rollback hentikan ARO")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository,
            "tambah_riwayat",
            tambah_riwayat_lalu_gagal,
        )
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RuntimeError):
            DepositoService.hentikan_aro(
                nik=nik, norek_pemberhentian=norek, pin=pin, id_deposito=id_deposito
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )

    def test_hentikan_aro_deposito_pin_salah_mencatat_percobaan_gagal(
        self,
        koneksi_test,
        deposito_aro_siap_dihentikan,
        siapkan_data_rekening_dan_nasabah,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]
        pin_salah = "123457"

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(PinTidakCocok) as info_error:
            DepositoService.hentikan_aro(
                nik=nik,
                norek_pemberhentian=norek,
                pin=pin_salah,
                id_deposito=id_deposito,
            )

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_hentikan_aro_deposito_rekening_terkunci_dengan_pin_benar(
        self,
        koneksi_test,
        deposito_aro_siap_dihentikan,
        siapkan_data_rekening_dan_nasabah,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin_benar = siapkan_data_rekening_dan_nasabah["pin"]
        id_deposito = deposito_aro_siap_dihentikan["id_deposito"]

        waktu_kunci = (
            datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat()
        koneksi_test.execute(
            "UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",
            (waktu_kunci, norek),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(RekeningTerkunci) as info_error:
            DepositoService.hentikan_aro(
                nik=nik,
                norek_pemberhentian=norek,
                id_deposito=id_deposito,
                pin=pin_benar,
            )

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert RekeningService.PESAN_REKENING_TERKUNCI in str(info_error.value)
