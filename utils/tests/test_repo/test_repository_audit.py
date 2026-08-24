import datetime

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)


AWAL_LOG_PENGUJIAN = "TEST-AUDIT-REPOSITORY"


def buat_audit(
        kategori,
        jenis,
        waktu,
        log,
        nama=None,
        nik=None,
        norek=None
):
    # Membuat dictionary audit sesuai struktur AuditService.
    return {
        "kategori": kategori,
        "jenis": jenis,
        "waktu": waktu,
        "log": log,
        "nama": nama,
        "nik": nik,
        "norek": norek
    }


def hapus_data_pengujian():
    koneksi = buat_koneksi()

    try:
        koneksi.execute(
            """
            DELETE FROM audit
            WHERE log LIKE ?
            """,
            (f"{AWAL_LOG_PENGUJIAN}%",)
        )

        koneksi.commit()

    finally:
        koneksi.close()


def uji_repository_audit():
    nik_pertama = "TEST-AUDIT-NIK-001"
    nik_kedua = "TEST-AUDIT-NIK-002"

    norek_pertama = "TEST-AUDIT-REKENING-001"
    norek_kedua = "TEST-AUDIT-REKENING-002"

    jenis_transfer = "transfer-test-repository"
    jenis_deposito = "deposito-test-repository"
    jenis_sistem = "reset-limit-test-repository"

    # Membersihkan data jika pengujian pernah dijalankan sebelumnya.
    hapus_data_pengujian()

    try:
        audit_transfer_pertama = buat_audit(
            kategori="transaksi",
            jenis=jenis_transfer,
            waktu=datetime.datetime(2026, 8, 24, 8, 0, 0),
            log=f"{AWAL_LOG_PENGUJIAN} | Transfer pertama",
            nama="Nasabah Audit Pertama",
            nik=nik_pertama,
            norek=norek_pertama
        )

        audit_deposito_pertama = buat_audit(
            kategori="transaksi",
            jenis=jenis_deposito,
            waktu=datetime.datetime(2026, 8, 24, 8, 1, 0),
            log=f"{AWAL_LOG_PENGUJIAN} | Deposito pertama",
            nama="Nasabah Audit Pertama",
            nik=nik_pertama,
            norek=norek_pertama
        )

        audit_transfer_kedua = buat_audit(
            kategori="transaksi",
            jenis=jenis_transfer,
            waktu=datetime.datetime(2026, 8, 24, 8, 2, 0),
            log=f"{AWAL_LOG_PENGUJIAN} | Transfer kedua",
            nama="Nasabah Audit Kedua",
            nik=nik_kedua,
            norek=norek_kedua
        )

        # Audit sistem tidak selalu mempunyai identitas nasabah atau rekening.
        audit_sistem = buat_audit(
            kategori="sistem",
            jenis=jenis_sistem,
            waktu=datetime.datetime(2026, 8, 24, 8, 3, 0),
            log=f"{AWAL_LOG_PENGUJIAN} | Reset limit sistem"
        )

        id_transfer_pertama = AuditRepository.tambah_audit(
            audit_transfer_pertama
        )

        id_deposito_pertama = AuditRepository.tambah_audit(
            audit_deposito_pertama
        )

        id_transfer_kedua = AuditRepository.tambah_audit(
            audit_transfer_kedua
        )

        id_audit_sistem = AuditRepository.tambah_audit(
            audit_sistem
        )

        seluruh_id = {
            id_transfer_pertama,
            id_deposito_pertama,
            id_transfer_kedua,
            id_audit_sistem
        }

        assert None not in seluruh_id, (
            "Ada audit yang gagal disimpan"
        )

        print("✅ Empat audit berhasil disimpan")

        assert len(seluruh_id) == 4, (
            "Setiap audit seharusnya mempunyai ID global berbeda"
        )

        print("✅ Seluruh audit mempunyai ID global berbeda")

        # Memastikan pencarian berdasarkan NIK terisolasi.
        hasil_nik_pertama = AuditRepository.cari_audit_dengan_nik(
            nik_pertama
        )

        assert len(hasil_nik_pertama) == 2, (
            "NIK pertama seharusnya mempunyai dua audit"
        )

        assert all(
            audit["nik"] == nik_pertama
            for audit in hasil_nik_pertama
        ), "Audit NIK pertama tercampur"

        print("✅ Pencarian audit berdasarkan NIK berhasil diisolasi")

        hasil_nik_kedua = AuditRepository.cari_audit_dengan_nik(
            nik_kedua
        )

        assert len(hasil_nik_kedua) == 1
        assert hasil_nik_kedua[0]["id"] == id_transfer_kedua
        assert hasil_nik_kedua[0]["nik"] == nik_kedua

        print("✅ Audit antar-nasabah berhasil dipisahkan")

        # Memastikan pencarian berdasarkan rekening terisolasi.
        hasil_norek_pertama = (
            AuditRepository.cari_audit_dengan_norek(
                norek_pertama
            )
        )

        assert len(hasil_norek_pertama) == 2

        assert all(
            audit["norek"] == norek_pertama
            for audit in hasil_norek_pertama
        ), "Audit rekening pertama tercampur"

        print("✅ Pencarian audit berdasarkan rekening berhasil")

        hasil_norek_kedua = (
            AuditRepository.cari_audit_dengan_norek(
                norek_kedua
            )
        )

        assert len(hasil_norek_kedua) == 1
        assert hasil_norek_kedua[0]["id"] == id_transfer_kedua

        print("✅ Audit antar-rekening berhasil dipisahkan")

        # Memastikan pencarian jenis dapat mencakup beberapa nasabah.
        hasil_transfer = AuditRepository.cari_audit_dengan_jenis(
            jenis_transfer
        )

        assert len(hasil_transfer) == 2

        id_hasil_transfer = {
            audit["id"]
            for audit in hasil_transfer
        }

        assert id_hasil_transfer == {
            id_transfer_pertama,
            id_transfer_kedua
        }

        assert all(
            audit["jenis"] == jenis_transfer
            for audit in hasil_transfer
        )

        print("✅ Pencarian audit berdasarkan jenis berhasil")

        # Hasil harus diurutkan dari ID terbesar ke terkecil.
        assert [
            audit["id"]
            for audit in hasil_transfer
        ] == [
            id_transfer_kedua,
            id_transfer_pertama
        ], "Audit tidak diurutkan berdasarkan ID terbaru"

        print("✅ Audit berhasil diurutkan berdasarkan ID terbaru")

        # Memastikan audit sistem tersimpan dengan data opsional NULL.
        hasil_sistem = AuditRepository.cari_audit_dengan_jenis(
            jenis_sistem
        )

        assert len(hasil_sistem) == 1

        audit_sistem_tersimpan = hasil_sistem[0]

        assert audit_sistem_tersimpan["id"] == id_audit_sistem
        assert audit_sistem_tersimpan["nama"] is None
        assert audit_sistem_tersimpan["nik"] is None
        assert audit_sistem_tersimpan["norek"] is None

        print("✅ Audit sistem tanpa identitas berhasil disimpan")

        # Memastikan datetime telah disimpan sebagai teks ISO.
        assert (
            audit_sistem_tersimpan["waktu"]
            == "2026-08-24T08:03:00"
        )

        print("✅ Waktu audit berhasil disimpan dalam format ISO")

        # Pencarian yang tidak menemukan data menghasilkan list kosong.
        nik_tidak_ada = AuditRepository.cari_audit_dengan_nik(
            "NIK-TIDAK-TERDAFTAR"
        )

        norek_tidak_ada = AuditRepository.cari_audit_dengan_norek(
            "REKENING-TIDAK-TERDAFTAR"
        )

        jenis_tidak_ada = AuditRepository.cari_audit_dengan_jenis(
            "JENIS-TIDAK-TERDAFTAR"
        )

        assert nik_tidak_ada == []
        assert norek_tidak_ada == []
        assert jenis_tidak_ada == []

        print("✅ Pencarian data tidak tersedia menghasilkan list kosong")
        print("✅ Repository audit bekerja sesuai rancangan")

    finally:
        # Data pengujian tetap dibersihkan apabila assert gagal.
        hapus_data_pengujian()


if __name__ == "__main__":
    uji_repository_audit()