from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List, Any
import uuid

class ScanBase(BaseModel):
    file_name: str
    file_type: str

class ScanCreate(ScanBase):
    file_size: int
    file_url: str

class ScanResponse(ScanBase):
    id: uuid.UUID
    user_id: uuid.UUID
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    deepfake_score: Optional[float]
    confidence: Optional[float]
    risk_level: Optional[str]
    analysis_result: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    scan_id: uuid.UUID
    score: Optional[float] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    artifacts_found: List[str] = []
    model_scores: Dict[str, Any] = {}
    heatmap_url: Optional[str] = None
    analysis_details: Dict[str, Any] = {}
    
    model_config = {
        "protected_namespaces": ()
    }
