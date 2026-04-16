from PySide6.QtWidgets import QMainWindow
import qdarktheme

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algorithm Tester")
        self.resize(1280, 720)
        self.setStyleSheet(qdarktheme.load_stylesheet("light"))
        
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("File")
        saveFile = fileMenu.addAction("Save")
        saveAsFile = fileMenu.addAction("Save as...")
        importFile = fileMenu.addAction("Import")
        exportFile = fileMenu.addAction("Export")

        settingsMenu = menuBar.addMenu("Settings")
        self.switchThemeSettings = settingsMenu.addAction("Switch to Dark Mode")

    def setTheme(self, newTheme, prevThemeText):
        self.switchThemeSettings.setText(f"Switch to {prevThemeText} Mode")
        self.setStyleSheet(qdarktheme.load_stylesheet(newTheme))

STYLESHEET = """
    QMainWindow {
        background-color: #FCF8D8;
    }
    
    /* Sidebar Styling */
    #Sidebar {
        background-color: #D9DADF;
        border-right: 1px solid #ADACA7;
    }
    
    /* App Title */
    #AppTitle {
        color: #DD700B;
        font-size: 20px;
        font-weight: bold;
    }
    
    /* Burger Button */
    #BurgerBtn {
        background-color: transparent;
        color: #7C7D75;
        font-size: 24px;
        text-align: center;
        padding: 5px;
        border: none;
        border-radius: 5px;
    }
    #BurgerBtn:hover {
        background-color: #ADACA7;
        color: #FCF8D8;
    }

    /* Sidebar Buttons */
    .SidebarBtn {
        background-color: transparent;
        color: #7C7D75;
        font-size: 16px;
        font-weight: bold;
        text-align: left;
        padding: 10px 15px; /* Important for clipping text when collapsed */
        border: none;
        border-radius: 5px;
    }
    
    .SidebarBtn:hover {
        background-color: #ADACA7;
        color: #FCF8D8;
    }
    
    .SidebarBtn:checked {
        background-color: #DD700B;
        color: #FCF8D8;
    }

    /* Dummy Content Styling */
    QLabel {
        color: #7C7D75;
        font-size: 24px;
    }
    
    /* Theme Toggle Checkbox */
    QCheckBox {
        color: #7C7D75;
        font-size: 14px;
        font-weight: bold;
        padding: 10px 10px;
    }
"""