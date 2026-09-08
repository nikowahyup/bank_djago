import datetime

from bank_djago.core.nasabah import Nasabahh
from bank_djago.core.rekening import (
    RekeningReguler,
    RekeningPrioritas,
    RekeningGold,
    RekeningPlatinum
)

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.rekening_repository import (
    RekeningRepository
)
from bank_djago.services.rekening.rekening_service import (
    RekeningService
)


NOREK_UJI = "3001781978899033"
ALASAN_UJI = "Persiapan pengujian buka blokir"


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
            waktu_dibuat = (
                datetime.datetime.fromisoformat(
                    data["waktu_dibuat"]
                )
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

        rekening.alasan_blokir = (
            data["alasan_blokir"]
        )

        nasabah.rekening.append(
            rekening
        )

        return rekening

    finally:
        koneksi.close()


def siapkan_status_blokir(rekening):

    koneksi = buat_koneksi()

    try:
        jumlah_baris = (
            RekeningRepository.perbarui_status_blokir(
                norek=rekening.norek,
                status_baru="blokir",
                alasan_blokir=ALASAN_UJI,
                koneksi=koneksi
            )
        )

        if jumlah_baris != 1:
            raise ValueError(
                "Gagal menyiapkan rekening untuk pengujian"
            )

        koneksi.commit()

    except Exception:
        koneksi.rollback()
        raise

    finally:
        koneksi.close()

    # Sinkronkan object dengan kondisi SQLite
    rekening.status = "blokir"
    rekening.alasan_blokir = ALASAN_UJI


def ambil_status_sqlite(norek):

    koneksi = buat_koneksi()

    try:
        data = koneksi.execute(
            """
            SELECT
                status,
                alasan_blokir
            FROM rekening
            WHERE norek = ?
            """,
            (norek,)
        ).fetchone()

        return data

    finally:
        koneksi.close()


def ambil_audit_buka_blokir_terakhir(norek):

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
            AND aksi = 'pembukaan_blokir_rekening'
            ORDER BY id DESC
            LIMIT 1
            """,
            (norek,)
        ).fetchone()

        return audit

    finally:
        koneksi.close()


def hitung_audit_buka_blokir(norek):

    koneksi = buat_koneksi()

    try:
        hasil = koneksi.execute(
            """
            SELECT
                COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
            AND aksi = 'pembukaan_blokir_rekening'
            """,
            (norek,)
        ).fetchone()

        return hasil["jumlah"]

    finally:
        koneksi.close()


def test_buka_blokir():

    print("=" * 70)
    print("TEST BUKA BLOKIR REKENING")
    print("=" * 70)

    # =========================================================
    # 1. MUAT REKENING
    # =========================================================

    rekening = muat_rekening_uji(
        NOREK_UJI
    )

    pin_benar = rekening.pin

    # Buat PIN salah yang dijamin berbeda dari PIN asli
    if pin_benar != "000000":
        pin_salah = "000000"
    else:
        pin_salah = "999999"

    # =========================================================
    # 2. SIAPKAN KONDISI BLOKIR
    # =========================================================

    siapkan_status_blokir(
        rekening
    )

    data = ambil_status_sqlite(
        rekening.norek
    )

    assert data["status"] == "blokir"

    assert (
        data["alasan_blokir"]
        == ALASAN_UJI
    )

    print()
    print(
        "Status awal        :",
        data["status"]
    )

    print(
        "Alasan blokir      :",
        data["alasan_blokir"]
    )

    print(
        "✅ Kondisi awal blokir berhasil disiapkan"
    )

    # =========================================================
    # 3. CATAT JUMLAH AUDIT AWAL
    # =========================================================

    jumlah_audit_awal = (
        hitung_audit_buka_blokir(
            rekening.norek
        )
    )

    # =========================================================
    # 4. COBA PIN SALAH
    # =========================================================

    print()
    print("Mencoba membuka blokir dengan PIN salah...")

    try:
        RekeningService.buka_blokir(
            rekening=rekening,
            pin=pin_salah
        )

        raise AssertionError(
            "PIN salah ternyata berhasil membuka blokir"
        )

    except ValueError as error:
        print(
            "✅ PIN salah ditolak:"
        )
        print(error)

    # =========================================================
    # 5. PASTIKAN PIN SALAH TIDAK MENGUBAH SQLITE
    # =========================================================

    data = ambil_status_sqlite(
        rekening.norek
    )

    assert data["status"] == "blokir"

    assert (
        data["alasan_blokir"]
        == ALASAN_UJI
    )

    jumlah_audit_setelah_pin_salah = (
        hitung_audit_buka_blokir(
            rekening.norek
        )
    )

    assert (
        jumlah_audit_setelah_pin_salah
        == jumlah_audit_awal
    )

    print(
        "✅ PIN salah tidak mengubah status "
        "atau membuat audit"
    )

    # =========================================================
    # 6. BUKA BLOKIR DENGAN PIN BENAR
    # =========================================================

    print()
    print("Membuka blokir dengan PIN benar...")

    RekeningService.buka_blokir(
        rekening=rekening,
        pin=pin_benar
    )

    # =========================================================
    # 7. CEK OBJECT MEMORY
    # =========================================================

    assert rekening.status == "aktif"

    assert rekening.alasan_blokir is None

    print(
        "✅ Object rekening kembali aktif"
    )

    # =========================================================
    # 8. CEK SQLITE
    # =========================================================

    data = ambil_status_sqlite(
        rekening.norek
    )

    assert data["status"] == "aktif"

    assert data["alasan_blokir"] is None

    print()
    print(
        "Status SQLite      :",
        data["status"]
    )

    print(
        "Alasan blokir      :",
        data["alasan_blokir"]
    )

    print(
        "✅ SQLite berhasil membuka blokir"
    )

    # =========================================================
    # 9. CEK AUDIT
    # =========================================================

    audit = ambil_audit_buka_blokir_terakhir(
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
        == "pembukaan_blokir_rekening"
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
        "✅ Audit pembukaan blokir tersimpan"
    )

    jumlah_audit_setelah_berhasil = (
        hitung_audit_buka_blokir(
            rekening.norek
        )
    )

    assert (
        jumlah_audit_setelah_berhasil
        == jumlah_audit_awal + 1
    )

    # =========================================================
    # 10. COBA BUKA BLOKIR KEDUA KALI
    # =========================================================

    print()
    print(
        "Mencoba membuka rekening "
        "yang sudah aktif..."
    )

    try:
        RekeningService.buka_blokir(
            rekening=rekening,
            pin=pin_benar
        )

        raise AssertionError(
            "Rekening aktif ternyata bisa "
            "dibuka blokir lagi"
        )

    except ValueError as error:
        print(
            "✅ Buka blokir kedua ditolak:"
        )
        print(error)

    # =========================================================
    # 11. PASTIKAN TIDAK ADA AUDIT TAMBAHAN
    # =========================================================

    jumlah_audit_akhir = (
        hitung_audit_buka_blokir(
            rekening.norek
        )
    )

    assert (
        jumlah_audit_akhir
        == jumlah_audit_setelah_berhasil
    )

    print(
        "✅ Percobaan kedua tidak membuat audit tambahan"
    )

    print()
    print("=" * 70)
    print("SEMUA TEST BUKA BLOKIR REKENING BERHASIL")
    print("=" * 70)


if __name__ == "__main__":
    test_buka_blokir()