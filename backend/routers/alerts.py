from fastapi import APIRouter, Query
from typing import Optional
import uuid
from datetime import datetime

router = APIRouter()

@router.get("/")
async def get_alerts(
    case_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get alerts - simple implementation"""
    now = datetime.now()
    alerts = []
    
    # Simple static data yang pasti berfungsi
    for i in range(min(limit, 5)):
        alerts.append({
            "id": f"alert-{uuid.uuid4().hex[:8]}",
            "case_id": case_id or "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "type": "COLLUSION",
            "severity": "CRITICAL",
            "title": f"Suspicious Pattern Detected #{i+1}",
            "description": f"Alert description for pattern {i+1}",
            "timestamp": now.isoformat(),
            "status": "NEW",
            "source": "AI_ANALYTICS",
            "confidence": 0.85,
            "evidence": ["evidence-1", "evidence-2"],
            "metadata": {}
        })
    
    return alerts

@router.get("/stats")
async def get_alerts_stats(case_id: Optional[str] = Query(None)):
    """Get alert statistics - simple implementation"""
    return {
        "total": 5,
        "new": 2,
        "acknowledged": 1,
        "resolved": 1,
        "escalated": 1,
        "critical": 2,
        "high": 1,
        "medium": 1,
        "low": 1
    }

@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get alert by ID - simple implementation"""
    return {
        "id": alert_id,
        "case_id": "446e216d-eb0e-487e-8e6b-ec943468ea20",
        "type": "COLLUSION",
        "severity": "CRITICAL",
        "title": "Suspicious Collusion Detected",
        "description": "Multiple entities showing collusion patterns",
        "timestamp": datetime.now().isoformat(),
        "status": "NEW",
        "source": "AI_ANALYTICS",
        "confidence": 0.92,
        "evidence": ["evidence-1", "evidence-2"],
        "metadata": {}
    }
