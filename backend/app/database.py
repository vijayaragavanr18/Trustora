from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from app.config import settings

# Determine final DATABASE_URL
# If the postgres URL is the default placeholder, use SQLite for reliability during developement
db_url = settings.DATABASE_URL
if "user:password" in db_url or not db_url.startswith("postgresql"):
    print("--- DB: Using persistent SQLite database for maximum reliability ---")
    db_url = "sqlite:///./trustora.db"
    # SQLite fix for concurrent access
    connect_args = {"check_same_thread": False}
else:
    print(f"--- DB: Connecting to {db_url.split('@')[-1]} ---")
    connect_args = {}

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    echo=False,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_and_fix_columns():
    """
    Poor man's migration: Automatically adds missing columns to the database 
    without needing Alembic. This prevents 'No such column' errors.
    """
    from app.models.user import User, UserSettings
    from app.models.scan import Scan
    
    inspector = inspect(engine)
    
    # Tables to check matches the models
    tables = {
        "users": User,
        "scans": Scan,
        "user_settings": UserSettings
    }
    
    with engine.connect() as conn:
        for table_name, model in tables.items():
            if table_name not in inspector.get_table_names():
                continue
                
            # Get existing columns
            existing_cols = [c["name"] for c in inspector.get_columns(table_name)]
            
            # Check model columns
            for col_name, column in model.__table__.columns.items():
                if col_name not in existing_cols:
                    print(f"--- DB: Adding missing column [{col_name}] to table [{table_name}] ---")
                    try:
                        # SQLite/Postgres syntax for ADD COLUMN
                        type_str = str(column.type)
                        # Normalize type for SQLite (very basic)
                        if "VARCHAR" in type_str: type_str = "TEXT"
                        if "JSON" in type_str: type_str = "TEXT" 
                        
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {type_str}"))
                        conn.commit()
                    except Exception as e:
                        print(f"--- DB ERROR: Could not add column {col_name}: {e} ---")
