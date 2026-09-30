import datetime

import pytest

from bank_djago import TransaksiService, JenisTransaksi
from bank_djago.conftest import siapkan_data_rekening_dan_nasabah, koneksi_test
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader

from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.services.exceptions import (
    InputTidakValid,
    NikTidakSesuai,
    RekeningTidakDitemukan,
    StatusTidakValid,
)
import bank_djago.penyimpanan.repositories.audit_repository as audit_repo_module


class TestSetortunai:

    def test_setor_tunai_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        hasil = TransaksiService.setor_tunai(
            nik_masuk=nik, norek=norek, nominal=nominal
        )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ?", (norek,)
        ).fetchone()

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_tujuan= ?", (norek,)
        ).fetchone()

        assert hasil is True
        assert saldo_sesudah == saldo_sebelum + nominal
        assert riwayat["kategori"] == "transaksi"
        assert riwayat["jenis"] == "setor uang"
        assert audit["norek"] == norek
        assert audit["kategori"] == "finansial"
        assert audit["objek"] == "rekening"
        assert audit["aksi"] == "setor_tunai"
        assert transaksi["jenis"] == JenisTransaksi.SETOR_TUNAI.value
        assert transaksi["nominal"] == nominal
        assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum
        assert transaksi["saldo_tujuan_sesudah"] == saldo_sesudah

    @pytest.mark.parametrize("nominal", [9999, -9999])
    def test_setor_tunai_dengan_nominal_tidak_sesuai(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, nominal
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(InputTidakValid) as info_error:
            TransaksiService.setor_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "Minimal setor" in str(info_error.value)

    def test_setor_tunai_dengan_nik_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = "12325"
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(NikTidakSesuai) as info_error:
            TransaksiService.setor_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "sebagai pemilik rekening" in str(info_error.value)

    def test_setor_tunai_dengan_norek_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = "12325"
        nominal = 1_000_000
        norek_asli = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            TransaksiService.setor_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "tidak terdaftar" in str(info_error.value)

    def test_rollback_setor_tunai(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, monkeypatch
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        method_asli = audit_repo_module.AuditRepository.tambah_audit

        def uji_rollback(**kwargs):
            method_asli(**kwargs)
            raise RuntimeError("Simulasi rollback setor tunai")

        monkeypatch.setattr(
            audit_repo_module.AuditRepository, "tambah_audit", uji_rollback
        )

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(RuntimeError):
            TransaksiService.setor_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ?", (norek,)
        ).fetchone()

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_tujuan= ?", (norek,)
        ).fetchone()

        assert saldo_sesudah == saldo_sebelum
        assert riwayat is None
        assert audit is None
        assert transaksi is None


class TestTarikTunai:

    def test_tarik_tunai_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        hasil = TransaksiService.tarik_tunai(
            nik_masuk=nik, norek=norek, nominal=nominal
        )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ?", (norek,)
        ).fetchone()

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber= ?", (norek,)
        ).fetchone()

        assert hasil is True
        assert saldo_sesudah == saldo_sebelum - nominal
        assert riwayat["kategori"] == "transaksi"
        assert riwayat["jenis"] == "tarik uang"
        assert audit["norek"] == norek
        assert audit["kategori"] == "finansial"
        assert audit["objek"] == "rekening"
        assert audit["aksi"] == "tarik_tunai"
        assert transaksi["jenis"] == JenisTransaksi.TARIK_TUNAI.value
        assert transaksi["nominal"] == nominal
        assert transaksi["saldo_sumber_sebelum"] == saldo_sebelum
        assert transaksi["saldo_sumber_sesudah"] == saldo_sesudah

    @pytest.mark.parametrize(
        "nominal, pesan_error, jenis_exception",
        [
            (9999, "Minimal tarik", InputTidakValid),
            (-9999, "Minimal tarik", InputTidakValid),
            (10_000_000, "tidak memenuhi saldo minimum", StatusTidakValid),
        ],
    )
    def test_tarik_tunai_dengan_nominal_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        nominal,
        pesan_error,
        jenis_exception,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(jenis_exception) as info_error:
            TransaksiService.tarik_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert pesan_error in str(info_error.value)

    def test_tarik_tunai_dengan_nik_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = "12325"
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(NikTidakSesuai) as info_error:
            TransaksiService.tarik_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "sebagai pemilik rekening" in str(info_error.value)

    def test_tarik_tunai_dengan_norek_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = "12325"
        nominal = 1_000_000
        norek_asli = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            TransaksiService.tarik_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_asli, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "tidak terdaftar" in str(info_error.value)

    def test_rollback_tarik_tunai(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, monkeypatch
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        method_asli = audit_repo_module.AuditRepository.tambah_audit

        def uji_rollback(**kwargs):
            method_asli(**kwargs)
            raise RuntimeError("Simulasi rollback tarik tunai")

        monkeypatch.setattr(
            audit_repo_module.AuditRepository, "tambah_audit", uji_rollback
        )

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(RuntimeError):
            TransaksiService.tarik_tunai(nik_masuk=nik, norek=norek, nominal=nominal)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ?", (norek,)
        ).fetchone()

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber= ?", (norek,)
        ).fetchone()

        assert saldo_sesudah == saldo_sebelum
        assert riwayat is None
        assert audit is None
        assert transaksi is None


def verifikasi_hasil_transfer(koneksi, norek_pengirim, norek_penerima):
    transaksi = koneksi.execute(
        "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
        (norek_pengirim, norek_penerima),
    ).fetchone()
    assert transaksi is not None
    id_transaksi = transaksi["id"]

    riwayat_pengirim = koneksi.execute(
        "SELECT * FROM riwayat WHERE norek = ? AND transaksi_id = ?",
        (norek_pengirim, id_transaksi),
    ).fetchone()
    riwayat_penerima = koneksi.execute(
        "SELECT * FROM riwayat WHERE norek = ? AND transaksi_id = ?",
        (norek_penerima, id_transaksi),
    ).fetchone()
    audit_pengirim = koneksi.execute(
        "SELECT * FROM audit WHERE norek = ? AND transaksi_id = ?",
        (norek_pengirim, id_transaksi),
    ).fetchone()
    audit_penerima = koneksi.execute(
        "SELECT * FROM audit WHERE norek = ? AND transaksi_id = ?",
        (norek_penerima, id_transaksi),
    ).fetchone()

    return {
        "transaksi": transaksi,
        "riwayat_pengirim": riwayat_pengirim,
        "riwayat_penerima": riwayat_penerima,
        "audit_pengirim": audit_pengirim,
        "audit_penerima": audit_penerima,
    }


class TestTransfer:

    def test_transfer_happy_path(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik_pengirim = siapkan_data_rekening_dan_nasabah["nik"]

        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        nominal = 1_000_000
        pajak = 2_000
        total = nominal + pajak

        TransaksiService.transfer(
            nik_masuk=nik_pengirim,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal,
        )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        data = verifikasi_hasil_transfer(
            koneksi=koneksi_test,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
        )

        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum - total
        assert saldo_penerima_sesudah == saldo_penerima_sebelum + nominal

        assert data["transaksi"]["nominal"] == nominal
        assert data["transaksi"]["saldo_sumber_sebelum"] == saldo_pengirim_sebelum
        assert data["transaksi"]["saldo_tujuan_sebelum"] == saldo_penerima_sebelum
        assert data["transaksi"]["saldo_sumber_sesudah"] == saldo_pengirim_sesudah
        assert data["transaksi"]["saldo_tujuan_sesudah"] == saldo_penerima_sesudah
        assert data["transaksi"]["biaya"] == pajak

        assert data["riwayat_pengirim"]["kategori"] == "transaksi"
        assert data["riwayat_penerima"]["kategori"] == "transaksi"
        assert data["riwayat_pengirim"]["jenis"] == "transfer saldo"
        assert data["riwayat_penerima"]["jenis"] == "terima saldo"

        assert data["audit_pengirim"]["kategori"] == "finansial"
        assert data["audit_penerima"]["kategori"] == "finansial"
        assert data["audit_pengirim"]["objek"] == "rekening"
        assert data["audit_penerima"]["objek"] == "rekening"
        assert data["audit_pengirim"]["aksi"] == "transfer_keluar"
        assert data["audit_penerima"]["aksi"] == "penerimaan_transfer"

    def test_transfer_dengan_minimal_transfer(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]
        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        pajak = rekening_pengirim.pajak
        nominal = 10_000
        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )
        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal,
        )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        data = verifikasi_hasil_transfer(
            koneksi=koneksi_test,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
        )

        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum - (nominal + pajak)
        assert saldo_penerima_sesudah == saldo_penerima_sebelum + nominal

        assert data["transaksi"]["nominal"] == nominal
        assert data["transaksi"]["saldo_sumber_sebelum"] == saldo_pengirim_sebelum
        assert data["transaksi"]["saldo_tujuan_sebelum"] == saldo_penerima_sebelum
        assert data["transaksi"]["saldo_sumber_sesudah"] == saldo_pengirim_sesudah
        assert data["transaksi"]["saldo_tujuan_sesudah"] == saldo_penerima_sesudah
        assert data["transaksi"]["biaya"] == pajak

        assert data["riwayat_pengirim"]["kategori"] == "transaksi"
        assert data["riwayat_penerima"]["kategori"] == "transaksi"
        assert data["riwayat_pengirim"]["jenis"] == "transfer saldo"
        assert data["riwayat_penerima"]["jenis"] == "terima saldo"

        assert data["audit_pengirim"]["kategori"] == "finansial"
        assert data["audit_penerima"]["kategori"] == "finansial"
        assert data["audit_pengirim"]["objek"] == "rekening"
        assert data["audit_penerima"]["objek"] == "rekening"
        assert data["audit_pengirim"]["aksi"] == "transfer_keluar"
        assert data["audit_penerima"]["aksi"] == "penerimaan_transfer"

    def test_transfer_dengan_limit_tak_terbatas(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        koneksi_test.execute(
            "UPDATE rekening SET saldo = 250_000_000, level = 4 WHERE norek = ?",
            (norek_pengirim,),
        )

        koneksi_test.commit()

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        nominal = 1_000_000
        pajak = rekening_pengirim.pajak
        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal,
        )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        data = verifikasi_hasil_transfer(
            koneksi=koneksi_test,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
        )

        limit_sisa_rekening = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()
        assert limit_sisa_rekening["limit_sisa"] is None
        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum - (nominal + pajak)
        assert saldo_penerima_sesudah == saldo_penerima_sebelum + nominal

        assert data["transaksi"]["nominal"] == nominal
        assert data["transaksi"]["saldo_sumber_sebelum"] == saldo_pengirim_sebelum
        assert data["transaksi"]["saldo_tujuan_sebelum"] == saldo_penerima_sebelum
        assert data["transaksi"]["saldo_sumber_sesudah"] == saldo_pengirim_sesudah
        assert data["transaksi"]["saldo_tujuan_sesudah"] == saldo_penerima_sesudah
        assert data["transaksi"]["biaya"] == pajak

        assert data["riwayat_pengirim"]["kategori"] == "transaksi"
        assert data["riwayat_penerima"]["kategori"] == "transaksi"
        assert data["riwayat_pengirim"]["jenis"] == "transfer saldo"
        assert data["riwayat_penerima"]["jenis"] == "terima saldo"

        assert data["audit_pengirim"]["kategori"] == "finansial"
        assert data["audit_penerima"]["kategori"] == "finansial"
        assert data["audit_pengirim"]["objek"] == "rekening"
        assert data["audit_penerima"]["objek"] == "rekening"
        assert data["audit_pengirim"]["aksi"] == "transfer_keluar"
        assert data["audit_penerima"]["aksi"] == "penerimaan_transfer"

    @pytest.mark.parametrize(
        "nominal, pesan_error, exception",
        [
            (9999, "Minimal transfer", InputTidakValid),
            (-9999, "Minimal transfer", InputTidakValid),
            (9_500_000, "untuk melakukan transfer", StatusTidakValid),
        ],
    )
    def test_transfer_dengan_nominal_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
        nominal,
        pesan_error,
        exception,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        with pytest.raises(exception) as info_error:

            TransaksiService.transfer(
                nik_masuk=nik,
                norek_pengirim=norek_pengirim,
                norek_penerima=norek_penerima,
                nominal=nominal,
            )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
            (norek_pengirim, norek_penerima),
        ).fetchone()

        assert transaksi is None

        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum
        assert saldo_penerima_sesudah == saldo_penerima_sebelum
        print(f"pesan error : {info_error.value}")
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah, exception, potongan_pesan",
        [
            ({"norek_pengirim": "000000"}, RekeningTidakDitemukan, "pengirim"),
            ({"nik_masuk": "111111111"}, NikTidakSesuai, "pemilik rekening"),
            ({"norek_penerima": "999999"}, RekeningTidakDitemukan, "penerima"),
        ],
        ids=["pengirim_tidak_ada", "nik_salah", "penerima_tidak_ada"],
    )
    def test_transfer_dengan_identitas_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
        kwargs_salah,
        exception,
        potongan_pesan,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        kwargs = {
            "nik_masuk": nik,
            "norek_pengirim": norek_pengirim,
            "norek_penerima": norek_penerima,
            "nominal": 100_000,
        }

        kwargs.update(kwargs_salah)

        with pytest.raises(exception) as info_error:
            TransaksiService.transfer(**kwargs)

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )
        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
            (norek_pengirim, norek_penerima),
        ).fetchone()

        assert transaksi is None

        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum
        assert saldo_penerima_sesudah == saldo_penerima_sebelum
        assert potongan_pesan in str(info_error.value)

    @pytest.mark.parametrize(
        "peran, status, exception, pesan_error",
        [
            ("pengirim", "blokir", StatusTidakValid, " Anda saat ini sedang"),
            ("pengirim", "tutup", StatusTidakValid, " Anda saat ini sedang"),
            ("penerima", "blokir", StatusTidakValid, "Rekening penerima saat ini"),
            ("penerima", "tutup", StatusTidakValid, "Rekening penerima saat ini"),
        ],
    )
    def test_transfer_dengan_status_rekeninng_pengirim_atau_penerima_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
        pesan_error,
        peran,
        status,
        exception,
    ):

        nik_pengirim = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]
        nominal = 1_000_000

        norek_yang_diubah = {"pengirim": norek_pengirim, "penerima": norek_penerima}

        norek_sesi_sekarang = norek_yang_diubah[peran]

        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?",
            (status, norek_sesi_sekarang),
        )

        koneksi_test.commit()

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        with pytest.raises(exception) as info_error:
            TransaksiService.transfer(
                nik_masuk=nik_pengirim,
                norek_pengirim=norek_pengirim,
                norek_penerima=norek_penerima,
                nominal=nominal,
            )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
            (norek_pengirim, norek_penerima),
        ).fetchone()

        assert transaksi is None
        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum
        assert saldo_penerima_sesudah == saldo_penerima_sebelum
        assert pesan_error in str(info_error.value)
        print(f"pesan error : {info_error.value}")

    def test_transfer_ke_rekening_sendiri(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        nominal = 1_000_000

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        with pytest.raises(StatusTidakValid) as info_error:
            TransaksiService.transfer(
                nik_masuk=nik,
                norek_pengirim=norek,
                norek_penerima=norek,
                nominal=nominal,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
            (norek, norek),
        ).fetchone()

        assert transaksi is None
        assert saldo_sesudah == saldo_sebelum
        assert "Tidak dapat transfer" in str(info_error.value)

    def test_transfer_dengan_limit_harian_habis_atau_tidak_cukup(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        nominal = rekening_pengirim.limit_sisa + 1
        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        with pytest.raises(StatusTidakValid) as info_error:
            TransaksiService.transfer(
                nik_masuk=nik,
                norek_pengirim=norek_pengirim,
                norek_penerima=norek_penerima,
                nominal=nominal,
            )

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
            (norek_pengirim, norek_penerima),
        ).fetchone()

        assert transaksi is None
        assert saldo_sesudah == saldo_sebelum
        print(f"pesan error : {info_error.value}")
        assert "untuk melakukan transfer" in str(info_error.value)

    def test_transfer_dengan_nominal_pas_limit_harian(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        nominal = rekening_pengirim.limit_sisa
        pajak = rekening_pengirim.pajak
        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal,
        )

        limit_sisa_pengirim = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()
        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum - (nominal + pajak)
        assert limit_sisa_pengirim["limit_sisa"] == 0
        assert saldo_penerima_sesudah == saldo_penerima_sebelum + nominal

        data = verifikasi_hasil_transfer(
            koneksi=koneksi_test,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
        )

        assert data["transaksi"]["nominal"] == nominal
        assert data["transaksi"]["saldo_sumber_sebelum"] == saldo_pengirim_sebelum
        assert data["transaksi"]["saldo_tujuan_sebelum"] == saldo_penerima_sebelum
        assert data["transaksi"]["saldo_sumber_sesudah"] == saldo_pengirim_sesudah
        assert data["transaksi"]["saldo_tujuan_sesudah"] == saldo_penerima_sesudah
        assert data["transaksi"]["biaya"] == pajak

        assert data["riwayat_pengirim"]["kategori"] == "transaksi"
        assert data["riwayat_penerima"]["kategori"] == "transaksi"
        assert data["riwayat_pengirim"]["jenis"] == "transfer saldo"
        assert data["riwayat_penerima"]["jenis"] == "terima saldo"

        assert data["audit_pengirim"]["kategori"] == "finansial"
        assert data["audit_penerima"]["kategori"] == "finansial"
        assert data["audit_pengirim"]["objek"] == "rekening"
        assert data["audit_penerima"]["objek"] == "rekening"
        assert data["audit_pengirim"]["aksi"] == "transfer_keluar"
        assert data["audit_penerima"]["aksi"] == "penerimaan_transfer"

    def test_transfer_hingga_mencapai_minimal_saldo(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]
        koneksi_test.execute(
            "UPDATE rekening SET limit_sisa = ? WHERE norek = ?",
            (20_000_000, norek_pengirim),
        )
        koneksi_test.commit()

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        pajak = rekening_pengirim.pajak
        nominal = rekening_pengirim.saldo - (rekening_pengirim.saldosetor_min + pajak)

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal,
        )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        data = verifikasi_hasil_transfer(
            koneksi=koneksi_test,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
        )

        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum - (nominal + pajak)
        assert saldo_penerima_sesudah == saldo_penerima_sebelum + nominal

        assert data["transaksi"]["nominal"] == nominal
        assert data["transaksi"]["saldo_sumber_sebelum"] == saldo_pengirim_sebelum
        assert data["transaksi"]["saldo_tujuan_sebelum"] == saldo_penerima_sebelum
        assert data["transaksi"]["saldo_sumber_sesudah"] == saldo_pengirim_sesudah
        assert data["transaksi"]["saldo_tujuan_sesudah"] == saldo_penerima_sesudah
        assert data["transaksi"]["biaya"] == pajak

        assert data["riwayat_pengirim"]["kategori"] == "transaksi"
        assert data["riwayat_penerima"]["kategori"] == "transaksi"
        assert data["riwayat_pengirim"]["jenis"] == "transfer saldo"
        assert data["riwayat_penerima"]["jenis"] == "terima saldo"

        assert data["audit_pengirim"]["kategori"] == "finansial"
        assert data["audit_penerima"]["kategori"] == "finansial"
        assert data["audit_pengirim"]["objek"] == "rekening"
        assert data["audit_penerima"]["objek"] == "rekening"
        assert data["audit_pengirim"]["aksi"] == "transfer_keluar"
        assert data["audit_penerima"]["aksi"] == "penerimaan_transfer"

    def test_rollback_proses_transfer(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
        monkeypatch,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]

        norek_penerima = siapkan_data_rekening_penerima["norek"]
        nominal = 1_000_000

        method_asli = audit_repo_module.AuditRepository.tambah_audit

        def uji_rollback(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulasi rollback proses transfer")

        monkeypatch.setattr(
            audit_repo_module.AuditRepository, "tambah_audit", uji_rollback
        )

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        with pytest.raises(RuntimeError):
            TransaksiService.transfer(
                nik_masuk=nik,
                norek_pengirim=norek_pengirim,
                norek_penerima=norek_penerima,
                nominal=nominal,
            )

        saldo_pengirim_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sesudah = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_sumber = ? AND norek_tujuan = ?",
            (norek_pengirim, norek_penerima),
        ).fetchone()

        assert transaksi is None
        assert saldo_pengirim_sesudah == saldo_pengirim_sebelum
        assert saldo_penerima_sesudah == saldo_penerima_sebelum

    def test_transfer_di_hari_berikutnya_mereset_limit(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]

        hari_ini = datetime.date.today()

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        nominal = 1_000_000
        pajak = rekening_pengirim.pajak

        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal,
            hari_ini=hari_ini,
        )

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        riwayat = koneksi_test.execute(
            "SELECT COUNT (*) FROM riwayat WHERE jenis = 'reset limit' AND norek = ?",
            (norek_pengirim,),
        ).fetchone()[0]

        assert riwayat == 0
        assert rekening_pengirim.limit_sisa == rekening_pengirim.limit_harian - nominal
        assert rekening_pengirim.reset == hari_ini

        hari_esok = hari_ini + datetime.timedelta(days=1)

        nominal_hari_kedua = 1_500_000

        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal_hari_kedua,
            hari_ini=hari_esok,
        )
        riwayat = koneksi_test.execute(
            "SELECT COUNT (*) FROM riwayat WHERE jenis = 'reset limit' AND norek = ?",
            (norek_pengirim,),
        ).fetchone()[0]

        saldo_pengirim = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )

        assert riwayat == 1
        assert (
            rekening_pengirim.limit_sisa
            == rekening_pengirim.limit_harian - nominal_hari_kedua
        )
        assert rekening_pengirim.reset == hari_esok
        assert saldo_pengirim == saldo_pengirim_sebelum - (
            nominal + nominal_hari_kedua + pajak * 2
        )
        assert saldo_penerima == saldo_penerima_sebelum + (nominal + nominal_hari_kedua)

    def test_transfer_lebih_dari_sekali_dalam_sehari(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        siapkan_data_rekening_penerima,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek_pengirim = siapkan_data_rekening_dan_nasabah["norek"]
        norek_penerima = siapkan_data_rekening_penerima["norek"]
        rekening_pengirim = RekeningLoader.muat_rekening(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        hari_ini = datetime.date.today()
        pajak = rekening_pengirim.pajak
        saldo_pengirim_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima_sebelum = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        nominal_pertama = 1_000_000
        limit_fresh = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()["limit_sisa"]
        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal_pertama,
            hari_ini=hari_ini,
        )
        limit_putaran_pertama = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()["limit_sisa"]

        assert limit_putaran_pertama == limit_fresh - nominal_pertama

        nominal_kedua = 3_000_000
        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal_kedua,
            hari_ini=hari_ini,
        )
        print(id(koneksi_test))
        limit_putaran_kedua = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()["limit_sisa"]

        assert limit_putaran_kedua == limit_putaran_pertama - nominal_kedua

        nominal_ketiga = 1_000_000
        TransaksiService.transfer(
            nik_masuk=nik,
            norek_pengirim=norek_pengirim,
            norek_penerima=norek_penerima,
            nominal=nominal_ketiga,
            hari_ini=hari_ini,
        )
        print(id(koneksi_test))
        limit_putaran_ketiga = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()["limit_sisa"]

        assert limit_putaran_ketiga == limit_putaran_kedua - nominal_ketiga

        nominal_keempat = 10_000
        with pytest.raises(StatusTidakValid) as info_error:
            TransaksiService.transfer(
                nik_masuk=nik,
                norek_pengirim=norek_pengirim,
                norek_penerima=norek_penerima,
                nominal=nominal_keempat,
                hari_ini=hari_ini,
            )
        limit_putaran_keempat = koneksi_test.execute(
            "SELECT limit_sisa FROM rekening WHERE norek = ?", (norek_pengirim,)
        ).fetchone()["limit_sisa"]
        assert limit_putaran_keempat == 0
        print(f"pesan error : {info_error.value}")
        assert "Limit harian tidak cukup" in str(info_error.value)

        saldo_pengirim = RekeningRepository.ambil_saldo(
            norek=norek_pengirim, koneksi=koneksi_test
        )
        saldo_penerima = RekeningRepository.ambil_saldo(
            norek=norek_penerima, koneksi=koneksi_test
        )

        assert saldo_penerima == (
            saldo_penerima_sebelum + nominal_pertama + nominal_kedua + nominal_ketiga
        )
        assert saldo_pengirim == saldo_pengirim_sebelum - (
            nominal_pertama + nominal_kedua + nominal_ketiga + pajak * 3
        )
