"""Audit Log API Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import logger
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.audit.logger import AuditLogger

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/log")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = None
):
    """Get audit logs with pagination"""
    logs = AuditLogger.get_logs(limit, offset, event_type)
    
    return {
        "total": len(AuditLogger._logs),
        "returned": len(logs),
        "offset": offset,
        "limit": limit,
        "logs": logs
    }


@router.get("/verify")
async def verify_audit_integrity():
    """Verify audit log integrity (tamper-proof check)"""
    result = AuditLogger.verify_integrity()
    
    return result


@router.get("/stats")
async def get_audit_stats():
    """Get audit log statistics"""
    return AuditLogger.get_stats()


@router.post("/test")
async def test_audit_log(action: str, actor: str = "test"):
    """Test audit log entry (for testing)"""
    entry = AuditLogger.log(
        action=action,
        actor=actor,
        resource="test",
        data={"test": True}
    )
    
    return {"message": "Test log created", "entry": entry}
