
from bank_djago.penyimpanan.loaders.deposito_loader import DepositoLoader
from bank_djago.penyimpanan.loaders.pinjaman_loader import PinjamanLoader
from bank_djago.penyimpanan.loaders.rekening_loaders import RekeningLoader
from bank_djago.services.pinjaman.pinjaman_service import PinjamanService
from bank_djago.services.notifikasi_service import NotifikasiService
from bank_djago.services.rekening.biaya_admin_service import  BiayaAdminService
from bank_djago.services.deposito.deposito_service import DepositoService,JenisAro
from bank_djago.services.rekening.bunga_service import BungaService

import datetime


from bank_djago.utils.utility import Utilitas, JenisReferensi


class Scheduler:

    @staticmethod
    def jalankan(hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()



        daftar_rekening = RekeningLoader.muat_semua_rekening_berjalan()

        for rekening in daftar_rekening:

            BungaService.berikan_bunga(rekening, hari_ini)

            BiayaAdminService.potong_admin(rekening, hari_ini)



        daftar_deposito = DepositoLoader.muat_semua_deposito_aktif()

        for deposito in daftar_deposito:

            if deposito.jenis_aro == JenisAro.TIDAK:
                sisa_hari = (deposito.jatuh_tempo - hari_ini).days

                if sisa_hari > 0:
                    if sisa_hari <= 3:
                        pesan = (
                            f"Deposito ber-ID {deposito.ID} akan jatuh tempo pada "
                            f"{Utilitas.format_tanggal_indonesia(deposito.jatuh_tempo)}"
                        )

                        NotifikasiService.simpan_notifikasi_referensi(
                            nasabah=deposito.pemilik,
                            jenis="deposito",
                            pesan=pesan,
                            jenis_referensi=JenisReferensi.DEPOSITO,
                            id_objek=deposito.ID
                        )

                    continue

                # sisa_hari == 0 atau negatif berarti sudah jatuh tempo.
                DepositoService.tandai_jatuh_tempo(
                    deposito=deposito,
                    hari_ini=hari_ini
                )

                pesan = (
                    f"Deposito ber-ID {deposito.ID} telah jatuh tempo. "
                    "Silakan lakukan pencairan deposito."
                )

                NotifikasiService.simpan_notifikasi_referensi(
                    nasabah=deposito.pemilik,
                    jenis="deposito",
                    pesan=pesan,
                    jenis_referensi=JenisReferensi.DEPOSITO,
                    id_objek=deposito.ID
                )

                continue
            else:


                if (
                        deposito.proses_aro is not None
                        and deposito.proses_aro < hari_ini
                ):
                    NotifikasiService.hapus_notifikasi_referensi(
                        nasabah=deposito.pemilik,
                        jenis_referensi=JenisReferensi.DEPOSITO,
                        id_objek=deposito.ID
                    )

                if hari_ini < deposito.jatuh_tempo:
                    continue

                DepositoService.perpanjangan(
                    deposito=deposito,
                    hari_ini=hari_ini
                )

                pesan = (
                    f"Deposito ARO ber-ID {deposito.ID} berhasil diperpanjang otomatis. "
                    f"Jatuh tempo berikutnya pada "
                    f"{Utilitas.format_tanggal_indonesia(deposito.jatuh_tempo)}."
                )

                NotifikasiService.simpan_notifikasi_referensi(
                    nasabah=deposito.pemilik,
                    jenis="deposito",
                    pesan=pesan,
                    jenis_referensi=JenisReferensi.DEPOSITO,
                    id_objek=deposito.ID
                )




        daftar_pinjaman = PinjamanLoader.muat_semua_pinjaman_aktif()

        for pinjaman in daftar_pinjaman:
            nasabah = pinjaman.pemilik
            pesan = PinjamanService.buat_pesan_pengingat(
                pinjaman=pinjaman,
                hari_ini=hari_ini
            )
            if pesan is None:
                continue

            NotifikasiService.simpan_notifikasi_referensi(
                nasabah=nasabah,
                jenis="pinjaman",
                pesan=pesan,
                jenis_referensi=JenisReferensi.PINJAMAN,
                id_objek=pinjaman.ID
            )





