from src.store.AppState import state
import sqlite3

class History:
    id: int | None
    alg: str

class HistoryModel:
    def __init__(self):
        self.conn = sqlite3.connect(state.appDbPath)
        self.c = self.conn.cursor()
    
    def insert(self, alg, source_osmid, dest_osmid, distance, exec_time, exec_space, vis_nodes, created_at):
        with self.conn:
            self.c.execute(
                """INSERT INTO histories (alg, source_osmid, dest_osmid, distance, exec_time, exec_space, vis_nodes, created_at)
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)""",
                (alg, source_osmid, dest_osmid, distance, exec_time, exec_space, vis_nodes, created_at)
                )
            
    def fetch_latest_id(self, created_at, alg):
        self.c.execute("SELECT history_id FROM histories WHERE created_at=? AND alg=? ORDER BY history_id DESC LIMIT 1", (created_at, alg))
        return self.c.fetchone()[0]
    
    def fetch_all(self):
        """Fetches all history records and returns them as a list of dictionaries.""" 
        # Fetch all columns, ordering by newest first
        query = """
            SELECT history_id, alg, source_osmid, dest_osmid, distance, 
                   exec_time, exec_space, vis_nodes, created_at 
            FROM histories 
            ORDER BY history_id DESC
        """
        self.c.execute(query)
        rows = self.c.fetchall()

        # Map the raw SQLite tuples to clean Python dictionaries
        history_list = []
        unique_dates = []
        for row in rows:
            if (row[8], row[2], row[3]) not in unique_dates:
                unique_dates.append((row[8], row[2], row[3]))

            history_list.append({
                "history_id": row[0],
                "alg": row[1],
                "source_osmid": row[2],
                "dest_osmid": row[3],
                "distance": row[4],
                "exec_time": row[5],
                "exec_space": row[6],
                "vis_nodes": row[7],
                "created_at": row[8]
            })
            
        return history_list, unique_dates