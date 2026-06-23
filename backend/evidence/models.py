from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum
import uuid

class EvidenceStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    ANALYZED = "analyzed"
    SUBMITTED = "submitted"
    REJECTED = "rejected"

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)  # Tanpa foreign key
    user_id = Column(String, nullable=False)  # Tanpa foreign key
    institution_id = Column(String, nullable=False)
    
    filename = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    
    mime_type = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    
    status = Column(SQLEnum(EvidenceStatus), default=EvidenceStatus.UPLOADED)
    confidence_score = Column(Float, default=0.0)
    
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verified_by = Column(String, nullable=True)
    
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChainOfCustody(Base):
    __tablename__ = "chain_of_custody"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, nullable=False)  # Tanpa foreign key
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    institution_id = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Finding(Base):
    __tablename__ = "findings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)  # Tanpa foreign key
    evidence_ids = Column(Text, nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    finding_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    
    anomaly_score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
