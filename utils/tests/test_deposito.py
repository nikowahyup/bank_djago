@staticmethod
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


-----------------------------------------------------------------------------------------