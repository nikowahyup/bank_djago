import pytest, datetime


from bank_djago.services.exceptions import (InputTidakValid, StatusTidakValid, PinTidakCocok, RekeningTerkunci, RekeningTidakSesuai, RekeningTidakDitemukan,PinjamanTidakDitemukan)
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.utils.utility import StatusPinjaman, JenisTransaksi
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository





class TestBayarCicilan:

    @pytest.fixture
    def pinjaman_siap_dibayar_cicilannya(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        koneksi_test.execute(
            """INSERT INTO pinjaman (
            id, norek, nominal_pinjaman, bunga, tenor, sisa_pokok, status,
            tanggal_pencairan, tanggal_jatuh_tempo, cicilan_terbayar, cicilan_tetap
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                norek,
                2_000_000,
                0.12,
                6,
                2_000_000,
                "aktif",
                datetime.date.today().isoformat(),
                (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                0,
                345_103,
            ),
        )
        koneksi_test.commit()
        return {"nik": nik, "norek": norek, "id_pinjaman": 1}

    @staticmethod
    def _ambil_kondisi_cicilan(koneksi, norek, id_pinjaman):
        pinjaman = koneksi.execute(
            "SELECT status, cicilan_terbayar, sisa_pokok, tanggal_jatuh_tempo FROM pinjaman WHERE id = ?",
            (id_pinjaman,),
        ).fetchone()
        return {
            "pinjaman": tuple(pinjaman) if pinjaman else None,
            "saldo": RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi),
            "transaksi": koneksi.execute(
                "SELECT COUNT(*) FROM transaksi WHERE jenis_referensi = 'pinjaman' AND id_referensi = ?",
                (id_pinjaman,),
            ).fetchone()[0],
            "riwayat": koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pembayaran cicilan'",
                (norek,),
            ).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pembayaran_cicilan_pinjaman'",
                (norek,),
            ).fetchone()[0],
        }
    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik':data['nik'],
            'norek_pembayaran' : data['norek'],
            'pin' : data['pin'],
            'id_pinjaman' : 1,
            'hari_ini': datetime.date.today() + datetime.timedelta(days=30)
        }

    def test_bayar_cicilan_happy_path(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pinjaman_siap_dibayar_cicilannya):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']

        kondisi_sebelum = self._ambil_kondisi_cicilan(koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman)
        kondisi_sebelum.pop('pinjaman')
        data_pinjaman = koneksi_test.execute("SELECT status, cicilan_tetap, sisa_pokok, cicilan_terbayar,tanggal_jatuh_tempo FROM pinjaman WHERE id = ?",(id_pinjaman,)).fetchone()


        assert data_pinjaman['status'] == StatusPinjaman.AKTIF.value
        assert data_pinjaman['cicilan_tetap'] == 345_103
        assert data_pinjaman['sisa_pokok'] == 2_000_000
        assert data_pinjaman['tanggal_jatuh_tempo'] == kwargs['hari_ini'].isoformat()
        assert data_pinjaman['cicilan_terbayar'] == 0

        PinjamanService.bayar_cicilan(**kwargs)

        kondisi_sesudah = self._ambil_kondisi_cicilan(koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman)
        kondisi_sesudah.pop('pinjaman')
        data_pinjaman_sesudah = koneksi_test.execute("SELECT status, cicilan_tetap, sisa_pokok, cicilan_terbayar,tanggal_jatuh_tempo FROM pinjaman WHERE id = ?",(id_pinjaman,)).fetchone()

        assert data_pinjaman_sesudah['cicilan_tetap'] == data_pinjaman['cicilan_tetap']
        assert data_pinjaman_sesudah['status'] == data_pinjaman['status']
        assert data_pinjaman_sesudah['sisa_pokok'] != 2_000_000
        assert data_pinjaman_sesudah['cicilan_terbayar'] == data_pinjaman['cicilan_terbayar'] + 1
        assert data_pinjaman_sesudah['tanggal_jatuh_tempo'] == (kwargs['hari_ini'] + datetime.timedelta(days=31)).isoformat()

        assert kondisi_sesudah['riwayat'] == kondisi_sebelum['riwayat'] + 1
        assert kondisi_sesudah['audit'] == kondisi_sebelum['audit'] + 1
        assert kondisi_sesudah['transaksi'] == kondisi_sebelum['transaksi'] + 1



    def test_bayar_cicilan_sebelum_jatuh_tempo(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        pinjaman_siap_dibayar_cicilannya,
    ):

        hari_ini = datetime.date.today() - datetime.timedelta(days=1)
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs['hari_ini'] = hari_ini
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']
        kondisi_sebelum = self._ambil_kondisi_cicilan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )
        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.bayar_cicilan(
                **kwargs
            )

        assert (
            self._ambil_kondisi_cicilan(
                koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
            )
            == kondisi_sebelum
        )
        assert "baru boleh dibayar" in str(info_error.value)

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
            # norek pembayaran
            pytest.param(
                {"norek_pembayaran": None},
                "Nomor rekening tidak boleh kosong",
                id="norek None",
            ),
            pytest.param(
                {"norek_pembayaran": ""},
                "Nomor rekening tidak boleh kosong",
                id="norek kosong",
            ),
            pytest.param(
                {"norek_pembayaran": " "},
                "Nomor rekening tidak boleh kosong",
                id="norek spasi",
            ),
            pytest.param(
                {"norek_pembayaran": "12345abcde123456"},
                "Nomor rekening tidak boleh mengandung huruf",
                id="norek ada huruf",
            ),
            pytest.param(
                {"norek_pembayaran": "2" * 15},
                "Jumlah digit nomor rekening tidak valid",
                id="norek 15 digit",
            ),
            pytest.param(
                {"norek_pembayaran": "2" * 17},
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
            # ID pinjaman
            pytest.param(
                {"id_pinjaman": None}, "ID pinjaman harus berupa angka", id="id None"
            ),
            pytest.param(
                {"id_pinjaman": "abc"}, "ID pinjaman harus berupa angka", id="id huruf"
            ),
            pytest.param(
                {"id_pinjaman": 1.5}, "ID pinjaman harus berupa angka", id="id desimal"
            ),
            pytest.param(
                {"id_pinjaman": True}, "ID pinjaman harus berupa angka", id="id bool"
            ),
            pytest.param({"id_pinjaman": 0}, "ID pinjaman tidak valid", id="id nol"),
            pytest.param(
                {"id_pinjaman": -9}, "ID pinjaman tidak valid", id="id negatif"
            ),
            # bukti urutan: cek murah sebelum PIN
            pytest.param(
                {"id_pinjaman": -9, "pin": "123457"},
                "ID pinjaman tidak valid",
                id="id cacat dan pin salah",
            ),
            pytest.param(
                {"norek_pembayaran": "2" * 15, "pin": "123457"},
                "Jumlah digit nomor rekening tidak valid",
                id="norek cacat dan pin salah",
            ),
        ],
    )
    def test_bayar_cicilan_dengan_input_tidak_valid(
            self,
            koneksi_test,
            pinjaman_siap_dibayar_cicilannya,
            siapkan_data_rekening_dan_nasabah,
            kwargs_salah,
            pesan_error,
    ):
        norek = pinjaman_siap_dibayar_cicilannya["norek"]
        id_pinjaman = pinjaman_siap_dibayar_cicilannya["id_pinjaman"]

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)

        with pytest.raises(InputTidakValid) as info_error:
            PinjamanService.bayar_cicilan(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)
                == kondisi_sebelum
        )
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek_pembayaran": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_bayar_cicilan_dengan_identitas_tidak_ditemukan(
            self,
            koneksi_test,
            pinjaman_siap_dibayar_cicilannya,
            siapkan_data_rekening_dan_nasabah,
            kwargs_salah,
    ):
        norek = pinjaman_siap_dibayar_cicilannya["norek"]
        id_pinjaman = pinjaman_siap_dibayar_cicilannya["id_pinjaman"]

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            PinjamanService.bayar_cicilan(**kwargs)

        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)
                == kondisi_sebelum
        )
        assert "Rekening tidak terdaftar" in str(info_error.value)

    @pytest.mark.parametrize("status_salah", ["blokir", "tutup"])
    def test_bayar_cicilan_dengan_status_rekening_tidak_valid(
            self,
            koneksi_test,
            pinjaman_siap_dibayar_cicilannya,
            siapkan_data_rekening_dan_nasabah,
            status_salah,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']

        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?",
            (
                status_salah,
                norek,
            ),
        )
        koneksi_test.commit()

        kondisi_sebelum = self._ambil_kondisi_cicilan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.bayar_cicilan(
                **kwargs
            )

        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)
                == kondisi_sebelum
        )
        assert f"Rekening Anda saat ini sedang di{status_salah}" in str(
            info_error.value
        )

    def test_bayar_cicilan_setelah_8_hari(
            self,
            koneksi_test,
            pinjaman_siap_dibayar_cicilannya,
            siapkan_data_rekening_dan_nasabah,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']

        jatuh_tempo_pinjaman = koneksi_test.execute(
            "SELECT tanggal_jatuh_tempo FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()["tanggal_jatuh_tempo"]
        jatuh_tempo_pinjaman = datetime.date.fromisoformat(jatuh_tempo_pinjaman)
        hari_ini = jatuh_tempo_pinjaman + datetime.timedelta(days=8)
        kwargs['hari_ini'] = hari_ini
        denda = 345

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        PinjamanService.bayar_cicilan(
            **kwargs
        )

        total_bayar = 345_103 + denda

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=id_pinjaman, koneksi=koneksi_test
        )
        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()
        assert transaksi is not None
        assert transaksi["jenis"] == JenisTransaksi.PEMBAYARAN_CICILAN.value
        assert transaksi["nominal"] == data_pinjaman["cicilan_tetap"]
        assert transaksi["biaya"] == denda

        assert saldo_sesudah == saldo_sebelum - total_bayar

    def test_bayar_cicilan_terakhir_untuk_pelunasan(
            self,
            koneksi_test,
            pinjaman_siap_dibayar_cicilannya,
            siapkan_data_rekening_dan_nasabah,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']

        tenor_pinjaman = koneksi_test.execute(
            "SELECT tenor FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()["tenor"]
        hari_ini = datetime.date.today() + datetime.timedelta(days=30 * tenor_pinjaman)
        kwargs['hari_ini'] = hari_ini
        sisa_pokok_update = 341_648
        koneksi_test.execute(
            "UPDATE pinjaman SET cicilan_terbayar = 5,sisa_pokok = ? WHERE id = ? AND norek = ?",
            (sisa_pokok_update, id_pinjaman, norek),
        )
        koneksi_test.commit()

        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=id_pinjaman, koneksi=koneksi_test
        )
        cicilan_terbayar_sebelum = data_pinjaman["cicilan_terbayar"]
        sisa_pokok_sebelum = data_pinjaman["sisa_pokok"]

        assert cicilan_terbayar_sebelum == 5
        assert sisa_pokok_sebelum == sisa_pokok_update

        PinjamanService.bayar_cicilan(
            **kwargs
        )

        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=id_pinjaman, koneksi=koneksi_test
        )

        sisa_pokok = data_pinjaman["sisa_pokok"]
        status = data_pinjaman["status"]
        cicilan_terbayar = data_pinjaman["cicilan_terbayar"]

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()
        assert transaksi is not None
        assert transaksi["jenis"] == JenisTransaksi.PEMBAYARAN_CICILAN.value
        assert transaksi["nominal"] == data_pinjaman["cicilan_tetap"]
        assert transaksi["id_referensi"] == id_pinjaman
        id_transaksi = transaksi["id"]

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembayaran cicilan' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pembayaran_cicilan_pinjaman' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()

        assert sisa_pokok == 0
        assert status == "lunas"
        assert cicilan_terbayar == 6
        assert riwayat is not None
        assert audit is not None

    def test_bayar_cicilan_dengan_id_pinjaman_tidak_terdaftar(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = 1
        kwargs['id_pinjaman'] = 99

        kondisi_sebelum = self._ambil_kondisi_cicilan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )

        with pytest.raises(PinjamanTidakDitemukan) as info_error:
            PinjamanService.bayar_cicilan(
               **kwargs
            )

        assert (
                self._ambil_kondisi_cicilan(
                    koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
                )
                == kondisi_sebelum
        )
        assert "Pinjaman tidak ditemukan" in str(info_error.value)

    def test_bayar_cicilan_dengan_norek_pembayaran_tidak_terdaftar_sebagai_pemilik_pinjaman(
            self,
            koneksi_test,
            siapkan_data_rekening_dan_nasabah,
            siapkan_data_rekening_penerima,
            pinjaman_siap_dibayar_cicilannya,
    ):
        norek_pemilik = pinjaman_siap_dibayar_cicilannya["norek"]
        id_pinjaman = pinjaman_siap_dibayar_cicilannya["id_pinjaman"]

        nik = siapkan_data_rekening_penerima["nik"]
        norek = siapkan_data_rekening_penerima["norek"]
        pin = siapkan_data_rekening_penerima["pin"]

        kondisi_pemilik_sebelum = self._ambil_kondisi_cicilan(
            koneksi_test, norek_pemilik, id_pinjaman
        )
        kondisi_pemanggil_sebelum = self._ambil_kondisi_cicilan(
            koneksi_test, norek, id_pinjaman
        )

        with pytest.raises(RekeningTidakSesuai) as info_error:
            PinjamanService.bayar_cicilan(
                nik=nik,
                norek_pembayaran=norek,
                pin=pin,
                id_pinjaman=id_pinjaman,
                hari_ini=datetime.date.today(),
            )

        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek_pemilik, id_pinjaman)
                == kondisi_pemilik_sebelum
        )
        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)
                == kondisi_pemanggil_sebelum
        )
        assert "Rekening ini tidak terdaftar sebagai pemilik pinjaman" in str(
            info_error.value
        )

    def test_bayar_cicilan_pin_salah_mencatat_percobaan_gagal(
            self, koneksi_test, pinjaman_siap_dibayar_cicilannya, siapkan_data_rekening_dan_nasabah
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']
        kwargs['pin'] = '123457'

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        kondisi_sebelum = self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)

        with pytest.raises(PinTidakCocok) as info_error:
            PinjamanService.bayar_cicilan(
                **kwargs
            )

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)
                == kondisi_sebelum
        )
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_bayar_cicilan_rekening_terkunci_dengan_pin_benar(
            self,
            koneksi_test,
            pinjaman_siap_dibayar_cicilannya,
            siapkan_data_rekening_dan_nasabah,
    ):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pembayaran']
        id_pinjaman = kwargs['id_pinjaman']

        waktu_kunci = (
                datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat()
        koneksi_test.execute(
            "UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",
            (waktu_kunci, norek),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)

        with pytest.raises(RekeningTerkunci) as info_error:
            PinjamanService.bayar_cicilan(
                **kwargs
            )

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert (
                self._ambil_kondisi_cicilan(koneksi_test, norek, id_pinjaman)
                == kondisi_sebelum
        )
        assert (
                "Rekening terkunci sementara karena terlalu banyak percobaan PIN salah"
                in str(info_error.value)
        )
