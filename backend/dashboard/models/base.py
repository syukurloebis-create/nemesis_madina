# backend/dashboard/models/base.py

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model with common fields."""
    
    class Config:
        frozen = True
        extra = "forbid"


class ResponseMeta(BaseModel):
    """Response metadata."""
    status: str = "success"
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    has_data: bool = True
    version: str = "2.0.0"
    
    class Config:
        frozen = True