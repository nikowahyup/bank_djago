# # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # #     RekeningRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
# # # # # # #     PengajuanRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # #     AuditRepository
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # # NOREK = "4001518075450587"
# # # # # # # #
# # # # # # # # data_rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
# # # # # # # #
# # # # # # # # pengajuan = PengajuanRepository.cari_pengajuan_aktif(
# # # # # # # #     norek=NOREK,
# # # # # # # #     jenis="tutup"
# # # # # # # # )
# # # # # # # #
# # # # # # # # daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
# # # # # # # #
# # # # # # # #
# # # # # # # # print("STATE REKENING")
# # # # # # # # print("Norek  :", data_rekening["norek"])
# # # # # # # # print("Level  :", data_rekening["level"])
# # # # # # # # print("Saldo  :", data_rekening["saldo"])
# # # # # # # # print("Status :", data_rekening["status"])
# # # # # # # #
# # # # # # # # print()
# # # # # # # # print("PENGAJUAN PENUTUPAN")
# # # # # # # #
# # # # # # # # if pengajuan is None:
# # # # # # # #     print("Pengajuan tidak ditemukan")
# # # # # # # # else:
# # # # # # # #     print("ID                :", pengajuan["id"])
# # # # # # # #     print("Norek             :", pengajuan["norek"])
# # # # # # # #     print("Jenis             :", pengajuan["jenis"])
# # # # # # # #     print("Alasan            :", pengajuan["alasan"])
# # # # # # # #     print("Status            :", pengajuan["status"])
# # # # # # # #     print("Waktu pengajuan   :", pengajuan["waktu_pengajuan"])
# # # # # # # #     print("Waktu diproses    :", pengajuan["waktu_diproses"])
# # # # # # # #     print("Catatan admin     :", pengajuan["catatan_admin"])
# # # # # # # #
# # # # # # # # print()
# # # # # # # # print("AUDIT TERBARU")
# # # # # # # #
# # # # # # # # if daftar_audit:
# # # # # # # #     audit_terbaru = daftar_audit[0]
# # # # # # # #
# # # # # # # #     print("ID       :", audit_terbaru["id"])
# # # # # # # #     print("Kategori :", audit_terbaru["kategori"])
# # # # # # # #     print("Jenis    :", audit_terbaru["jenis"])
# # # # # # # #     print("Waktu    :", audit_terbaru["waktu"])
# # # # # # # #     print("Log      :", audit_terbaru["log"])
# # # # # # # #     print("Nama     :", audit_terbaru["nama"])
# # # # # # # #     print("NIK      :", audit_terbaru["nik"])
# # # # # # # #     print("Norek    :", audit_terbaru["norek"])
# # # # # # # # else:
# # # # # # # #     print("Audit tidak ditemukan")
# # # # # # # #
# # # # # # # #
# # # # # # # # assert data_rekening is not None
# # # # # # # # assert data_rekening["status"] == "aktif"
# # # # # # # #
# # # # # # # # assert pengajuan is not None
# # # # # # # # assert pengajuan["norek"] == NOREK
# # # # # # # # assert pengajuan["jenis"] == "tutup"
# # # # # # # # assert pengajuan["status"] == "diajukan"
# # # # # # # # assert pengajuan["waktu_diproses"] is None
# # # # # # # # assert pengajuan["catatan_admin"] is None
# # # # # # # #
# # # # # # # # assert daftar_audit
# # # # # # # # assert daftar_audit[0]["jenis"] == "pengajuan penutupan"
# # # # # # # # assert daftar_audit[0]["norek"] == NOREK
# # # # # # # #
# # # # # # # # print()
# # # # # # # # print("✅ Pengajuan penutupan berhasil disimpan")
# # # # # # # # print("✅ Rekening tetap aktif selama menunggu admin")
# # # # # # # # print("✅ Waktu proses dan catatan admin masih kosong")
# # # # # # # # print("✅ Audit pengajuan berhasil disimpan")
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # # # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
# # # # # # #     PengajuanRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # #     RekeningRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # #     AuditRepository
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # ID_PENGAJUAN = 1
# # # # # # # NOREK = "4001518075450587"
# # # # # # #
# # # # # # #
# # # # # # # pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
# # # # # # #     ID_PENGAJUAN
# # # # # # # )
# # # # # # #
# # # # # # # rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # #     NOREK
# # # # # # # )
# # # # # # #
# # # # # # # daftar_audit = AuditRepository.cari_audit_dengan_norek(
# # # # # # #     NOREK
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # print("KONDISI PENGAJUAN")
# # # # # # #
# # # # # # # if pengajuan is None:
# # # # # # #     raise AssertionError("Pengajuan tidak ditemukan")
# # # # # # #
# # # # # # # print("ID                :", pengajuan["id"])
# # # # # # # print("Norek             :", pengajuan["norek"])
# # # # # # # print("Jenis             :", pengajuan["jenis"])
# # # # # # # print("Alasan            :", pengajuan["alasan"])
# # # # # # # print("Status            :", pengajuan["status"])
# # # # # # # print("Waktu pengajuan   :", pengajuan["waktu_pengajuan"])
# # # # # # # print("Waktu diproses    :", pengajuan["waktu_diproses"])
# # # # # # # print("Catatan admin     :", pengajuan["catatan_admin"])
# # # # # # #
# # # # # # #
# # # # # # # print()
# # # # # # # print("KONDISI REKENING")
# # # # # # #
# # # # # # # if rekening is None:
# # # # # # #     raise AssertionError("Rekening tidak ditemukan")
# # # # # # #
# # # # # # # print("Norek  :", rekening["norek"])
# # # # # # # print("Saldo  :", rekening["saldo"])
# # # # # # # print("Level  :", rekening["level"])
# # # # # # # print("Status :", rekening["status"])
# # # # # # #
# # # # # # #
# # # # # # # print()
# # # # # # # print("AUDIT TERBARU")
# # # # # # #
# # # # # # # if not daftar_audit:
# # # # # # #     raise AssertionError("Audit rekening tidak ditemukan")
# # # # # # #
# # # # # # # audit_terbaru = daftar_audit[0]
# # # # # # #
# # # # # # # print("ID       :", audit_terbaru["id"])
# # # # # # # print("Kategori :", audit_terbaru["kategori"])
# # # # # # # print("Jenis    :", audit_terbaru["jenis"])
# # # # # # # print("Waktu    :", audit_terbaru["waktu"])
# # # # # # # print("Log      :", audit_terbaru["log"])
# # # # # # # print("Nama     :", audit_terbaru["nama"])
# # # # # # # print("NIK      :", audit_terbaru["nik"])
# # # # # # # print("Norek    :", audit_terbaru["norek"])
# # # # # # #
# # # # # # #
# # # # # # # assert pengajuan["id"] == ID_PENGAJUAN
# # # # # # # assert pengajuan["norek"] == NOREK
# # # # # # # assert pengajuan["jenis"] == "tutup"
# # # # # # # assert pengajuan["status"] == "ditolak"
# # # # # # # assert pengajuan["waktu_diproses"] is not None
# # # # # # # assert pengajuan["catatan_admin"] is not None
# # # # # # # assert pengajuan["catatan_admin"].strip() != ""
# # # # # # #
# # # # # # # assert rekening["status"] == "aktif"
# # # # # # #
# # # # # # # assert audit_terbaru["kategori"] == "rekening"
# # # # # # # assert audit_terbaru["jenis"] == "penolakan pengajuan"
# # # # # # # assert audit_terbaru["norek"] == NOREK
# # # # # # #
# # # # # # # print()
# # # # # # # print("✅ Status pengajuan berhasil berubah menjadi ditolak")
# # # # # # # print("✅ Waktu proses dan catatan admin berhasil disimpan")
# # # # # # # print("✅ Rekening tetap aktif setelah pengajuan ditolak")
# # # # # # # print("✅ Audit penolakan berhasil disimpan")
# # # # # # #
# # # # # # #
# # # # # # #
# # # # # #
# # # # # # # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository  import (
# # # # # # #     PengajuanRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # #     RekeningRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # #     AuditRepository
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # ID_PENGAJUAN = 2
# # # # # # # NOREK = "4001518075450587"
# # # # # # #
# # # # # # #
# # # # # # # pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(ID_PENGAJUAN)
# # # # # # # rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
# # # # # # # daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
# # # # # # # daftar_pending = PengajuanRepository.cari_semua_pengajuan_diajukan()
# # # # # # #
# # # # # # #
# # # # # # # print("HASIL PENGAJUAN")
# # # # # # # print("ID               :", pengajuan["id"])
# # # # # # # print("Jenis            :", pengajuan["jenis"])
# # # # # # # print("Status           :", pengajuan["status"])
# # # # # # # print("Waktu diproses   :", pengajuan["waktu_diproses"])
# # # # # # # print("Catatan admin    :", pengajuan["catatan_admin"])
# # # # # # #
# # # # # # # print()
# # # # # # # print("KONDISI REKENING")
# # # # # # # print("Norek            :", rekening["norek"])
# # # # # # # print("Status rekening  :", rekening["status"])
# # # # # # # print("Saldo            :", rekening["saldo"])
# # # # # # #
# # # # # # # print()
# # # # # # # print("AUDIT TERBARU")
# # # # # # # audit_terbaru = daftar_audit[0]
# # # # # # #
# # # # # # # print("Jenis            :", audit_terbaru["jenis"])
# # # # # # # print("Log              :", audit_terbaru["log"])
# # # # # # # print("NIK              :", audit_terbaru["nik"])
# # # # # # # print("Norek            :", audit_terbaru["norek"])
# # # # # # #
# # # # # # # print()
# # # # # # # print("PENGAJUAN YANG MASIH MENUNGGU")
# # # # # # # print("Jumlah           :", len(daftar_pending))
# # # # # # #
# # # # # # #
# # # # # # # assert pengajuan["status"] == "disetujui"
# # # # # # # assert pengajuan["waktu_diproses"] is not None
# # # # # # # assert pengajuan["catatan_admin"] is not None
# # # # # # # assert rekening["status"] == "aktif"
# # # # # # # assert audit_terbaru["jenis"] == "persetujuan pengajuan"
# # # # # # # assert all(data["id"] != ID_PENGAJUAN for data in daftar_pending)
# # # # # # #
# # # # # # # print()
# # # # # # # print("✅ Status pengajuan berhasil diubah menjadi disetujui")
# # # # # # # print("✅ Waktu proses dan catatan admin berhasil disimpan")
# # # # # # # print("✅ Rekening tetap aktif sampai penutupan diselesaikan nasabah")
# # # # # # # print("✅ Audit persetujuan berhasil disimpan")
# # # # # # # print("✅ Pengajuan tidak lagi muncul dalam daftar yang menunggu")
# # # # # #
# # # # # #
# # # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # # #     RekeningRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository  import (
# # # # # # #     PengajuanRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.riwayat_repository import (
# # # # # # #     RiwayatRepository
# # # # # # # )
# # # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # # #     AuditRepository
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # NOREK = "4001518075450587"
# # # # # # # ID_PENGAJUAN = 2
# # # # # # #
# # # # # # #
# # # # # # # data_rekening = RekeningRepository.cari_rekening_dengan_norek(NOREK)
# # # # # # #
# # # # # # # data_pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
# # # # # # #     ID_PENGAJUAN
# # # # # # # )
# # # # # # #
# # # # # # # daftar_riwayat = RiwayatRepository.cari_seluruh_riwayat(NOREK)
# # # # # # #
# # # # # # # daftar_audit = AuditRepository.cari_audit_dengan_norek(NOREK)
# # # # # # #
# # # # # # #
# # # # # # # print("KONDISI REKENING SETELAH PENUTUPAN")
# # # # # # # print("Norek   :", data_rekening["norek"])
# # # # # # # print("Saldo   :", data_rekening["saldo"])
# # # # # # # print("Status  :", data_rekening["status"])
# # # # # # #
# # # # # # #
# # # # # # # print()
# # # # # # # print("KONDISI PENGAJUAN")
# # # # # # # print("ID              :", data_pengajuan["id"])
# # # # # # # print("Jenis           :", data_pengajuan["jenis"])
# # # # # # # print("Status          :", data_pengajuan["status"])
# # # # # # # print("Waktu diproses  :", data_pengajuan["waktu_diproses"])
# # # # # # # print("Catatan admin   :", data_pengajuan["catatan_admin"])
# # # # # # #
# # # # # # #
# # # # # # # print()
# # # # # # # print("RIWAYAT TERBARU")
# # # # # # #
# # # # # # # riwayat_terbaru = daftar_riwayat[0]
# # # # # # #
# # # # # # # print("Kategori :", riwayat_terbaru["kategori"])
# # # # # # # print("Jenis    :", riwayat_terbaru["jenis"])
# # # # # # # print("Waktu    :", riwayat_terbaru["waktu"])
# # # # # # # print("Log      :", riwayat_terbaru["log"])
# # # # # # #
# # # # # # #
# # # # # # # print()
# # # # # # # print("AUDIT TERBARU")
# # # # # # #
# # # # # # # audit_terbaru = daftar_audit[0]
# # # # # # #
# # # # # # # print("Kategori :", audit_terbaru["kategori"])
# # # # # # # print("Jenis    :", audit_terbaru["jenis"])
# # # # # # # print("Waktu    :", audit_terbaru["waktu"])
# # # # # # # print("Log      :", audit_terbaru["log"])
# # # # # # # print("Nama     :", audit_terbaru["nama"])
# # # # # # # print("NIK      :", audit_terbaru["nik"])
# # # # # # # print("Norek    :", audit_terbaru["norek"])
# # # # # # #
# # # # # # #
# # # # # # # assert data_rekening["saldo"] == 0
# # # # # # # assert data_rekening["status"] == "tutup"
# # # # # # #
# # # # # # # assert data_pengajuan["id"] == ID_PENGAJUAN
# # # # # # # assert data_pengajuan["jenis"] == "tutup"
# # # # # # # assert data_pengajuan["status"] == "disetujui"
# # # # # # #
# # # # # # # assert riwayat_terbaru["jenis"] == "penutupan rekening"
# # # # # # # assert audit_terbaru["jenis"] == "penutupan tarik saldo"
# # # # # # #
# # # # # # #
# # # # # # # print()
# # # # # # # print("✅ Saldo rekening berhasil dikosongkan")
# # # # # # # print("✅ Status rekening berhasil diubah menjadi tutup")
# # # # # # # print("✅ Persetujuan penutupan tetap tersimpan")
# # # # # # # print("✅ Riwayat penutupan berhasil disimpan")
# # # # # # # print("✅ Audit penarikan seluruh saldo berhasil disimpan")
# # # # # # # print("✅ Penyelesaian penutupan rekening bekerja sesuai rancangan")
# # # # # #
# # # # # #
# # # # # #
# # # # # #
# # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # #     RekeningRepository
# # # # # # )
# # # # # #
# # # # # #
# # # # # # # NOREK_ASAL = "3001946913802745"
# # # # # # # NOREK_PENERIMA = "2001569043650499"
# # # # # # #
# # # # # # #
# # # # # # # rekening_asal = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # #     NOREK_ASAL
# # # # # # # )
# # # # # # #
# # # # # # # rekening_penerima = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # #     NOREK_PENERIMA
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # print("KONDISI SEBELUM PENUTUPAN")
# # # # # # #
# # # # # # # print()
# # # # # # # print("REKENING ASAL")
# # # # # # # print("Norek  :", rekening_asal["norek"])
# # # # # # # print("Saldo  :", rekening_asal["saldo"])
# # # # # # # print("Status :", rekening_asal["status"])
# # # # # # #
# # # # # # # print()
# # # # # # # print("REKENING PENERIMA")
# # # # # # # print("Norek  :", rekening_penerima["norek"])
# # # # # # # print("Saldo  :", rekening_penerima["saldo"])
# # # # # # # print("Status :", rekening_penerima["status"])
# # # # # #
# # # # # #
# # # # # #
# # # # # # # NOREK_ASAL = "3001946913802745"
# # # # # # # NOREK_PENERIMA = "2001569043650499"
# # # # # # #
# # # # # # #
# # # # # # # rekening_asal = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # #     NOREK_ASAL
# # # # # # # )
# # # # # # #
# # # # # # # rekening_penerima = RekeningRepository.cari_rekening_dengan_norek(
# # # # # # #     NOREK_PENERIMA
# # # # # # # )
# # # # # # #
# # # # # # #
# # # # # # # print("KONDISI SETELAH PENUTUPAN")
# # # # # # #
# # # # # # # print()
# # # # # # # print("REKENING ASAL")
# # # # # # # print("Norek  :", rekening_asal["norek"])
# # # # # # # print("Saldo  :", rekening_asal["saldo"])
# # # # # # # print("Status :", rekening_asal["status"])
# # # # # # #
# # # # # # # print()
# # # # # # # print("REKENING PENERIMA")
# # # # # # # print("Norek  :", rekening_penerima["norek"])
# # # # # # # print("Saldo  :", rekening_penerima["saldo"])
# # # # # # # print("Status :", rekening_penerima["status"])
# # # # # #
# # # # # #
# # # # # # from bank_djago.penyimpanan.repositories.rekening_repository import (
# # # # # #     RekeningRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository  import (
# # # # # #     PengajuanRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.repositories.riwayat_repository import (
# # # # # #     RiwayatRepository
# # # # # # )
# # # # # # from bank_djago.penyimpanan.repositories.audit_repository import (
# # # # # #     AuditRepository
# # # # # # )
# # # # # #
# # # # # #
# # # # # # NOREK_ASAL = "3001946913802745"
# # # # # # NOREK_PENERIMA = "2001569043650499"
# # # # # # ID_PENGAJUAN = 3
# # # # # #
# # # # # #
# # # # # # rekening_asal = RekeningRepository.cari_rekening_dengan_norek(
# # # # # #     NOREK_ASAL
# # # # # # )
# # # # # #
# # # # # # rekening_penerima = RekeningRepository.cari_rekening_dengan_norek(
# # # # # #     NOREK_PENERIMA
# # # # # # )
# # # # # #
# # # # # # pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
# # # # # #     ID_PENGAJUAN
# # # # # # )
# # # # # #
# # # # # # riwayat_asal = RiwayatRepository.cari_seluruh_riwayat(
# # # # # #     NOREK_ASAL
# # # # # # )
# # # # # #
# # # # # # audit_asal = AuditRepository.cari_audit_dengan_norek(
# # # # # #     NOREK_ASAL
# # # # # # )
# # # # # #
# # # # # #
# # # # # # print("REKENING ASAL SETELAH PENUTUPAN")
# # # # # # print("Norek  :", rekening_asal["norek"])
# # # # # # print("Saldo  :", rekening_asal["saldo"])
# # # # # # print("Status :", rekening_asal["status"])
# # # # # #
# # # # # #
# # # # # # print()
# # # # # # print("REKENING PENERIMA SETELAH TRANSFER")
# # # # # # print("Norek  :", rekening_penerima["norek"])
# # # # # # print("Saldo  :", rekening_penerima["saldo"])
# # # # # # print("Status :", rekening_penerima["status"])
# # # # # #
# # # # # #
# # # # # # print()
# # # # # # print("KONDISI PENGAJUAN")
# # # # # # print("ID      :", pengajuan["id"])
# # # # # # print("Jenis   :", pengajuan["jenis"])
# # # # # # print("Status  :", pengajuan["status"])
# # # # # #
# # # # # #
# # # # # # print()
# # # # # # print("RIWAYAT TERBARU REKENING ASAL")
# # # # # #
# # # # # # riwayat_terbaru = riwayat_asal[0]
# # # # # #
# # # # # # print("Jenis   :", riwayat_terbaru["jenis"])
# # # # # # print("Waktu   :", riwayat_terbaru["waktu"])
# # # # # # print("Log     :", riwayat_terbaru["log"])
# # # # # #
# # # # # #
# # # # # # print()
# # # # # # print("AUDIT TERBARU")
# # # # # #
# # # # # # audit_terbaru = audit_asal[0]
# # # # # #
# # # # # # print("Jenis   :", audit_terbaru["jenis"])
# # # # # # print("Waktu   :", audit_terbaru["waktu"])
# # # # # # print("Log     :", audit_terbaru["log"])
# # # # # # print("NIK     :", audit_terbaru["nik"])
# # # # # # print("Norek   :", audit_terbaru["norek"])
# # # # # #
# # # # # #
# # # # # # assert rekening_asal["saldo"] == 0
# # # # # # assert rekening_asal["status"] == "tutup"
# # # # # #
# # # # # # assert rekening_penerima["saldo"] == 109_000_000
# # # # # # assert rekening_penerima["status"] == "aktif"
# # # # # #
# # # # # # assert pengajuan["id"] == ID_PENGAJUAN
# # # # # # assert pengajuan["status"] == "disetujui"
# # # # # #
# # # # # # assert riwayat_terbaru["jenis"] == "penutupan rekening"
# # # # # # assert audit_terbaru["jenis"] == "penutupan transfer saldo"
# # # # # #
# # # # # #
# # # # # # print()
# # # # # # print("✅ Saldo rekening asal berhasil dikosongkan")
# # # # # # print("✅ Rekening asal berhasil ditutup")
# # # # # # print("✅ Saldo penerima bertambah menjadi Rp109.000.000")
# # # # # # print("✅ Rekening penerima tetap aktif")
# # # # # # print("✅ Pengajuan persetujuan tetap tersimpan")
# # # # # # print("✅ Riwayat dan audit penutupan berhasil disimpan")
# # # # #
# # # # #
# # # # #
# # # # #
# # # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # # # # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
# # # # #     PengajuanRepository
# # # # # )
# # # # #
# # # # #
# # # # # norek = "3001327791680308"
# # # # #
# # # # # koneksi = buat_koneksi()
# # # # #
# # # # # try:
# # # # #     pengajuan = PengajuanRepository.cari_pengajuan_aktif(
# # # # #         norek=norek,
# # # # #         jenis="tutup",
# # # # #         koneksi=koneksi
# # # # #     )
# # # # #
# # # # #     if pengajuan is None:
# # # # #         print("Pengajuan penutupan tidak ditemukan")
# # # # #     else:
# # # # #         print("Pengajuan berhasil ditemukan")
# # # # #         print(f"ID                 : {pengajuan['id']}")
# # # # #         print(f"Nomor rekening     : {pengajuan['norek']}")
# # # # #         print(f"Jenis              : {pengajuan['jenis']}")
# # # # #         print(f"Alasan             : {pengajuan['alasan']}")
# # # # #         print(f"Status             : {pengajuan['status']}")
# # # # #         print(f"Waktu pengajuan    : {pengajuan['waktu_pengajuan']}")
# # # # #         print(f"Waktu diproses     : {pengajuan['waktu_diproses']}")
# # # # #         print(f"Catatan admin      : {pengajuan['catatan_admin']}")
# # # # #
# # # # # finally:
# # # # #     koneksi.close()
# # # #
# # # #
# # # #
# # # #
# # # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # from bank_djago.penyimpanan.repositories.pengajuan_rekening_repository import (
# #     PengajuanRepository
# # )
# # from bank_djago.penyimpanan.repositories.rekening_repository import (
# #     RekeningRepository)
# # # # )
# # # #
# # # #
# # # # id_pengajuan = 6
# # # # norek = "3001327791680308"
# # # #
# # # # koneksi = buat_koneksi()
# # # #
# # # # try:
# # # #     pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
# # # #         id_pengajuan=id_pengajuan,
# # # #         koneksi=koneksi
# # # #     )
# # # #
# # # #     rekening = RekeningRepository.cari_rekening_dengan_norek(
# # # #         norek=norek,
# # # #         koneksi=koneksi
# # # #     )
# # # #
# # # #     if pengajuan is None:
# # # #         raise ValueError("Pengajuan tidak ditemukan")
# # # #
# # # #     if rekening is None:
# # # #         raise ValueError("Rekening tidak ditemukan")
# # # #
# # # #     print("=== DATA PENGAJUAN ===")
# # # #     print(f"ID pengajuan      : {pengajuan['id']}")
# # # #     print(f"Nomor rekening    : {pengajuan['norek']}")
# # # #     print(f"Jenis             : {pengajuan['jenis']}")
# # # #     print(f"Alasan            : {pengajuan['alasan']}")
# # # #     print(f"Status            : {pengajuan['status']}")
# # # #     print(f"Waktu pengajuan   : {pengajuan['waktu_pengajuan']}")
# # # #     print(f"Waktu diproses    : {pengajuan['waktu_diproses']}")
# # # #     print(f"Catatan admin     : {pengajuan['catatan_admin']}")
# # # #
# # # #     print("\n=== DATA REKENING ===")
# # # #     print(f"Nomor rekening    : {rekening['norek']}")
# # # #     print(f"Saldo             : {rekening['saldo']}")
# # # #     print(f"Status rekening   : {rekening['status']}")
# # # #
# # # #     assert pengajuan["status"] == "disetujui"
# # # #     assert pengajuan["waktu_diproses"] is not None
# # # #     assert pengajuan["catatan_admin"] is not None
# # # #
# # # #     # Persetujuan belum boleh langsung menutup rekening.
# # # #     assert rekening["saldo"] == 10_000_000
# # # #     assert rekening["status"] == "aktif"
# # # #
# # # #     print("\n✅ Persetujuan penutupan tersimpan dengan benar")
# # # #
# # # # finally:
# # # #     koneksi.close()
# # #
# # #
# # #
# # # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # #
# # #
# # # norek = "3001327791680308"
# # # saldo_awal = 10_000_000
# # #
# # # koneksi = buat_koneksi()
# # #
# # # try:
# # #     # 1. Periksa rekening
# # #     rekening = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM rekening
# # #         WHERE norek = ?
# # #         """,
# # #         (norek,)
# # #     ).fetchone()
# # #
# # #     if rekening is None:
# # #         raise ValueError("Rekening tidak ditemukan")
# # #
# # #     # 2. Cari transaksi penutupan terbaru
# # #     transaksi = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM transaksi
# # #         WHERE norek_sumber = ?
# # #           AND jenis = 'penarikan_saldo_penutupan'
# # #         ORDER BY id DESC
# # #         LIMIT 1
# # #         """,
# # #         (norek,)
# # #     ).fetchone()
# # #
# # #     if transaksi is None:
# # #         raise ValueError(
# # #             "Transaksi penarikan saldo penutupan tidak ditemukan"
# # #         )
# # #
# # #     id_transaksi = transaksi["id"]
# # #
# # #     # 3. Cari riwayat yang terhubung
# # #     daftar_riwayat = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM riwayat
# # #         WHERE transaksi_id = ?
# # #         ORDER BY id ASC
# # #         """,
# # #         (id_transaksi,)
# # #     ).fetchall()
# # #
# # #     # 4. Cari audit yang terhubung
# # #     daftar_audit = koneksi.execute(
# # #         """
# # #         SELECT *
# # #         FROM audit
# # #         WHERE transaksi_id = ?
# # #         ORDER BY id ASC
# # #         """,
# # #         (id_transaksi,)
# # #     ).fetchall()
# # #
# # #     print("=== DATA REKENING ===")
# # #     print(f"Nomor rekening       : {rekening['norek']}")
# # #     print(f"Saldo                : {rekening['saldo']}")
# # #     print(f"Status               : {rekening['status']}")
# # #
# # #     print("\n=== DATA TRANSAKSI ===")
# # #     print(f"ID transaksi         : {transaksi['id']}")
# # #     print(f"Jenis                : {transaksi['jenis']}")
# # #     print(f"Rekening sumber      : {transaksi['norek_sumber']}")
# # #     print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
# # #     print(f"Nominal              : {transaksi['nominal']}")
# # #     print(
# # #         f"Saldo sumber sebelum : "
# # #         f"{transaksi['saldo_sumber_sebelum']}"
# # #     )
# # #     print(
# # #         f"Saldo sumber sesudah : "
# # #         f"{transaksi['saldo_sumber_sesudah']}"
# # #     )
# # #     print(f"Waktu                : {transaksi['waktu']}")
# # #
# # #     print("\n=== RIWAYAT TERHUBUNG ===")
# # #
# # #     for riwayat in daftar_riwayat:
# # #         print(
# # #             f"ID {riwayat['id']} | "
# # #             f"Transaksi {riwayat['transaksi_id']} | "
# # #             f"{riwayat['jenis']} | "
# # #             f"{riwayat['log']}"
# # #         )
# # #
# # #     print("\n=== AUDIT TERHUBUNG ===")
# # #
# # #     for audit in daftar_audit:
# # #         print(
# # #             f"ID {audit['id']} | "
# # #             f"Transaksi {audit['transaksi_id']} | "
# # #             f"{audit['jenis']} | "
# # #             f"{audit['log']}"
# # #         )
# # #
# # #     # Pemeriksaan otomatis rekening
# # #     assert rekening["saldo"] == 0
# # #     assert rekening["status"] == "tutup"
# # #
# # #     # Pemeriksaan otomatis transaksi
# # #     assert transaksi["jenis"] == (
# # #         "penarikan_saldo_penutupan"
# # #     )
# # #     assert transaksi["norek_sumber"] == norek
# # #     assert transaksi["norek_tujuan"] is None
# # #     assert transaksi["nominal"] == saldo_awal
# # #     assert transaksi["saldo_sumber_sebelum"] == saldo_awal
# # #     assert transaksi["saldo_sumber_sesudah"] == 0
# # #     assert transaksi["saldo_tujuan_sebelum"] is None
# # #     assert transaksi["saldo_tujuan_sesudah"] is None
# # #
# # #     # Metode tarik menghasilkan satu riwayat dan satu audit
# # #     assert len(daftar_riwayat) == 1
# # #     assert len(daftar_audit) == 1
# # #
# # #     assert daftar_riwayat[0]["transaksi_id"] == id_transaksi
# # #     assert daftar_audit[0]["transaksi_id"] == id_transaksi
# # #
# # #     print(
# # #         "\n✅ Penutupan dengan metode tarik "
# # #         "tersimpan dengan benar"
# # #     )
# # #
# # # finally:
# # #     koneksi.close()
# # # from bank_djago.penyimpanan.repositories.rekening_repository import RekeningRepository
# # from bank_djago.penyimpanan.sqlite.database import buat_koneksi
# # #
# # # koneksi = buat_koneksi()
# # #
# # # rekening = RekeningRepository.cari_rekening_dengan_norek("2001842427316253")
# # #
# # # print(f'saldo ',rekening["saldo"])
# #
# #
# # id_pengajuan = 7
# # norek = "3001327791680308"
# #
# # koneksi = buat_koneksi()
# #
# # try:
# #     pengajuan = PengajuanRepository.cari_pengajuan_dengan_id(
# #         id_pengajuan=id_pengajuan,
# #         koneksi=koneksi
# #     )
# #
# #     rekening = RekeningRepository.cari_rekening_dengan_norek(
# #         norek=norek,
# #         koneksi=koneksi
# #     )
# #
# #     if pengajuan is None:
# #         raise ValueError("Pengajuan tidak ditemukan")
# #
# #     if rekening is None:
# #         raise ValueError("Rekening tidak ditemukan")
# #
# #     print("=== DATA PENGAJUAN ===")
# #     print(f"ID pengajuan      : {pengajuan['id']}")
# #     print(f"Nomor rekening    : {pengajuan['norek']}")
# #     print(f"Jenis             : {pengajuan['jenis']}")
# #     print(f"Alasan            : {pengajuan['alasan']}")
# #     print(f"Status            : {pengajuan['status']}")
# #     print(f"Waktu pengajuan   : {pengajuan['waktu_pengajuan']}")
# #     print(f"Waktu diproses    : {pengajuan['waktu_diproses']}")
# #     print(f"Catatan admin     : {pengajuan['catatan_admin']}")
# #
# #     print("\n=== DATA REKENING ===")
# #     print(f"Nomor rekening    : {rekening['norek']}")
# #     print(f"Saldo             : {rekening['saldo']}")
# #     print(f"Status rekening   : {rekening['status']}")
# #
# #     assert pengajuan["status"] == "disetujui"
# #     assert pengajuan["waktu_diproses"] is not None
# #     assert pengajuan["catatan_admin"] is not None
# #
# #     # Persetujuan belum boleh langsung menutup rekening.
# #     assert rekening["saldo"] == 1000
# #     assert rekening["status"] == "aktif"
# #
# #     print("\n✅ Persetujuan penutupan tersimpan dengan benar")
# #
# # finally:
# #     koneksi.close()
#
#
#
#
# from bank_djago.penyimpanan.sqlite.database import buat_koneksi
#
#
# norek_sumber = "4001319935443781"
# norek_penerima = "2001842427316253"
#
# saldo_awal_sumber = 1_000_000
# saldo_awal_penerima = 100_000_000
# saldo_akhir_penerima = 101_000_000
#
# koneksi = buat_koneksi()
#
# try:
#     # ==========================================================
#     # 1. Periksaahkan kedua rekening
#     # ==========================================================
#     rekening_sumber = koneksi.execute(
#         """
#         SELECT *
#         FROM rekening
#         WHERE norek = ?
#         """,
#         (norek_sumber,)
#     ).fetchone()
#
#     rekening_penerima = koneksi.execute(
#         """
#         SELECT *
#         FROM rekening
#         WHERE norek = ?
#         """,
#         (norek_penerima,)
#     ).fetchone()
#
#     if rekening_sumber is None:
#         raise ValueError("Rekening sumber tidak ditemukan")
#
#     if rekening_penerima is None:
#         raise ValueError("Rekening penerima tidak ditemukan")
#
#     # ==========================================================
#     # 2. Cari transaksi pemindahan saldo penutupan
#     # ==========================================================
#     transaksi = koneksi.execute(
#         """
#         SELECT *
#         FROM transaksi
#         WHERE norek_sumber = ?
#           AND norek_tujuan = ?
#           AND jenis = 'pemindahan_saldo_penutupan'
#         ORDER BY id DESC
#         LIMIT 1
#         """,
#         (
#             norek_sumber,
#             norek_penerima
#         )
#     ).fetchone()
#
#     if transaksi is None:
#         raise ValueError(
#             "Transaksi pemindahan saldo penutupan "
#             "tidak ditemukan"
#         )
#
#     id_transaksi = transaksi["id"]
#
#     # ==========================================================
#     # 3. Cari seluruh riwayat yang terhubung
#     # ==========================================================
#     daftar_riwayat = koneksi.execute(
#         """
#         SELECT *
#         FROM riwayat
#         WHERE transaksi_id = ?
#         ORDER BY id ASC
#         """,
#         (id_transaksi,)
#     ).fetchall()
#
#     # ==========================================================
#     # 4. Cari seluruh audit yang terhubung
#     # ==========================================================
#     daftar_audit = koneksi.execute(
#         """
#         SELECT *
#         FROM audit
#         WHERE transaksi_id = ?
#         ORDER BY id ASC
#         """,
#         (id_transaksi,)
#     ).fetchall()
#
#     # ==========================================================
#     # Tampilkan hasil
#     # ==========================================================
#     print("=== REKENING SUMBER ===")
#     print(f"Nomor rekening : {rekening_sumber['norek']}")
#     print(f"Saldo          : {rekening_sumber['saldo']}")
#     print(f"Status         : {rekening_sumber['status']}")
#
#     print("\n=== REKENING PENERIMA ===")
#     print(f"Nomor rekening : {rekening_penerima['norek']}")
#     print(f"Saldo          : {rekening_penerima['saldo']}")
#     print(f"Status         : {rekening_penerima['status']}")
#
#     print("\n=== DATA TRANSAKSI ===")
#     print(f"ID transaksi         : {transaksi['id']}")
#     print(f"Jenis                : {transaksi['jenis']}")
#     print(f"Rekening sumber      : {transaksi['norek_sumber']}")
#     print(f"Rekening tujuan      : {transaksi['norek_tujuan']}")
#     print(f"Nominal              : {transaksi['nominal']}")
#     print(
#         f"Saldo sumber sebelum : "
#         f"{transaksi['saldo_sumber_sebelum']}"
#     )
#     print(
#         f"Saldo sumber sesudah : "
#         f"{transaksi['saldo_sumber_sesudah']}"
#     )
#     print(
#         f"Saldo tujuan sebelum : "
#         f"{transaksi['saldo_tujuan_sebelum']}"
#     )
#     print(
#         f"Saldo tujuan sesudah : "
#         f"{transaksi['saldo_tujuan_sesudah']}"
#     )
#     print(f"Waktu                : {transaksi['waktu']}")
#
#     print("\n=== RIWAYAT TERHUBUNG ===")
#
#     for riwayat in daftar_riwayat:
#         print(
#             f"ID {riwayat['id']} | "
#             f"Rekening {riwayat['norek']} | "
#             f"Transaksi {riwayat['transaksi_id']} | "
#             f"{riwayat['jenis']} | "
#             f"{riwayat['log']}"
#         )
#
#     print("\n=== AUDIT TERHUBUNG ===")
#
#     for audit in daftar_audit:
#         print(
#             f"ID {audit['id']} | "
#             f"Rekening {audit['norek']} | "
#             f"Transaksi {audit['transaksi_id']} | "
#             f"{audit['jenis']} | "
#             f"{audit['log']}"
#         )
#
#     # ==========================================================
#     # Assertions rekening
#     # ==========================================================
#     assert rekening_sumber["saldo"] == 0
#     assert rekening_sumber["status"] == "tutup"
#
#     assert rekening_penerima["saldo"] == saldo_akhir_penerima
#     assert rekening_penerima["status"] == "aktif"
#
#     # ==========================================================
#     # Assertions transaksi
#     # ==========================================================
#     assert transaksi["jenis"] == (
#         "pemindahan_saldo_penutupan"
#     )
#
#     assert transaksi["norek_sumber"] == norek_sumber
#     assert transaksi["norek_tujuan"] == norek_penerima
#     assert transaksi["nominal"] == saldo_awal_sumber
#
#     assert transaksi["saldo_sumber_sebelum"] == (
#         saldo_awal_sumber
#     )
#     assert transaksi["saldo_sumber_sesudah"] == 0
#
#     assert transaksi["saldo_tujuan_sebelum"] == (
#         saldo_awal_penerima
#     )
#     assert transaksi["saldo_tujuan_sesudah"] == (
#         saldo_akhir_penerima
#     )
#
#     # ==========================================================
#     # Assertions hubungan
#     # ==========================================================
#     assert len(daftar_riwayat) == 2
#     assert len(daftar_audit) == 2
#
#     norek_dalam_riwayat = {
#         riwayat["norek"]
#         for riwayat in daftar_riwayat
#     }
#
#     norek_dalam_audit = {
#         audit["norek"]
#         for audit in daftar_audit
#     }
#
#     assert norek_dalam_riwayat == {
#         norek_sumber,
#         norek_penerima
#     }
#
#     assert norek_dalam_audit == {
#         norek_sumber,
#         norek_penerima
#     }
#
#     assert all(
#         riwayat["transaksi_id"] == id_transaksi
#         for riwayat in daftar_riwayat
#     )
#
#     assert all(
#         audit["transaksi_id"] == id_transaksi
#         for audit in daftar_audit
#     )
#
#     print(
#         "\n✅ Penutupan dengan metode transfer "
#         "tersimpan dengan benar"
#     )
#
# finally:
#     koneksi.close()




from unittest.mock import patch

from bank_djago.penyimpanan.sqlite.database import buat_koneksi
from bank_djago.penyimpanan.loaders.rekening_loaders import (
    RekeningLoader
)
from bank_djago.penyimpanan.repositories.audit_repository import (
    AuditRepository
)
from bank_djago.services.rekening.pengajuan_service import (
    PengajuanService
)


norek_sumber = "2001842427316253"
norek_penerima = "3001781978899033"


def ambil_kondisi_database():
    koneksi = buat_koneksi()

    try:
        sumber = koneksi.execute(
            """
            SELECT norek, saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (norek_sumber,)
        ).fetchone()

        penerima = koneksi.execute(
            """
            SELECT norek, saldo, status
            FROM rekening
            WHERE norek = ?
            """,
            (norek_penerima,)
        ).fetchone()

        pengajuan = koneksi.execute(
            """
            SELECT id, status
            FROM pengajuan_rekening
            WHERE id = 8
            """
        ).fetchone()

        jumlah_transaksi = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM transaksi
            """
        ).fetchone()["jumlah"]

        jumlah_riwayat = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM riwayat
            """
        ).fetchone()["jumlah"]

        jumlah_audit = koneksi.execute(
            """
            SELECT COUNT(*) AS jumlah
            FROM audit
            """
        ).fetchone()["jumlah"]

        return {
            "saldo_sumber": sumber["saldo"],
            "status_sumber": sumber["status"],
            "saldo_penerima": penerima["saldo"],
            "status_penerima": penerima["status"],
            "status_pengajuan": pengajuan["status"],
            "jumlah_transaksi": jumlah_transaksi,
            "jumlah_riwayat": jumlah_riwayat,
            "jumlah_audit": jumlah_audit
        }

    finally:
        koneksi.close()


# ==========================================================
# Kondisi sebelum pengujian
# ==========================================================
kondisi_sebelum = ambil_kondisi_database()

print("=== KONDISI SEBELUM ===")
print(kondisi_sebelum)

assert kondisi_sebelum["saldo_sumber"] == 101_000_000
assert kondisi_sebelum["status_sumber"] == "aktif"
assert kondisi_sebelum["status_penerima"] == "aktif"
assert kondisi_sebelum["status_pengajuan"] == "disetujui"


koneksi = buat_koneksi()
# Muat objek rekening sumber.
rekening_sumber = RekeningLoader.muat_rekening(
    norek_sumber,koneksi
)


# ==========================================================
# Paksa kegagalan sebelum commit
# ==========================================================
try:
    with patch.object(
        AuditRepository,
        "tambah_audit",
        side_effect=RuntimeError(
            "Kegagalan audit untuk menguji rollback"
        )
    ):
        PengajuanService.selesaikan_penutupan(
            rekening=rekening_sumber,
            metode="transfer",
            norek_penerima=norek_penerima
        )

    raise AssertionError(
        "Service seharusnya gagal, tetapi justru berhasil"
    )

except RuntimeError as error:
    assert str(error) == (
        "Kegagalan audit untuk menguji rollback"
    )

    print("\n✅ Kegagalan buatan berhasil dipicu")
    print(f"Pesan error: {error}")


# ==========================================================
# Kondisi setelah rollback
# ==========================================================
kondisi_sesudah = ambil_kondisi_database()

print("\n=== KONDISI SETELAH ROLLBACK ===")
print(kondisi_sesudah)


# Seluruh keadaan database harus sama.
assert kondisi_sesudah == kondisi_sebelum

# Objek Python juga belum boleh berubah karena perubahan
# objek dilakukan setelah commit berhasil.
assert rekening_sumber.saldo == 101_000_000
assert rekening_sumber.status == "aktif"

print(
    "\n✅ ROLLBACK BERHASIL: saldo, status, pengajuan, "
    "transaksi, riwayat, dan audit tidak berubah"
)