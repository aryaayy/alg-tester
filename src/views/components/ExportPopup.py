from PySide6.QtWidgets import QFileDialog, QMessageBox

def get_export_path(self):
    # 1. Open a Save File Dialog so the user can pick the location and filename
    file_path, _ = QFileDialog.getSaveFileName(
        self, 
        "Export Riwayat ke CSV", 
        "riwayat_algoritma.csv",  # Default file name
        "CSV Files (*.csv);;All Files (*)"
    )
    return file_path

def show_export_failed(self, msg):
    QMessageBox.warning(
        self, 
        "Export Dibatalkan", 
        msg
    )

def show_export_error(self, e):
    QMessageBox.critical(
        self, 
        "Gagal Export", 
        f"Terjadi kesalahan saat mengekspor data:\n{str(e)}"
    )

def show_export_success(self, msg):
    QMessageBox.information(
        self, 
        "Export Berhasil", 
        msg
    )