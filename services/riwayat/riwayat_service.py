from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi_baca


class RiwayatService:

    SEMUA_KATEGORI = ["rekening", "pinjaman", "deposito", "transaksi"]
    @staticmethod
    def ambil_riwayat(norek, kategori):

        if kategori not in RiwayatService.SEMUA_KATEGORI:
            raise  ValueError(
                "Kategori riwayat tidak terdaftar"
            )

        with buat_koneksi_baca() as koneksi:

            data_rekening = RekeningRepository.cari_rekening_dengan_norek(
                norek=norek,
                koneksi=koneksi
            )
            if data_rekening is None:
                raise ValueError(
                    "Nomor Rekening Tidak Terdaftar"
                )
            data_riwayat = RiwayatRepository.cari_riwayat_dengan_kategori(
                norek=norek,
                kategori=kategori,
                koneksi=koneksi
            )


        return data_riwayat




