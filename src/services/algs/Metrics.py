import tracemalloc
import time

class Metrics:
    exec_time: float
    exec_space: float
    vis_nodes: int

    def __init__(self):
        self.exec_time = 0.0
        self.exec_space = 0.0
        self.vis_nodes = 0

    def to_dict(self):
        metrics = {
            "exec_time": self.exec_time,
            "exec_space": self.exec_space,
            "vis_nodes": self.vis_nodes
        }
        return metrics
    
    def __enter__(self):
        tracemalloc.start()
        self._start = time.time()

    def __exit__(self, exc_type, exc, tb):
        end = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        self.exec_time = end - self._start
        self.exec_space = peak