from src.views.HelpView import HelpView

class HelpController:
    def __init__(self, appController):
        self.appController = appController
        self.view = HelpView()

        self.view.btn.clicked.connect(self.btnAction)

    def btnAction(self):
        self.appController.route("HomeView")