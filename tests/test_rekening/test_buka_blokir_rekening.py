import pytest, datetime

from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.exceptions import PinTidakCocok, RekeningTerkunci, RekeningTidakDitemukan, StatusTidakValid, InputTidakValid

class TestBukaBlokir:

    @staticmethod
    def _ambil_kondisi_rekening(koneksi, norek):
        return{
            'status':koneksi.execute('SELECT status FROM rekening WHERE norek = ?',(norek,)).fetchone()['status'],
            'riwayat':koneksi.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pembukaan blokir rekening'",(norek,)).fetchone()[0],
            'audit': koneksi.execute("SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pembukaan_blokir_rekening'",(norek,)).fetchone()[0]
        }

    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik':data['nik'],
            'norek':data['norek'],
            'pin':data['pin']
        }
    def test_buka_blokir_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']

        koneksi_test.execute(
            "UPDATE rekening SET status = 'blokir' WHERE norek = ?", (norek,)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        assert kondisi_sebelum['status'] == 'blokir'

        RekeningService.buka_blokir(**kwargs)

        kondisi_sesudah = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        assert kondisi_sesudah['status'] == 'aktif'
        assert kondisi_sesudah['riwayat'] == kondisi_sebelum['riwayat'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1


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
                {"norek": None},
                "Nomor rekening tidak boleh kosong",
                id="norek None",
            ),
            pytest.param(
                {"norek": ""},
                "Nomor rekening tidak boleh kosong",
                id="norek kosong",
            ),
            pytest.param(
                {"norek": " "},
                "Nomor rekening tidak boleh kosong",
                id="norek spasi",
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
            )])
    def test_buka_blokir_dengan_input_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
        pesan_error,

    ):

        norek = siapkan_data_rekening_dan_nasabah['norek']
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        koneksi_test.execute(
            "UPDATE rekening SET status = 'blokir' WHERE norek = ?", (norek,)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.buka_blokir(**kwargs)

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "status_salah, pesan_error",
        [("aktif", "sudah dalam status aktif"), ("tutup", "telah ditutup!")],
    )
    def test_buka_blokir_dengan_status_rekening_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, status_salah, pesan_error
    ):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']

        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?", (status_salah, norek)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.buka_blokir(**kwargs)

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert pesan_error in str(info_error.value)


    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_buka_blokir_dengan_identitas_tidak_ditemukan(self,koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
        kwargs.update(kwargs_salah)



        koneksi_test.execute(
            "UPDATE rekening SET status = 'blokir' WHERE norek = ?", (norek,)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            RekeningService.buka_blokir(**kwargs)

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert 'Rekening tidak terdaftar' in str(info_error.value)


    def test_buka_blokir_pin_salah_mencatat_percobaan_gagal(self, koneksi_test, siapkan_rekening_siap_diturunkan):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        kwargs['pin'] = '123457'
        norek = kwargs['norek']

        koneksi_test.execute(
            "UPDATE rekening SET status = 'blokir' WHERE norek = ?", (norek,)
        )
        koneksi_test.commit()
        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0


        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(PinTidakCocok) as info_error:
            RekeningService.buka_blokir(**kwargs)

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert (
            self._ambil_kondisi_rekening(koneksi_test, norek)
            == kondisi_sebelum
        )
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_buka_blokir_dengan_kondisi_rekening_terkunci_dan_masukkan_pin_benar(
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
            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            with pytest.raises(RekeningTerkunci) as info_error:
                RekeningService.buka_blokir(**kwargs)

            waktu_kunci_sesudah = koneksi_test.execute(
                "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
            ).fetchone()["terkunci_sampai"]

            assert waktu_kunci_sesudah == waktu_kunci
            assert (
                    self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
                    == kondisi_sebelum
            )
            assert RekeningService.PESAN_REKENING_TERKUNCI in str(info_error.value)
