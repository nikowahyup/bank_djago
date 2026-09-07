"""Skenario manual yang dipulihkan dari `utils/tests/test_service/test_deposito.py` (urutan 5).

File ini mempertahankan langkah pengujian asli sebagai bahan belajar.
Jalankan hanya setelah membaca data awal dan efek mutasinya.
"""

from unittest.mock import patch

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.loaders.deposito_loader import (
    DepositoLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.services.deposito.deposito_service import (
    DepositoService,
    StatusDeposito
)
from bank_djago.utils.utility import JenisReferensiID


NOREK = "3001781978899033"
NOMINAL_DEPOSITO = 1_000_000
TENOR_DEPOSITO = 1


def cari_deposito_pengujian():
    """
    Mencari deposito terbaru yang sesuai dengan data pengujian.

    Filter lengkap digunakan agar pengujian tidak salah memilih
    deposito aktif lain yang kebetulan baru dibuat.
    """
    koneksi = buat_koneksi()

    try:
        return koneksi.execute(
            """
            SELECT *
            FROM deposito
            WHERE norek = ?
              AND nominal = ?
              AND lama_bulan = ?
              AND jenis_aro = 'tidak'
              AND status = 'aktif'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                NOREK,
                NOMINAL_DEPOSITO,
                TENOR_DEPOSITO
            )
        ).fetchone()

    finally:
        koneksi.close()


def ambil_kondisi_database(id_deposito):
    """
    Mengambil kondisi yang harus tetap sama apabila
    pencairan deposito mengalami rollback.
    """
    koneksi = buat_koneksi()

    try:
        rekening = koneksi.execute(
            """
            SELECT saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (NOREK,)
        ).fetchone()

        deposito = koneksi.execute(
            """
            SELECT
                status,
                nominal,
                lama_bulan,
                jenis_aro,
                jatuh_tempo
            FROM deposito
            WHERE id = ?
            """,
            (id_deposito,)
        ).fetchone()

        # Untuk deposito ini seharusnya sudah ada satu transaksi
        # pembukaan. Transaksi pencairan yang gagal tidak boleh
        # menambah jumlah tersebut.
        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            WHERE jenis_referensi = ?
              AND id_referensi = ?
            """,
            (
                JenisReferensiID.DEPOSITO.value,
                id_deposito
            )
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            WHERE norek = ?
            """,
            (NOREK,)
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            WHERE norek = ?
            """,
            (NOREK,)
        ).fetchone()["jumlah"]

        jumlah_notifikasi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM notifikasi
            WHERE jenis_referensi = ?
              AND id_objek = ?
            """,
            (
                JenisReferensiID.DEPOSITO.value,
                id_deposito
            )
        ).fetchone()["jumlah"]

        return {
            "saldo": rekening["saldo"],
            "status_rekening": rekening["status"],
            "status_deposito": deposito["status"],
            "nominal_deposito": deposito["nominal"],
            "tenor_deposito": deposito["lama_bulan"],
            "jenis_aro": deposito["jenis_aro"],
            "jatuh_tempo": deposito["jatuh_tempo"],
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit,
            "jumlah_notifikasi": jumlah_notifikasi
        }

    finally:
        koneksi.close()


# ==========================================================
# 1. Cari deposito baru berdasarkan data yang diketahui
# ==========================================================
data_deposito = cari_deposito_pengujian()

assert data_deposito is not None, (
    "Deposito aktif non-ARO sebesar Rp1.000.000 "
    "dengan tenor 3 bulan tidak ditemukan"
)

id_deposito = data_deposito["id"]

print("=== DEPOSITO YANG DITEMUKAN ===")
print(f"ID deposito      : {id_deposito}")
print(f"Nomor rekening   : {data_deposito['norek']}")
print(f"Nominal          : {data_deposito['nominal']}")
print(f"Tenor            : {data_deposito['lama_bulan']} bulan")
print(f"Jenis ARO        : {data_deposito['jenis_aro']}")
print(f"Status           : {data_deposito['status']}")
print(f"Jatuh tempo      : {data_deposito['jatuh_tempo']}")


# ==========================================================
# 2. Muat objek deposito dari SQLite
# ==========================================================
daftar_deposito_aktif = (
    DepositoLoader.muat_semua_deposito_aktif()
)

deposito = next(
    (
        item
        for item in daftar_deposito_aktif
        if item.ID == id_deposito
    ),
    None
)

assert deposito is not None, (
    f"Objek deposito ID {id_deposito} gagal dimuat"
)

assert deposito.rekening.norek == NOREK
assert deposito.nominal == NOMINAL_DEPOSITO
assert deposito.lama_bulan == TENOR_DEPOSITO
assert deposito.jenis_aro == "tidak"
assert deposito.status == StatusDeposito.AKTIF


# ==========================================================
# 3. Simulasikan tibanya tanggal jatuh tempo
# ==========================================================
# Kita tidak mengubah tanggal komputer atau main.py.
# Tanggal jatuh tempo hanya diberikan sebagai argumen.
hari_simulasi = deposito.jatuh_tempo

DepositoService.tandai_jatuh_tempo(
    deposito=deposito,
    hari_ini=hari_simulasi
)

assert deposito.status == StatusDeposito.JATUH_TEMPO

print("\n=== SETELAH PENANDAAN JATUH TEMPO ===")
print(f"Hari simulasi    : {hari_simulasi}")
print(f"Status objek     : {deposito.status}")
print("✅ Deposito berhasil ditandai jatuh tempo")


# ==========================================================
# 4. Rekam kondisi sebelum mencoba pencairan
# ==========================================================
# Status jatuh tempo sudah di-commit sebagai proses terpisah.
# Kondisi inilah yang harus dipertahankan setelah rollback.
kondisi_sebelum = ambil_kondisi_database(id_deposito)

saldo_objek_sebelum = deposito.rekening.saldo
status_objek_sebelum = deposito.status

jumlah_riwayat_objek_sebelum = len(
    deposito.rekening.riwayat
)

print("\n=== KONDISI SEBELUM PENCAIRAN ===")
print(kondisi_sebelum)

assert kondisi_sebelum["status_deposito"] == (
    StatusDeposito.JATUH_TEMPO
)
assert kondisi_sebelum["status_rekening"] == "aktif"
assert kondisi_sebelum["nominal_deposito"] == (
    NOMINAL_DEPOSITO
)
assert kondisi_sebelum["tenor_deposito"] == (
    TENOR_DEPOSITO
)
assert kondisi_sebelum["jenis_aro"] == "tidak"


# ==========================================================
# 5. Buat pencairan gagal setelah beberapa query berjalan
# ==========================================================
# AuditRepository sementara diganti dengan fungsi yang selalu
# menghasilkan error.
#
# Sebelum mencapai audit, service telah mencoba:
# - mengubah status deposito menjadi dicairkan;
# - menambahkan hasil pencairan ke saldo rekening;
# - membuat transaksi pencairan;
# - membuat riwayat pencairan.
#
# Seluruh perubahan itu menggunakan koneksi yang sama dan
# belum di-commit, sehingga harus dibatalkan oleh rollback.
try:
    with patch.object(
        AuditRepository,
        "tambah_audit",
        side_effect=RuntimeError(
            "Kegagalan audit untuk menguji rollback pencairan"
        )
    ):
        DepositoService.cairkan_deposito(
            deposito=deposito,
            hari_ini=hari_simulasi
        )

    # Jika baris ini tercapai, berarti pencairan justru berhasil
    # meskipun audit sudah dibuat gagal.
    raise AssertionError(
        "Pencairan deposito seharusnya gagal"
    )

except RuntimeError as error:
    assert str(error) == (
        "Kegagalan audit untuk menguji rollback pencairan"
    )

    print("\n✅ Kegagalan buatan berhasil dipicu")
    print(f"Pesan error: {error}")


# ==========================================================
# 6. Ambil kondisi setelah rollback
# ==========================================================
kondisi_sesudah = ambil_kondisi_database(id_deposito)

print("\n=== KONDISI SETELAH ROLLBACK ===")
print(kondisi_sesudah)


# ==========================================================
# 7. Periksa kondisi database
# ==========================================================
# Seluruh kondisi harus identik dengan keadaan setelah
# deposito ditandai jatuh tempo.
assert kondisi_sesudah == kondisi_sebelum

# Penandaan jatuh tempo sudah menjadi transaksi terpisah,
# sehingga status ini tidak boleh kembali menjadi aktif.
assert kondisi_sesudah["status_deposito"] == (
    StatusDeposito.JATUH_TEMPO
)


# ==========================================================
# 8. Periksa kondisi objek Python
# ==========================================================
# Pembaruan objek dalam cairkan_deposito dilakukan setelah
# commit. Karena commit tidak tercapai, objek harus tetap sama.
assert deposito.rekening.saldo == saldo_objek_sebelum
assert deposito.status == status_objek_sebelum

assert len(deposito.rekening.riwayat) == (
    jumlah_riwayat_objek_sebelum
)


print(
    "\n✅ ROLLBACK PENCAIRAN BERHASIL: saldo tetap, "
    "deposito tetap jatuh tempo, transaksi tidak bertambah, "
    "dan tidak ada riwayat atau audit pencairan yang tersisa"



)
