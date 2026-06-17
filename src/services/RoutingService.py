from src.services.algs.SSSP import Dijkstra, AStar, BiDijkstra, BiAStar, BMSSP
from src.services.algs.PathFinder import PathFinder
from PySide6.QtCore import QThread, Signal
from src.models.HistoryModel import HistoryModel
from src.models.PathModel import PathModel
import datetime
import csv

class RoutingThread(QThread):
    routing_finished = Signal(dict)
    progress_updated = Signal(int, str) # 1. TAMBAHKAN SINYAL BARU DI SINI

    def __init__(self, source_osmid, dest_osmid, db_path, active_algs, loop_count, is_save_traversal):
        super().__init__()
        self.source_osmid = source_osmid
        self.dest_osmid = dest_osmid
        self.db_path = db_path
        self.active_algs = active_algs
        self.loop_count = loop_count
        self.is_save_traversal = is_save_traversal
        
        self.alg_classes = {
            "dijkstra": Dijkstra,
            "astar": AStar,
            "bidijkstra": BiDijkstra,
            "biastar": BiAStar,
            "bmssp": BMSSP
        }

    def run(self):
        print("[Background Thread] Starting routing algorithms...")
        results = [{} for _ in range(self.loop_count)]
        summary = {}

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 2. HITUNG TOTAL LANGKAH UNTUK PERSENTASE
        total_steps = self.loop_count * len(self.active_algs) * 2
        current_step = 0

        try:
            for i in range(self.loop_count):
                for alg_name in self.active_algs:
                    if alg_name not in self.alg_classes:
                        continue
                        
                    # 3. UPDATE PROGRESS SETIAP KALI ALGORITMA AKAN BERJALAN
                    percent = int((current_step / total_steps) * 100)
                    pesan = f"Iterasi {i+1}/{self.loop_count} | Menjalankan {alg_name.upper()}..."
                    self.progress_updated.emit(percent, pesan)
                    
                    solver = self.alg_classes[alg_name]()
                    result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
                    
                    results[i][alg_name] = {
                        "distance": result["distance"], 
                        "traversal_path": result["visited"], 
                        "final_path": result["final_path"], 
                        "metrics": solver.metrics.to_dict(), 
                        "created_at": created_at
                    }

                    current_step += 1

                    percent = int((current_step / total_steps) * 100)
                    pesan = f"Iterasi {i+1}/{self.loop_count} | Menyimpan hasil routing {alg_name.upper()}..."
                    self.progress_updated.emit(percent, pesan)

                    # Simpan ke DB (History & Path)
                    history = HistoryModel()
                    history.insert(
                        alg_name.upper(), self.source_osmid, self.dest_osmid, 
                        results[i][alg_name]['distance'], results[i][alg_name]['metrics']['exec_time'], 
                        results[i][alg_name]['metrics']['exec_space'], results[i][alg_name]['metrics']['vis_nodes'], 
                        results[i][alg_name]["created_at"]
                    )

                    if self.is_save_traversal:
                        history_id = history.fetch_latest_id(created_at, alg_name.upper())

                        paths = PathModel()
                        traversal_coords = paths.to_coords(results[i][alg_name]['traversal_path'])
                        final_path_coords = paths.to_coords(results[i][alg_name]['final_path'])
                        paths.insert_traversal(history_id, traversal_coords)
                        paths.insert_final_path(history_id, final_path_coords)
                    
                    current_step += 1
        except Exception as e:
            percent = int((current_step / total_steps) * 100)
            pesan = f"Gagal! {str(e)}"
            self.progress_updated.emit(percent, pesan)
            self.routing_finished.emit({"msg": e})
            print(e)
            return

        percent = int((current_step / total_steps) * 100)
        pesan = f"Selesai"
        self.progress_updated.emit(percent, pesan)

        # (Bagian kalkulasi summary ke bawah tetap sama persis seperti sebelumnya)
        for alg_name in self.active_algs:
            summary[alg_name] = {
                "distance": 0.0,
                "metrics": {
                    "exec_time": 0.0,
                    "exec_space": 0.0,
                    "vis_nodes": 0.0,
                }
            }

        for i in range(self.loop_count):
            for alg_name, data in results[i].items():
                summary[alg_name]["distance"] += data['distance']
                summary[alg_name]["metrics"]["exec_time"] += data['metrics']['exec_time']
                summary[alg_name]["metrics"]["exec_space"] += data['metrics']['exec_space']
                summary[alg_name]["metrics"]["vis_nodes"] += data['metrics']['vis_nodes']
        
        for alg_name in self.active_algs:
            summary[alg_name]["distance"] /= self.loop_count
            summary[alg_name]["metrics"]["exec_time"] /= self.loop_count
            summary[alg_name]["metrics"]["exec_space"] /= self.loop_count
            summary[alg_name]["metrics"]["vis_nodes"] /= self.loop_count

        self.routing_finished.emit(summary)

# =====================================================================
# 2. BATCH ROUTING THREAD BARU (UNTUK EKSPERIMEN SKRIPSI)
# =====================================================================
class BatchRoutingThread(QThread):
    progress_updated = Signal(int, str) # Sinyal untuk ProgressBar (persentase, pesan)
    routing_finished = Signal(str)        # Mengirimkan teks ringkasan (summary) ke UI

    def __init__(self, csv_file_path, db_path, active_algs, loop_count, is_save_traversal):
        super().__init__()
        self.csv_file_path = csv_file_path
        self.db_path = db_path
        self.active_algs = active_algs
        self.loop_count = loop_count
        self.is_save_traversal = is_save_traversal

        self.alg_classes = {
            "dijkstra": Dijkstra,
            "astar": AStar,
            "bidijkstra": BiDijkstra,
            "biastar": BiAStar,
            "bmssp": BMSSP
        }

    def run(self):
        print(f"[Batch Thread] Memulai eksperimen dari file: {self.csv_file_path}")
        
        # 1. BACA FILE SKENARIO
        scenarios = []
        try:
            with open(self.csv_file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    scenarios.append(row)
        except Exception as e:
            self.routing_finished.emit(f"ERROR: Gagal membaca CSV. Pastikan format benar. ({str(e)})")
            return

        db_created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        total_tasks = (self.loop_count) * 2 * len(scenarios) * len(self.active_algs)
        current_task = 0
        
        # Variabel untuk summary di akhir
        total_success = 0
        
        try:
            # 2. EKSEKUSI SKENARIO
            for idx, scenario in enumerate(scenarios):
                kategori = scenario.get('kategori', f"Row_{idx+1}")
                source = int(scenario.get('source_osmid', 0))
                dest = int(scenario.get('dest_osmid', 0))

                for alg_name in self.active_algs:

                    for i in range(self.loop_count):
                        percent = int((current_task / total_tasks) * 100)
                        msg = f"Menjalankan {alg_name.upper()} | {kategori.upper()} | Skenario {idx+1}/{len(scenarios)} | Iterasi {i+1}/{self.loop_count}"
                        self.progress_updated.emit(percent, msg)

                        solver: PathFinder = self.alg_classes[alg_name]()

                        result = solver.find_shortest_path(source, dest, self.db_path)

                        current_task += 1
                        
                        percent = int((current_task / total_tasks) * 100)
                        msg = f"Menyimpan hasil routing {alg_name.upper()} | {kategori.upper()} | Skenario {idx+1}/{len(scenarios)} | Iterasi {i+1}/{self.loop_count}"
                        self.progress_updated.emit(percent, msg)

                        summary = {
                            "distance": result["distance"], 
                            "traversal_path": result["visited"], 
                            "final_path": result["final_path"], 
                            "metrics": solver.metrics.to_dict(), 
                            "created_at": db_created_at
                        }
                        
                        # Simpan ke DB (History & Path)
                        history = HistoryModel()
                        history.insert(
                            alg_name.upper(), source, dest, 
                            summary['distance'], summary['metrics']['exec_time'], 
                            summary['metrics']['exec_space'], summary['metrics']['vis_nodes'], 
                            summary["created_at"]
                        )
                        
                        if self.is_save_traversal:
                            history_id = history.fetch_latest_id(db_created_at, alg_name.upper())

                            paths = PathModel()
                            traversal_coords = paths.to_coords(summary["traversal_path"])
                            final_path_coords = paths.to_coords(summary["final_path"])
                            paths.insert_traversal(history_id, traversal_coords)
                            paths.insert_final_path(history_id, final_path_coords)
                        
                        current_task += 1
                    
                    total_success += 1
        except Exception as e:
            percent = int((current_task / total_tasks) * 100)
            pesan = f"Gagal! {str(e)}"
            self.progress_updated.emit(percent, pesan)
            self.routing_finished.emit(str(e))
            print(e)
            return

        percent = int((current_task / total_tasks) * 100)
        msg = f"Selesai"
        self.progress_updated.emit(percent, msg)
        
        # 4. BUAT SUMMARY UNTUK DIALOG BOX UI
        summary_teks = (
            f"Eksperimen Batch selesai!\n\n"
            f"Jumlah Skenario: {len(scenarios)}\n"
            f"Algoritma Diuji: {len(self.active_algs)}\n"
            f"Iterasi per Rute: {self.loop_count} kali\n"
            f"Total Data Disimpan ke Database: {total_success} baris\n\n"
            f"Anda dapat melihat data selengkapnya di menu 'Riwayat' "
            f"atau mengekspornya ke CSV dari menu 'File'."
        )
        
        # Kirim teks ke Controller agar dimunculkan di QMessageBox
        self.routing_finished.emit(summary_teks)

# # =====================================================================
# # 2. BATCH ROUTING THREAD BARU (UNTUK EKSPERIMEN SKRIPSI)
# # =====================================================================
# class BatchRoutingThread(QThread):
#     progress_updated = Signal(int, str) # Sinyal untuk ProgressBar (persentase, pesan)
#     routing_finished = Signal(str)        # Mengirimkan teks ringkasan (summary) ke UI

#     def __init__(self, csv_file_path, db_path, active_algs, loop_count):
#         super().__init__()
#         self.csv_file_path = csv_file_path
#         self.db_path = db_path
#         self.active_algs = active_algs
#         self.loop_count = loop_count

#         self.alg_classes = {
#             "dijkstra": Dijkstra,
#             "astar": AStar,
#             "bidijkstra": BiDijkstra,
#             "biastar": BiAStar,
#             "bmssp": BMSSP
#         }

#     def run(self):
#         print(f"[Batch Thread] Memulai eksperimen dari file: {self.csv_file_path}")
        
#         # 1. BACA FILE SKENARIO
#         scenarios = []
#         try:
#             with open(self.csv_file_path, mode='r', encoding='utf-8-sig') as f:
#                 reader = csv.DictReader(f)
#                 for row in reader:
#                     scenarios.append(row)
#         except Exception as e:
#             self.routing_finished.emit(f"ERROR: Gagal membaca CSV. Pastikan format benar. ({str(e)})")
#             return

#         db_created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#         total_tasks = (self.loop_count+1) * len(scenarios) * len(self.active_algs)
#         current_task = 0
        
#         # Variabel untuk summary di akhir
#         total_success = 0
        
#         # 2. EKSEKUSI SKENARIO
#         for idx, scenario in enumerate(scenarios):
#             kategori = scenario.get('kategori', f"Row_{idx+1}")
#             source = int(scenario.get('source_osmid', 0))
#             dest = int(scenario.get('dest_osmid', 0))

#             for alg_name in self.active_algs:
                
#                 # Update UI Loading
#                 msg = f"Menjalankan {alg_name.upper()} | {kategori.upper()} | Skenario {idx+1}/{len(scenarios)}"

#                 # Syarat Bab 3.6.3: Rata-rata dari n iterasi
#                 total_dist = 0.0
#                 total_time = 0.0
#                 total_space = 0.0
#                 total_nodes = 0
                
#                 final_path_to_save = []
#                 traversal_path_to_save = []

#                 for i in range(self.loop_count):
#                     percent = int((current_task / total_tasks) * 100)
#                     msg_itr = f"{msg} | Iterasi {i+1}/{self.loop_count}"
#                     self.progress_updated.emit(percent, msg_itr)

#                     solver: PathFinder = self.alg_classes[alg_name]()

#                     result = solver.find_shortest_path(source, dest, self.db_path)
                    
#                     total_dist = result['distance'] 
#                     total_time += solver.metrics.exec_time
#                     total_space += solver.metrics.exec_space
#                     total_nodes += solver.metrics.vis_nodes

#                     if i == 0:
#                         final_path_to_save = result['final_path']
#                         traversal_path_to_save = result['visited']
                    
#                     current_task += 1

#                 percent = int((current_task / total_tasks) * 100)
#                 msg = f"Menyimpan hasil routing {alg_name.upper()} | {kategori.upper()} | Skenario {idx+1}/{len(scenarios)}"
#                 self.progress_updated.emit(percent, msg)

#                 # Hitung Rata-rata akhir
#                 avg_time = total_time / self.loop_count
#                 avg_space = total_space / self.loop_count
#                 avg_nodes = int(total_nodes / self.loop_count)

#                 # -------------------------------------------------------------
#                 # 3. SIMPAN KE DATABASE (HISTORY & PATH)
#                 # -------------------------------------------------------------
                
#                 history = HistoryModel()
#                 history.insert(
#                     alg_name.upper(), 
#                     source, 
#                     dest, 
#                     total_dist, 
#                     avg_time, 
#                     avg_space, 
#                     avg_nodes, 
#                     db_created_at
#                 )
#                 history_id = history.fetch_latest_id(db_created_at, alg_name.upper())

#                 paths = PathModel()
#                 traversal_coords = paths.to_coords(traversal_path_to_save)
#                 final_path_coords = paths.to_coords(final_path_to_save)
#                 paths.insert_traversal(history_id, traversal_coords)
#                 paths.insert_final_path(history_id, final_path_coords)
#                 # -------------------------------------------------------------
                
#                 current_task += 1
#                 total_success += 1

#         percent = int((current_task / total_tasks) * 100)
#         msg = f"Selesai"
#         self.progress_updated.emit(percent, msg)
        
#         # 4. BUAT SUMMARY UNTUK DIALOG BOX UI
#         summary_teks = (
#             f"Eksperimen Batch selesai!\n\n"
#             f"Jumlah Skenario: {len(scenarios)}\n"
#             f"Algoritma Diuji: {len(self.active_algs)}\n"
#             f"Iterasi per Rute: {self.loop_count} kali\n"
#             f"Total Data Disimpan ke Database: {total_success} baris\n\n"
#             f"Anda dapat melihat data selengkapnya di menu 'Riwayat' "
#             f"atau mengekspornya ke CSV dari menu 'File'."
#         )
        
#         # Kirim teks ke Controller agar dimunculkan di QMessageBox
#         self.routing_finished.emit(summary_teks)