from bank_djago.services.exceptions import StatusTidakValid, PinTidakCocok
import bcrypt

from bank_djago.services.exceptions import InputTidakValid


class Validator:

    @staticmethod
    def validasi_nasabah(nama, nik, alamat, pin):
        error = []
        if not all(kata.isalpha() for kata in nama.split()):

            error.append("Nama tidak boleh mengandung angka")
        if not len(nik) == 16:
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
    def validasi_format_pin(pin):
        if not isinstance(pin, str) or not pin.strip():
            raise InputTidakValid("PIN tidak boleh kosong")
        if not len(pin) == 6 or not pin.isdigit():
            raise InputTidakValid("PIN harus berupa 6 digit angka")

    @staticmethod
    def validasi_format_nik(nik):
        if not isinstance(nik, str) or not nik.strip():
            raise InputTidakValid("NIK tidak boleh kosong")
        if not nik.isdigit():
            raise InputTidakValid("NIK tidak boleh mengandung huruf")
        if len(nik) != 16:
            raise InputTidakValid("Jumlah digit NIK tidak valid")

    @staticmethod
    def validasi_format_norek(norek):
        if not isinstance(norek, str) or not norek.strip():
            raise InputTidakValid("Nomor rekening tidak boleh kosong")
        if not norek.isdigit():
            raise InputTidakValid("Nomor rekening tidak boleh mengandung huruf")
        if len(norek) != 16:
            raise InputTidakValid("Jumlah digit nomor rekening tidak valid")

    @staticmethod
    def validasi_nominal(nominal):
        if not isinstance(nominal, int):
            raise InputTidakValid("Nominal tidak valid")
        if nominal < 10_000:
            raise InputTidakValid("Minimal transaksi adalah Rp10.000")

    @staticmethod
    def validasi_format_identtitas(nik, norek):

        Validator.validasi_format_nik(nik=nik)
        Validator.validasi_format_norek(norek=norek)

    @staticmethod
    def amankan_rekening(rekening):
        if rekening.status != "aktif":
            raise StatusTidakValid(f"Rekening Anda saat ini sedang di{rekening.status}")

    @staticmethod
    def buat_hash(pin, rounds=12):

        bytes_pin = pin.encode("utf-8")
        salt = bcrypt.gensalt(rounds=rounds)
        bytes_hash = bcrypt.hashpw(bytes_pin, salt)

        hash_str = bytes_hash.decode("utf-8")

        return hash_str

    @staticmethod
    def verifikasi_pin(pin_input, pin_database):

        pin_input_encode = pin_input.encode("utf-8")
        pin_database_hash = pin_database.encode("utf-8")

        is_sama = bcrypt.checkpw(pin_input_encode, pin_database_hash)

        if not is_sama:
            raise PinTidakCocok("PIN yang dimasukkan salah")
