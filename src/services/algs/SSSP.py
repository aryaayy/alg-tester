from src.services.algs.PathFinder import PathFinder
from src.services.algs.Helper import haversine
import heapq
import math

from src.services.algs.PathFinder import PathFinder
from src.services.algs.Helper import haversine
import heapq
import math

class Dijkstra(PathFinder):
    def find_shortest_path(self, G, S, D, is_save_traversal: bool = True):
        visited = []
        came_from = {}

        def run_alg():
            self.metrics.vis_nodes = 0
            
            frontier = []
            distance = {}  
            
            distance[S] = 0
            heapq.heappush(frontier, (0, S))

            while frontier:
                current_distance, current_node = heapq.heappop(frontier)
                
                self.metrics.vis_nodes += 1
                if is_save_traversal: visited.append(current_node)
                
                if current_distance > distance.get(current_node, float('inf')):
                    continue
                    
                if current_node == D:
                    return distance[D]
                    
                for n, w in G.edges.get(current_node, []):
                    new_distance = current_distance + w

                    if new_distance < distance.get(n, float('inf')):
                        distance[n] = new_distance
                        heapq.heappush(frontier, (new_distance, n))
                        if is_save_traversal: came_from[n] = current_node
                        
            return float('inf')
        
        with self.metrics:
            result = run_alg()

        final_path = []
        
        if is_save_traversal and (D in came_from or D == S):
            current = D
            while current != S:
                final_path.append(current)
                current = came_from[current]
            final_path.append(S)
            final_path.reverse() 

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }


class AStar(PathFinder):
    def find_shortest_path(self, G, S, D, is_save_traversal: bool = True):
        visited = []
        came_from = {}

        def run_alg():
            self.metrics.vis_nodes = 0
            
            s_coords = G.coords.get(S)
            d_coords = G.coords.get(D)
            
            if not s_coords or not d_coords:
                return float('inf')
                
            s_y, s_x = s_coords
            d_y, d_x = d_coords
            
            frontier = []
            g_score = {}
            f_score = {}
            
            g_score[S] = 0
            f_score[S] = haversine(s_y, s_x, d_y, d_x)
            
            heapq.heappush(frontier, (f_score[S], S))
            
            while frontier:
                current_f_score, current_node = heapq.heappop(frontier)
                
                self.metrics.vis_nodes += 1
                if is_save_traversal: visited.append(current_node)
                
                if current_f_score > f_score.get(current_node, float('inf')):
                    continue
                    
                if current_node == D:
                    return g_score[D]
                    
                for target_node, w in G.edges.get(current_node, []):
                    new_g_score = g_score[current_node] + w
                    
                    if new_g_score < g_score.get(target_node, float('inf')):
                        g_score[target_node] = new_g_score
                        
                        n_y, n_x = G.coords[target_node]
                        
                        h = haversine(n_y, n_x, d_y, d_x)
                        f_score[target_node] = new_g_score + h
                        
                        heapq.heappush(frontier, (f_score[target_node], target_node))
                        if is_save_traversal: came_from[target_node] = current_node
                        
            return float('inf')
        
        with self.metrics:
            result = run_alg()

        final_path = []
        
        if is_save_traversal and (D in came_from or D == S):
            current = D
            while current != S:
                final_path.append(current)
                current = came_from[current]
            final_path.append(S)
            final_path.reverse() 

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }

class BiDijkstra(PathFinder):
    def find_shortest_path(self, G, S, D, is_save_traversal: bool = True):
        visited = []
        parent_f = {}
        parent_b = {}

        def run_alg():
            shared = None
            self.metrics.vis_nodes = 0
            
            if S == D:
                return (0, S)
                
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
                        if is_save_traversal: visited.append(u)
                        
                        d_u_s = current_dist_f
                        
                        if d_u_s + d_u_t >= mu:
                            return (mu, shared)
                            
                        # Successors (RAM-based)
                        for v, w in G.edges.get(u, []):
                            if v not in closed_f:
                                new_dist = dist_f[u] + w
                                if new_dist < dist_f.get(v, float('inf')):
                                    dist_f[v] = new_dist
                                    heapq.heappush(frontier_f, (new_dist, v))
                                    if is_save_traversal: parent_f[v] = u
                        
                            if v in closed_b:
                                mu = min(mu, dist_f[u] + w + dist_b.get(v, float('inf')))
                                if is_save_traversal: shared = v

                # --- BACKWARD SEARCH ---
                if frontier_b:
                    current_dist_b, u = heapq.heappop(frontier_b)
                    
                    if current_dist_b <= dist_b.get(u, float('inf')):
                        closed_b.add(u)
                        self.metrics.vis_nodes += 1
                        if is_save_traversal: visited.append(u)
                        
                        d_u_t = current_dist_b
                        
                        if d_u_s + d_u_t >= mu:
                            return (mu, shared)
                            
                        # Predecessors (RAM-based menggunakan redges)
                        for v, w in G.redges.get(u, []):
                            if v not in closed_b:
                                new_dist = dist_b[u] + w
                                if new_dist < dist_b.get(v, float('inf')):
                                    dist_b[v] = new_dist
                                    heapq.heappush(frontier_b, (new_dist, v))
                                    if is_save_traversal: parent_b[v] = u
                        
                            if v in closed_f:
                                mu = min(mu, dist_b[u] + w + dist_f.get(v, float('inf')))
                                if is_save_traversal: shared = v

            return (mu, shared) if mu != float('inf') else float('inf')
        
        with self.metrics:
            result, shared = run_alg()

        final_path = []
        temp_final_b = []
        temp_final_f = []
        
        if is_save_traversal and shared:
            if S == D:
                final_path.append(S)
            else:
                current = shared
                while current != D:
                    temp_final_b.append(current)
                    current = parent_b[current]
                
                temp_final_b.append(D)

                current = shared
                while current != S:
                    if temp_final_f != shared:
                        temp_final_f.append(current)
                    current = parent_f[current]
                
                temp_final_f.append(S)
                temp_final_f.reverse()

                final_path = temp_final_f + temp_final_b

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }


class BiAStar(PathFinder):
    def find_shortest_path(self, G, S, D, is_save_traversal: bool = True):
        visited = []
        parent_f = {}
        parent_b = {}

        def run_alg():
            shared = None
            self.metrics.vis_nodes = 0
            
            if S == D:
                return (0, S)
                
            s_coords = G.coords.get(S)
            d_coords = G.coords.get(D)
            
            if not s_coords or not d_coords:
                return (float('inf'), shared)
                
            s_lat, s_lon = s_coords
            t_lat, t_lon = d_coords
            
            L = float('inf')
            
            g_f = {}
            g_f[S] = 0
            frontier_f = []
            h_S_t = haversine(s_lat, s_lon, t_lat, t_lon)
            heapq.heappush(frontier_f, (h_S_t, 0, S, s_lat, s_lon))
            
            g_b = {}
            g_b[D] = 0
            frontier_b = []
            h_T_s = haversine(t_lat, t_lon, s_lat, s_lon)
            heapq.heappush(frontier_b, (h_T_s, 0, D, t_lat, t_lon))

            while frontier_f or frontier_b:
                
                # --- FORWARD SEARCH ---
                if frontier_f:
                    F_b = frontier_b[0][0] if frontier_b else float('inf')
                    f_u, g_u, u, u_lat, u_lon = heapq.heappop(frontier_f)

                    if g_u <= g_f.get(u, float('inf')):
                        self.metrics.vis_nodes += 1
                        if is_save_traversal: visited.append(u)
                        
                        h_u_t = haversine(u_lat, u_lon, t_lat, t_lon) 
                        h_b_u = haversine(u_lat, u_lon, s_lat, s_lon) 
                        
                        if not (g_u + h_u_t >= L or g_u + F_b - h_b_u >= L):
                            for v, w in G.edges.get(u, []):
                                new_g = g_u + w
                                if new_g < g_f.get(v, float('inf')):
                                    g_f[v] = new_g
                                    v_lat, v_lon = G.coords[v]
                                    f_v = new_g + haversine(v_lat, v_lon, t_lat, t_lon)
                                    heapq.heappush(frontier_f, (f_v, new_g, v, v_lat, v_lon))
                                    if is_save_traversal: parent_f[v] = u
                                
                                if g_f.get(v, float('inf')) + g_b.get(v, float('inf')) < L:
                                    L = g_f[v] + g_b[v]
                                    if is_save_traversal: shared = v

                # --- BACKWARD SEARCH ---
                if frontier_b:
                    F_f = frontier_f[0][0] if frontier_f else float('inf')
                    f_u, g_u, u, u_lat, u_lon = heapq.heappop(frontier_b)
                    
                    if g_u <= g_b.get(u, float('inf')):
                        self.metrics.vis_nodes += 1
                        if is_save_traversal: visited.append(u)
                        
                        h_u_s = haversine(u_lat, u_lon, s_lat, s_lon) 
                        h_f_u = haversine(u_lat, u_lon, t_lat, t_lon) 
                        
                        if not (g_u + h_u_s >= L or g_u + F_f - h_f_u >= L):
                            for v, w in G.redges.get(u, []):
                                new_g = g_u + w
                                if new_g < g_b.get(v, float('inf')):
                                    g_b[v] = new_g
                                    v_lat, v_lon = G.coords[v]
                                    f_v = new_g + haversine(v_lat, v_lon, s_lat, s_lon)
                                    heapq.heappush(frontier_b, (f_v, new_g, v, v_lat, v_lon))
                                    if is_save_traversal: parent_b[v] = u
                                    
                                if g_f.get(v, float('inf')) + g_b.get(v, float('inf')) < L:
                                    L = g_f[v] + g_b[v]
                                    if is_save_traversal: shared = v

            return (L, shared) if L != float('inf') else float('inf')
        
        with self.metrics:
            result, shared = run_alg()

        final_path = []
        temp_final_b = []
        temp_final_f = []
        
        if is_save_traversal and shared:
            if S == D:
                final_path.append(S)
            else:
                current = shared
                while current != D:
                    temp_final_b.append(current)
                    current = parent_b[current]
                
                temp_final_b.append(D)

                current = shared
                while current != S:
                    if temp_final_f != shared:
                        temp_final_f.append(current)
                    current = parent_f[current]
                
                temp_final_f.append(S)
                temp_final_f.reverse()

                final_path = temp_final_f + temp_final_b

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }


class BMSSP(PathFinder):
    def find_shortest_path(self, G, S, D, is_save_traversal: bool = True):
        dist_hat = {}
        came_from = {}
        traversal = []
        
        best_goal_dist = float('inf')
        bucket_queue = BucketQueue(10.0)
        
        # O(1) RAM-based Degree Fetcher
        def _get_degree(node):
            return len(G.edges.get(node, []))

        def _dijkstra_delta_stepping(S_set, bound, delta):
            nonlocal best_goal_dist
            pq = bucket_queue
            pq.clear()
            pq.delta = max(0.001, delta)
            
            local_visited = set()
            
            for v in S_set:
                dist_v = dist_hat.get(v, float('inf'))
                if dist_v < bound:
                    pq.insert(v, dist_v)
                    
            while True:
                u, ok = pq.extract_min()
                if not ok: break
                
                if u in local_visited:
                    continue
                local_visited.add(u)
                
                dist_u = dist_hat.get(u, float('inf'))
                if dist_u >= bound:
                    continue
                    
                if u == D:
                    if dist_u < best_goal_dist:
                        best_goal_dist = dist_u
                    return
                    
                self.metrics.vis_nodes += 1
                if is_save_traversal: traversal.append(u)
                
                # RAM-based Successors
                for v, w_uv in G.edges.get(u, []):
                    new_dist = dist_u + w_uv
                    
                    if new_dist < dist_hat.get(v, float('inf')) and new_dist < bound and new_dist < best_goal_dist:
                        dist_hat[v] = new_dist
                        came_from[v] = u
                        pq.insert(v, new_dist)
                        
        def _smart_pivot_selection(nodes_list):
            num_nodes = len(nodes_list)
            if num_nodes <= 5:
                return nodes_list[num_nodes // 2]
                
            sample_indices = [0, num_nodes // 4, num_nodes // 2, num_nodes * 3 // 4, num_nodes - 1]
            samples = [nodes_list[i] for i in sample_indices]
            
            scored_samples = []
            for node in samples:
                dist = dist_hat.get(node, float('inf'))
                degree = _get_degree(node)
                score = dist * (degree + 1)
                scored_samples.append((score, node))
                
            scored_samples.sort(key=lambda x: x[0])
            return scored_samples[len(scored_samples) // 2][1]

        def _bmssp(bound, S_set):
            nonlocal best_goal_dist
            if not S_set:
                return
                
            if dist_hat.get(D, float('inf')) < bound:
                best_goal_dist = min(best_goal_dist, dist_hat.get(D))
                S_set = {v for v in S_set if dist_hat.get(v, float('inf')) < best_goal_dist}
                if not S_set:
                    return
                    
            if len(S_set) <= 2 or bound <= 10.0:
                _dijkstra_delta_stepping(S_set, bound, 10.0)
                return
                
            S_list = list(S_set)
            pivot = _smart_pivot_selection(S_list)
            pivot_dist = dist_hat.get(pivot, float('inf'))
            
            new_bound = pivot_dist + 1e-5
            
            if new_bound >= bound:
                _dijkstra_delta_stepping(S_set, bound, 10.0)
                return
                
            _dijkstra_delta_stepping(S_set, new_bound, 5.0)
            
            left = {v for v in S_list if dist_hat.get(v, float('inf')) < new_bound}
            right = {v for v in S_list if new_bound <= dist_hat.get(v, float('inf')) < bound}
            
            if len(left) < len(right):
                _bmssp(new_bound, left)
                _bmssp(bound, right)
            else:
                _bmssp(bound, right)
                _bmssp(new_bound, left)
                
        def run_alg():
            nonlocal best_goal_dist
            self.metrics.vis_nodes = 0
            dist_hat[S] = 0.0
            best_goal_dist = float('inf')
            
            _bmssp(float('inf'), {S})
            
            return dist_hat.get(D, float('inf'))
            
        with self.metrics:
            result = run_alg()
            
        final_path = []
        if D in came_from or D == S:
            curr = D
            visited_path = set()
            while curr is not None and curr not in visited_path:
                final_path.append(curr)
                visited_path.add(curr)
                if curr == S: break
                curr = came_from.get(curr)
                
            if not final_path or final_path[-1] != S:
                final_path = []
            else:
                final_path.reverse()
                
        return {
            "distance": result,
            "visited": traversal if is_save_traversal else [],
            "final_path": final_path
        }

class DijkstraSQLite(PathFinder):
    # Removed G from parameters, added db_path for flexibility
    def find_shortest_path(self, S, D, is_save_traversal: bool = True):
        visited = []
        came_from = {}

        def run_alg():
            self.metrics.vis_nodes = 0
            
            frontier = []
            distance = {}  # Only store discovered nodes to save RAM
            
            distance[S] = 0
            heapq.heappush(frontier, (0, S))

            while frontier:
                current_distance, current_node = heapq.heappop(frontier)
                
                self.metrics.vis_nodes += 1
                if is_save_traversal: visited.append(current_node)
                
                # Skip if we already found a shorter path to this node
                if current_distance > distance.get(current_node, float('inf')):
                    continue
                    
                # Destination reached
                if current_node == D:
                    return distance[D]
                    
                # --- SQLite Graph Access ---
                # This single query gets all neighbors and automatically picks 
                # the shortest edge if there are multiple connecting the same nodes.
                for n, w in self.G.successors(current_node):
                    # Skip if database has null lengths
                    if w is None: 
                        continue
                        
                    w = float(w)
                    new_distance = current_distance + w

                    if new_distance < distance.get(n, float('inf')):
                        distance[n] = new_distance
                        heapq.heappush(frontier, (new_distance, n))
                        if is_save_traversal: came_from[n] = current_node
                        
            return float('inf')
        
        with self.metrics:
            result = run_alg()

        final_path = []
        
        # Check if we actually found a way to the destination
        if is_save_traversal and (D in came_from or D == S):
            current = D
            # Work backwards from the destination to the start
            while current != S:
                final_path.append(current)
                current = came_from[current]
            
            # Don't forget to add the start node!
            final_path.append(S)
            
            # Reverse it so it goes Source -> Destination
            final_path.reverse() 

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }
    
class AStarSQLite(PathFinder):
    def find_shortest_path(self, S, D, is_save_traversal: bool = True):
        visited = []
        came_from = {}

        def run_alg():
            self.metrics.vis_nodes = 0
            
            # 1. Fetch Coordinates for Source and Destination upfront
            s_coords = self.G.coords(S)
            d_coords = self.G.coords(D)
            
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
                if is_save_traversal: visited.append(current_node)
                
                if current_f_score > f_score.get(current_node, float('inf')):
                    continue
                    
                if current_node == D:
                    return g_score[D]
                    
                # 2. Query neighbors, shortest edge, AND neighbor coordinates at the same time
                for target_node, w, n_y, n_x in self.G.successors_with_coords(current_node):
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
                        if is_save_traversal: came_from[target_node] = current_node
                        
            return float('inf')
        
        with self.metrics:
            result = run_alg()

        final_path = []
        
        # Check if we actually found a way to the destination
        if is_save_traversal and (D in came_from or D == S):
            current = D
            # Work backwards from the destination to the start
            while current != S:
                final_path.append(current)
                current = came_from[current]
            
            # Don't forget to add the start node!
            final_path.append(S)
            
            # Reverse it so it goes Source -> Destination
            final_path.reverse() 

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }

class BiAStarSQLite(PathFinder):
    def find_shortest_path(self, S, D, is_save_traversal: bool = True):
        visited = []
        parent_f = {}
        parent_b = {}

        def run_alg():
            shared = None
            self.metrics.vis_nodes = 0
            
            if S == D:
                return (0, S)
                
            # 1. Fetch Source and Destination coordinates upfront
            s_coords = self.G.coords(S)
            d_coords = self.G.coords(D)
            
            if not s_coords or not d_coords:
                return (float('inf'), shared)
                
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
                        if is_save_traversal: visited.append(u)
                        
                        h_u_t = haversine(u_lat, u_lon, t_lat, t_lon) # h(u)
                        h_b_u = haversine(u_lat, u_lon, s_lat, s_lon) # h~(u)
                        
                        if not (g_u + h_u_t >= L or g_u + F_b - h_b_u >= L):
                            
                            # Successors (Where 'u' is source) JOINED with nodes to get coords
                            for v, w, v_lat, v_lon in self.G.successors_with_coords(u):
                                if w is None: continue
                                w = float(w)
                                
                                new_g = g_u + w
                                if new_g < g_f.get(v, float('inf')):
                                    g_f[v] = new_g
                                    f_v = new_g + haversine(v_lat, v_lon, t_lat, t_lon)
                                    heapq.heappush(frontier_f, (f_v, new_g, v, v_lat, v_lon))
                                    if is_save_traversal: parent_f[v] = u
                                
                                if g_f.get(v, float('inf')) + g_b.get(v, float('inf')) < L:
                                    L = g_f[v] + g_b[v]
                                    if is_save_traversal: shared = v

                # --- BACKWARD SEARCH ---
                if frontier_b:
                    F_f = frontier_f[0][0] if frontier_f else float('inf')
                    
                    f_u, g_u, u, u_lat, u_lon = heapq.heappop(frontier_b)
                    
                    if g_u <= g_b.get(u, float('inf')):
                        self.metrics.vis_nodes += 1
                        if is_save_traversal: visited.append(u)
                        
                        h_u_s = haversine(u_lat, u_lon, s_lat, s_lon) # h~(u)
                        h_f_u = haversine(u_lat, u_lon, t_lat, t_lon) # h(u)
                        
                        if not (g_u + h_u_s >= L or g_u + F_f - h_f_u >= L):
                            
                            # Predecessors (Where 'u' is target) JOINED with nodes to get coords
                            for v, w, v_lat, v_lon in self.G.predecessors_with_coords(u):
                                if w is None: continue
                                w = float(w)
                                
                                new_g = g_u + w
                                if new_g < g_b.get(v, float('inf')):
                                    g_b[v] = new_g
                                    f_v = new_g + haversine(v_lat, v_lon, s_lat, s_lon)
                                    heapq.heappush(frontier_b, (f_v, new_g, v, v_lat, v_lon))
                                    if is_save_traversal: parent_b[v] = u
                                    
                                if g_f.get(v, float('inf')) + g_b.get(v, float('inf')) < L:
                                    L = g_f[v] + g_b[v]
                                    if is_save_traversal: shared = v

            return (L, shared) if L != float('inf') else float('inf')
        
        with self.metrics:
            result, shared = run_alg()

        final_path = []
        temp_final_b = []
        temp_final_f = []
        
        # Check if we actually found a way to the destination
        if is_save_traversal and shared:
            if S == D:
                final_path.append(S)
            else:
                current = shared
                # Work backwards from the destination to the start
                while current != D:
                    temp_final_b.append(current)
                    current = parent_b[current]
                
                # Don't forget to add the start node!
                temp_final_b.append(D)

                current = shared
                # Work backwards from the destination to the start
                while current != S:
                    if temp_final_f != shared:
                        temp_final_f.append(current)
                    current = parent_f[current]
                
                # Don't forget to add the start node!
                temp_final_f.append(S)
                temp_final_f.reverse()

                final_path = temp_final_f + temp_final_b

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }
    
class BiDijkstraSQLite(PathFinder):
    def find_shortest_path(self, S, D, is_save_traversal: bool = True):
        visited = []
        parent_f = {}
        parent_b = {}

        def run_alg():
            shared = None
            self.metrics.vis_nodes = 0
            
            if S == D:
                return (0, S)
                
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
                        if is_save_traversal: visited.append(u)
                        
                        d_u_s = current_dist_f
                        
                        if d_u_s + d_u_t >= mu:
                            return (mu, shared)
                            
                        # Successors: Where 'u' is the source
                        for v, w in self.G.successors(u):
                            if w is None:
                                continue
                            w = float(w)
                            
                            if v not in closed_f:
                                new_dist = dist_f[u] + w
                                if new_dist < dist_f.get(v, float('inf')):
                                    dist_f[v] = new_dist
                                    heapq.heappush(frontier_f, (new_dist, v))
                                    if is_save_traversal: parent_f[v] = u
                        
                            if v in closed_b:
                                mu = min(mu, dist_f[u] + w + dist_b.get(v, float('inf')))
                                if is_save_traversal: shared = v

                # --- BACKWARD SEARCH ---
                if frontier_b:
                    current_dist_b, u = heapq.heappop(frontier_b)
                    
                    if current_dist_b <= dist_b.get(u, float('inf')):
                        closed_b.add(u)
                        self.metrics.vis_nodes += 1
                        if is_save_traversal: visited.append(u)
                        
                        d_u_t = current_dist_b
                        
                        if d_u_s + d_u_t >= mu:
                            return (mu, shared)
                            
                        # Predecessors: Where 'u' is the target
                        for v, w in self.G.predecessors(u):
                            if w is None:
                                continue
                            w = float(w)
                            
                            if v not in closed_b:
                                new_dist = dist_b[u] + w
                                if new_dist < dist_b.get(v, float('inf')):
                                    dist_b[v] = new_dist
                                    heapq.heappush(frontier_b, (new_dist, v))
                                    if is_save_traversal: parent_b[v] = u
                        
                            if v in closed_f:
                                mu = min(mu, dist_b[u] + w + dist_f.get(v, float('inf')))
                                if is_save_traversal: shared = v

            return (mu, shared) if mu != float('inf') else float('inf')
        
        with self.metrics:
            result, shared = run_alg()

        final_path = []
        temp_final_b = []
        temp_final_f = []
        
        # Check if we actually found a way to the destination
        if is_save_traversal and shared:
            if S == D:
                final_path.append(S)
            else:
                current = shared
                # Work backwards from the destination to the start
                while current != D:
                    temp_final_b.append(current)
                    current = parent_b[current]
                
                # Don't forget to add the start node!
                temp_final_b.append(D)

                current = shared
                # Work backwards from the destination to the start
                while current != S:
                    if temp_final_f != shared:
                        temp_final_f.append(current)
                    current = parent_f[current]
                
                # Don't forget to add the start node!
                temp_final_f.append(S)
                temp_final_f.reverse()

                final_path = temp_final_f + temp_final_b

        return {
            "distance": result,
            "visited": visited,
            "final_path": final_path
        }

import math
from collections import deque

class BucketQueue:
    def __init__(self, delta: float, initial_buckets=64):
        self.delta = max(0.001, delta)
        self.min_idx = 0
        self.buckets = [deque() for _ in range(initial_buckets)]
        self.max_idx = -1

    def clear(self):
        for i in range(self.min_idx, self.max_idx + 1):
            if i < len(self.buckets):
                self.buckets[i].clear()
        self.min_idx = 0
        self.max_idx = -1

    def insert(self, v: int, dist: float):
        idx = int(dist / self.delta)
        if idx >= len(self.buckets):
            num_new_buckets = idx - len(self.buckets) + 1
            self.buckets.extend(deque() for _ in range(num_new_buckets))
        self.buckets[idx].append(v)
        if idx > self.max_idx:
            self.max_idx = idx

    def extract_min(self):
        min_idx = self.min_idx
        while min_idx <= self.max_idx:
            if min_idx < len(self.buckets) and self.buckets[min_idx]:
                self.min_idx = min_idx
                v = self.buckets[min_idx].popleft()
                return v, True
            min_idx += 1
        self.min_idx = min_idx
        return None, False


class BMSSPSQLite(PathFinder):
    def find_shortest_path(self, S, D, is_save_traversal: bool = True):
        dist_hat = {}
        came_from = {}
        traversal = []
        
        best_goal_dist = float('inf')
        bucket_queue = BucketQueue(10.0)
        
        # Helper untuk mendapatkan derajat (jumlah tetangga) dari SQLite
        def _get_degree(node):
            count = 0
            for _ in self.G.successors(node):
                count += 1
            return count

        # Terjemahan _dijkstra_delta_stepping milik Bzantium
        def _dijkstra_delta_stepping(S_set, bound, delta):
            nonlocal best_goal_dist
            pq = bucket_queue
            pq.clear()
            pq.delta = max(0.001, delta)
            
            local_visited = set()
            
            for v in S_set:
                dist_v = dist_hat.get(v, float('inf'))
                if dist_v < bound:
                    pq.insert(v, dist_v)
                    
            while True:
                u, ok = pq.extract_min()
                if not ok: break
                
                if u in local_visited:
                    continue
                local_visited.add(u)
                
                dist_u = dist_hat.get(u, float('inf'))
                if dist_u >= bound:
                    continue
                    
                if u == D:
                    if dist_u < best_goal_dist:
                        best_goal_dist = dist_u
                    return
                    
                self.metrics.vis_nodes += 1
                if is_save_traversal: traversal.append(u)
                
                for v, w_uv in self.G.successors(u):
                    if w_uv is None: continue
                    new_dist = dist_u + float(w_uv)
                    
                    # 3 Lapisan Pruning Agresif Bzantium
                    if new_dist < dist_hat.get(v, float('inf')) and new_dist < bound and new_dist < best_goal_dist:
                        dist_hat[v] = new_dist
                        came_from[v] = u
                        pq.insert(v, new_dist)
                        
        # Terjemahan _smart_pivot_selection milik Bzantium
        def _smart_pivot_selection(nodes_list):
            num_nodes = len(nodes_list)
            if num_nodes <= 5:
                return nodes_list[num_nodes // 2]
                
            sample_indices = [0, num_nodes // 4, num_nodes // 2, num_nodes * 3 // 4, num_nodes - 1]
            samples = [nodes_list[i] for i in sample_indices]
            
            scored_samples = []
            for node in samples:
                dist = dist_hat.get(node, float('inf'))
                degree = _get_degree(node)
                score = dist * (degree + 1)
                scored_samples.append((score, node))
                
            scored_samples.sort(key=lambda x: x[0])
            return scored_samples[len(scored_samples) // 2][1]

        # Terjemahan Sederhana Divide and Conquer milik Bzantium
        def _bmssp(bound, S_set):
            nonlocal best_goal_dist
            if not S_set:
                return
                
            if dist_hat.get(D, float('inf')) < bound:
                best_goal_dist = min(best_goal_dist, dist_hat.get(D))
                S_set = {v for v in S_set if dist_hat.get(v, float('inf')) < best_goal_dist}
                if not S_set:
                    return
                    
            if len(S_set) <= 2 or bound <= 10.0:
                _dijkstra_delta_stepping(S_set, bound, 10.0)
                return
                
            S_list = list(S_set)
            pivot = _smart_pivot_selection(S_list)
            pivot_dist = dist_hat.get(pivot, float('inf'))
            
            new_bound = pivot_dist + 1e-5
            
            if new_bound >= bound:
                _dijkstra_delta_stepping(S_set, bound, 10.0)
                return
                
            _dijkstra_delta_stepping(S_set, new_bound, 5.0)
            
            left = {v for v in S_list if dist_hat.get(v, float('inf')) < new_bound}
            right = {v for v in S_list if new_bound <= dist_hat.get(v, float('inf')) < bound}
            
            # Eksekusi partisi yang lebih kecil terlebih dahulu untuk memori yang lebih efisien (Cache Locality)
            if len(left) < len(right):
                _bmssp(new_bound, left)
                _bmssp(bound, right)
            else:
                _bmssp(bound, right)
                _bmssp(new_bound, left)
                
        def run_alg():
            nonlocal best_goal_dist
            self.metrics.vis_nodes = 0
            dist_hat[S] = 0.0
            best_goal_dist = float('inf')
            
            _bmssp(float('inf'), {S})
            
            return dist_hat.get(D, float('inf'))
            
        with self.metrics:
            result = run_alg()
            
        final_path = []
        if D in came_from or D == S:
            curr = D
            visited_path = set()
            while curr is not None and curr not in visited_path:
                final_path.append(curr)
                visited_path.add(curr)
                if curr == S: break
                curr = came_from.get(curr)
                
            if not final_path or final_path[-1] != S:
                final_path = []
            else:
                final_path.reverse()
                
        return {
            "distance": result,
            "visited": traversal if is_save_traversal else [],
            "final_path": final_path
        }
    
import math
import heapq
from collections import deque

# 1. Struktur Data V1: EfficientDataStructure (dari data_structure.py)
class EfficientDataStructure:
    def __init__(self, block_size: int, bound: float):
        self.batch_blocks = deque()
        self.sorted_blocks = []
        self.block_size = block_size
        self.bound = bound

    def insert(self, vertex: int, distance: float):
        if distance < self.bound:
            if not self.sorted_blocks or len(self.sorted_blocks[-1]) >= self.block_size:
                self.sorted_blocks.append([])
            self.sorted_blocks[-1].append((vertex, distance))

    def batch_prepend(self, items: list):
        if items:
            self.batch_blocks.appendleft(list(items))

    def pull(self):
        block_to_process = None
        
        if self.batch_blocks:
            block_to_process = self.batch_blocks.popleft()
        elif self.sorted_blocks:
            min_dist_in_blocks = [
                min(distance for _, distance in block) if block else float('inf') 
                for block in self.sorted_blocks
            ]
            min_block_idx = min(range(len(min_dist_in_blocks)), key=min_dist_in_blocks.__getitem__)
            block_to_process = self.sorted_blocks.pop(min_block_idx)

        if block_to_process:
            block_to_process.sort(key=lambda vertex_dist_pair: vertex_dist_pair[1])
            vertices = [vertex for vertex, distance in block_to_process]
            next_bound = self.peek_min()
            return next_bound, vertices

        return self.bound, []

    def peek_min(self) -> float:
        min_val = self.bound
        all_blocks = list(self.batch_blocks) + self.sorted_blocks
        for block in all_blocks:
            if block:
                block_min = min(distance for vertex, distance in block)
                min_val = min(min_val, block_min)
        return min_val

    def is_empty(self) -> bool:
        return not any(self.batch_blocks) and not any(self.sorted_blocks)


# 2. Solver V1: Arsitektur Rekursi Multi-Level (dari bmssp_solver.py)
class BMSSP_V1(PathFinder):
    def find_shortest_path(self, S, D, is_save_traversal: bool = True):
        dist_hat = {}
        came_from = {}
        traversal = []
        complete = set() 
        
        dist_hat[S] = 0.0
        best_goal = float('inf')

        n = self.G.nodes_count()
        if n < 2: n = 2
        
        k = int(math.log2(n)**(1/3) * 2) if n > 1 else 1
        t = int(math.log2(n)**(2/3)) if n > 1 else 1
        k = max(k, 3)
        t = max(t, 2)
        
        max_level = math.ceil(math.log2(n) / t) if n > 1 else 0

        def _base_case(bound: float, frontier: list) -> list:
            nonlocal best_goal
            pq = []
            for start_node in frontier:
                if start_node not in complete and dist_hat.get(start_node, float('inf')) < bound:
                    heapq.heappush(pq, (dist_hat[start_node], start_node))

            completed_nodes = []

            while pq:
                dist, u = heapq.heappop(pq)

                if u in complete or dist > dist_hat.get(u, float('inf')):
                    continue

                complete.add(u)
                completed_nodes.append(u)
                
                self.metrics.vis_nodes += 1
                if is_save_traversal: traversal.append(u)

                if u == D:
                    if dist < best_goal: best_goal = dist
                    break

                for v, w_uv in self.G.successors(u):
                    if w_uv is None: continue
                    new_dist = dist + float(w_uv)

                    if v in complete: continue
                    
                    curr_dist = dist_hat.get(v, float('inf'))
                    
                    # LOGIKA JANGKAR: Menyelamatkan aliran dari _find_pivots
                    if new_dist <= curr_dist and new_dist < bound and new_dist < best_goal:
                        if new_dist < curr_dist:
                            dist_hat[v] = new_dist
                            came_from[v] = u
                            heapq.heappush(pq, (new_dist, v))
                        elif came_from.get(v) == u:
                            heapq.heappush(pq, (new_dist, v))

            return completed_nodes

        def _find_pivots(bound: float, frontier: list):
            nonlocal best_goal
            working_set = set(frontier)
            current_layer = {node for node in frontier if node not in complete}

            for _ in range(k):
                next_layer = set()
                for u in current_layer:
                    if dist_hat.get(u, float('inf')) >= bound:
                        continue
                        
                    self.metrics.vis_nodes += 1

                    for v, w_uv in self.G.successors(u):
                        if w_uv is None or v in complete: continue
                        new_dist = dist_hat.get(u, float('inf')) + float(w_uv)
                        curr_dist = dist_hat.get(v, float('inf'))

                        # LOGIKA JANGKAR: Mengamankan relaksasi awal
                        if new_dist <= curr_dist and new_dist < bound and new_dist < best_goal:
                            if new_dist < curr_dist:
                                dist_hat[v] = new_dist
                                came_from[v] = u
                                if v not in working_set:
                                    next_layer.add(v)
                            elif came_from.get(v) == u:
                                if v not in working_set:
                                    next_layer.add(v)

                if not next_layer:
                    break

                working_set.update(next_layer)
                current_layer = next_layer

                if len(working_set) > k * len(frontier):
                    return frontier, list(working_set)

            children = {node: [] for node in working_set}
            for node in working_set:
                pred = came_from.get(node)
                if pred is not None and pred in working_set:
                    children.setdefault(pred, []).append(node)

            subtree_sizes = {node: len(ch) for node, ch in children.items()}
            pivots = [root for root in frontier if subtree_sizes.get(root, 0) >= k]

            if not pivots:
                return frontier, list(working_set)

            return pivots, list(working_set)

        def _edge_relaxation(completed_vertices: list, lower_bound: float, upper_bound: float, ds: EfficientDataStructure):
            nonlocal best_goal
            batch_prepend_list = []

            for u in completed_vertices:
                for v, w_uv in self.G.successors(u):
                    if w_uv is None or v in complete: continue
                    new_dist = dist_hat.get(u, float('inf')) + float(w_uv)
                    curr_dist = dist_hat.get(v, float('inf'))

                    # LOGIKA JANGKAR: Merambatkan antrean tanpa terputus
                    if new_dist <= curr_dist and new_dist < best_goal:
                        if new_dist < curr_dist:
                            dist_hat[v] = new_dist
                            came_from[v] = u
                            if new_dist < lower_bound:
                                batch_prepend_list.append((v, new_dist))
                            elif new_dist < upper_bound:
                                ds.insert(v, new_dist)
                        elif came_from.get(v) == u:
                            if new_dist < lower_bound:
                                batch_prepend_list.append((v, new_dist))
                            elif new_dist < upper_bound:
                                ds.insert(v, new_dist)

            if batch_prepend_list:
                ds.batch_prepend(batch_prepend_list)

        def _bmssp_recursive(level: int, bound: float, pivots: list):
            nonlocal best_goal
            
            if not pivots or (D in complete):
                return []

            if level == 0:
                return _base_case(bound, pivots)

            pivots, _ = _find_pivots(bound, pivots)

            block_size = 2**max(0, (level - 1) * t)
            ds = EfficientDataStructure(block_size, bound)

            for pivot in pivots:
                if pivot not in complete and dist_hat.get(pivot, float('inf')) < bound:
                    ds.insert(pivot, dist_hat.get(pivot))

            result_set = []

            while not ds.is_empty():
                if D in complete:
                    break

                subset_bound, subset = ds.pull()
                if not subset:
                    continue

                sub_result = _bmssp_recursive(level - 1, subset_bound, subset)
                result_set.extend(sub_result)

                _edge_relaxation(sub_result, subset_bound, bound, ds)

            return result_set

        def run_alg():
            self.metrics.vis_nodes = 0
            _bmssp_recursive(max_level, float('inf'), [S])
            return dist_hat.get(D, float('inf'))
            
        with self.metrics:
            result = run_alg()
            
        final_path = []
        if D in came_from or D == S:
            curr = D
            visited_path = set()
            while curr is not None and curr not in visited_path:
                final_path.append(curr)
                visited_path.add(curr)
                if curr == S: break
                curr = came_from.get(curr)
                
            if not final_path or final_path[-1] != S:
                final_path = []
            else:
                final_path.reverse()
                
        return {
            "distance": result,
            "visited": traversal if is_save_traversal else [],
            "final_path": final_path
        }
    
# class BMSSPDS:
#     def __init__(self, M, B):
#         self.M = max(1, M)
#         self.B = B
#         self.heap = []
    
#     def insert(self, item):
#         heapq.heappush(self.heap, item)

#     def pull(self, dist_hat):
#         if not self.heap:
#             return self.B, set()
        
#         Si = set()
#         while self.heap and len(Si) < self.M:
#             dist, node = heapq.heappop(self.heap)
            
#             # CEK LAZY DELETION: Abaikan jika ini adalah riwayat jarak yang sudah usang!
#             if dist > dist_hat.get(node, float('inf')):
#                 continue
                
#             if node not in Si:
#                 Si.add(node)
                
#         # Bersihkan sisa elemen usang di pucuk antrean agar batas Bi akurat!
#         while self.heap:
#             top_dist, top_node = self.heap[0]
#             if top_dist > dist_hat.get(top_node, float('inf')) or top_node in Si:
#                 heapq.heappop(self.heap)
#             else:
#                 break

#         Bi = self.heap[0][0] if self.heap else self.B
#         return Bi, Si

#     def batch_prepend(self, item_set):
#         for item in item_set:
#             self.insert(item)
    
#     def is_empty(self):
#         return len(self.heap) == 0


# class BMSSP(PathFinder):
#     def __init__(self):
#         super().__init__()
#         self.dist_hat = {}
#         self.c = None  # We will store the DB cursor here for recursive access
#         self.visited = []
#         self.came_from = {}

#     def _find_pivots(self, B, S, k):
#         W = set(S)
#         W_prev = set(S)
        
#         for i in range(1, k + 1):
#             W_curr = set()
#             for u in W_prev:
#                 # self.visited.append(u)
#                 self.metrics.vis_nodes += 1
#                 # print(u)
                
#                 # SQLite Successors
#                 self.c.execute("""
#                     SELECT target, MIN(length) 
#                     FROM edges 
#                     WHERE source = ? 
#                     GROUP BY target
#                 """, (u,))
                
#                 for v, w_uv in self.c.fetchall():
#                     if w_uv is None: continue
#                     w_uv = float(w_uv)
                    
#                     dist_u = self.dist_hat.get(u, float('inf'))
#                     dist_v = self.dist_hat.get(v, float('inf'))
                    
#                     if dist_u + w_uv <= dist_v:
#                         self.dist_hat[v] = dist_u + w_uv
#                         if dist_u + w_uv < B:
#                             W_curr.add(v)
#                             # self.came_from[v] = u
            
#             W.update(W_curr)
#             W_prev = W_curr
            
#             if len(W) > k * len(S):
#                 return set(S), W
                
#         P = set(S) 
#         return P, W

#     def _base_case(self, B, S, k):
#         if not S:
#             return B, set()
            
#         # x = list(S)[0]
#         U0 = set()
#         H = []
#         for x in S:
#             heapq.heappush(H, (self.dist_hat.get(x, float('inf')), x))
        
#         while H and len(U0) < k + 1:
#             d_u, u = heapq.heappop(H)
            
#             if d_u > self.dist_hat.get(u, float('inf')):
#                 continue
                
#             U0.add(u)
#             # self.visited.append(u)
#             self.metrics.vis_nodes += 1
            
#             self.c.execute("""
#                 SELECT target, MIN(length) 
#                 FROM edges 
#                 WHERE source = ? 
#                 GROUP BY target
#             """, (u,))
            
#             for v, w_uv in self.c.fetchall():
#                 if w_uv is None: continue
#                 w_uv = float(w_uv)
                
#                 new_dist = self.dist_hat.get(u, float('inf')) + w_uv
                
#                 if new_dist < self.dist_hat.get(v, float('inf')) and new_dist < B:
#                     self.dist_hat[v] = new_dist
#                     heapq.heappush(H, (new_dist, v))
#                     # self.came_from[v] = u
                    
#         if len(U0) <= k:
#             return B, U0
#         else:
#             B_prime = max([self.dist_hat.get(v, float('inf')) for v in U0]) if U0 else B
#             U_return = {v for v in U0 if self.dist_hat.get(v, float('inf')) < B_prime}
#             return B_prime, U_return

#     def _bmssp_recursive(self, l, B, S, k, t):
#         if l == 0:
#             return self._base_case(B, S, k)
            
#         P, W = self._find_pivots(B, S, k)
        
#         M = max(1, int(2 ** ((l - 1) * t)))
#         D = BMSSPDS(M, B)
        
#         for x in P:
#             D.insert((self.dist_hat.get(x, float('inf')), x))
            
#         current_B_prime = min([self.dist_hat.get(x, float('inf')) for x in P]) if P else B
#         U = set()
        
#         max_u_size = k * (2 ** (l * t))
#         prev_u_size = len(U)
        
#         while len(U) < max_u_size and not D.is_empty():
#             Bi, Si = D.pull(self.dist_hat)
            
#             if self.best_distance_to_dest != float('inf') and Bi >= self.best_distance_to_dest: 
#                 break

#             Bi_prime, Ui = self._bmssp_recursive(l - 1, Bi, Si, k, t)
#             current_B_prime = Bi_prime  
#             U.update(Ui)
            
#             K_set = set()
#             for u in Ui:
#                 # self.visited.append(u)
#                 self.metrics.vis_nodes += 1
#                 # print(u)
                
#                 # SQLite Successors
#                 self.c.execute("""
#                     SELECT target, MIN(length) 
#                     FROM edges 
#                     WHERE source = ? 
#                     GROUP BY target
#                 """, (u,))
                
#                 for v, w_uv in self.c.fetchall():
#                     if w_uv is None: continue
#                     w_uv = float(w_uv)
                    
#                     new_dist = self.dist_hat.get(u, float('inf')) + w_uv

#                     # --- THE PRUNING CONDITION ---
#                     if self.best_distance_to_dest != float('inf') and new_dist >= self.best_distance_to_dest:
#                         continue # Skip this branch, it's already too long!

#                     if new_dist < self.dist_hat.get(v, float('inf')):
#                         self.dist_hat[v] = new_dist

#                         # --- UPDATE THE GLOBAL BOUND IF WE HIT DESTINATION ---
#                         if v == self.target_node:
#                             self.best_distance_to_dest = new_dist
                        
#                         if Bi <= new_dist < B:
#                             D.insert((new_dist, v))
#                         elif Bi_prime <= new_dist < Bi:
#                             K_set.add((new_dist, v))

#                         # self.came_from[v] = u
                            
#             batch_items = K_set.union({(self.dist_hat.get(x, float('inf')), x) for x in Si if Bi_prime <= self.dist_hat.get(x, float('inf')) < Bi})
#             D.batch_prepend(batch_items)

#             # if len(U) == prev_u_size and not batch_items:
#             #     break
#             prev_u_size = len(U)
            
#         final_B_prime = min(current_B_prime, B)
#         U.update({x for x in W if self.dist_hat.get(x, float('inf')) < final_B_prime})
        
#         return final_B_prime, U

#     def find_shortest_path(self, S, D, is_save_traversal: bool = True):
#         conn = sqlite3.connect(db_path)
#         self.c = conn.cursor()

#         def run_alg():
#             self.metrics.vis_nodes = 0
            
#             self.dist_hat = {} 
#             self.dist_hat[S] = 0

#             # --- NEW: INITIALIZE THE EARLY STOPPING VARIABLES HERE ---
#             self.target_node = D 
#             self.best_distance_to_dest = float('inf') # Starts at infinity!
            
#             # Fetch the total number of nodes in the graph to calculate 'k' and 't' bounds
#             self.c.execute("SELECT COUNT(*) FROM nodes")
#             V = self.c.fetchone()[0]
            
#             log_n = math.log2(V) if V > 1 else 1
            
#             k = max(1, int(math.floor(log_n ** (1/3))))
#             t = max(1, int(math.floor(log_n ** (2/3))))
#             l = max(1, int(math.ceil(log_n / t))) if t > 0 else 1
            
#             self._bmssp_recursive(l, float('inf'), {S}, k, t)
            
#             result = self.dist_hat.get(D, float('inf'))
#             return result if result != float('inf') else float('inf')
        
#         with self.metrics:
#             result = run_alg()

#         conn.close()
#         final_path = []
        
#         # Check if we actually found a way to the destination
#         if D in self.came_from or D == S:
#             current = D
#             # Work backwards from the destination to the start
#             while current != S:
#                 final_path.append(current)
#                 current = self.came_from[current]
            
#             # Don't forget to add the start node!
#             final_path.append(S)
            
#             # Reverse it so it goes Source -> Destination
#             final_path.reverse() 

#         return {
#             "distance": result,
#             "visited": list(dict.fromkeys(self.visited)), 
#             "final_path": final_path
#         }