import pytest, datetime
from pytest_cov.plugin import pytest_addoption

from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.utils.utility import JenisTransaksi
from bank_djago.services.exceptions import InputTidakValid

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


class TestBukaRekening:

    @pytest.fixture
    def siapkan_data_nasabah(self, koneksi_test):
        koneksi_test.execute(
            "INSERT INTO nasabah (nama, alamat, nik) VALUES (?,?,?)",
            ("Nasabah Pengujian", "Jln.thmarin", "1111222233334444"),
        )
        koneksi_test.commit()

        return {"nik": "1111222233334444"}


    @staticmethod
    def _ambil_kondisi_nasabah(koneksi, nik):

        return {
            'jumlah_rekening':
                koneksi.execute('SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?',(nik,)).fetchone()[0],
            'audit':koneksi.execute("SELECT COUNT(*) FROM audit WHERE nik = ? AND aksi = 'pembukaan_rekening'",(nik,)).fetchone()[0]
        }

    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik':data['nik'],
            'pilihan': 3,
            'setor_awal': 100_000_000,
        'pin' :"123456"

        }
    def test_buka_rekening_happy_path(self, koneksi_test, siapkan_data_nasabah):

        kwargs = self._kwargs_valid(siapkan_data_nasabah)
        nik = kwargs['nik']
        kondisi_sebelum = self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)


        RekeningService.buka_rekening(**kwargs)

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE nik_pemilik = ? AND level = 3",(nik,)).fetchone()
        norek = data_rekening['norek']

        riwayat_pembukaan = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",(norek,)).fetchone()
        riwayat_setor = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal'",(norek,)).fetchone()
        transaksi = koneksi_test.execute('SELECT * FROM transaksi WHERE norek_tujuan = ? AND jenis = ?',(norek, JenisTransaksi.SETOR_AWAL.value)).fetchone()

        kondisi_sesudah = self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)

        assert kondisi_sesudah['jumlah_rekening'] == kondisi_sebelum['jumlah_rekening'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1
        assert riwayat_setor is not None
        assert riwayat_pembukaan is not None
        assert data_rekening['saldo'] == kwargs['setor_awal']
        assert transaksi is not None
        assert transaksi['nominal'] == kwargs['setor_awal']

    @pytest.mark.parametrize("level_rekening", [1, 2, 3, 4])
    def test_buka_rekening_dengan_setor_awal_tidak_memenuhi(
        self, koneksi_test, siapkan_data_nasabah, level_rekening
    ):

        kwargs = self._kwargs_valid(siapkan_data_nasabah)
        nik = kwargs['nik']
        kwargs['pilihan'] = level_rekening
        kwargs['setor_awal'] = jenis_rekening[level_rekening]['minimal_setor'] - 1

        kondisi_sebelum = self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.buka_rekening(
                **kwargs
            )

        assert self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik) == kondisi_sebelum
        assert "saldo minimal setoran awal" in str(info_error.value)

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
            pytest.param({'pilihan': 5}, "Level rekening tidak tersedia",id='target lebih'),
            pytest.param({'pilihan':'abc'}, 'Level rekening harus berupa angka', id='target huruf'),
            pytest.param({'pilihan': 0}, "Level rekening tidak boleh 0 atau negatif",id= 'target nol'),
            pytest.param({'pilihan': -1} ,"Level rekening tidak boleh 0 atau negatif", id='taret negatif'),

            pytest.param({'setor_awal': 'absg'},"Setor awal harus berupa angka", id='setor huruf'),
            pytest.param({'setor_awal': True},"Setor awal harus berupa angka", id='setor boolean')

        ])

    def test_buka_rekening_dengan_input_tidak_valid(self,koneksi_test, siapkan_data_nasabah, pesan_error, kwargs_salah):

        nik = siapkan_data_nasabah['nik']
        kwargs = self._kwargs_valid(siapkan_data_nasabah)
        kondisi_sebelum = self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)
        kwargs.update(kwargs_salah)

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.buka_rekening(**kwargs)

        assert kondisi_sebelum == self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)
        assert pesan_error in str(info_error.value)



    @pytest.mark.parametrize('level_rekening',[1,2,3,4])
    def test_buka_rekening_dengan_setor_awal_tepat_memenuhi(self, koneksi_test, siapkan_data_nasabah, level_rekening):

        kwargs = self._kwargs_valid(siapkan_data_nasabah)
        nik = kwargs['nik']
        kwargs['setor_awal'] = jenis_rekening[level_rekening]['minimal_setor']
        kwargs['pilihan'] = level_rekening
        kondisi_sebelum = self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)


        RekeningService.buka_rekening(**kwargs)

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE nik_pemilik = ? AND level = ?",(nik,level_rekening)).fetchone()
        norek = data_rekening['norek']

        riwayat_pembukaan = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",(norek,)).fetchone()
        riwayat_setor = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal'",(norek,)).fetchone()
        transaksi = koneksi_test.execute('SELECT * FROM transaksi WHERE norek_tujuan = ? AND jenis = ?',(norek, JenisTransaksi.SETOR_AWAL.value)).fetchone()

        kondisi_sesudah = self._ambil_kondisi_nasabah(koneksi=koneksi_test, nik=nik)

        assert kondisi_sesudah['jumlah_rekening'] == kondisi_sebelum['jumlah_rekening'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1
        assert riwayat_setor is not None
        assert riwayat_pembukaan is not None
        assert data_rekening['saldo'] == kwargs['setor_awal']
        assert transaksi is not None
        assert transaksi['nominal'] == kwargs['setor_awal']