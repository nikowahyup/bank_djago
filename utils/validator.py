class Validator:

    @staticmethod
    def validasi_nasabah(nama,nik,alamat,pin):
        error = []
        if not all(kata.isalpha() for kata in nama.split()):

            error.append("Nama tidak boleh mengandung angka")
        if not len(nik)==16:
            error.append("Jumlah digit NIK tidak valid")
        if not nik.isdigit():
            error.append("NIK tidak boleh mengandung huruf")

        if not len(pin) == 6 or not pin.isdigit():
            error.append("PIN harus berupa 6 digit angka")

        if not alamat.strip():
            error.append("Alamat tidak boleh kosong")

        if error:
            raise ValueError(error)

    @staticmethod
    def validasi_pin(pin):
        if not len(pin) == 6:
            raise  ValueError("Jumlah PIN harus 6 digit")
        if not pin.isdigit():
            raise  ValueError("PIN harus berupa angka semua")

    @staticmethod
    def amankan_rekening(rekening):
        if rekening.status != "aktif":
            raise  ValueError(f"Rekening Anda saat ini sedang di{rekening.status}")





    # nasabah = bank.data_nasabah["3510152602082002"]
    # pinjaman = nasabah.pinjaman
    # # PinjamanService.cairkan_pinjaman(bank,pinjaman,datetime.date(2027,1,31))
    # PinjamanService.bayar_cicilan(
    #     bank,
    #     pinjaman,
    #     datetime.date(2027, 2, 20)
    # )
    #
    # print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
    # print("Jatuh tempo baru :", pinjaman.tanggal_jatuh_tempo)
    # print(
    #     "Boleh bayar lagi :",
    #     PinjamanService.tanggal_boleh_bayar(pinjaman)
    # )
    #
    #
    # print("Tanggal pencairan :", pinjaman.tanggal_pencairan)
    # print("Jatuh tempo       :", pinjaman.tanggal_jatuh_tempo)
    #
    # PinjamanService.bayar_cicilan(
    #     bank,
    #     pinjaman,
    #     datetime.date(2027, 3, 1)
    # )
    #
    # print("Cicilan terbayar :", pinjaman.cicilan_terbayar)
    # print("Jatuh tempo baru :", pinjaman.tanggal_jatuh_tempo)
    # print(
    #     "Boleh bayar lagi :",
    #     PinjamanService.tanggal_boleh_bayar(pinjaman))

    # hari_ini = datetime.date(2026,9,18)
    # # Scheduler.jalankan(bank,hari_ini)
    # #
    # # hari_ini = datetime.date(2026, 9, 18)
    # # Scheduler.jalankan(bank, hari_ini
    # nasabah = bank.data_nasabah["3150152602002002"]
    # pinjaman = nasabah.pinjaman
    # # PinjamanService.bayar_cicilan(bank,pinjaman,hari_ini)
    # #
    # tanggal_test = [
    #     datetime.date(2026, 9, 5),  # cicilan 1
    #     datetime.date(2026, 9, 18),  # cicilan 2
    #     datetime.date(2026, 10, 18),  # cicilan 3
    #     datetime.date(2026, 11, 18),  # cicilan 4
    #     datetime.date(2026, 12, 18),  # cicilan 5
    #     datetime.date(2027, 1, 18),  # cicilan 6
    # ]
    #
    # for tanggal in tanggal_test:
    #     PinjamanService.bayar_cicilan(
    #         bank,
    #         pinjaman,
    #         tanggal
    #     )
    #
    #     print(
    #         tanggal,
    #         pinjaman.cicilan_terbayar,
    #         pinjaman.sisa_pokok,
    #         pinjaman.status
    #     )
    # PinjamanService.bayar_cicilan(bank,pinjaman,datetime.date(2027,2,18))
    # bank.proses_harian()
    # error = BankService.cek_integritas_rekening(bank)
    #
    # if not error:
    #     print("✅ Integritas rekening valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #     for item in error:
    #         print("-", item)
    # error = BankService.cek_integritas_deposito(bank)
    #
    # if not error:
    #     print("✅ Integritas deposito valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #
    #     for item in error:
    #         print("-", item)
    #
    # error = BankService.cek_integritas_pinjaman(bank)
    #
    # if not error:
    #     print("✅ Integritas pinjaman valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #
    #     for item in error:
    #         print("-", item)
    # #
    # error = BankService.cek_integritas_notifikasi(bank)
    #
    # if not error:
    #     print("✅ Integritas notifikasi valid.")
    # else:
    #     print("❌ Ditemukan masalah:")
    #     for item in error:
    #         print("-", item)