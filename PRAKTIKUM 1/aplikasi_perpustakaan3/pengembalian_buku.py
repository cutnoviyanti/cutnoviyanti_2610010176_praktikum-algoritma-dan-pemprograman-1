import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate
import db_helper


class PengembalianBukuWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi("pengembalian_buku.ui", self)

        # Mengatur tanggal otomatis
        self.dateKembali.setDate(QDate.currentDate())

        # Menghubungkan tombol
        self.btnProses.clicked.connect(
            self.process_return
        )

        self.btnRefresh.clicked.connect(
            self.load_loans
        )

        self.btnKembali.clicked.connect(
            self.close
        )

        # Mengatur tabel
        self.tablePengembalian.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )

        self.tablePengembalian.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )

        self.tablePengembalian.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        self.tablePengembalian.cellClicked.connect(
            self.select_row
        )

        # Memuat data
        self.load_loans()

    def load_loans(self):

        # Mengambil data peminjaman aktif
        rows = db_helper.get_active_loans()

        self.cmbPinjam.clear()
        self.tablePengembalian.setRowCount(0)

        for data in rows:

            id_pinjam = data[0]
            nama = data[1]
            judul = data[3]

            # Memasukkan data ke combo box
            self.cmbPinjam.addItem(
                f"{id_pinjam} - {nama} - {judul}",
                id_pinjam
            )

            # Memasukkan data ke tabel
            row = self.tablePengembalian.rowCount()

            self.tablePengembalian.insertRow(row)

            for col, value in enumerate(data[:6]):

                item = QtWidgets.QTableWidgetItem(
                    str(value)
                )

                self.tablePengembalian.setItem(
                    row, col, item
                )

        self.btnProses.setEnabled(bool(rows))

    def select_row(self, row, column):

        item = self.tablePengembalian.item(row, 0)

        if item:

            index = self.cmbPinjam.findData(
                item.text()
            )

            if index >= 0:
                self.cmbPinjam.setCurrentIndex(index)

    def process_return(self):

        id_pinjam = self.cmbPinjam.currentData()

        if not id_pinjam:

            QtWidgets.QMessageBox.warning(
                self,
                "Peringatan",
                "Tidak ada peminjaman aktif!"
            )

            return

        tanggal = self.dateKembali.date().toString(
            "yyyy-MM-dd"
        )

        denda = self.spinDenda.value()

        # Memproses pengembalian melalui database
        sukses, pesan = db_helper.return_book(
            id_pinjam,
            tanggal,
            denda
        )

        if sukses:

            QtWidgets.QMessageBox.information(
                self,
                "Berhasil",
                pesan
            )

            self.spinDenda.setValue(0)

            self.dateKembali.setDate(
                QDate.currentDate()
            )

            self.load_loans()

        else:

            QtWidgets.QMessageBox.warning(
                self,
                "Gagal",
                pesan
            )


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    db_helper.init_db()

    window = PengembalianBukuWindow()

    window.show()

    sys.exit(app.exec_())