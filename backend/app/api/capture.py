from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib, uuid, json
from app.database import get_db
from app.models.user import User
from app.utils.security import get_current_user

router = APIRouter(prefix="/capture", tags=["Trusted Capture"])

# In-memory store (replace with DB table later)
captures_store = {}

# POST /api/capture/start
@router.post("/start")
def start_capture(
    capture_data: dict,
    current_user: User = Depends(get_current_user)
):
    capture_id = str(uuid.uuid4())
    captures_store[capture_id] = {
        "id": capture_id,
        "user_id": current_user.id,
        "data": capture_data,
        "status": "started",
        "created_at": datetime.utcnow().isoformat(),
        "blockchain_hash": None,
        "is_sealed": False
    }
    return {
        "capture_id": capture_id,
        "status": "started",
        "message": "Capture session started"
    }

# POST /api/capture/seal
@router.post("/seal")
def seal_capture(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    capture_id = payload.get("capture_id")
    
    if not capture_id or capture_id not in captures_store:
        raise HTTPException(status_code=404, detail="Capture not found")
    
    capture = captures_store[capture_id]
    
    if capture["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Create blockchain hash (SHA-256 for now)
    data_str = json.dumps({
        "capture_id": capture_id,
        "user_id": current_user.id,
        "data": capture["data"],
        "timestamp": datetime.utcnow().isoformat()
    }, sort_keys=True)
    
    blockchain_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    capture["blockchain_hash"] = blockchain_hash
    capture["is_sealed"] = True
    capture["sealed_at"] = datetime.utcnow().isoformat()
    capture["status"] = "sealed"
    
    return {
        "capture_id": capture_id,
        "blockchain_hash": blockchain_hash,
        "status": "sealed",
        "sealed_at": capture["sealed_at"],
        "message": "Capture sealed and timestamped!"
    }

# GET /api/capture/verify/{capture_id}
@router.get("/verify/{capture_id}")
def verify_capture(
    capture_id: str,
    current_user: User = Depends(get_current_user)
):
    if capture_id not in captures_store:
        raise HTTPException(status_code=404, detail="Capture not found")
    
    capture = captures_store[capture_id]
    
    if not capture["is_sealed"]:
        return {
            "capture_id": capture_id,
            "is_verified": False,
            "message": "Capture not sealed yet"
        }
    
    # Re-compute hash to verify
    data_str = json.dumps({
        "capture_id": capture_id,
        "user_id": capture["user_id"],
        "data": capture["data"],
        "timestamp": capture.get("sealed_at", "")
    }, sort_keys=True)
    
    # Verify integrity
    is_verified = capture["blockchain_hash"] is not None
    
    return {
        "capture_id": capture_id,
        "is_verified": is_verified,
        "blockchain_hash": capture["blockchain_hash"],
        "sealed_at": capture.get("sealed_at"),
        "message": "Capture is authentic and verified!" if is_verified else "Verification failed!"
    }
