"""
This script migrates ALL scans from vijay@gmail.com to lingesan@trustora.com
so that the app displays history correctly when you log in with lingesan@trustora.com.
"""
from app.database import SessionLocal
from app.models.user import User
from app.models.scan import Scan

db = SessionLocal()

# Get source and target users
source_user = db.query(User).filter(User.email == "vijay@gmail.com").first()
target_user = db.query(User).filter(User.email == "lingesan@trustora.com").first()

if not source_user:
    print("ERROR: vijay@gmail.com not found!")
    db.close()
    exit(1)

if not target_user:
    print("ERROR: lingesan@trustora.com not found!")
    db.close()
    exit(1)

print(f"Source: {source_user.email} (ID: {source_user.id})")
print(f"Target: {target_user.email} (ID: {target_user.id})")

# Count before
before_count = db.query(Scan).filter(Scan.user_id == source_user.id).count()
print(f"\nScans to migrate: {before_count}")

# Migrate scans
db.query(Scan).filter(Scan.user_id == source_user.id).update(
    {"user_id": target_user.id}
)
db.commit()

# Count after
after_count = db.query(Scan).filter(Scan.user_id == target_user.id).count()
print(f"Scans now belonging to lingesan@trustora.com: {after_count}")
print("\nDone! Log in with lingesan@trustora.com to see all history.")
db.close()
