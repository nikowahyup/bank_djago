import pytest, datetime

from bank_djago.services.deposito.deposito_service import DepositoService, StatusDeposito
from bank_djago.utils.utility import JenisAro
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.deposito_repository import DepositoRepository
from bank_djago.services.scheduler import Scheduler
from bank_djago.services.exceptions import StatusTidakValid





class TestAroPokok:

    @pytest.fixture
    def deposito_siap_diperpanjang(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        koneksi_test.execute(
            """INSERT INTO deposito(id, norek, nominal, bunga, lama_bulan, tanggal_buka, jatuh_tempo, status, jenis_aro, lama_aro) 
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                1_000_000,
                0.03,
                1,
                datetime.date.today().isoformat(),
                (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
                StatusDeposito.AKTIF,
                JenisAro.POKOK,
                1,
            ),
        )

        koneksi_test.commit()

        return {"id_deposito": 1}

    @staticmethod
    def _ambil_kondisi_deposito(koneksi, norek, id_deposito):
        deposito = koneksi.execute(
            "SELECT status FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()
        return {
            "deposito": tuple(deposito) if deposito else None,
            "saldo": RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi),
            "transaksi": koneksi.execute(
                "SELECT COUNT(*) FROM transaksi WHERE jenis_referensi = 'deposito' AND id_referensi = ?",
                (id_deposito,),
            ).fetchone()[0],
            "riwayat_aro": koneksi.execute(
                "SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'bunga deposito'",
                (norek,),
            ).fetchone()[0],
            'riwayat': koneksi.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'perpanjang deposito'",(norek,)).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'perpanjangan_deposito_aro'",
                (norek,),
            ).fetchone()[0],

        }

    @staticmethod
    def _kwargs_valid(koneksi):
        return {
            'koneksi':koneksi,
            'id_deposito':1,
            'hari_ini':(datetime.date.today() + datetime.timedelta(days=30))
        }

    def test_aro_pokok_happy_path(self, koneksi_test, deposito_siap_diperpanjang, siapkan_data_rekening_dan_nasabah):

        norek = siapkan_data_rekening_dan_nasabah["norek"]

        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        id_deposito = kwargs['id_deposito']
        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )


        jatuh_tempo_baru = DepositoService.perpanjangan(
                **kwargs
        )

        saldo_setelah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )
        tanggal_buka = (kwargs['hari_ini']).isoformat()
        jatuh_tempo = (kwargs['hari_ini'] + datetime.timedelta(days=31))
        assert jatuh_tempo_baru == jatuh_tempo
        assert saldo_setelah == saldo_sebelum + 2_500
        assert data_deposito["status"] == StatusDeposito.AKTIF
        assert data_deposito["nominal"] == 1_000_000
        assert data_deposito["tanggal_buka"] == tanggal_buka
        assert data_deposito['jatuh_tempo'] == jatuh_tempo.isoformat()



    def test_perpannjang_deposito_tapi_rekeningnya_tutup(
        self,
        koneksi_test,
        deposito_siap_diperpanjang,
        siapkan_data_rekening_dan_nasabah,
    ):

        norek = siapkan_data_rekening_dan_nasabah["norek"]

        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        id_deposito = kwargs['id_deposito']

        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)

        koneksi_test.execute(
            """UPDATE rekening SET status = 'tutup' WHERE norek = ?""",
            (norek,),
        )
        koneksi_test.commit()


        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                **kwargs
            )


        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        assert data_deposito["jatuh_tempo"] == kwargs['hari_ini'].isoformat()
        assert kondisi_sebelum == self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)
        print(f"pesan error : {info_error.value}")
        assert "tidak dapat diperpanjang" in str(info_error.value)


    @pytest.mark.parametrize(
        "kolom, nilai_baru,pesan_error",
        [
            ("status", "dicairkan", "tidak dapat diperpanjang"),
            ("jatuh_tempo", "2026-12-31", "belum jatuh tempo"),
        ],
    )

    def test_perpanjangan_aro_kondisi_tidak_valid(
        self,
        koneksi_test,
        deposito_siap_diperpanjang,
        kolom,
        nilai_baru,
        pesan_error,
        siapkan_data_rekening_dan_nasabah,
    ):

        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        id_deposito = kwargs['id_deposito']
        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)
        kondisi_sebelum.pop('deposito')

        koneksi_test.execute(
            f"UPDATE deposito SET {kolom} = ? WHERE id = ?",
            (nilai_baru, id_deposito),
        )
        koneksi_test.commit()

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                **kwargs
            )

        kondisi_sesudah = self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)
        kondisi_sesudah.pop('deposito')

        assert kondisi_sesudah == kondisi_sebelum
        assert pesan_error in str(info_error.value)



    def test_scheduler_memproses_aro_deposito(
        self, koneksi_test, deposito_siap_diperpanjang
    ):

        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        hari_ini = kwargs['hari_ini']
        Scheduler.jalankan(hari_ini)

        data_deposito = koneksi_test.execute(
            """SELECT * FROM deposito WHERE id = ?""",
            (deposito_siap_diperpanjang["id_deposito"],),
        ).fetchone()
        pesan = koneksi_test.execute(
            """SELECT pesan FROM notifikasi WHERE id_objek = ?""",
            (deposito_siap_diperpanjang["id_deposito"],),
        ).fetchone()


        jatuh_tempo = (hari_ini + datetime.timedelta(days=31)).isoformat()

        assert pesan is not None, "seharusnya ada pesan utuk jatuh tempo deposito ini"
        assert (
            data_deposito["status"] == StatusDeposito.AKTIF
        ), "seharusnya status deposito masih aktif"
        assert data_deposito["tanggal_buka"] == hari_ini.isoformat()
        assert data_deposito["jatuh_tempo"] == jatuh_tempo
        assert data_deposito["proses_aro"] == hari_ini.isoformat()
        assert data_deposito["nominal"] == 1_000_000



class TestAroPokokBunga:
    @pytest.fixture
    def deposito_pokok_bunga_siap_diperpanjang(
        self, koneksi_test, siapkan_data_rekening_dan_nasabah
    ):

        koneksi_test.execute(
            """INSERT INTO deposito(id, norek, nominal, bunga, lama_bulan, tanggal_buka, jatuh_tempo, status, jenis_aro, lama_aro) 
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                1,
                siapkan_data_rekening_dan_nasabah["norek"],
                1_000_000,
                0.03,
                1,
                datetime.date.today().isoformat(),
                (datetime.date.today() + datetime.timedelta(days=30)),
                StatusDeposito.AKTIF,
                JenisAro.POKOK_BUNGA,
                1,
            ),
        )

        koneksi_test.commit()

        return {"id_deposito": 1}

    @staticmethod
    def _ambil_kondisi_deposito(koneksi, norek, id_deposito):
        deposito = koneksi.execute(
            "SELECT status FROM deposito WHERE id = ?", (id_deposito,)
        ).fetchone()
        return {
            "deposito": tuple(deposito) if deposito else None,
            "saldo": RekeningRepository.ambil_saldo(norek=norek, koneksi=koneksi),
            "transaksi": koneksi.execute(
                "SELECT COUNT(*) FROM transaksi WHERE jenis_referensi = 'deposito' AND id_referensi = ?",
                (id_deposito,),
            ).fetchone()[0],
            'riwayat': koneksi.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'perpanjang deposito'",(norek,)).fetchone()[0],
            "audit": koneksi.execute(
                "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'perpanjangan_deposito_aro'",
                (norek,),
            ).fetchone()[0],

        }

    @staticmethod
    def _kwargs_valid(koneksi):
        return {
            'koneksi':koneksi,
            'id_deposito':1,
            'hari_ini':(datetime.date.today() + datetime.timedelta(days=30))
        }



    def test_perpanjang_aro_pokok_bunga_happy_path(self, koneksi_test, deposito_pokok_bunga_siap_diperpanjang, siapkan_data_rekening_dan_nasabah):
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        id_deposito = kwargs['id_deposito']
        saldo_sebelum = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )
        riwayat_sebelum =  koneksi_test.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'perpanjang deposito'",
                                   (norek,)).fetchone()[0]
        audit_sebelum =  koneksi_test.execute(
            "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'perpanjangan_deposito_aro'",
            (norek,),
        ).fetchone()[0]

        jatuh_tempo_baru = DepositoService.perpanjangan(
            **kwargs
        )

        saldo_setelah = RekeningRepository.ambil_saldo(
            norek=norek, koneksi=koneksi_test
        )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )
        riwayat =  koneksi_test.execute("SELECT COUNT(*) FROM riwayat WHERE norek = ? AND jenis = 'perpanjang deposito'",
                                   (norek,)).fetchone()[0]
        audit =  koneksi_test.execute(
            "SELECT COUNT(*) FROM audit WHERE norek = ? AND aksi = 'perpanjangan_deposito_aro'",
            (norek,),
        ).fetchone()[0]
        tanggal_buka = (kwargs['hari_ini']).isoformat()
        jatuh_tempo = (kwargs['hari_ini'] + datetime.timedelta(days=31))

        assert riwayat == riwayat_sebelum + 1
        assert audit == audit_sebelum + 1
        assert jatuh_tempo_baru == jatuh_tempo
        assert saldo_setelah == saldo_sebelum
        assert data_deposito["status"] == StatusDeposito.AKTIF
        assert data_deposito["nominal"] != 1_000_000
        assert data_deposito["tanggal_buka"] == tanggal_buka
        assert data_deposito['jatuh_tempo'] == jatuh_tempo.isoformat()



    def test_scheduler_memproses_aro_deposito(
        self, koneksi_test, deposito_pokok_bunga_siap_diperpanjang
    ):

        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        hari_ini = kwargs['hari_ini']
        Scheduler.jalankan(hari_ini)

        data_deposito = koneksi_test.execute(
            """SELECT * FROM deposito WHERE id = ?""",
            (deposito_pokok_bunga_siap_diperpanjang["id_deposito"],),
        ).fetchone()
        pesan = koneksi_test.execute(
            """SELECT pesan FROM notifikasi WHERE id_objek = ?""",
            (deposito_pokok_bunga_siap_diperpanjang["id_deposito"],),
        ).fetchone()


        jatuh_tempo = (hari_ini + datetime.timedelta(days=31)).isoformat()

        assert pesan is not None, "seharusnya ada pesan utuk jatuh tempo deposito ini"
        assert (
            data_deposito["status"] == StatusDeposito.AKTIF
        ), "seharusnya status deposito masih aktif"
        assert data_deposito["tanggal_buka"] == hari_ini.isoformat()
        assert data_deposito["jatuh_tempo"] == jatuh_tempo
        assert data_deposito["proses_aro"] == hari_ini.isoformat()
        assert data_deposito["nominal"] != 1_000_000

    def test_perpannjang_deposito_tapi_rekeningnya_tutup(
            self,
            koneksi_test,
            deposito_pokok_bunga_siap_diperpanjang,
            siapkan_data_rekening_dan_nasabah,
    ):
        norek = siapkan_data_rekening_dan_nasabah["norek"]

        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        id_deposito = kwargs['id_deposito']

        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)

        koneksi_test.execute(
            """UPDATE rekening SET status = 'tutup' WHERE norek = ?""",
            (norek,),
        )
        koneksi_test.commit()

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                **kwargs
            )

        data_deposito = DepositoRepository.cari_deposito_dengan_id(
            id_deposito=id_deposito, koneksi=koneksi_test
        )

        assert data_deposito["jatuh_tempo"] == kwargs['hari_ini'].isoformat()
        assert kondisi_sebelum == self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek,
                                                               id_deposito=id_deposito)
        print(f"pesan error : {info_error.value}")
        assert "tidak dapat diperpanjang" in str(info_error.value)



    @pytest.mark.parametrize(
        "kolom, nilai_baru,pesan_error",
        [
            ("status", "dicairkan", "tidak dapat diperpanjang"),
            ("jatuh_tempo", "2026-12-31", "belum jatuh tempo"),
        ],
    )

    def test_perpanjangan_aro_kondisi_tidak_valid(
        self,
        koneksi_test,
        deposito_pokok_bunga_siap_diperpanjang,
        kolom,
        nilai_baru,
        pesan_error,
        siapkan_data_rekening_dan_nasabah,
    ):

        norek = siapkan_data_rekening_dan_nasabah["norek"]
        kwargs = self._kwargs_valid(koneksi=koneksi_test)
        id_deposito = kwargs['id_deposito']
        kondisi_sebelum = self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)
        kondisi_sebelum.pop('deposito')

        koneksi_test.execute(
            f"UPDATE deposito SET {kolom} = ? WHERE id = ?",
            (nilai_baru, id_deposito),
        )
        koneksi_test.commit()

        with pytest.raises(StatusTidakValid) as info_error:
            DepositoService.perpanjangan(
                **kwargs
            )

        kondisi_sesudah = self._ambil_kondisi_deposito(koneksi=koneksi_test, norek=norek, id_deposito=id_deposito)
        kondisi_sesudah.pop('deposito')

        assert kondisi_sesudah == kondisi_sebelum
        assert pesan_error in str(info_error.value)




