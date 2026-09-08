# Arsip Pengujian Legacy

Folder ini mengumpulkan kode pengujian lama yang sudah tidak menjadi jalur utama pengujian Bank Djago.

- `json/` berisi pengujian yang bergantung pada arsitektur penyimpanan JSON lama.
- `deposito/` berisi skenario deposito lama yang sudah digantikan pengujian SQLite yang lebih terarah.
- `sumber_asli/` menyimpan file besar sebelum pengujian dipecah ke folder `utils/tests/skenario/`.

Sebagian besar arsip menggunakan ekstensi `.txt` agar tidak dianggap sebagai test Python aktif oleh IDE/test runner. Isi tetap dipertahankan sebagai catatan belajar dan referensi historis.

File yang perilakunya masih relevan tetapi hanya memakai harness lama tidak dimasukkan ke sini sampai penggantinya dimigrasikan ke arsitektur SQLite saat ini.
