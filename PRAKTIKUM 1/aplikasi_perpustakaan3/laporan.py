import sys
from PyQt5 import QtWidgets, uic
import db_helper


class LaporanWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi("laporan.ui", self)

        self.btnRefresh.clicked.connect(self.refresh)
        self.btnKembali.clicked.connect(self.close)

        self.tableStatistik.setEditTriggers(
            QtWidgets.QAbstractItemView.NoEditTriggers
        )

        self.tableStatistik.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows
        )

        self.tableStatistik.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        self.refresh()

    def refresh(self):

        stats = db_helper.get_general_statistics()

        returned = db_helper.get_return_statistics()

        popular = db_helper.get_most_borrowed_books()

        books = db_helper.get_all_books()

        # Menghitung jumlah judul buku
        self.valTotalJudul.setText(str(len(books)))

        # Total stok buku
        self.valTotalStok.setText(str(stats["total_buku"]))

        # Jumlah peminjaman aktif
        self.valAktif.setText(str(stats["active_loans"]))

        # Jumlah buku yang sudah dikembalikan
        self.valKembali.setText(str(returned["total_kembali"]))

        # Total denda
        denda = stats["total_denda"]

        self.valDenda.setText(
            "Rp {:,.0f}".format(denda).replace(",", ".")
        )

        # Menampilkan buku paling sering dipinjam
        self.tableStatistik.setRowCount(0)

        for row_data in popular:

            row = self.tableStatistik.rowCount()

            self.tableStatistik.insertRow(row)

            for col, value in enumerate(row_data):

                self.tableStatistik.setItem(
                    row,
                    col,
                    QtWidgets.QTableWidgetItem(str(value))
                )

        if not popular:

            self.tableStatistik.setRowCount(1)

            item = QtWidgets.QTableWidgetItem(
                "Belum ada transaksi peminjaman"
            )

            item.setTextAlignment(0x84)

            self.tableStatistik.setItem(0, 0, item)

            self.tableStatistik.setSpan(0, 0, 1, 4)

    def showEvent(self, event):

        super().showEvent(event)

        self.refresh()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    db_helper.init_db()

    window = LaporanWindow()

    window.show()

    sys.exit(app.exec_())