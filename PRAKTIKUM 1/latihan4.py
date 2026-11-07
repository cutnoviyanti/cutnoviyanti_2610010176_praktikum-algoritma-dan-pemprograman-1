
import sys
import re
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kalkulator")
        self.setGeometry(300, 300, 250, 300)

        layout = QVBoxLayout()

        # Display kalkulator
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet(
            "font-size: 20px; padding: 5px;"
        )
        layout.addWidget(self.display)

        # Tombol kalkulator
        grid = QGridLayout()

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', '=', '+'
        ]

        row, col = 0, 0

        for btn_text in buttons:
            button = QPushButton(btn_text)
            button.setStyleSheet(
                "font-size: 16px; padding: 10px;"
            )
            button.clicked.connect(self.on_button_click)
            grid.addWidget(button, row, col)

            col += 1
            if col > 3:
                col = 0
                row += 1

        layout.addLayout(grid)
        self.setLayout(layout)

        self.expression = ""

    def on_button_click(self):
        button = self.sender()
        text = button.text()

        if text == 'C':
            self.expression = ""

        elif text == '=':
            try:
                if not self.expression:
                    return

                # Membatasi input hanya untuk matematika
                if not re.fullmatch(
                    r"[0-9+\-*/(). ]+",
                    self.expression
                ):
                    raise ValueError

                hasil = eval(
                    self.expression,
                    {"__builtins__": {}},
                    {}
                )

                self.expression = str(hasil)

            except Exception:
                self.expression = "Error"

        else:
            # Jika sebelumnya Error, mulai dari input baru
            if self.expression == "Error":
                self.expression = ""

            self.expression += text

        self.display.setText(self.expression)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())
