from src.services.algs.PathFinder import PathFinder
from src.services.algs.Helper import haversine
import heapq
import math
import sqlite3

class AStar(PathFinder):
    # Removed G, added db_path
    def find_shortest_path(self, S, D, db_path="sumatra.db"):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        def run_alg():
            self.metrics.vis_nodes = 0
            
            # 1. Fetch Coordinates for Source and Destination upfront
            c.execute("SELECT y, x FROM nodes WHERE osmid = ?", (S,))
            s_coords = c.fetchone()
            
            c.execute("SELECT y, x FROM nodes WHERE osmid = ?", (D,))
            d_coords = c.fetchone()
            
            # Safety check if nodes don't exist in DB
            if not s_coords or not d_coords:
                return float('inf')
                
            s_y, s_x = s_coords
            d_y, d_x = d_coords
            
            frontier = []
            
            # Lazy dictionaries to save memory
            g_score = {}
            f_score = {}
            
            g_score[S] = 0
            f_score[S] = haversine(s_y, s_x, d_y, d_x)
            
            heapq.heappush(frontier, (f_score[S], S))
            
            while frontier:
                current_f_score, current_node = heapq.heappop(frontier)
                
                self.metrics.vis_nodes += 1
                
                if current_f_score > f_score.get(current_node, float('inf')):
                    continue
                    
                if current_node == D:
                    return g_score[D]
                    
                # 2. Query neighbors, shortest edge, AND neighbor coordinates at the same time
                c.execute("""
                    SELECT e.target, MIN(e.length), n.y, n.x
                    FROM edges e
                    JOIN nodes n ON e.target = n.osmid
                    WHERE e.source = ?
                    GROUP BY e.target
                """, (current_node,))
                
                neighbors = c.fetchall()
                
                for target_node, w, n_y, n_x in neighbors:
                    if w is None:
                        continue
                        
                    w = float(w)
                    new_g_score = g_score[current_node] + w
                    
                    if new_g_score < g_score.get(target_node, float('inf')):
                        g_score[target_node] = new_g_score
                        
                        # Calculate heuristic using the joined coordinates
                        h = haversine(n_y, n_x, d_y, d_x)
                        f_score[target_node] = new_g_score + h
                        
                        heapq.heappush(frontier, (f_score[target_node], target_node))
                        
            return float('inf')
        
        with self.metrics:
            result = run_alg()

        conn.close()
        return result

class BiAStar(PathFinder):
    def find_shortest_path(self, S, D, db_path="sumatra.db"):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        def run_alg():
            self.metrics.vis_nodes = 0
            
            if S == D:
                return 0
                
            # 1. Fetch Source and Destination coordinates upfront
            c.execute("SELECT y, x FROM nodes WHERE osmid = ?", (S,))
            s_coords = c.fetchone()
            
            c.execute("SELECT y, x FROM nodes WHERE osmid = ?", (D,))
            d_coords = c.fetchone()
            
            if not s_coords or not d_coords:
                return float('inf')
                
            s_lat, s_lon = s_coords
            t_lat, t_lon = d_coords
            
            L = float('inf')
            
            # Lazy initialization for Forward Search
            g_f = {}
            g_f[S] = 0
            frontier_f = []
            h_S_t = haversine(s_lat, s_lon, t_lat, t_lon)
            # OPTIMIZATION: Store lat/lon in the queue to avoid extra DB queries
            heapq.heappush(frontier_f, (h_S_t, 0, S, s_lat, s_lon))
            
            # Lazy initialization for Backward Search
            g_b = {}
            g_b[D] = 0
            frontier_b = []
            h_T_s = haversine(t_lat, t_lon, s_lat, s_lon)
            heapq.heappush(frontier_b, (h_T_s, 0, D, t_lat, t_lon))

            while frontier_f or frontier_b:
                
                # --- FORWARD SEARCH ---
                if frontier_f:
                    F_b = frontier_b[0][0] if frontier_b else float('inf')
                    
                    # Unpack the coordinates from our optimized queue
                    f_u, g_u, u, u_lat, u_lon = heapq.heappop(frontier_f)

                    if g_u <= g_f.get(u, float('inf')):
                        self.metrics.vis_nodes += 1
                        
                        h_u_t = haversine(u_lat, u_lon, t_lat, t_lon) # h(u)
                        h_b_u = haversine(u_lat, u_lon, s_lat, s_lon) # h~(u)
                        
                        if not (g_u + h_u_t >= L or g_u + F_b - h_b_u >= L):
                            
                            # Successors (Where 'u' is source) JOINED with nodes to get coords
                            c.execute("""
                                SELECT e.target, MIN(e.length), n.y, n.x
                                FROM edges e
                                JOIN nodes n ON e.target = n.osmid
                                WHERE e.source = ?
                                GROUP BY e.target
                            """, (u,))
                            
                            for v, w, v_lat, v_lon in c.fetchall():
                                if w is None: continue
                                w = float(w)
                                
                                new_g = g_u + w
                                if new_g < g_f.get(v, float('inf')):
                                    g_f[v] = new_g
                                    f_v = new_g + haversine(v_lat, v_lon, t_lat, t_lon)
                                    heapq.heappush(frontier_f, (f_v, new_g, v, v_lat, v_lon))
                                
                                if g_f.get(v, float('inf')) + g_b.get(v, float('inf')) < L:
                                    L = g_f[v] + g_b[v]

                # --- BACKWARD SEARCH ---
                if frontier_b:
                    F_f = frontier_f[0][0] if frontier_f else float('inf')
                    
                    f_u, g_u, u, u_lat, u_lon = heapq.heappop(frontier_b)
                    
                    if g_u <= g_b.get(u, float('inf')):
                        self.metrics.vis_nodes += 1
                        
                        h_u_s = haversine(u_lat, u_lon, s_lat, s_lon) # h~(u)
                        h_f_u = haversine(u_lat, u_lon, t_lat, t_lon) # h(u)
                        
                        if not (g_u + h_u_s >= L or g_u + F_f - h_f_u >= L):
                            
                            # Predecessors (Where 'u' is target) JOINED with nodes to get coords
                            c.execute("""
                                SELECT e.source, MIN(e.length), n.y, n.x
                                FROM edges e
                                JOIN nodes n ON e.source = n.osmid
                                WHERE e.target = ?
                                GROUP BY e.source
                            """, (u,))
                            
                            for v, w, v_lat, v_lon in c.fetchall():
                                if w is None: continue
                                w = float(w)
                                
                                new_g = g_u + w
                                if new_g < g_b.get(v, float('inf')):
                                    g_b[v] = new_g
                                    f_v = new_g + haversine(v_lat, v_lon, s_lat, s_lon)
                                    heapq.heappush(frontier_b, (f_v, new_g, v, v_lat, v_lon))
                                    
                                if g_f.get(v, float('inf')) + g_b.get(v, float('inf')) < L:
                                    L = g_f[v] + g_b[v]

            return L if L != float('inf') else float('inf')
        
        with self.metrics:
            result = run_alg()

        conn.close()
        return result
    
class BiDijkstra(PathFinder):
    def find_shortest_path(self, S, D, db_path="sumatra.db"):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        def run_alg():
            self.metrics.vis_nodes = 0
            
            if S == D:
                return 0
                
            mu = float('inf')
            
            # Lazy initialization for dictionaries
            dist_f = {}
            dist_f[S] = 0
            frontier_f = []
            heapq.heappush(frontier_f, (0, S))
            closed_f = set()
            
            dist_b = {}
            dist_b[D] = 0
            frontier_b = []
            heapq.heappush(frontier_b, (0, D))
            closed_b = set()
            
            d_u_s = 0
            d_u_t = 0
            
            while frontier_f or frontier_b:
                
                # --- FORWARD SEARCH ---
                if frontier_f:
                    current_dist_f, u = heapq.heappop(frontier_f)
                    
                    if current_dist_f <= dist_f.get(u, float('inf')):
                        closed_f.add(u)
                        self.metrics.vis_nodes += 1
                        
                        d_u_s = current_dist_f
                        
                        if d_u_s + d_u_t >= mu:
                            return mu
                            
                        # Successors: Where 'u' is the source
                        c.execute("""
                            SELECT target, MIN(length) 
                            FROM edges 
                            WHERE source = ? 
                            GROUP BY target
                        """, (u,))
                        
                        for v, w in c.fetchall():
                            if w is None:
                                continue
                            w = float(w)
                            
                            if v not in closed_f:
                                new_dist = dist_f[u] + w
                                if new_dist < dist_f.get(v, float('inf')):
                                    dist_f[v] = new_dist
                                    heapq.heappush(frontier_f, (new_dist, v))
                        
                            if v in closed_b:
                                mu = min(mu, dist_f[u] + w + dist_b.get(v, float('inf')))

                # --- BACKWARD SEARCH ---
                if frontier_b:
                    current_dist_b, u = heapq.heappop(frontier_b)
                    
                    if current_dist_b <= dist_b.get(u, float('inf')):
                        closed_b.add(u)
                        self.metrics.vis_nodes += 1
                        
                        d_u_t = current_dist_b
                        
                        if d_u_s + d_u_t >= mu:
                            return mu
                            
                        # Predecessors: Where 'u' is the target
                        c.execute("""
                            SELECT source, MIN(length) 
                            FROM edges 
                            WHERE target = ? 
                            GROUP BY source
                        """, (u,))
                        
                        for v, w in c.fetchall():
                            if w is None:
                                continue
                            w = float(w)
                            
                            if v not in closed_b:
                                new_dist = dist_b[u] + w
                                if new_dist < dist_b.get(v, float('inf')):
                                    dist_b[v] = new_dist
                                    heapq.heappush(frontier_b, (new_dist, v))
                        
                            if v in closed_f:
                                mu = min(mu, dist_b[u] + w + dist_f.get(v, float('inf')))

            return mu if mu != float('inf') else float('inf')
        
        with self.metrics:
            result = run_alg()

        conn.close()
        return result
    
class BMSSPDS:
    def __init__(self, M, B):
        self.M = max(1, M)
        self.B = B
        self.heap = []
    
    def insert(self, item):
        heapq.heappush(self.heap, item)

    def pull(self):
        if not self.heap:
            return self.B, set()
        
        Si = set()
        while self.heap and len(Si) < self.M:
            dist, node = heapq.heappop(self.heap)
            if node not in Si:
                Si.add(node)
                
        while self.heap and self.heap[0][1] in Si:
            heapq.heappop(self.heap)

        Bi = self.heap[0][0] if self.heap else self.B
        return Bi, Si

    def batch_prepend(self, item_set):
        for item in item_set:
            self.insert(item)
    
    def is_empty(self):
        return len(self.heap) == 0

class BMSSP(PathFinder):
    def __init__(self):
        super().__init__()
        self.dist_hat = {}
        self.c = None  # We will store the DB cursor here for recursive access
    
    def _find_pivots(self, B, S, k):
        W = set(S)
        W_prev = set(S)
        
        for i in range(1, k + 1):
            W_curr = set()
            for u in W_prev:
                self.metrics.vis_nodes += 1
                
                # SQLite Successors
                self.c.execute("""
                    SELECT target, MIN(length) 
                    FROM edges 
                    WHERE source = ? 
                    GROUP BY target
                """, (u,))
                
                for v, w_uv in self.c.fetchall():
                    if w_uv is None: continue
                    w_uv = float(w_uv)
                    
                    dist_u = self.dist_hat.get(u, float('inf'))
                    dist_v = self.dist_hat.get(v, float('inf'))
                    
                    if dist_u + w_uv <= dist_v:
                        self.dist_hat[v] = dist_u + w_uv
                        if dist_u + w_uv < B:
                            W_curr.add(v)
            
            W.update(W_curr)
            W_prev = W_curr
            
            if len(W) > k * len(S):
                return set(S), W
                
        P = set(S) 
        return P, W

    def _base_case(self, B, S, k):
        if not S:
            return B, set()
            
        x = list(S)[0]
        U0 = set()
        H = []
        heapq.heappush(H, (self.dist_hat.get(x, float('inf')), x))
        
        while H and len(U0) < k + 1:
            d_u, u = heapq.heappop(H)
            
            if d_u > self.dist_hat.get(u, float('inf')):
                continue
                
            U0.add(u)
            self.metrics.vis_nodes += 1
            
            # SQLite Successors
            self.c.execute("""
                SELECT target, MIN(length) 
                FROM edges 
                WHERE source = ? 
                GROUP BY target
            """, (u,))
            
            for v, w_uv in self.c.fetchall():
                if w_uv is None: continue
                w_uv = float(w_uv)
                
                new_dist = self.dist_hat.get(u, float('inf')) + w_uv
                if new_dist <= self.dist_hat.get(v, float('inf')) and new_dist < B:
                    self.dist_hat[v] = new_dist
                    heapq.heappush(H, (new_dist, v))
                    
        if len(U0) <= k:
            return B, U0
        else:
            B_prime = max([self.dist_hat.get(v, float('inf')) for v in U0]) if U0 else B
            U_return = {v for v in U0 if self.dist_hat.get(v, float('inf')) < B_prime}
            return B_prime, U_return

    def _bmssp_recursive(self, l, B, S, k, t):
        if l == 0:
            return self._base_case(B, S, k)
            
        P, W = self._find_pivots(B, S, k)
        
        M = max(1, int(2 ** ((l - 1) * t)))
        D = BMSSPDS(M, B)
        
        for x in P:
            D.insert((self.dist_hat.get(x, float('inf')), x))
            
        current_B_prime = min([self.dist_hat.get(x, float('inf')) for x in P]) if P else B
        U = set()
        
        max_u_size = k * (2 ** (l * t))
        prev_u_size = len(U)
        
        while len(U) < max_u_size and not D.is_empty():
            Bi, Si = D.pull()
            
            Bi_prime, Ui = self._bmssp_recursive(l - 1, Bi, Si, k, t)
            current_B_prime = Bi_prime  
            U.update(Ui)
            
            K_set = set()
            for u in Ui:
                self.metrics.vis_nodes += 1
                
                # SQLite Successors
                self.c.execute("""
                    SELECT target, MIN(length) 
                    FROM edges 
                    WHERE source = ? 
                    GROUP BY target
                """, (u,))
                
                for v, w_uv in self.c.fetchall():
                    if w_uv is None: continue
                    w_uv = float(w_uv)
                    
                    new_dist = self.dist_hat.get(u, float('inf')) + w_uv
                    if new_dist <= self.dist_hat.get(v, float('inf')):
                        self.dist_hat[v] = new_dist
                        
                        if Bi <= new_dist < B:
                            D.insert((new_dist, v))
                        elif Bi_prime <= new_dist < Bi:
                            K_set.add((new_dist, v))
                            
            batch_items = K_set.union({(self.dist_hat.get(x, float('inf')), x) for x in Si if Bi_prime <= self.dist_hat.get(x, float('inf')) < Bi})
            D.batch_prepend(batch_items)

            if len(U) == prev_u_size and not batch_items:
                break
            prev_u_size = len(U)
            
        final_B_prime = min(current_B_prime, B)
        U.update({x for x in W if self.dist_hat.get(x, float('inf')) < final_B_prime})
        
        return final_B_prime, U

    def find_shortest_path(self, S, D, db_path="sumatra.db"):
        conn = sqlite3.connect(db_path)
        self.c = conn.cursor()

        def run_alg():
            self.metrics.vis_nodes = 0
            
            self.dist_hat = {} # Start entirely empty
            self.dist_hat[S] = 0
            
            # Fetch the total number of nodes in the graph to calculate 'k' and 't' bounds
            self.c.execute("SELECT COUNT(*) FROM nodes")
            V = self.c.fetchone()[0]
            
            log_n = math.log2(V) if V > 1 else 1
            
            k = max(1, int(math.floor(log_n ** (1/3))))
            t = max(1, int(math.floor(log_n ** (2/3))))
            l = max(1, int(math.ceil(log_n / t))) if t > 0 else 1
            
            self._bmssp_recursive(l, float('inf'), {S}, k, t)
            
            result = self.dist_hat.get(D, float('inf'))
            return result if result != float('inf') else float('inf')
        
        with self.metrics:
            result = run_alg()

        conn.close()
        return result
    
class Dijkstra(PathFinder):
    # Removed G from parameters, added db_path for flexibility
    def find_shortest_path(self, S, D, db_path="sumatra.db"): 
        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        def run_alg():
            self.metrics.vis_nodes = 0
            
            frontier = []
            distance = {}  # Only store discovered nodes to save RAM
            
            distance[S] = 0
            heapq.heappush(frontier, (0, S))
            
            while frontier:
                current_distance, current_node = heapq.heappop(frontier)
                
                self.metrics.vis_nodes += 1
                
                # Skip if we already found a shorter path to this node
                if current_distance > distance.get(current_node, float('inf')):
                    continue
                    
                # Destination reached
                if current_node == D:
                    return distance[D]
                    
                # --- SQLite Graph Access ---
                # This single query gets all neighbors and automatically picks 
                # the shortest edge if there are multiple connecting the same nodes.
                c.execute("""
                    SELECT target, MIN(length) 
                    FROM edges 
                    WHERE source = ? 
                    GROUP BY target
                """, (current_node,))
                
                neighbors = c.fetchall()
                
                for n, w in neighbors:
                    # Skip if database has null lengths
                    if w is None: 
                        continue
                        
                    w = float(w)
                    new_distance = current_distance + w

                    if new_distance < distance.get(n, float('inf')):
                        distance[n] = new_distance
                        heapq.heappush(frontier, (new_distance, n))
                        
            return float('inf')
        
        with self.metrics:
            result = run_alg()

        conn.close()
        return result