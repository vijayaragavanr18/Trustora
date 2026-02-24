from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.utils.security import get_current_user
import uuid
from typing import Dict, Any

router = APIRouter(prefix="/report", tags=["Report"])

@router.get("/{scan_id}/json")
def get_json_report(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    return {
        "scan_id": str(scan.id),
        "timestamp": scan.created_at.isoformat(),
        "file_name": scan.file_name,
        "type": scan.file_type,
        "results": {
            "score": scan.deepfake_score,
            "confidence": scan.confidence,
            "risk": scan.risk_level,
            "details": scan.analysis_result
        }
    }

@router.get("/{scan_id}/pdf")
def get_pdf_report(
    scan_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TODO: Implement actual PDF generation using ReportLab or FPDF
    # For now, return a dummy response or similar
    scan = db.query(Scan).filter(
        Scan.id == scan_id,
        Scan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return {
        "message": "PDF generation not implemented yet",
        "link": f"/api/report/{scan_id}/json"
    }
