# Peta Pengujian Deposito

Dokumen ini memetakan isi `test_deposito.py` tanpa menghapus eksperimen lama.
File tersebut bukan satu test otomatis, melainkan jurnal pengujian manual yang
bertambah selama migrasi JSON ke SQLite dan penambahan tabel transaksi.

## Cara membaca file

- Baris **1–4277** berisi pengujian lama yang sengaja dinonaktifkan dengan
  komentar. Beberapa bagian memiliki lebih dari satu lapisan `#` karena setiap
  percobaan baru pernah ditambahkan di bawah percobaan sebelumnya.
- Baris **4278–4580** adalah satu-satunya skenario yang aktif saat ini.
- Jangan menjalankan seluruh arsip sekaligus. Beberapa skenario sukses mengubah
  database dan dirancang untuk data deposito tertentu.
- Untuk memakai ulang sebuah skenario, salin bloknya ke file pengujian baru,
  sesuaikan konstanta, lalu jalankan hanya file tersebut.

## Jalur baca yang disarankan

Jika tujuanmu mempelajari integrasi deposito dengan tabel transaksi, baca dalam
urutan berikut:

1. **1520–1728** — pembukaan deposito dan transaksi.
2. **1729–1888** — rollback pembukaan deposito.
3. **1889–2313** — pencairan deposito dan transaksi.
4. **2314–2648** — rollback pencairan deposito.
5. **2649–3044** — ARO pokok dan bunga masuk rekening.
6. **3728–4095** — ARO pokok+bunga dan kapitalisasi bunga.
7. **4096–4277** — pemeriksaan transaksi hasil kapitalisasi.
8. **4278–4580** — rollback ARO pokok+bunga.

Urutan tersebut memperlihatkan pola yang sama pada setiap operasi:

1. simpan kondisi awal;
2. jalankan service;
3. baca ulang database;
4. periksa transaksi, riwayat, dan audit;
5. bandingkan objek di memori;
6. untuk test kegagalan, pastikan seluruh perubahan di-rollback.

## Daftar seluruh blok

| Baris | Fokus pengujian | Data utama | Efek jika diaktifkan |
|---:|---|---|---|
| 1–211 | Memeriksa hasil pembukaan deposito versi awal | Norek `2001569043650499` | Hanya membaca |
| 212–391 | Memeriksa loader nasabah, rekening, dan deposito | Deposito ID 5 | Hanya membaca |
| 392–725 | Pencairan deposito versi awal | Deposito ID 5 | Mengubah status dan saldo |
| 726–841 | Inventaris deposito ARO pokok dan pokok+bunga | Data nasabah lama | Hanya membaca |
| 842–1040 | Perpanjangan ARO pokok versi awal | Deposito ID 6 | Menambah bunga ke rekening |
| 1041–1246 | Perpanjangan ARO pokok+bunga versi awal | Deposito ID 7 | Mengapitalisasi bunga |
| 1247–1345 | Memeriksa loader seluruh deposito aktif | Semua deposito aktif | Hanya membaca |
| 1346–1519 | Menjalankan scheduler untuk periode ARO berikutnya | Hari simulasi 28 Desember 2026 | Mengubah deposito yang jatuh tempo |
| 1520–1728 | Memeriksa transaksi pembukaan deposito terbaru | Norek `3001781978899033` | Hanya membaca |
| 1729–1888 | Menguji rollback pembukaan saat audit gagal | Norek yang sama | Gagal secara sengaja; seharusnya tidak menyisakan perubahan |
| 1889–2313 | Menguji pencairan beserta transaksi, riwayat, audit, dan notifikasi | Deposito ID 10 | Mencairkan deposito |
| 2314–2648 | Menguji rollback pencairan saat audit gagal | Deposito non-ARO terbaru yang cocok | Gagal secara sengaja; deposito tetap jatuh tempo |
| 2649–3044 | Menguji ARO pokok dengan transaksi bunga | Deposito ID 12 | Memperpanjang deposito dan menambah saldo rekening |
| 3045–3537 | Percobaan ARO pokok+bunga yang pernah dijalankan berulang | Deposito ID 13 | Memperpanjang periode setiap kali dijalankan |
| 3538–3598 | Menghitung hasil kapitalisasi berulang | Deposito ID 13 | Hanya membaca |
| 3599–3653 | Memeriksa riwayat dan audit transaksi 19–23 sebelum pemulihan manual | Transaksi ID 19–23 | Hanya membaca; terdapat typo SQL historis |
| 3654–3727 | Pengaman kondisi awal ARO pokok+bunga | Deposito ID 14 | Hanya membaca |
| 3728–4095 | Pengujian utama ARO pokok+bunga | Deposito ID 14 | Memperpanjang deposito satu kali |
| 4096–4277 | Validasi transaksi, dua riwayat, dan audit kapitalisasi | Deposito ID 14 | Hanya membaca |
| 4278–4580 | Rollback ARO pokok+bunga saat audit gagal | Deposito ID 15 | Gagal secara sengaja; seharusnya aman diulang |

## Kelompok berdasarkan konsep

### Pembukaan deposito

- **1–211:** pemeriksaan implementasi pembukaan lama.
- **1520–1728:** versi yang sudah memeriksa tabel transaksi dan hubungan
  `transaksi_id` pada riwayat serta audit.
- **1729–1888:** pembuktian bahwa kegagalan audit membatalkan pemotongan saldo,
  deposito baru, transaksi, dan catatan pendukung.

### Pencairan deposito

- **392–725:** rancangan pencairan sebelum integrasi transaksi terbaru.
- **1889–2313:** versi lengkap yang memeriksa tujuan saldo, nominal pencairan,
  referensi deposito, riwayat, audit, dan penghapusan notifikasi.
- **2314–2648:** versi rollback dengan kegagalan audit buatan.

### ARO pokok

- **842–1040:** eksperimen awal perilaku ARO pokok.
- **2649–3044:** versi terbaru yang memastikan bunga masuk rekening, pokok
  deposito tetap, periode diperpanjang, dan transaksi `bunga_deposito` dibuat.

### ARO pokok+bunga

- **1041–1246:** eksperimen awal kapitalisasi.
- **3045–3537:** versi yang membantu menemukan masalah proses berulang pada
  deposito ID 13.
- **3654–3727:** pengaman agar deposito ID 14 belum pernah diproses.
- **3728–4095:** versi utama yang memastikan bunga menjadi bagian nominal baru
  tanpa mengubah saldo rekening.
- **4096–4277:** pemeriksaan terpisah terhadap transaksi kapitalisasi.
- **4278–4580:** pembuktian rollback database dan objek di memori.

## Tingkat keamanan menjalankan ulang

| Jenis blok | Aman diulang? | Alasan |
|---|---|---|
| Pemeriksaan baca-saja | Ya | Tidak menjalankan service yang mengubah data |
| Pengujian rollback | Ya, jika kondisi awal cocok | Kegagalan dipicu sebelum commit dan hasil dibandingkan dengan snapshot |
| Pembukaan, pencairan, atau ARO sukses | Tidak otomatis | Setiap eksekusi dapat membuat transaksi atau memajukan periode deposito |
| Scheduler | Tidak otomatis | Dapat memproses lebih dari satu deposito berdasarkan tanggal simulasi |

## Catatan teknis

- Nomor ID dan tanggal dalam file adalah data pengujian historis, bukan fixture
  yang dibuat otomatis.
- Banyak blok lama masih memakai nama `JenisReferensiID`; pada kode terbaru
  namanya adalah `JenisReferensi` dengan nilai string.
- Blok 3599–3653 menyimpan typo historis `ORDER BY transaksi_idpppppppooo`.
  Blok itu berguna sebagai catatan proses, tetapi tidak siap dijalankan tanpa
  koreksi.
- Tahap perapian berikutnya dapat memindahkan tiap blok ke file terpisah. Salinan
  asli sebaiknya tetap dipertahankan sampai semua skenario baru terbukti setara.
