from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import QStackedWidget, QMessageBox
from PySide6.QtCore import QThread, Signal # ADDED QThread and Signal

from src.views.MapView import MapView
from src.views.LoadingView import LoadingView

from src.services.MapService import MapService
from src.services.algs.SSSP import Dijkstra, BiDijkstra, AStar, BiAStar, BMSSP
from src.services.RoutingService import RoutingThread

from src.models.HistoryModel import HistoryModel

from src.store.AppState import state

class MapLoaderThread(QThread):
    service_ready = Signal(object) 

    # Accept the target thread when we create the worker
    def __init__(self, main_thread):
        super().__init__()
        self.main_thread = main_thread

    def run(self):
        print("[Background Thread] Starting heavy KDTree data load...")
        
        service = MapService() 
        
        # FIX: The Background thread currently owns 'receiver'. 
        # We politely "push" ownership to the Main Thread before we send it up.
        service.receiver.moveToThread(self.main_thread)
        
        # Now it is perfectly safe to emit!
        self.service_ready.emit(service)

class MapController:
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.main_thread = QThread.currentThread() 
        
        self.view = QStackedWidget()
        self.loading_view = LoadingView()
        self.view.addWidget(self.loading_view)
        self.view.setCurrentWidget(self.loading_view)
        
        # Pass the main_thread down into the worker
        self.loader_thread = MapLoaderThread(self.main_thread)
        self.loader_thread.service_ready.connect(self.on_map_data_loaded)
        self.loader_thread.start()


    def on_map_data_loaded(self, service):
        print("[Main Thread] Data loaded, setting up UI...")
        
        self.map_service = service
        
        # DELETE the old moveToThread line from here!
        # self.map_service.receiver.moveToThread(self.main_thread) <--- REMOVE THIS
        
        self.channel = QWebChannel()
        self.channel.registerObject("pyReceiver", self.map_service.receiver)
        
        self.map_service.receiver.node_selected_info.connect(self.on_node_selected)
        self.map_service.receiver.node_selected.connect(self.set_node_selected)
        
        html_path = self.map_service.generate_base_map()
        self.map_view = MapView(self.channel, html_path)
        
        self.view.addWidget(self.map_view)
        self.view.setCurrentWidget(self.map_view)

        self.map_view.startButton.clicked.connect(self.start_routing)
        self.source_osmid = None
        self.dest_osmid = None

        print("Map loaded and displayed.")

    def on_node_selected(self, node_type, lat, lon, osmid):
        print(f"[{node_type.upper()}] Lat: {lat}, Lon: {lon} | OSMID: {osmid}")

    def set_node_selected(self, source_osmid, dest_osmid):
        print(f"Triggering routing algorithm from {source_osmid} to {dest_osmid}!")
        self.source_osmid = source_osmid
        self.dest_osmid = dest_osmid
        # e.g., result = SqlBiAStar().find_shortest_path(source_osmid, dest_osmid)

    def start_routing(self):
        if self.source_osmid == None or self.dest_osmid == None:
            self.map_view.show_message(QMessageBox.Icon.Critical, "Gagal!", "Pilih simpul asal dan tujuan!")
            return

        active_algs = self.map_view.get_selected_algorithms()

        if not active_algs:
            self.map_view.show_message(QMessageBox.Icon.Critical, "Gagal!", "Pilih paling tidak 1 algoritma!")
            return

        self.map_view.show_message(QMessageBox.Icon.Information, "Sedang Memproses", "Algoritma sedang memproses rute di latar belakang. Silakan tunggu...")

        # 3. Create and Start the Background Thread
        self.routing_thread = RoutingThread(
            self.source_osmid, 
            self.dest_osmid, 
            state.indoDbPath, 
            active_algs
        )
        
        # Connect the signal to receive the results when it finishes
        self.routing_thread.routing_finished.connect(self.on_routing_finished)
        
        # START THE THREAD (This runs without freezing the UI!)
        self.routing_thread.start()

    # 4. Handle the results back on the Main Thread
    def on_routing_finished(self, results):
        print("\n[Main Thread] Routing Complete! Results:")
        
        text = ""
        for alg_name, data in results.items():
            print(f"--- {alg_name.upper()} ---")
            print(f"Distance: {round(data['distance'], 2)} meters")
            print(f"Metrics: {data['metrics']}\n")
            text += f"""--- {alg_name.upper()} ---\nDistance: {round(data['distance'], 2)} meters\nMetrics: {data['metrics']}\n\n"""
            
        # You can now trigger your MapService to draw the winning path!
        answer = self.map_view.show_question(None, "Sukses!", f"{text}Pencarian rute selesai! Simpan riwayat?")

        if(answer == QMessageBox.StandardButton.Yes):
            for alg_name, data in results.items():
                history = HistoryModel()
                history.insert(alg_name.upper(), self.source_osmid, self.dest_osmid, data['distance'], data['metrics']['exec_time'], data['metrics']['exec_space'], data['metrics']['vis_nodes'], data["created_at"])

            self.app_controller.route("HistoryView")
