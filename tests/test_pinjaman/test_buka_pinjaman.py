import pytest, datetime


from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository

from bank_djago.utils.utility import StatusPinjaman
from bank_djago.services.exceptions import (InputTidakValid, RekeningTidakDitemukan, RekeningTerkunci,StatusTidakValid, PinTidakCocok)


class TestBukaPinjaman:

    @staticmethod
    def _hitung_jejak_pinjaman(koneksi, norek):
        return {
            'jumlah_pinjaman':koneksi.execute(
                "SELECT COUNT(*) FROM pinjaman WHERE norek = ?", (norek,)
            ).fetchone()[0],
            'riwayat':koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pembukaan pinjaman'",
                (norek,),
            ).fetchone()[0],
            'audit':koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pengajuan_pinjaman'",
                (norek,),
            ).fetchone()[0],

        }



    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik' : data['nik'],
            'norek' : data['norek'],
            'pin' : data['pin'],
            'nominal' : 1_000_000,
            'tenor':6
        }


    def test_ajukan_pinjaman_happy_path(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
        kondisi_sebelum = self._hitung_jejak_pinjaman(koneksi=koneksi_test, norek=norek)


        id_pinjaman = PinjamanService.ajukan_pinjaman(**kwargs)

        kondisi_sesudah = self._hitung_jejak_pinjaman(koneksi=koneksi_test, norek=norek)
        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(id_pinjaman=id_pinjaman, koneksi=koneksi_test)

        assert kondisi_sesudah['jumlah_pinjaman'] == kondisi_sebelum['jumlah_pinjaman'] + 1
        assert kondisi_sesudah['riwayat'] == kondisi_sebelum['riwayat'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1
        assert data_pinjaman['status'] == StatusPinjaman.DIAJUKAN.value
        assert data_pinjaman['tenor'] == 6
        assert data_pinjaman['tanggal_pencairan'] is None


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
            # tenor
            pytest.param(
                {"tenor": None}, "Jangka waktu harus berupa angka", id="tenor None"
            ),
            pytest.param(
                {"tenor": "abc"}, "Jangka waktu harus berupa angka", id="tenor huruf"
            ),
            pytest.param(
                {"tenor": 0}, "Pilihan tenor pinjaman tidak tersedia", id="tenor 0"
            ),
            pytest.param(
                {"tenor": -6}, "Pilihan tenor pinjaman tidak tersedia", id="tenor minus"
            ),
            pytest.param(
                {"tenor": 7},
                "Pilihan tenor pinjaman tidak tersedia",
                id="tenor tidak tersedia",
            ),
            # nominal
            pytest.param(
                {"nominal": None}, "Nominal harus berupa angka", id="nominal None"
            ),
            pytest.param(
                {"nominal": "abc"}, "Nominal harus berupa angka", id="nominal huruf"
            ),
            pytest.param(
                {"nominal": 0},
                "Nominal pinjaman di bawah batas minimal",
                id="nominal 0",
            ),
            pytest.param(
                {"nominal": -1_000_000},
                "Nominal pinjaman di bawah batas minimal",
                id="nominal minus",
            ),
            pytest.param(
                {"nominal": 999_999},
                "Nominal pinjaman di bawah batas minimal",
                id="nominal kurang",
            ),
            pytest.param(
                {"nominal": 50_000_001},
                "Nominal pinjaman melebihi batas maksimal",
                id="nominal lebih",
            ),
            # bukti urutan: cek murah sebelum PIN, jadi PIN salah tidak sempat dihitung
            pytest.param(
                {"nominal": 999_999, "pin": "123457"},
                "Nominal pinjaman di bawah batas minimal",
                id="nominal cacat dan pin salah",
            ),
            pytest.param(
                {"tenor": 7, "pin": "123457"},
                "Pilihan tenor pinjaman tidak tersedia",
                id="tenor cacat dan pin salah",
            ),
            pytest.param(
                {"norek": "2" * 15, "pin": "123457"},
                "Jumlah digit nomor rekening tidak valid",
                id="norek cacat dan pin salah",
            ),
        ],
    )
    def test_ajukan_pinjaman_dengan_input_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah, pesan_error
    ):

        norek = siapkan_data_rekening_dan_nasabah["norek"]


        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(InputTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_ajukan_pinjaman_dengan_identitas_tidak_ditemukan(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah
    ):

        norek = siapkan_data_rekening_dan_nasabah['norek']
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            PinjamanService.ajukan_pinjaman(**kwargs)

        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert "Rekening tidak terdaftar" in str(info_error.value)

    @pytest.mark.parametrize("status_rekening_salah", ["blokir", "tutup"])
    def test_ajukan_pinjaman_dengan_rekening_selain_aktif(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah, status_rekening_salah
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?",
            (status_rekening_salah, norek),
        )

        koneksi_test.commit()

        kondisi_sebelum = self._hitung_jejak_pinjaman(koneksi=koneksi_test, norek=norek)
        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(
                **kwargs
            )

        assert kondisi_sebelum == self._hitung_jejak_pinjaman(koneksi=koneksi_test, norek=norek)
        assert f"Rekening Anda saat ini sedang di{status_rekening_salah}" in str(
            info_error.value
        )

    @pytest.mark.parametrize("status_pinjaman_sebelumnya", ["diajukan", "disetujui"])
    def test_ajukan_pinjaman_saat_masih_ada_pinjaman_belum_disetujui_atau_masih_diajukan(
            self,
            koneksi_test,
            siapkan_data_rekening_dan_nasabah,
            status_pinjaman_sebelumnya,
    ):
        koneksi_test.execute(
            """INSERT INTO pinjaman (id, norek, nominal_pinjaman, bunga, tenor, sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                1_000_000,
                0.1,
                6,
                0,
                status_pinjaman_sebelumnya,
            ),
        )

        koneksi_test.commit()

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
        kondisi_sebelum = self._hitung_jejak_pinjaman(koneksi=koneksi_test, norek=norek)


        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(
                **kwargs
            )
        assert kondisi_sebelum == self._hitung_jejak_pinjaman(koneksi=koneksi_test, norek=norek)
        assert "masih memiliki pengajuan pinjaman" in str(info_error.value)

    def test_ajukan_pinjaman_pin_salah_mencatat_percobaan_gagal(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek']
        kwargs['pin'] = '123457'

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(PinTidakCocok) as info_error:
            PinjamanService.ajukan_pinjaman(
                **kwargs
            )

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_ajukan_pinjaman_rekening_terkunci_dengan_pin_benar(
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
        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(RekeningTerkunci) as info_error:
            PinjamanService.ajukan_pinjaman(
                **kwargs
            )

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert (
                "Rekening terkunci sementara karena terlalu banyak percobaan PIN salah"
                in str(info_error.value)
        )



