from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QComboBox, QLabel, QDialog, QSpinBox, QDialogButtonBox, QCheckBox
from PySide6.QtCore import Signal, Qt

class LoadSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pengaturan Visualisasi")
        self.resize(350, 220) # Made slightly taller to fit the warning
        
        layout = QVBoxLayout(self)
        
        # --- NEW: Render All Checkbox and Warning ---
        self.render_all_checkbox = QCheckBox("Render Semua Simpul")
        self.render_all_checkbox.stateChanged.connect(self.toggle_spinbox)
        layout.addWidget(self.render_all_checkbox)
        
        self.warning_label = QLabel("⚠️ Tidak disarankan untuk rute jarak jauh.\nDapat menyebabkan aplikasi lag atau crash.")
        self.warning_label.setStyleSheet("color: #dc3545; font-size: 11px; font-style: italic;") # Red italic text
        layout.addWidget(self.warning_label)
        
        layout.addSpacing(10)

        # --- EXISTING: Max Nodes Setting ---
        self.spinbox_label = QLabel("Maksimal Simpul Animasi (Downsampling):")
        layout.addWidget(self.spinbox_label)
        
        self.max_nodes_spinbox = QSpinBox()
        self.max_nodes_spinbox.setRange(100, 50000) 
        self.max_nodes_spinbox.setValue(25000)       
        self.max_nodes_spinbox.setSingleStep(100)
        layout.addWidget(self.max_nodes_spinbox)
        
        layout.addSpacing(20)

        # --- EXISTING: Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        
        self.button_box.button(QDialogButtonBox.Ok).setText("Visualisasikan")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Batal")
        
        layout.addWidget(self.button_box)

    def toggle_spinbox(self, state):
        """Disables the spinbox if the user chooses to render ALL nodes."""
        if state == Qt.CheckState.Checked.value:
            self.max_nodes_spinbox.setEnabled(False)
            self.spinbox_label.setEnabled(False)
        else:
            self.max_nodes_spinbox.setEnabled(True)
            self.spinbox_label.setEnabled(True)

    def get_settings(self):
        """Returns a dictionary of the user's chosen settings."""
        # If checked, we send -1 as a 'secret code' meaning NO LIMIT.
        if self.render_all_checkbox.isChecked():
            final_max_nodes = -1 
        else:
            final_max_nodes = self.max_nodes_spinbox.value()
            
        return {
            "max_nodes": final_max_nodes
        }

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
        self.mode_combo.addItems(["Grouped", "Semua Riwayat"])
        self.mode_combo.currentTextChanged.connect(self.on_combo_changed)
        
        control_layout.addWidget(self.mode_combo)

        self.refresh_btn = QPushButton("Refresh")
        control_layout.addWidget(self.refresh_btn)
        control_layout.addStretch() # Pushes the dropdown to the left side
        
        layout.addLayout(control_layout)
        # ----------------------------

        self.table = QTableWidget()
        layout.addWidget(self.table)

    def on_combo_changed(self, text):
        """Translates the UI dropdown change into a clean MVC signal."""
        if text == "Grouped":
            self.mode_changed.emit("grouped")
        else:
            self.mode_changed.emit("all")

    def populate_grouped(self, unique_dates):
        self.table.clear() # Wipes the table clean!
        
        headers = ["Tanggal", "Source ID", "Dest ID", "Aksi"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        self.table.setRowCount(len(unique_dates))
        for row_index, data in enumerate(unique_dates):
            self.table.setItem(row_index, 0, QTableWidgetItem(str(data[0])))
            self.table.setItem(row_index, 1, QTableWidgetItem(str(data[1])))
            self.table.setItem(row_index, 2, QTableWidgetItem(str(data[2])))
            
            detail_btn = QPushButton("Detail")
            detail_btn.setStyleSheet("background-color: #17a2b8; color: white; border-radius: 4px; padding: 4px;")
            detail_btn.clicked.connect(lambda checked=False, d=data[0]: self.detail_requested.emit(d))
            self.table.setCellWidget(row_index, 3, detail_btn)

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
            action_btn.clicked.connect(lambda checked=False, r=record: self.show_load_settings.emit(r))
            self.table.setCellWidget(row_index, 8, action_btn)
    
    def show_load_settings(self, record):
        """Opens the settings dialog before loading the route on the map."""
        dialog = LoadSettingsDialog(self)
        
        # .exec() halts the UI until the user clicks OK or Cancel
        if dialog.exec() == QDialog.Accepted:
            # User clicked "Visualisasikan"
            settings = dialog.get_settings()
            
            # Attach the chosen settings to the record dictionary
            record["max_nodes"] = settings["max_nodes"]
            
            # NOW we tell the Controller to load it!
            self.load_route_requested.emit(record)

            return True
        
        return False

class HistoryDetailDialog(QDialog):
    def __init__(self, date, specific_data, parent: HistoryView =None):
        super().__init__(parent)
        self.parent_view = parent
        self.setWindowTitle(f"Detail Riwayat: {date}")
        self.resize(800, 400) # Make the popup decently large

        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        # headers = ["Algoritma", "Source ID", "Dest ID", "Jarak (m)", "Waktu (s)", "Memori", "Simpul"]
        headers = ["Algoritma", "Jarak (m)", "Waktu (s)", "Memori (bytes)", "Simpul", "Aksi"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Populate the detail table
        self.table.setRowCount(len(specific_data))
        for i, record in enumerate(specific_data):
            self.table.setItem(i, 0, QTableWidgetItem(record["alg"]))
            # self.table.setItem(i, 1, QTableWidgetItem(str(record["source_osmid"])))
            # self.table.setItem(i, 2, QTableWidgetItem(str(record["dest_osmid"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(round(record["distance"], 2))))
            self.table.setItem(i, 2, QTableWidgetItem(str(round(record["exec_time"], 4))))
            self.table.setItem(i, 3, QTableWidgetItem(str(record["exec_space"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(record["vis_nodes"])))

            action_btn = QPushButton("Load")
            action_btn.setStyleSheet("background-color: #007bff; color: white; border-radius: 4px; padding: 4px;")
            action_btn.clicked.connect(lambda checked=False, r=record: self.on_load_clicked(r))
            self.table.setCellWidget(i, 5, action_btn)
            
        layout.addWidget(self.table)
    
    def on_load_clicked(self, record):
        is_successful = self.parent_view.show_load_settings(record)
        if is_successful:
            self.accept()