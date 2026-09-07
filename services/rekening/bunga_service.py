from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas, JenisTransaksi
import datetime
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository

class BungaService:

    @staticmethod
    def hitung_bulan(waktu_dapat_bunga, hari_ini):

        daftar_periode = []

        tanggal_berikutnya = Utilitas.tambah_bulan(waktu_dapat_bunga,1)

        while tanggal_berikutnya <= hari_ini:
            daftar_periode.append(tanggal_berikutnya)

            tanggal_berikutnya = Utilitas.tambah_bulan(tanggal_berikutnya, 1)

        return daftar_periode




    @staticmethod
    def berikan_bunga(rekening, hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        koneksi = buat_koneksi()

        try:
            data_rekening = RekeningRepository.cari_rekening_dengan_norek(
                norek=rekening.norek,
                koneksi=koneksi
                )

            if data_rekening is None:
                raise ValueError('Data rekening tidak ditemukan')

            if data_rekening['level'] != rekening.level:
                raise ValueError("Level rekening pada database dengan objek python tidak sama")

            if data_rekening['status'] == "tutup":
                raise ValueError(
                    "Bunga tidak dapat diberikan untuk rekening tutup"
                )

            saldo_sebelum = data_rekening['saldo']
            waktu_dapat_bunga = (
                datetime.date.fromisoformat(data_rekening['dapat_bunga'])
                )
            bunga = rekening.bunga
            daftar_bunga = BungaService.hitung_bulan(waktu_dapat_bunga=waktu_dapat_bunga,hari_ini=hari_ini)

            jumlah_dapat_bunga = len(daftar_bunga)
            if jumlah_dapat_bunga == 0:
                return 0

            jumlah_satu_bunga = round(
                saldo_sebelum * bunga / 12
            )
            total_bunga = jumlah_satu_bunga * jumlah_dapat_bunga

            saldo_baru = saldo_sebelum + total_bunga

            waktu_dapat_bunga_baru = daftar_bunga[
                jumlah_dapat_bunga - 1
                ]


            jumlah_baris = (
                RekeningRepository.perbarui_setelah_dapat_bunga(
                    norek=rekening.norek,
                    waktu_dapat_bunga_baru=waktu_dapat_bunga_baru,
                    saldo_baru=saldo_baru,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise ValueError("Gagal memberikan bunga ke rekening")


            riwayat = None

            if total_bunga > 0:
                transaksi = {
                    "jenis": JenisTransaksi.BUNGA_TABUNGAN,
                    "norek_tujuan": rekening.norek,
                    "nominal": total_bunga,
                    "saldo_tujuan_sebelum": saldo_sebelum,
                    "saldo_tujuan_sesudah": saldo_baru,
                    "waktu": datetime.datetime.now()
                }

                id_transaksi = TransaksiRepository.tambah_transaksi(
                    transaksi,
                    koneksi
                )

                riwayat = RiwayatTemplate.template(
                    kategori="transaksi",
                    jenis="bunga bulanan",
                    log=(
                        f"BUNGA BULANAN | "
                        f"{jumlah_dapat_bunga} bulan | "
                        f"+Rp{Utilitas.format_rupiah(total_bunga)}"
                    )
                )

                audit = AuditService.tambah_audit(
                    kategori="transaksi",
                    jenis="dapat bunga",
                    log=(
                        f"Pemberian bunga bulanan "
                        f"{jumlah_dapat_bunga} bulan sebesar "
                        f"Rp{Utilitas.format_rupiah(total_bunga)}"
                    ),
                    nama=rekening.pemilik.nama,
                    nik=rekening.pemilik.NIK,
                    norek=rekening.norek
                )

                RiwayatRepository.tambah_riwayat(
                    norek=rekening.norek,
                    riwayat=riwayat,
                    id_transaksi=id_transaksi,
                    koneksi=koneksi
                )

                AuditRepository.tambah_audit(
                    audit=audit,
                    id_transaksi=id_transaksi,
                    koneksi=koneksi
                )

            koneksi.commit()
        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        rekening.set_saldo(saldo_baru)
        rekening.dapat_bunga = waktu_dapat_bunga_baru
        if riwayat is not None:
            rekening.simpan_riwayat(riwayat)
        return total_bunga



