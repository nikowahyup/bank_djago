
import pytest, datetime

from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.services.exceptions import (InputTidakValid, StatusTidakValid, RekeningTidakDitemukan, RekeningTerkunci, LevelRekeningTidakValid, PinTidakCocok)
from bank_djago.core.rekening import (
    RekeningReguler,
    RekeningPrioritas,
    RekeningGold,
    RekeningPlatinum,
)


reguler = RekeningReguler(norek="1234", pin="1234", pemilik=None)
prioritas = RekeningPrioritas(norek="1234", pin="1234", pemilik=None)
gold = RekeningGold(norek="1234", pin="1234", pemilik=None)
platinum = RekeningPlatinum(norek="1234", pin="1234", pemilik=None)


jenis_rekening = {
    1: {
        "minimal_upgrade": 0,
        "limit_sisa": reguler.limit_sisa,
        "minimal_setor": reguler.saldosetor_min,
    },
    2: {
        "minimal_upgrade": 3_000_000,
        "limit_sisa": prioritas.limit_sisa,
        "minimal_setor": prioritas.saldosetor_min,
    },
    3: {
        "minimal_upgrade": 50_000_000,
        "limit_sisa": gold.limit_sisa,
        "minimal_setor": gold.saldosetor_min,
    },
    4: {
        "minimal_upgrade": 200_000_000,
        "limit_sisa": platinum.limit_sisa,
        "minimal_setor": platinum.saldosetor_min,
    },
}

def konversi_waktu(waktu):
    return datetime.date.fromisoformat(waktu) if waktu is not None else None


class TestDowngradeRekening:
    @staticmethod
    def _ambil_kondisi_rekening(koneksi, norek):
        rekening = koneksi.execute('SELECT limit_sisa, terakhir_ubah_rekening, level FROM rekening WHERE norek = ?',(norek,)).fetchone()

        return {
            'data_rekening' : rekening if rekening is not None else None,
            'riwayat' : koneksi.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis ='penurunan rekening'",(norek,)).fetchone()[0],
            'audit':koneksi.execute("SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'penurunan_level_rekening'",(norek,)).fetchone()[0]
        }

    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik':data['nik'],
            'norek':data['norek'],
            'pin' : data['pin'],
            'target_level' : 2
        }


    @pytest.mark.parametrize('level_target',[2,1])
    def test_turunkan_rekening_happy_path(self, koneksi_test, siapkan_rekening_siap_diturunkan, level_target):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        kwargs['target_level'] = level_target
        norek = kwargs['norek']

        rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi_test)

        assert rekening.saldo >= rekening.saldosetor_min
        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        data_rekening_sebelum = kondisi_sebelum['data_rekening']
        assert data_rekening_sebelum['level'] == 3
        assert data_rekening_sebelum['limit_sisa'] == rekening.limit_sisa
        assert data_rekening_sebelum['terakhir_ubah_rekening'] is None

        RekeningService.downgrade_rekening(
            **kwargs
        )

        kondisi_sesudah = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        data_rekening_sesudah = kondisi_sesudah['data_rekening']

        assert kondisi_sesudah['riwayat'] == kondisi_sebelum['riwayat'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1
        assert data_rekening_sesudah['limit_sisa'] != data_rekening_sebelum['limit_sisa']
        assert data_rekening_sesudah['level'] == level_target
        assert data_rekening_sesudah['terakhir_ubah_rekening'] == datetime.date.today().isoformat()


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
            ),
            pytest.param({'target_level': 5}, "Level rekening tidak tersedia",id='target lebih'),
            pytest.param({'target_level':'abc'}, 'Level rekening harus berupa angka', id='target huruf'),
            pytest.param({'target_level': 0}, "Level rekening tidak boleh 0 atau negatif",id= 'target nol'),
            pytest.param({'target_level': -1} ,"Level rekening tidak boleh 0 atau negatif", id='taret negatif')])


    def test_turunkan_rekening_input_tidak_valid(self,koneksi_test, siapkan_rekening_siap_diturunkan, pesan_error, kwargs_salah):


        norek = siapkan_rekening_siap_diturunkan['norek']
        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        kwargs.update(kwargs_salah)
        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(InputTidakValid) as info_error:

            RekeningService.upgrade_rekening(**kwargs)

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert pesan_error in str(info_error.value)



    def test_turunkan_rekening_dengan_waktu_ubah_memenuhi(
            self, koneksi_test, siapkan_rekening_siap_diturunkan
    ):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        norek = kwargs['norek']
        hari_ini = datetime.date.today()
        update_terakhir_ubah = hari_ini - datetime.timedelta(days=1)

        koneksi_test.execute(
            "UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",
            (update_terakhir_ubah.isoformat(), norek),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert kondisi_sebelum['data_rekening']['level'] == 3
        assert kondisi_sebelum['data_rekening']['terakhir_ubah_rekening'] == update_terakhir_ubah.isoformat()
        assert kondisi_sebelum['data_rekening']['limit_sisa'] == jenis_rekening[3]['limit_sisa']

        RekeningService.downgrade_rekening(
            **kwargs
        )

        kondisi_sesudah = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        data_rekening_sesudah = kondisi_sesudah['data_rekening']

        assert kondisi_sesudah['riwayat'] == kondisi_sebelum['riwayat'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1
        assert data_rekening_sesudah['limit_sisa'] != kondisi_sebelum['data_rekening']['limit_sisa']
        assert data_rekening_sesudah['level'] == kwargs['target_level']
        assert data_rekening_sesudah['terakhir_ubah_rekening'] == hari_ini.isoformat()

    @pytest.mark.parametrize("status_invalid", ["blokir", "tutup"])
    def test_turunkan_rekening_dengan_status_rekening_tidak_valid(
        self, koneksi_test, siapkan_rekening_siap_diturunkan, status_invalid
    ):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        norek = kwargs['norek']

        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?", (status_invalid, norek)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)


        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.downgrade_rekening(
                **kwargs
            )

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert "Rekening Anda saat ini sedang" in str(info_error.value)

    def test_turunkan_rekening_lebih_dari_sekali_sehari(
        self, koneksi_test, siapkan_rekening_siap_diturunkan
    ):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        norek = kwargs['norek']

        hari_ini = datetime.date.today()

        koneksi_test.execute(
            "UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",
            (hari_ini.isoformat(), norek),
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        limit_sisa_level_ini = jenis_rekening[3]['limit_sisa']

        assert kondisi_sebelum['data_rekening']['level'] == 3
        assert kondisi_sebelum['data_rekening']['terakhir_ubah_rekening'] == hari_ini.isoformat()
        assert kondisi_sebelum['data_rekening']['limit_sisa'] == limit_sisa_level_ini

        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.downgrade_rekening(
                **kwargs
            )

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert "rekening hanya bisa dilakukan 1 kali" in str(info_error.value)

    @pytest.mark.parametrize(
        "level_sekarang, level_tujuan, exception, pesan_error",
        [
            (1, 1, StatusTidakValid, "ini sudah level terendah"),
            (3, 3, LevelRekeningTidakValid, "harus lebih rendah dari level saat ini"),
            (3, 4, LevelRekeningTidakValid, "harus lebih rendah dari level saat ini"),
            (1, 2, StatusTidakValid, "ini sudah level terendah"),
        ],
    )
    def test_turunkan_rekening_dengan_pilihan_tidak_valid(
        self,
        koneksi_test,
        siapkan_rekening_siap_diturunkan,
        level_sekarang,
        level_tujuan,
        exception,
        pesan_error,
    ):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        kwargs['target_level'] = level_tujuan
        norek = kwargs['norek']

        koneksi_test.execute(
            "UPDATE rekening SET level = ? WHERE norek = ?", (level_sekarang, norek)
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(exception) as info_error:
            RekeningService.downgrade_rekening(
                **kwargs
            )

        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert pesan_error in str(info_error.value)


    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek": "4" * 16}, id="norek tidak ada"),
        ],
    )

    def test_turunkan_rekening_dengan_identitas_tidak_ditemukan(self, koneksi_test, kwargs_salah, siapkan_rekening_siap_diturunkan):

        norek = siapkan_rekening_siap_diturunkan['norek']
        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            RekeningService.downgrade_rekening(**kwargs)


        assert kondisi_sebelum == self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
        assert "Rekening tidak terdaftar" in str(info_error.value)


    def test_turunkan_rekening_pin_ssalah_mencatat_percobaan_gagal(self, koneksi_test, siapkan_rekening_siap_diturunkan):

        kwargs = self._kwargs_valid(siapkan_rekening_siap_diturunkan)
        kwargs['pin'] = '123457'
        norek = kwargs['norek']

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0


        kondisi_sebelum = self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)

        with pytest.raises(PinTidakCocok) as info_error:
            RekeningService.downgrade_rekening(**kwargs)

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert (
            self._ambil_kondisi_rekening(koneksi_test, norek)
            == kondisi_sebelum
        )
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_turunkan_rekening_dengan_kondisi_rekening_terkunci_dan_masukkan_pin_benar(
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
                RekeningService.downgrade_rekening(**kwargs)

            waktu_kunci_sesudah = koneksi_test.execute(
                "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
            ).fetchone()["terkunci_sampai"]

            assert waktu_kunci_sesudah == waktu_kunci
            assert (
                    self._ambil_kondisi_rekening(koneksi=koneksi_test, norek=norek)
                    == kondisi_sebelum
            )
            assert RekeningService.PESAN_REKENING_TERKUNCI in str(info_error.value)