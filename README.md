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
* **Konsep Utama:** Object-Oriented Programming (OOP), Data Encapsulation, Inheritance, Data Validation, File Handling (JSON)

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
├── storage/
├── ui/
├── utils/
├── main.py
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
- [x] **Pemisahan UI Teller:** Input dan komunikasi dengan nasabah ditangani `TellerUI`.
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
- [ ] **Denda Keterlambatan**
- [ ] **Status Tunggakan**

### `v1.0` - Penyempurnaan Sistem
Fokus pada stabilitas, pengujian, integritas data, dan kesiapan arsitektur sebelum migrasi database dan web.

- [x] **Scheduler:** Otomatisasi proses bunga, biaya admin, limit, jatuh tempo, dan notifikasi.
- [x] **Notification System:** Sistem notifikasi berbasis referensi dan `id_objek`.
- [x] **Pengujian Lifecycle Pinjaman:** Pengajuan → persetujuan → pencairan → cicilan → jatuh tempo → pembayaran → pelunasan.
- [x] **Pengujian Deposito ARO & Non-ARO:** Pengujian reminder, jatuh tempo, pencairan, dan perpanjangan otomatis.
- [x] **Pengujian Multiple Deposito:** Memastikan notifikasi beberapa deposito dalam satu nasabah tidak saling bertabrakan.
- [x] **Pengujian Integrasi:** Menguji alur deposito dan pinjaman dalam satu nasabah, scheduler berbasis tanggal simulasi, pergantian notifikasi, ARO/non-ARO, pembayaran, pencairan, serta save/load setelah perubahan.
- [ ] **Denda Keterlambatan:** Implementasi aturan denda dan konsekuensi tunggakan.
- [ ] **Status Tunggakan:** Menambahkan lifecycle khusus untuk cicilan yang melewati jatuh tempo.
- [x] **Validasi Integritas Data:** Memastikan relasi nasabah, rekening, deposito, pinjaman, dan notifikasi tetap konsisten setelah save/load.
- [x] **Pengujian Edge Case:** Menguji repeated scheduler, missed scheduler, multiple deposito, save/load, pembayaran sebelum jatuh tempo, pencegahan pembayaran periode berikutnya terlalu cepat, saldo tidak cukup, status lunas, dan tanggal ujung bulan.
- [ ] **Perapian Struktur Proyek:** Refactor bagian yang masih memiliki tanggung jawab tumpang tindih.
- [ ] **Dokumentasi:** Melengkapi dokumentasi arsitektur, alur bisnis, dan keputusan desain.

### `v1.1` - Database
- [ ] Migrasi dari JSON ke SQLite.
- [ ] Pemisahan layer penyimpanan data.
- [ ] Penyesuaian model dan service terhadap database.
- [ ] Validasi relasi dan integritas data pada database.

### `v2.0` - Web Interface
- [ ] Migrasi antarmuka terminal ke Django.
- [ ] UI berbasis web.
- [ ] Integrasi sistem autentikasi.
- [ ] Dashboard nasabah dan admin.
- [ ] Integrasi business logic yang sudah dibangun pada backend.

---

## 🚧 Roadmap Utama

- [x] Sistem rekening dan transaksi dasar
- [x] Manajemen admin
- [x] Audit dan rekapitulasi
- [x] Deposito
- [x] Pinjaman
- [x] Scheduler
- [x] Notification System
- [ ] Denda keterlambatan dan tunggakan
- [x] Penyempurnaan testing dan validasi integritas data
- [ ] Migrasi database ke SQLite
- [ ] Migrasi ke Django
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

# Refactor Besar
- Memisahkan beberapa fitur bank yang sebelumnya ada di fitur layanan nasabah ke customer service admin
- Menambahkan menu informasi untuk nasabah
- Memisahkan logika transaksi dari inputan data nasabah
- Memisahkan UI nasabah dan admin
