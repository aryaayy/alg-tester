import os
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QMessageBox, QLabel, QSpinBox
from PySide6.QtCore import QUrl, Qt

class MapView(QWidget):
    def __init__(self, web_channel, map_html_path):
        super().__init__()
        
        self.web_view = QWebEngineView()
        
        # Security Settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)

        # Connect the communication channel
        self.web_view.page().setWebChannel(web_channel)
        self.web_view.setUrl(QUrl.fromLocalFile(map_html_path))

        # ==========================================
        # CONTAINER 1: Routing Controls (Base Map)
        # ==========================================
        self.routing_container = QWidget()
        routing_layout = QVBoxLayout(self.routing_container)
        routing_layout.setContentsMargins(10, 10, 10, 10) # add padding

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

        self.spinbox_label = QLabel("Jumlah Iterasi:")
        
        self.loop_count = QSpinBox()
        self.loop_count.setRange(1, 20) 
        self.loop_count.setValue(10)       
        self.loop_count.setSingleStep(1)

        spinBoxLayout = QHBoxLayout()
        spinBoxLayout.addWidget(self.spinbox_label)
        spinBoxLayout.addWidget(self.loop_count)
        spinBoxLayout.setStretch(1, 1)

        routing_layout.addLayout(optionsLayout)
        routing_layout.addLayout(spinBoxLayout)
        routing_layout.addWidget(self.startButton)

        # ==========================================
        # CONTAINER 2: Reset Controls (Animated Map)
        # ==========================================
        self.reset_container = QWidget()
        reset_layout = QVBoxLayout(self.reset_container)
        reset_layout.setContentsMargins(0, 0, 0, 0) # Remove padding

        self.resetButton = QPushButton("Kembali ke Peta Awal")
        reset_layout.addWidget(self.resetButton)
        
        # Hide the reset button by default when the app opens
        self.reset_container.setVisible(False)

        # ==========================================
        # MAIN LAYOUT
        # ==========================================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)
        
        # Add both containers to the main layout
        layout.addWidget(self.routing_container)
        layout.addWidget(self.reset_container)
        layout.setStretch(0, 1)
    
    # --- NEW METHODS TO TOGGLE THE UI ---
    
    def set_mode_animated(self):
        """Hides the checkboxes and shows the Reset button."""
        self.routing_container.setVisible(False)
        self.reset_container.setVisible(True)

    def set_mode_base(self):
        """Hides the Reset button and brings back the checkboxes."""
        self.routing_container.setVisible(True)
        self.reset_container.setVisible(False)

    # ------------------------------------

    def get_selected_algorithms(self):
        active = []
        if self.dijkstraCkBox.isChecked(): active.append("dijkstra")
        if self.astarCkBox.isChecked(): active.append("astar")
        if self.bidijkstraCkBox.isChecked(): active.append("bidijkstra")
        if self.biastarCkBox.isChecked(): active.append("biastar")
        if self.bmsspCkBox.isChecked(): active.append("bmssp")
        return active
    
    def get_loop_count(self):
        return self.loop_count.value()

    def show_message(self, icon, title, text):
        msg = QMessageBox(self)
        msg.setIcon(icon)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.exec()

    def show_question(self, icon, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        return msg.exec()