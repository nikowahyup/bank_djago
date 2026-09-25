import datetime


from bank_djago.utils.utility import Utilitas
from bank_djago.utils.utility import StatusPinjaman


# blueprint untuk pinjaman
class Pinjaman:

    BATAS_HARI_TUNGGAKAN = 7
    PERSENTASE_DENDA_HARIAN = 0.001
    MAKSIMAL_PERSENTASE_DENDA = 0.1

    def __init__(self, pemilik, rekening, nominal_pinjaman, bunga, tenor, id=None):
        self.ID = id
        self.pemilik = pemilik
        self.rekening = rekening
        self.nominal_pinjaman = nominal_pinjaman
        self.bunga = bunga
        self.tenor = tenor
        self.sisa_pokok = 0
        self.cicilan_tetap = 0
        self.cicilan_terbayar = 0
        self.status = StatusPinjaman.DIAJUKAN
        self.tanggal_pencairan = None
        self.tanggal_jatuh_tempo = None

    def ke_dict(self):
        return {
            "ID": self.ID,
            "nik": self.pemilik.NIK,
            "rekening": self.rekening.norek,
            "nominal_pinjaman": self.nominal_pinjaman,
            "bunga": self.bunga,
            "tenor": self.tenor,
            "cicilan_tetap": self.cicilan_tetap,
            "sisa_pokok": self.sisa_pokok,
            "cicilan_terbayar": self.cicilan_terbayar,
            "status": self.status.value,
            "tanggal_pencairan": (
                self.tanggal_pencairan.isoformat() if self.tanggal_pencairan else None
            ),
            "jatuh_tempo": (
                self.tanggal_jatuh_tempo.isoformat()
                if self.tanggal_jatuh_tempo
                else None
            ),
        }

    def tanggal_boleh_bayar(self):
        if self.cicilan_terbayar == 0:
            return self.tanggal_pencairan

        jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
            tanggal=self.tanggal_pencairan, bulan=1
        )

        for _ in range(self.cicilan_terbayar - 1):
            jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
                tanggal=jatuh_tempo_sebelumnya, bulan=1
            )

        return jatuh_tempo_sebelumnya + datetime.timedelta(days=1)

    def hitung_hari_terlambat(self, hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        return max(0, (hari_ini - self.tanggal_jatuh_tempo).days)

    def hitung_denda(self, hari_ini=None):
        hari_terlambat = self.hitung_hari_terlambat(hari_ini)
        hari_denda = max(0, hari_terlambat - self.BATAS_HARI_TUNGGAKAN)

        denda = self.cicilan_tetap * hari_denda * self.PERSENTASE_DENDA_HARIAN

        denda_maksimal = self.cicilan_tetap * self.MAKSIMAL_PERSENTASE_DENDA

        return round(min(denda, denda_maksimal))
