from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.scan import Scan
from app.utils.security import get_current_user

router = APIRouter(prefix="/report", tags=["Reports"])

# GET /api/report/{scan_id}/json
@router.get("/{scan_id}/json")
def get_json_report(
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
    
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    report = {
        "report_id": f"RPT-{scan_id[:8].upper()}",
        "generated_at": datetime.utcnow().isoformat(),
        "scan_details": {
            "scan_id": scan.id,
            "file_name": scan.file_name,
            "file_type": scan.file_type,
            "analyzed_at": scan.completed_at.isoformat() if scan.completed_at else None
        },
        "results": {
            "deepfake_score": scan.deepfake_score,
            "confidence": scan.confidence,
            "risk_level": scan.risk_level,
            "verdict": "DEEPFAKE DETECTED" if scan.deepfake_score > 70 else "LIKELY AUTHENTIC",
            "artifacts": scan.analysis_result.get("artifacts_detected", []) if scan.analysis_result else [],
            "model_scores": scan.analysis_result.get("model_scores", {}) if scan.analysis_result else {}
        },
        "user": {
            "email": current_user.email,
            "full_name": current_user.full_name,
            "organization": current_user.organization
        },
        "trustora_version": "1.0.0"
    }
    
    return JSONResponse(content=report)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from xml.sax.saxutils import escape
from fastapi import Response

def _generate_pdf_report(scan: Scan, current_user: User) -> bytes:
    """Zero-dependency low-level Canvas generator with full details restored"""
    buffer = BytesIO()
    try:
        c = canvas.Canvas(buffer, pagesize=letter)
        w, h = letter
        y = h - 50
        
        # 1. Header
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#06b6d4")) # Trustora Cyan
        c.drawCentredString(w/2.0, y, "TRUSTORA FORENSIC ANALYSIS")
        y -= 10
        c.setStrokeColor(colors.lightgrey)
        c.line(50, y, w-50, y)
        y -= 25
        
        # 2. Basic Info
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "REPORT ID:")
        c.setFont("Helvetica", 10)
        c.drawString(120, y, str(scan.id))
        y -= 15
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "GENERATED:")
        c.setFont("Helvetica", 10)
        c.drawString(120, y, f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        y -= 35
        
        # 3. Verdict Section
        score = float(scan.deepfake_score or 0.0)
        verdict = "DEEPFAKE DETECTED" if score > 70 else "SUSPICIOUS CONTENT" if score > 40 else "AUTHENTIC MEDIA"
        v_col = colors.red if score > 70 else colors.orange if score > 40 else colors.green
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "ANALYSIS VERDICT:")
        c.setFillColor(v_col)
        c.drawString(180, y, verdict)
        y -= 20
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Confidence Score: {score:.2f}%")
        c.drawString(250, y, f"Risk Level: {str(scan.risk_level or 'N/A').upper()}")
        y -= 40
        
        # 4. Forensic Metadata
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "FORENSIC METADATA")
        y -= 5
        c.line(50, y, 200, y)
        y -= 20
        
        c.setFont("Helvetica", 9)
        c.drawString(60, y, f"Filename: {str(scan.file_name)}")
        y -= 15
        c.drawString(60, y, f"File Type: {str(scan.file_type).upper()}")
        y -= 15
        c.drawString(60, y, f"File Size: {getattr(scan, 'file_size', 0) / 1024:.1f} KB")
        y -= 15
        c.drawString(60, y, f"Analyzed At: {scan.completed_at.strftime('%Y-%m-%d %H:%M:%S') if scan.completed_at else 'N/A'}")
        y -= 35
        
        # 5. Detected Artifacts (Restored)
        res = scan.analysis_result or {}
        artifacts = res.get("artifacts_found", res.get("artifacts_detected", []))
        if artifacts:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "DETECTED ANOMALIES")
            y -= 5
            c.line(50, y, 200, y)
            y -= 20
            
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.red)
            for art in artifacts:
                c.drawString(65, y, f"• {str(art).replace('_', ' ').capitalize()}")
                y -= 14
                if y < 100: # Simple page overflow check
                    c.showPage()
                    y = h - 50
            y -= 20
            c.setFillColor(colors.black)

        # 6. Blockchain Integrity Seal
        seal = res.get("blockchain_seal")
        if seal and isinstance(seal, dict):
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "BLOCKCHAIN INTEGRITY SEAL")
            y -= 5
            c.line(50, y, 200, y)
            y -= 20
            
            c.setFont("Helvetica", 8)
            c.drawString(60, y, "Evidence Forensic Hash (SHA-256):")
            y -= 12
            c.setFont("Courier", 7)
            c.drawString(70, y, str(seal.get("evidence_hash", "N/A")))
            y -= 18
            
            c.setFont("Helvetica", 8)
            c.drawString(60, y, "Sepolia Transaction ID:")
            y -= 12
            c.setFont("Courier", 7)
            c.setFillColor(colors.blue)
            c.drawString(70, y, str(seal.get("transaction_hash", "N/A")))
            y -= 25
            c.setFillColor(colors.black)
        
        # 7. Requester Info
        y = max(y, 100) # Ensure it doesn't fall off bottom
        c.setFont("Helvetica", 9)
        name = str(current_user.full_name or "Authorized User")
        email = str(current_user.email or "N/A")
        c.drawString(50, y, f"Report requested by: {name} ({email})")
        y -= 20
        
        # 8. Disclaimer
        c.setFont("Helvetica-Oblique", 7)
        c.setFillColor(colors.grey)
        disclaimer = "LEGAL DISCLAIMER: This report is generated by Trustora's multi-modal AI forensic system. While results are statistically significant, they should be used as supporting evidence and verified by a digital forensics expert in legal proceedings."
        # Simple wrapping for disclaimer
        c.drawString(50, y, disclaimer[:100])
        c.drawString(50, y-10, disclaimer[100:])

        c.save()
        return buffer.getvalue()
    except Exception as e:
        import sys, traceback
        print(f"[ERROR] PDF Generation: {e}", file=sys.stderr)
        traceback.print_exc()
        # Emergency canvas
        b2 = BytesIO()
        c2 = canvas.Canvas(b2)
        c2.drawString(100, 700, "Forensic Report Generation Error")
        c2.drawString(100, 680, f"Details: {str(e)}")
        c2.save()
        return b2.getvalue()

# GET /api/report/{scan_id}/pdf  
@router.get("/{scan_id}/pdf")
def get_pdf_report(
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
    
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    try:
        pdf_bytes = _generate_pdf_report(scan, current_user)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report_{scan_id}.pdf"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

# POST /api/report/batch-export
@router.post("/batch-export")
def batch_export(
    scan_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    import zipfile
    from io import BytesIO
    from fastapi.responses import Response
    import os

    scans = db.query(Scan).filter(
        Scan.id.in_(scan_ids),
        Scan.user_id == current_user.id
    ).all()

    if not scans:
        raise HTTPException(status_code=404, detail="No scans found to export")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for scan in scans:
            if scan.status != "completed":
                continue
            
            # 1. Add PDF Report
            pdf_bytes = _generate_pdf_report(scan, current_user)
            zip_file.writestr(f"reports/report_{scan.id}.pdf", pdf_bytes)

            # 2. Add Original File
            file_path = scan.file_url.lstrip("/")
            if os.path.exists(file_path):
                zip_file.write(file_path, arcname=f"media/{scan.file_name}")

    zip_buffer.seek(0)
    filename = f"trustora_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
