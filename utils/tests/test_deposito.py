
def cek_integritas_deposito(bank):
    error = []

    for nik, nasabah in bank.data_nasabah.items():

        id_deposito = set()

        for deposito in nasabah.deposito:

            # 1. Deposito harus punya pemilik
            if deposito.pemilik is None:
                error.append(
                    f"Deposito {deposito.ID} tidak memiliki pemilik."
                )

            # 2. Pemilik harus sesuai dengan nasabah
            elif deposito.pemilik is not nasabah:
                error.append(
                    f"Deposito {deposito.ID} milik {nik} "
                    f"tetapi deposito.pemilik menunjuk ke "
                    f"{deposito.pemilik.NIK}."
                )

            # 3. ID harus unik dalam satu nasabah
            if deposito.ID in id_deposito:
                error.append(
                    f"Nasabah {nik} memiliki ID deposito "
                    f"duplikat: {deposito.ID}."
                )
            else:
                id_deposito.add(deposito.ID)

            # 4. Rekening harus ada
            if deposito.rekening is None:
                error.append(
                    f"Deposito {deposito.ID} tidak memiliki rekening."
                )
            else:
                if deposito.rekening.norek not in bank.rekening_index:
                    error.append(
                        f"Deposito {deposito.ID} menggunakan rekening "
                        f"{deposito.rekening.norek} yang tidak ditemukan."
                    )

                # 5. Rekening harus punya pemilik yang benar
                if deposito.rekening.pemilik is not nasabah:
                    pemilik = (
                        deposito.rekening.pemilik.NIK
                        if deposito.rekening.pemilik
                        else "None"
                    )

                    error.append(
                        f"Deposito {deposito.ID} milik {nik} "
                        f"menggunakan rekening {deposito.rekening.norek} "
                        f"yang pemiliknya adalah {pemilik}."
                    )

    return error


# -----------------------------------------------------------------------------------------


def uji_serialisasi_integer_deposito(bank):
    jumlah_diperiksa = 0
    nik_sudah_diperiksa = set()

    for rekening in bank.rekening_index.values():
        nasabah = rekening.pemilik

        # Satu nasabah mungkin memiliki beberapa rekening.
        # Pemeriksaan cukup dilakukan sekali untuk setiap nasabah.
        if nasabah.NIK in nik_sudah_diperiksa:
            continue

        nik_sudah_diperiksa.add(nasabah.NIK)

        for deposito in nasabah.deposito:
            # Membentuk dictionary yang nantinya disimpan ke JSON.
            data_deposito = deposito.ke_dict()
            nominal = data_deposito["nominal"]

            print(
                f"Deposito {deposito.ID} milik {nasabah.NIK} | "
                f"Nominal: {nominal} | "
                f"Tipe: {type(nominal)}"
            )

            assert isinstance(nominal, int), (
                f"Nominal deposito {deposito.ID} "
                f"milik {nasabah.NIK} belum berupa integer"
            )

            jumlah_diperiksa += 1

    assert jumlah_diperiksa > 0, (
        "Tidak ada deposito yang dapat diperiksa"
    )

    print()
    print(
        f"✅ {jumlah_diperiksa} deposito siap disimpan "
        f"dengan nominal berupa integer"
    )


    # -----------------------------------------------------------------------------

from bank_djago.utils.utility import Utilitas
from bank_djago.services.deposito.deposito_service import DepositoService, StatusDeposito
from bank_djago.penyimpanan.storage import JsonStorage

import datetime

def uji_integer_aro_pokok_bunga(bank):
    # Mencari deposito ARO pokok+bunga yang masih aktif.
    nasabah = bank.data_nasabah["3510152602082002"]
    deposito = nasabah.deposito[1]

    assert deposito is not None, (
        "Deposito ARO pokok+bunga yang aktif tidak ditemukan"
    )

    # Menyimpan keadaan awal sebagai pembanding.
    nominal_awal = deposito.nominal
    total_pencairan = deposito.total_pencairan
    saldo_awal = deposito.rekening.saldo
    jatuh_tempo_awal = deposito.jatuh_tempo
    lama_aro = deposito.lama_aro

    print("SEBELUM PERPANJANGAN")
    print("ID deposito       :", deposito.ID)
    print("Nominal awal      :", nominal_awal)
    print("Total pencairan   :", total_pencairan)
    print("Saldo rekening    :", saldo_awal)
    print("Jatuh tempo awal  :", jatuh_tempo_awal)
    print("Lama ARO          :", lama_aro)

    assert isinstance(nominal_awal, int), (
        "Nominal awal deposito belum berupa integer"
    )

    assert isinstance(total_pencairan, int), (
        "Total pencairan belum berupa integer"
    )

    # Memajukan deposito ke hari jatuh tempo agar dapat diperpanjang.
    deposito.jatuh_tempo = datetime.date.today()

    jatuh_tempo_simulasi = deposito.jatuh_tempo
    jatuh_tempo_yang_diharapkan = Utilitas.tambah_bulan(
        jatuh_tempo_simulasi,
        lama_aro
    )

    DepositoService.perpanjangan(bank, deposito)

    print()
    print("SETELAH PERPANJANGAN")
    print("Nominal baru      :", deposito.nominal)
    print("Jenis nominal     :", type(deposito.nominal))
    print("Saldo rekening    :", deposito.rekening.saldo)
    print("Jatuh tempo baru  :", deposito.jatuh_tempo)
    print("Status deposito   :", deposito.status)

    # Seluruh pokok dan bunga harus menjadi nominal periode berikutnya.
    assert deposito.nominal == total_pencairan, (
        "Nominal baru tidak sama dengan total pencairan sebelumnya"
    )

    assert isinstance(deposito.nominal, int), (
        "Nominal baru ARO pokok+bunga belum berupa integer"
    )

    # ARO pokok+bunga memasukkan total ke rekening lalu menariknya kembali.
    assert deposito.rekening.saldo == saldo_awal, (
        "Saldo rekening berubah pada ARO pokok+bunga"
    )

    assert deposito.jatuh_tempo == jatuh_tempo_yang_diharapkan, (
        "Jatuh tempo baru tidak sesuai dengan lama ARO"
    )

    assert deposito.status == StatusDeposito.AKTIF, (
        "Deposito tidak kembali berstatus aktif"
    )

    print()
    print("✅ ARO pokok+bunga berhasil diperpanjang")
    print("✅ Nominal baru sudah berupa integer")
    print("✅ Saldo rekening tetap konsisten")

bank = JsonStorage.muat_bank()

if __name__=="__main__":
    uji_integer_aro_pokok_bunga(bank)

# -----------------------------------------------------------------------------




# ---------------------------------------------------------------------------------







