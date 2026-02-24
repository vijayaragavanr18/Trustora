from sqlalchemy import create_engine, text
from app.config import settings

def check_owner():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tableowner FROM pg_tables WHERE tablename = 'users'"))
        row = result.fetchone()
        if row:
            print(f"Table Owner: {row[0]}")
        
        result = conn.execute(text("SELECT CURRENT_USER"))
        row = result.fetchone()
        if row:
            print(f"Current User: {row[0]}")

if __name__ == "__main__":
    check_owner()
