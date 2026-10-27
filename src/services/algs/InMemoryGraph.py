from src.models.IndonesiaModel import IndonesiaModel

class InMemoryGraph:
    def __init__(self, db_model: IndonesiaModel):
        self.db = db_model
        self.edges = {}
        self.redges = {}
        self.coords = {}
        self.is_loaded = False

    def load_data(self):
        if self.is_loaded:
            return

        # load edges
        for u, v, w in self.db.edges():
            if w is None: continue
            w = float(w)
            
            # successors (forward edges)
            if u not in self.edges: self.edges[u] = []
            self.edges[u].append((v, w))
            
            # predecessors (backward edges)
            if v not in self.redges: self.redges[v] = []
            self.redges[v].append((u, w))

        # load nodes
        for osmid, y, x in self.db.nodes():
            self.coords[osmid] = (y, x)
            
        # set loading status
        self.is_loaded = True