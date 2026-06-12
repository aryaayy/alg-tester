from src.models.HistoryModel import HistoryModel
import csv

def to_csv_all(file_path):
    """Triggered when the user clicks File -> Export or presses Ctrl+E"""
    
    # 1. Open a Save File Dialog
    # file_path = caller.get_export_path()
    
    if not file_path:
        return {
            "res": "failed",
            "code": 467,
            "msg": "Tidak ada file path"
        }

    # 2. Call your Model!
    history_model = HistoryModel()
    history_list, _ = history_model.fetch_all()
    
    # Check if there is actually data to export
    if not history_list:
        return {
            "res": "failed",
            "code": 477,
            "msg": "Tidak ada data riwayat"
        }

    # 3. Get the exact headers from the dictionary keys 
    # (history_id, alg, source_osmid, etc.)
    headers = list(history_list[0].keys())

    # 4. Write to CSV using DictWriter
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        # DictWriter automatically maps your dictionaries to the correct columns!
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        
        writer.writeheader()         # Write the top row (column names)
        writer.writerows(history_list) # Dump all the dictionaries in at once
    
    return {
        "res": "success",
        "code": 200,
        "msg": f"{len(history_list)} berhasil diexport ke: {file_path}"
    }

def to_csv_by_timestamp(file_path, timestamp):
    """Triggered when the user clicks File -> Export or presses Ctrl+E"""
    
    # 1. Open a Save File Dialog
    # file_path = caller.get_export_path()
    
    if not file_path:
        return {
            "res": "failed",
            "code": 467,
            "msg": "Tidak ada file path"
        }

    # 2. Call your Model!
    history_model = HistoryModel()
    history_list = history_model.fetch_by_timestamp(timestamp)
    
    # Check if there is actually data to export
    if not history_list:
        return {
            "res": "failed",
            "code": 477,
            "msg": "Tidak ada data riwayat"
        }

    # 3. Get the exact headers from the dictionary keys 
    # (history_id, alg, source_osmid, etc.)
    headers = list(history_list[0].keys())

    # 4. Write to CSV using DictWriter
    with open(file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        # DictWriter automatically maps your dictionaries to the correct columns!
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        
        writer.writeheader()         # Write the top row (column names)
        writer.writerows(history_list) # Dump all the dictionaries in at once
    
    return {
        "res": "success",
        "code": 200,
        "msg": f"{len(history_list)} berhasil diexport ke: {file_path}"
    }
      