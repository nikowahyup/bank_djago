# 🏦 Simulasi Sistem Perbankan Bank Djago

Aplikasi simulasi perbankan berbasis Python untuk mengelola nasabah dan rekening, mulai dari transaksi harian hingga fitur layanan keuangan lanjutan.

> **Tujuan Utama:** Membangun portofolio *software engineering* yang kuat sebagai fondasi menuju *AI Engineer*.

### 💡 Prinsip Pengembangan:
* **Kualitas di Atas Kuantitas:** Lebih baik fokus mendalami satu proyek daripada banyak proyek setengah jadi.
* **Tujuan di Setiap Fitur:** Setiap fitur baru dirancang untuk mempelajari konsep pemrograman/arsitektur baru.
* **Desain Terarah:** Setiap keputusan arsitektur kode memiliki alasan teknis yang jelas.

---

## 🛠️ Teknologi yang Digunakan
* **Bahasa Pemrograman:** Python 3.x
* **Konsep Utama:** Object-Oriented Programming (OOP), Data Encapsulation, Inheritance, Data Validation, Transaction Management, dan Relational Database
* **Penyimpanan:** SQLite sebagai sumber data utama; JSON dipertahankan sebagai bagian dari riwayat pengembangan

---

## 📈 Status Pengembangan (Development Progress)

## Konsep yang sudah Dipelajari dan Dipakai
- Object-Oriented Programming
- Encapsulation
- Inheritance
- Polymorphism
- Composition
- Separation of Responsibility
- Business Logic
- Audit Trail
- Data Validation
- JSON Persistence
- Scheduler
- Notification System

## Struktur Folder
```text
bank_djago/
│
├── core/
├── services/
│   ├── admin/
│   ├── deposito/
│   ├── pinjaman/
│   ├── rekening/
│   └── transaksi/
├── penyimpanan/
├── tests/
├── utils/
├── Data/
└── main.py
```

### 📑 Fitur Saat Ini

## 📌 Versi Pengembangan

### `v0.1` - Pembuatan Objek Esensial
Memisahkan tanggung jawab objek (*Separation of Concerns*).

- [x] `Bank`: Wadah penyimpanan data dan eksekutor logika utama perbankan.
- [x] `Nasabah`: Objek pemilik rekening yang terdaftar secara resmi.
- [x] `Rekening`: Entitas keuangan yang menangani saldo, PIN, dan riwayat transaksi.

### `v0.2` - Fundamental
- [x] **Logika Transaksi:** Setor tunai, tarik tunai, dan transfer antar-rekening.
- [x] **Keamanan & Validasi:** Keberadaan rekening, validasi PIN, dan saldo minimum.
- [x] **Data Persistence:** Penyimpanan dan pemuatan menggunakan JSON.

### `v0.3` - Perluasan & Konsep OOP Lanjutan
- [x] **Inheritance:** Variasi jenis rekening dari satu parent class.
- [x] **Fitur Finansial:** Bunga, limit transfer harian, dan saldo minimum.

### `v0.4` - Manajemen Status Rekening
- [x] **Status Lifecycle:** Aktif, diblokir, dan ditutup.
- [x] **Fitur Dinamis:** Upgrade dan downgrade jenis rekening.

### `v0.5` - Audit & Rekapitulasi Data
- [x] **Audit System:** Pencatatan aktivitas transaksi.
- [x] **Bank Summary:** Rekap nasabah, rekening aktif, dan akumulasi kas.

### `v0.6` - Refactor & Penyempurnaan Arsitektur
- [x] **Pemisahan Logika Transaksi:** Memindahkan aturan transaksi ke `TransaksiService`.
- [x] **Pemisahan UI Transaksi:** Input dan komunikasi transaksi dengan nasabah ditangani `TransaksiUI`.
- [x] **Pemisahan Riwayat:** Log transaksi ditangani pada layer transaksi.
- [x] **Penyederhanaan Struktur:** Menghapus perantara yang tidak lagi memiliki tanggung jawab jelas.
- [x] **UI Terminal:** Menambahkan sistem warna pada header dan membedakan level navigasi.

### `v0.7` - Manajemen Admin
- [x] **Admin:** Pengelolaan nasabah dan rekening.
- [x] **Audit Log:** Pemantauan aktivitas bank.
- [x] **Rekapitulasi:** Penyajian laporan administrasi.

### `v0.8` - Deposito
- [x] **Struktur Deposito:** Membuat entitas deposito.
- [x] **Pembukaan Deposito:** Validasi nominal minimum, saldo minimum, tenor, dan bunga.
- [x] **Jatuh Tempo:** Perhitungan tanggal jatuh tempo berdasarkan tenor.
- [x] **Riwayat & Audit:** Mencatat pembukaan deposito.
- [x] **Pencairan Deposito:** Pencairan saat jatuh tempo dan perhitungan hasil deposito.
- [x] **ARO:** Perpanjangan otomatis pokok atau pokok + bunga.
- [x] **Scheduler Deposito:** Pemeriksaan jatuh tempo dan proses otomatis.
- [x] **Notifikasi Deposito:** Reminder, jatuh tempo, pencairan, dan informasi perpanjangan otomatis.
- [x] **Pemisahan Notifikasi per Objek:** Notifikasi deposito menggunakan `id_objek` untuk membedakan beberapa deposito milik nasabah yang sama.
- [x] **UI Deposito:** Menu dan alur input deposito.

### `v0.9` - Pinjaman
- [x] **Pengajuan Pinjaman**
- [x] **Persetujuan dan Penolakan Pinjaman**
- [x] **Tenor dan Bunga**
- [x] **Perhitungan Cicilan**
- [x] **Pencairan Pinjaman**
- [x] **Jatuh Tempo Cicilan**
- [x] **Reminder Jatuh Tempo**
- [x] **Notifikasi Jatuh Tempo**
- [x] **Pembayaran Cicilan**
- [x] **Pergeseran Jatuh Tempo Setelah Pembayaran**
- [x] **Validasi Periode Pembayaran:** Mencegah cicilan periode berikutnya dibayar sebelum periode pembayaran berikutnya dimulai.
- [x] **Validasi Saldo Pembayaran:** Menolak pembayaran jika saldo setelah cicilan berada di bawah saldo minimum rekening.
- [x] **Pelunasan**
- [x] **Persistence Pinjaman ke JSON**
- [x] **Denda Keterlambatan:** Denda harian 0,1% setelah masa toleransi 7 hari, dengan batas maksimal 10% dari cicilan.
- [x] **Status Tunggakan:** Deteksi keterlambatan berdasarkan selisih tanggal jatuh tempo tanpa menyimpan state turunan.
- [x] **Pembayaran Cicilan Tertunggak:** Pembayaran menyelesaikan cicilan tertua beserta dendanya tanpa menggeser jadwal kontrak.
- [x] **Pengejaran Beberapa Periode:** Nasabah dapat membayar beberapa cicilan tertunggak secara berurutan untuk kembali mengikuti jadwal.

### `v1.0` - Penyempurnaan Sistem
Fokus pada stabilitas, pengujian, integritas data, dan kesiapan arsitektur sebelum migrasi database dan web.

- [x] **Scheduler:** Otomatisasi proses bunga, biaya admin, limit, jatuh tempo, dan notifikasi.
- [x] **Notification System:** Sistem notifikasi berbasis referensi dan `id_objek`.
- [x] **Pengujian Lifecycle Pinjaman:** Pengajuan → persetujuan → pencairan → cicilan → jatuh tempo → pembayaran → pelunasan.
- [x] **Pengujian Deposito ARO & Non-ARO:** Pengujian reminder, jatuh tempo, pencairan, dan perpanjangan otomatis.
- [x] **Pengujian Multiple Deposito:** Memastikan notifikasi beberapa deposito dalam satu nasabah tidak saling bertabrakan.
- [x] **Pengujian Integrasi:** Menguji alur deposito dan pinjaman dalam satu nasabah, scheduler berbasis tanggal simulasi, pergantian notifikasi, ARO/non-ARO, pembayaran, pencairan, serta save/load setelah perubahan.
- [x] **Denda Keterlambatan:** Perhitungan denda harian setelah masa toleransi, pembayaran denda bersama cicilan, dan batas maksimal denda.
- [x] **Status Tunggakan:** Kondisi tunggakan dihitung dari tanggal jatuh tempo sehingga tetap konsisten pada repeated scheduler dan missed scheduler.
- [x] **Validasi Integritas Data:** Memastikan relasi nasabah, rekening, deposito, pinjaman, dan notifikasi tetap konsisten setelah save/load.
- [x] **Pengujian Edge Case:** Menguji repeated scheduler, missed scheduler, multiple deposito, save/load, pembayaran sebelum jatuh tempo, pencegahan pembayaran periode berikutnya terlalu cepat, saldo tidak cukup, status lunas, dan tanggal ujung bulan.
- [x] **Pengujian Tunggakan & Denda:** Menguji H/H+1/H+7/H+8, batas maksimal denda, pembayaran gagal tanpa perubahan state, beberapa periode tertunggak, pelunasan terlambat, dan save/load saat menunggak.
- [x] **Integritas Upgrade/Downgrade:** Memastikan Bank, Nasabah, Deposito, Pinjaman, dan UI menunjuk objek rekening pengganti yang sama.
- [x] **Riwayat Multiple Pinjaman:** Menyimpan seluruh pinjaman nasabah menggunakan struktur NIK → ID pinjaman → data pinjaman.
- [x] **Pemulihan Pinjaman Aktif:** Memuat seluruh riwayat pinjaman ke Bank dan memilih pinjaman berjalan berdasarkan status.
- [x] **Isolasi Notifikasi:** Memastikan penghapusan notifikasi deposito tidak memengaruhi deposito lain, pinjaman, atau rekening.
- [x] **Validasi Relasi Rekening:** Mencegah rekening ditutup selama masih memiliki deposito atau pinjaman berjalan.
- [x] **Validasi Rekening Terblokir:** Menolak pembayaran cicilan melalui rekening yang sedang diblokir.
- [x] **Perapian Struktur Proyek:** Memisahkan service, UI, penyimpanan, dan pengujian berdasarkan tanggung jawab.
- [x] **Dokumentasi:** Mendokumentasikan arsitektur, alur bisnis, integrity check, dan keputusan desain.

### `v1.1` - Database SQLite
Fokus pada pemindahan sumber kebenaran dari JSON dan objek `Bank` menuju database relasional.

- [x] Membuat skema SQLite untuk nasabah, rekening, deposito, pinjaman, notifikasi, riwayat, audit, dan pengajuan rekening.
- [x] Memisahkan repository, service, UI, dan loader.
- [x] Mengaktifkan foreign key dan menguji integritas relasi antartabel.
- [x] Memigrasikan pendaftaran nasabah dan pembukaan rekening pertama secara atomik.
- [x] Memigrasikan login dan pemuatan objek nasabah beserta seluruh rekeningnya.
- [x] Memigrasikan setor tunai, tarik tunai, dan transfer sebagai transaksi database.
- [x] Memigrasikan pembukaan, upgrade, downgrade, riwayat, serta audit rekening.
- [x] Menambahkan alur pengajuan, persetujuan, penolakan, dan penyelesaian penutupan rekening.
- [x] Mempertahankan rekening tertutup untuk kebutuhan audit dan riwayat.
- [ ] Menyelesaikan migrasi operasional deposito, pinjaman, notifikasi, scheduler, dan rekap.
- [ ] Menghapus ketergantungan akhir terhadap penyimpanan JSON dan agregat `Bank`.

### `v2.0` - Web Interface
- [ ] Mempelajari dasar HTTP, routing, request/response, template, session, dan autentikasi menggunakan Flask.
- [ ] Memigrasikan antarmuka terminal ke Flask secara bertahap.
- [ ] Membuat UI berbasis web.
- [ ] Mengintegrasikan autentikasi nasabah dan admin.
- [ ] Membuat dashboard nasabah dan admin.
- [ ] Menghubungkan business logic yang sudah dibangun tanpa memindahkannya ke route.
- [ ] Mengevaluasi Django setelah memahami dasar aplikasi web dan kebutuhan proyek bertambah.

---

## 🚧 Roadmap Utama

- [x] Sistem rekening dan transaksi dasar
- [x] Manajemen admin
- [x] Audit dan rekapitulasi
- [x] Deposito
- [x] Pinjaman
- [x] Scheduler
- [x] Notification System
- [x] Denda keterlambatan dan tunggakan
- [x] Penyempurnaan testing dan validasi integritas data
- [x] Fondasi database dan layanan utama menggunakan SQLite
- [ ] Menyelesaikan migrasi seluruh fitur ke SQLite
- [ ] Mempelajari dan mengintegrasikan Flask
- [ ] Web Interface

---

## Change Log

(05/08/2026)
- Memisahkan menu admin

(06/08/2026)
- Memisahkan semua service dari bank ke admin

(07/08/2026)
- Refactor Transaksi dari admin teller

(10/08/2026)
- Refactor menu dan admin

(14/08/2026)
- Menyelesaikan lifecycle pinjaman dan sistem notifikasi scheduler
- Menambahkan pengujian reminder dan jatuh tempo pinjaman
- Menambahkan notifikasi deposito ARO dan non-ARO
- Menambahkan `id_objek` pada notifikasi untuk membedakan objek deposito
- Menguji beberapa deposito dalam satu nasabah
- Menyelesaikan pengujian integrasi deposito dan pinjaman hingga save/load setelah pembayaran dan pencairan

(17/08/2026)
- Menyelesaikan validasi integritas relasi rekening, deposito, pinjaman, dan notifikasi pada fresh dataset
- Menguji scheduler berulang pada tanggal yang sama serta missed scheduler untuk deposito ARO dan pinjaman
- Menambahkan persistence tanggal proses ARO agar cleanup notifikasi tetap konsisten setelah save/load
- Menguji pembayaran cicilan sebelum jatuh tempo dan mencegah pembayaran cicilan periode berikutnya terlalu cepat
- Menambahkan validasi saldo minimum saat pembayaran cicilan dan memastikan kegagalan pembayaran tidak mengubah state pinjaman
- Menguji pelunasan hingga status `LUNAS` serta penolakan pembayaran setelah pinjaman lunas
- Menguji tanggal ujung bulan dengan pencairan 31 Januari dan penyesuaian jatuh tempo melalui Februari
- Menambahkan masa toleransi tunggakan 7 hari dan denda harian 0,1% dengan batas maksimal 10% dari cicilan
- Mengintegrasikan denda ke pembayaran cicilan tanpa mengurangi pokok atau menggeser jadwal jatuh tempo
- Menguji pembayaran beberapa periode tertunggak, pelunasan dengan denda, dan kegagalan pembayaran tanpa perubahan state
- Memastikan perhitungan denda tetap konsisten setelah save/load dan repeated scheduler

(18/08/2026)
- Memperbaiki relasi objek rekening setelah upgrade dan downgrade
- Menguji relasi rekening dengan deposito dan pinjaman setelah save/load
- Menambahkan penyimpanan multiple riwayat pinjaman berdasarkan NIK dan ID
- Memulihkan pinjaman berjalan berdasarkan status bisnis
- Memperbaiki isolasi penghapusan notifikasi deposito
- Mencegah penutupan rekening yang masih memiliki kewajiban berjalan
- Menolak pembayaran cicilan melalui rekening terblokir
- Menghapus state status pembayaran yang dapat dihitung dari tanggal jatuh tempo

(27/08/2026)
- Memigrasikan layanan utama dari JSON menuju SQLite
- Menambahkan repository dan loader untuk memisahkan persistence dari objek domain
- Membuat transaksi atomik untuk pendaftaran, transaksi saldo, perubahan level, dan penutupan rekening
- Menambahkan pengajuan penutupan yang diproses oleh admin
- Mendukung penyelesaian penutupan melalui penarikan atau pemindahan seluruh saldo
- Mempertahankan rekening tertutup beserta riwayat dan auditnya
- Menggabungkan pengajuan dan penyelesaian penutupan menjadi satu menu dinamis

# Catatan Desain

### 1. Mengapa rekening dibuat sebagai objek baru saat di-upgrade atau downgrade?

Jawaban:
Karena setiap jenis rekening memiliki perilaku yang berbeda (limit harian, bunga, saldo minimal).
Daripada hanya mengubah atribut level, lebih baik membuat rekening baru yang sesuai dengan perilaku masing-masing.

### 2. Mengapa logika transaksi dipindahkan ke `TransaksiService`?

Jawaban:
Agar logika transaksi terpusat di `TransaksiService` dan terpisah dari input serta tampilan antarmuka.

### 3. Mengapa notifikasi memiliki `referensi_id` dan `id_objek`?

Jawaban:
`referensi_id` menunjukkan domain atau jenis objek yang dirujuk, sedangkan `id_objek` menunjukkan entitas spesifik yang memiliki notifikasi tersebut. Dengan demikian beberapa deposito milik nasabah yang sama dapat memiliki notifikasi masing-masing tanpa saling bertabrakan.

### 4. Bagaimana aturan jatuh tempo pada tanggal ujung bulan?

Jawaban:
Jatuh tempo berikutnya dihitung satu bulan dari jatuh tempo sebelumnya. Jika bulan tujuan tidak memiliki tanggal yang sama, tanggal disesuaikan ke hari terakhir bulan tersebut. Tanggal hasil penyesuaian menjadi acuan untuk jatuh tempo berikutnya.

### 5. Mengapa denda tidak disimpan sebagai state pinjaman?

Jawaban:
Denda dihitung dari cicilan tetap, tanggal jatuh tempo, tanggal proses, masa toleransi, dan persentase denda. Karena seluruh sumber perhitungannya sudah tersedia, menyimpan nominal denda akan membuat dua sumber kebenaran yang berisiko tidak sinkron. Perhitungan dinamis juga menjaga hasil tetap konsisten ketika scheduler dijalankan berulang atau sempat terlewat.

### 6. Mengapa keterlambatan tidak menggeser jadwal cicilan?

Jawaban:
Setiap pembayaran menyelesaikan cicilan tertua, lalu jatuh tempo berikutnya dihitung satu bulan dari jatuh tempo sebelumnya, bukan dari tanggal pembayaran. Nasabah yang terlambat tetap dapat mengejar beberapa cicilan, sedangkan keterlambatan tidak berubah menjadi perpanjangan tenor secara otomatis.

### 7. Bagaimana prinsip penambahan state baru?

Jawaban:
State lama dan nilai turunan digunakan terlebih dahulu. State baru hanya ditambahkan jika mewakili informasi bisnis independen yang tidak dapat dihitung kembali secara aman. Prinsip ini mengurangi duplikasi data dan mempermudah integrity check, persistence, serta migrasi menuju database dan web.

### 8. Mengapa status pembayaran tidak disimpan sebagai state?

Jawaban:
Status pembayaran merupakan nilai turunan dari status pinjaman, tanggal jatuh tempo, dan tanggal pemeriksaan. Menyimpannya akan menciptakan dua sumber kebenaran yang dapat tidak sinkron. Kondisi lancar atau menunggak ditentukan secara dinamis melalui perhitungan hari keterlambatan.

### 9. Mengapa SQLite menjadi sumber kebenaran utama, tetapi objek Python tetap digunakan?

Jawaban:
SQLite menyimpan state yang bertahan setelah program berhenti, sedangkan objek Python digunakan untuk menjalankan perilaku bisnis selama aplikasi aktif. Loader bertugas merangkai kembali data database menjadi objek agar service tetap dapat menggunakan desain OOP tanpa menjadikan memori sebagai sumber data utama.

### 10. Mengapa UI, service, repository, dan loader dipisahkan?

Jawaban:
UI menangani input dan pesan pengguna, service menjalankan aturan bisnis serta transaksi, repository menjalankan SQL, dan loader membentuk kembali objek. Pemisahan ini mencegah satu method mengurus tampilan, aturan bisnis, dan penyimpanan sekaligus serta mempermudah migrasi dari terminal menuju web.

### 11. Mengapa commit dan rollback dikelola oleh service?

Jawaban:
Satu fitur bisnis dapat menjalankan beberapa query. Contohnya pendaftaran harus menyimpan nasabah dan rekening pertama, sedangkan transfer harus mengubah dua saldo sekaligus serta menyimpan riwayat dan audit. Service memiliki gambaran lengkap terhadap operasi tersebut, sehingga seluruh query dapat berhasil bersama atau dibatalkan bersama.

### 12. Mengapa beberapa repository menerima koneksi dari luar?

Jawaban:
Koneksi dari luar memungkinkan beberapa query memakai transaksi database yang sama. Repository tidak menutup koneksi yang diterimanya karena kepemilikan commit, rollback, dan close tetap berada pada service yang membuka transaksi tersebut. Method baca yang digunakan secara mandiri tetap boleh membuat dan menutup koneksinya sendiri.

### 13. Mengapa repository tidak mengulang seluruh validasi bisnis?

Jawaban:
Repository bertugas menyimpan data yang sudah diputuskan oleh service. Integritas dasar tetap dijaga oleh primary key, foreign key, NOT NULL, UNIQUE, dan CHECK pada SQLite, sedangkan aturan seperti saldo minimum, limit transfer, dan kelayakan penutupan ditangani oleh service.

### 14. Mengapa riwayat dan audit dipisahkan?

Jawaban:
Riwayat ditujukan kepada nasabah dan melekat pada rekening, sedangkan audit ditujukan untuk pemantauan sistem dan admin. Satu aktivitas dapat menghasilkan keduanya karena tujuan pembaca dan tingkat informasi yang disimpan berbeda.

### 15. Mengapa rekening yang ditutup tidak dihapus?

Jawaban:
Penghapusan akan memutus jejak transaksi, pengajuan, riwayat, audit, deposito, atau pinjaman yang pernah merujuk rekening tersebut. Karena itu penutupan mengubah status dan mengosongkan saldo, sementara record rekening tetap disimpan sebagai data historis.

### 16. Mengapa penutupan rekening menggunakan pengajuan admin?

Jawaban:
Nasabah hanya mengajukan penutupan. Admin memeriksa deposito dan pinjaman berjalan sebelum menyetujui atau menolak. Selama menunggu, rekening tetap aktif. Setelah disetujui, nasabah menyelesaikan saldo melalui penarikan atau pemindahan ke rekening lain, lalu status rekening berubah menjadi `tutup`.

### 17. Mengapa pendaftaran nasabah dan rekening pertama berada dalam satu transaksi?

Jawaban:
Desain mengharuskan nasabah baru langsung memiliki rekening pertama dan bebas memilih jenisnya. Jika salah satu penyimpanan gagal, keduanya harus dibatalkan agar tidak terbentuk nasabah tanpa rekening atau rekening tanpa pemilik yang sah.

### 18. Mengapa file database dan data pribadi tidak ikut dicommit?

Jawaban:
Repository membagikan struktur, kode pembuat database, dan contoh pengujian, bukan state lokal pengguna. Database dapat berisi saldo, PIN, identitas, audit, dan aktivitas pengujian. Pengguna lain dapat membuat database mereka sendiri dari skema yang tersedia tanpa menerima data lokal pengembang.

### 19. Mengapa Flask dipilih lebih dahulu untuk tahap web?

Jawaban:
Flask menyediakan komponen web secara lebih eksplisit sehingga routing, request/response, template, session, autentikasi, dan integrasi service dapat dipelajari satu per satu. Django tetap dapat dievaluasi ketika kebutuhan proyek berkembang dan manfaat fitur bawaannya menjadi lebih besar.

# Refactor Besar
- Memisahkan beberapa fitur bank yang sebelumnya ada di fitur layanan nasabah ke customer service admin
- Menambahkan menu informasi untuk nasabah
- Memisahkan logika transaksi dari inputan data nasabah
- Memisahkan UI nasabah dan admin
