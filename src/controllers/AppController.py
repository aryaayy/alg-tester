from src.views.MainWindow import MainWindow
from src.views.LoadingView import LoadingView
from src.controllers.HomeController import HomeController
from src.controllers.HelpController import HelpController
from src.controllers.MapController import MapController
from src.controllers.HistoryController import HistoryController
from src.models.HistoryModel import HistoryModel
import csv

class AppController:
    def __init__(self):
        self.mainWindow = MainWindow()

        self.mainWindow.export_button.triggered.connect(self.on_export)

        # Connect Navigation Bar Buttons to the router
        self.mainWindow.btn_home.clicked.connect(lambda: self.route("HomeView"))
        self.mainWindow.btn_map.clicked.connect(lambda: self.route("MapView"))
        self.mainWindow.btn_history.clicked.connect(lambda: self.route("HistoryView"))
        self.mainWindow.btn_help.clicked.connect(lambda: self.route("HelpView"))
        
        self.pages = {}

    def initApp(self):
        # 1. Initialize all controllers ONCE
        self.loadingView = LoadingView()
        self.homeController = HomeController(self)
        self.helpController = HelpController(self)
        self.mapController = MapController(self)
        self.historyController = HistoryController(self)

        self.mapController.app_ready.connect(self.unlock_app)
        self.loadingView.show()

    def unlock_app(self):
        self.mainWindow.stack.addWidget(self.homeController.view)
        self.pages["HomeView"] = self.homeController.view

        self.mainWindow.stack.addWidget(self.helpController.view)
        self.pages["HelpView"] = self.helpController.view

        self.mainWindow.stack.addWidget(self.mapController.view)
        self.pages["MapView"] = self.mapController.view

        self.mainWindow.stack.addWidget(self.historyController.view)
        self.pages["HistoryView"] = self.historyController.view
        
        self.route("MapView")
        self.loadingView.close()
        self.mainWindow.show()

    def route(self, target):
        if target in self.pages:
            if target == "HistoryView":
                self.historyController.refresh()
            self.mainWindow.stack.setCurrentWidget(self.pages[target])

            if target != "LoadingView":
                self.update_nav_buttons(target)

    def update_nav_buttons(self, active_target):
        """Highlights the active button and un-highlights the rest."""
        self.mainWindow.btn_home.setChecked(active_target == "HomeView")
        self.mainWindow.btn_map.setChecked(active_target == "MapView")
        self.mainWindow.btn_history.setChecked(active_target == "HistoryView")
        self.mainWindow.btn_help.setChecked(active_target == "HelpView")
    
    def on_export(self):
        """Triggered when the user clicks File -> Export or presses Ctrl+E"""
        
        # 1. Open a Save File Dialog
        file_path = self.mainWindow.get_export_path()
        
        if not file_path:
            return 

        try:
            # 2. Call your Model!
            history_model = HistoryModel()
            history_list, _ = history_model.fetch_all()
            
            # Check if there is actually data to export
            if not history_list:
                self.mainWindow.show_export_failed()
                return

            # 3. Get the exact headers from the dictionary keys 
            # (history_id, alg, source_osmid, etc.)
            headers = list(history_list[0].keys())

            # 4. Write to CSV using DictWriter
            with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
                # DictWriter automatically maps your dictionaries to the correct columns!
                writer = csv.DictWriter(csv_file, fieldnames=headers)
                
                writer.writeheader()         # Write the top row (column names)
                writer.writerows(history_list) # Dump all the dictionaries in at once
                
            # 5. Show success message
            self.mainWindow.show_export_success(len(history_list), file_path)
            
        except Exception as e:
            self.mainWindow.show_export_error(e)