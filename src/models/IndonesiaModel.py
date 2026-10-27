from src.store.AppState import state
import sqlite3
import csv

class IndonesiaModel:
    def __init__(self):
        self.conn = sqlite3.connect(state.indoDbPath)
        self.c = self.conn.cursor()

    def nodes(self):
        self.c.execute("SELECT osmid, y, x FROM nodes")
        return self.c.fetchall()

    def edges(self):
        self.c.execute("SELECT source, target, MIN(length) FROM edges GROUP BY source, target")
        return self.c.fetchall()
    
    def nodes_count(self):
        self.c.execute("SELECT COUNT(*) FROM nodes")
        return self.c.fetchone()[0]

    def coords(self, osmid):
        self.c.execute("SELECT y, x FROM nodes WHERE osmid = ?", (osmid,))
        return self.c.fetchone()

    def successors(self, osmid):
        self.c.execute("""
            SELECT target, MIN(length) 
            FROM edges 
            WHERE source = ? 
            GROUP BY target
        """, (osmid,))
        return self.c.fetchall()

    def predecessors(self, osmid):
        self.c.execute("""
            SELECT source, MIN(length) 
            FROM edges 
            WHERE target = ? 
            GROUP BY source
        """, (osmid,))
        return self.c.fetchall()

    def successors_with_coords(self, osmid):
        self.c.execute("""
            SELECT e.target, MIN(e.length), n.y, n.x
            FROM edges e
            JOIN nodes n ON e.target = n.osmid
            WHERE e.source = ?
            GROUP BY e.target
        """, (osmid,))
        return self.c.fetchall()

    def predecessors_with_coords(self, osmid):
        self.c.execute("""
            SELECT e.source, MIN(e.length), n.y, n.x
            FROM edges e
            JOIN nodes n ON e.source = n.osmid
            WHERE e.target = ?
            GROUP BY e.source
        """, (osmid,))
        return self.c.fetchall()

    def get_coordinates_from_csv(self, csv_file_path):
        """Membaca CSV dan mengambil koordinat lat/lon dari SQLite berdasarkan OSMID"""
        with self.conn:
            # Kumpulkan semua OSMID unik dari CSV agar query database efisien
            sources = set()
            dests = set()
            
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('source_osmid'): sources.add(int(row['source_osmid']))
                    if row.get('dest_osmid'): dests.add(int(row['dest_osmid']))

            osmids = sources.union(dests)
            if not osmids:
                return []
            
            # Menggunakan klausa IN (id1, id2, ...)
            format_strings = ','.join('?' for _ in osmids)
            query = f"SELECT osmid, y, x FROM nodes WHERE osmid IN ({format_strings})"
            self.c.execute(query, list(osmids))
            rows = self.c.fetchall()
            
            pinpoints = []
            for row in rows:
                node_id = row[0]
                # Tentukan apakah ini titik awal atau tujuan
                node_type = "source" if node_id in sources else "dest"
                
                pinpoints.append({
                    "id": node_id, 
                    "lat": row[1], 
                    "lon": row[2], 
                    "type": node_type # <-- Info tipe ini akan dibaca oleh JavaScript!
                })
            # Ubah menjadi format list of dict agar mudah dikirim ke JavaScript
            # pinpoints = [{"id": row[0], "lat": row[1], "lon": row[2]} for row in rows]
            return pinpoints