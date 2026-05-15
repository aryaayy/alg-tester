import tracemalloc
import time
import math

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

def haversine(s_lat, s_long, d_lat, d_long):
    R = 6371000.0

    lat1_rad = math.radians(s_lat)
    lat2_rad = math.radians(d_lat)

    delta_lat = math.radians(d_lat - s_lat)
    delta_long = math.radians(d_long - s_long)

    a = (math.sin(delta_lat/2)**2) + (math.cos(lat2_rad) * math.cos(lat1_rad) * (math.sin(delta_long/2)**2))
    a = min(1.0, a)

    dist = 2 * R * math.asin(math.sqrt(a))

    return dist