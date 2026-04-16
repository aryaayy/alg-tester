from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from src.controllers.AppController import AppController
import sys

def main():
    app = QApplication(sys.argv)
    window = AppController()
    window.initApp()
    app.exec()

main()