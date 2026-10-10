import datetime

import pytest

from bank_djago import JenisTransaksi
from bank_djago.conftest import siapkan_data_rekening_dan_nasabah, koneksi_test
from bank_djago.services.rekening.pengajuan_service import PengajuanService
from bank_djago.services.exceptions import (
    NikTidakSesuai,
    RekeningTidakDitemukan,
    PinTidakCocok,
    InputTidakValid,
    StatusTidakValid,
    SudahAdaPengajuan,
)


class TestAjukanPenutupanRekening:

    def test_ajukan_penutupan_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        alasan = "Ajukan penutupan untuk pengujian"

        status_rekening = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]
        assert status_rekening == "aktif"

        PengajuanService.ajukan_penutupan(nik=nik, norek=norek, alasan=alasan, pin=pin)

        data_pengajuan = koneksi_test.execute(
            "SELECT * FROM pengajuan_rekening WHERE norek = ?", (norek,)
        ).fetchone()
        jenis_pengajuan = data_pengajuan["jenis"]
        status_pengajuan = data_pengajuan["status"]
        alasan_pengajuan = data_pengajuan["alasan"]
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pengajuan_penutupan_rekening'",
            (norek,),
        ).fetchone()

        status_rekening_sesudah = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]

        assert status_rekening_sesudah == status_rekening
        assert jenis_pengajuan == "tutup"
        assert status_pengajuan == "diajukan"
        assert alasan_pengajuan == alasan
        assert audit is not None

    @pytest.mark.parametrize(
        "kwargs_salah, exception, pesan_error",
        [
            (
                {"nik": "1111"},
                NikTidakSesuai,
                "tidak terdaftar sebagai pemilik rekening",
            ),
            ({"norek": "7777"}, RekeningTidakDitemukan, "tidak terdaftar"),
            ({"pin": "123457"}, PinTidakCocok, "PIN yang dimasukkan salah"),
            ({"alasan": ""}, InputTidakValid, "Alasan penutupan tidak boleh kosong"),
        ],
    )
    def test_ajukan_penutupan_dengan_input_tidak_valid(
        self,
        kwargs_salah,
        exception,
        pesan_error,
        siapkan_data_rekening_dan_nasabah,
        koneksi_test,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        alasan = "Ajukan penutupan untuk pengujian"

        kwargs = {"nik": nik, "norek": norek, "pin": pin, "alasan": alasan}
        kwargs.update(kwargs_salah)

        status_rekening = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]
        assert status_rekening == "aktif"

        with pytest.raises(exception) as info_error:

            PengajuanService.ajukan_penutupan(**kwargs)

        data_pengajuan = koneksi_test.execute(
            "SELECT * FROM pengajuan_rekening WHERE norek = ?", (norek,)
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pengajuan_penutupan_rekening'",
            (norek,),
        ).fetchone()
        status_rekening_sesudah = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]

        assert status_rekening_sesudah == status_rekening
        assert data_pengajuan is None
        assert audit is None
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize("status_salah", ["blokir", "tutup"])
    def test_ajukan_penutupan_dengan_status_rekening_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, status_salah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        alasan = "Ajukan penutupan untuk pengujian"
        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?", (status_salah, norek)
        )
        koneksi_test.commit()

        status_sebelum = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]
        assert status_sebelum == status_salah

        with pytest.raises(StatusTidakValid) as info_error:
            PengajuanService.ajukan_penutupan(
                nik=nik, norek=norek, pin=pin, alasan=alasan
            )

        data_pengajuan = koneksi_test.execute(
            "SELECT * FROM pengajuan_rekening WHERE norek = ?", (norek,)
        ).fetchone()
        status_sesudah = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'pengajuan_penutupan_rekening'",
            (norek,),
        ).fetchone()

        assert data_pengajuan is None
        assert status_sesudah == status_sebelum
        assert "Rekening Anda saat ini sedang" in str(info_error.value)
        assert audit is None

    def test_ajukan_penutupan_tetapi_sudah_pernah_mengajukan_dan_belum_diproses_admin(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        alasan = "Ajukan penutupan untuk pengujian"

        status_rekening = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]

        PengajuanService.ajukan_penutupan(nik=nik, norek=norek, pin=pin, alasan=alasan)

        status_rekening_sesudah = koneksi_test.execute(
            "SELECT status FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["status"]

        assert status_rekening_sesudah == status_rekening

        with pytest.raises(SudahAdaPengajuan) as info_error:
            PengajuanService.ajukan_penutupan(
                nik=nik, norek=norek, pin=pin, alasan=alasan
            )

        data_pengajuan_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM pengajuan_rekening WHERE norek = ?", (norek,)
        ).fetchone()[0]

        audit_kedua = koneksi_test.execute(
            "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pengajuan_penutupan_rekening'",
            (norek,),
        ).fetchone()[0]

        assert data_pengajuan_sesudah == 1
        assert audit_kedua == 1
        assert "Anda sudah mengajukan penutupan sebelumnya" in str(info_error.value)


class TestSelesaikanPenutupanRekening:

    @pytest.fixture
    def pengajuan_penutupan_siap_diselesaikan(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        koneksi_test.execute(
            "INSERT INTO pengajuan_rekening (norek,jenis,alasan,waktu_pengajuan,status) VALUES (?,?,?,?,?)",
            (
                norek,
                "tutup",
                "Penutupan rekening untuk pengujian",
                datetime.datetime.now().isoformat(),
                "disetujui",
            ),
        )
        koneksi_test.commit()

    def test_penutupan_rekening_metode_tarik_happy_path(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        pengajuan_penutupan_siap_diselesaikan,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        metode = "tarik"

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == "aktif"
        assert saldo_sebelum != 0

        hasil = PengajuanService.selesaikan_penutupan(
            nik=nik, norek=norek, pin=pin, metode=metode
        )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        saldo_sesudah = data_rekening_sesudah["saldo"]
        status_sesudah = data_rekening_sesudah["status"]

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND saldo_sumber_sebelum = ? AND nominal = ?",
            (norek, saldo_sebelum, saldo_sebelum),
        ).fetchone()
        assert transaksi is not None
        id_transaksi = transaksi["id"]
        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'penarikan_saldo_penutupan' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        assert hasil == saldo_sebelum
        assert transaksi["jenis"] == JenisTransaksi.PENARIKAN_SALDO_PENUTUPAN.value
        assert saldo_sesudah == 0
        assert status_sesudah == "tutup"
        assert riwayat is not None
        assert audit is not None

    @pytest.mark.parametrize(
        "kwargs_salah, pesan_error,exception",
        [
            (
                {"nik": "12345"},
                "tidak terdaftar sebagai pemilik rekening",
                NikTidakSesuai,
            ),
            ({"norek": "8765"}, "Rekening tidak terdaftar", RekeningTidakDitemukan),
            ({"pin": "123457"}, "PIN yang dimasukkan salah", PinTidakCocok),
            (
                {"metode": "transfer", "norek_penerima": "88754"},
                "penerima tidak terdaftar",
                RekeningTidakDitemukan,
            ),
            (
                {"metode": "transfer", "norek_penerima": None},
                "rekening penerima wajib diisi",
                InputTidakValid,
            ),
        ],
    )
    def test_penutupan_rekening_dengan_input_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        pengajuan_penutupan_siap_diselesaikan,
        kwargs_salah,
        pesan_error,
        exception,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]
        metode = "tarik"

        kwargs = {"nik": nik, "norek": norek, "pin": pin, "metode": metode}
        kwargs.update(kwargs_salah)

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == "aktif"
        assert saldo_sebelum != 0

        with pytest.raises(exception) as info_error:
            PengajuanService.selesaikan_penutupan(**kwargs)

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        saldo_sesudah = data_rekening_sesudah["saldo"]
        status_sesudah = data_rekening_sesudah["status"]

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND saldo_sumber_sebelum = ? AND nominal = ?",
            (norek, saldo_sebelum, saldo_sebelum),
        ).fetchone()
        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening'",
            (norek,),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'penarikan_saldo_penutupan'",
            (norek,),
        ).fetchone()

        assert transaksi is None
        assert saldo_sesudah == saldo_sebelum
        assert status_sesudah == "aktif"
        assert riwayat is None
        assert audit is None
        assert pesan_error in str(info_error.value)
