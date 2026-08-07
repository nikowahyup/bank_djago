import time

from bank_djago.utils.utililty import Utilitas
from bank_djago.services.transaksi.limit import LimitService

class TransaksiService:

    @staticmethod
    def cek_saldo(nasabah):
        nasabah.cek_saldo()

    @staticmethod
    def animasi():
        print("Proses", end="")
        for _ in range(3):
            print(".", end="", flush=True)
            time.sleep(1)
        print()

    @staticmethod
    def setor_tunai(rekening,nominal):
        if nominal < 10000:
            raise ValueError("Minimal setor adalah Rp10.0000")
        rekening.tambah_saldo(nominal)



    @staticmethod
    def tarik_tunai(rekening,nominal):
        if nominal < 10000:
            raise ValueError("Minimal tari adalah Rp10.000")
        if rekening.saldo - nominal < rekening.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika Anda menarik sebesar Rp{Utilitas.format_rupiah(nominal)}")
        rekening.kurangi_saldo(nominal)

    @staticmethod
    def transfer(pengirim,penerima,nominal):
        if nominal < 10000:
            raise ValueError("Minimal transfer adalah Rp10.0000")
        LimitService.reset_limit(pengirim)
        total = nominal + pengirim.pajak
        if pengirim.limit_harian is not None:
            if pengirim.limit_sisa < nominal:
                raise ValueError("Limit harian telah tercapai")

        if pengirim.saldo - total < pengirim.saldosetor_min:
            raise ValueError(f"Saldo tidak memenuhi saldo minimum jika transfer Rp{Utilitas.format_rupiah(nominal)}")

        pengirim.kurangi_saldo(total)
        penerima.tambah_saldo(nominal)

        if pengirim.limit_harian is not None:
            pengirim.limit_sisa -= nominal

