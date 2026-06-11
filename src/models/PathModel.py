from src.store.AppState import state
import sqlite3
import gc

class PathModel:
    def __init__(self):
        self.conn = sqlite3.connect(state.appDbPath)
        self.c = self.conn.cursor()
    
    def to_coords(self, osmid_list: list) -> list:
        """
        Converts a massive list of OSMIDs into an ordered list of [lat, lon] coordinates.
        Uses bulk chunking to prevent database freezing.
        """
        if not osmid_list:
            return []

        conn_indo = sqlite3.connect(state.indoDbPath)
        c_indo = conn_indo.cursor()

        # 1. We use a dictionary to temporarily store the results
        # so we can rebuild the exact order later.
        coords_dict = {}

        # 2. SQLite has a limit of 999 variables per query.
        # We split the massive list into chunks of 900 to be safe.
        chunk_size = 900
        
        # Make sure your column names here match your actual Indonesia database!
        # OSMnx usually names them 'y' (lat) and 'x' (lon). If yours are 'lat'/'lon', change them here.
        query_base = "SELECT osmid, y, x FROM nodes WHERE osmid IN ({})"

        for i in range(0, len(osmid_list), chunk_size):
            chunk = osmid_list[i:i + chunk_size]
            
            # Create a string of question marks: "?, ?, ?, ..."
            placeholders = ','.join(['?'] * len(chunk))
            query = query_base.format(placeholders)
            
            c_indo.execute(query, chunk)
            
            # Populate our dictionary: { 12345: [-6.20, 106.81] }
            for row in c_indo.fetchall():
                osmid = row[0]
                lat = row[1]
                lon = row[2]
                coords_dict[osmid] = [lat, lon]

        conn_indo.close()

        # 3. Rebuild the final list in the EXACT original order of the algorithm
        ordered_coords = []
        for osmid in osmid_list:
            if osmid in coords_dict:
                ordered_coords.append(coords_dict[osmid])

        return ordered_coords

    def insert_final_path(self, history_id: int, ordered_coords: list):   
        """
        Saves a list of coordinates into the 'paths' table.
        ordered_coords format: [[lat1, lon1], [lat2, lon2], ...]
        """
        if not ordered_coords:
            return

        # 1. Prepare the data list
        points_to_insert = []
        for coords in ordered_coords:
            lat = coords[0]
            lon = coords[1]
            # Pack them into a tuple matching your columns: (lat, long, history_id)
            points_to_insert.append((lat, lon, history_id))

        # 2. Blast it into the database all at once
        with self.conn:
            self.c.executemany(
                """INSERT INTO paths (lat, long, history_id)
                   VALUES (?, ?, ?)""",
                points_to_insert
            )
            
    def get_final_path_by_history(self, history_id: int):
        with self.conn:
            # ORDER BY path_id ensures the animation/line is drawn in the correct direction!
            self.c.execute(
                """SELECT lat, long FROM paths 
                   WHERE history_id = ? 
                   ORDER BY path_id ASC""", 
                (history_id,)
            )
            # Returns a list of tuples: [(-6.2, 106.8), (-6.3, 106.9), ...]
            return self.c.fetchall()

    def insert_traversal(self, history_id: int, ordered_coords: list):   
        """
        Saves a list of coordinates into the 'paths' table.
        ordered_coords format: [[lat1, lon1], [lat2, lon2], ...]
        """
        if not ordered_coords:
            return

        # len_coords = len(ordered_coords)
        # if len_coords <= max_nodes:
        #     sampled_coords = ordered_coords
        # else:
        #     sampled_coords = ordered_coords[::len_coords//max_nodes]
        
        # del ordered_coords
        # gc.collect()

        # 1. Prepare the data list
        points_to_insert = []
        for coords in ordered_coords:
            lat = coords[0]
            lon = coords[1]
            # Pack them into a tuple matching your columns: (lat, long, history_id)
            points_to_insert.append((lat, lon, history_id))

        # 2. Blast it into the database all at once
        with self.conn:
            self.c.executemany(
                """INSERT INTO traversals (lat, long, history_id)
                   VALUES (?, ?, ?)""",
                points_to_insert
            )        
    
    def get_traversal_by_history(self, history_id: int, max_nodes=30000):
        with self.conn:
            # ORDER BY path_id ensures the animation/line is drawn in the correct direction!
            self.c.execute(
                """SELECT lat, long FROM traversals 
                   WHERE history_id = ? 
                   ORDER BY path_id ASC""", 
                (history_id,)
            )

            all_nodes = self.c.fetchall()
            total_nodes = len(all_nodes)
            
            # 1. If it's a short route, just return everything
            if max_nodes == -1 or total_nodes <= max_nodes:
                return all_nodes
                
            # 2. If it's massive, calculate the skip interval
            # e.g., 45,000 total nodes // 1,500 max = grab every 30th node
            step_size = total_nodes // max_nodes
            # x / y = 1500
            
            # 3. Use Python list slicing to grab every N-th item
            # The syntax [start:stop:step] keeps the exact chronological order!
            sampled_nodes = all_nodes[::step_size]
            
            print(f"Downsampled traversal from {total_nodes} nodes to {len(sampled_nodes)} nodes.")
            
            return sampled_nodes
    
    def get_traversal_by_history_all(self, history_id: int):
        with self.conn:
            # ORDER BY path_id ensures the animation/line is drawn in the correct direction!
            self.c.execute(
                """SELECT lat, long FROM traversals 
                   WHERE history_id = ? 
                   ORDER BY path_id ASC""", 
                (history_id,)
            )
            # Returns a list of tuples: [(-6.2, 106.8), (-6.3, 106.9), ...]
            return self.c.fetchall()