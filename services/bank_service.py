from bank_djago.utils.utililty import JenisReferensiID

class BankService:

    @staticmethod
    def cek_integritas_rekening(bank):
        error = []

        # 1. Setiap rekening harus punya pemilik
        for norek, rekening in bank.rekening_index.items():
            if rekening.pemilik is None:
                error.append(
                    f"Rekening {norek} tidak memiliki pemilik."
                )

        # 2. Setiap rekening milik nasabah harus ada di rekening_index
        # 3. Setiap rekening hanya boleh dimiliki satu nasabah
        pemilik_rekening = {}

        for nik, nasabah in bank.data_nasabah.items():
            for rekening in nasabah.rekening:
                norek = rekening.norek

                if norek not in bank.rekening_index:
                    error.append(
                        f"Rekening {norek} milik nasabah {nik} "
                        f"tidak ditemukan di rekening_index."
                    )

                if norek in pemilik_rekening:
                    error.append(
                        f"Rekening {norek} dimiliki lebih dari satu nasabah: "
                        f"{pemilik_rekening[norek]} dan {nik}."
                    )
                else:
                    pemilik_rekening[norek] = nik

                # 4. Pemilik pada objek rekening harus sesuai
                if rekening.pemilik is not nasabah:
                    pemilik = (
                        rekening.pemilik.NIK
                        if rekening.pemilik is not None
                        else "None"
                    )

                    error.append(
                        f"Rekening {norek}: "
                        f"pemilik pada objek = {pemilik}, "
                        f"tetapi tercantum pada nasabah = {nik}."
                    )

        return error

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

    @staticmethod
    def cek_integritas_pinjaman(bank):
        error = []
        pemilik_pinjaman = {}

        for pinjaman in bank.daftar_pinjaman:

            # 1. Pemilik harus ada
            if pinjaman.pemilik is None:
                error.append(
                    f"Pinjaman {pinjaman.ID} tidak memiliki pemilik."
                )
                continue

            nasabah = pinjaman.pemilik
            nik = nasabah.NIK

            # 2. NIK pemilik harus terdaftar di bank
            if nik not in bank.data_nasabah:
                error.append(
                    f"Pinjaman {pinjaman.ID} memiliki pemilik "
                    f"dengan NIK {nik} yang tidak terdaftar."
                )

            # 3. Pemilik pinjaman harus menunjuk ke nasabah yang benar
            if bank.data_nasabah.get(nik) is not nasabah:
                error.append(
                    f"Pinjaman {pinjaman.ID} menunjuk ke objek "
                    f"nasabah yang tidak sesuai dengan NIK {nik}."
                )

            # 4. Satu nasabah hanya punya satu pinjaman
            if nik in pemilik_pinjaman:
                error.append(
                    f"Nasabah {nik} memiliki lebih dari satu pinjaman: "
                    f"{pemilik_pinjaman[nik]} dan {pinjaman.ID}."
                )
            else:
                pemilik_pinjaman[nik] = pinjaman.ID

            # 5. Rekening harus ada
            if pinjaman.rekening is None:
                error.append(
                    f"Pinjaman {pinjaman.ID} tidak memiliki rekening."
                )
                continue

            norek = pinjaman.rekening.norek

            # 6. Rekening harus ada di index
            if norek not in bank.rekening_index:
                error.append(
                    f"Pinjaman {pinjaman.ID} menggunakan rekening "
                    f"{norek} yang tidak ditemukan."
                )

            # 7. Rekening harus dimiliki nasabah yang sama
            if pinjaman.rekening.pemilik is not nasabah:
                pemilik_rekening = (
                    pinjaman.rekening.pemilik.NIK
                    if pinjaman.rekening.pemilik is not None
                    else "None"
                )

                error.append(
                    f"Pinjaman {pinjaman.ID} milik nasabah {nik} "
                    f"menggunakan rekening {norek} yang dimiliki "
                    f"oleh {pemilik_rekening}."
                )

        return error

    @staticmethod
    def cek_integritas_notifikasi(bank):
        error = []

        for nik, nasabah in bank.data_nasabah.items():

            for notifikasi in nasabah.notifikasi:

                referensi = notifikasi.referensi_id
                id_objek = notifikasi.id_objek

                # Notifikasi umum tidak wajib memiliki objek
                if referensi is None:
                    if id_objek is not None:
                        error.append(
                            f"Notifikasi umum milik nasabah {nik} "
                            f"memiliki id_objek={id_objek}."
                        )
                    continue

                # =========================
                # NOTIFIKASI DEPOSITO
                # =========================
                if referensi == JenisReferensiID.DEPOSITO:

                    if id_objek is None:
                        error.append(
                            f"Notifikasi deposito milik nasabah {nik} "
                            f"tidak memiliki id_objek."
                        )
                        continue

                    deposito_ditemukan = any(
                        deposito.ID == id_objek
                        for deposito in nasabah.deposito
                    )

                    if not deposito_ditemukan:
                        error.append(
                            f"Notifikasi deposito milik nasabah {nik} "
                            f"menunjuk ke deposito ID {id_objek} "
                            f"yang tidak ditemukan pada nasabah tersebut."
                        )

                # =========================
                # NOTIFIKASI PINJAMAN
                # =========================
                elif referensi == JenisReferensiID.PINJAMAN:

                    if id_objek is None:
                        continue

                    pinjaman_ditemukan = any(
                        pinjaman.ID == id_objek
                        and pinjaman.pemilik is nasabah
                        for pinjaman in bank.daftar_pinjaman
                    )

                    if not pinjaman_ditemukan:
                        error.append(
                            f"Notifikasi pinjaman milik nasabah {nik} "
                            f"menunjuk ke pinjaman ID {id_objek} "
                            f"yang tidak ditemukan atau bukan milik nasabah tersebut."
                        )

                # =========================
                # REFERENSI YANG BELUM DIKENAL
                # =========================
                else:
                    error.append(
                        f"Notifikasi milik nasabah {nik} "
                        f"memiliki referensi tidak dikenal: {referensi}."
                    )

        return error