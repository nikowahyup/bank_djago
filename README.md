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

#### `v0.1` - Pembuatan Objek Esensial
Memisahkan tanggung jawab objek (*Separation of Concerns*):
* `Bank`: Wadah penyimpanan data dan eksekutor logika utama perbankan.
* `Nasabah`: Objek pemilik rekening yang terdaftar secara resmi.
* `Rekening`: Entitas keuangan yang menangani saldo (dengan enkapsulasi), PIN, serta penyimpanan riwayat transaksi.

#### `v0.2` - Fundamental 
* **Logika Transaksi:** Setor tunai, tarik tunai, dan transfer antar-rekening.
* **Keamanan & Validasi:** Pengecekan keberadaan rekening, validasi PIN, dan syarat minimal setoran/saldo.
* **Data Persistence:** Penyimpanan dan pemuatan data menggunakan format `JSON`.

#### `v0.3` - Perluasan & Konsep OOP Lanjutan
* **Inheritance (Pewarisan):** Membuat variasi jenis rekening dari satu *parent class*.
* **Fitur Finansial:** Penerapan sistem bunga sederhana, limit transfer harian berbeda tiap jenis rekening, dan syarat minimal saldo mengendap.

#### `v0.4` - Manajemen Status Rekening
* **Status Lifecycle:** Penanganan status rekening (`Aktif`, `Diblokir`, `Ditutup`).
* **Fitur Dinamis:** Mekanisme *upgrade* dan *downgrade* jenis rekening berdasarkan syarat tertentu.

#### `v0.5` - Audit & Rekapitulasi Data
* **Audit System:** Pencatatan dan pemantauan riwayat aktivitas transaksi menyeluruh.
* **Bank Summary:** Rekap data tingkat tinggi (Total nasabah terdaftar, jumlah rekening aktif, total akumulasi kas).

---

## 🚧 Sedang & Akan Dikembangkan (Roadmap)
-  **Sisi Admin:** Fitur manajemen seluruh nasabah dan laporan *audit log*.
-  **Fitur Deposito & Pinjaman:** Perhitungan bunga, tenor, denda pencairan awal, dan skema cicilan.
-  *Integrasi Database:** Bermigrasi dari simpanan JSON ke database relasional `SQLite`.
-  *Web Interface:** Mengembangkan antarmuka berbasis web menggunakan *framework* `Django`.

##Change Log

(05/08/2026)
- Memisahkan menu admin
(06/08/2026)
- Memisahkan semua service dari bank ke admin

# Catatan Desain
1. Mengapa rekening dibuat sebagai objek baru saat diupgrade atau downgrade?
Jawaban:
Karena setiap jenis rekening memiliki perilaku yang berbeda(limit harian,bunga,saldo minimal).
Daripada hanya mengubah atribut level,lebih baik membuat rekening baru yang sesuai dengan perilaku
masing-masing.


# Refactor Besar
- Memisahkan beberapa fitur bank yang sebelumnya ada di fitur layanan nasabah ke customer service admin
- Menambahkan menu informasi untuk nasabah
