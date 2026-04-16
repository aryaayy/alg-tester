from PySide6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
# from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from src.store.AppState import state

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self):
        self.btn = QPushButton("Klik aku")
        self.text = QLabel("SELAMAT DATANG")

        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.btn)

    def showMessage(self):
        message = QMessageBox()
        message.setText("Berhasil")
        message.exec()