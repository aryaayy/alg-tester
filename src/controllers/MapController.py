from PySide6.QtWebChannel import QWebChannel
from PySide6.QtWidgets import QStackedWidget, QMessageBox
from PySide6.QtCore import QObject, QThread, Signal # ADDED QThread and Signal

from src.views.MapView import MapView
from src.views.LoadingView import LoadingView

from src.services.MapService import MapService
from src.services.algs.SSSP import Dijkstra, BiDijkstra, AStar, BiAStar, BMSSP
from src.services.RoutingService import RoutingThread, BatchRoutingThread

from src.models.HistoryModel import HistoryModel
from src.models.PathModel import PathModel
from src.models.IndonesiaModel import IndonesiaModel

from src.store.AppState import state

import folium
import json
import os
from PySide6.QtCore import QUrl
from branca.element import Element

import csv

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

class MapController(QObject):
    app_ready = Signal() 

    def __init__(self, app_controller):
        super().__init__() # Required for QObject
        self.app_controller = app_controller
        self.main_thread = QThread.currentThread() 
        
        # WE DELETED THE QStackedWidget AND LoadingView FROM HERE!
        # MapController now ONLY cares about the map.
        self.view = None 
        
        # Start the background thread immediately when the app opens
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
        
        self.base_html_path = self.map_service.generate_base_map()
        self.view = MapView(self.channel, self.base_html_path)
        self.view.startButton.clicked.connect(self.on_start_clicked)
        self.view.resetButton.clicked.connect(self.on_reset_clicked)
        self.view.radioMap.toggled.connect(self._toggle_mode_ui)
        self.view.btnSelectFile.clicked.connect(self._open_file_dialog)

        self.source_osmid = None
        self.dest_osmid = None

        self.app_ready.emit()

    def on_node_selected(self, node_type, lat, lon, osmid):
        print(f"[{node_type.upper()}] Lat: {lat}, Lon: {lon} | OSMID: {osmid}")

    def set_node_selected(self, source_osmid, dest_osmid):
        print(f"Triggering routing algorithm from {source_osmid} to {dest_osmid}!")
        self.source_osmid = source_osmid
        self.dest_osmid = dest_osmid
        
        # csv_filename = "D:/Arya/Skripsi/alg_tester/test/jauhcoba.csv"

        # if self.source_osmid != None and self.dest_osmid != None:        
        #     # Open the file in append mode ('a')
        #     with open(csv_filename, mode='a', newline='') as file:
        #         writer = csv.writer(file)
        #         # Append the source and destination as a new row
        #         writer.writerow(["jauh", source_osmid, dest_osmid])

    def on_start_clicked(self):
        mode = self.view.get_input_mode()
    
        if mode == "file":
            file_path = self.view.get_batch_file_path()
            if not file_path:
                self.view.show_message(QMessageBox.Icon.Warning, "Gagal!", "Pilih file CSV terlebih dahulu!")
                return
            # Panggil BatchRoutingThread di sini...
        elif mode == "map":
            if self.source_osmid == None or self.dest_osmid == None:
                self.view.show_message(QMessageBox.Icon.Warning, "Gagal!", "Pilih simpul asal dan tujuan!")
                return

        active_algs = self.view.get_selected_algorithms()
        loop_count = self.view.get_loop_count()
        is_save_traversal = self.view.is_save_traversal()

        if not active_algs:
            self.view.show_message(QMessageBox.Icon.Warning, "Gagal!", "Pilih paling tidak 1 algoritma!")
            return

        self.view.show_message(QMessageBox.Icon.Information, "Sedang Memproses", "Algoritma sedang memproses rute di latar belakang. Silakan tunggu...")

        # 3. Create and Start the Background Thread
        if mode == "file":
            self.routing_thread = BatchRoutingThread(
                file_path, 
                state.indoDbPath, 
                active_algs,
                loop_count,
                is_save_traversal
            )
        elif mode == "map":
            self.routing_thread = RoutingThread(
                self.source_osmid, 
                self.dest_osmid, 
                state.indoDbPath, 
                active_algs,
                loop_count,
                is_save_traversal
            )
        
        self.view.set_mode_progress()

        # Connect the signal to receive the results when it finishes
        self.routing_thread.progress_updated.connect(self.view.update_progress)
        self.routing_thread.routing_finished.connect(self.on_routing_finished)
        
        # START THE THREAD (This runs without freezing the UI!)
        self.routing_thread.start()

    # 4. Handle the results back on the Main Thread
    def on_routing_finished(self, results):
        print("\n[Main Thread] Routing Complete! Results:")
        
        # text = "SUMMARY\n\n"
        # for alg_name, data in results.items():
        #     print(f"--- {alg_name.upper()} ---")
        #     print(f"Distance: {round(data['distance'], 2)} meters")
        #     print(f"Metrics: {data['metrics']}\n")
        #     text += f"""--- {alg_name.upper()} ---\nDistance: {round(data['distance'], 2)} meters\nMetrics: {data['metrics']}\n\n"""
            
        # You can now trigger your MapService to draw the winning path!
        # answer = self.view.show_question(None, "Sukses!", f"{text}Pencarian rute selesai! Simpan riwayat?")
        self.view.show_message(QMessageBox.Icon.Information, "Sukses!", f"Pencarian rute selesai!")
        self.view.set_mode_base()

        # if(answer == QMessageBox.StandardButton.Yes):
            # for alg_name, data in results.items():
            #     history = HistoryModel()
            #     history.insert(alg_name.upper(), self.source_osmid, self.dest_osmid, data['distance'], data['metrics']['exec_time'], data['metrics']['exec_space'], data['metrics']['vis_nodes'], data["created_at"])
            #     history_id = history.fetch_latest_id(data['created_at'], alg_name.upper())

            #     paths = PathModel()
            #     traversal_coords = paths.to_coords(data['traversal_path'])
            #     final_path_coords = paths.to_coords(data['final_path'])
            #     paths.insert_traversal(history_id, traversal_coords)
            #     paths.insert_final_path(history_id, final_path_coords)

        self.app_controller.route("HistoryView")

    def display_animated_map(self, center_lat, center_lon, final_path_coords, traversal_coords):
        """Called by HistoryController to show an animated route."""
        
        # 1. Ask the Service to build the map
        map_file_path = self.map_service.generate_animated_map(
            center_lat, 
            center_lon, 
            final_path_coords, 
            traversal_coords
        )
        
        # 2. Tell the View to load the file
        self.view.web_view.load(QUrl.fromLocalFile(map_file_path))
        self.view.set_mode_animated()

    def on_reset_clicked(self):
        """Reloads the clean base map and resets all clicking variables."""
        print("Returning to base map...")
        
        # A. Clear the selected nodes
        self.source_osmid = None
        self.dest_osmid = None
        
        # B. CRITICAL: Reset the Python click receiver count
        # If we don't do this, your next click will register as click #3!
        self.map_service.receiver.click_count = 0
        
        # C. Reload the original blank map into the browser!
        # Because the HTML page is reloading, the JavaScript variables 
        # (like the JS click count and active markers) will automatically reset too.
        self.view.web_view.load(QUrl.fromLocalFile(self.base_html_path))
        self.view.set_mode_base()

    def _toggle_mode_ui(self):
        """Memunculkan atau menyembunyikan input file berdasarkan radio button."""
        is_file_mode = True if self.view.get_input_mode() == "file" else False
        self.view.file_container.setVisible(is_file_mode)
        
        # Kirim sinyal ke JavaScript untuk mengunci atau membuka interaksi klik peta
        if is_file_mode:
            self.view.web_view.page().runJavaScript("lockMapInteractions(true);")
        else:
            self.view.web_view.page().runJavaScript("lockMapInteractions(false);")
            self.clear_batch_pinpoints()

    def _open_file_dialog(self):
        """Membuka dialog untuk memilih file skenario pengujian CSV."""
        path, _ = self.view.get_file_path()

        if path:
            self.view.selected_file_path = path
            filename = os.path.basename(path)
            self.view.lblFilePath.setText(filename)
            self.view.lblFilePath.setStyleSheet("color: black; font-weight: bold;")
            
            # Pemicu otomatis untuk merender pinpoints setelah file dipilih
            self.trigger_batch_pinpoints_render()

    def trigger_batch_pinpoints_render(self):
        """Meminta controller atau internal fungsi untuk merender pinpoints"""
        if not self.view.selected_file_path: return
        
        # Ambil koordinat dari file CSV
        indo_model = IndonesiaModel()
        points = indo_model.get_coordinates_from_csv(self.view.selected_file_path)
        
        # Tampilkan ke peta melalui JavaScript
        points_json = json.dumps(points)
        self.view.web_view.page().runJavaScript(f"renderBatchPinpoints({points_json});")

    def clear_batch_pinpoints(self):
        """Membersihkan pinpoints eksperimen ketika kembali ke mode manual"""
        self.view.web_view.page().runJavaScript("clearBatchPinpoints();")