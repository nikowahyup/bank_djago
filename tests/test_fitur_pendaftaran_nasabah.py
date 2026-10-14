import pytest

from bank_djago import JenisTransaksi
from bank_djago.services.nasabah.nasabah_service import NasabahService
from bank_djago.services.rekening.rekening_service import RekeningService
from bank_djago.services.exceptions import InputTidakValid


class TestDaftarNasabah:

    @pytest.fixture
    def data_nasabah_siap_digunakan_untuk_pendaftaran(self):
        nama = "Nasabah Pengujian"
        nik = "1100220033004400"
        alamat = "Jln.Pengujian Pytest"
        pin = "123456"
        level_rekening = 2
        setor_awal = 5_000_000  # saldo minimal level 2 adalah 3 juta

        return {
            "nik": nik,
            "nama": nama,
            "alamat": alamat,
            "pin": pin,
            "level": level_rekening,
            "setor_awal": setor_awal,
        }

    def test_daftar_dan_buka_rekening_happy_path(
        self, koneksi_test, data_nasabah_siap_digunakan_untuk_pendaftaran
    ):

        data_persiapan = data_nasabah_siap_digunakan_untuk_pendaftaran
        jumlah_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM nasabah WHERE nik = ?", (data_persiapan["nik"],)
        ).fetchone()[0]

        assert jumlah_sebelum == 0

        nasabah_baru, rekening_baru = NasabahService.daftar_dan_buka_rekening(
            **data_persiapan
        )
        norek = rekening_baru.norek
        nik = nasabah_baru.NIK

        assert nik == data_persiapan["nik"]

        data_nasabah = koneksi_test.execute(
            "SELECT * FROM nasabah WHERE nik = ?", (nik,)
        ).fetchone()
        assert data_nasabah is not None

        assert data_nasabah["nama"] == data_persiapan["nama"]
        assert data_nasabah["alamat"] == data_persiapan["alamat"]

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE nik_pemilik = ? AND norek = ?", (nik, norek)
        ).fetchone()
        assert data_rekening is not None
        assert data_rekening["saldo"] == data_persiapan["setor_awal"]
        assert data_rekening["level"] == data_persiapan["level"]
        assert data_rekening["pin"] != data_persiapan["pin"]
        assert data_rekening["status"] == "aktif"

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_tujuan = ?", (norek,)
        ).fetchone()
        assert transaksi is not None

        id_transaksi = transaksi["id"]

        assert transaksi["jenis"] == JenisTransaksi.SETOR_AWAL.value
        assert transaksi["nominal"] == data_persiapan["setor_awal"]
        assert transaksi["saldo_tujuan_sebelum"] == 0
        assert transaksi["saldo_tujuan_sesudah"] == data_persiapan["setor_awal"]

        audit_pendaftaran = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pendaftaran_nasabah' AND norek = ?",
            (nik, norek),
        ).fetchone()
        riwayat_pembukaan = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",
            (norek,),
        ).fetchone()
        riwayat_setor_awal = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit_pembukaan_rekening = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pembukaan_rekening' AND norek = ? AND transaksi_id = ?",
            (nik, norek, id_transaksi),
        ).fetchone()
        assert audit_pembukaan_rekening is not None
        assert audit_pendaftaran is not None
        assert riwayat_pembukaan is not None
        assert riwayat_setor_awal is not None

    def test_daftar_nasabah_dengan_nik_sudah_terdaftar(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        data_nasabah_siap_digunakan_untuk_pendaftaran,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]

        data_persiapan = data_nasabah_siap_digunakan_untuk_pendaftaran
        data_persiapan["nik"] = nik

        is_nik_terdaftar = koneksi_test.execute(
            "SELECT * FROM nasabah WHERE nik = ?", (nik,)
        ).fetchone()

        assert is_nik_terdaftar is not None
        assert (
            is_nik_terdaftar["nama"] != data_persiapan["nama"]
        )  # ini opsional. Bisa saja NIK yang sama dipakai orang yang sama. Skenario NIK sama beda orang bisa terjadi jika anggota keluarga memakai NIK yang sama dengan NIK yang sudah terdaftar
        assert (
            is_nik_terdaftar["alamat"] != data_persiapan["alamat"]
        )  # ini juga opsional

        jumlah_rekening_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?", (nik,)
        ).fetchone()[0]
        assert jumlah_rekening_sebelum == 1
        jumlah_riwayat_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM riwayat"
        ).fetchone()[0]
        with pytest.raises(InputTidakValid) as info_error:
            NasabahService.daftar_dan_buka_rekening(**data_persiapan)

        nasabah_sesudah = koneksi_test.execute(
            "SELECT * FROM nasabah WHERE nik = ?", (nik,)
        ).fetchone()
        assert nasabah_sesudah["nama"] == is_nik_terdaftar["nama"]
        assert nasabah_sesudah["alamat"] == is_nik_terdaftar["alamat"]

        jumlah_data_nik_tersimpan = koneksi_test.execute(
            "SELECT COUNT(*) FROM nasabah WHERE nik = ?", (nik,)
        ).fetchone()[0]
        jumlah_rekening_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?", (nik,)
        ).fetchone()[0]
        jumlah_riwayat_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM riwayat"
        ).fetchone()[0]
        audit_pendaftaran = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pendaftaran_nasabah'", (nik,)
        ).fetchone()

        assert jumlah_data_nik_tersimpan == 1
        assert jumlah_rekening_sesudah == jumlah_rekening_sebelum
        assert jumlah_riwayat_sesudah == jumlah_riwayat_sebelum
        assert audit_pendaftaran is None
        assert "NIK sudah terdaftar" in str(info_error.value)

    def test_rollback_pendaftaran_karena_setor_awal_tidak_memenuhi_syarat(
        self, koneksi_test, data_nasabah_siap_digunakan_untuk_pendaftaran
    ):

        data_persiapan = data_nasabah_siap_digunakan_untuk_pendaftaran
        data_persiapan["setor_awal"] = (
            RekeningService.jenis_rekening[data_persiapan["level"]]["minimal_setor"] - 1
        )

        cek_data_nik_sebelum = koneksi_test.execute(
            "SELECT * FROM nasabah WHERE nik = ?", (data_persiapan["nik"],)
        ).fetchone()
        assert cek_data_nik_sebelum is None

        jumlah_rekening_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",
            (data_persiapan["nik"],),
        ).fetchone()[0]
        assert jumlah_rekening_sebelum == 0
        jumlah_riwayat_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM riwayat"
        ).fetchone()[0]

        with pytest.raises(InputTidakValid) as info_error:
            NasabahService.daftar_dan_buka_rekening(**data_persiapan)

        cek_data_nik_sesudah = koneksi_test.execute(
            "SELECT * FROM nasabah WHERE nik = ?", (data_persiapan["nik"],)
        ).fetchone()
        jumlah_rekening_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",
            (data_persiapan["nik"],),
        ).fetchone()[0]
        jumlah_riwayat_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM riwayat"
        ).fetchone()[0]
        audit_pendaftaran = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pendaftaran_nasabah'",
            (data_persiapan["nik"],),
        ).fetchone()

        assert cek_data_nik_sesudah is None
        assert jumlah_rekening_sesudah == jumlah_rekening_sebelum
        assert jumlah_riwayat_sesudah == jumlah_riwayat_sebelum
        assert audit_pendaftaran is None
        assert "Setor awal tidak memenuhi saldo minimal setoran awal" in str(
            info_error.value
        )

    @pytest.mark.parametrize(
        "kwargs_salah,pesan_error",
        [
            ({"nama": " "}, "Nama tidak boleh kosong"),
            ({"nik": " "}, "NIK tidak boleh kosong"),
            ({"nik": "123ew"}, "NIK tidak boleh mengandung huruf"),
            ({"alamat": " "}, "Alamat tidak boleh kosong"),
            ({"pin": "1234"}, "PIN harus berupa 6 digit angka"),
            ({"pin": "1234ab"}, "PIN harus berupa 6 digit angka"),
            ({"level": 0}, "Pilihan level rekening tidak tersedia"),
            ({"level": 5}, "Pilihan level rekening tidak tersedia"),
            ({"setor_awal": "10000000"}, "Setor awal harus berupa angka"),
            ({"nik": "1" * 15}, "Jumlah digit NIK tidak valid"),
            ({"nik": "1" * 17}, "Jumlah digit NIK tidak valid"),
            (
                {"nama": ""},
                "Nama tidak boleh kosong",
            ),  # perwakilan untuk NIK,PIN,dan alamat(tidak boleh kosong,spasi pun tidak boleh)
        ],
    )
    def test_pendaftaran_dengan_input_tidak_valid(
        self,
        koneksi_test,
        data_nasabah_siap_digunakan_untuk_pendaftaran,
        kwargs_salah,
        pesan_error,
    ):

        data_persiapan = data_nasabah_siap_digunakan_untuk_pendaftaran

        data_persiapan.update(kwargs_salah)

        jumlah_nasabah_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM nasabah"
        ).fetchone()[0]
        jumlah_rekening_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM rekening"
        ).fetchone()[0]
        jumlah_audit_pendaftaran_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM audit WHERE aksi = 'pendaftaran_nasabah'"
        ).fetchone()[0]
        jumlah_riwayat_sebelum = koneksi_test.execute(
            "SELECT COUNT(*) FROM riwayat"
        ).fetchone()[0]
        with pytest.raises(InputTidakValid) as info_error:
            NasabahService.daftar_dan_buka_rekening(**data_persiapan)

        jumlah_audit_pendaftaran_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM audit WHERE aksi = 'pendaftaran_nasabah'"
        ).fetchone()[0]
        jumlah_nasabah_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM nasabah"
        ).fetchone()[0]
        jumlah_rekening_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM rekening"
        ).fetchone()[0]
        jumlah_riwayat_sesudah = koneksi_test.execute(
            "SELECT COUNT(*) FROM riwayat"
        ).fetchone()[0]

        assert jumlah_nasabah_sesudah == jumlah_nasabah_sebelum
        assert jumlah_rekening_sesudah == jumlah_rekening_sebelum
        assert jumlah_audit_pendaftaran_sesudah == jumlah_audit_pendaftaran_sebelum
        assert jumlah_riwayat_sesudah == jumlah_riwayat_sebelum
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize("level_valid", [1, 4])
    def test_pendaftaran_dengan_memilih_level_rekening_batas_bawah_dan_atas(
        self, koneksi_test, level_valid, data_nasabah_siap_digunakan_untuk_pendaftaran
    ):

        data_persiapan = data_nasabah_siap_digunakan_untuk_pendaftaran
        data_persiapan["level"] = level_valid
        data_persiapan["setor_awal"] = RekeningService.jenis_rekening[
            data_persiapan["level"]
        ]["minimal_setor"]

        nasabah_baru, rekening_baru = NasabahService.daftar_dan_buka_rekening(
            **data_persiapan
        )
        norek = rekening_baru.norek
        nik = nasabah_baru.NIK

        assert nik == data_persiapan["nik"]

        data_nasabah = koneksi_test.execute(
            "SELECT * FROM nasabah WHERE nik = ?", (nik,)
        ).fetchone()
        assert data_nasabah is not None

        assert data_nasabah["nama"] == data_persiapan["nama"]
        assert data_nasabah["alamat"] == data_persiapan["alamat"]

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE nik_pemilik = ? AND norek = ?", (nik, norek)
        ).fetchone()
        assert data_rekening is not None
        assert data_rekening["saldo"] == data_persiapan["setor_awal"]
        assert data_rekening["level"] == level_valid
        assert data_rekening["pin"] != data_persiapan["pin"]
        assert data_rekening["status"] == "aktif"

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE norek_tujuan = ?", (norek,)
        ).fetchone()
        assert transaksi is not None

        id_transaksi = transaksi["id"]

        assert transaksi["jenis"] == JenisTransaksi.SETOR_AWAL.value
        assert transaksi["nominal"] == data_persiapan["setor_awal"]
        assert transaksi["saldo_tujuan_sebelum"] == 0
        assert transaksi["saldo_tujuan_sesudah"] == data_persiapan["setor_awal"]

        audit_pendaftaran = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pendaftaran_nasabah' AND norek = ?",
            (nik, norek),
        ).fetchone()
        riwayat_pembukaan = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",
            (norek,),
        ).fetchone()
        riwayat_setor_awal = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal' AND transaksi_id = ?",
            (norek, id_transaksi),
        ).fetchone()
        audit_pembukaan_rekening = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pembukaan_rekening' AND norek = ? AND transaksi_id = ?",
            (nik, norek, id_transaksi),
        ).fetchone()
        assert audit_pembukaan_rekening is not None
        assert audit_pendaftaran is not None
        assert riwayat_pembukaan is not None
        assert riwayat_setor_awal is not None
