from sqlalchemy import create_engine, text
import sys
import os

# Add current dir to path to import app correctly
sys.path.append(os.getcwd())

from app.config import settings

engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE scans ADD COLUMN is_deleted INTEGER DEFAULT 0;"))
        conn.commit()
        print("Successfully added is_deleted column to scans table.")
    except Exception as e:
        print(f"Result: {e}")
