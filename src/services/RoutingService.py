from src.services.algs.SSSP import Dijkstra, AStar, BiDijkstra, BiAStar, BMSSP
from PySide6.QtCore import QThread, Signal
from src.models.HistoryModel import HistoryModel
from src.models.PathModel import PathModel
import datetime

class RoutingThread(QThread):
    # This signal will carry a dictionary of results back to the Main Thread
    routing_finished = Signal(dict)

    def __init__(self, source_osmid, dest_osmid, db_path, active_algs, loop_count):
        super().__init__()
        self.source_osmid = source_osmid
        self.dest_osmid = dest_osmid
        self.db_path = db_path
        self.active_algs = active_algs
        self.loop_count = loop_count

    def run(self):
        print("[Background Thread] Starting routing algorithms...")
        results = [{} for _ in range(self.loop_count)]
        summary = {}

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Initiated at: {created_at}")

        i = 0
        for i in range(self.loop_count):
            # Run only the algorithms the user checked
            if "dijkstra" in self.active_algs:
                print("Running Dijkstra...")
                solver = Dijkstra()
                result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
                results[i]["dijkstra"] = {"distance": result["distance"], "traversal_path": result["visited"], "final_path": result["final_path"], "metrics": solver.metrics.to_dict(), "created_at": created_at}

                history = HistoryModel()
                history.insert("DIJKSTRA", self.source_osmid, self.dest_osmid, results[i]['dijkstra']['distance'], results[i]['dijkstra']['metrics']['exec_time'], results[i]['dijkstra']['metrics']['exec_space'], results[i]['dijkstra']['metrics']['vis_nodes'], results[i]['dijkstra']["created_at"])
                history_id = history.fetch_latest_id(created_at, "DIJKSTRA")

                paths = PathModel()
                traversal_coords = paths.to_coords(results[i]['dijkstra']['traversal_path'])
                final_path_coords = paths.to_coords(results[i]['dijkstra']['final_path'])
                paths.insert_traversal(history_id, traversal_coords)
                paths.insert_final_path(history_id, final_path_coords)
                # history = HistoryModel()
                # history.insert("Dijkstra", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

            if "astar" in self.active_algs:
                print("Running A*...")
                solver = AStar()
                result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
                results[i]["astar"] = {"distance": result["distance"], "traversal_path": result["visited"], "final_path": result["final_path"], "metrics": solver.metrics.to_dict(), "created_at": created_at}

                history = HistoryModel()
                history.insert("ASTAR", self.source_osmid, self.dest_osmid, results[i]['astar']['distance'], results[i]['astar']['metrics']['exec_time'], results[i]['astar']['metrics']['exec_space'], results[i]['astar']['metrics']['vis_nodes'], results[i]['astar']["created_at"])
                history_id = history.fetch_latest_id(created_at, "ASTAR")

                paths = PathModel()
                traversal_coords = paths.to_coords(results[i]['astar']['traversal_path'])
                final_path_coords = paths.to_coords(results[i]['astar']['final_path'])
                paths.insert_traversal(history_id, traversal_coords)
                paths.insert_final_path(history_id, final_path_coords)
                # history = HistoryModel()
                # history.insert("A*", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

            if "bidijkstra" in self.active_algs:
                print("Running BiDijkstra...")
                solver = BiDijkstra()
                result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
                results[i]["bidijkstra"] = {"distance": result["distance"], "traversal_path": result["visited"], "final_path": result["final_path"], "metrics": solver.metrics.to_dict(), "created_at": created_at}

                history = HistoryModel()
                history.insert("BIDIJKSTRA", self.source_osmid, self.dest_osmid, results[i]['bidijkstra']['distance'], results[i]['bidijkstra']['metrics']['exec_time'], results[i]['bidijkstra']['metrics']['exec_space'], results[i]['bidijkstra']['metrics']['vis_nodes'], results[i]['bidijkstra']["created_at"])
                history_id = history.fetch_latest_id(created_at, "BIDIJKSTRA")

                paths = PathModel()
                traversal_coords = paths.to_coords(results[i]['bidijkstra']['traversal_path'])
                final_path_coords = paths.to_coords(results[i]['bidijkstra']['final_path'])
                paths.insert_traversal(history_id, traversal_coords)
                paths.insert_final_path(history_id, final_path_coords)
                # history = HistoryModel()
                # history.insert("Bi-Dijkstra", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

            if "biastar" in self.active_algs:
                print("Running BiA*...")
                solver = BiAStar()
                result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
                results[i]["biastar"] = {"distance": result["distance"], "traversal_path": result["visited"], "final_path": result["final_path"], "metrics": solver.metrics.to_dict(), "created_at": created_at}

                history = HistoryModel()
                history.insert("BIASTAR", self.source_osmid, self.dest_osmid, results[i]['biastar']['distance'], results[i]['biastar']['metrics']['exec_time'], results[i]['biastar']['metrics']['exec_space'], results[i]['biastar']['metrics']['vis_nodes'], results[i]['biastar']["created_at"])
                history_id = history.fetch_latest_id(created_at, "BIASTAR")

                paths = PathModel()
                traversal_coords = paths.to_coords(results[i]['biastar']['traversal_path'])
                final_path_coords = paths.to_coords(results[i]['biastar']['final_path'])
                paths.insert_traversal(history_id, traversal_coords)
                paths.insert_final_path(history_id, final_path_coords)
                # history = HistoryModel()
                # history.insert("Bi-A*", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

            if "bmssp" in self.active_algs:
                print("Running BMSSP...")
                solver = BMSSP()
                result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
                results[i]["bmssp"] = {"distance": result["distance"], "traversal_path": result["visited"], "final_path": result["final_path"], "metrics": solver.metrics.to_dict(), "created_at": created_at}

                history = HistoryModel()
                history.insert("BMSSP", self.source_osmid, self.dest_osmid, results[i]['bmssp']['distance'], results[i]['bmssp']['metrics']['exec_time'], results[i]['bmssp']['metrics']['exec_space'], results[i]['bmssp']['metrics']['vis_nodes'], results[i]['bmssp']["created_at"])
                history_id = history.fetch_latest_id(created_at, "BMSSP")

                paths = PathModel()
                traversal_coords = paths.to_coords(results[i]['bmssp']['traversal_path'])
                final_path_coords = paths.to_coords(results[i]['bmssp']['final_path'])
                paths.insert_traversal(history_id, traversal_coords)
                paths.insert_final_path(history_id, final_path_coords)
                # history = HistoryModel()
                # history.insert("BMSSP", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

        for alg_name in self.active_algs:
            summary[alg_name] = {
                "distance": 0.0,
                "metrics": {
                    "exec_time": 0.0,
                    "exec_space": 0.0,
                    "vis_nodes": 0.0,
                }
            }

        i = 0
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

        # Send all the finished results back to the Main Thread safely!
        self.routing_finished.emit(summary)