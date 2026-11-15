APLIKASI PERPUSTAKAAN - PyQt5

Isi folder:
- main.py / main.ui: menu utama
- kelola_buku.py / kelola_buku.ui: tambah, edit, hapus, dan lihat data buku
- pinjam_buku.py / pinjam_buku.ui: transaksi peminjaman
- db_helper.py: database SQLite dan fungsi data

Instalasi:
    pip install PyQt5

Jalankan:
    python main.py

Database perpustakaan.db akan dibuat otomatis saat aplikasi pertama dijalankan.
Data contoh buku dari modul akan dimasukkan jika tabel buku masih kosong.

Catatan:
Modul PDF yang diberikan memuat implementasi menu utama, pengelolaan buku,
peminjaman, dan fungsi database termasuk pengembalian/statistik. Namun PDF
belum memuat desain/form Python untuk pengembalian. Tombol pengembalian
sementara menampilkan pemberitahuan; laporan statistik menggunakan fungsi
database yang tersedia.
