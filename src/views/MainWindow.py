from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFileDialog, QMessageBox

STYLESHEET = """
    /* A simple gray line to separate the navigation bar from the content */
    #NavBar {
        border-bottom: 1px solid #ccc; 
    }

    /* Minimal, flat buttons */
    .NavBtn {
        font-size: 14px;
        padding: 8px 16px;
        border: 1px solid transparent;
        border-radius: 4px;
    }
    
    /* Subtle hover effect */
    .NavBtn:hover {
        background-color: rgba(0, 0, 0, 0.05); 
        border: 1px solid #ccc;
    }
    
    /* Pushed-in look for the active page */
    .NavBtn:checked {
        background-color: rgba(0, 0, 0, 0.1); 
        border: 1px solid #aaa;
        font-weight: bold;
    }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algorithm Tester")
        self.resize(1280, 720)
        
        # --- Native Menubar (Stripped down) ---
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")

        self.export_button = file_menu.addAction("Export")
        self.export_button.setShortcut("Ctrl+E")

        # --- Main Layout Structure ---
        main_container = QWidget()
        self.setCentralWidget(main_container)
        self.main_layout = QVBoxLayout(main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Top Navigation Bar ---
        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("NavBar") 
        self.nav_layout = QHBoxLayout(self.nav_bar)
        
        self.btn_home = QPushButton("Home")
        self.btn_map = QPushButton("Peta")
        self.btn_history = QPushButton("Riwayat")
        self.btn_help = QPushButton("Help")

        for btn in [self.btn_map, self.btn_history]:
            btn.setProperty("class", "NavBtn")
            btn.setCheckable(True) 
            self.nav_layout.addWidget(btn)
            
        self.nav_layout.addStretch() # Pushes buttons to the left

        # --- Stacked Widget (Deck of Cards) ---
        self.stack = QStackedWidget()

        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.addWidget(self.stack)

        # Apply the plain stylesheet
        self.setStyleSheet(STYLESHEET)
    
    def get_export_path(self):
        # 1. Open a Save File Dialog so the user can pick the location and filename
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export Riwayat ke CSV", 
            "riwayat_algoritma.csv",  # Default file name
            "CSV Files (*.csv);;All Files (*)"
        )
        return file_path
    
    def show_export_failed(self):
        QMessageBox.warning(
            self, 
            "Export Dibatalkan", 
            "Tidak ada data riwayat untuk diekspor."
        )

    def show_export_error(self, e):
        QMessageBox.critical(
            self, 
            "Gagal Export", 
            f"Terjadi kesalahan saat mengekspor data:\n{str(e)}"
        )
    
    def show_export_success(self, len, file_path):
        QMessageBox.information(
            self, 
            "Export Berhasil", 
            f"{len} baris data berhasil diekspor ke:\n{file_path}"
        )