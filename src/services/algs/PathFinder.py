from abc import ABC, abstractmethod

from src.services.algs.Metrics import Metrics

class PathFinder(ABC):
    def __init__(self):
        self.metrics = Metrics()

    @abstractmethod
    def find_shortest_path(self, G, S, D, is_save_traversal):
        pass