from src.views.MainWindow import MainWindow
from src.controllers.HomeController import HomeController
from src.controllers.HelpController import HelpController
from src.controllers.MapController import MapController
from src.controllers.HistoryController import HistoryController
from src.store.AppState import state

class AppController:
    def __init__(self):
        self.mainWindow = MainWindow()

        self.mainWindow.switchThemeSettings.triggered.connect(self.switchThemeSettingsAction)

    def initApp(self):
        self.showHome()
        self.mainWindow.show()

    def switchThemeSettingsAction(self):
        state.isLightTheme = not state.isLightTheme
        
        if state.isLightTheme:
            prevThemeText = "Dark"
            newTheme = "light"
        else:
            prevThemeText = "Light"
            newTheme = "dark"

        self.mainWindow.setTheme(newTheme, prevThemeText)

    def route(self, target):
        if target == "HomeView":
            self.showHome()
        elif target == "HelpView":
            self.showHelp()
        elif target == "MapView":
            self.showMap()
        elif target == "HistoryView":
            self.showHistory()

    def showHome(self):
        self.homeController = HomeController(self)
        self.mainWindow.setCentralWidget(self.homeController.view)

    def showHelp(self):
        self.helpController = HelpController(self)
        self.mainWindow.setCentralWidget(self.helpController.view)

    def showMap(self):
        self.mapController = MapController(self)
        self.mainWindow.setCentralWidget(self.mapController.view)

    def showHistory(self):
        self.historyController = HistoryController(self)
        self.mainWindow.setCentralWidget(self.historyController.view)