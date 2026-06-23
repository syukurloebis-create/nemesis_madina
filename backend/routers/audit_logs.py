from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from security.dependencies import get_current_active_user
from security.models import User

router = APIRouter(prefix="/audit", tags=["audit"])

# Mock data untuk audit logs
MOCK_AUDIT_LOGS = [
    {
        "id": "1",
        "action": "CASE_CREATED",
        "entity_type": "case",
        "entity_id": "case-001",
        "user_id": "user-001",
        "user_name": "Admin User",
        "changes": {"title": "Fraud Investigation", "priority": "HIGH"},
        "timestamp": datetime.now().isoformat(),
        "ip_address": "192.168.1.1"
    },
    {
        "id": "2",
        "action": "EVIDENCE_ADDED",
        "entity_type": "evidence",
        "entity_id": "evid-001",
        "user_id": "user-001",
        "user_name": "Admin User",
        "changes": {"title": "Financial Report", "type": "document"},
        "timestamp": datetime.now().isoformat(),
        "ip_address": "192.168.1.1"
    },
    {
        "id": "3",
        "action": "CASE_ASSIGNED",
        "entity_type": "case",
        "entity_id": "case-001",
        "user_id": "user-002",
        "user_name": "Investigator",
        "changes": {"assignee": "investigator_01", "status": "INVESTIGATING"},
        "timestamp": datetime.now().isoformat(),
        "ip_address": "192.168.1.2"
    },
    {
        "id": "4",
        "action": "USER_LOGIN",
        "entity_type": "user",
        "entity_id": "user-001",
        "user_id": "user-001",
        "user_name": "Admin User",
        "changes": {"login_success": True},
        "timestamp": datetime.now().isoformat(),
        "ip_address": "192.168.1.1"
    },
    {
        "id": "5",
        "action": "STATUS_CHANGED",
        "entity_type": "case",
        "entity_id": "case-001",
        "user_id": "user-002",
        "user_name": "Investigator",
        "changes": {"old_status": "OPEN", "new_status": "INVESTIGATING"},
        "timestamp": datetime.now().isoformat(),
        "ip_address": "192.168.1.2"
    }
]


@router.get("/logs")
async def get_audit_logs(
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """Get audit logs with filters"""
    logs = MOCK_AUDIT_LOGS.copy()
    
    if entity_id:
        logs = [l for l in logs if l["entity_id"] == entity_id]
    if entity_type:
        logs = [l for l in logs if l["entity_type"] == entity_type]
    if action:
        logs = [l for l in logs if l["action"] == action]
    
    # Sort by timestamp descending
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    total = len(logs)
    logs = logs[offset:offset + limit]
    
    return {"data": logs, "total": total, "offset": offset, "limit": limit}


@router.get("/logs/{log_id}")
async def get_audit_log(
    log_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get audit log by ID"""
    log = next((l for l in MOCK_AUDIT_LOGS if l["id"] == log_id), None)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return log


@router.get("/summary/stats")
async def get_audit_stats(
    current_user: User = Depends(get_current_active_user)
):
    """Get audit log statistics"""
    return {
        "total_logs": len(MOCK_AUDIT_LOGS),
        "by_action": {
            "CASE_CREATED": 1,
            "EVIDENCE_ADDED": 1,
            "CASE_ASSIGNED": 1,
            "USER_LOGIN": 1,
            "STATUS_CHANGED": 1
        },
        "last_24h": 3,
        "unique_users": 2
    }
