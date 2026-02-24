"""
Add is_deleted column to scans table for soft delete support.
Tries multiple approaches to get it done.
"""
import os
import sys

# Load .env manually
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, val = line.partition('=')
                os.environ.setdefault(key.strip(), val.strip())

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://trustora_user:password@localhost:5432/trustora')
print(f"Using DB: {DATABASE_URL}")

try:
    import psycopg2
    from urllib.parse import urlparse

    parsed = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=parsed.path.lstrip('/'),
        user=parsed.username,
        password=parsed.password
    )
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute("ALTER TABLE scans ADD COLUMN is_deleted INTEGER DEFAULT 0;")
        print("✅ is_deleted column added successfully!")
    except psycopg2.errors.DuplicateColumn:
        print("ℹ️  is_deleted column already exists — nothing to do.")
    except Exception as e:
        print(f"❌ Could not add column: {e}")
    finally:
        cur.close()
        conn.close()

except ImportError:
    print("psycopg2 not available, trying sqlalchemy...")
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE scans ADD COLUMN IF NOT EXISTS is_deleted INTEGER DEFAULT 0"))
            conn.commit()
            print("✅ is_deleted column added via SQLAlchemy!")
        except Exception as e:
            print(f"❌ SQLAlchemy error: {e}")
