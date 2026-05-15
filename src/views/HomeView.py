from PySide6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox
from PySide6.QtCore import Qt
# from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from src.store.AppState import state

class HomeView(QWidget):
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self):
        self.mapBtn = QPushButton("Peta")
        self.historyBtn = QPushButton("Riwayat")
        self.text = QLabel("SELAMAT DATANG")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.historyBtn)
        layout.addWidget(self.mapBtn)

    def showMessage(self):
        message = QMessageBox()
        message.setText("Berhasil")
        message.exec()