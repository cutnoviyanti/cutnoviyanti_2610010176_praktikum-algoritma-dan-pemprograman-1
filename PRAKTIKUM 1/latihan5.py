
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi


class TodoApp(QWidget):
    def __init__(self):
        super().__init__()

        # Memanggil tampilan dari Qt Designer
        loadUi("To-Do_list.ui", self)

        # Menghubungkan tombol dengan fungsi
        self.tombolTambah.clicked.connect(self.add_task)
        self.tombolSelesai.clicked.connect(self.complete_task)
        self.tombolHapus.clicked.connect(self.delete_task)

        # Menambahkan tugas dengan tombol Enter
        self.masukanTugas.returnPressed.connect(self.add_task)

    def add_task(self):
        task = self.masukanTugas.text().strip()

        if task:
            self.daftarTugas.addItem(task)
            self.masukanTugas.clear()

    def complete_task(self):
        current = self.daftarTugas.currentItem()

        if current:
            if not current.text().startswith("✓ "):
                current.setText(f"✓ {current.text()}")

            current.setForeground(Qt.green)

    def delete_task(self):
        current = self.daftarTugas.currentRow()

        if current >= 0:
            self.daftarTugas.takeItem(current)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TodoApp()
    window.show()
    sys.exit(app.exec_())