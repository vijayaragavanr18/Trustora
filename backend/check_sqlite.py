import sqlite3
import os

db_path = "trustora.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT email FROM users;")
        rows = cursor.fetchall()
        print(f"Users in SQLite ({db_path}):")
        for row in rows:
            print(f" - {row[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
else:
    print(f"File {db_path} not found.")
