class BankException(Exception):
    pass


class DataTidakDitemukan(BankException):
    pass


class PinjamanTidakDitemukan(DataTidakDitemukan):
    pass


class NasabahTidakDitemukan(DataTidakDitemukan):
    pass


class DepositoTidakDitemukan(DataTidakDitemukan):
    pass


class RekeningTidakDitemukan(DataTidakDitemukan):
    pass


class PengajuanTidakDitemukan(DataTidakDitemukan):
    pass


# -------------------------------------------------------------------


class KondisiTidakValid(BankException):
    pass


class StatusTidakValid(KondisiTidakValid):
    pass


class LevelRekeningTidakValid(KondisiTidakValid):
    pass


class InputTidakValid(KondisiTidakValid):
    pass


class JenisAroTidakValid(KondisiTidakValid):
    pass


# ---------------------------------------------------------------------


class OperasiGagal(BankException):
    pass


class PenguranganSaldoGagal(OperasiGagal):
    pass


class PenambahanSaldoGagal(OperasiGagal):
    pass


class PerbaruiStatusGagal(OperasiGagal):
    pass


# -----------------------------------------------------------------------------------


class TidakBerwenang(BankException):
    pass


class NikTidakSesuai(TidakBerwenang):
    pass


class RekeningTidakSesuai(TidakBerwenang):
    pass
