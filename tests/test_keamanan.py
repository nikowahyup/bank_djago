from bank_djago.utils.validator import Validator
import pytest


def test_tipe_data_pin_setelah_diolah():

    pin = "123456"
    hash_pin = Validator.buat_hash(pin)

    assert isinstance(hash_pin, str), "seharusnya tipenya string"
    assert hash_pin != pin, "seharusnya setelah diolah,pin berbeda dengan hash pin"


def test_dua_pin_harus_memiliki_hash_berbeda_dan_lolos_verifikasi():

    pin_1 = "123456"
    pin_2 = "123456"

    hash_pin_1 = Validator.buat_hash(pin_1)
    hash_pin_2 = Validator.buat_hash(pin_2)

    verifikasi_pin_1 = Validator.verifikasi_pin(
        pin_input=pin_1, pin_database=hash_pin_1
    )
    verifikasi_pin_2 = Validator.verifikasi_pin(
        pin_input=pin_2, pin_database=hash_pin_2
    )

    assert hash_pin_1 != hash_pin_2, "seharusnya hash berbeda"
    assert verifikasi_pin_1 is True
    assert verifikasi_pin_2 is True


def test_verifikasi_pin_dengan_pin_yang_benar_mengembalikan_true():

    pin = "123456"
    hash_pin = Validator.buat_hash(pin)

    verifikasi = Validator.verifikasi_pin(pin_input=pin, pin_database=hash_pin)

    assert verifikasi is True, "seharusnya mengembalikan True"


@pytest.mark.parametrize("pin_salah", ["12345", " ", "1 2 3 4 5", "", "123457"])
def test_verifikasi_pin_berbeda_mengembalikan_false(pin_salah):

    pin_benar = "123456"
    hash_pin = Validator.buat_hash(pin_benar)

    verifikasi = Validator.verifikasi_pin(pin_input=pin_salah, pin_database=hash_pin)

    assert (
        verifikasi is False
    ), "seharusnya hash pin input berbeda dengan hash tersimpan"


def test_panjang_format_hash():

    pin = "123456"
    hash_pin = Validator.buat_hash(pin)

    assert len(hash_pin) == 60, "seharusnya panjang hash 60 karakter"


def test_tujuh_karakter_pertama_hash():

    pin = "123456"
    hash_pin = Validator.buat_hash(pin)

    assert hash_pin.startswith("$2b$12$")
