import datetime
from bank_djago.penyimpanan.repositories.nasabah_repository import NasabahRepository
from bank_djago.core.pinjaman import Pinjaman
from bank_djago.penyimpanan.repositories.audit_repository import AuditRepository
from bank_djago.penyimpanan.repositories.pinjaman_repository import PinjamanRepository
from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
from bank_djago.penyimpanan.repositories.riwayat_repository import RiwayatRepository
from bank_djago.penyimpanan.repositories.transaksi_repository import TransaksiRepository
from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.services.admin.audit_service import AuditService
from bank_djago.services.transaksi.riwayat.riwayat_template import RiwayatTemplate
from bank_djago.utils.utility import Utilitas, StatusPinjaman, JenisReferensi, JenisTransaksi
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
    def cairkan_pinjaman(nasabah, id_pinjaman,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        if nasabah is None:
            raise ValueError("Nasabah tidak tersedia")

        if not isinstance(id_pinjaman, int):
            raise TypeError("ID pinjaman harus berupa angka")

        if id_pinjaman <= 0:
            raise ValueError("ID pinjaman tidak valid")


        koneksi = buat_koneksi()
        try:
            data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(id_pinjaman, koneksi)

            if data_pinjaman is None:
                raise   ValueError("Pinjaman tidak ditemukan")

            if data_pinjaman['status'] != StatusPinjaman.DISETUJUI.value:
                raise ValueError("Pinjaman belum disetujui")

            data_rekening = RekeningRepository.cari_rekening_dengan_norek(data_pinjaman["norek"], koneksi)

            if data_rekening is None:
                raise ValueError("Rekening untuk pinjaman ini tidak ditemukan")

            if data_rekening["nik_pemilik"] != nasabah.NIK:
                raise ValueError("Nasabah ini tidak terdaftar sebagai pemilik pinjaman")

            rekening = next((rekening for rekening in nasabah.rekening if rekening.norek == data_rekening['norek']),None)
            if rekening is None:
                raise ValueError("Rekening pinjaman tidak ditemukan pada data nasabah")
            if rekening.pemilik is not nasabah:
                raise ValueError("Pemilik objek rekening tidak sesuai")

            Validator.amankan_rekening(rekening)

            pinjaman = next((pinjaman for pinjaman in nasabah.daftar_pinjaman if pinjaman.ID == id_pinjaman),None)

            if pinjaman is None:
                raise ValueError("Objek pinjaman tidak ditemukan pada data nasabah")

            if pinjaman.pemilik is not nasabah:
                raise ValueError("Pinjaman tidak terdaftar di daftar pinjaman nasabah")

            if pinjaman.rekening is not rekening:
                raise ValueError("Objek rekening pada pinjaman tidak sesuai")

            bunga = data_pinjaman['bunga']
            tenor = data_pinjaman['tenor']
            nominal_pinjaman = data_pinjaman['nominal_pinjaman']
            persentase_bunga = bunga / 12
            sisa_pokok = nominal_pinjaman

            saldo_sebelum = data_rekening['saldo']
            saldo_baru = saldo_sebelum + nominal_pinjaman
            cicilan_tetap = round((nominal_pinjaman * persentase_bunga * ((1 + persentase_bunga) ** tenor)) /
                                  ((1 + persentase_bunga) ** tenor - 1))

            status_baru = StatusPinjaman.AKTIF
            tanggal_pencairan = hari_ini
            tanggal_jatuh_tempo = Utilitas.tambah_bulan(tanggal_pencairan,1)

            jumlah_baris = PinjamanRepository.perbarui_setelah_pencairan(
                                                                         id_pinjaman=id_pinjaman,
                                                                         cicilan_tetap_baru=cicilan_tetap,
                                                                         tanggal_jatuh_tempo_baru=tanggal_jatuh_tempo,
                                                                         tanggal_pencairan_baru=tanggal_pencairan,
                                                                            sisa_pokok_baru=sisa_pokok,
                                                                         status_baru=status_baru,
                                                                         koneksi=koneksi
                                                                         )

            if jumlah_baris != 1:
                raise ValueError('Gagal memperbarui status pinjaman')


            jumlah_baris_rek = RekeningRepository.perbarui_saldo(norek=data_rekening['norek'],saldo_baru=saldo_baru,koneksi=koneksi)

            if jumlah_baris_rek != 1:
                raise ValueError("Gagal menambah saldo rekening")

            transaksi = {"jenis":JenisTransaksi.PENCAIRAN_PINJAMAN,
                         "norek_tujuan":rekening.norek,
                         "nominal": nominal_pinjaman,
                         "saldo_tujuan_sebelum":saldo_sebelum,
                         "saldo_tujuan_sesudah":saldo_baru,
                         "jenis_referensi":JenisReferensi.PINJAMAN,
                         "id_referensi":id_pinjaman,
                         "waktu":datetime.datetime.now()}

            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi,koneksi)

            riwayat = RiwayatTemplate.template(kategori="transaksi",jenis='pencairan pinjaman',log=f"PENCAIRAN PINJAMAN {id_pinjaman} | +Rp{Utilitas.format_rupiah(nominal_pinjaman)}")
            audit = AuditService.tambah_audit(kategori="transaksi",jenis='pencairan pinjaman',log=f"Nasabah {nasabah.nama} mencairkan pinjaman {id_pinjaman}",nama=nasabah.nama,nik=nasabah.NIK,norek=rekening.norek)

            RiwayatRepository.tambah_riwayat(norek=rekening.norek, riwayat=riwayat, koneksi=koneksi, id_transaksi=id_transaksi)
            AuditRepository.tambah_audit(audit=audit, koneksi=koneksi, id_transaksi=id_transaksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        pinjaman.cicilan_tetap = cicilan_tetap
        pinjaman.tanggal_pencairan = tanggal_pencairan
        pinjaman.status = status_baru
        pinjaman.tanggal_jatuh_tempo = tanggal_jatuh_tempo
        pinjaman.sisa_pokok = sisa_pokok
        rekening.set_saldo(saldo_baru)
        rekening.simpan_riwayat(riwayat)

        return pinjaman




    @staticmethod
    def bayar_cicilan(nasabah,id_pinjaman,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()

        if nasabah is None:
            raise ValueError("Nasabah tidak tersedia")

        if not isinstance(id_pinjaman, int):
            raise TypeError("ID pinjaman harus berupa angka")

        if id_pinjaman <= 0:
            raise ValueError("ID pinjaman tidak valid")


        koneksi = buat_koneksi()

        try:
            data_pinjaman = PinjamanRepository.cari_pinjaman_dengan_id(id_pinjaman, koneksi)

            if data_pinjaman is None:
                raise ValueError("Pinjaman tidak ditemukan")

            if data_pinjaman['status'] != StatusPinjaman.AKTIF.value:
                raise ValueError("Pinjaman sedang tidak aktif")

            data_rekening = RekeningRepository.cari_rekening_dengan_norek(data_pinjaman["norek"], koneksi)

            if data_rekening is None:
                raise ValueError("Rekening untuk pinjaman ini tidak ditemukan")

            if data_rekening["nik_pemilik"] != nasabah.NIK:
                raise ValueError("Nasabah ini tidak terdaftar sebagai pemilik pinjaman")

            rekening = next((rekening for rekening in nasabah.rekening if rekening.norek == data_rekening['norek']),
                            None)
            if rekening is None:
                raise ValueError("Rekening pinjaman tidak ditemukan pada data nasabah")
            if rekening.pemilik is not nasabah:
                raise ValueError("Pemilik objek rekening tidak sesuai")

            Validator.amankan_rekening(rekening)

            pinjaman = next((pinjaman for pinjaman in nasabah.daftar_pinjaman if pinjaman.ID == id_pinjaman), None)

            if pinjaman is None:
                raise ValueError("Objek pinjaman tidak ditemukan pada data nasabah")

            if pinjaman.pemilik is not nasabah:
                raise ValueError("Pinjaman tidak terdaftar di daftar pinjaman nasabah")

            if pinjaman.rekening is not rekening:
                raise ValueError("Objek rekening pada pinjaman tidak sesuai")

            if data_pinjaman["sisa_pokok"] <= 0:
                raise ValueError("Pinjaman tidak memiliki sisa pokok")

            if data_pinjaman["cicilan_terbayar"] >= data_pinjaman["tenor"]:
                raise ValueError("Seluruh cicilan pinjaman telah dibayar")

            if data_pinjaman["tanggal_pencairan"] is None:
                raise ValueError("Pinjaman belum memiliki tanggal pencairan")

            if data_pinjaman["tanggal_jatuh_tempo"] is None:
                raise ValueError("Jadwal pembayaran pinjaman belum tersedia")

            norek = data_rekening['norek']
            saldo_sebelum = data_rekening["saldo"]

            tenor = data_pinjaman["tenor"]
            bunga = data_pinjaman["bunga"]
            cicilan_tetap = data_pinjaman["cicilan_tetap"]
            cicilan_terbayar = data_pinjaman["cicilan_terbayar"]
            sisa_pokok = data_pinjaman["sisa_pokok"]

            tanggal_pencairan = datetime.date.fromisoformat(
                data_pinjaman["tanggal_pencairan"]
            )

            tanggal_jatuh_tempo = datetime.date.fromisoformat(
                data_pinjaman["tanggal_jatuh_tempo"]
            )


            tanggal_boleh_bayar = PinjamanService.tanggal_boleh_bayar(
                                                    cicilan_terbayar=cicilan_terbayar,
                                                    tanggal_pencairan=tanggal_pencairan)

            if hari_ini < tanggal_boleh_bayar:
                raise ValueError(f"Cicilan selanjutnya baru boleh dibayar mulai "
                                 f"{Utilitas.format_tanggal_indonesia(tanggal_boleh_bayar)}")

            hari_terlambat = PinjamanService.hitung_hari_terlambat(tanggal_jatuh_tempo, hari_ini)

            denda = PinjamanService.hitung_denda(
                    tanggal_jatuh_tempo=tanggal_jatuh_tempo,
                    cicilan_tetap=cicilan_tetap,
                    hari_ini=hari_ini)

            persentase_bunga = bunga / 12
            total_bayar = cicilan_tetap + denda
            bunga_bulanan = round(sisa_pokok * persentase_bunga)
            pokok_saja = cicilan_tetap - bunga_bulanan
            saldo_baru = saldo_sebelum - total_bayar


            if saldo_baru < rekening.saldosetor_min:
                raise ValueError("Saldo tidak cukup untuk membayar cicilan dan denda")

            cicilan_terbayar_baru = cicilan_terbayar + 1

            pinjaman_lunas = cicilan_terbayar_baru >= tenor

            if pinjaman_lunas:

                status_baru = StatusPinjaman.LUNAS
                sisa_pokok_baru = 0
                tanggal_jatuh_tempo_baru = tanggal_jatuh_tempo

                log_audit = (
                    f"{nasabah.nama} telah melunasi "
                    f"pinjaman {id_pinjaman} "
                    f"sebesar Rp"
                    f"{Utilitas.format_rupiah(total_bayar)}"
                )

                log_riwayat = (
                    f"PELUNASAN PINJAMAN | "
                    f"Cicilan Rp"
                    f"{Utilitas.format_rupiah(cicilan_tetap)} | "
                    f"Denda Rp{Utilitas.format_rupiah(denda)} | "
                    f"Terlambat {hari_terlambat} hari | "
                    f"Total Rp"
                    f"{Utilitas.format_rupiah(total_bayar)}"
                )

            else:

                sisa_pokok_baru = sisa_pokok - pokok_saja
                status_baru = StatusPinjaman.AKTIF
                tanggal_jatuh_tempo_baru = Utilitas.tambah_bulan(tanggal_jatuh_tempo, 1)

                log_audit = (
                    f"{nasabah.nama} membayar cicilan "
                    f"pinjaman {id_pinjaman} "
                    f"sebesar Rp{Utilitas.format_rupiah(total_bayar)}"
                )

                log_riwayat = (
                    f"PEMBAYARAN CICILAN | "
                    f"Cicilan Rp{Utilitas.format_rupiah(cicilan_tetap)} | "
                    f"Denda Rp{Utilitas.format_rupiah(denda)} | "
                    f"Terlambat {hari_terlambat} hari | "
                    f"Total Rp{Utilitas.format_rupiah(total_bayar)}"
                )

            jumlah_baris_rek = RekeningRepository.perbarui_saldo(norek, saldo_baru, koneksi)
            if jumlah_baris_rek != 1:
                raise ValueError("Gagal melakukan pembayaran cicilan")

            jumlah_baris_pin = PinjamanRepository.perbarui_setelah_pembayaran(id_pinjaman=id_pinjaman,
                                                                          status_baru=status_baru,
                                                                          cicilan_terbayar_baru=cicilan_terbayar_baru,
                                                                          sisa_pokok_baru=sisa_pokok_baru,
                                                                          tanggal_jatuh_tempo_baru=tanggal_jatuh_tempo_baru,
                                                                          koneksi=koneksi)
            if jumlah_baris_pin != 1:
                raise ValueError("Gagal memperbarui status pinjaman")

            transaksi = {"jenis": JenisTransaksi.PEMBAYARAN_CICILAN,
                         "norek_sumber": norek,
                         "nominal": cicilan_tetap,
                         "biaya": denda,
                         "saldo_sumber_sebelum": saldo_sebelum,
                         "saldo_sumber_sesudah": saldo_baru,
                         "jenis_referensi": JenisReferensi.PINJAMAN,
                         "id_referensi": id_pinjaman,
                         "waktu": datetime.datetime.now()}

            audit = AuditService.tambah_audit(kategori='transaksi', jenis='pembayaran cicilan', log=log_audit,
                                              nama=nasabah.nama, nik=nasabah.NIK, norek=norek)
            riwayat = RiwayatTemplate.template(kategori='transaksi', jenis='pembayaran cicilan', log=log_riwayat)

            id_transaksi = TransaksiRepository.tambah_transaksi(transaksi,koneksi)
            RiwayatRepository.tambah_riwayat(norek, riwayat, koneksi, id_transaksi)
            AuditRepository.tambah_audit(audit, koneksi, id_transaksi)

            koneksi.commit()

        except Exception:
            koneksi.rollback()
            raise

        finally:
            koneksi.close()

        pinjaman.status = status_baru
        pinjaman.sisa_pokok = sisa_pokok_baru
        pinjaman.cicilan_terbayar = cicilan_terbayar_baru
        pinjaman.tanggal_jatuh_tempo = tanggal_jatuh_tempo_baru
        rekening.set_saldo(saldo_baru)
        rekening.simpan_riwayat(riwayat)
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
            if item.referensi_id == JenisReferensi.PINJAMAN:
                nasabah.notifikasi.remove(item)
                break


    @staticmethod
    def daftar_ajuan(bank):
        return [ajuan for ajuan in bank.daftar_pinjaman if ajuan.status == StatusPinjaman.DIAJUKAN]

    @staticmethod
    def tanggal_boleh_bayar(cicilan_terbayar,tanggal_pencairan):

        if cicilan_terbayar == 0:
            return tanggal_pencairan

        jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
            tanggal_pencairan,
            1
        )

        for _ in range(cicilan_terbayar - 1):
            jatuh_tempo_sebelumnya = Utilitas.tambah_bulan(
                jatuh_tempo_sebelumnya,
                1
            )

        return (
                jatuh_tempo_sebelumnya
                + datetime.timedelta(days=1)
        )

    @staticmethod
    def hitung_hari_terlambat(tanggal_jatuh_tempo,hari_ini=None):
        if hari_ini is None:
            hari_ini = datetime.date.today()
        return  max(0,(hari_ini - tanggal_jatuh_tempo).days)


    @staticmethod
    def hitung_denda(tanggal_jatuh_tempo,cicilan_tetap,hari_ini=None):
        hari_terlambat = PinjamanService.hitung_hari_terlambat(tanggal_jatuh_tempo, hari_ini)

        hari_denda = max(0,hari_terlambat-PinjamanService.BATAS_HARI_TUNGGAKAN)

        denda = cicilan_tetap*hari_denda*PinjamanService.PERSENTASE_DENDA_HARIAN

        denda_maksimal =cicilan_tetap*PinjamanService.MAKSIMAL_PERSENTASE_DENDA

        return round(min(denda,denda_maksimal))


# log_audit = (
#     f"{pinjaman.pemilik.nama} membayar cicilan "
#     f"pinjaman {pinjaman.ID} "
#     f"sebesar Rp{Utilitas.format_rupiah(round(total_bayar))}"
# )
#
# log_riwayat = (
#     f"PEMBAYARAN CICILAN | "
#     f"Cicilan Rp{Utilitas.format_rupiah(round(pinjaman.cicilan_tetap))} | "
#     f"Denda Rp{Utilitas.format_rupiah(denda)} | "
#     f"Terlambat {hari_terlambat} hari | "
#     f"Total Rp{Utilitas.format_rupiah(round(total_bayar))}"
# )

