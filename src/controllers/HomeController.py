from src.views.HomeView import HomeView

class HomeController:
    def __init__(self, appController):
        self.appController = appController
        self.view = HomeView()

        self.view.mapBtn.clicked.connect(self.mapBtnAction)
        self.view.historyBtn.clicked.connect(self.historyBtnAction)

    def mapBtnAction(self):
        self.appController.route("MapView")

    def historyBtnAction(self):
        self.appController.route("HistoryView")