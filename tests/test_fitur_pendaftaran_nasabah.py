import pytest

from bank_djago import JenisTransaksi
from bank_djago.services.nasabah.nasabah_service import NasabahService


class TestDaftarNasabah:

    @pytest.fixture
    def data_nasabah_siap_digunakan_untuk_pendaftaran(self):
        nama = "Nasabah Pengujian"
        nik = "1100220033004400"
        alamat = "Jln.Pengujian Pytest"
        pin = "123456"
        level_rekening = 2
        setor_awal = 5_000_000 # saldo minimal level 2 adalah 3 juta

        return {
            'nik':nik,
            'nama':nama,
            'alamat':alamat,
            'pin':pin,
            'level':level_rekening,
            'setor_awal':setor_awal
        }



    def test_daftar_dan_buka_rekening_happy_path(self,koneksi_test,data_nasabah_siap_digunakan_untuk_pendaftaran):

        data_persiapan = data_nasabah_siap_digunakan_untuk_pendaftaran
        jumlah_sebelum = koneksi_test.execute("SELECT COUNT(*) FROM nasabah WHERE nik = ?",(data_persiapan['nik'],)).fetchone()[0]

        assert jumlah_sebelum == 0

        nasabah_baru, rekening_baru =  NasabahService.daftar_dan_buka_rekening(**data_persiapan)
        norek = rekening_baru.norek
        nik = nasabah_baru.NIK

        assert nik == data_persiapan['nik']


        data_nasabah = koneksi_test.execute("SELECT * FROM nasabah WHERE nik = ?",(nik,)).fetchone()
        assert data_nasabah is not None

        assert data_nasabah['nama'] == data_persiapan['nama']
        assert data_nasabah['alamat'] == data_persiapan['alamat']

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE nik_pemilik = ? AND norek = ?",(nik, norek)).fetchone()
        assert data_rekening is not None
        assert data_rekening['saldo'] == data_persiapan['setor_awal']
        assert data_rekening['level'] == data_persiapan['level']
        assert data_rekening['pin'] != data_persiapan['pin']
        assert data_rekening['status'] == 'aktif'


        transaksi = koneksi_test.execute("SELECT * FROM transaksi WHERE norek_tujuan = ?",(norek,)).fetchone()
        assert transaksi is not None

        id_transaksi = transaksi['id']

        assert transaksi['jenis'] == JenisTransaksi.SETOR_AWAL.value
        assert transaksi['nominal'] == data_persiapan['setor_awal']
        assert transaksi['saldo_tujuan_sebelum'] == 0
        assert transaksi['saldo_tujuan_sesudah'] == data_persiapan['setor_awal']

        audit_pendaftaran = koneksi_test.execute("SELECT * FROM audit WHERE nik = ? AND aksi = 'pendaftaran_nasabah' AND norek = ?",(nik,norek)).fetchone()
        riwayat_pembukaan = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",(norek,)).fetchone()
        riwayat_setor_awal = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal' AND transaksi_id = ?",(norek,id_transaksi)).fetchone()
        audit_pembukaan_rekening = koneksi_test.execute(
            "SELECT * FROM audit WHERE nik = ? AND aksi = 'pembukaan_rekening' AND norek = ? AND transaksi_id = ?",
            (nik, norek,id_transaksi),
        ).fetchone()
        assert audit_pembukaan_rekening is not None
        assert audit_pendaftaran is not None
        assert riwayat_pembukaan is not None
        assert riwayat_setor_awal is not None