

import sqlite3
import os

# ==========================================
# KONFIGURASI DATABASE
# ==========================================

DB_NAME = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "perpustakaan.db"
)


def get_connection():
    """Membuat koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==========================================
# INISIALISASI DATABASE
# ==========================================

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Tabel Buku
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buku (
                id_buku TEXT PRIMARY KEY,
                judul TEXT NOT NULL,
                pengarang TEXT NOT NULL,
                penerbit TEXT NOT NULL,
                tahun INTEGER NOT NULL,
                stok INTEGER NOT NULL
            )
        """)

        # Tabel Peminjaman
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS peminjaman (
                id_pinjam TEXT PRIMARY KEY,
                nama_peminjam TEXT NOT NULL,
                id_buku TEXT NOT NULL,
                tanggal_pinjam TEXT NOT NULL,
                durasi INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Dipinjam',
                FOREIGN KEY (id_buku)
                    REFERENCES buku(id_buku)
            )
        """)

        # Tabel Pengembalian
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pengembalian (
                id_kembali INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pinjam TEXT NOT NULL,
                tanggal_kembali TEXT NOT NULL,
                denda REAL NOT NULL,
                FOREIGN KEY (id_pinjam)
                    REFERENCES peminjaman(id_pinjam)
            )
        """)

        # Data buku awal jika tabel masih kosong
        cursor.execute("SELECT COUNT(*) FROM buku")

        if cursor.fetchone()[0] == 0:
            dummy_books = [
                (
                    "B001",
                    "Algoritma & Struktur Data",
                    "Rinaldi Munir",
                    "Informatika",
                    2020,
                    5
                ),
                (
                    "B002",
                    "Python untuk Pemula",
                    "Jubilee Enterprise",
                    "Elex Media",
                    2021,
                    3
                ),
                (
                    "B003",
                    "Pemrograman GUI dengan Python dan PyQt",
                    "Budi Raharjo",
                    "Informatika",
                    2019,
                    2
                ),
                (
                    "B004",
                    "Dasar-Dasar Rekayasa Perangkat Lunak",
                    "Rosa A.S.",
                    "Modula",
                    2018,
                    4
                )
            ]

            cursor.executemany("""
                INSERT INTO buku
                (id_buku, judul, pengarang, penerbit, tahun, stok)
                VALUES (?, ?, ?, ?, ?, ?)
            """, dummy_books)

        conn.commit()

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()


# ==========================================
# OPERASI DATA BUKU (CRUD)
# ==========================================

def get_all_books():
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM buku ORDER BY id_buku")
        return cursor.fetchall()

    finally:
        conn.close()


def get_book_by_id(id_buku):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM buku WHERE id_buku = ?",
            (id_buku,)
        )
        return cursor.fetchone()

    finally:
        conn.close()


def add_book(id_buku, judul, pengarang, penerbit, tahun, stok):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO buku
            (id_buku, judul, pengarang, penerbit, tahun, stok)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_buku, judul, pengarang,
            penerbit, tahun, stok
        ))

        conn.commit()
        return True, "Buku berhasil ditambahkan!"

    except sqlite3.IntegrityError:
        return False, "ID Buku sudah terdaftar atau data tidak valid."

    except sqlite3.Error as e:
        return False, str(e)

    finally:
        conn.close()


def update_book(id_buku, judul, pengarang, penerbit, tahun, stok):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE buku
            SET judul = ?,
                pengarang = ?,
                penerbit = ?,
                tahun = ?,
                stok = ?
            WHERE id_buku = ?
        """, (
            judul, pengarang, penerbit,
            tahun, stok, id_buku
        ))

        conn.commit()

        if cursor.rowcount > 0:
            return True, "Buku berhasil diperbarui!"

        return False, "ID Buku tidak ditemukan."

    except sqlite3.Error as e:
        return False, str(e)

    finally:
        conn.close()


def delete_book(id_buku):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM buku WHERE id_buku = ?",
            (id_buku,)
        )

        conn.commit()

        if cursor.rowcount > 0:
            return True, "Buku berhasil dihapus!"

        return False, "ID Buku tidak ditemukan."

    except sqlite3.IntegrityError:
        return False, "Buku tidak bisa dihapus karena terikat transaksi."

    except sqlite3.Error as e:
        return False, str(e)

    finally:
        conn.close()


# ==========================================
# OPERASI PEMINJAMAN BUKU
# ==========================================

def get_active_loans():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.id_pinjam,
                p.nama_peminjam,
                p.id_buku,
                b.judul,
                p.tanggal_pinjam,
                p.durasi,
                p.status
            FROM peminjaman p
            JOIN buku b ON p.id_buku = b.id_buku
            WHERE p.status = 'Dipinjam'
            ORDER BY p.tanggal_pinjam DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()


def get_loan_by_id(id_pinjam):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.id_pinjam,
                p.nama_peminjam,
                p.id_buku,
                b.judul,
                p.tanggal_pinjam,
                p.durasi,
                p.status
            FROM peminjaman p
            JOIN buku b ON p.id_buku = b.id_buku
            WHERE p.id_pinjam = ?
        """, (id_pinjam,))

        return cursor.fetchone()

    finally:
        conn.close()


def add_loan(
    id_pinjam,
    nama_peminjam,
    id_buku,
    tanggal_pinjam,
    durasi
):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Periksa ID peminjaman
        cursor.execute("""
            SELECT id_pinjam
            FROM peminjaman
            WHERE id_pinjam = ?
        """, (id_pinjam,))

        if cursor.fetchone():
            return False, "ID Pinjam sudah terdaftar."

        # Periksa buku dan stok
        cursor.execute("""
            SELECT stok, judul
            FROM buku
            WHERE id_buku = ?
        """, (id_buku,))

        book = cursor.fetchone()

        if not book:
            return False, "Buku tidak ditemukan."

        stok, judul = book

        if stok <= 0:
            return False, f"Stok buku '{judul}' sedang habis."

        # Simpan transaksi peminjaman
        cursor.execute("""
            INSERT INTO peminjaman (
                id_pinjam,
                nama_peminjam,
                id_buku,
                tanggal_pinjam,
                durasi,
                status
            )
            VALUES (?, ?, ?, ?, ?, 'Dipinjam')
        """, (
            id_pinjam,
            nama_peminjam,
            id_buku,
            tanggal_pinjam,
            durasi
        ))

        # Kurangi stok buku
        cursor.execute("""
            UPDATE buku
            SET stok = stok - 1
            WHERE id_buku = ?
        """, (id_buku,))

        conn.commit()

        return True, "Transaksi peminjaman berhasil dicatat!"

    except sqlite3.Error as e:
        conn.rollback()
        return False, str(e)

    finally:
        conn.close()


# ==========================================
# OPERASI PENGEMBALIAN BUKU
# ==========================================

def return_book(id_pinjam, tanggal_kembali, denda):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Periksa transaksi peminjaman
        cursor.execute("""
            SELECT id_buku, status
            FROM peminjaman
            WHERE id_pinjam = ?
        """, (id_pinjam,))

        loan = cursor.fetchone()

        if not loan:
            return False, "Transaksi peminjaman tidak ditemukan."

        id_buku, status = loan

        if status == "Kembali":
            return False, "Buku ini sudah pernah dikembalikan."

        # Simpan data pengembalian
        cursor.execute("""
            INSERT INTO pengembalian
            (id_pinjam, tanggal_kembali, denda)
            VALUES (?, ?, ?)
        """, (
            id_pinjam,
            tanggal_kembali,
            denda
        ))

        # Ubah status peminjaman
        cursor.execute("""
            UPDATE peminjaman
            SET status = 'Kembali'
            WHERE id_pinjam = ?
        """, (id_pinjam,))

        # Tambahkan kembali stok buku
        cursor.execute("""
            UPDATE buku
            SET stok = stok + 1
            WHERE id_buku = ?
        """, (id_buku,))

        conn.commit()

        return True, "Buku berhasil dikembalikan!"

    except sqlite3.Error as e:
        conn.rollback()
        return False, str(e)

    finally:
        conn.close()


# ==========================================
# STATISTIK DAN LAPORAN
# ==========================================

def get_general_statistics():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Total seluruh eksemplar buku,
        # termasuk buku yang sedang dipinjam
        cursor.execute("""
            SELECT
                COALESCE((SELECT SUM(stok) FROM buku), 0)
                +
                (SELECT COUNT(*)
                 FROM peminjaman
                 WHERE status = 'Dipinjam')
        """)

        total_buku = cursor.fetchone()[0] or 0

        # Total peminjaman yang masih aktif
        cursor.execute("""
            SELECT COUNT(*)
            FROM peminjaman
            WHERE status = 'Dipinjam'
        """)

        active_loans = cursor.fetchone()[0] or 0

        # Total denda pengembalian
        cursor.execute("""
            SELECT COALESCE(SUM(denda), 0)
            FROM pengembalian
        """)

        total_denda = cursor.fetchone()[0] or 0.0

        return {
            "total_buku": total_buku,
            "active_loans": active_loans,
            "total_denda": total_denda
        }

    finally:
        conn.close()


def get_return_statistics():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM pengembalian
        """)

        total_kembali = cursor.fetchone()[0] or 0

        return {
            "total_kembali": total_kembali
        }

    finally:
        conn.close()


def get_most_borrowed_books():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                b.id_buku,
                b.judul,
                b.pengarang,
                COUNT(p.id_pinjam) AS jumlah_dipinjam
            FROM peminjaman p
            JOIN buku b ON p.id_buku = b.id_buku
            GROUP BY b.id_buku, b.judul, b.pengarang
            ORDER BY jumlah_dipinjam DESC
        """)

        return cursor.fetchall()

    finally:
        conn.close()