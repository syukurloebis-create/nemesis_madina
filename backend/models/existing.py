# backend/models/existing.py

# Re-export from compatibility layer (which re-exports from canonical)
from backend.models.user import User
from backend.cases.models import Case

# Keep AuditLog (unique to this file)
from backend.database import Base
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    action = Column(String)
    resource = Column(String)
    resource_id = Column(String)
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

__all__ = [
    "User",
    "Case",
    "AuditLog",
]