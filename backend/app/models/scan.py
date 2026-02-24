from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size = Column(Integer)
    file_url = Column(String)
    
    status = Column(String, default="pending")
    
    deepfake_score = Column(Float)
    confidence = Column(Float)
    risk_level = Column(String)
    
    analysis_result = Column(JSON)
    is_deleted = Column(Integer, default=0) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    user = relationship("app.models.user.User", backref="scans")
