import pytest, datetime

from bank_djago.services.deposito.deposito_service import StatusDeposito
from bank_djago.services.deposito.deposito_service import DepositoService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.utility import JenisTransaksi
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository

from bank_djago.services.exceptions import (
    StatusTidakValid,
    InputTidakValid,
    RekeningTidakDitemukan,
    DepositoTidakDitemukan,
    PinTidakCocok,
    RekeningTerkunci,
    RekeningTidakSesuai
)



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

    @staticmethod
    def _kwargs_valid(data):
        return {"nik":data['nik'],
                "norek_pencairan":data['norek'],
                "id_deposito":1,
                "pin":data['pin']}


    def test_cairkan_deposito_happy_path(
        self, koneksi_test, deposito_siap_dicairkan, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = deposito_siap_dicairkan["jatuh tempo"] + datetime.timedelta(
            days=10
        )

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['hari_ini'] = hari_ini
        norek = kwargs['norek_pencairan']
        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        DepositoService.cairkan_deposito(
            **kwargs
        )
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_deposito = koneksi_test.execute(
            "SELECT * FROM deposito WHERE id = ?", (kwargs['id_deposito'],)
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

        hari_ini = deposito_siap_dicairkan["jatuh tempo"] - datetime.timedelta(days=1)

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['hari_ini'] = hari_ini
        norek = kwargs['norek_pencairan']

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=kwargs['id_deposito']
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                **kwargs
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=kwargs['id_deposito']
            )
            == kondisi_sebelum
        )
        assert "Deposito belum jatuh tempo" in str(info_error.value)

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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)

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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_deposito = 99
        kwargs['id_deposito'] = id_deposito

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )
        with pytest.raises(DepositoTidakDitemukan) as info_error:
            DepositoService.cairkan_deposito(
                **kwargs
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

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['hari_ini'] = hari_ini
        id_deposito = kwargs['id_deposito']
        norek = kwargs['norek_pencairan']

        koneksi_test.execute(
            "UPDATE deposito SET status = ? WHERE id = ?", (status_salah, id_deposito)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                **kwargs
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



        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_deposito = kwargs['id_deposito']

        koneksi_test.execute(
            """UPDATE rekening SET status = ? WHERE norek = ?""",
            (status_rekening_salah, siapkan_data_rekening_dan_nasabah["norek"]),
        )
        koneksi_test.commit()


        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                **kwargs
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['pin'] = '123457'
        norek = kwargs['norek_pencairan']
        id_deposito = kwargs['id_deposito']

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0

        kondisi_sebelum = self._ambil_kondisi_pencairan_deposito(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(PinTidakCocok) as info_error:
            DepositoService.cairkan_deposito(
                **kwargs
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_deposito = kwargs['id_deposito']

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
                **kwargs
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


    def test_cairkan_deposito_dua_kali(
        self, deposito_siap_dicairkan, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        hari_ini = deposito_siap_dicairkan["jatuh tempo"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['hari_ini'] = hari_ini

        norek = kwargs['norek_pencairan']
        id_deposito = kwargs['id_deposito']

        DepositoService.cairkan_deposito(
            **kwargs
        )

        kondisi_sebelum_pencairan_kedua = self._ambil_kondisi_pencairan_deposito(
            koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.cairkan_deposito(
                **kwargs
            )

        assert (
            self._ambil_kondisi_pencairan_deposito(
                koneksi=koneksi_test, norek=norek, id_deposito=id_deposito
            )
            == kondisi_sebelum_pencairan_kedua
        )
        assert "tidak dapat dicairkan" in str(info_error.value)
