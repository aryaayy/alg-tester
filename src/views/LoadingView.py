from PySide6.QtWidgets import QWidget, QMainWindow, QLabel, QPushButton, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
# from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from src.store.AppState import state

class LoadingView(QWidget):
    def __init__(self):
        super().__init__()
        self.draw()

    def draw(self):
        self.text = QLabel("GENERATING MAP....")

        layout = QVBoxLayout(self)
        layout.addWidget(self.text, alignment=Qt.AlignmentFlag.AlignCenter)