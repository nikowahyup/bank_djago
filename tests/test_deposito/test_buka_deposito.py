import pytest, datetime


from bank_djago.services.deposito.deposito_service import DepositoService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.utils.utility import JenisTransaksi
from bank_djago.services.deposito.deposito_service import JenisAro
from bank_djago.services.deposito.deposito_service import StatusDeposito
from bank_djago.services.exceptions import (
    StatusTidakValid,
    InputTidakValid,
    JenisAroTidakValid,
    RekeningTidakDitemukan,
    PinTidakCocok,
    RekeningTerkunci)

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
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']

        saldo_sebelum = RekeningRepository.ambil_saldo(norek=norek,koneksi=koneksi_test)

        DepositoService.buka_deposito(**kwargs)

        saldo_sesudah = RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi_test)

        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE norek = ?", (norek,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()
        assert transaksi is not None
        assert transaksi["jenis"] == JenisTransaksi.PEMBUKAAN_DEPOSITO.value
        assert transaksi["nominal"] == kwargs['nominal']
        id_transaksi = transaksi["id"]

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pembukaan_deposito' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()

        assert saldo_sesudah == saldo_sebelum - kwargs['nominal']
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
        kwargs['nominal'] = 10_000_000
        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi=koneksi_test,norek=norek)

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.buka_deposito(
                **kwargs
            )

        assert kondisi_sebelum == self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek)
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
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
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