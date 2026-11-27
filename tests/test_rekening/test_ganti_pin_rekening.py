import pytest, datetime

from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.validator import Validator
from bank_djago.services.exceptions import PinTidakCocok, InputTidakValid, RekeningTidakDitemukan, RekeningTerkunci



class TestGantiPin:

        @staticmethod
        def _ambil_kondisi_rekening(koneksi, norek):

            return {
                'pin':koneksi.execute("SELECT pin FROM rekening WHERE norek = ?",(norek,)).fetchone()['pin'],
                'riwayat':koneksi.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'penggantian pin rekening'",(norek,)).fetchone()[0],
                'audit':koneksi.execute("SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'penggantian_pin_rekening'",(norek,)).fetchone()[0]
            }

        @staticmethod
        def _kwargs_valid(data):
            return {
                'nik':data['nik'],
                'norek':data['norek'],
                'pin_lama': data['pin'],
                'pin_baru': '654321'
            }

        def test_ganti_pin_happy_path(
                self, koneksi_test, siapkan_data_rekening_dan_nasabah
        ):
            kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
            norek = kwargs['norek']

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
            RekeningService.ganti_pin(
                **kwargs
            )
            kondisi_sesudah = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            assert kondisi_sesudah['pin'] != kwargs['pin_baru']
            Validator.verifikasi_pin(pin_input=kwargs['pin_baru'], pin_database=kondisi_sesudah['pin'])
            with pytest.raises(PinTidakCocok):
                Validator.verifikasi_pin(pin_input=kwargs['pin_lama'], pin_database=kondisi_sesudah['pin'])
            assert kondisi_sebelum['pin'] != kondisi_sesudah['pin']
            assert kondisi_sesudah['riwayat'] == kondisi_sebelum['riwayat'] + 1
            assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1

        def test_ganti_pin_dengan_pin_lama_salah(
                self, koneksi_test, siapkan_data_rekening_dan_nasabah
        ):


            kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
            kwargs['pin_lama'] = '789732'
            norek = kwargs['norek']

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            with pytest.raises(PinTidakCocok) as info_error:
                RekeningService.ganti_pin(
                    **kwargs
                )

            assert self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek) == kondisi_sebelum
            assert "PIN yang dimasukkan" in str(info_error.value)

        def test_ganti_pin_dengan_pin_baru_sama_dengan_pin_lama(
                self, koneksi_test, siapkan_data_rekening_dan_nasabah
        ):

            kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
            kwargs['pin_baru'] = kwargs['pin_lama']
            norek = kwargs['norek']

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            with pytest.raises(InputTidakValid) as info_error:
                RekeningService.ganti_pin(
                    **kwargs
                )

            assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
            assert "PiN baru tidak boleh sama dengan PIN lama" in str(info_error.value)

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
                pytest.param({"pin_baru": None}, "PIN tidak boleh kosong", id="pin None"),
                pytest.param({"pin_baru": ""}, "PIN tidak boleh kosong", id="pin kosong"),
                pytest.param({"pin_baru": " "}, "PIN tidak boleh kosong", id="pin spasi"),
                pytest.param(
                    {"pin_baru": "1234"}, "PIN harus berupa 6 digit angka", id="pin kurang"
                ),
                pytest.param(
                    {"pin_baru": "12345q"}, "PIN harus berupa 6 digit angka", id="pin ada huruf"
                ),
                pytest.param({"pin_lama": None}, "PIN tidak boleh kosong", id="pin None"),
                pytest.param({"pin_lama": ""}, "PIN tidak boleh kosong", id="pin kosong"),
                pytest.param({"pin_lama": " "}, "PIN tidak boleh kosong", id="pin spasi"),
                pytest.param(
                    {"pin_lama": "1234"}, "PIN harus berupa 6 digit angka", id="pin kurang"
                ),
                pytest.param(
                    {"pin_lama": "12345q"}, "PIN harus berupa 6 digit angka", id="pin ada huruf"
                )])

        def test_ganti_pin_dengan_input_tidak_valid(self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah, pesan_error):

            kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
            norek = siapkan_data_rekening_dan_nasabah['norek']

            kwargs.update(kwargs_salah)

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            with pytest.raises(InputTidakValid) as info_error:
                RekeningService.ganti_pin(**kwargs)


            assert self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek) == kondisi_sebelum
            assert pesan_error in str(info_error.value)

        @pytest.mark.parametrize(
            "kwargs_salah",
            [
                pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
                pytest.param({"norek": "4" * 16}, id="norek tidak ada"),
            ],
        )
        def tset_ganti_pin_dengan_identitas_tidak_ditemukan(self, koneksi_test, siapkan_data_rakening_dan_nasabah, kwargs_salah):

            kwargs = self._kwargs_valid(siapkan_data_rakening_dan_nasabah)
            norek = siapkan_data_rakening_dan_nasabah['norek']
            kwargs.update(kwargs_salah)

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            with pytest.raises(RekeningTidakDitemukan) as info_error:

                RekeningService.ganti_pin(**kwargs)

            assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
            assert "Rekening tidak terdaftar" in str(info_error.value)

        def test_ganti_pin_dengan_pin_benar_saat_rekening_terkunci(
                self, koneksi_test, siapkan_data_rekening_dan_nasabah
        ):


            kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
            norek = kwargs['norek']


            waktu_kunci = (
                    datetime.datetime.now() + datetime.timedelta(minutes=5)
            ).isoformat()

            koneksi_test.execute(
                """
                UPDATE rekening
                SET percobaan_gagal = 3, terkunci_sampai = ?
                WHERE norek = ?
                """,
                (waktu_kunci, norek),
            )
            koneksi_test.commit()

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)


            with pytest.raises(RekeningTerkunci) as info_error:
                RekeningService.ganti_pin(
                    **kwargs
                )


            data_rekening = koneksi_test.execute(
                "SELECT percobaan_gagal, terkunci_sampai FROM rekening WHERE norek = ?",
                (norek,),
            ).fetchone()


            assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
            assert data_rekening["percobaan_gagal"] == 3
            assert data_rekening["terkunci_sampai"] == waktu_kunci
            assert RekeningService.PESAN_REKENING_TERKUNCI in str(info_error.value)

        def test_ganti_pin_dengan_pin_lama_salah_mencatat_percobaan_gagal(
                self, koneksi_test, siapkan_data_rekening_dan_nasabah
        ):

            kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
            norek = kwargs['norek']
            kwargs['pin_lama'] = '112357'

            kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

            percobaan_sebelum = koneksi_test.execute(
                "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
            ).fetchone()["percobaan_gagal"]

            assert percobaan_sebelum == 0

            with pytest.raises(PinTidakCocok) as info_error:
                RekeningService.ganti_pin(
                    **kwargs
                )


            percobaan_sesudah = koneksi_test.execute(
                "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
            ).fetchone()["percobaan_gagal"]



            assert percobaan_sesudah == 1
            assert self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek) == kondisi_sebelum
            assert "PIN yang dimasukkan salah" in str(info_error.value)
