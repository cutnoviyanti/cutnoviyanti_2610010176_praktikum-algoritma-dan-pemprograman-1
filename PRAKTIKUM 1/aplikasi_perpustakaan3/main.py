
import sys
from pathlib import Path

from PyQt5 import QtWidgets, uic

import db_helper

from kelola_buku import KelolaBukuWindow
from pinjam_buku import PinjamBukuWindow
from pengembalian_buku import PengembalianBukuWindow
from laporan import LaporanWindow


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # Menentukan lokasi folder project
        self.project_dir = Path(__file__).resolve().parent

        # Memastikan file UI dan database terbaca
        import os
        os.chdir(self.project_dir)

        # Memuat tampilan menu utama
        uic.loadUi(
            str(self.project_dir / "main.ui"),
            self
        )

        # Membuat database jika belum tersedia
        db_helper.init_db()

        # Menyimpan objek setiap halaman
        self.kelola_buku_win = None
        self.pinjam_buku_win = None
        self.pengembalian_win = None
        self.laporan_win = None

        # Menghubungkan tombol menu utama
        self.btnKelolaBuku.clicked.connect(
            self.open_kelola_buku
        )

        self.btnPinjamBuku.clicked.connect(
            self.open_pinjam_buku
        )

        self.btnPengembalian.clicked.connect(
            self.open_pengembalian
        )

        self.btnLaporan.clicked.connect(
            self.open_laporan
        )

        self.btnKeluar.clicked.connect(
            self.close
        )

    # ==============================
    # HALAMAN KELOLA DATA BUKU
    # ==============================

    def open_kelola_buku(self):

        if self.kelola_buku_win is None:
            self.kelola_buku_win = KelolaBukuWindow()

        self.kelola_buku_win.show()
        self.kelola_buku_win.raise_()
        self.kelola_buku_win.activateWindow()

    # ==============================
    # HALAMAN PEMINJAMAN BUKU
    # ==============================

    def open_pinjam_buku(self):

        if self.pinjam_buku_win is None:
            self.pinjam_buku_win = PinjamBukuWindow()

        self.pinjam_buku_win.load_books_combo()
        self.pinjam_buku_win.load_active_loans()

        self.pinjam_buku_win.show()
        self.pinjam_buku_win.raise_()
        self.pinjam_buku_win.activateWindow()

    # ==============================
    # HALAMAN PENGEMBALIAN BUKU
    # ==============================

    def open_pengembalian(self):

        if self.pengembalian_win is None:
            self.pengembalian_win = PengembalianBukuWindow()

        self.pengembalian_win.load_loans()

        self.pengembalian_win.show()
        self.pengembalian_win.raise_()
        self.pengembalian_win.activateWindow()

    # ==============================
    # HALAMAN LAPORAN & STATISTIK
    # ==============================

    def open_laporan(self):

        if self.laporan_win is None:
            self.laporan_win = LaporanWindow()

        self.laporan_win.refresh()

        self.laporan_win.show()
        self.laporan_win.raise_()
        self.laporan_win.activateWindow()


# ==============================
# MENJALANKAN APLIKASI
# ==============================

if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec_())