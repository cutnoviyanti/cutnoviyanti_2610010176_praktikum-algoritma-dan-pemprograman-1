import sys
from PyQt5 import QtWidgets, uic
import db_helper

class KelolaBukuWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("kelola_buku.ui", self)
        self.btnTambah.clicked.connect(self.add_book)
        self.btnEdit.clicked.connect(self.edit_book)
        self.btnHapus.clicked.connect(self.delete_book)
        self.btnBersihkan.clicked.connect(self.clear_fields)
        self.btnKembali.clicked.connect(self.close)
        self.tableBuku.itemSelectionChanged.connect(self.on_table_select)
        self.tableBuku.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.load_books()

    def load_books(self):
        self.tableBuku.setRowCount(0)
        for r, row_data in enumerate(db_helper.get_all_books()):
            self.tableBuku.insertRow(r)
            for c, data in enumerate(row_data):
                self.tableBuku.setItem(r, c, QtWidgets.QTableWidgetItem(str(data)))

    def on_table_select(self):
        selected = self.tableBuku.selectionModel().selectedRows()
        if not selected:
            return
        row = selected[0].row()
        fields = [self.txtIdBuku, self.txtJudul, self.txtPengarang,
                  self.txtPenerbit, self.txtTahun, self.txtStok]
        for col, field in enumerate(fields):
            field.setText(self.tableBuku.item(row, col).text())
        self.txtIdBuku.setReadOnly(True)

    def validate_inputs(self):
        values = [self.txtIdBuku.text().strip(), self.txtJudul.text().strip(),
                  self.txtPengarang.text().strip(), self.txtPenerbit.text().strip(),
                  self.txtTahun.text().strip(), self.txtStok.text().strip()]
        if not all(values):
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal", "Semua kolom harus diisi!")
            return None
        try:
            year, stock = int(values[4]), int(values[5])
            if year < 0 or stock < 0:
                raise ValueError
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal",
                "Tahun Terbit dan Stok harus berupa angka bulat positif!")
            return None
        return (*values[:4], year, stock)

    def add_book(self):
        data = self.validate_inputs()
        if data is None:
            return
        ok, msg = db_helper.add_book(*data)
        self.show_result(ok, msg)

    def edit_book(self):
        if not self.txtIdBuku.isReadOnly():
            QtWidgets.QMessageBox.warning(self, "Edit Gagal", "Pilih buku dari tabel terlebih dahulu untuk diedit!")
            return
        data = self.validate_inputs()
        if data is None:
            return
        answer = QtWidgets.QMessageBox.question(self, "Konfirmasi Edit",
            f"Apakah Anda yakin ingin memperbarui data buku dengan ID {data[0]}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if answer == QtWidgets.QMessageBox.Yes:
            self.show_result(*db_helper.update_book(*data))

    def delete_book(self):
        book_id = self.txtIdBuku.text().strip()
        if not book_id or not self.txtIdBuku.isReadOnly():
            QtWidgets.QMessageBox.warning(self, "Hapus Gagal", "Pilih buku dari tabel terlebih dahulu untuk dihapus!")
            return
        answer = QtWidgets.QMessageBox.question(self, "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus buku dengan ID {book_id}?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if answer == QtWidgets.QMessageBox.Yes:
            self.show_result(*db_helper.delete_book(book_id))

    def show_result(self, success, message):
        box = QtWidgets.QMessageBox.information if success else QtWidgets.QMessageBox.critical
        box(self, "Berhasil" if success else "Gagal", message)
        if success:
            self.load_books()
            self.clear_fields()

    def clear_fields(self):
        for field in (self.txtIdBuku, self.txtJudul, self.txtPengarang,
                      self.txtPenerbit, self.txtTahun, self.txtStok):
            field.clear()
        self.txtIdBuku.setReadOnly(False)
        self.tableBuku.clearSelection()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    db_helper.init_db()
    window = KelolaBukuWindow()
    window.show()
    sys.exit(app.exec_())
