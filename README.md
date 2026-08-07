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

## Konsep yang sudah Dipelajari dan dipakai
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

## Struktur Folder
bank_djago/
│
├── core/
├── services/
├── storage/
├── ui/
├── utils/
├── main.py

### 📑 Fitur Saat Ini (22 Juli - 05 Agustus 2026)

## 📌 Versi Pengembangan

### `v0.1` - Pembuatan Objek Esensial
Memisahkan tanggung jawab objek (*Separation of Concerns*).

- `Bank`: Wadah penyimpanan data dan eksekutor logika utama perbankan.
- `Nasabah`: Objek pemilik rekening yang terdaftar secara resmi.
- `Rekening`: Entitas keuangan yang menangani saldo, PIN, dan riwayat transaksi.

### `v0.2` - Fundamental
- **Logika Transaksi:** Setor tunai, tarik tunai, dan transfer antar-rekening.
- **Keamanan & Validasi:** Keberadaan rekening, validasi PIN, dan saldo minimum.
- **Data Persistence:** Penyimpanan dan pemuatan menggunakan JSON.

### `v0.3` - Perluasan & Konsep OOP Lanjutan
- **Inheritance:** Variasi jenis rekening dari satu parent class.
- **Fitur Finansial:** Bunga, limit transfer harian, dan saldo minimum.

### `v0.4` - Manajemen Status Rekening
- **Status Lifecycle:** Aktif, diblokir, dan ditutup.
- **Fitur Dinamis:** Upgrade dan downgrade jenis rekening.

### `v0.5` - Audit & Rekapitulasi Data
- **Audit System:** Pencatatan aktivitas transaksi.
- **Bank Summary:** Rekap nasabah, rekening aktif, dan akumulasi kas.

### `v0.6` - Refactor & Penyempurnaan Arsitektur
- **Pemisahan Logika Transaksi:** Memindahkan aturan transaksi ke `TransaksiService`.
- **Pemisahan UI Teller:** Input dan komunikasi dengan nasabah ditangani `TellerUI`.
- **Pemisahan Riwayat:** Log transaksi ditangani pada layer transaksi.
- **Penyederhanaan Struktur:** Menghapus perantara yang tidak lagi memiliki tanggung jawab jelas.
- **UI Terminal:** Menambahkan sistem warna pada header dan membedakan level navigasi.

### `v0.7` - Manajemen Admin
- **Admin:** Pengelolaan nasabah dan rekening.
- **Audit Log:** Pemantauan aktivitas bank.
- **Rekapitulasi:** Penyajian laporan administrasi.

## 🚧 Sedang & Akan Dikembangkan (Roadmap)
-  **Sisi Admin:** Fitur manajemen seluruh nasabah dan laporan *audit log*.
-  **Fitur Deposito & Pinjaman:** Perhitungan bunga, tenor, denda pencairan awal, dan skema cicilan.
-  *Integrasi Database:** Bermigrasi dari simpanan JSON ke database relasional `SQLite`.
-  *Web Interface:** Mengembangkan antarmuka berbasis web menggunakan *framework* `Django`.

### `v0.7` - Deposito
- **Struktur Deposito:** Membuat entitas deposito.
- **Pembukaan Deposito:** Validasi nominal minimum, saldo minimum, tenor, dan bunga.
- **Jatuh Tempo:** Perhitungan tanggal jatuh tempo berdasarkan tenor.
- **Riwayat & Audit:** Mencatat pembukaan deposito.
- **Pencairan Deposito:** Pencairan saat jatuh tempo dan perhitungan hasil deposito.
- **UI Deposito:** Menu dan alur input deposito.

### `v0.9` - Pinjaman
- **Pengajuan Pinjaman**
- **Tenor dan Bunga**
- **Perhitungan Cicilan**
- **Denda Keterlambatan**
- **Pelunasan**

### `v1.0` - Penyempurnaan Sistem
- Stabilitas dan validasi keseluruhan sistem.
- Pengujian fitur utama.
- Perapian struktur proyek.
- Dokumentasi.

### `v1.1` - Database
- Migrasi dari JSON ke SQLite.
- Pemisahan layer penyimpanan data.
- Penyesuaian model dan service terhadap database.

### `v2.0` - Web Interface
- Migrasi antarmuka terminal ke Django.
- UI berbasis web.
- Integrasi sistem autentikasi.
- Dashboard nasabah dan admin.

---

##Change Log

(05/08/2026)
- Memisahkan menu admin
(06/08/2026)
- Memisahkan semua service dari bank ke admin
(07/08/2026)
- Refactor Transaksi dari admin teller

# Catatan Desain
1. Mengapa rekening dibuat sebagai objek baru saat diupgrade atau downgrade?
Jawaban:
Karena setiap jenis rekening memiliki perilaku yang berbeda(limit harian,bunga,saldo minimal).
Daripada hanya mengubah atribut level,lebih baik membuat rekening baru yang sesuai dengan perilaku
masing-masing.


# Refactor Besar
- Memisahkan beberapa fitur bank yang sebelumnya ada di fitur layanan nasabah ke customer service admin
- Menambahkan menu informasi untuk nasabah
