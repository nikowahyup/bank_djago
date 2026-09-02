import datetime

from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.core.notifikasi import Notifikasi
from bank_djago.core.pinjaman import Pinjaman
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas, StatusPinjaman, JenisReferensiID
from bank_djago.utils.validator import Validator





class PinjamanService:
    TENOR = {
        6: 0.10,
        12: 0.12,
        18: 0.13,
        24: 0.14,
    }

    MIN_PINJAMAN = 1_000_000
    MAX_PINJAMAN = 50_000_000
    BATAS_HARI_TUNGGAKAN = 7
    PERSENTASE_DENDA_HARIAN = 0.001
    MAKSIMAL_PERSENTASE_DENDA = 0.1

    @staticmethod
    def ajukan_pinjaman(nasabah, rekening, nominal, tenor):
        Validator.amankan_rekening(rekening)

        if rekening.pemilik is not nasabah:
            raise ValueError("Rekening bukan milik nasabah")

        if nominal < PinjamanService.MIN_PINJAMAN:
            raise ValueError("Nominal pinjaman di bawah batas minimal")

        if nominal > PinjamanService.MAX_PINJAMAN:
            raise ValueError("Nominal pinjaman melebihi batas maksimal")

        if tenor not in PinjamanService.TENOR:
            raise ValueError("Pilihan tenor pinjaman tidak tersedia")

        koneksi = buat_koneksi()

        try:
            pengajuan_aktif = (
                PinjamanRepository.cari_pengajuan_aktif_nasabah(
                    nik=nasabah.NIK,
                    koneksi=koneksi
                )
            )

            if pengajuan_aktif is not None:
                raise ValueError(
                    "Anda masih memiliki pengajuan pinjaman "
                    "yang sedang menunggu proses"
                )

            bunga = PinjamanService.TENOR[tenor]

            pinjaman = Pinjaman(
                pemilik=nasabah,
                rekening=rekening,
                nominal_pinjaman=nominal,
                bunga=bunga,
                tenor=tenor,
                id=None
            )

            id_pinjaman = PinjamanRepository.tambah_pinjaman(
                pinjaman=pinjaman,
                koneksi=koneksi
            )

            pinjaman.ID = id_pinjaman

            riwayat = RiwayatTemplate.template(
                kategori="transaksi",
                jenis="pinjaman",
                log=(
                    f"PENGAJUAN PINJAMAN | ID {pinjaman.ID} | "
                    f"Rp{Utilitas.format_rupiah(nominal)} | "
                    f"Tenor {tenor} bulan"
                )
            )

            audit = AuditService.tambah_audit(
                kategori="transaksi",
                jenis="pengajuan pinjaman",
                log=(
                    f"{nasabah.nama} mengajukan pinjaman "
                    f"sebesar Rp{Utilitas.format_rupiah(nominal)}"
                ),
                nama=nasabah.nama,
                nik=nasabah.NIK,
                norek=rekening.norek
            )

            RiwayatRepository.tambah_riwayat(
                norek=rekening.norek,
                riwayat=riwayat,
                koneksi=koneksi
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        nasabah.daftar_pinjaman.append(pinjaman)
        rekening.simpan_riwayat(riwayat)

        return pinjaman

    @staticmethod
    def setujui_pinjaman(id_pinjaman):
        koneksi = buat_koneksi()

        try:
            data_pinjaman = (
                PinjamanRepository.cari_pinjaman_dengan_id(
                    id_pinjaman=id_pinjaman,
                    koneksi=koneksi
                )
            )

            if data_pinjaman is None:
                raise ValueError(
                    f"Pinjaman ber-ID {id_pinjaman} tidak ditemukan"
                )

            if (
                    data_pinjaman["status"]
                    != StatusPinjaman.DIAJUKAN.value
            ):
                raise ValueError(
                    f"Pinjaman tidak dapat disetujui. "
                    f"Status saat ini: {data_pinjaman['status']}"
                )

            data_rekening = (
                RekeningRepository.cari_rekening_dengan_norek(
                    norek=data_pinjaman["norek"],
                    koneksi=koneksi
                )
            )

            if data_rekening is None:
                raise ValueError(
                    f"Rekening untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            data_nasabah = (
                NasabahRepository.cari_nasabah_dengan_nik(
                    nik=data_rekening["nik_pemilik"],
                    koneksi=koneksi
                )
            )

            if data_nasabah is None:
                raise ValueError(
                    f"Nasabah untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            status_baru = StatusPinjaman.DISETUJUI.value

            jumlah_baris = (
                PinjamanRepository.perbarui_status_pinjaman(
                    id_pinjaman=id_pinjaman,
                    status_baru=status_baru,
                    koneksi=koneksi
                )
            )

            if jumlah_baris != 1:
                raise ValueError(
                    "Gagal memperbarui status pinjaman"
                )

            audit = AuditService.tambah_audit(
                kategori="transaksi",
                jenis="persetujuan pinjaman",
                log=(
                    f"Pinjaman ber-ID {id_pinjaman} "
                    f"milik {data_nasabah['nama']} telah disetujui"
                ),
                nama=data_nasabah["nama"],
                nik=data_nasabah["nik"],
                norek=data_pinjaman["norek"]
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            # TODO: Simpan notifikasi persetujuan pinjaman
            # menggunakan koneksi transaksi yang sama.

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True




    @staticmethod
    def cairkan_pinjaman(bank,pinjaman,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        if pinjaman.status != StatusPinjaman.DISETUJUI:
            raise ValueError("Pinjaman masih belum disetujui")

        pinjaman.rekening.tambah_saldo(pinjaman.nominal_pinjaman)
        pinjaman.sisa_pokok = pinjaman.nominal_pinjaman
        persentase_bunga = pinjaman.bunga/12
        pinjaman.cicilan_tetap = round((pinjaman.nominal_pinjaman * persentase_bunga * ((1 + persentase_bunga) ** pinjaman.tenor)) / ((1 + persentase_bunga) ** pinjaman.tenor - 1))
        pinjaman.status = StatusPinjaman.AKTIF
        bunga_bulanan = round(pinjaman.sisa_pokok * persentase_bunga)
        pinjaman.bunga_bulanan = bunga_bulanan
        pinjaman.tanggal_pencairan = hari_ini
        pinjaman.tanggal_jatuh_tempo = Utilitas.tambah_bulan(pinjaman.tanggal_pencairan,1)




        AuditService.tambah_audit(bank,kategori='transaksi',jenis='pinjaman',log=f'{pinjaman.pemilik.nama} menerima pencairan pinjaman Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}',nik=pinjaman.pemilik.NIK,norek=pinjaman.rekening.norek)
        log = RiwayatTemplate.template(kategori="transaksi",jenis="pinjaman",log=f'PENCAIRAN PINJAMAN |  +Rp{Utilitas.format_rupiah(pinjaman.nominal_pinjaman)}')

        pinjaman.rekening.simpan_riwayat(log)

        return pinjaman

    @staticmethod
    def bayar_cicilan(bank, pinjaman,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        if pinjaman.status != StatusPinjaman.AKTIF:
            raise ValueError("Pinjaman sedang tidak aktif")

        if pinjaman.rekening.status == "tutup" or pinjaman.rekening.status == "blokir":
            raise ValueError("Pembayaran cicilan tidak dapat dilakukan menggunakan\n"
                             "rekening yang sedang diblokir atau sudah ditutup")


        tanggal_boleh_bayar = PinjamanService.tanggal_boleh_bayar(pinjaman)

        if hari_ini < tanggal_boleh_bayar:
            raise ValueError(f"Cicilan berikutnya baru boleh dibayar mulai "
                             f"{Utilitas.format_tanggal_indonesia(tanggal_boleh_bayar)}")


        denda = PinjamanService.hitung_denda(pinjaman,hari_ini)
        hari_terlambat = PinjamanService.hitung_hari_terlambat(pinjaman,hari_ini)
        total_bayar = pinjaman.cicilan_tetap + denda

        if pinjaman.rekening.saldo - total_bayar < pinjaman.rekening.saldosetor_min:
            raise ValueError("Saldo Anda tidak cukup untuk membayar cicilan dan denda")


        pinjaman.rekening.kurangi_saldo(total_bayar)

        persentase_bunga = pinjaman.bunga / 12

        bunga_bulanan = round(pinjaman.sisa_pokok * persentase_bunga)
        pokok_saja = pinjaman.cicilan_tetap - bunga_bulanan

        pinjaman.sisa_pokok -= pokok_saja
        pinjaman.cicilan_terbayar += 1

        pinjaman.bunga_bulanan = bunga_bulanan
        PinjamanService.hapus_notif_pinjaman(pinjaman.pemilik)

        # Pinjaman dinyatakan lunas ketika seluruh cicilan
        # telah dibayar atau sisa pokok telah habis.
        if (
                pinjaman.cicilan_terbayar >= pinjaman.tenor
                or pinjaman.sisa_pokok <= 0
        ):
            pinjaman.sisa_pokok = 0
            pinjaman.status = StatusPinjaman.LUNAS

            # Hapus referensi pinjaman aktif agar nasabah
            # dapat mengajukan pinjaman baru.
            pinjaman.pemilik.pinjaman = None

            log_audit = (
                f"{pinjaman.pemilik.nama} telah melunasi "
                f"pinjaman {pinjaman.ID} "
                f"sebesar Rp"
                f"{Utilitas.format_rupiah(round(total_bayar))}"
            )

            log_riwayat = (
                f"PELUNASAN PINJAMAN | "
                f"Cicilan Rp"
                f"{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))} | "
                f"Denda Rp{Utilitas.format_rupiah(denda)} | "
                f"Terlambat {hari_terlambat} hari | "
                f"Total Rp"
                f"{Utilitas.format_rupiah(round(total_bayar))}"
            )

            nasabah = pinjaman.pemilik

            PinjamanService.hapus_notif_pinjaman(nasabah)

            notifikasi = Notifikasi(
                jenis="pinjaman",
                pesan=(
                    "🎉 Pinjaman Anda telah lunas. "
                    "Terima kasih telah mempercayai Bank Djago"
                ),
                referensi_id=JenisReferensiID.PINJAMAN,
                id_objek=pinjaman.ID
            )

            nasabah.notifikasi.append(notifikasi)

        else:
            pinjaman.tanggal_jatuh_tempo = Utilitas.tambah_bulan(
                pinjaman.tanggal_jatuh_tempo,
                1
            )

            pinjaman.notifikasi_jatuh_tempo = False

            log_audit = (
                f"{pinjaman.pemilik.nama} membayar cicilan "
                f"pinjaman {pinjaman.ID} "
                f"sebesar Rp{Utilitas.format_rupiah(round(total_bayar))}"
            )

            log_riwayat = (
                f"PEMBAYARAN CICILAN | "
                f"Cicilan Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))} | "
                f"Denda Rp{Utilitas.format_rupiah(denda)} | "
                f"Terlambat {hari_terlambat} hari | "
                f"Total Rp{Utilitas.format_rupiah(round(total_bayar))}"
            )

        AuditService.tambah_audit(
            bank,
            kategori="transaksi",
            jenis="pinjaman",
            log=log_audit,
            nik=pinjaman.pemilik.NIK,
            norek=pinjaman.rekening.norek
        )

        pinjaman.rekening.simpan_riwayat(
            RiwayatTemplate.template(
                kategori="transaksi",
                jenis="pinjaman",
                log=log_riwayat
            )
        )
        return pinjaman




    @staticmethod
    def tolak_pinjaman(id_pinjaman,catatan_admin):
        catatan_admin = catatan_admin.strip()
        if not catatan_admin:
            raise ValueError("Catatan tidak boleh kosong")
        koneksi = buat_koneksi()

        try:
            data_pinjaman = (
                PinjamanRepository.cari_pinjaman_dengan_id(
                    id_pinjaman=id_pinjaman,
                    koneksi=koneksi
                )
            )

            if data_pinjaman is None:
                raise ValueError(
                    f"Pinjaman ber-ID {id_pinjaman} tidak ditemukan"
                )

            if (
                    data_pinjaman["status"]
                    != StatusPinjaman.DIAJUKAN.value
            ):
                raise ValueError(
                    f"Pinjaman tidak dapat ditolak. "
                    f"Status saat ini: {data_pinjaman['status']}"
                )

            data_rekening = (
                RekeningRepository.cari_rekening_dengan_norek(
                    norek=data_pinjaman["norek"],
                    koneksi=koneksi
                )
            )

            if data_rekening is None:
                raise ValueError(
                    f"Rekening untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            data_nasabah = (
                NasabahRepository.cari_nasabah_dengan_nik(
                    nik=data_rekening["nik_pemilik"],
                    koneksi=koneksi
                )
            )

            if data_nasabah is None:
                raise ValueError(
                    f"Nasabah untuk pinjaman ber-ID "
                    f"{id_pinjaman} tidak ditemukan"
                )

            status_baru = StatusPinjaman.DITOLAK.value

            jumlah_baris = (
                PinjamanRepository.perbarui_status_pinjaman(
                    id_pinjaman=id_pinjaman,
                    status_baru=status_baru,
                    koneksi=koneksi,
                    catatan=catatan_admin

                )
            )

            if jumlah_baris != 1:
                raise ValueError(
                    "Gagal memperbarui status pinjaman"
                )

            audit = AuditService.tambah_audit(
                kategori="transaksi",
                jenis="penolakan pinjaman",
                log=(
                    f"Pinjaman ber-ID {id_pinjaman} "
                    f"milik {data_nasabah['nama']} telah ditolak.\n"
                    f"Catatan admin: {catatan_admin}"
                ),
                nama=data_nasabah["nama"],
                nik=data_nasabah["nik"],
                norek=data_pinjaman["norek"]
            )

            AuditRepository.tambah_audit(
                audit=audit,
                koneksi=koneksi
            )

            # TODO: Simpan notifikasi persetujuan pinjaman
            # menggunakan koneksi transaksi yang sama.

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        return True











    @staticmethod
    def hapus_notif_pinjaman(nasabah):
        for item in nasabah.notifikasi:
            if item.referensi_id == JenisReferensiID.PINJAMAN:
                nasabah.notifikasi.remove(item)
                break


    @staticmethod
    def daftar_ajuan(bank):
        return [ajuan for ajuan in bank.daftar_pinjaman if ajuan.status == StatusPinjaman.DIAJUKAN]

    @staticmethod
    def tanggal_boleh_bayar(pinjaman):
        if pinjaman.cicilan_terbayar == 0:
            return pinjaman.tanggal_pencairan

        jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
            pinjaman.tanggal_pencairan,
            1
        )

        for _ in range(pinjaman.cicilan_terbayar - 1):
            jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
                jatuh_tempo_sebelumnya,
                1
            )

        return jatuh_tempo_sebelumnya + datetime.timedelta(days=1)

    @staticmethod
    def hitung_hari_terlambat(pinjaman,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        return  max(0,(hari_ini - pinjaman.tanggal_jatuh_tempo).days)


    @staticmethod
    def hitung_denda(pinjaman,hari_ini=None):
        hari_terlambat = PinjamanService.hitung_hari_terlambat(pinjaman, hari_ini)

        hari_denda = max(0,hari_terlambat-PinjamanService.BATAS_HARI_TUNGGAKAN)

        denda = pinjaman.cicilan_tetap*hari_denda*PinjamanService.PERSENTASE_DENDA_HARIAN

        denda_maksimal = pinjaman.cicilan_tetap*PinjamanService.MAKSIMAL_PERSENTASE_DENDA

        return round(min(denda,denda_maksimal))







