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

        koneksi_test.execute(
            """INSERT INTO pinjaman (
        id,norek, nominal_pinjaman, bunga,tenor,sisa_pokok,status) VALUES (?,?,?,?,?,?,?)""",
            (1, "123456", 2_000_000, 0.12, 6, 0, "disetujui"),
        )

        koneksi_test.commit()

        return {"nik": "987654321", "norek": "123456", "id_pinjaman": 1}

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

    def test_ajukan_pinjaman_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = "987654321"
        norek = "123456"
        id_pnjaman = PinjamanService.ajukan_pinjaman(
            nik=nik, norek=norek, nominal=1_000_000, tenor=6
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

    def test_ajukan_pinjaman_dengan_nik_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = "87654321"
        norek = "123456"

        with pytest.raises(NikTidakSesuai) as info_error:

            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert "tidak terdaftar sebagai" in str(info_error.value)
        assert data_pinjaman is None

    def test_ajukan_pinjaman_dengan_norek_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = "87654321"
        norek = "12345"

        with pytest.raises(RekeningTidakDitemukan) as info_error:

            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()

        print(f"pesan error : {info_error.value}")
        assert "tidak ditemukan" in str(info_error.value)
        assert data_pinjaman is None

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

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()

        assert data_pinjaman is None
        print(f"pesan error : {info_error.value}")
        assert "Anda saat ini " in str(info_error.value)

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

        with pytest.raises(StatusTidakValid) as info_error:
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6
            )

        print(f"pesan error : {info_error.value}")
        assert "masih memiliki pengajuan pinjaman" in str(info_error.value)

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

        with pytest.raises(RuntimeError):
            PinjamanService.ajukan_pinjaman(
                nik=nik, norek=norek, nominal=1_000_000, tenor=6
            )

        data_pinjaman = koneksi_test.execute(
            "SELECT * FROM pinjaman WHERE norek = ?", (norek,)
        ).fetchone()

        assert data_pinjaman is None


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
