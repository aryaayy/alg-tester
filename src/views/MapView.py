import os
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, 
    QMessageBox, QLabel, QSpinBox, QRadioButton, QFileDialog, QProgressBar
)
from PySide6.QtCore import QUrl, Qt
from src.models.IndonesiaModel import IndonesiaModel

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

        # --- NEW: Mode Selection (Map vs Batch File) ---
        modeLayout = QHBoxLayout()
        self.radioMap = QRadioButton("Pilih dari Peta")
        self.radioFile = QRadioButton("Batch Processing (File CSV)")
        self.radioMap.setChecked(True) # Default ke Peta
        modeLayout.addWidget(self.radioMap)
        modeLayout.addWidget(self.radioFile)
        modeLayout.addStretch()

        # --- NEW: File Selection Sub-Container (Sembunyi secara default) ---
        self.file_container = QWidget()
        file_layout = QHBoxLayout(self.file_container)
        file_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btnSelectFile = QPushButton("Pilih File CSV")
        self.lblFilePath = QLabel("Belum ada file terpilih")
        self.lblFilePath.setStyleSheet("color: #6c757d; font-style: italic;")
        
        file_layout.addWidget(self.btnSelectFile)
        file_layout.addWidget(self.lblFilePath)
        file_layout.setStretch(1, 1)
        self.file_container.setVisible(False) # Sembunyikan saat mode peta
        self.selected_file_path = None

        # Menyambungkan logika pergantian UI
        # self.radioMap.toggled.connect(self._toggle_mode_ui)
        # self.btnSelectFile.clicked.connect(self._open_file_dialog)

        # --- EXISTING: Checkboxes ---
        self.bmsspCkBox = QCheckBox(text="BMSSP")
        self.dijkstraCkBox = QCheckBox(text="Dijkstra")
        self.astarCkBox = QCheckBox(text="A*")
        self.bidijkstraCkBox = QCheckBox(text="Bi-Dijkstra")
        self.biastarCkBox = QCheckBox(text="Bi-A*")
        
        optionsLayout = QHBoxLayout()
        optionsLayout.addWidget(self.bmsspCkBox)
        optionsLayout.addWidget(self.dijkstraCkBox)
        optionsLayout.addWidget(self.astarCkBox)
        optionsLayout.addWidget(self.bidijkstraCkBox)
        optionsLayout.addWidget(self.biastarCkBox)

        # --- EXISTING: Spinbox & Start Button ---
        self.spinbox_label = QLabel("Jumlah Iterasi:")
        self.loop_count = QSpinBox()
        self.loop_count.setRange(1, 20) 
        self.loop_count.setValue(10)       
        self.loop_count.setSingleStep(1)


        spinBoxLayout = QHBoxLayout()
        spinBoxLayout.addWidget(self.spinbox_label)
        spinBoxLayout.addWidget(self.loop_count)
        spinBoxLayout.setStretch(1, 1)

        self.save_traversal = QCheckBox(text="Simpan Traversal")

        self.startButton = QPushButton("Mulai")

        # Masukkan semuanya ke layout utama routing
        routing_layout.addLayout(modeLayout)
        routing_layout.addWidget(self.file_container)
        routing_layout.addLayout(optionsLayout)
        routing_layout.addLayout(spinBoxLayout)
        routing_layout.addWidget(self.save_traversal)
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
        # CONTAINER 3: Progress Controls (Loading) - NEW!
        # ==========================================
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(10, 10, 10, 10)

        # Label untuk menampilkan teks (misal: "Menjalankan DIJKSTRA...")
        self.progress_label = QLabel("Memulai kalkulasi...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-weight: bold;")

        # Progress bar dari 0% sampai 100%
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)

        # Sembunyikan saat aplikasi baru dibuka
        self.progress_container.setVisible(False)

        # ==========================================
        # MAIN LAYOUT
        # ==========================================
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web_view)
        
        # Add both containers to the main layout
        layout.addWidget(self.routing_container)
        layout.addWidget(self.reset_container)
        layout.addWidget(self.progress_container)
        layout.setStretch(0, 1)
    
    # --- NEW: UI Logic Methods ---
    def get_file_path(self):
        return QFileDialog.getOpenFileName(
            self, "Pilih File Skenario Uji", "", "CSV Files (*.csv)"
        )
# Tambahkan di bagian bawah fungsi __init__ setelah menghubungkan radio button:
    # self.radioFile.toggled.connect(self._handle_batch_mode_activated)

    # def _toggle_mode_ui(self):
    #     """Memunculkan atau menyembunyikan input file berdasarkan radio button."""
    #     is_file_mode = self.radioFile.isChecked()
    #     self.file_container.setVisible(is_file_mode)
        
    #     # Kirim sinyal ke JavaScript untuk mengunci atau membuka interaksi klik peta
    #     if is_file_mode:
    #         self.web_view.page().runJavaScript("lockMapInteractions(true);")
    #     else:
    #         self.web_view.page().runJavaScript("lockMapInteractions(false);")
    #         self.clear_batch_pinpoints()

    # def _open_file_dialog(self):
    #     """Membuka dialog untuk memilih file skenario pengujian CSV."""
    #     path, _ = QFileDialog.getOpenFileName(
    #         self, "Pilih File Skenario Uji", "", "CSV Files (*.csv)"
    #     )
    #     if path:
    #         self.selected_file_path = path
    #         filename = os.path.basename(path)
    #         self.lblFilePath.setText(filename)
    #         self.lblFilePath.setStyleSheet("color: black; font-weight: bold;")
            
    #         # Pemicu otomatis untuk merender pinpoints setelah file dipilih
    #         self.trigger_batch_pinpoints_render()

    # def trigger_batch_pinpoints_render(self):
    #     """Meminta controller atau internal fungsi untuk merender pinpoints"""
    #     if not self.selected_file_path: return
        
    #     # Ambil koordinat dari file CSV
    #     indo_model = IndonesiaModel()
    #     points = indo_model.get_coordinates_from_csv(self.selected_file_path)
        
    #     # Tampilkan ke peta melalui JavaScript
    #     import json
    #     points_json = json.dumps(points)
    #     self.web_view.page().runJavaScript(f"renderBatchPinpoints({points_json});")

    # def clear_batch_pinpoints(self):
    #     """Membersihkan pinpoints eksperimen ketika kembali ke mode manual"""
    #     self.web_view.page().runJavaScript("clearBatchPinpoints();")

    def get_input_mode(self):
        """Mengembalikan 'map' atau 'file' agar Controller tahu mode apa yang aktif."""
        return "file" if self.radioFile.isChecked() else "map"

    def get_batch_file_path(self):
        """Mengembalikan path file CSV yang dipilih (None jika belum memilih)."""
        return self.selected_file_path

    # --- EXISTING: UI Methods ---
    
    def set_mode_animated(self):
        """Hides the routing controls and shows the Reset button."""
        self.routing_container.setVisible(False)
        self.progress_container.setVisible(False)
        self.reset_container.setVisible(True)

    def set_mode_base(self):
        """Hides the Reset button and brings back the routing controls."""
        self.routing_container.setVisible(True)
        self.progress_container.setVisible(False)
        self.reset_container.setVisible(False)

    def set_mode_progress(self):
        self.routing_container.setVisible(False)
        self.progress_container.setVisible(True)
        self.reset_container.setVisible(False)

        self.progress_bar.setValue(0)
        self.progress_label.setText("Mempersiapkan...")
    
    # --- Progress Update Method ---

    def update_progress(self, percent, message):
        """Memperbarui nilai loading bar dan teks status."""
        self.progress_bar.setValue(percent)
        self.progress_label.setText(message)

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
    
    def is_save_traversal(self):
        return self.save_traversal.isChecked()

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