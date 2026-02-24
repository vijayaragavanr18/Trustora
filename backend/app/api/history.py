from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.schemas.scan import ScanResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/history", tags=["History"])

# Cache migration status to prevent repeated SQL errors in logs
MIGRATION_MISSING = False

@router.get("", response_model=List[ScanResponse])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all scans
    all_scans = db.query(Scan).filter(
        Scan.user_id == current_user.id
    ).order_by(Scan.created_at.desc()).all()
    
    # Filter out soft-deleted ones (using JSON check)
    scans = []
    for s in all_scans:
        res = s.analysis_result or {}
        if not res.get("is_deleted"):
            scans.append(s)
            
    return scans

# GET /api/history/bin (Recycle Bin)
@router.get("/bin", response_model=List[ScanResponse])
def get_deleted_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    all_scans = db.query(Scan).filter(
        Scan.user_id == current_user.id
    ).order_by(Scan.created_at.desc()).all()
    
    deleted_scans = []
    for s in all_scans:
        res = s.analysis_result or {}
        if res.get("is_deleted"):
            deleted_scans.append(s)
            
    return deleted_scans

# POST /api/history/{scan_id}/restore
@router.post("/{scan_id}/restore")
def restore_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    res = scan.analysis_result or {}
    res["is_deleted"] = False
    scan.analysis_result = res
    db.commit()
    return {"message": "Scan restored", "scan_id": scan_id}

# DELETE /api/history/{scan_id} (Soft Delete)
@router.delete("/{scan_id}")
def delete_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Soft delete in JSON
    from sqlalchemy.orm.attributes import flag_modified
    res = scan.analysis_result or {}
    res["is_deleted"] = True
    scan.analysis_result = res
    flag_modified(scan, "analysis_result") # Ensure SQLA sees the change
    db.commit()
    return {"message": "Moved to Recycle Bin", "scan_id": scan_id}

# DELETE /api/history/{scan_id}/permanent (Hard Delete)
@router.delete("/{scan_id}/permanent")
def hard_delete_scan(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    db.delete(scan)
    db.commit()
    return {"message": "Permanently deleted"}

# GET /api/history/{scan_id}
@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan_detail(
    scan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan