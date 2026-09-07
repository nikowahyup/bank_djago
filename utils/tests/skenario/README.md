# Peta Skenario Pengujian

Folder ini memisahkan jurnal pengujian besar berdasarkan urutan berikut:

`objek/domain → fitur → skenario`

Contoh: pengujian rollback pembayaran cicilan berada di
`pinjaman/pembayaran/test_rollback.py`, sedangkan rollback ARO pokok+bunga
berada di `deposito/aro/test_rollback_pokok_bunga.py`.

## Kelompok utama

| Folder | Isi |
|---|---|
| `deposito/` | Pembukaan, pencairan, jatuh tempo, ARO, dan repository deposito |
| `pinjaman/` | Keputusan admin, pencairan, pembayaran, scheduler, loader, dan diagnostik |
| `rekening/` | Pembukaan, penutupan, transfer, bunga, biaya admin, dan perubahan level |
| `notifikasi/` | Repository, loader, dan perubahan pesan notifikasi |
| `pencatatan/` | Repository audit dan riwayat |
| `nasabah/` | Pendaftaran, service, dan repository nasabah |
| `scheduler/` | Integrasi proses berkala lintas rekening |
| `integritas/` | Pemeriksaan hubungan objek domain |
| `legacy/` | Pengujian lama berbasis JSON yang masih berguna untuk belajar |

## Cara membaca

1. Pilih domain yang sedang dipelajari.
2. Masuk ke fitur yang relevan, misalnya `pinjaman/pembayaran/`.
3. Mulai dari skenario normal, kemudian penolakan, idempotensi, dan rollback.
4. Baca `arsip_sumber_asli/` hanya jika ingin melihat urutan eksperimen sebelum
   kode dipisahkan.

## Peringatan menjalankan test

Sebagian file merupakan pengujian manual yang memakai keadaan database
pengembangan dan dapat mengubah data. Docstring di awal setiap file hasil
pemisahan mencatat sumber serta urutannya. Periksa ID, nomor rekening, tanggal
simulasi, dan kondisi awal sebelum menjalankan file.

Pemeriksaan sintaks tidak menjalankan transaksi. Untuk pengujian yang mengubah
data, jalankan hanya skenario yang kondisi awalnya sudah disiapkan.

## Aturan pengujian baru

- Satu file memiliki satu tujuan utama.
- Nama file menjelaskan perilaku yang diperiksa, bukan urutan percobaan.
- Pisahkan kondisi awal, aksi, dan hasil yang diharapkan.
- Pengujian kegagalan menyimpan snapshot state sebelum aksi.
- Pengujian mutasi menyatakan apakah aman dijalankan ulang.
- Jangan kembali menumpuk versi lama sebagai lapisan komentar; riwayat Git dan
  `arsip_sumber_asli/` sudah menyimpan jejak belajarnya.
