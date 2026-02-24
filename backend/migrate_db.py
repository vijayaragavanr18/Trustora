from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print("Starting manual migration...")
        
        # Add language
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR DEFAULT 'English (US)'"))
            print("Added language column")
        except Exception as e:
            print(f"Language column skip: {e}")

        # Add timezone
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN timezone VARCHAR DEFAULT 'UTC-05:00'"))
            print("Added timezone column")
        except Exception as e:
            print(f"Timezone column skip: {e}")

        # Add preferences
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN preferences VARCHAR DEFAULT '{\"analysis_complete\": true, \"security_alerts\": true, \"marketing\": false}'"))
            print("Added preferences column to users")
        except Exception as e:
            print(f"Preferences column skip: {e}")

        # Add is_deleted to scans
        try:
            conn.execute(text("ALTER TABLE scans ADD COLUMN is_deleted INTEGER DEFAULT 0"))
            print("Added is_deleted column to scans")
        except Exception as e:
            print(f"is_deleted column skip: {e}")
            
        conn.commit()
        print("Migration complete!")

if __name__ == "__main__":
    migrate()
