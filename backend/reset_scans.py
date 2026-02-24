import sqlite3
import os

db_path = "trustora.db"

def reset_stuck_scans():
    if not os.path.exists(db_path):
        print("Database not found.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Reset any scan that has been "processing" for too long (or from previous sessions)
        cursor.execute("UPDATE scans SET status = 'pending' WHERE status = 'processing';")
        count = conn.total_changes
        conn.commit()
        print(f"✅ Reset {count} stuck scans to 'pending'.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_stuck_scans()
