import datetime
from datetime import date

from bank_djago import JenisReferensi
from bank_djago.conftest import koneksi_test
from bank_djago.core.pinjaman import Pinjaman

from bank_djago.penyimpanan.repositories.notifikasi_repository import (
    NotifikasiRepository,
)
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.services.exceptions import (
    RekeningTidakSesuai,
    NikTidakSesuai,
    InputTidakValid,
    StatusTidakValid,
    PinjamanTidakDitemukan,
    RekeningTidakDitemukan,
    PerbaruiStatusGagal,
PinTidakCocok,
RekeningTerkunci
)
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
import bank_djago.penyimpanan.repositories.riwayat_repository as riwayat_repo_module
import bank_djago.penyimpanan.repositories.pinjaman_repository as pinjaman_repo_module
import bank_djago.penyimpanan.repositories.audit_repository as audit_repo_module

import pytest

from bank_djago.utils.utility import StatusPinjaman

# ========================================================================
# ========================= TEST HITUNG DENDA ===========================
# ========================================================================


class TestHItungDenda:

    def test_hitung_denda_nol_saat_jatuh_tempo(self):

        pinjaman = Pinjaman(
            pemilik=None,
            rekening=None,
            nominal_pinjaman=10_000_000,
            bunga=0.12,
            tenor=12,
            id=3,
        )

        pinjaman.cicilan_tetap = 888_848
        pinjaman.tanggal_jatuh_tempo = date(2026, 9, 18)

        denda = pinjaman.hitung_denda(hari_ini=date(2026, 9, 18))

        assert denda == 0

    def test_hitung_denda_nol_satu_hari_sebelum_jatuh_tempo(self):
        pinjaman = Pinjaman(
            pemilik=None,
            rekening=None,
            nominal_pinjaman=10_000_000,
            bunga=0.12,
            tenor=12,
            id=3,
        )

        pinjaman.cicilan_tetap = 888_848
        pinjaman.tanggal_jatuh_tempo = date(2026, 9, 18)

        denda = pinjaman.hitung_denda(hari_ini=date(2026, 9, 17))

        assert denda == 0

    def test_hitung_denda_nol_satu_hari_setelah_jatuh_tempo(self):

        pinjaman = Pinjaman(
            pemilik=None,
            rekening=None,
            nominal_pinjaman=10_000_000,
            bunga=0.12,
            tenor=12,
            id=3,
        )

        pinjaman.cicilan_tetap = 888_848
        pinjaman.tanggal_jatuh_tempo = date(2026, 9, 18)

        denda = pinjaman.hitung_denda(hari_ini=date(2026, 9, 19))

        assert denda == 0

    def test_hitung_denda_nol_saat_masa_toleransi_tepat_7_hari(self):

        pinjaman = Pinjaman(
            pemilik=None,
            rekening=None,
            nominal_pinjaman=10_000_000,
            bunga=0.12,
            tenor=12,
            id=3,
        )

        pinjaman.cicilan_tetap = 888_848
        pinjaman.tanggal_jatuh_tempo = date(2026, 9, 18)

        denda = pinjaman.hitung_denda(hari_ini=date(2026, 9, 25))

        assert denda == 0

    def test_hitung_denda_saat_masa_toleransi_berakhir(self):

        pinjaman = Pinjaman(
            pemilik=None,
            rekening=None,
            nominal_pinjaman=1_000_000,
            bunga=0.12,
            tenor=12,
            id=3,
        )

        pinjaman.cicilan_tetap = 888_848
        pinjaman.tanggal_jatuh_tempo = date(2026, 9, 18)

        denda = pinjaman.hitung_denda(hari_ini=date(2026, 9, 29))

        assert denda != 0


# ========================================================================
# ====================== TEST PENCAIRAN PINJAMAN ========================
# ========================================================================


class TestCairkanPinjaman:

    def test_pencairan_pinjaman_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,norek, nominal_pinjaman, bunga,tenor,sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (1, "123456", 2_000_000, 0.12, 6, 0, "disetujui"),
        )

        koneksi_test.commit()

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        PinjamanService.cairkan_pinjaman(nik=nik, norek_pencairan=norek, id_pinjaman=1)

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        transaksi = koneksi_test.execute(
            "SELECT * FROM transaksi WHERE jenis_referensi = 'pinjaman' AND id_referensi = ?",
            (1,),
        ).fetchone()
        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ?", (norek,)
        ).fetchone()
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        cursor = koneksi_test.execute("""SELECT * FROM pinjaman WHERE id = ?""", (1,))
        hasil = cursor.fetchone()

        cicilan_tetap = hasil["cicilan_tetap"]
        sisa_pokok = hasil["sisa_pokok"]
        waktu_pencairan = hasil["tanggal_pencairan"]
        waktu_jatuh_tempo = hasil["tanggal_jatuh_tempo"]
        status = hasil["status"]

        assert cicilan_tetap > 0
        assert sisa_pokok == 2_000_000
        assert waktu_pencairan is not None
        assert waktu_jatuh_tempo is not None
        assert status == "aktif"

        assert saldo_sesudah == saldo_sebelum + 2_000_000
        assert transaksi is not None
        assert transaksi["norek_tujuan"] == norek
        assert transaksi["nominal"] == 2_000_000
        assert transaksi["saldo_tujuan_sebelum"] == saldo_sebelum
        assert transaksi["saldo_tujuan_sesudah"] == saldo_sesudah

        assert riwayat is not None
        assert audit is not None

    @pytest.fixture
    def pinjaman_siap_cair(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,norek, nominal_pinjaman, bunga,tenor,sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (1, "123456", 2_000_000, 0.12, 6, 0, "disetujui"),
        )

        koneksi_test.commit()

        return {"nik": nik, "norek": norek, "id_pinjaman": 1}

    def test_pencairan_pinjaman_dengan_norek_salah(
        self, koneksi_test, pinjaman_siap_cair
    ):

        nik = pinjaman_siap_cair["nik"]
        norek = "123"
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        with pytest.raises(RekeningTidakSesuai) as info_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )

        print(f"Pesan error: {info_error.value}")
        assert "tidak terdaftar" in str(info_error.value)

    def test_pencairan_pinjaman_nik_salah(self, koneksi_test, pinjaman_siap_cair):

        nik = "9999"
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        with pytest.raises(NikTidakSesuai) as info_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )

        print(f"Pesan error: {info_error.value}")
        assert "NIK" in str(info_error.value)

    def test_pencairan_pinjaman_menggunakan_id_pinjaman_negatif(
        self, koneksi_test, pinjaman_siap_cair
    ):

        nik = pinjaman_siap_cair["nik"]
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = -99

        with pytest.raises(InputTidakValid) as angka_negatif:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )

        print(f"Pesan error: {angka_negatif.value}")
        assert "tidak valid" in str(angka_negatif.value)

    def test_pencairan_menggunakan_id_pinjaman_tidak_terdaftar(
        self, koneksi_test, pinjaman_siap_cair
    ):

        nik = pinjaman_siap_cair["nik"]
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = 98

        with pytest.raises(PinjamanTidakDitemukan) as tidak_terdaftar:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )

        print(f"Pesan error: {tidak_terdaftar.value}")
        assert "tidak ditemukan" in str(tidak_terdaftar.value)

    def test_pencairan_menggunakan_id_pinjaman_berupa_huruf(
        self, koneksi_test, pinjaman_siap_cair
    ):

        nik = pinjaman_siap_cair["nik"]
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = "abc"

        with pytest.raises(InputTidakValid) as tipe_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )
        print(f"pesan error : {tipe_error.value}")
        assert "berupa angka" in str(tipe_error.value)

    @pytest.mark.parametrize("status_salah", ["diajukan", "aktif", "lunas", "ditolak"])
    def test_pencairan_status_salah(
        self, koneksi_test, status_salah, pinjaman_siap_cair
    ):

        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]
        koneksi_test.execute(
            "UPDATE pinjaman SET status = ? WHERE id = ?", (status_salah, id_pinjaman)
        )
        koneksi_test.commit()

        nik = pinjaman_siap_cair["nik"]
        norek = pinjaman_siap_cair["norek"]

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )
        print(f"Pesan error: {info_error.value}")
        assert "belum disetujui" in str(info_error.value)

    @pytest.mark.parametrize("status_rekening", ["blokir", "tutup"])
    def test_pencairan_dengan_status_rekening_selain_aktif(
        self, koneksi_test, status_rekening, pinjaman_siap_cair
    ):
        norek = pinjaman_siap_cair["norek"]
        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?", (status_rekening, norek)
        )

        koneksi_test.commit()

        nik = pinjaman_siap_cair["nik"]
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )

        print(f"Pesan error: {info_error.value}")
        assert "saat ini sedang" in str(info_error.value)

    def test_pencairan_ganda(self, koneksi_test, pinjaman_siap_cair):

        nik = pinjaman_siap_cair["nik"]
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        PinjamanService.cairkan_pinjaman(
            nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
        )

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )
        assert "belum disetujui" in str(info_error.value)

    def test_rollback_pencairan(self, koneksi_test, pinjaman_siap_cair, monkeypatch):

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def penggagal_pencairan(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulasi pencairan gagal")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository, "tambah_riwayat", penggagal_pencairan
        )

        nik = pinjaman_siap_cair["nik"]
        norek = pinjaman_siap_cair["norek"]
        id_pinjaman = pinjaman_siap_cair["id_pinjaman"]

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        with pytest.raises(RuntimeError):
            PinjamanService.cairkan_pinjaman(
                nik=nik, norek_pencairan=norek, id_pinjaman=id_pinjaman
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()
        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum
        assert data_pinjaman["cicilan_tetap"] == 0
        assert data_pinjaman["sisa_pokok"] == 0
        assert data_pinjaman["tanggal_pencairan"] is None
        assert data_pinjaman["tanggal_jatuh_tempo"] is None
        assert data_pinjaman["status"] == StatusPinjaman.DISETUJUI.value


class TestBayarCicilan:

    def test_bayar_cicilan_pertama_happy_path(self, koneksi_test):
        koneksi_test.execute(
            """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
            ("Pengujian", "jln.ninjaku", "987654321"),
        )

        koneksi_test.execute(
            """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?)""",
            (
                "123456",
                "987654321",
                10_000_000,
                "1234",
                "2026-01-19",
                "2026-01-20",
                "2026-02-23",
                "2026-02-23",
            ),
        )

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,
        norek, 
        nominal_pinjaman, 
        bunga,
        tenor,
        sisa_pokok,
        status,
        tanggal_pencairan,
        tanggal_jatuh_tempo,
        cicilan_terbayar,
        cicilan_tetap
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                "123456",
                2_000_000,
                0.12,
                6,
                2_000_000,
                "aktif",
                "2026-09-20",
                "2026-10-20",
                0,
                345_103,
            ),
        )

        koneksi_test.commit()

        hari_ini = date(2026, 10, 21)

        PinjamanService.bayar_cicilan(
            nik="987654321", norek_pembayaran="123456", id_pinjaman=1, hari_ini=hari_ini
        )

        cursor = koneksi_test.execute("""SELECT * FROM pinjaman WHERE id = ?""", (1,))
        hasil = cursor.fetchone()

        cicilan_tetap = hasil["cicilan_tetap"]
        sisa_pokok = hasil["sisa_pokok"]
        waktu_pencairan = hasil["tanggal_pencairan"]
        waktu_jatuh_tempo = hasil["tanggal_jatuh_tempo"]
        cicilan_terbayar = hasil["cicilan_terbayar"]
        status = hasil["status"]

        assert cicilan_tetap == 345_103
        assert sisa_pokok == 1_674_897
        assert waktu_pencairan is not None
        assert waktu_jatuh_tempo is not None
        assert status == "aktif"
        assert cicilan_terbayar != 0

    @pytest.fixture
    def pinjaman_siap_dibayar_cicilannya(self, koneksi_test):
        koneksi_test.execute(
            """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
            ("Pengujian", "jln.ninjaku", "987654321"),
        )

        koneksi_test.execute(
            """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?)""",
            (
                "123456",
                "987654321",
                10_000_000,
                "1234",
                "2026-01-19",
                "2026-01-20",
                "2026-02-23",
                "2026-02-23",
            ),
        )

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,
        norek, 
        nominal_pinjaman, 
        bunga,
        tenor,
        sisa_pokok,
        status,
        tanggal_pencairan,
        tanggal_jatuh_tempo,
        cicilan_terbayar,
        cicilan_tetap
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                "123456",
                2_000_000,
                0.12,
                6,
                2_000_000,
                "aktif",
                "2026-09-20",
                "2026-10-20",
                0,
                345_103,
            ),
        )

        koneksi_test.commit()

        return {"nik": "987654321", "norek": "123456", "id_pinjaman": 1}

    def test_bayar_cicilan_sebelum_jatuh_tempo(
        self,
        koneksi_test,
    ):
        koneksi_test.execute(
            """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
            ("Pengujian", "jln.ninjaku", "987654321"),
        )

        koneksi_test.execute(
            """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?)""",
            (
                "123456",
                "987654321",
                10_000_000,
                "1234",
                "2026-01-19",
                "2026-01-20",
                "2026-02-23",
                "2026-02-23",
            ),
        )

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,
        norek, 
        nominal_pinjaman, 
        bunga,
        tenor,
        sisa_pokok,
        status,
        tanggal_pencairan,
        tanggal_jatuh_tempo,
        cicilan_terbayar,
        cicilan_tetap
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                "123456",
                2_000_000,
                0.12,
                6,
                2_000_000,
                "aktif",
                "2026-09-20",
                "2026-11-20",
                1,
                345_103,
            ),
        )

        koneksi_test.commit()

        hari_ini = date(2026, 10, 19)

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.bayar_cicilan(
                nik="987654321",
                norek_pembayaran="123456",
                id_pinjaman=1,
                hari_ini=hari_ini,
            )

        print(f"pesan error :{info_error.value}")
        assert "baru boleh dibayar" in str(info_error.value)

    def test_bayar_cicilan_dengan_norek_salah(
        self, koneksi_test, pinjaman_siap_dibayar_cicilannya
    ):

        with pytest.raises(RekeningTidakSesuai) as norek_salah:
            hari_ini = date(2026, 9, 18)
            PinjamanService.bayar_cicilan(
                nik=pinjaman_siap_dibayar_cicilannya["nik"],
                norek_pembayaran="5554",
                id_pinjaman=pinjaman_siap_dibayar_cicilannya["id_pinjaman"],
                hari_ini=hari_ini,
            )

        print(f"pesan error : {norek_salah.value}")
        assert "pemilik pinjaman" in str(norek_salah.value)

    def test_bayar_cicilan_dengan_nik_salah(
        self, koneksi_test, pinjaman_siap_dibayar_cicilannya
    ):

        with pytest.raises(NikTidakSesuai) as nik_salah:
            hari_ini = date(2026, 9, 18)
            PinjamanService.bayar_cicilan(
                nik="9990",
                norek_pembayaran=pinjaman_siap_dibayar_cicilannya["norek"],
                id_pinjaman=pinjaman_siap_dibayar_cicilannya["id_pinjaman"],
                hari_ini=hari_ini,
            )

        print(f"pesan error : {nik_salah.value}")
        assert "pemilik pinjaman" in str(nik_salah.value)

    def test_bayar_cicilan_dengan_id_pinjaman_negatif(
        self, koneksi_test, pinjaman_siap_dibayar_cicilannya
    ):

        with pytest.raises(InputTidakValid) as info_id:
            hari_ini = date(2026, 9, 18)
            PinjamanService.bayar_cicilan(
                nik=pinjaman_siap_dibayar_cicilannya["nik"],
                norek_pembayaran=pinjaman_siap_dibayar_cicilannya["norek"],
                id_pinjaman=-9,
                hari_ini=hari_ini,
            )

        print(f"pesan error : {info_id.value}")
        assert "tidak valid" in str(info_id.value)

    def test_bayar_cicilan_dengan_id_tidak_terdaftar(
        self, koneksi_test, pinjaman_siap_dibayar_cicilannya
    ):

        with pytest.raises(PinjamanTidakDitemukan) as info_id:
            hari_ini = date(2026, 9, 18)
            PinjamanService.bayar_cicilan(
                nik=pinjaman_siap_dibayar_cicilannya["nik"],
                norek_pembayaran=pinjaman_siap_dibayar_cicilannya["norek"],
                id_pinjaman=100,
                hari_ini=hari_ini,
            )

        print(f"pesan error : {info_id.value}")
        assert "tidak ditemukan" in str(info_id.value)

    def test_bayar_cicilan_dengan_id_berupa_huruf(
        self, koneksi_test, pinjaman_siap_dibayar_cicilannya
    ):

        with pytest.raises(InputTidakValid) as info_error:

            PinjamanService.bayar_cicilan(
                nik=pinjaman_siap_dibayar_cicilannya["nik"],
                norek_pembayaran=pinjaman_siap_dibayar_cicilannya["norek"],
                id_pinjaman="abc",
                hari_ini=date(2026, 10, 19),
            )

        print(f"pesan error : {info_error.value}")

        assert "berupa angka" in str(info_error.value)

    def test_bayar_cicilan_setelah_8_hari(
        self, koneksi_test, pinjaman_siap_dibayar_cicilannya
    ):
        hari_ini = date(2026, 10, 28)

        denda = 345

        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek="123456", koneksi=koneksi_test
        )

        PinjamanService.bayar_cicilan(
            nik=pinjaman_siap_dibayar_cicilannya["nik"],
            norek_pembayaran=pinjaman_siap_dibayar_cicilannya["norek"],
            id_pinjaman=pinjaman_siap_dibayar_cicilannya["id_pinjaman"],
            hari_ini=hari_ini,
        )

        total_bayar = 345_103 + denda

        saldo_sesudah = RekeningRepository.ambil_saldo(
            norek="123456", koneksi=koneksi_test
        )

        assert saldo_sesudah == saldo_sebelum - total_bayar

    def test_bayar_cicilan_terakhir_untuk_pelunasan(self, koneksi_test):

        koneksi_test.execute(
            """INSERT INTO nasabah (nama,alamat,nik) VALUES (?,?,?)""",
            ("Pengujian", "jln.ninjaku", "987654321"),
        )

        koneksi_test.execute(
            """INSERT INTO rekening
        (norek, nik_pemilik, saldo, pin, waktu_dibuat, reset, dapat_bunga, waktu_bayar_admin)
        VALUES(?,?,?,?,?,?,?,?)""",
            (
                "123456",
                "987654321",
                10_000_000,
                "1234",
                "2026-01-19",
                "2026-01-20",
                "2026-02-23",
                "2026-02-23",
            ),
        )

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,
        norek,
         nominal_pinjaman, 
         bunga,
         tenor,
         sisa_pokok,
         status,
         tanggal_pencairan,
         tanggal_jatuh_tempo,
         cicilan_terbayar,
         cicilan_tetap
         ) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                "123456",
                2_000_000,
                0.12,
                6,
                341_648,
                "aktif",
                "2026-09-20",
                "2026-10-20",
                5,
                345_103,
            ),
        )

        koneksi_test.commit()

        PinjamanService.bayar_cicilan(
            nik="987654321",
            norek_pembayaran="123456",
            id_pinjaman=1,
            hari_ini=date(2027, 2, 21),
        )

        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=1, koneksi=koneksi_test
        )

        sisa_pokok = data_pinjaman["sisa_pokok"]
        status = data_pinjaman["status"]
        cicilan_terbayar = data_pinjaman["cicilan_terbayar"]

        assert sisa_pokok == 0
        assert status == "lunas"
        assert cicilan_terbayar == 6


class TestAjukanPinjaman:


    @staticmethod
    def _hitung_jejak_pinjaman(koneksi, norek):
        return (
            koneksi.execute("SELECT COUNT(*) FROM pinjaman WHERE norek = ?", (norek,)).fetchone()[0],
            koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'pembukaan pinjaman'", (norek,)
            ).fetchone()[0],
            koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'pengajuan_pinjaman'", (norek,)
            ).fetchone()[0],
        )

    def test_ajukan_pinjaman_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah['pin']
        id_pnjaman = PinjamanService.ajukan_pinjaman(
            nik=nik, norek=norek, nominal=1_000_000, tenor=6, pin=pin
        )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()

        riwayat = koneksi_test.execute(
            "SELECT * FROM riwayat WHERE norek = ?", (norek,)
        ).fetchone()

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek =?", (norek,)
        ).fetchone()

        assert data_pinjaman is not None
        assert riwayat is not None
        assert audit is not None
        assert data_pinjaman["norek"] == norek
        assert data_pinjaman["status"] == StatusPinjaman.DIAJUKAN.value
        assert data_pinjaman["tenor"] == 6
        assert data_pinjaman["nominal_pinjaman"] == 1_000_000
        assert data_pinjaman["cicilan_tetap"] == 0
        assert data_pinjaman["cicilan_terbayar"] == 0
        assert data_pinjaman["sisa_pokok"] == 0
        assert data_pinjaman["tanggal_pencairan"] is None
        assert data_pinjaman["tanggal_jatuh_tempo"] is None
        assert id_pnjaman is not None



    @pytest.mark.parametrize(
        "kwargs_salah, pesan_error",
        [
            # NIK
            pytest.param({"nik": None}, "NIK tidak boleh kosong", id="nik None"),
            pytest.param({"nik": ""}, "NIK tidak boleh kosong", id="nik kosong"),
            pytest.param({"nik": " "}, "NIK tidak boleh kosong", id="nik spasi"),
            pytest.param({"nik": "12345abcde123456"}, "NIK tidak boleh mengandung huruf", id="nik ada huruf"),
            pytest.param({"nik": "3" * 15}, "Jumlah digit NIK tidak valid", id="nik 15 digit"),
            pytest.param({"nik": "3" * 17}, "Jumlah digit NIK tidak valid", id="nik 17 digit"),
            # norek
            pytest.param({"norek": None}, "Nomor rekening tidak boleh kosong", id="norek None"),
            pytest.param({"norek": ""}, "Nomor rekening tidak boleh kosong", id="norek kosong"),
            pytest.param({"norek": " "}, "Nomor rekening tidak boleh kosong", id="norek spasi"),
            pytest.param({"norek": "12345abcde123456"}, "Nomor rekening tidak boleh mengandung huruf",
                         id="norek ada huruf"),
            pytest.param({"norek": "2" * 15}, "Jumlah digit nomor rekening tidak valid", id="norek 15 digit"),
            pytest.param({"norek": "2" * 17}, "Jumlah digit nomor rekening tidak valid", id="norek 17 digit"),
            # PIN
            pytest.param({"pin": None}, "PIN tidak boleh kosong", id="pin None"),
            pytest.param({"pin": ""}, "PIN tidak boleh kosong", id="pin kosong"),
            pytest.param({"pin": " "}, "PIN tidak boleh kosong", id="pin spasi"),
            pytest.param({"pin": "1234"}, "PIN harus berupa 6 digit angka", id="pin kurang"),
            pytest.param({"pin": "12345q"}, "PIN harus berupa 6 digit angka", id="pin ada huruf"),
            # tenor
            pytest.param({"tenor": None}, "Jangka waktu harus berupa angka", id="tenor None"),
            pytest.param({"tenor": "abc"}, "Jangka waktu harus berupa angka", id="tenor huruf"),
            pytest.param({"tenor": 0}, "Pilihan tenor pinjaman tidak tersedia", id="tenor 0"),
            pytest.param({"tenor": -6}, "Pilihan tenor pinjaman tidak tersedia", id="tenor minus"),
            pytest.param({"tenor": 7}, "Pilihan tenor pinjaman tidak tersedia", id="tenor tidak tersedia"),
            # nominal
            pytest.param({"nominal": None}, "Nominal harus berupa angka", id="nominal None"),
            pytest.param({"nominal": "abc"}, "Nominal harus berupa angka", id="nominal huruf"),
            pytest.param({"nominal": 0}, "Nominal pinjaman di bawah batas minimal", id="nominal 0"),
            pytest.param({"nominal": -1_000_000}, "Nominal pinjaman di bawah batas minimal", id="nominal minus"),
            pytest.param({"nominal": 999_999}, "Nominal pinjaman di bawah batas minimal", id="nominal kurang"),
            pytest.param({"nominal": 50_000_001}, "Nominal pinjaman melebihi batas maksimal", id="nominal lebih"),
            # bukti urutan: cek murah sebelum PIN, jadi PIN salah tidak sempat dihitung
            pytest.param({"nominal": 999_999, "pin": "123457"}, "Nominal pinjaman di bawah batas minimal",
                         id="nominal cacat dan pin salah"),
            pytest.param({"tenor": 7, "pin": "123457"}, "Pilihan tenor pinjaman tidak tersedia",
                         id="tenor cacat dan pin salah"),
            pytest.param({"norek": "2" * 15, "pin": "123457"}, "Jumlah digit nomor rekening tidak valid",
                         id="norek cacat dan pin salah"),
        ],
    )
    def test_ajukan_pinjaman_dengan_input_tidak_valid(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah, pesan_error
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        kwargs = {"nik": nik, "norek": norek, "pin": pin, "nominal": 1_000_000, "tenor": 6}
        kwargs.update(kwargs_salah)

        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(InputTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(**kwargs)

        percobaan_gagal = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_gagal == 0
        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert pesan_error in str(info_error.value)

    @pytest.mark.parametrize(
        "kwargs_salah",
        [
            pytest.param({"nik": "2" * 16}, id="nik bukan pemilik"),
            pytest.param({"norek": "4" * 16}, id="norek tidak ada"),
        ],
    )
    def test_ajukan_pinjaman_dengan_identitas_tidak_ditemukan(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah, kwargs_salah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah["pin"]

        kwargs = {"nik": nik, "norek": norek, "pin": pin, "nominal": 1_000_000, "tenor": 6}
        kwargs.update(kwargs_salah)

        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            PinjamanService.ajukan_pinjaman(**kwargs)

        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert "Rekening tidak terdaftar" in str(info_error.value)


    @pytest.mark.parametrize("status_rekening_salah", ["blokir", "tutup"])
    def test_ajukan_pinjaman_dengan_rekening_selain_aktif(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, status_rekening_salah
    ):

        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?",
            (status_rekening_salah, siapkan_data_rekening_dan_nasabah["norek"]),
        )

        koneksi_test.commit()

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah['pin']

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6,pin=pin
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()
        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan pinjaman'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pengajuan_pinjaman'",(norek,)).fetchone()

        assert data_pinjaman is None
        assert riwayat is None
        assert audit is None
        assert f"Rekening Anda saat ini sedang di{status_rekening_salah}" in str(info_error.value)

    @pytest.mark.parametrize("status_pinjaman_sebelumnya", ["diajukan", "disetujui"])
    def test_ajukan_pinjaman_saat_masih_ada_pinjaman_belum_disetujui_atau_masih_diajukan(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        status_pinjaman_sebelumnya,
    ):


        koneksi_test.execute(
            """INSERT INTO pinjaman (id, norek, nominal_pinjaman, bunga, tenor, sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                1_000_000,
                0.1,
                6,
                0,
                status_pinjaman_sebelumnya,
            ),
        )

        koneksi_test.commit()

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah['pin']

        jumlah_pinjaman = koneksi_test.execute("SELECT COUNT(*) FROM pinjaman WHERE norek = ?",(norek,)).fetchone()[0]

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6, pin=pin
            )


        jumlah_pinjaman_sesudah = koneksi_test.execute("SELECT COUNT(*) FROM pinjaman WHERE norek = ?",(norek,)).fetchone()[0]
        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan pinjaman'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pengajuan_pinjaman'",(norek,)).fetchone()

        assert jumlah_pinjaman == jumlah_pinjaman_sesudah
        assert riwayat is None
        assert audit is None

        assert "masih memiliki pengajuan pinjaman" in str(info_error.value)

    def test_ajukan_pinjaman_pin_salah_mencatat_percobaan_gagal(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin_salah = "123457"

        percobaan_sebelum = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]
        assert percobaan_sebelum == 0
        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(PinTidakCocok) as info_error:
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, pin=pin_salah, nominal=1_000_000, tenor=6
            )

        percobaan_sesudah = koneksi_test.execute(
            "SELECT percobaan_gagal FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["percobaan_gagal"]

        assert percobaan_sesudah == 1
        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert "PIN yang dimasukkan salah" in str(info_error.value)

    def test_ajukan_pinjaman_rekening_terkunci_dengan_pin_benar(
            self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin_benar = siapkan_data_rekening_dan_nasabah["pin"]

        waktu_kunci = (datetime.datetime.now() + datetime.timedelta(minutes=5)).isoformat()
        koneksi_test.execute(
            "UPDATE rekening SET percobaan_gagal = 3, terkunci_sampai = ? WHERE norek = ?",
            (waktu_kunci, norek),
        )
        koneksi_test.commit()
        jejak_sebelum = self._hitung_jejak_pinjaman(koneksi_test, norek)

        with pytest.raises(RekeningTerkunci) as info_error:
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, pin=pin_benar, nominal=1_000_000, tenor=6
            )

        waktu_kunci_sesudah = koneksi_test.execute(
            "SELECT terkunci_sampai FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()["terkunci_sampai"]

        assert waktu_kunci_sesudah == waktu_kunci
        assert self._hitung_jejak_pinjaman(koneksi_test, norek) == jejak_sebelum
        assert "Rekening terkunci sementara karena terlalu banyak percobaan PIN salah" in str(info_error.value)



    def test_rollback_ajukan_pinjaman(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, monkeypatch
    ):

        method_asli = riwayat_repo_module.RiwayatRepository.tambah_riwayat

        def penggagal_simpan_data(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulasi gagal menyimpan data pinjaman")

        monkeypatch.setattr(
            riwayat_repo_module.RiwayatRepository,
            "tambah_riwayat",
            penggagal_simpan_data,
        )

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        pin = siapkan_data_rekening_dan_nasabah['pin']

        with pytest.raises(RuntimeError):
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6, pin=pin
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()
        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan pinjaman'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pengajuan_pinjaman'",(norek,)).fetchone()

        assert data_pinjaman is None
        assert riwayat is None
        assert audit is None



class TestSetujuiAtauTolakPinjaman:

    @pytest.fixture
    def pinjaman_siap_diputuskan(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,norek, nominal_pinjaman, bunga,tenor,sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                2_000_000,
                0.12,
                6,
                0,
                "diajukan",
            ),
        )
        koneksi_test.commit()

        return {"id_pinjaman": 1}

    @pytest.mark.parametrize(
        "fungsi_service, kwargs_tambahan, status_pinjaman, catatan_diharapkan,aksi_diharapkan",
        [
            (
                PinjamanService.setujui_pinjaman,
                {},
                StatusPinjaman.DISETUJUI.value,
                None,
                "persetujuan_pinjaman",
            ),
            (
                PinjamanService.tolak_pinjaman,
                {"catatan_admin": "Pinjaman ditolak untuk tes"},
                StatusPinjaman.DITOLAK.value,
                "Pinjaman ditolak untuk tes",
                "penolakan_pinjaman",
            ),
        ],
    )
    def test_setujui_dan_tolak_pinjaman_happy_path(
        self,
        koneksi_test,
        fungsi_service,
        kwargs_tambahan,
        pinjaman_siap_diputuskan,
        status_pinjaman,
        catatan_diharapkan,
        siapkan_data_rekening_dan_nasabah,
        aksi_diharapkan,
    ):
        id_pinjaman = pinjaman_siap_diputuskan["id_pinjaman"]
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        fungsi_service(id_pinjaman=id_pinjaman, **kwargs_tambahan)

        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=id_pinjaman, koneksi=koneksi_test
        )

        notifikasi = NotifikasiRepository.cari_notifikasi_dengan_referensi(
            nik_pemilik=nik,
            jenis_referensi=JenisReferensi.PINJAMAN,
            id_objek=id_pinjaman,
            koneksi=koneksi_test,
        )
        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        assert data_pinjaman["status"] == status_pinjaman
        assert notifikasi is not None
        assert audit is not None
        assert audit["aksi"] == aksi_diharapkan
        if catatan_diharapkan is not None:
            assert data_pinjaman["catatan_admin"] == catatan_diharapkan

    @pytest.mark.parametrize(
        "fungsi_service, id_invalid, kwargs_tambahan, pesan_diharapkan",
        [
            (PinjamanService.setujui_pinjaman, "abc", {}, "berupa angka"),
            (PinjamanService.setujui_pinjaman, -1, {}, "tidak valid"),
            (
                PinjamanService.tolak_pinjaman,
                "abc",
                {"catatan_admin": "penolakan untuk pengujian"},
                "berupa angka",
            ),
            (
                PinjamanService.tolak_pinjaman,
                -1,
                {"catatan_admin": "penolakan untuk pengujian"},
                "tidak valid",
            ),
        ],
    )
    def test_setujui_atau_tolak_pinjaman_dengan_id_invalid(
        self, fungsi_service, id_invalid, kwargs_tambahan, pesan_diharapkan
    ):
        with pytest.raises(InputTidakValid) as info_error:
            fungsi_service(id_pinjaman=id_invalid, **kwargs_tambahan)

        assert pesan_diharapkan in str(info_error.value)

    @pytest.mark.parametrize(
        "fungsi_service, kwargs_tambahan, status_salah",
        [
            (PinjamanService.setujui_pinjaman, {}, "aktif"),
            (PinjamanService.setujui_pinjaman, {}, "disetujui"),
            (PinjamanService.setujui_pinjaman, {}, "ditolak"),
            (
                PinjamanService.tolak_pinjaman,
                {"catatan_admin": "penolakan untuk pengujian"},
                "aktif",
            ),
            (
                PinjamanService.tolak_pinjaman,
                {"catatan_admin": "penolakan untuk pengujian"},
                "disetujui",
            ),
            (
                PinjamanService.tolak_pinjaman,
                {"catatan_admin": "penolakan untuk pengujian"},
                "ditolak",
            ),
        ],
    )
    def test_setujui_atau_tolak_pinjaman_dengan_status_salah(
        self,
        koneksi_test,
        fungsi_service,
        kwargs_tambahan,
        status_salah,
        siapkan_data_rekening_dan_nasabah,
    ):

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,norek, nominal_pinjaman, bunga,tenor,sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                2_000_000,
                0.12,
                6,
                0,
                status_salah,
            ),
        )
        koneksi_test.commit()

        id_pinjaman = 1

        with pytest.raises(StatusTidakValid) as info_error:
            fungsi_service(id_pinjaman=id_pinjaman, **kwargs_tambahan)

        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=id_pinjaman, koneksi=koneksi_test
        )

        print(f"pesan errof : {info_error.value}")
        assert data_pinjaman["status"] == status_salah
        assert "Pinjaman tidak dapat" in str(info_error.value)

    def test_setujui_atau_tolak_pinjaman_race_condition(
        self, koneksi_test, pinjaman_siap_diputuskan, monkeypatch
    ):

        id_pinjaman = pinjaman_siap_diputuskan["id_pinjaman"]
        method_asli = pinjaman_repo_module.PinjamanRepository.perbarui_status_pinjaman

        def penggagal_pengubah_keputusan(**kwargs):
            koneksi_test.execute(
                "UPDATE pinjaman SET status = 'disetujui' WHERE id = ?", (id_pinjaman,)
            )

            koneksi_test.commit()

            return method_asli(**kwargs)

        monkeypatch.setattr(
            pinjaman_repo_module.PinjamanRepository,
            "perbarui_status_pinjaman",
            penggagal_pengubah_keputusan,
        )

        with pytest.raises(PerbaruiStatusGagal) as info_error:

            PinjamanService.setujui_pinjaman(id_pinjaman=id_pinjaman)

        assert "memperbarui status pinjaman" in str(info_error.value)

    @pytest.mark.parametrize(
        "fungsi_service, kwargs_tambahan",
        [
            (PinjamanService.setujui_pinjaman, {}),
            (
                PinjamanService.tolak_pinjaman,
                {"catatan_admin": "penolakan untuk pengujian"},
            ),
        ],
    )
    def test_rollback_setujui_atau_tolak_pinjaman(
        self,
        koneksi_test,
        pinjaman_siap_diputuskan,
        monkeypatch,
        fungsi_service,
        kwargs_tambahan,
        siapkan_data_rekening_dan_nasabah,
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        id_pinjaman = pinjaman_siap_diputuskan["id_pinjaman"]
        method_asli = audit_repo_module.AuditRepository.tambah_audit

        def uji_rollback(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Uji rollback keputusan untuk pinjaman")

        monkeypatch.setattr(
            audit_repo_module.AuditRepository, "tambah_audit", uji_rollback
        )

        with pytest.raises(RuntimeError):
            fungsi_service(id_pinjaman=id_pinjaman, **kwargs_tambahan)

        data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(
            id_pinjaman=id_pinjaman, koneksi=koneksi_test
        )
        notifikasi = NotifikasiRepository.cari_notifikasi_dengan_referensi(
            nik_pemilik=nik,
            jenis_referensi=JenisReferensi.PINJAMAN,
            id_objek=id_pinjaman,
            koneksi=koneksi_test,
        )

        audit = koneksi_test.execute(
            "SELECT * FROM audit WHERE norek = ?", (norek,)
        ).fetchone()

        assert data_pinjaman["status"] == StatusPinjaman.DIAJUKAN.value
        assert notifikasi is None
        assert audit is None
