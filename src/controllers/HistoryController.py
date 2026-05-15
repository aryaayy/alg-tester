# Inside your Controller
from src.views.HistoryView import HistoryView, HistoryDetailDialog
from src.models.HistoryModel import HistoryModel
from src.store.AppState import state

class HistoryController:
    def __init__(self, appController):
        self.appController = appController

        history = HistoryModel()
        self.all_histories, self.unique_dates = history.fetch_all()

        self.view = HistoryView()

        self.view.detail_requested.connect(self.on_detail_requested)
        self.view.load_route_requested.connect(self.on_history_load_clicked)
        self.view.mode_changed.connect(self.on_history_mode_changed)

        self.view.populate_grouped(self.unique_dates)
    
    def on_detail_requested(self, selected_date):
        """Triggered when a 'Detail' button is clicked."""
        print(f"Opening details for: {selected_date}")
        
        # Filter the master list to only include records from this date
        filtered_data = [
            record for record in self.all_histories 
            if record["created_at"].startswith(selected_date)
        ]
        
        # Create and show the popup dialog
        # We pass self.history_view as the parent so the popup centers over it
        dialog = HistoryDetailDialog(selected_date, filtered_data, self.view)
        
        # .exec() halts the user from clicking the main app until they close the popup
        dialog.exec()
    
    def on_history_mode_changed(self, mode):
        """Swaps the table data dynamically based on the dropdown!"""
        if mode == "grouped":
            self.view.populate_grouped(self.unique_dates)
        elif mode == "all":
            self.view.populate_all(self.all_histories)

    def on_history_load_clicked(self, record):
        """This function receives the specific dictionary of the row the user clicked!"""
        print(f"User wants to load: {record['alg']} from {record['source_osmid']} to {record['dest_osmid']}")