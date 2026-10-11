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
PengajuanTidakDitemukan
)
NOREK_PENERIMA_TIDAK_DIPAKAI = '88547'

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
            ({'metode':'cek'},'Metode penyelesaian saldo tidak tersedia',InputTidakValid)
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


    def test_penutupan_rekening_dengan_tidak_ada_pengajuan_yang_disetujui(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'tarik'

        koneksi_test.execute(
            "INSERT INTO pengajuan_rekening (norek,jenis,alasan,waktu_pengajuan,status) VALUES (?,?,?,?,?)",
            (
                norek,
                "tutup",
                "Penutupan rekening untuk pengujian",
                datetime.datetime.now().isoformat(),
                "diajukan",
            ),
        )
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == "aktif"
        assert saldo_sebelum != 0

        with pytest.raises(PengajuanTidakDitemukan) as info_error:
            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek,pin=pin,metode=metode)

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
        assert "Belum ada persetujuan penutupan" in str(info_error.value)

    @pytest.mark.parametrize('status_salah',['blokir','tutup'])
    def test_penutupan_rekening_dengan_status_rekening_tidak_valid(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pengajuan_penutupan_siap_diselesaikan,status_salah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'tarik'

        koneksi_test.execute("UPDATE rekening SET status = ? WHERE norek = ?",(status_salah, norek))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == status_salah
        assert saldo_sebelum != 0

        with pytest.raises(StatusTidakValid) as info_error:
            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode)

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
        assert status_sesudah == status_salah
        assert riwayat is None
        assert audit is None
        assert f"Rekening Anda saat ini sedang di{status_salah}" in str(info_error.value)


    @pytest.mark.parametrize("status_salah",['aktif','jatuh tempo'])
    def test_penutupan_rekening_dengan_rekening_punya_deposito_masih_berjalan(self,koneksi_test, siapkan_data_rekening_dan_nasabah, status_salah,pengajuan_penutupan_siap_diselesaikan):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'tarik'

        tanggal_buka = datetime.date.today()
        jatuh_tempo = tanggal_buka + datetime.timedelta(days=30)
        koneksi_test.execute("INSERT INTO deposito (norek, nominal, bunga, lama_bulan, tanggal_buka, jatuh_tempo,status) VALUES (?,?,?,?,?,?,?)",(norek,1_000_000,0.03, 1,tanggal_buka.isoformat(),jatuh_tempo.isoformat(),status_salah))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == 'aktif'
        assert saldo_sebelum != 0

        with pytest.raises(StatusTidakValid) as info_error:
            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode)


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
        assert status_sesudah == status_sebelum
        assert riwayat is None
        assert audit is None
        assert "Rekening masih mempunyai deposito berjalan" in str(info_error.value)



    @pytest.mark.parametrize("status_salah",["diajukan","disetujui","aktif"])
    def test_penutupan_rekening_dengan_rekening_punya_pinjaman_masih_berjalan(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pengajuan_penutupan_siap_diselesaikan,status_salah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'tarik'

        koneksi_test.execute("INSERT INTO pinjaman (norek, nominal_pinjaman, bunga, tenor, sisa_pokok, status) VALUES (?,?,?,?,?,?)",(norek, 1_000_000,0.1,6,0,status_salah))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == 'aktif'
        assert saldo_sebelum != 0

        with pytest.raises(StatusTidakValid) as info_error:

            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode)

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
        assert status_sesudah == status_sebelum
        assert riwayat is None
        assert audit is None
        assert "Rekening masih mempunyai pinjaman berjalan" in str(info_error.value)


    def test_penutupan_rekening_dengan_metode_langsung_tutup_happy_path(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pengajuan_penutupan_siap_diselesaikan):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = "langsung tutup"

        koneksi_test.execute("UPDATE rekening SET saldo = 0 WHERE norek = ?",(norek,))
        koneksi_test.commit()


        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == "aktif"
        assert saldo_sebelum == 0

        hasil = PengajuanService.selesaikan_penutupan(
            nik=nik, norek=norek, pin=pin, metode=metode
        )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        saldo_sesudah = data_rekening_sesudah["saldo"]
        status_sesudah = data_rekening_sesudah["status"]

        jumlah_transaksi = koneksi_test.execute(
            "SELECT COUNT(*) FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()[0]

        assert jumlah_transaksi == 0

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening'",
            (norek,),
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ? AND aksi = 'penutupan_saldo_kosong'",
            (norek,),
        ).fetchone()
        assert hasil == saldo_sebelum

        assert saldo_sesudah == 0
        assert status_sesudah == "tutup"
        assert riwayat is not None
        assert audit is not None


    @pytest.mark.parametrize("metode, norek_penerima, aksi_audit,pesan_error, saldo_mutasi",[('tarik',None,"penarikan_saldo_penutupan","Silahkan pilih metode langsung tutup",0),
                                                       ('transfer',NOREK_PENERIMA_TIDAK_DIPAKAI,"pemindahan_saldo_penutupan","Silahkan pilih metode langsung tutup",0),
                                                                                            ("langsung tutup",None,"penutupan_saldo_kosong","Silahkan pilih metode tarik atau transfer",1_000_000)])
    def test_penutupan_rekening_dengan_metode_saldo_tidak_sesuai(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pengajuan_penutupan_siap_diselesaikan,metode, norek_penerima,aksi_audit,saldo_mutasi,pesan_error):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']

        koneksi_test.execute("UPDATE rekening SET saldo = ? WHERE norek = ?",(saldo_mutasi,norek))
        koneksi_test.commit()


        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == "aktif"
        assert saldo_sebelum == saldo_mutasi

        with pytest.raises(StatusTidakValid) as info_error:
            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode, norek_penerima=norek_penerima)

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
            "SELECT * FROM audit WHERE norek = ? AND aksi = ?",
            (norek,aksi_audit),
        ).fetchone()

        assert transaksi is None
        assert saldo_sesudah == saldo_sebelum
        assert status_sesudah == status_sebelum
        assert riwayat is None
        assert audit is None
        assert pesan_error in str(info_error.value)


    def test_penutupan_rekening_dengan_metode_transfer_happy_path(self, koneksi_test, siapkan_data_rekening_dan_nasabah, siapkan_data_rekening_penerima, pengajuan_penutupan_siap_diselesaikan):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'transfer'
        norek_penerima = siapkan_data_rekening_penerima['norek']

        data_rekening_pengirim = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        saldo_pengirim_sebelum = data_rekening_pengirim['saldo']
        status_pengirim_sebelum = data_rekening_pengirim['status']

        assert saldo_pengirim_sebelum != 0
        assert status_pengirim_sebelum == 'aktif'

        data_rekening_penerima = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek_penerima,)).fetchone()
        saldo_penerima_sebelum = data_rekening_penerima['saldo']
        status_penerima = data_rekening_penerima['status']

        assert status_penerima == 'aktif'

        hasil = PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode, norek_penerima=norek_penerima)

        data_pengirim_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        status_pengirim_sesudah = data_pengirim_sesudah['status']
        saldo_pengirim_sesudah = data_pengirim_sesudah['saldo']

        saldo_penerima_sesudah = koneksi_test.execute("SELECT saldo FROM rekening WHERE norek = ?",(norek_penerima,)).fetchone()['saldo']

        transaksi = koneksi_test.execute("SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",(norek, norek_penerima)).fetchone()
        assert transaksi is not None
        assert transaksi['jenis'] == JenisTransaksi.PEMINDAHAN_SALDO_PENUTUPAN.value
        assert transaksi['nominal'] == hasil


        id_transaksi = transaksi['id']
        riwayat_pengirim = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening' AND transaksi_id = ?",(norek,id_transaksi)).fetchone()
        riwayat_penerima = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'terima saldo' AND transaksi_id = ?",(norek_penerima, id_transaksi)).fetchone()

        audit_pengirim = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pemindahan_saldo_penutupan' AND transaksi_id = ?",(norek, id_transaksi)).fetchone()
        audit_penerima = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'penerimaan_saldo_penutupan' AND transaksi_id = ?",(norek_penerima,id_transaksi)).fetchone()

        assert status_pengirim_sesudah == 'tutup'
        assert hasil == saldo_pengirim_sebelum
        assert saldo_pengirim_sesudah == 0
        assert saldo_penerima_sesudah == saldo_penerima_sebelum + hasil
        assert riwayat_pengirim is not None
        assert riwayat_penerima is not None
        assert audit_pengirim is not None
        assert audit_penerima is not None
        assert transaksi['saldo_sumber_sebelum'] == saldo_pengirim_sebelum
        assert transaksi['saldo_tujuan_sebelum'] == saldo_penerima_sebelum
        assert transaksi['saldo_sumber_sesudah'] == saldo_pengirim_sesudah
        assert transaksi['saldo_tujuan_sesudah'] == saldo_penerima_sesudah



    def test_penutupan_rekening_dengan_metode_transfer_norek_penerima_adalah_norek_sendiri(self, koneksi_test, siapkan_data_rekening_dan_nasabah, pengajuan_penutupan_siap_diselesaikan):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'transfer'

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sebelum = data_rekening["saldo"]
        status_sebelum = data_rekening["status"]

        assert status_sebelum == "aktif"
        assert saldo_sebelum != 0

        with pytest.raises(StatusTidakValid) as info_error:
            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode, norek_penerima=norek)


        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sesudah = data_rekening_sesudah["saldo"]
        status_sesudah = data_rekening_sesudah["status"]


        transaksi = koneksi_test.execute("SELECT * FROM transaksi WHERE norek_sumber = ? AND jenis = ?",(norek, JenisTransaksi.PEMINDAHAN_SALDO_PENUTUPAN.value)).fetchone()
        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pemindahan_saldo_penutupan'",(norek,)).fetchone()

        assert transaksi is None
        assert status_sesudah == status_sebelum
        assert saldo_sesudah == saldo_sebelum
        assert riwayat is None
        assert audit is None
        assert "Tidak dapat transfer ke nomor rekening sendiri" in str(info_error.value)

    @pytest.mark.parametrize("status_salah",['blokir','tutup'])
    def test_penutupan_rekening_dengan_metode_transfer_dengan_status_rekening_penerima_tidak_valid(self, koneksi_test, siapkan_data_rekening_dan_nasabah, siapkan_data_rekening_penerima,pengajuan_penutupan_siap_diselesaikan, status_salah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        metode = 'transfer'
        norek_penerima = siapkan_data_rekening_penerima['norek']

        koneksi_test.execute("UPDATE rekening SET status = ? WHERE norek = ?",(status_salah, norek_penerima))
        koneksi_test.commit()

        data_rekening_pengirim = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        saldo_pengirim_sebelum = data_rekening_pengirim['saldo']
        status_pengirim_sebelum = data_rekening_pengirim['status']

        assert saldo_pengirim_sebelum != 0
        assert status_pengirim_sebelum == 'aktif'

        data_rekening_penerima = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek_penerima,)).fetchone()
        saldo_penerima_sebelum = data_rekening_penerima['saldo']
        status_penerima = data_rekening_penerima['status']

        assert status_penerima == status_salah

        with pytest.raises(StatusTidakValid) as info_error:
            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin,metode=metode, norek_penerima=norek_penerima)

        data_pengirim_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        status_pengirim_sesudah = data_pengirim_sesudah['status']
        saldo_pengirim_sesudah = data_pengirim_sesudah['saldo']

        saldo_penerima_sesudah = koneksi_test.execute("SELECT saldo FROM rekening WHERE norek = ?",(norek_penerima,)).fetchone()['saldo']
        jumlah_transaksi = koneksi_test.execute(
            "SELECT COUNT(*) FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()[0]
        assert jumlah_transaksi == 0

        riwayat_pengirim = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening'",(norek,)).fetchone()
        riwayat_penerima = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'terima saldo'",(norek_penerima,)).fetchone()

        audit_pengirim = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pemindahan_saldo_penutupan'",(norek,)).fetchone()
        audit_penerima = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'penerimaan_saldo_penutupan'",(norek_penerima,)).fetchone()


        assert status_pengirim_sesudah == status_pengirim_sebelum
        assert saldo_penerima_sesudah == saldo_penerima_sebelum
        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum
        assert riwayat_penerima is None
        assert riwayat_pengirim is None
        assert audit_penerima is None
        assert audit_pengirim is None
        assert f"Rekening penerima saat ini sedang di{status_penerima}" in str(info_error.value)



    def test_penutupan_rekening_dengan_metode_langsung_tutup_tapi_input_memasukkan_norek_penerima_juga(self, koneksi_test, siapkan_data_rekening_dan_nasabah, siapkan_data_rekening_penerima,pengajuan_penutupan_siap_diselesaikan):
        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        pin = siapkan_data_rekening_dan_nasabah['pin']
        norek_penerima = siapkan_data_rekening_penerima['norek']
        metode = 'langsung tutup'

        data_rekening_pengirim = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        saldo_pengirim_sebelum = data_rekening_pengirim['saldo']
        status_pengirim_sebelum = data_rekening_pengirim['status']

        assert saldo_pengirim_sebelum != 0
        assert status_pengirim_sebelum == 'aktif'

        data_rekening_penerima = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek_penerima,)).fetchone()
        saldo_penerima_sebelum = data_rekening_penerima['saldo']
        status_penerima = data_rekening_penerima['status']

        assert status_penerima == 'aktif'
        with pytest.raises(StatusTidakValid) as info_error:

            PengajuanService.selesaikan_penutupan(nik=nik, norek=norek, pin=pin, metode=metode,norek_penerima=norek_penerima)


        data_pengirim_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        status_pengirim_sesudah = data_pengirim_sesudah['status']
        saldo_pengirim_sesudah = data_pengirim_sesudah['saldo']

        saldo_penerima_sesudah = koneksi_test.execute("SELECT saldo FROM rekening WHERE norek = ?",(norek_penerima,)).fetchone()['saldo']
        jumlah_transaksi = koneksi_test.execute(
            "SELECT COUNT(*) FROM transaksi WHERE norek_sumber = ?", (norek,)
        ).fetchone()[0]
        assert jumlah_transaksi == 0

        riwayat_pengirim = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penutupan rekening'",(norek,)).fetchone()
        riwayat_penerima = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'terima saldo'",(norek_penerima,)).fetchone()

        audit_pengirim = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pemindahan_saldo_penutupan'",(norek,)).fetchone()
        audit_penerima = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'penerimaan_saldo_penutupan'",(norek_penerima,)).fetchone()


        assert status_pengirim_sesudah == status_pengirim_sebelum
        assert saldo_penerima_sesudah == saldo_penerima_sebelum
        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum
        assert riwayat_penerima is None
        assert riwayat_pengirim is None
        assert audit_penerima is None
        assert audit_pengirim is None
        assert "rekening yang saldonya sudah kosong. Silahkan pilih metode tarik atau transfer" in str(info_error.value)




