from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QLabel, QDialog
from PySide6.QtCore import Signal

class HistoryView(QWidget):
    # We now have three signals!
    detail_requested = Signal(str)
    load_route_requested = Signal(dict)
    mode_changed = Signal(str) # Emits "grouped" or "all"

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # --- NEW: Top Control Bar ---
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Tampilkan:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Berdasarkan Tanggal", "Semua Riwayat"])
        self.mode_combo.currentTextChanged.connect(self.on_combo_changed)
        
        control_layout.addWidget(self.mode_combo)
        control_layout.addStretch() # Pushes the dropdown to the left side
        
        layout.addLayout(control_layout)
        # ----------------------------

        self.table = QTableWidget()
        layout.addWidget(self.table)

    def on_combo_changed(self, text):
        """Translates the UI dropdown change into a clean MVC signal."""
        if text == "Berdasarkan Tanggal":
            self.mode_changed.emit("grouped")
        else:
            self.mode_changed.emit("all")

    def populate_grouped(self, unique_dates):
        self.table.clear() # Wipes the table clean!
        
        headers = ["Tanggal", "Aksi"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setRowCount(len(unique_dates))
        for row_index, date in enumerate(unique_dates):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(date)))
            
            detail_btn = QPushButton("Detail")
            detail_btn.setStyleSheet("background-color: #17a2b8; color: white; border-radius: 4px; padding: 4px;")
            detail_btn.clicked.connect(lambda checked=False, d=date: self.detail_requested.emit(d))
            self.table.setCellWidget(row_index, 1, detail_btn)

    def populate_all(self, history_data):
        self.table.clear() # Wipes the table clean!
        
        headers = ["Algoritma", "Source ID", "Dest ID", "Jarak (m)", "Waktu (s)", "Memori (bytes)", "Simpul", "Tanggal", "Aksi"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setRowCount(len(history_data))
        for row_index, record in enumerate(history_data):
            # self.table.setItem(row_index, 0, QTableWidgetItem(str(record["history_id"])))
            self.table.setItem(row_index, 0, QTableWidgetItem(record["alg"]))
            self.table.setItem(row_index, 1, QTableWidgetItem(str(record["source_osmid"])))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(record["dest_osmid"])))
            self.table.setItem(row_index, 3, QTableWidgetItem(str(round(record["distance"], 2))))
            self.table.setItem(row_index, 4, QTableWidgetItem(str(round(record["exec_time"], 4))))
            self.table.setItem(row_index, 5, QTableWidgetItem(str(record["exec_space"])))
            self.table.setItem(row_index, 6, QTableWidgetItem(str(record["vis_nodes"])))
            self.table.setItem(row_index, 7, QTableWidgetItem(str(record["created_at"])))
            
            action_btn = QPushButton("Load")
            action_btn.setStyleSheet("background-color: #007bff; color: white; border-radius: 4px; padding: 4px;")
            action_btn.clicked.connect(lambda checked=False, r=record: self.load_route_requested.emit(r))
            self.table.setCellWidget(row_index, 8, action_btn)

class HistoryDetailDialog(QDialog):
    def __init__(self, date, specific_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detail Riwayat: {date}")
        self.resize(800, 400) # Make the popup decently large

        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        # headers = ["Algoritma", "Source ID", "Dest ID", "Jarak (m)", "Waktu (s)", "Memori", "Simpul"]
        headers = ["Algoritma", "Source ID", "Dest ID", "Jarak (m)", "Waktu (s)", "Memori (bytes)", "Jml Simpul"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Populate the detail table
        self.table.setRowCount(len(specific_data))
        for i, record in enumerate(specific_data):
            self.table.setItem(i, 0, QTableWidgetItem(record["alg"]))
            self.table.setItem(i, 1, QTableWidgetItem(str(record["source_osmid"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(record["dest_osmid"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(round(record["distance"], 2))))
            self.table.setItem(i, 4, QTableWidgetItem(str(round(record["exec_time"], 4))))
            self.table.setItem(i, 5, QTableWidgetItem(str(record["exec_space"])))
            self.table.setItem(i, 6, QTableWidgetItem(str(record["vis_nodes"])))
            
        layout.addWidget(self.table)