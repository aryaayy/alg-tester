from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QMainWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class LoadingView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algorithm Tester")
        self.resize(1280, 720)

        container = QWidget()
        self.setCentralWidget(container)

        # 1. Main Layout (Centered)
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 2. Title Text
        self.title_label = QLabel("Algorithm Tester v1.0.0")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 3. Subtitle Text
        self.subtitle_label = QLabel("Sedang memuat aplikasi.\nHarap tunggu sebentar...")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #6c757d; font-size: 12px;") # Gray text
        
        # 4. The Animated Loading Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(300)
        
        # MAGICAL TRICK: Setting both min and max to 0 creates an 
        # infinite animated bouncing loading bar in PySide6!
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0) 
        
        # 5. Add everything to the layout
        layout.addWidget(self.title_label)
        layout.addSpacing(10)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(10)
        layout.addWidget(self.subtitle_label)