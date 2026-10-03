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
    LevelRekeningTidakValid, PerbaruiStatusGagal,
)

import bank_djago.penyimpanan.repositories.audit_repository as audit_repo_module
import bank_djago.penyimpanan.repositories.rekening_repository as rekening_repo_module

jenis_rekening = {
    1: {
        "minimal_upgrade": 0,
        "limit_sisa" :5_000_000
    },
    2: {
        "minimal_upgrade": 3_000_000,
        "limit_sisa" : 15_000_000
    },
    3: {
        "minimal_upgrade": 50_000_000,
        "limit_sisa" : 200_000_000
    },
    4: {
        "minimal_upgrade": 200_000_000,
        "limit_sisa" : None
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
        "level_sekarang, level_peningkatan", [(1, 1), (3, 2), (4, 3)]
    )
    def test_tingkatkan_rekening_dengan_pilihan_level_tidak_valid(
        self,
        koneksi_test,
        siapkan_data_rekening_dan_nasabah,
        level_sekarang,
        level_peningkatan,
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

        with pytest.raises(LevelRekeningTidakValid) as info_error:
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
        assert " harus lebih tinggi dari level saat ini" in str(info_error.value)


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









