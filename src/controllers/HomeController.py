from src.views.HomeView import HomeView

class HomeController:
    def __init__(self, appController):
        self.appController = appController
        self.view = HomeView()

        self.view.btn.clicked.connect(self.btnAction)

    def btnAction(self):
        self.view.showMessage()
        self.appController.route("HelpView")