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



from bank_djago.utils.utility import JenisReferensi

def cek_integritas_notifikasi(bank):
    error = []

    for nik, nasabah in bank.data_nasabah.items():

        for notifikasi in nasabah.notifikasi:

            referensi = notifikasi.jenis_referensi
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
            if referensi == JenisReferensi.DEPOSITO:

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
            elif referensi == JenisReferensi.PINJAMAN:

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



from bank_djago.utils.utility import StatusPinjaman

def cek_integritas_pinjaman(bank):
    error = []

    status_berjalan = (
        StatusPinjaman.DIAJUKAN,
        StatusPinjaman.DISETUJUI,
        StatusPinjaman.AKTIF
    )

    status_valid = (
        StatusPinjaman.DIAJUKAN,
        StatusPinjaman.DITOLAK,
        StatusPinjaman.DISETUJUI,
        StatusPinjaman.AKTIF,
        StatusPinjaman.LUNAS
    )

    pinjaman_berjalan_per_nik = {}

    for pinjaman in bank.daftar_pinjaman:
        # Pinjaman harus mempunyai pemilik.
        if pinjaman.pemilik is None:
            error.append(
                f"Pinjaman {pinjaman.ID} tidak memiliki pemilik."
            )
            continue

        nasabah = pinjaman.pemilik
        nik = nasabah.NIK

        # Pemilik harus terdaftar dalam bank.
        if nik not in bank.data_nasabah:
            error.append(
                f"Pinjaman {pinjaman.ID} memiliki pemilik "
                f"dengan NIK {nik} yang tidak terdaftar."
            )

        elif bank.data_nasabah[nik] is not nasabah:
            error.append(
                f"Pinjaman {pinjaman.ID} menunjuk objek nasabah "
                f"yang tidak sesuai dengan NIK {nik}."
            )

        # Status pinjaman harus dikenal sistem.
        if pinjaman.status not in status_valid:
            error.append(
                f"Pinjaman {pinjaman.ID} mempunyai "
                f"status tidak valid: {pinjaman.status}."
            )

        # Hanya pinjaman berjalan yang dibatasi satu per nasabah.
        if pinjaman.status in status_berjalan:
            if nik in pinjaman_berjalan_per_nik:
                pinjaman_sebelumnya = (
                    pinjaman_berjalan_per_nik[nik]
                )

                error.append(
                    f"Nasabah {nik} mempunyai lebih dari satu "
                    f"pinjaman berjalan: "
                    f"{pinjaman_sebelumnya.ID} dan {pinjaman.ID}."
                )
            else:
                pinjaman_berjalan_per_nik[nik] = pinjaman

        # Pinjaman harus mempunyai rekening.
        if pinjaman.rekening is None:
            error.append(
                f"Pinjaman {pinjaman.ID} tidak memiliki rekening."
            )
            continue

        rekening = pinjaman.rekening
        norek = rekening.norek

        # Rekening harus terdaftar dalam indeks bank.
        if norek not in bank.rekening_index:
            error.append(
                f"Pinjaman {pinjaman.ID} menggunakan rekening "
                f"{norek} yang tidak ditemukan."
            )

        else:
            # Harus menunjuk objek rekening resmi dalam indeks.
            if bank.rekening_index[norek] is not rekening:
                error.append(
                    f"Pinjaman {pinjaman.ID} masih menunjuk "
                    f"objek rekening lama."
                )

        # Rekening harus dimiliki nasabah yang sama.
        if rekening.pemilik is not nasabah:
            pemilik_rekening = (
                rekening.pemilik.NIK
                if rekening.pemilik is not None
                else "None"
            )

            error.append(
                f"Pinjaman {pinjaman.ID} milik nasabah {nik} "
                f"menggunakan rekening milik {pemilik_rekening}."
            )

    # Memastikan referensi pinjaman pada setiap nasabah sesuai.
    for nik, nasabah in bank.data_nasabah.items():
        pinjaman_berjalan = pinjaman_berjalan_per_nik.get(nik)

        if pinjaman_berjalan is None:
            if nasabah.pinjaman is not None:
                error.append(
                    f"Nasabah {nik} masih menunjuk pinjaman, "
                    f"padahal tidak ada pinjaman berjalan."
                )

        elif nasabah.pinjaman is not pinjaman_berjalan:
            error.append(
                f"Nasabah {nik} tidak menunjuk objek "
                f"pinjaman berjalan yang benar."
            )

    return error


def cek_integritas_rekening(bank):
    error = []
    pemilik_rekening = {}

    status_valid = (
        "aktif",
        "blokir",
        "tutup"
    )

    # Memeriksa seluruh rekening resmi yang disimpan bank.
    for norek_index, rekening in bank.rekening_index.items():
        # Key indeks harus sama dengan nomor pada objek rekening.
        if rekening.norek != norek_index:
            error.append(
                f"Key indeks {norek_index} tidak sesuai dengan "
                f"nomor pada objek rekening {rekening.norek}."
            )

        # Setiap rekening harus mempunyai pemilik.
        if rekening.pemilik is None:
            error.append(
                f"Rekening {norek_index} tidak memiliki pemilik."
            )
            continue

        nasabah = rekening.pemilik
        nik = nasabah.NIK

        # Pemilik rekening harus terdaftar dalam bank.
        if nik not in bank.data_nasabah:
            error.append(
                f"Pemilik rekening {norek_index} dengan NIK {nik} "
                f"tidak terdaftar dalam bank."
            )

        elif bank.data_nasabah[nik] is not nasabah:
            error.append(
                f"Rekening {norek_index} menunjuk objek nasabah "
                f"yang berbeda dari data_nasabah[{nik}]."
            )

        # Objek rekening harus terdapat pada daftar rekening pemilik.
        rekening_ditemukan = any(
            rekening_milik_nasabah is rekening
            for rekening_milik_nasabah in nasabah.rekening
        )

        if not rekening_ditemukan:
            error.append(
                f"Rekening {norek_index} ada dalam rekening_index, "
                f"tetapi tidak ada pada daftar rekening milik {nik}."
            )

        if rekening.status not in status_valid:
            error.append(
                f"Rekening {norek_index} memiliki "
                f"status tidak valid: {rekening.status}."
            )

    # Memeriksa rekening dari sisi setiap nasabah.
    for nik, nasabah in bank.data_nasabah.items():
        for rekening in nasabah.rekening:
            norek = rekening.norek

            # Rekening nasabah harus terdaftar dalam indeks bank.
            if norek not in bank.rekening_index:
                error.append(
                    f"Rekening {norek} milik nasabah {nik} "
                    f"tidak ditemukan dalam rekening_index."
                )

            else:
                # Nomor yang sama harus menunjuk objek yang sama.
                if bank.rekening_index[norek] is not rekening:
                    error.append(
                        f"Rekening {norek} milik nasabah {nik} "
                        f"bukan objek resmi dalam rekening_index."
                    )

            # Satu nomor rekening tidak boleh dimiliki dua nasabah.
            if norek in pemilik_rekening:
                error.append(
                    f"Rekening {norek} dimiliki lebih dari "
                    f"satu nasabah: "
                    f"{pemilik_rekening[norek]} dan {nik}."
                )
            else:
                pemilik_rekening[norek] = nik

            # Atribut pemilik harus menunjuk nasabah yang menyimpannya.
            if rekening.pemilik is not nasabah:
                pemilik_objek = (
                    rekening.pemilik.NIK
                    if rekening.pemilik is not None
                    else "None"
                )

                error.append(
                    f"Rekening {norek}: pemilik pada objek adalah "
                    f"{pemilik_objek}, tetapi rekening tersimpan "
                    f"pada nasabah {nik}."
                )

    return error


