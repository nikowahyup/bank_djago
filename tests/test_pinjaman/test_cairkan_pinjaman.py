

import pytest, datetime
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.utils.utility import StatusPinjaman
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.exceptions import (InputTidakValid, StatusTidakValid, PinjamanTidakDitemukan, RekeningTidakDitemukan, RekeningTidakSesuai,PinTidakCocok, RekeningTerkunci)


class TestCairkanPinjaman:




    @pytest.fixture
    def pinjaman_siap_cair(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,norek, nominal_pinjaman, bunga,tenor,sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (1, norek, 2_000_000, 0.12, 6, 0, "disetujui"),
        )

        koneksi_test.commit()

        return {"nik": nik, "norek": norek, "id_pinjaman": 1}

    @staticmethod
    def _ambil_kondisi_pencairan(koneksi, norek, id_pinjaman):
        pinjaman = koneksi.execute(
            "SELECT status, cicilan_tetap, sisa_pokok, tanggal_pencairan FROM pinjaman WHERE id = ?",
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
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pencairan pinjaman'",
                (norek,),
            ).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pencairan_pinjaman'",
                (norek,),
            ).fetchone()[0],
        }

    @staticmethod
    def _kwargs_valid(data):
        return {
            'nik':data['nik'],
            'norek_pencairan':data['norek'],
            'id_pinjaman' : 1,
            'pin': data['pin']
        }


    def test_cairkan_pinjaman_happy_path(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pinjaman_siap_cair):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_pinjaman = kwargs['id_pinjaman']

        kondisi_sebelum = self._ambil_kondisi_pencairan(koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman)
        data_pinjaman = koneksi_test.execute("SELECT status, cicilan_tetap, sisa_pokok, tanggal_pencairan FROM pinjaman WHERE id = ?",(id_pinjaman,)).fetchone()
        kondisi_sebelum.pop('pinjaman')
        assert data_pinjaman['status'] == StatusPinjaman.DISETUJUI.value
        assert data_pinjaman['cicilan_tetap'] == 0
        assert data_pinjaman['sisa_pokok'] == 0
        assert data_pinjaman['tanggal_pencairan'] is None


        total_pencairan = PinjamanService.cairkan_pinjaman(**kwargs)

        kondisi_sesudah = self._ambil_kondisi_pencairan(koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman)
        data_pinjaman_sesudah = koneksi_test.execute("SELECT status, cicilan_tetap, sisa_pokok, tanggal_pencairan FROM pinjaman WHERE id = ?",(id_pinjaman,)).fetchone()
        kondisi_sesudah.pop('pinjaman')

        assert data_pinjaman_sesudah['status'] == StatusPinjaman.AKTIF.value
        assert data_pinjaman_sesudah['cicilan_tetap'] != 0
        assert data_pinjaman_sesudah['sisa_pokok'] != 0
        assert data_pinjaman_sesudah['tanggal_pencairan'] == datetime.date.today().isoformat()
        assert total_pencairan == 2_000_000
        assert kondisi_sesudah['transaksi'] == kondisi_sebelum['transaksi'] + 1
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
                {"id_pinjaman": -99}, "ID pinjaman tidak valid", id="id negatif"
            ),
            # bukti urutan: cek murah sebelum PIN, jadi PIN salah tidak sempat dihitung
            pytest.param(
                {"id_pinjaman": -99, "pin": "123457"},
                "ID pinjaman tidak valid",
                id="id cacat dan pin salah",
            ),
            pytest.param(
                {"norek_pencairan": "2" * 15, "pin": "123457"},
                "Jumlah digit nomor rekening tidak valid",
                id="norek cacat dan pin salah",
            ),
        ],
    )
    def test_pencairan_dengan_input_tidak_valid(
        self,
        koneksi_test,
        pinjaman_siap_cair,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
        pesan_error,
    ):

        norek = siapkan_data_rekening_dan_nasabah['norek']
        id_pinjaman = pinjaman_siap_cair['id_pinjaman']
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)

        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi_test, norek, id_pinjaman
        )

        with pytest.raises(InputTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert (
            self._ambil_kondisi_pencairan(koneksi_test, norek, id_pinjaman)
            == kondisi_sebelum
        )
        assert pesan_error in str(info_error.value)


    def test_cairkan_pinjaman_dengan_id_tidak_terdaftar(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, pinjaman_siap_cair
    ):

        id_pinjaman_benar = pinjaman_siap_cair["id_pinjaman"]
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        kwargs['id_pinjaman'] = 99

        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman_benar
        )

        with pytest.raises(PinjamanTidakDitemukan) as info_error:
            PinjamanService.cairkan_pinjaman(
                **kwargs
            )

        assert (
            self._ambil_kondisi_pencairan(
                koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman_benar
            )
            == kondisi_sebelum
        )
        assert "Pinjaman tidak ditemukan" in str(info_error.value)

    def test_cairkan_pinjaman_dengan_norek_pencairan_tidak_terdaftar_sebagai_pemilik_pinjaman(
        self, koneksi_test, siapkan_data_rekening_penerima, pinjaman_siap_cair
    ):
        norek = siapkan_data_rekening_penerima["norek"]
        nik = siapkan_data_rekening_penerima["nik"]
        pin = siapkan_data_rekening_penerima["pin"]
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )

        with pytest.raises(RekeningTidakSesuai) as info_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman, pin=pin
            )

        assert (
            self._ambil_kondisi_pencairan(
                koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
            )
            == kondisi_sebelum
        )
        assert "Rekening ini tidak terdaftar sebagai pemilik pinjaman" in str(
            info_error.value
        )

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek_pencairan": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_pencairan_dengan_identitas_tidak_ditemukan(
        self,
        koneksi_test,
        pinjaman_siap_cair,
        siapkan_data_rekening_dan_nasabah,
        kwargs_salah,
    ):
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        kwargs.update(kwargs_salah)

        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi_test, norek, id_pinjaman
        )

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            PinjamanService.cairkan_pinjaman(**kwargs)

        assert (
            self._ambil_kondisi_pencairan(koneksi_test, norek, id_pinjaman)
            == kondisi_sebelum
        )
        assert "Rekening tidak terdaftar" in str(info_error.value)

    @pytest.mark.parametrize("status_salah", ["diajukan", "aktif", "lunas", "ditolak"])
    def test_pencairan_status_pinjaman_salah(
        self,
        koneksi_test,
        status_salah,
        pinjaman_siap_cair,
        siapkan_data_rekening_dan_nasabah,
    ):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_pinjaman = kwargs['id_pinjaman']
        koneksi_test.execute(
            "UPDATE pinjaman SET status = ? WHERE id = ?", (status_salah, id_pinjaman)
        )
        koneksi_test.commit()


        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(
                **kwargs
            )

        assert (
            self._ambil_kondisi_pencairan(koneksi_test, norek, id_pinjaman)
            == kondisi_sebelum
        )
        assert "Pinjaman tidak berstatus disetujui" in str(info_error.value)

    @pytest.mark.parametrize("status_rekening", ["blokir", "tutup"])
    def test_pencairan_dengan_status_rekening_selain_aktif(
        self,
        koneksi_test,
        status_rekening,
        pinjaman_siap_cair,
        siapkan_data_rekening_dan_nasabah,
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_pinjaman = kwargs['id_pinjaman']
        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?", (status_rekening, norek)
        )

        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )
        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(
                **kwargs
            )

        assert (
            self._ambil_kondisi_pencairan(koneksi_test, norek, id_pinjaman)
            == kondisi_sebelum
        )
        assert "saat ini sedang" in str(info_error.value)

    def test_pencairan_ganda(
        self, koneksi_test, pinjaman_siap_cair, siapkan_data_rekening_dan_nasabah
    ):

        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_pinjaman = kwargs['id_pinjaman']

        PinjamanService.cairkan_pinjaman(
            **kwargs
        )
        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
        )
        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(
                **kwargs
            )

        assert (
            self._ambil_kondisi_pencairan(
                koneksi=koneksi_test, norek=norek, id_pinjaman=id_pinjaman
            )
            == kondisi_sebelum
        )
        assert "Pinjaman tidak berstatus disetujui" in str(info_error.value)

    def test_pencairan_pin_salah_mencatat_percobaan_gagal(
        self, koneksi_test, pinjaman_siap_cair, siapkan_data_rekening_dan_nasabah
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_pinjaman = kwargs['id_pinjaman']
        kwargs['pin'] = '123457'

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi_test, norek, id_pinjaman
        )

        with pytest.raises(PinTidakCocok) as info_error:
            PinjamanService.cairkan_pinjaman(
                **kwargs
            )

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert (
            self._ambil_kondisi_pencairan(koneksi_test, norek, id_pinjaman)
            == kondisi_sebelum
        )
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_pencairan_rekening_terkunci_dengan_pin_benar(
        self, koneksi_test, pinjaman_siap_cair, siapkan_data_rekening_dan_nasabah
    ):
        kwargs = self._kwargs_valid(siapkan_data_rekening_dan_nasabah)
        norek = kwargs['norek_pencairan']
        id_pinjaman = kwargs['id_pinjaman']

        waktu_kunci = (
            datetime.datetime.now() + datetime.timedelta(minutes=5)
        ).isoformat()
        koneksi_test.execute(
            "UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",
            (waktu_kunci, norek),
        )
        koneksi_test.commit()
        kondisi_sebelum = self._ambil_kondisi_pencairan(
            koneksi_test, norek, id_pinjaman
        )

        with pytest.raises(RekeningTerkunci) as info_error:
            PinjamanService.cairkan_pinjaman(
                **kwargs
            )

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert (
            self._ambil_kondisi_pencairan(koneksi_test, norek, id_pinjaman)
            == kondisi_sebelum
        )
        assert (
            "Rekening terkunci sementara karena terlalu banyak percobaan PIN salah"
            in str(info_error.value)
        )


