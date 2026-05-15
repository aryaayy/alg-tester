from src.services.algs.SSSP import Dijkstra, AStar, BiDijkstra, BiAStar, BMSSP
from PySide6.QtCore import QThread, Signal
from src.models.HistoryModel import HistoryModel
import datetime

class RoutingThread(QThread):
    # This signal will carry a dictionary of results back to the Main Thread
    routing_finished = Signal(dict)

    def __init__(self, source_osmid, dest_osmid, db_path, active_algs):
        super().__init__()
        self.source_osmid = source_osmid
        self.dest_osmid = dest_osmid
        self.db_path = db_path
        self.active_algs = active_algs  # A list of algorithms to run

    def run(self):
        print("[Background Thread] Starting routing algorithms...")
        results = {}

        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Initiated at: {created_at}")

        # Run only the algorithms the user checked
        if "dijkstra" in self.active_algs:
            print("Running Dijkstra...")
            solver = Dijkstra()
            result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
            results["dijkstra"] = {"distance": result, "metrics": solver.metrics.to_dict(), "created_at": created_at}
            # history = HistoryModel()
            # history.insert("Dijkstra", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

        if "astar" in self.active_algs:
            print("Running A*...")
            solver = AStar()
            result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
            results["astar"] = {"distance": result, "metrics": solver.metrics.to_dict(), "created_at": created_at}
            # history = HistoryModel()
            # history.insert("A*", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

        if "bidijkstra" in self.active_algs:
            print("Running BiDijkstra...")
            solver = BiDijkstra()
            result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
            results["bidijkstra"] = {"distance": result, "metrics": solver.metrics.to_dict(), "created_at": created_at}
            # history = HistoryModel()
            # history.insert("Bi-Dijkstra", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

        if "biastar" in self.active_algs:
            print("Running BiA*...")
            solver = BiAStar()
            result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
            results["biastar"] = {"distance": result, "metrics": solver.metrics.to_dict(), "created_at": created_at}
            # history = HistoryModel()
            # history.insert("Bi-A*", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

        if "bmssp" in self.active_algs:
            print("Running BMSSP...")
            solver = BMSSP()
            result = solver.find_shortest_path(self.source_osmid, self.dest_osmid, self.db_path)
            results["bmssp"] = {"distance": result, "metrics": solver.metrics.to_dict(), "created_at": created_at}
            # history = HistoryModel()
            # history.insert("BMSSP", self.source_osmid, self.dest_osmid, result, solver.metrics.exec_time, solver.metrics.exec_space, solver.metrics.vis_nodes, created_at)

        # Send all the finished results back to the Main Thread safely!
        self.routing_finished.emit(results)