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





