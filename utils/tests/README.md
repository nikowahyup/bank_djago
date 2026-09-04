# Panduan Kode Pengujian Bank Djago

Folder ini berisi dua jenis kode:

1. **Pengujian mandiri** yang membuat data khusus, menjalankan pemeriksaan, lalu
   membersihkannya kembali.
2. **Jurnal pengujian manual** yang memakai database pengembangan dan menyimpan
   percobaan lama sebagai komentar.

Keduanya berguna, tetapi cara menjalankannya berbeda. Baca kolom **Sifat** dan
**Keamanan** sebelum menjalankan sebuah file.

## Arti penanda

| Penanda | Arti |
|---|---|
| Mandiri | Membuat data pengujian sendiri dan biasanya membersihkannya di `finally` |
| Baca-saja | Memeriksa data yang sudah ada tanpa menjalankan service pengubah data |
| Mutasi | Mengubah database pengembangan ketika dijalankan |
| Rollback | Sengaja memicu kegagalan dan memastikan perubahan tidak tersimpan |
| Arsip | Seluruh atau sebagian besar kode dinonaktifkan sebagai catatan belajar |

## Urutan belajar yang disarankan

1. Mulai dari `test_repo/test_repository_nasabah.py` untuk memahami bentuk dasar
   pengujian repository.
2. Lanjutkan ke repository rekening, riwayat, audit, notifikasi, deposito, dan
   pinjaman.
3. Baca `test_repo/test_repo_transaksi.py` untuk memahami snapshot saldo dan
   hubungan transaksi dengan riwayat serta audit.
4. Masuk ke test service: pendaftaran nasabah, pembukaan rekening, transfer,
   penutupan, deposito, lalu pinjaman.
5. Gunakan `cek_integritas.py` setelah memahami hubungan antar-objek.

## Peta utama

| File | Fokus | Sifat | Keamanan menjalankan ulang |
|---|---|---|---|
| `cek_integritas.py` | Relasi deposito, notifikasi, pinjaman, dan rekening dalam objek `Bank` | Kumpulan fungsi | Aman; tidak berjalan sendiri |
| `test_pinjaman.py` | Jurnal lama pinjaman: tunggakan, denda, pelunasan, dua pinjaman, dan save/load | Arsip + fungsi aktif | Panggil satu fungsi yang diperlukan saja |
| `test_repo/test_repository_nasabah.py` | Tambah, cari, duplikat, dan data tidak ditemukan | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repository_rekening.py` | Foreign key pemilik, CRUD dasar, duplikat, dan state rekening | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repository_riwayat.py` | ID global, filter rekening/jenis, urutan, dan isolasi data | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repository_audit.py` | Filter NIK/norek/jenis, audit sistem, urutan, dan waktu | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repository_notifikasi.py` | ID global, referensi, isolasi NIK, pencarian, dan penghapusan | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repository_deposito.py` | FK rekening, ID global, pencarian ID/norek/NIK, dan pembaruan | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repository_pinjaman.py` | FK rekening, pinjaman berjalan, riwayat lunas, dan pembaruan | Mandiri | Aman; data khusus dibersihkan |
| `test_repo/test_repo_transaksi.py` | Transaksi repository, setor, tarik, transfer, FK, urutan, dan setor awal | Jurnal manual | Hanya blok terakhir aktif; bergantung data lokal |
| `test_repo/test_notifikasi.py` | Siklus reminder H-3 hingga jatuh tempo | Mutasi manual | Tidak aman diulang tanpa menyiapkan ulang data |
| `test_repo/test_notifikasi_1.py` | Jatuh tempo, pencairan, serta siklus notifikasi ARO versi lama | Arsip penuh | Tidak berjalan; gunakan sebagai bahan baca |
| `test_service/test_pendaftaran_nasabah.py` | Memeriksa hasil pendaftaran melalui UI | Baca-saja | Aman jika NIK pengujian tersedia |
| `test_service/test_nasabah_service.py` | Pendaftaran, NIK duplikat, rollback, dan rekening tambahan | Mandiri | Aman jika fungsi utama dipanggil dan cleanup selesai |
| `test_service/test_buka_rekening.py` | Jurnal pembukaan rekening serta migrasi `waktu_dibuat` | Arsip + utilitas mutasi | Blok aktif dapat memperbarui rekening lama |
| `test_service/test_transfer.py` | Batas limit dan reset limit transfer | Mutasi manual | Tidak otomatis aman diulang |
| `test_service/test_up_down_rekening.py` | Upgrade/downgrade dan manipulasi tanggal perubahan | Jurnal manual | Blok aktif memundurkan tanggal di database |
| `test_service/test_penutupan.py` | Pengajuan, keputusan admin, tarik/transfer saldo, transaksi, dan rollback | Jurnal manual | Blok rollback aktif aman jika kondisi awal cocok |
| `test_service/test_deposito.py` | Pembukaan, pencairan, ARO, transaksi, dan rollback | Jurnal manual | Lihat `PETA_TEST_DEPOSITO.md` |
| `test_service/test_pinjaman.py` | Migrasi pinjaman SQLite dan pemeriksaan schema/waktu | Arsip + inspeksi aktif | Blok aktif hanya membaca schema transaksi |

## Peta jurnal transaksi

File: `test_repo/test_repo_transaksi.py`

| Baris | Skenario | Efek |
|---:|---|---|
| 1–151 | Repository transaksi: enum, arah, nominal, snapshot, waktu, dan rollback | Membuat transaksi lalu rollback |
| 152–341 | Setor tunai | Mengubah saldo dan membuat transaksi |
| 342–520 | Tarik tunai | Mengubah saldo dan membuat transaksi |
| 521–807 | Transfer dua rekening | Mengubah dua saldo dan membuat catatan kedua sisi |
| 808–918 | Pemeriksaan kolom serta foreign key `transaksi_id` | Baca-saja |
| 919–1154 | Urutan setor, tarik, transfer, dan snapshot saldo | Baca-saja |
| 1155–akhir | Transaksi setor awal pembukaan rekening | Baca-saja terhadap norek `2001842427316253` |

## Peta jurnal penutupan rekening

File: `test_service/test_penutupan.py`

| Baris | Skenario | Efek |
|---:|---|---|
| 1–86 | Pengajuan penutupan rekening | Membuat pengajuan dan audit |
| 87–182 | Admin menolak pengajuan | Mengubah status pengajuan |
| 183–245 | Admin menyetujui pengajuan | Mengubah status pengajuan |
| 246–336 | Penutupan dengan tarik seluruh saldo versi awal | Menutup rekening |
| 337–398 | Perbandingan saldo sebelum/sesudah transfer penutupan | Baca-saja |
| 399–504 | Penutupan dengan transfer saldo versi lengkap | Menutup rekening dan menambah saldo penerima |
| 505–736 | Persetujuan, hasil tarik, dan transaksi penutupan | Campuran pemeriksaan manual |
| 737–1032 | Persetujuan, transfer, transaksi, riwayat, dan audit | Campuran pemeriksaan manual |
| 1033–akhir | Rollback transfer penutupan ketika audit gagal | Gagal sengaja; kondisi harus tetap sama |

## Peta jurnal pinjaman

### `test_pinjaman.py`

| Baris | Skenario |
|---:|---|
| 1–284 | Save/load pinjaman menunggak |
| 285–569 | Pelunasan dengan denda |
| 570–832 | Mengejar tiga cicilan tertunggak |
| 833–904 | Saldo tidak cukup untuk pembayaran berdenda |
| 905–1090 | Pembayaran cicilan beserta denda |
| 1091–1272 | Menyiapkan pinjaman lama lunas dan pinjaman aktif baru |
| 1273–1465 | Save/load dua pinjaman milik nasabah yang sama |
| 1466–akhir | Pemeriksaan integritas histori dan pinjaman aktif |

### `test_service/test_pinjaman.py`

| Baris | Skenario |
|---:|---|
| 1–197 | Pengajuan pinjaman tersimpan dan berhasil dimuat kembali |
| 198–344 | Persetujuan pinjaman dan audit |
| 345–510 | Penolakan pinjaman serta pemulihan loader |
| 511–621 | Pemeriksaan data penolakan dan audit |
| 622–709 | Waktu pembukaan rekening yang dipakai pinjaman |
| 710–770 | Loader mempertahankan `waktu_dibuat` |
| 771–akhir | Inspeksi struktur tabel transaksi |

## Peta rekening dan transfer

### `test_service/test_buka_rekening.py`

- Bagian awal menyimpan pemeriksaan repository, audit, dan riwayat pembukaan
  rekening versi lama.
- Baris 225–akhir adalah utilitas untuk mengisi `waktu_dibuat` rekening lama
  dari audit pembukaan dan melaporkan rekening yang tidak memiliki audit.
- Utilitas tersebut mengubah data; jangan menjalankannya hanya untuk melihat
  hasil.

### `test_service/test_transfer.py`

- Baris 1–151 adalah catatan pemeriksaan transfer versi lama.
- Baris 152–336 menguji penolakan transfer yang melebihi limit dan memastikan
  saldo, limit, riwayat, serta audit tidak berubah.
- Baris 337–akhir menguji reset limit berdasarkan tanggal sebelum transfer.
  Skenario ini benar-benar melakukan transfer.

### `test_service/test_up_down_rekening.py`

- Baris 1–170 berisi catatan pemeriksaan perubahan jenis rekening versi lama.
- Baris 171–262 memeriksa hasil downgrade, state, riwayat, dan audit.
- Baris 263–akhir memundurkan `terakhir_ubah_rekening` untuk menyiapkan
  pengujian berikutnya; ini adalah utilitas mutasi, bukan assert test.

## Peta notifikasi

### `test_repo/test_notifikasi.py`

Skenario aktif menjalankan scheduler pada H-4, H-3, dan hari jatuh tempo. Ia
memastikan reminder baru dibuat tepat sekali, berubah menjadi pesan pencairan,
serta tetap benar setelah loader dijalankan.

### `test_repo/test_notifikasi_1.py`

| Baris | Skenario arsip |
|---:|---|
| 1–154 | Reminder H-3 berubah menjadi notifikasi jatuh tempo |
| 155–352 | Pencairan menghapus notifikasi dari memori dan SQLite |
| 353–akhir | Siklus notifikasi ARO pokok serta ARO pokok+bunga |

## Aturan menambah pengujian baru

1. Satu file sebaiknya memiliki satu tujuan utama.
2. Letakkan konfigurasi data di bagian atas dengan nama yang jelas.
3. Pisahkan tahap **Arrange**, **Act**, dan **Assert** menggunakan komentar.
4. Gunakan data khusus berawalan `TEST-` jika repository mengizinkannya.
5. Bersihkan hanya data buatan test sendiri di dalam `finally`.
6. Untuk pengujian kegagalan, simpan snapshot database dan objek sebelum aksi.
7. Lindungi eksekusi dengan `if __name__ == "__main__":`.
8. Beri peringatan jika test sukses mengubah database dan tidak aman diulang.
9. Jangan menonaktifkan seluruh file dengan menambah lapisan `#`; pindahkan
   versi lama ke blok arsip yang sudah dipetakan atau simpan lewat riwayat Git.
10. Sebelum menghapus arsip, pastikan skenario penggantinya telah diuji dan
    menghasilkan pemeriksaan yang setara.

## Tahap perapian selanjutnya

Peta ini sengaja dibuat sebelum memindahkan kode. Langkah aman berikutnya adalah
mengekstrak satu domain pada satu waktu ke file bernama berdasarkan skenario,
misalnya `test_rollback_pencairan_deposito.py`. File jurnal asli dipertahankan
sampai semua hasil pengujian baru cocok dengan versi lama.
