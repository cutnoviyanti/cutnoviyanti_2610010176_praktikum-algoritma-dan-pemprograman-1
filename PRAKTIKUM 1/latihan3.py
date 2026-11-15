import sys
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtCore import Qt, QDate


class LibrarySystem(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistem Peminjaman Buku")
        self.setGeometry(300, 300, 900, 600)

        self.init_db()
        self.setup_ui()

    # ==================================
    # 1. DATABASE
    # ==================================

    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("library.db")

        if not self.db.open():
            raise RuntimeError(
                "Database gagal dibuka: " + self.db.lastError().text()
            )

        query = QSqlQuery(self.db)

        query.exec_("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                stock INTEGER DEFAULT 1
            )
        """)

        query.exec_("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                borrower TEXT,
                loan_date TEXT,
                return_date TEXT,
                status TEXT DEFAULT 'active'
            )
        """)

    # ==================================
    # 2. QUERY HELPER
    # ==================================

    def execute_query(self, sql, values=None):
        query = QSqlQuery(self.db)

        if values is not None:
            query.prepare(sql)

            for value in values:
                query.addBindValue(value)

            success = query.exec_()
        else:
            success = query.exec_(sql)

        if not success:
            QMessageBox.critical(
                self,
                "Database Error",
                query.lastError().text()
            )
            return None

        return query

    # ==================================
    # 3. SETUP USER INTERFACE
    # ==================================

    def setup_ui(self):

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # TAB 1: KELOLA BUKU

        books_tab = QWidget()
        tabs.addTab(books_tab, "Kelola Buku")

        books_layout = QVBoxLayout(books_tab)

        form_layout = QGridLayout()

        self.title_input = QLineEdit()
        self.author_input = QLineEdit()

        self.stock_input = QSpinBox()
        self.stock_input.setRange(1, 100)

        form_layout.addWidget(QLabel("Judul:"), 0, 0)
        form_layout.addWidget(self.title_input, 0, 1)

        form_layout.addWidget(QLabel("Penulis:"), 1, 0)
        form_layout.addWidget(self.author_input, 1, 1)

        form_layout.addWidget(QLabel("Stok:"), 2, 0)
        form_layout.addWidget(self.stock_input, 2, 1)

        btn_layout = QHBoxLayout()

        self.add_book_btn = QPushButton("Tambah Buku")
        self.update_book_btn = QPushButton("Update Buku")
        self.delete_book_btn = QPushButton("Hapus Buku")

        btn_layout.addWidget(self.add_book_btn)
        btn_layout.addWidget(self.update_book_btn)
        btn_layout.addWidget(self.delete_book_btn)

        self.book_model = QSqlTableModel(self, self.db)
        self.book_model.setTable("books")
        self.book_model.select()

        self.book_table = QTableView()
        self.book_table.setModel(self.book_model)
        self.book_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        books_layout.addLayout(form_layout)
        books_layout.addLayout(btn_layout)
        books_layout.addWidget(self.book_table)

        # TAB 2: PINJAM BUKU

        borrow_tab = QWidget()
        tabs.addTab(borrow_tab, "Pinjam Buku")

        borrow_layout = QVBoxLayout(borrow_tab)

        borrow_layout.addWidget(QLabel("Pilih Buku:"))

        self.book_combo = QComboBox()
        borrow_layout.addWidget(self.book_combo)

        borrow_layout.addWidget(QLabel("Nama Peminjam:"))

        self.borrower_input = QLineEdit()
        borrow_layout.addWidget(self.borrower_input)

        self.borrow_btn = QPushButton("Pinjam Buku")
        borrow_layout.addWidget(self.borrow_btn)

        # TAB 3: KEMBALIKAN BUKU

        return_tab = QWidget()
        tabs.addTab(return_tab, "Kembalikan Buku")

        return_layout = QVBoxLayout(return_tab)

        return_layout.addWidget(
            QLabel("Peminjaman Aktif:")
        )

        self.loan_model = QSqlTableModel(self, self.db)
        self.loan_model.setTable("loans")
        self.loan_model.setFilter("status='active'")
        self.loan_model.select()

        self.loan_table = QTableView()
        self.loan_table.setModel(self.loan_model)
        self.loan_table.setSelectionBehavior(
            QAbstractItemView.SelectRows
        )

        self.return_btn = QPushButton("Kembalikan Buku")

        return_layout.addWidget(self.loan_table)
        return_layout.addWidget(self.return_btn)

        # TAB 4: LAPORAN

        reports_tab = QWidget()
        tabs.addTab(reports_tab, "Laporan")

        reports_layout = QVBoxLayout(reports_tab)

        self.stats_label = QLabel()
        self.stats_label.setAlignment(Qt.AlignTop)

        self.refresh_btn = QPushButton("Refresh Laporan")

        reports_layout.addWidget(self.stats_label)
        reports_layout.addWidget(self.refresh_btn)

        # SIGNAL CONNECTIONS

        self.add_book_btn.clicked.connect(self.add_book)
        self.update_book_btn.clicked.connect(self.update_book)
        self.delete_book_btn.clicked.connect(self.delete_book)

        self.book_table.clicked.connect(self.on_book_select)

        self.borrow_btn.clicked.connect(self.borrow_book)
        self.return_btn.clicked.connect(self.return_book)
        self.refresh_btn.clicked.connect(self.refresh_stats)

        self.load_books_to_combo()
        self.refresh_stats()

    # ==================================
    # 4. LOAD BOOKS
    # ==================================

    def load_books_to_combo(self):

        self.book_combo.clear()

        query = self.execute_query(
            "SELECT id, title FROM books WHERE stock > 0"
        )

        if query is None:
            return

        while query.next():
            self.book_combo.addItem(
                str(query.value(1)),
                query.value(0)
            )

    # ==================================
    # 5. ADD BOOK
    # ==================================

    def add_book(self):

        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        stock = self.stock_input.value()

        if not title:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Judul buku harus diisi!"
            )
            return

        query = self.execute_query(
            """
            INSERT INTO books (title, author, stock)
            VALUES (?, ?, ?)
            """,
            (title, author, stock)
        )

        if query is not None:
            self.book_model.select()
            self.load_books_to_combo()
            self.clear_book_form()
            self.refresh_stats()

            QMessageBox.information(
                self,
                "Sukses",
                "Buku berhasil ditambahkan!"
            )

    # ==================================
    # 6. UPDATE BOOK
    # ==================================

    def update_book(self):

        current = self.book_table.currentIndex()

        if not current.isValid():
            QMessageBox.warning(
                self,
                "Peringatan",
                "Pilih buku yang ingin diupdate!"
            )
            return

        row = current.row()

        book_id = self.book_model.record(row).value("id")

        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        stock = self.stock_input.value()

        if not title:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Judul buku harus diisi!"
            )
            return

        query = self.execute_query(
            """
            UPDATE books
            SET title = ?, author = ?, stock = ?
            WHERE id = ?
            """,
            (title, author, stock, book_id)
        )

        if query is not None:
            self.book_model.select()
            self.load_books_to_combo()
            self.refresh_stats()

            QMessageBox.information(
                self,
                "Sukses",
                "Data buku berhasil diupdate!"
            )

    # ==================================
    # 7. DELETE BOOK
    # ==================================

    def delete_book(self):

        current = self.book_table.currentIndex()

        if not current.isValid():
            QMessageBox.warning(
                self,
                "Peringatan",
                "Pilih buku yang ingin dihapus!"
            )
            return

        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Apakah kamu yakin ingin menghapus buku ini?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            row = current.row()
            book_id = self.book_model.record(row).value("id")

            query = self.execute_query(
                "DELETE FROM books WHERE id = ?",
                (book_id,)
            )

            if query is not None:
                self.book_model.select()
                self.load_books_to_combo()
                self.refresh_stats()

                QMessageBox.information(
                    self,
                    "Sukses",
                    "Buku berhasil dihapus!"
                )

    # ==================================
    # 8. SELECT BOOK
    # ==================================

    def on_book_select(self, index):

        row = index.row()

        self.title_input.setText(
            str(self.book_model.record(row).value("title"))
        )

        self.author_input.setText(
            str(self.book_model.record(row).value("author") or "")
        )

        stock = self.book_model.record(row).value("stock")
        self.stock_input.setValue(int(stock))

    # ==================================
    # 9. CLEAR FORM
    # ==================================

    def clear_book_form(self):

        self.title_input.clear()
        self.author_input.clear()
        self.stock_input.setValue(1)

    # ==================================
    # 10. BORROW BOOK
    # ==================================

    def borrow_book(self):

        book_id = self.book_combo.currentData()
        borrower = self.borrower_input.text().strip()

        if not borrower:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Nama peminjam harus diisi!"
            )
            return

        if book_id is None:
            QMessageBox.warning(
                self,
                "Peringatan",
                "Tidak ada buku yang tersedia!"
            )
            return

        today = QDate.currentDate().toString("yyyy-MM-dd")

        if not self.db.transaction():
            QMessageBox.critical(
                self,
                "Database Error",
                "Transaksi database gagal dimulai!"
            )
            return

        update_query = self.execute_query(
            """
            UPDATE books
            SET stock = stock - 1
            WHERE id = ? AND stock > 0
            """,
            (book_id,)
        )

        if update_query is None or update_query.numRowsAffected() != 1:
            self.db.rollback()
            QMessageBox.warning(
                self,
                "Peringatan",
                "Stok buku tidak tersedia!"
            )
            return

        insert_query = self.execute_query(
            """
            INSERT INTO loans
            (book_id, borrower, loan_date, status)
            VALUES (?, ?, ?, 'active')
            """,
            (book_id, borrower, today)
        )

        if insert_query is None:
            self.db.rollback()
            return

        if not self.db.commit():
            self.db.rollback()
            QMessageBox.critical(
                self,
                "Database Error",
                "Transaksi peminjaman gagal disimpan!"
            )
            return

        self.book_model.select()
        self.loan_model.select()
        self.load_books_to_combo()
        self.borrower_input.clear()
        self.refresh_stats()

        QMessageBox.information(
            self,
            "Sukses",
            f"Buku berhasil dipinjam oleh {borrower}!"
        )

    # ==================================
    # 11. RETURN BOOK
    # ==================================

    def return_book(self):

        current = self.loan_table.currentIndex()

        if not current.isValid():
            QMessageBox.warning(
                self,
                "Peringatan",
                "Pilih peminjaman yang ingin dikembalikan!"
            )
            return

        row = current.row()

        loan_id = self.loan_model.record(row).value("id")
        book_id = self.loan_model.record(row).value("book_id")

        today = QDate.currentDate().toString("yyyy-MM-dd")

        if not self.db.transaction():
            QMessageBox.critical(
                self,
                "Database Error",
                "Transaksi database gagal dimulai!"
            )
            return

        update_loan = self.execute_query(
            """
            UPDATE loans
            SET return_date = ?, status = 'returned'
            WHERE id = ? AND status = 'active'
            """,
            (today, loan_id)
        )

        if update_loan is None or update_loan.numRowsAffected() != 1:
            self.db.rollback()
            QMessageBox.warning(
                self,
                "Peringatan",
                "Data peminjaman tidak ditemukan!"
            )
            return

        update_stock = self.execute_query(
            """
            UPDATE books
            SET stock = stock + 1
            WHERE id = ?
            """,
            (book_id,)
        )

        if update_stock is None:
            self.db.rollback()
            return

        if not self.db.commit():
            self.db.rollback()
            QMessageBox.critical(
                self,
                "Database Error",
                "Pengembalian gagal disimpan!"
            )
            return

        self.book_model.select()
        self.loan_model.select()
        self.load_books_to_combo()
        self.refresh_stats()

        QMessageBox.information(
            self,
            "Sukses",
            "Buku berhasil dikembalikan!"
        )

    # ==================================
    # 12. REPORT
    # ==================================

    def refresh_stats(self):

        query = self.execute_query(
            "SELECT COUNT(*) FROM books"
        )

        if query is None:
            return

        query.next()
        total_books = query.value(0)

        query = self.execute_query(
            "SELECT COUNT(*) FROM loans WHERE status='active'"
        )

        if query is None:
            return

        query.next()
        active_loans = query.value(0)

        query = self.execute_query(
            "SELECT COALESCE(SUM(stock), 0) FROM books"
        )

        if query is None:
            return

        query.next()
        available_books = query.value(0)

        self.stats_label.setText(f"""
            <h2>Laporan Perpustakaan</h2>
            <p><b>Total Judul Buku:</b> {total_books}</p>
            <p><b>Buku Sedang Dipinjam:</b> {active_loans}</p>
            <p><b>Total Stok Tersedia:</b> {available_books}</p>
        """)


# ==================================
# 13. MAIN PROGRAM
# ==================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = LibrarySystem()
    window.show()

    sys.exit(app.exec_())
