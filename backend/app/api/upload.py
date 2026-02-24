from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid, os
from pathlib import Path
from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.schemas.scan import ScanResponse
from app.utils.security import get_current_user
from typing import List
from app.config import settings

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg", "image/webp", "image/heic"]
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/mov", "video/avi", "video/quicktime", "video/webm", "video/x-matroska"]
ALLOWED_AUDIO_TYPES = ["audio/mpeg", "audio/wav", "audio/mp3", "audio/ogg", "audio/webm", "audio/aac", "audio/x-m4a"]

def is_allowed_type(content_type: str, allowed_list: List[str]) -> bool:
    if not content_type:
        return False
    # Handle types like 'video/webm;codecs=vp9'
    base_type = content_type.split(';')[0].strip().lower()
    return base_type in allowed_list

def save_file(file: UploadFile, folder: str):
    upload_dir = Path(settings.UPLOAD_DIR) / folder
    upload_dir.mkdir(parents=True, exist_ok=True)
    ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_name
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return str(file_path), f"/uploads/{folder}/{unique_name}"

# POST /api/upload/image
@router.post("/image", response_model=ScanResponse)
def upload_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_allowed_type(file.content_type, ALLOWED_IMAGE_TYPES):
        raise HTTPException(status_code=400, detail=f"Invalid image type: {file.content_type}")
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")
    
    _, file_url = save_file(file, "images")
    
    scan = Scan(
        user_id=current_user.id,
        file_name=file.filename,
        file_type="image",
        file_size=file_size,
        file_url=file_url,
        status="pending"
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan

# POST /api/upload/video
@router.post("/video", response_model=ScanResponse)
def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_allowed_type(file.content_type, ALLOWED_VIDEO_TYPES):
        raise HTTPException(status_code=400, detail=f"Invalid video type: {file.content_type}")
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")
    
    _, file_url = save_file(file, "videos")
    
    scan = Scan(
        user_id=current_user.id,
        file_name=file.filename,
        file_type="video",
        file_size=file_size,
        file_url=file_url,
        status="pending"
    )
    db.add(scan)
    db.commit()
    try:
        db.refresh(scan)
    except:
        db.rollback()
    return scan

# POST /api/upload/audio
@router.post("/audio", response_model=ScanResponse)
def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_allowed_type(file.content_type, ALLOWED_AUDIO_TYPES):
        raise HTTPException(status_code=400, detail=f"Invalid audio type: {file.content_type}")
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    _, file_url = save_file(file, "audio")
    
    scan = Scan(
        user_id=current_user.id,
        file_name=file.filename,
        file_type="audio",
        file_size=file_size,
        file_url=file_url,
        status="pending"
    )
    db.add(scan)
    db.commit()
    try:
        db.refresh(scan)
    except:
        db.rollback()
    return scan

# GET /api/upload/status/{upload_id}
@router.get("/status/{upload_id}")
def get_upload_status(
    upload_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == upload_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return {
        "upload_id": scan.id,
        "status": scan.status,
        "file_name": scan.file_name,
        "file_type": scan.file_type
    }
