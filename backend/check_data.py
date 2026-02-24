from app.database import SessionLocal
from app.models.user import User
from app.models.scan import Scan

db = SessionLocal()

print("=== ALL USERS ===")
users = db.query(User).all()
for u in users:
    scans = db.query(Scan).filter(Scan.user_id == u.id).all()
    print(f"User: {u.email} | ID: {u.id} | Scans: {len(scans)}")

print("\n=== ALL SCANS (with owner) ===")
all_scans = db.query(Scan).all()
print(f"Total scans in DB: {len(all_scans)}")
for s in all_scans:
    owner = db.query(User).filter(User.id == s.user_id).first()
    owner_email = owner.email if owner else "NO OWNER FOUND"
    print(f"Scan ID: {s.id[:8]}... | Owner: {owner_email} | File: {s.file_name} | Status: {s.status}")

db.close()
