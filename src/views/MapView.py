import os
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QMessageBox
from PySide6.QtCore import QUrl, Qt

class MapView(QWidget):
    def __init__(self, web_channel, map_html_path):
        super().__init__()
        
        self.web_view = QWebEngineView()
        
        # Security Settings to allow JS and WebChannel
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        # Connect the communication channel
        self.web_view.page().setWebChannel(web_channel)

        # Load the HTML map
        self.web_view.setUrl(QUrl.fromLocalFile(map_html_path))

        self.bmsspCkBox = QCheckBox(text="BMSSP")
        self.dijkstraCkBox = QCheckBox(text="Dijkstra")
        self.astarCkBox = QCheckBox(text="A*")
        self.bidijkstraCkBox = QCheckBox(text="Bi-Dijkstra")
        self.biastarCkBox = QCheckBox(text="Bi-A*")
        self.startButton = QPushButton("Mulai")

        optionsLayout = QHBoxLayout()
        optionsLayout.addWidget(self.bmsspCkBox)
        optionsLayout.addWidget(self.dijkstraCkBox)
        optionsLayout.addWidget(self.astarCkBox)
        optionsLayout.addWidget(self.bidijkstraCkBox)
        optionsLayout.addWidget(self.biastarCkBox)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)
        layout.addWidget(self.web_view)
        layout.addWidget(self.startButton)
        layout.addLayout(optionsLayout)
        layout.addWidget(self.startButton)
    
    def get_selected_algorithms(self):
        active = []
        if self.dijkstraCkBox.isChecked(): active.append("dijkstra")
        if self.astarCkBox.isChecked(): active.append("astar")
        if self.bidijkstraCkBox.isChecked(): active.append("bidijkstra")
        if self.biastarCkBox.isChecked(): active.append("biastar")
        if self.bmsspCkBox.isChecked(): active.append("bmssp")
        return active

    def show_message(self, icon, title, text):
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

    def show_question(self, icon, title, text):
        msg = QMessageBox(self)
        # msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        return msg.exec()