import pytest, datetime


from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.deposito.deposito_service import StatusDeposito
from bank_djago.utils.utility import JenisAro
from bank_djago.services.deposito.deposito_service import DepositoService
from bank_djago.services.exceptions import InputTidakValid
from bank_djago.services.exceptions import (
    RekeningTidakDitemukan,
    StatusTidakValid,
    RekeningTerkunci,
    RekeningTidakSesuai,
    JenisAroTidakValid,
    PinTidakCocok,
    DepositoTidakDitemukan
)

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

    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik':data['nik'],
            'norek_pemberhentian':data['norek'],
            'pin':data['pin'],
            'id_deposito':1
        }

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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
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

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pemberhentian']
        id_deposito = kwargs['id_deposito']

        koneksi_test.execute(
            "UPDATE rekening SET status = 'tutup' WHERE norek = ?", (norek,)
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )
        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.hentikan_aro(
               **kwargs
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


    @pytest.mark.parametrize("status_salah", ["jatuh tempo", "dicairkan"])
    def test_hentikan_aro_deposito_dengan_status_deposito_bukan_aktif(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
        status_salah,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pemberhentian']
        id_deposito = kwargs['id_deposito']

        koneksi_test.execute(
            "UPDATE deposito SET status = ? WHERE id = ?", (status_salah, id_deposito)
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.hentikan_aro(
               **kwargs
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
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        id_asli = deposito_aro_siap_dihentikan["id_deposito"]
        norek = kwargs['norek_pemberhentian']
        kwargs['id_deposito'] = 99

        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_asli
        )

        with pytest.raises(DepositoTidakDitemukan) as info_error:
            DepositoService.hentikan_aro(
                **kwargs
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_asli
            )
            == kondisi_sebelum
        )
        assert "Deposito tidak ditemukan" in str(info_error.value)

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

    def test_hentikan_aro_deposito_yang_sudah_non_aro(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        deposito_aro_siap_dihentikan,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        id_deposito = kwargs['id_deposito']
        norek = kwargs['norek_pemberhentian']

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
                **kwargs
            )

        assert (
            self._ambil_kondisi_deposito_sebelum_dihentikan(
                koneksi_test, norek, id_deposito
            )
            == kondisi_sebelum
        )
        assert "tidak menggunakan ARO" in str(info_error.value)

    def test_hentikan_aro_deposito_pin_salah_mencatat_percobaan_gagal(
        self,
        koneksi_test,
        deposito_aro_siap_dihentikan,
        siapkan_data_rekening_dan_nasabah,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['pin'] = '123457'
        norek = kwargs['norek_pemberhentian']
        id_deposito = kwargs['id_deposito']

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        kondisi_sebelum = self._ambil_kondisi_deposito_sebelum_dihentikan(
            koneksi_test, norek, id_deposito
        )

        with pytest.raises(PinTidakCocok) as info_error:
            DepositoService.hentikan_aro(
                **kwargs
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
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pemberhentian']
        id_deposito = kwargs['id_deposito']

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
                **kwargs
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