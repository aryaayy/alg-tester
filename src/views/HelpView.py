from PySide6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
# from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from src.store.AppState import state

class HelpView(QWidget):
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self):
        self.text = QLabel("Ini halaman HELP")
        self.btn = QPushButton("Klik aku")

        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.btn)