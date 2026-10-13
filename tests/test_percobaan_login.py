import datetime

import pytest

from bank_djago.services.exceptions import PinTidakCocok,RekeningTerkunci, RekeningTidakDitemukan
from bank_djago.services.rekening.rekening_service import RekeningService



class TestPercobaanLogin:

    def test_1_kali_gagal_lalu_benar_untuk_percobaan_kedua(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin_benar = siapkan_data_rekening_dan_nasabah['pin']
        pin_salah = '123457'
        jumlah_percobaan_sebelum = koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?",(norek,)).fetchone()['percobaan_gagal']
        waktu_terkunci_sebelum = \
        koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'terkunci_sampai']
        waktu_terkunci_sebelum = datetime.datetime.fromisoformat(
            waktu_terkunci_sebelum) if waktu_terkunci_sebelum is not None else None

        assert jumlah_percobaan_sebelum == 0
        assert waktu_terkunci_sebelum is None
        with pytest.raises(PinTidakCocok) as info_error:

            RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_salah)

        jumlah_percobaan_sesudah = koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?",(norek,)).fetchone()['percobaan_gagal']
        waktu_terkunci_sesudah  = koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?",(norek,)).fetchone()['terkunci_sampai']
        waktu_terkunci_sesudah  = datetime.datetime.fromisoformat(waktu_terkunci_sesudah ) if waktu_terkunci_sesudah  is not None else None

        assert jumlah_percobaan_sesudah == 1
        assert waktu_terkunci_sesudah  is None
        assert "PIN yang dimasukkan salah" in str(info_error.value)

        RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_benar)

        jumlah_percobaan_sesudah = koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?",(norek,)).fetchone()['percobaan_gagal']
        waktu_terkunci_sesudah  = koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?",(norek,)).fetchone()['terkunci_sampai']
        waktu_terkunci_sesudah  = datetime.datetime.fromisoformat(waktu_terkunci_sesudah ) if waktu_terkunci_sesudah  is not None else None

        assert jumlah_percobaan_sesudah == 0
        assert waktu_terkunci_sesudah is None



    def test_2_kali_gagal_login_lalu_benar_untuk_percobaan_ketiga(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin_benar = siapkan_data_rekening_dan_nasabah['pin']

        koneksi_test.execute("UPDATE rekening SET percobaan_gagal = 2 WHERE norek = ?",(norek,))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        jumlah_percobaan = data_rekening['percobaan_gagal']
        waktu_terkunci = datetime.datetime.fromisoformat(data_rekening['terkunci_sampai']) if data_rekening['terkunci_sampai'] is not None else None

        assert jumlah_percobaan == 2
        assert waktu_terkunci is None

        RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_benar)

        jumlah_percobaan_sesudah = koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?",(norek,)).fetchone()['percobaan_gagal']
        waktu_terkunci_sesudah  = koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?",(norek,)).fetchone()['terkunci_sampai']
        waktu_terkunci_sesudah  = datetime.datetime.fromisoformat(waktu_terkunci_sesudah ) if waktu_terkunci_sesudah  is not None else None

        assert jumlah_percobaan_sesudah == 0
        assert waktu_terkunci_sesudah is None

    def test_3_kali_gagal_login_dikunci_sementara_pada_percobaan_keempat(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin_salah = "123457"
        pin_benar = siapkan_data_rekening_dan_nasabah['pin']

        koneksi_test.execute("UPDATE rekening SET percobaan_gagal = 2 WHERE norek = ?",(norek,))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        jumlah_percobaan = data_rekening['percobaan_gagal']
        waktu_terkunci = datetime.datetime.fromisoformat(data_rekening['terkunci_sampai']) if data_rekening['terkunci_sampai'] is not None else None

        assert jumlah_percobaan == 2
        assert waktu_terkunci is None

        with pytest.raises(PinTidakCocok) as info_error:
            RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_salah)

        jumlah_percobaan_sesudah = koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?",(norek,)).fetchone()['percobaan_gagal']
        waktu_terkunci_sesudah  = koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?",(norek,)).fetchone()['terkunci_sampai']
        waktu_terkunci_sesudah  = datetime.datetime.fromisoformat(waktu_terkunci_sesudah ) if waktu_terkunci_sesudah  is not None else None


        assert jumlah_percobaan_sesudah == 3
        assert waktu_terkunci_sesudah is not None
        assert "PIN yang dimasukkan salah" in str(info_error.value)

        with pytest.raises(RekeningTerkunci) as info_error:
            RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_benar)

        jumlah_percobaan_sesudah = \
        koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'percobaan_gagal']
        waktu_terkunci_sesudah = \
        koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'terkunci_sampai']
        waktu_terkunci_sesudah = datetime.datetime.fromisoformat(
            waktu_terkunci_sesudah) if waktu_terkunci_sesudah is not None else None

        assert jumlah_percobaan_sesudah == 3
        assert waktu_terkunci_sesudah is not None
        assert "Coba beberapa saat lagi" in str(info_error.value)

    def test_tunggu_waktu_kunci_sementara_lalu_coba_login_kembali(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin_benar = siapkan_data_rekening_dan_nasabah['pin']

        satu_menit = (datetime.datetime.now() - datetime.timedelta(minutes=1)).isoformat()
        koneksi_test.execute("UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",(satu_menit,norek))
        koneksi_test.commit()

        RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_benar)

        jumlah_percobaan_sesudah = \
        koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'percobaan_gagal']
        waktu_terkunci_sesudah = \
        koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'terkunci_sampai']
        waktu_terkunci_sesudah = datetime.datetime.fromisoformat(
            waktu_terkunci_sesudah) if waktu_terkunci_sesudah is not None else None

        assert jumlah_percobaan_sesudah == 0
        assert waktu_terkunci_sesudah is None

    def test_coba_login_dengan_pin_salah_saat_waktu_kunci_masih_aktif(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin_salah = '123475'
        waktu_kunci = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
        koneksi_test.execute("UPDATE rekening SET percobaan_gagal = 3,terkunci_sampai = ? WHERE norek = ?",(waktu_kunci, norek))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        jumlah_percobaan = data_rekening['percobaan_gagal']
        waktu_terkunci = datetime.datetime.fromisoformat(data_rekening['terkunci_sampai']) if data_rekening['terkunci_sampai'] is not None else None

        assert jumlah_percobaan == 3
        assert waktu_terkunci is not None

        with pytest.raises(RekeningTerkunci) as info_error:
            RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_salah)



        jumlah_percobaan_sesudah = \
        koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'percobaan_gagal']
        waktu_terkunci_sesudah = \
        koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'terkunci_sampai']
        waktu_terkunci_sesudah = datetime.datetime.fromisoformat(
            waktu_terkunci_sesudah) if waktu_terkunci_sesudah is not None else None

        assert jumlah_percobaan_sesudah == 3
        assert waktu_terkunci_sesudah == waktu_terkunci
        assert "Coba beberapa saat lagi" in str(info_error.value)

    def test_pin_salah_setelah_kunci_berakhir_mengunci_ulang(self, koneksi_test, siapkan_data_rekening_dan_nasabah):
        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin_salah = '123457'
        waktu_kunci_lampau = (datetime.datetime.now() - datetime.timedelta(minutes=1)).isoformat()
        koneksi_test.execute("UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",(waktu_kunci_lampau, norek))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        jumlah_percobaan = data_rekening['percobaan_gagal']
        waktu_terkunci = datetime.datetime.fromisoformat(data_rekening['terkunci_sampai']) if data_rekening['terkunci_sampai'] is not None else None

        assert jumlah_percobaan == 3
        assert waktu_terkunci is not None

        with pytest.raises(PinTidakCocok) as info_error:
            RekeningService.verifikasi_login_pin(nik_aktif=nik, norek_aktif=norek, pin_input=pin_salah)



        jumlah_percobaan_sesudah = \
        koneksi_test.execute("SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'percobaan_gagal']
        waktu_terkunci_sesudah = \
        koneksi_test.execute("SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)).fetchone()[
            'terkunci_sampai']
        waktu_terkunci_sesudah = datetime.datetime.fromisoformat(
            waktu_terkunci_sesudah) if waktu_terkunci_sesudah is not None else None

        assert jumlah_percobaan_sesudah == 3
        assert waktu_terkunci_sesudah > datetime.datetime.now()
        assert "PIN yang dimasukkan salah" in str(info_error.value)


    @pytest.mark.parametrize("kwargs_salah",[({"nik_aktif":"6353728548293"}),({"norek_aktif":"999999999999"})
                                             ])
    def test_percobaan_login_dengan_norek_atau_nik_salah(self, koneksi_test, siapkan_data_rekening_dan_nasabah,kwargs_salah):
        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']

        kwargs = {'nik_aktif':nik,
                  'norek_aktif':norek,
                  'pin_input':pin}
        kwargs.update(kwargs_salah)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            RekeningService.verifikasi_login_pin(**kwargs)

        assert "Rekening tidak terdaftar" in str(info_error.value)