# Inside your Controller
from src.views.HistoryView import HistoryView, HistoryDetailDialog
from src.models.HistoryModel import HistoryModel
from src.models.PathModel import PathModel
from src.store.AppState import state

class HistoryController:
    def __init__(self, appController):
        self.appController = appController

        self.history = HistoryModel()
        self.all_histories, self.unique_dates = self.history.fetch_all()

        self.view = HistoryView()

        self.view.detail_requested.connect(self.on_detail_requested)
        self.view.load_route_requested.connect(self.on_history_load_clicked)
        self.view.mode_changed.connect(self.on_history_mode_changed)

        self.view.populate_grouped(self.unique_dates)
        self.view.refresh_btn.clicked.connect(self.refresh)
    
    def refresh(self):
        self.all_histories, self.unique_dates = self.history.fetch_all()
        mode_idx = self.view.mode_combo.currentIndex()
        if mode_idx == 0:
            self.view.populate_grouped(self.unique_dates)
        else:
            self.view.populate_all(self.all_histories)
    
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
        
        # 1. Fetch from SQLite using the history_id
        path = PathModel()
        traversal_coords = path.get_traversal_by_history(
            record['history_id'], 
            max_nodes=record['max_nodes']
        )
        final_path_coords = path.get_final_path_by_history(record['history_id'])

        # 2. Dynamically find the center of the map (Use the starting point of the route!)
        # if final_path_coords:
        #     center_lat = final_path_coords[0][0] # First row, Lat column
        #     center_lon = final_path_coords[0][1] # First row, Lon column
        # else:
            # Fallback to Jakarta if something went wrong
        center_lat, center_lon = traversal_coords[0][0], traversal_coords[0][1]
            # center_lat, center_lon = -6.2, 106.8

        # 3. Pass it to the map
        self.appController.mapController.display_animated_map(center_lat, center_lon, final_path_coords, traversal_coords)
        
        # 4. CRITICAL: Switch the screen so the user can see it!
        self.appController.route("MapView")