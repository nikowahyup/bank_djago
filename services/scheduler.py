import datetime


from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
from bank_djago.penyimpanan.loaders.pinjaman_loader import PinjamanLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_tulis
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.notifikasi.notifikasi_service import NotifikasiService
from bank_djago.services.rekening.biaya_admin_service import BiayaAdminService
from bank_djago.services.deposito.deposito_service import DepositoService, JenisAro
from bank_djago.services.rekening.bunga_service import BungaService


from bank_djago.utils.utility import JenisReferensi


class Scheduler:

    @staticmethod
    def jalankan(hari_ini=None):

        if hari_ini is None:
            hari_ini = datetime.date.today()

        daftar_rekening = RekeningLoader.muat_semua_rekening_berjalan()
        total_pendapatan_untuk_admin = 0
        total_pengeluaran_untuk_bunga = 0

        jumlah_berhasil = 0
        jumlah_gagal = 0

        for rekening in daftar_rekening:

            with buat_koneksi_tulis() as koneksi:

                try:
                    total_bayar_bunga = BungaService.berikan_bunga(
                        rekening=rekening, koneksi=koneksi, hari_ini=hari_ini
                    )

                    total_bayar_admin = BiayaAdminService.potong_admin(
                        rekening=rekening, koneksi=koneksi, hari_ini=hari_ini
                    )
                    total_pendapatan_untuk_admin += total_bayar_admin
                    total_pengeluaran_untuk_bunga += total_bayar_bunga

                    jumlah_berhasil += 1

                except Exception:
                    jumlah_gagal += 1
                    continue

        daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()
        jumlah_deposito_jatuh_tempo = 0
        jumlah_deposito_perpanjangan = 0

        for deposito in daftar_deposito:
            nasabah = deposito.pemilik

            sisa_hari = (deposito.jatuh_tempo - hari_ini).days

            if deposito.jenis_aro == JenisAro.TIDAK:
                if sisa_hari > 3:
                    continue

                try:
                    with buat_koneksi_tulis() as koneksi:

                        if sisa_hari <= 0:

                            DepositoService.tandai_jatuh_tempo(
                                deposito=deposito, koneksi=koneksi, hari_ini=hari_ini
                            )
                            jumlah_deposito_jatuh_tempo += 1

                        pesan = DepositoService.buat_pesan_pengingat(
                            deposito=deposito, hari_ini=hari_ini
                        )

                        NotifikasiService.simpan_notifikasi_referensi(
                            nasabah=nasabah,
                            jenis="deposito",
                            pesan=pesan,
                            jenis_referensi=JenisReferensi.DEPOSITO,
                            id_objek=deposito.ID,
                            koneksi=koneksi,
                        )
                except Exception:
                    continue

            else:

                if hari_ini < deposito.jatuh_tempo:
                    continue

                try:
                    with buat_koneksi_tulis() as koneksi:

                        DepositoService.perpanjangan(
                            deposito=deposito, koneksi=koneksi, hari_ini=hari_ini
                        )
                        pesan = DepositoService.buat_pesan_pengingat(
                            deposito=deposito, hari_ini=hari_ini
                        )

                        NotifikasiService.simpan_notifikasi_referensi(
                            nasabah=nasabah,
                            jenis="deposito",
                            pesan=pesan,
                            jenis_referensi=JenisReferensi.DEPOSITO,
                            id_objek=deposito.ID,
                            koneksi=koneksi,
                        )

                        jumlah_deposito_perpanjangan += 1

                except Exception:
                    continue

        daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()

        for pinjaman in daftar_pinjaman:
            nasabah = pinjaman.pemilik

            try:
                pesan = PinjamanService.buat_pesan_pengingat(
                    pinjaman=pinjaman, hari_ini=hari_ini
                )
                if pesan is None:
                    continue

                with buat_koneksi_tulis() as koneksi:
                    NotifikasiService.simpan_notifikasi_referensi(
                        nasabah=nasabah,
                        jenis="pinjaman",
                        pesan=pesan,
                        jenis_referensi=JenisReferensi.PINJAMAN,
                        id_objek=pinjaman.ID,
                        koneksi=koneksi,
                    )

            except Exception:
                continue
