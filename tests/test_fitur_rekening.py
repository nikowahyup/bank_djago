import datetime

import pytest


from bank_djago import RekeningService
from bank_djago.conftest import siapkan_data_rekening_dan_nasabah, koneksi_test
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.services.exceptions import (
    NikTidakSesuai,
    RekeningTidakDitemukan,
    InputTidakValid,
    StatusTidakValid,
    LevelRekeningTidakValid, PerbaruiStatusGagal, NasabahTidakDitemukan,
)

import bank_djago.penyimpanan.repositories.audit_repository as audit_repo_module
import bank_djago.penyimpanan.repositories.rekening_repository as rekening_repo_module

from bank_djago.core.rekening import RekeningReguler,RekeningPrioritas, RekeningGold, RekeningPlatinum

reguler = RekeningReguler(norek="1234",pin='1234',pemilik=None)
prioritas = RekeningPrioritas(norek="1234",pin='1234',pemilik=None)
gold = RekeningGold(norek="1234",pin='1234',pemilik=None)
platinum = RekeningPlatinum(norek="1234",pin='1234',pemilik=None)


jenis_rekening = {
    1: {
        "minimal_upgrade": 0,
        "limit_sisa" :reguler.limit_sisa,
        "minimal_setor":reguler.saldosetor_min
    },
    2: {
        "minimal_upgrade": 3_000_000,
        "limit_sisa" : prioritas.limit_sisa,
        "minimal_setor":prioritas.saldosetor_min
    },
    3: {
        "minimal_upgrade": 50_000_000,
        "limit_sisa" : gold.limit_sisa,
        "minimal_setor":gold.saldosetor_min
    },
    4: {
        "minimal_upgrade": 200_000_000,
        "limit_sisa" : platinum.limit_sisa,
        "minimal_setor":platinum.saldosetor_min
    },
}


def konversi_waktu(waktu):
    return datetime.date.fromisoformat(waktu) if waktu is not None else None


class TestTingkatkanRekening:

    def test_tingkatkan_rekening_happy_path(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        target_level = 2  # untuk rekening prioritas, saldo rekening yang sudah disiapkan ini sudah cocok
        rekening = RekeningLoader.muat_rekening(norek=norek, koneksi=koneksi_test)

        assert rekening.saldo >= rekening.saldosetor_min

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        saldo_sebelum = data_rekening["saldo"]
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        assert level == 1
        assert terakhir_ubah is None  # pertama kali ubah pasti None

        RekeningService.upgrade_rekening(
            nik=nik, norek=norek, target_level=target_level
        )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'peningkatan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'peningkatan_level_rekening'",(norek,)).fetchone()

        level = data_rekening_sesudah["level"]
        saldo_sesudah = data_rekening_sesudah["saldo"]
        terakhir_ubah = konversi_waktu(data_rekening_sesudah["terakhir_ubah_rekening"])
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        assert riwayat is not None
        assert audit is not None
        assert limit_sisa_sesudah != limit_sisa_sebelum
        assert level == target_level
        assert saldo_sesudah == saldo_sebelum
        assert terakhir_ubah == datetime.date.today()

    @pytest.mark.parametrize(
        "target_invalid, pesan_error",
        [
            (5, "Level rekening tidak tersedia"),
            ("abc", "Level rekening harus berupa angka"),
            (0, "Level rekening harus di antara 1 - 4"),
        ],
    )
    def test_tingkatkan_rekening_dengan_pilihan_target_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        target_invalid,
        pesan_error,
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=target_invalid
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = data_rekening_sesudah["terakhir_ubah_rekening"]
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sesudah == limit_sisa_sebelum
        assert pesan_error in str(info_error.value)

    def test_tingkatkan_rekening_dengan_nik_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = "0000"
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        target_level = 2

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(NikTidakSesuai) as info_error:
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=target_level
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = data_rekening_sesudah["terakhir_ubah_rekening"]
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sesudah == limit_sisa_sebelum
        assert "NIK ini tidak terdaftar sebagai" in str(info_error.value)

    def test_tingkatkan_rekening_dengan_norek_salah(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):
        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = "111222"
        target_level = 2
        norek_asli = siapkan_data_rekening_dan_nasabah["norek"]

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek_asli,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(RekeningTidakDitemukan) as info_error:
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=target_level
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek_asli,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = data_rekening_sesudah["terakhir_ubah_rekening"]
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sesudah == limit_sisa_sebelum
        assert "Rekening tidak terdaftar" in str(info_error.value)

    def test_tingkatkan_rekening_lebih_dari_sekali_dalam_sehari(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        target_level = 2

        terakhir_ubah_rekening = datetime.date.today()

        koneksi_test.execute(
            "UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",
            (terakhir_ubah_rekening.isoformat(), norek),
        )
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=target_level
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = konversi_waktu(
            data_rekening_sesudah["terakhir_ubah_rekening"]
        )
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sebelum == limit_sisa_sesudah
        assert "rekening hanya bisa dilakukan 1 kali" in str(info_error.value)

    @pytest.mark.parametrize(
        "level_sekarang, level_peningkatan, exception,pesan_error", [(1, 1,LevelRekeningTidakValid,"lebih tinggi dari level saat ini"), (3, 2,LevelRekeningTidakValid, "lebih tinggi dari level saat ini"),(4,3,StatusTidakValid,"sudah level tertinggi")]
    )
    def test_tingkatkan_rekening_dengan_pilihan_level_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        level_sekarang,
        level_peningkatan,
        exception,
        pesan_error
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        koneksi_test.execute(
            "UPDATE rekening SET level = ? WHERE norek = ?", (level_sekarang, norek)
        )
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(exception) as info_error:
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=level_peningkatan
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = konversi_waktu(
            data_rekening_sesudah["terakhir_ubah_rekening"]
        )
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sesudah == limit_sisa_sebelum
        assert pesan_error in str(info_error.value)


    @pytest.mark.parametrize("status_salah", ["blokir", "tutup"])
    def test_tingkatkan_rekening_dengan_status_rekening_tidak_valid(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, status_salah
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        target_level = 2
        koneksi_test.execute(
            "UPDATE rekening SET status = ? WHERE norek = ?", (status_salah, norek)
        )
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=target_level
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = konversi_waktu(
            data_rekening_sesudah["terakhir_ubah_rekening"]
        )
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sesudah == limit_sisa_sebelum

        assert "Rekening Anda saat ini" in str(info_error.value)

    def test_rollback_peningkatan_rekening(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah, monkeypatch
    ):

        nik = siapkan_data_rekening_dan_nasabah["nik"]
        norek = siapkan_data_rekening_dan_nasabah["norek"]
        target_level = 2

        method_asli = audit_repo_module.AuditRepository.tambah_audit

        def uji_rollback(**kwargs):
            method_asli(**kwargs)

            raise RuntimeError("Simulasi rollback upgrade rekening")

        monkeypatch.setattr(
            audit_repo_module.AuditRepository, "tambah_audit", uji_rollback
        )
        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(RuntimeError, match="Simulasi rollback upgrade rekening"):
            RekeningService.upgrade_rekening(
                nik=nik, norek=norek, target_level=target_level
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = konversi_waktu(
            data_rekening_sesudah["terakhir_ubah_rekening"]
        )
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'peningkatan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'peningkatan_level_rekening'",(norek,)).fetchone()

        assert riwayat is None
        assert audit is None
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sesudah == limit_sisa_sebelum


    def test_race_condition_peningkatan_rekening(self, koneksi_test,siapkan_data_rekening_dan_nasabah, monkeypatch):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        target_level = 2
        method_asli = rekening_repo_module.RekeningRepository.ubah_state_setelah_upgrade_atau_downgrade
        kemarin = datetime.date.today() - datetime.timedelta(days=1)

        def uji_race_condition(**kwargs):
            koneksi_test.execute("UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",(kemarin.isoformat(), norek))
            koneksi_test.commit()
            return method_asli(**kwargs)

        monkeypatch.setattr(rekening_repo_module.RekeningRepository,"ubah_state_setelah_upgrade_atau_downgrade",uji_race_condition)

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        limit_sisa_sebelum = data_rekening["limit_sisa"]

        with pytest.raises(PerbaruiStatusGagal) as info_error:
            RekeningService.upgrade_rekening(nik=nik, norek=norek, target_level=target_level)


        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = konversi_waktu(
            data_rekening_sesudah["terakhir_ubah_rekening"]
        )
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'peningkatan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'peningkatan_level_rekening'",(norek,)).fetchone()

        assert riwayat is None
        assert audit is None
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == kemarin
        assert limit_sisa_sesudah == limit_sisa_sebelum
        assert "melakukan peningkatan" in str(info_error.value)



    @pytest.mark.parametrize("level_target",[2,3,4])
    def test_tingkatkan_rekening_dengan_saldo_tepat_minimal_persyaratan(self, koneksi_test, siapkan_data_rekening_dan_nasabah, level_target):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        update_saldo = jenis_rekening[level_target]['minimal_upgrade']

        koneksi_test.execute("UPDATE rekening SET saldo = ? WHERE norek = ?",(update_saldo, norek))
        koneksi_test.commit()
        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        level = data_rekening['level']
        limit_sisa_target = jenis_rekening[level_target]['limit_sisa']
        saldo = data_rekening['saldo']

        assert saldo == update_saldo
        assert terakhir_ubah is None
        assert level == 1

        RekeningService.upgrade_rekening(nik=nik, norek=norek, target_level=level_target)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])
        limit_sisa_baru = data_rekening_sesudah['limit_sisa']
        saldo_sesudah = data_rekening_sesudah['saldo']

        assert level_sesudah == level_target
        assert saldo_sesudah == saldo
        assert terakhir_ubah_sesudah == datetime.date.today()
        assert limit_sisa_baru == limit_sisa_target



    @pytest.mark.parametrize("level_target",[2,3,4])
    def test_tingkatkan_rekening_dengan_minimal_saldo_tidak_memenuhi(self, koneksi_test, siapkan_data_rekening_dan_nasabah,level_target):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']

        update_saldo = jenis_rekening[level_target]['minimal_upgrade'] - 1

        koneksi_test.execute("UPDATE rekening SET saldo = ? WHERE norek = ?",(update_saldo, norek))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        level_sebelum = data_rekening['level']
        saldo = data_rekening['saldo']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sebelum = data_rekening['limit_sisa']

        assert saldo  == update_saldo
        assert level_sebelum == 1
        assert terakhir_ubah is None

        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.upgrade_rekening(nik=nik, norek=norek, target_level=level_target)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sesudah = data_rekening_sesudah['limit_sisa']
        saldo_sesudah = data_rekening_sesudah['saldo']
        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        assert terakhir_ubah_sesudah == terakhir_ubah
        assert saldo == saldo_sesudah
        assert limit_sesudah == limit_sebelum
        assert level_sesudah == level_sebelum
        assert "memenuhi saldo minimum rekening" in str(info_error.value)


    def test_tingkatkan_rekening_dengan_waktu_ubah_memenuhi(self, koneksi_test, siapkan_data_rekening_dan_nasabah):

        nik = siapkan_data_rekening_dan_nasabah['nik']
        norek = siapkan_data_rekening_dan_nasabah['norek']
        target_level = 2
        hari_ini = datetime.date.today()
        update_terakhir_ubah = hari_ini - datetime.timedelta(days=1)

        koneksi_test.execute("UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",(update_terakhir_ubah.isoformat(), norek))
        koneksi_test.commit()
        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_target = jenis_rekening[target_level]['limit_sisa']
        assert terakhir_ubah == update_terakhir_ubah
        assert level == 1

        RekeningService.upgrade_rekening(nik=nik, norek=norek, target_level=target_level)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        limit_sesudah = data_rekening_sesudah['limit_sisa']
        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'peningkatan rekening'",(norek,)).fetchone()

        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'peningkatan_level_rekening'",(norek,)).fetchone()

        assert riwayat is not None
        assert audit is not None
        assert limit_target == limit_sesudah
        assert terakhir_ubah_sesudah == datetime.date.today()


class TestTurunkanRekening:


    @pytest.mark.parametrize("target_level",[2,1])
    def test_turunkan_rekening_happy_path(self, koneksi_test, siapkan_rekening_siap_diturunkan, target_level):

        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = siapkan_rekening_siap_diturunkan['norek']

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sisa = data_rekening['limit_sisa']
        limit_sisa_target = jenis_rekening[target_level]['limit_sisa']
        saldo = data_rekening['saldo']


        assert level == 3
        assert terakhir_ubah is None
        assert limit_sisa != limit_sisa_target

        RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=target_level)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']
        saldo_sesudah = data_rekening_sesudah['saldo']
        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        riwayat = koneksi_test.execute("SELECT COUNT (*) FROM riwayat WHERE norek = ? AND jenis = 'penurunan rekening'",(norek,)).fetchone()[0]
        audit = koneksi_test.execute("SELECT COUNT (*) FROM audit WHERE norek = ? AND aksi  = 'penurunan_level_rekening'",(norek,)).fetchone()[0]

        assert level_sesudah == target_level
        assert riwayat == 1
        assert audit == 1
        assert limit_sisa_sesudah == limit_sisa_target
        assert saldo == saldo_sesudah
        assert terakhir_ubah_sesudah == datetime.date.today()



    @pytest.mark.parametrize("input_invalid, pesan_error",[("abc","rekening harus berupa angka")
                                                           ,(0, "rekening harus di antara 1 - 4"),
                                                           (6, "rekening tidak tersedia"),
                                                           ])
    def test_turunkan_rekening_dengan_input_tidak_valid(self, koneksi_test,siapkan_rekening_siap_diturunkan, input_invalid,pesan_error):

        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = siapkan_rekening_siap_diturunkan['norek']

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sisa = data_rekening['limit_sisa']
        limit_sisa_level_ini = jenis_rekening[level]['limit_sisa']
        assert level == 3
        assert terakhir_ubah is None
        assert limit_sisa == limit_sisa_level_ini

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=input_invalid)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']

        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        assert limit_sisa_sesudah == limit_sisa_level_ini
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert pesan_error in str(info_error.value)


    def test_turunkan_rekening_dengan_nik_salah(self, koneksi_test, siapkan_rekening_siap_diturunkan):

        nik = "999"
        norek = siapkan_rekening_siap_diturunkan['norek']
        target_level = 2

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sisa = data_rekening['limit_sisa']
        limit_sisa_level_ini = jenis_rekening[level]['limit_sisa']
        assert level == 3
        assert terakhir_ubah is None
        assert limit_sisa == limit_sisa_level_ini

        with pytest.raises(NikTidakSesuai) as info_error:
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=target_level)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']

        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        assert limit_sisa_sesudah == limit_sisa_level_ini
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert "NIK ini tidak" in str(info_error.value)



    def test_turunkan_rekening_dengan_norek_salah(self, koneksi_test, siapkan_rekening_siap_diturunkan):

        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = "999900"
        norek_asli = siapkan_rekening_siap_diturunkan['norek']

        target_level = 2

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek_asli,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sisa = data_rekening['limit_sisa']
        limit_sisa_level_ini = jenis_rekening[level]['limit_sisa']
        assert level == 3
        assert terakhir_ubah is None
        assert limit_sisa == limit_sisa_level_ini


        with pytest.raises(RekeningTidakDitemukan) as info_error:
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=target_level)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek_asli,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']

        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        assert limit_sisa_sesudah == limit_sisa_level_ini
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert "tidak terdaftar" in str(info_error.value)



    @pytest.mark.parametrize("status_invalid",['blokir','tutup'])
    def test_turunkan_rekening_dengan_status_rekening_tidak_valid(self, koneksi_test, siapkan_rekening_siap_diturunkan,status_invalid):

        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = siapkan_rekening_siap_diturunkan['norek']

        koneksi_test.execute("UPDATE rekening SET status = ? WHERE norek = ?",(status_invalid, norek))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sisa = data_rekening['limit_sisa']
        limit_sisa_level_ini = jenis_rekening[level]['limit_sisa']
        target_level = level - 1
        assert level == 3
        assert terakhir_ubah is None
        assert limit_sisa == limit_sisa_level_ini


        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=target_level)


        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']
        status = data_rekening_sesudah['status']

        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        assert limit_sisa_sesudah == limit_sisa_level_ini
        assert level_sesudah == level
        assert status == status_invalid
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert "Rekening Anda saat ini sedang" in str(info_error.value)


    def test_turunkan_rekening_lebih_dari_sekali_sehari(self, koneksi_test, siapkan_rekening_siap_diturunkan):
        nik = siapkan_rekening_siap_diturunkan["nik"]
        norek = siapkan_rekening_siap_diturunkan["norek"]
        target_level = 2

        hari_ini = datetime.date.today()

        koneksi_test.execute(
            "UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",
            (hari_ini.isoformat(), norek),
        )
        koneksi_test.commit()

        data_rekening = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()
        level = data_rekening["level"]
        terakhir_ubah = konversi_waktu(data_rekening["terakhir_ubah_rekening"])
        limit_sisa_sebelum = data_rekening["limit_sisa"]
        limit_sisa_level_ini = jenis_rekening[level]['limit_sisa']

        assert level == 3
        assert terakhir_ubah == hari_ini
        assert limit_sisa_sebelum == limit_sisa_level_ini


        with pytest.raises(StatusTidakValid) as info_error:
            RekeningService.downgrade_rekening(
                nik=nik, norek=norek, target_level=target_level
            )

        data_rekening_sesudah = koneksi_test.execute(
            "SELECT * FROM rekening WHERE norek = ?", (norek,)
        ).fetchone()

        level_sesudah = data_rekening_sesudah["level"]
        terakhir_ubah_sesudah = konversi_waktu(
            data_rekening_sesudah["terakhir_ubah_rekening"]
        )
        limit_sisa_sesudah = data_rekening_sesudah["limit_sisa"]

        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert limit_sisa_sebelum == limit_sisa_sesudah
        assert "rekening hanya bisa dilakukan 1 kali" in str(info_error.value)

    @pytest.mark.parametrize("level_sekarang, level_tujuan, exception, pesan_error",[(1, 1,StatusTidakValid, "ini sudah level terendah")
                                                             ,(3,3,LevelRekeningTidakValid, "harus lebih rendah dari level saat ini"),
                                                             (3,4,LevelRekeningTidakValid, "harus lebih rendah dari level saat ini"),
                                                                                     (1,2, StatusTidakValid,"ini sudah level terendah")])
    def test_turunkan_rekening_dengan_pilihan_tidak_valid(self, koneksi_test, siapkan_rekening_siap_diturunkan,level_sekarang,level_tujuan,exception,pesan_error):


        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = siapkan_rekening_siap_diturunkan['norek']

        koneksi_test.execute("UPDATE rekening SET level = ? WHERE norek = ?",(level_sekarang,norek))
        koneksi_test.commit()

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level = data_rekening['level']
        terakhir_ubah = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        limit_sisa = data_rekening['limit_sisa']


        assert level == level_sekarang
        assert terakhir_ubah is None


        with pytest.raises(exception) as info_error:
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=level_tujuan)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?", (norek,)).fetchone()

        level_sesudah = data_rekening_sesudah['level']
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']

        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        assert limit_sisa_sesudah == limit_sisa
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah
        assert pesan_error in str(info_error.value)

    def test_race_condition_penurunan_rekening(self, koneksi_test, siapkan_rekening_siap_diturunkan, monkeypatch):

        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = siapkan_rekening_siap_diturunkan['norek']

        kemarin = datetime.date.today() - datetime.timedelta(days=1)

        method_asli = rekening_repo_module.RekeningRepository.ubah_state_setelah_upgrade_atau_downgrade

        def uji_race_condition(**kwargs):

            koneksi_test.execute("UPDATE rekening SET terakhir_ubah_rekening = ? WHERE norek = ?",(kemarin.isoformat(), norek))
            koneksi_test.commit()

            return method_asli(**kwargs)


        monkeypatch.setattr(rekening_repo_module.RekeningRepository,"ubah_state_setelah_upgrade_atau_downgrade",uji_race_condition)
        data_rekening = koneksi_test.execute('SELECT * FROM rekening WHERE norek = ?',(norek,)).fetchone()
        level = data_rekening['level']
        limit_sisa = data_rekening['limit_sisa']
        terakhir_ubah_sebelum = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        target_level = level - 1


        assert level == 3
        assert terakhir_ubah_sebelum is None

        with pytest.raises(PerbaruiStatusGagal) as info_error:
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=target_level)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']
        level_sesudah = data_rekening_sesudah['level']
        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penurunan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'penurunan_level_rekening'",(norek,)).fetchone()

        assert riwayat is None
        assert audit is None
        assert limit_sisa_sesudah == limit_sisa
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == kemarin
        assert "melakukan penurunan rekening" in str(info_error.value)



    def test_rollback_penurunan_rekening(self, koneksi_test, siapkan_rekening_siap_diturunkan, monkeypatch):

        nik = siapkan_rekening_siap_diturunkan['nik']
        norek = siapkan_rekening_siap_diturunkan['norek']

        method_asli = audit_repo_module.AuditRepository.tambah_audit


        def uji_rollback(**kwargs):
            method_asli(**kwargs)
            raise RuntimeError("Simulasi rollaback penurunan rekening")

        monkeypatch.setattr(audit_repo_module.AuditRepository, "tambah_audit",uji_rollback)

        data_rekening = koneksi_test.execute('SELECT * FROM rekening WHERE norek = ?',(norek,)).fetchone()
        level = data_rekening['level']
        limit_sisa = data_rekening['limit_sisa']
        terakhir_ubah_sebelum = konversi_waktu(data_rekening['terakhir_ubah_rekening'])
        target_level = level - 1


        assert level == 3

        assert terakhir_ubah_sebelum is None

        with pytest.raises(RuntimeError,match="Simulasi rollaback penurunan rekening"):
            RekeningService.downgrade_rekening(nik=nik, norek=norek, target_level=target_level)

        data_rekening_sesudah = koneksi_test.execute("SELECT * FROM rekening WHERE norek = ?",(norek,)).fetchone()
        limit_sisa_sesudah = data_rekening_sesudah['limit_sisa']
        level_sesudah = data_rekening_sesudah['level']
        terakhir_ubah_sesudah = konversi_waktu(data_rekening_sesudah['terakhir_ubah_rekening'])

        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'penurunan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'penurunan_level_rekening'",(norek,)).fetchone()

        assert riwayat is None
        assert audit is None
        assert limit_sisa_sesudah == limit_sisa
        assert level_sesudah == level
        assert terakhir_ubah_sesudah == terakhir_ubah_sebelum




class TestBukaRekening:

    @pytest.fixture
    def siapkan_data_nasabah(self, koneksi_test):
        koneksi_test.execute("INSERT INTO nasabah (nama, alamat, nik) VALUES (?,?,?)",("Nasabah Pengujian","Jln.thmarin","1111222233334444"))
        koneksi_test.commit()

        return {"nik":"1111222233334444"}


    def test_buka_rekening_happy_path(self, koneksi_test, siapkan_data_nasabah):

        nik = siapkan_data_nasabah['nik']
        level_rekening = 3
        setor_awal = 100_000_000
        pin = "123456"

        limit_sisa_level_ini = jenis_rekening[level_rekening]['limit_sisa']

        RekeningService.buka_rekening(nik=nik,pilihan=level_rekening,pin=pin, setor_awal=setor_awal)

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE nik_pemilik = ?",(nik,)).fetchone()
        assert data_rekening is not None

        level = data_rekening['level']
        waktu_dibuat = datetime.datetime.fromisoformat(data_rekening['waktu_dibuat'])
        saldo = data_rekening['saldo']
        norek = data_rekening['norek']
        pin_rekening = data_rekening['pin']
        waktu_bayar_admin = konversi_waktu(data_rekening['waktu_bayar_admin'])
        waktu_dapat_bunga = konversi_waktu(data_rekening['dapat_bunga'])
        reset = konversi_waktu(data_rekening['reset'])
        status = data_rekening['status']
        limit_sisa = data_rekening['limit_sisa']


        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pembukaan_rekening'",(norek,)).fetchone()
        riwayat_setor = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal'",(norek,)).fetchone()

        assert riwayat is not None
        assert riwayat_setor is not None
        assert audit is not None
        assert waktu_dibuat is not None
        assert level == level_rekening
        assert saldo == setor_awal
        assert status == 'aktif'
        assert pin_rekening == pin
        assert limit_sisa == limit_sisa_level_ini
        assert reset == datetime.date.today()
        assert waktu_bayar_admin == datetime.date.today()
        assert waktu_dapat_bunga == datetime.date.today()


    @pytest.mark.parametrize("kwargs_salah, pesan_error",[({'nik':'1234a'},"NIK tidak bolah"),
                                                          ({'pilihan':0}," harus di antara 1 - 4"),
                                                          ({'pilihan':5},"tidak tersedia"),
                                                          ({'pin':"1234"},"berupa 6 digit"),
                                                          ({'pin':'abc'},'berupa 6 digit'),
                                                          ({'setor_awal':'abc'},"berupa berupa angka")
                                                          ])
    def test_buka_rekening_dengan_input_tidak_valid(self, koneksi_test, siapkan_data_nasabah, kwargs_salah, pesan_error):

        nik = siapkan_data_nasabah['nik']
        pilihan_level = 3
        setor_awal = 100_000_000
        pin = '123456'

        kwargs = {'nik':nik,
                  'pilihan':pilihan_level,
                  'pin':pin,
                  'setor_awal':setor_awal,
                  'koneksi':koneksi_test
                  }

        kwargs.update(kwargs_salah)

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.buka_rekening(**kwargs)

        rekening = koneksi_test.execute("SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",(nik,)).fetchone()[0]

        assert rekening == 0
        assert pesan_error in str(info_error.value)


    def test_buka_rekening_dengan_nik_salah(self, koneksi_test, siapkan_data_nasabah):


        nik_asli = siapkan_data_nasabah['nik']
        nik = '123'
        pilihan_level = 3
        setor_awal = 100_000_000
        pin = '123456'

        with pytest.raises(NasabahTidakDitemukan) as info_error:
            RekeningService.buka_rekening(nik=nik,pilihan=pilihan_level,pin=pin,setor_awal=setor_awal,koneksi=koneksi_test)

        rekening = koneksi_test.execute("SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",(nik_asli,)).fetchone()[0]

        assert rekening == 0
        assert 'tidak terdaftar' in str(info_error.value)


    @pytest.mark.parametrize("level_rekening",[1,2,3,4])
    def test_buka_rekening_dengan_setor_awal_tidak_memenuhi(self, koneksi_test, siapkan_data_nasabah,level_rekening):

        nik = siapkan_data_nasabah['nik']
        setor_awal = jenis_rekening[level_rekening]['minimal_setor'] - 1
        pin = '123456'

        punya_rekening = koneksi_test.execute("SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",(nik,)).fetchone()[0]
        assert punya_rekening == 0

        with pytest.raises(InputTidakValid) as info_error:
            RekeningService.buka_rekening(nik=nik,pilihan=level_rekening,pin=pin, setor_awal=setor_awal,koneksi=koneksi_test)


        rekening = koneksi_test.execute("SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",(nik,)).fetchone()[0]
        riwayat = koneksi_test.execute("SELECT COUNT(*) FROM riwayat WHERE jenis = 'pembukaan rekening'").fetchone()[0]
        riwayat_setor = koneksi_test.execute("SELECT COUNT(*) FROM riwayat WHERE jenis = 'setor awal'").fetchone()[0]
        audit = koneksi_test.execute("SELECT COUNT(*) FROM audit WHERE aksi = 'pembukaan_rekening' AND nik = ?",(nik,)).fetchone()[0]

        assert rekening == 0
        assert riwayat == 0
        assert riwayat_setor == 0
        assert audit == 0
        assert "saldo minimal setoran awal" in str(info_error.value)


    @pytest.mark.parametrize("level_rekening",[1,2,3,4])
    def test_buka_rekening_dengan_setor_awal_tepat_memenuhi_persyaratan(self, koneksi_test, siapkan_data_nasabah, level_rekening):

        nik = siapkan_data_nasabah['nik']
        setor_awal = jenis_rekening[level_rekening]['minimal_setor']
        pin = '123456'
        limit_sisa_level_ini = jenis_rekening[level_rekening]['limit_sisa']
        punya_rekening = koneksi_test.execute("SELECT COUNT(*) FROM rekening WHERE nik_pemilik = ?",(nik,)).fetchone()[0]

        assert punya_rekening == 0


        RekeningService.buka_rekening(nik=nik,pilihan=level_rekening,pin=pin, setor_awal=setor_awal)

        data_rekening = koneksi_test.execute("SELECT * FROM rekening WHERE nik_pemilik = ?",(nik,)).fetchone()
        assert data_rekening is not None

        level = data_rekening['level']
        waktu_dibuat = datetime.datetime.fromisoformat(data_rekening['waktu_dibuat'])
        saldo = data_rekening['saldo']
        norek = data_rekening['norek']
        pin_rekening = data_rekening['pin']
        waktu_bayar_admin = konversi_waktu(data_rekening['waktu_bayar_admin'])
        waktu_dapat_bunga = konversi_waktu(data_rekening['dapat_bunga'])
        reset = konversi_waktu(data_rekening['reset'])
        status = data_rekening['status']
        limit_sisa = data_rekening['limit_sisa']


        riwayat = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'pembukaan rekening'",(norek,)).fetchone()
        audit = koneksi_test.execute("SELECT * FROM audit WHERE norek = ? AND aksi = 'pembukaan_rekening'",(norek,)).fetchone()
        riwayat_setor = koneksi_test.execute("SELECT * FROM riwayat WHERE norek = ? AND jenis = 'setor awal'",(norek,)).fetchone()

        assert riwayat is not None
        assert riwayat_setor is not None
        assert audit is not None
        assert waktu_dibuat is not None
        assert level == level_rekening
        assert saldo == setor_awal
        assert status == 'aktif'
        assert pin_rekening == pin
        assert limit_sisa == limit_sisa_level_ini
        assert reset == datetime.date.today()
        assert waktu_bayar_admin == datetime.date.today()
        assert waktu_dapat_bunga == datetime.date.today()


