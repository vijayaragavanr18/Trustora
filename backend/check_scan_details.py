import sqlite3
import os
import json

db_path = "trustora.db"
scan_id = "9c5f2c1e-66d8-481d-a726-c884de4f9378"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, status, deepfake_score, created_at, completed_at, analysis_result FROM scans WHERE id = ?;", (scan_id,))
        row = cursor.fetchone()
        if row:
            print(f"Scan ID: {row[0]}")
            print(f"Status: {row[1]}")
            print(f"Score: {row[2]}")
            print(f"Created At: {row[3]}")
            print(f"Completed At: {row[4]}")
            print(f"Result length: {len(row[5]) if row[5] else 'None'}")
            if row[5]:
                print(f"Result: {row[5]}")
        else:
            print(f"Scan {scan_id} not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"File {db_path} not found.")
