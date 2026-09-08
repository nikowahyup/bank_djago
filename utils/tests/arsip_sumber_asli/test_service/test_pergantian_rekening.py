import datetime

from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.rekening import (
    RekeningReguler,
    RekeningPrioritas,
    RekeningGold,
    RekeningPlatinum
)

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.rekening.rekening_service import RekeningService


NOREK_UJI = "3001781978899033"


def muat_rekening_uji(norek):

    koneksi = buat_koneksi()

    try:
        data = koneksi.execute(
            """
            SELECT
                rekening.*,
                nasabah.nama AS nama_pemilik,
                nasabah.alamat AS alamat_pemilik
            FROM rekening
            JOIN nasabah
                ON nasabah.nik = rekening.nik_pemilik
            WHERE rekening.norek = ?
            """,
            (norek,)
        ).fetchone()

        if data is None:
            raise ValueError(
                "Rekening pengujian tidak ditemukan"
            )

        nasabah = Nasabahh(
            nama=data["nama_pemilik"],
            alamat=data["alamat_pemilik"],
            nik=data["nik_pemilik"]
        )

        if data["level"] == 1:
            kelas_rekening = RekeningReguler

        elif data["level"] == 2:
            kelas_rekening = RekeningPrioritas

        elif data["level"] == 3:
            kelas_rekening = RekeningGold

        elif data["level"] == 4:
            kelas_rekening = RekeningPlatinum

        else:
            raise ValueError(
                "Level rekening tidak dikenal"
            )

        waktu_dibuat = None

        if data["waktu_dibuat"] is not None:
            waktu_dibuat = datetime.datetime.fromisoformat(
                data["waktu_dibuat"]
            )

        rekening = kelas_rekening(
            norek=data["norek"],
            pin=data["pin"],
            pemilik=nasabah,
            waktu_dibuat=waktu_dibuat
        )

        rekening.set_saldo(
            data["saldo"]
        )

        rekening.status = data["status"]
        rekening.alasan_blokir = data["alasan_blokir"]

        nasabah.rekening.append(
            rekening
        )

        return rekening

    finally:
        koneksi.close()


def ambil_pin_sqlite(norek):

    koneksi = buat_koneksi()

    try:
        data = koneksi.execute(
            """
            SELECT pin
            FROM rekening
            WHERE norek = ?
            """,
            (norek,)
        ).fetchone()

        return data["pin"]

    finally:
        koneksi.close()


def hitung_audit_ganti_pin(norek):

    koneksi = buat_koneksi()

    try:
        data = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
            AND aksi = 'penggantian_pin_rekening'
            """,
            (norek,)
        ).fetchone()

        return data["jumlah"]

    finally:
        koneksi.close()


def ambil_audit_ganti_pin_terakhir(norek):

    koneksi = buat_koneksi()

    try:
        audit = koneksi.execute(
            """
            SELECT
                id,
                kategori,
                objek,
                aksi,
                log,
                nama,
                nik,
                norek
            FROM audit
            WHERE norek = ?
            AND aksi = 'penggantian_pin_rekening'
            ORDER BY id DESC
            LIMIT 1
            """,
            (norek,)
        ).fetchone()

        return audit

    finally:
        koneksi.close()


def test_ganti_pin():

    print("=" * 70)
    print("TEST GANTI PIN REKENING")
    print("=" * 70)

    rekening = muat_rekening_uji(
        NOREK_UJI
    )

    assert rekening.status == "aktif"

    pin_asli = rekening.pin

    # Buat PIN baru yang pasti berbeda
    if pin_asli != "654321":
        pin_baru = "654321"
    else:
        pin_baru = "123456"

    # Buat PIN salah yang pasti berbeda
    if pin_asli != "000000":
        pin_salah = "000000"
    else:
        pin_salah = "999999"

    print()
    print(
        "Status rekening :",
        rekening.status
    )

    print(
        "✅ Rekening aktif dan siap diuji"
    )

    jumlah_audit_awal = (
        hitung_audit_ganti_pin(
            rekening.norek
        )
    )

    # =========================================================
    # 1. PIN LAMA SALAH
    # =========================================================

    print()
    print(
        "Mencoba mengganti PIN dengan PIN lama salah..."
    )

    try:
        RekeningService.ganti_pin(
            rekening=rekening,
            pin_lama=pin_salah,
            pin_baru=pin_baru
        )

        raise AssertionError(
            "PIN lama salah ternyata diterima"
        )

    except ValueError as error:
        print(
            "✅ PIN lama salah ditolak:"
        )
        print(error)

    # SQLite dan object harus tetap sama
    assert rekening.pin == pin_asli

    assert (
        ambil_pin_sqlite(rekening.norek)
        == pin_asli
    )

    assert (
        hitung_audit_ganti_pin(rekening.norek)
        == jumlah_audit_awal
    )

    print(
        "✅ Tidak ada perubahan PIN atau audit"
    )

    # =========================================================
    # 2. PIN BARU SAMA DENGAN PIN LAMA
    # =========================================================

    print()
    print(
        "Mencoba menggunakan PIN baru "
        "yang sama dengan PIN lama..."
    )

    try:
        RekeningService.ganti_pin(
            rekening=rekening,
            pin_lama=pin_asli,
            pin_baru=pin_asli
        )

        raise AssertionError(
            "PIN yang sama ternyata diterima"
        )

    except ValueError as error:
        print(
            "✅ PIN baru yang sama ditolak:"
        )
        print(error)

    assert rekening.pin == pin_asli

    assert (
        ambil_pin_sqlite(rekening.norek)
        == pin_asli
    )

    assert (
        hitung_audit_ganti_pin(rekening.norek)
        == jumlah_audit_awal
    )

    print(
        "✅ Tidak ada perubahan atau audit tambahan"
    )

    # =========================================================
    # 3. PIN BARU TIDAK VALID
    # =========================================================

    print()
    print(
        "Mencoba PIN baru dengan format tidak valid..."
    )

    try:
        RekeningService.ganti_pin(
            rekening=rekening,
            pin_lama=pin_asli,
            pin_baru="12345"
        )

        raise AssertionError(
            "PIN tidak valid ternyata diterima"
        )

    except ValueError as error:
        print(
            "✅ PIN tidak valid ditolak:"
        )
        print(error)

    assert rekening.pin == pin_asli

    assert (
        ambil_pin_sqlite(rekening.norek)
        == pin_asli
    )

    assert (
        hitung_audit_ganti_pin(rekening.norek)
        == jumlah_audit_awal
    )

    # =========================================================
    # 4. GANTI PIN DENGAN DATA VALID
    # =========================================================

    print()
    print(
        "Mengganti PIN dengan data valid..."
    )

    RekeningService.ganti_pin(
        rekening=rekening,
        pin_lama=pin_asli,
        pin_baru=pin_baru
    )

    # Object memory harus berubah
    assert rekening.pin == pin_baru

    print(
        "✅ PIN pada object berhasil berubah"
    )

    # SQLite harus berubah
    pin_sqlite = ambil_pin_sqlite(
        rekening.norek
    )

    assert pin_sqlite == pin_baru

    print(
        "PIN SQLite :",
        pin_sqlite
    )

    print(
        "✅ PIN SQLite berhasil diperbarui"
    )

    # =========================================================
    # 5. CEK AUDIT
    # =========================================================

    jumlah_audit_setelah_berhasil = (
        hitung_audit_ganti_pin(
            rekening.norek
        )
    )

    assert (
        jumlah_audit_setelah_berhasil
        == jumlah_audit_awal + 1
    )

    audit = ambil_audit_ganti_pin_terakhir(
        rekening.norek
    )

    assert audit is not None

    assert (
        audit["kategori"]
        == "administratif"
    )

    assert (
        audit["objek"]
        == "rekening"
    )

    assert (
        audit["aksi"]
        == "penggantian_pin_rekening"
    )

    assert (
        audit["norek"]
        == rekening.norek
    )

    print()
    print("Audit ditemukan:")
    print(
        "Kategori :",
        audit["kategori"]
    )
    print(
        "Objek    :",
        audit["objek"]
    )
    print(
        "Aksi     :",
        audit["aksi"]
    )
    print(
        "Log      :",
        audit["log"]
    )

    print(
        "✅ Audit penggantian PIN tersimpan"
    )

    # =========================================================
    # 6. PIN LAMA TIDAK BOLEH BERLAKU LAGI
    # =========================================================

    print()
    print(
        "Mencoba menggunakan PIN lama setelah perubahan..."
    )

    try:
        RekeningService.ganti_pin(
            rekening=rekening,
            pin_lama=pin_asli,
            pin_baru="987654"
        )

        raise AssertionError(
            "PIN lama ternyata masih diterima"
        )

    except ValueError as error:
        print(
            "✅ PIN lama sudah tidak berlaku:"
        )
        print(error)

    assert rekening.pin == pin_baru

    assert (
        ambil_pin_sqlite(rekening.norek)
        == pin_baru
    )

    assert (
        hitung_audit_ganti_pin(rekening.norek)
        == jumlah_audit_setelah_berhasil
    )

    # =========================================================
    # 7. KEMBALIKAN PIN ASLI
    # =========================================================

    print()
    print(
        "Mengembalikan PIN ke nilai semula..."
    )

    RekeningService.ganti_pin(
        rekening=rekening,
        pin_lama=pin_baru,
        pin_baru=pin_asli
    )

    assert rekening.pin == pin_asli

    assert (
        ambil_pin_sqlite(rekening.norek)
        == pin_asli
    )

    print(
        "✅ PIN rekening berhasil dikembalikan"
    )

    print()
    print("=" * 70)
    print("SEMUA TEST GANTI PIN REKENING BERHASIL")
    print("=" * 70)


if __name__ == "__main__":
    test_ganti_pin()