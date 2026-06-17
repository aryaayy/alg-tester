from abc import ABC, abstractmethod
import networkx as nx

from src.services.algs.Helper import Metrics

class PathFinder(ABC):
    def __init__(self):
        self.metrics = Metrics()

    @abstractmethod
    def find_shortest_path(self, S, D):
        pass