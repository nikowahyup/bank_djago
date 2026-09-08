from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_service import AuditService
import datetime
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.utils.utility import JenisTransaksi
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas



class BiayaAdminService:

    @staticmethod
    def cari_periode_admin(
            waktu_bayar_admin,
            hari_ini
    ):
        daftar_periode = []

        tanggal_berikutnya = Utilitas.tambah_bulan(
            waktu_bayar_admin,
            1
        )

        while tanggal_berikutnya <= hari_ini:
            daftar_periode.append(tanggal_berikutnya)

            tanggal_berikutnya = Utilitas.tambah_bulan(
                tanggal_berikutnya,
                1
            )

        return daftar_periode


    @staticmethod
    def potong_admin(rekening,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        koneksi = buat_koneksi()
        try:
            data_rekening = RekeningRepository.cari_rekening_dengan_norek(norek=rekening.norek,koneksi=koneksi)

            if data_rekening is None:
                raise   ValueError("Rekening tidak ditemukan")

            if data_rekening['level'] != rekening.level:
                raise ValueError("Level rekening database dan objek python tidak sama")

            if data_rekening["status"] == "tutup":
                raise ValueError("Tidak dapat memotong saldo dari rekening tutup")


            saldo_sebelum = data_rekening['saldo']
            waktu_bayar_admin = (
                datetime.date.fromisoformat(data_rekening['waktu_bayar_admin'])
                )

            biaya_admin = rekening.biaya_admin

            if biaya_admin <= 0:
                raise ValueError("Biaya admin rekening tidak valid")
            daftar_periode = BiayaAdminService.cari_periode_admin(waktu_bayar_admin=waktu_bayar_admin,hari_ini=hari_ini)
            jumlah_periode_tertunggak = len(daftar_periode)
            if jumlah_periode_tertunggak == 0:
                return 0
            jumlah_periode_mampu = (saldo_sebelum//biaya_admin)
            jumlah_periode_dibayar = min(jumlah_periode_tertunggak,jumlah_periode_mampu)

            if jumlah_periode_dibayar == 0:
                return 0

            total_bayar = biaya_admin * jumlah_periode_dibayar
            saldo_baru = saldo_sebelum - total_bayar
            waktu_bayar_admin_baru = daftar_periode[jumlah_periode_dibayar - 1]

            jumlah_baris = RekeningRepository.perbarui_setelah_bayar_admin(norek=rekening.norek,
                                                                           saldo_baru=saldo_baru,
                                                                           waktu_bayar_admin_baru=waktu_bayar_admin_baru,
                                                                           koneksi=koneksi)

            if jumlah_baris != 1:
                raise ValueError("Gagal melakukan pembayaran biaya admin")

            transaksi = {
                "jenis": JenisTransaksi.BIAYA_ADMIN,
                "norek_sumber": rekening.norek,
                "nominal": total_bayar,
                "saldo_sumber_sebelum": saldo_sebelum,
                "saldo_sumber_sesudah": saldo_baru,
                "waktu": datetime.datetime.now()
            }

            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi, koneksi)

            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="biaya admin",
                log=(
                    f"BIAYA ADMIN | "
                    f"{jumlah_periode_dibayar} bulan | "
                    f"-Rp{Utilitas.format_rupiah(total_bayar)}"
                )
            )
            audit = AuditService.tambah_audit(
                kategori="finansial",
                objek="rekening",
                aksi="pemotongan_biaya_admin",
                log=(
                    f"Pembayaran biaya admin "
                    f"{jumlah_periode_dibayar} bulan sebesar "
                    f"Rp{Utilitas.format_rupiah(total_bayar)}"
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
                id_transaksi=id_transaksi
                ,koneksi=koneksi
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        rekening.set_saldo(saldo_baru)
        rekening.waktu_bayar_admin = waktu_bayar_admin_baru
        rekening.simpan_riwayat(riwayat)
        return total_bayar









