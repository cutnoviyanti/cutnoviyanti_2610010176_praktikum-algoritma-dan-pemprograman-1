import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate
import db_helper

class PinjamBukuWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("pinjam_buku.ui", self)
        self.datePinjam.setDate(QDate.currentDate())
        self.btnPinjam.clicked.connect(self.borrow_book)
        self.btnBersihkan.clicked.connect(self.clear_fields)
        self.btnKembali.clicked.connect(self.close)
        self.tablePeminjaman.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.load_books_combo()
        self.load_active_loans()

    def load_books_combo(self):
        self.cmbBuku.clear()
        for book in db_helper.get_all_books():
            id_buku, judul, _, _, _, stok = book
            if stok > 0:
                self.cmbBuku.addItem(f"{id_buku} - {judul} (Stok: {stok})", id_buku)

    def load_active_loans(self):
        self.tablePeminjaman.setRowCount(0)
        for r, row_data in enumerate(db_helper.get_active_loans()):
            self.tablePeminjaman.insertRow(r)
            for c, data in enumerate(row_data):
                self.tablePeminjaman.setItem(r, c, QtWidgets.QTableWidgetItem(str(data)))

    def borrow_book(self):
        loan_id = self.txtIdPinjam.text().strip()
        borrower = self.txtNamaPeminjam.text().strip()
        if not loan_id or not borrower:
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal", "ID Pinjam dan Nama Peminjam harus diisi!")
            return
        if self.cmbBuku.currentIndex() == -1:
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal", "Buku harus dipilih!")
            return
        book_id = self.cmbBuku.currentData()
        date = self.datePinjam.date().toString("yyyy-MM-dd")
        duration = self.spinDurasi.value()
        success, message = db_helper.add_loan(loan_id, borrower, book_id, date, duration)
        if success:
            QtWidgets.QMessageBox.information(self, "Berhasil", message)
            self.load_active_loans()
            self.load_books_combo()
            self.clear_fields()
        else:
            QtWidgets.QMessageBox.critical(self, "Gagal", message)

    def clear_fields(self):
        self.txtIdPinjam.clear()
        self.txtNamaPeminjam.clear()
        self.datePinjam.setDate(QDate.currentDate())
        self.spinDurasi.setValue(7)
        if self.cmbBuku.count():
            self.cmbBuku.setCurrentIndex(0)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    db_helper.init_db()
    window = PinjamBukuWindow()
    window.show()
    sys.exit(app.exec_())
