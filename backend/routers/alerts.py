from fastapi import APIRouter, Query, HTTPException
from typing import Optional
import uuid
from datetime import datetime
from pydantic import BaseModel

# BUAT ROUTER TANPA PREFIX
router = APIRouter()

# ============================================================
# MODELS
# ============================================================

class AlertActionPayload(BaseModel):
    level: Optional[str] = None
    reason: Optional[str] = None


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/")
async def get_alerts(
    case_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50)
):
    """Get alerts"""
    now = datetime.now()
    alerts = []

    templates = [
        {"type": "COLLUSION", "severity": "CRITICAL", "title": "Suspicious Collusion Detected"},
        {"type": "FRAUD", "severity": "HIGH", "title": "Unusual Transaction Pattern"},
        {"type": "ANOMALY", "severity": "MEDIUM", "title": "Anomaly in Network"},
        {"type": "RISK", "severity": "HIGH", "title": "Risk Score Increase"},
        {"type": "RED_FLAG", "severity": "CRITICAL", "title": "Red Flag Detected"},
    ]

    statuses = ["NEW", "ACKNOWLEDGED", "RESOLVED", "ESCALATED", "NEW"]

    for i in range(min(limit, len(templates))):
        t = templates[i]
        alerts.append({
            "id": f"alert-{uuid.uuid4().hex[:8]}",
            "case_id": case_id or "446e216d-eb0e-487e-8e6b-ec943468ea20",
            "type": t["type"],
            "severity": t["severity"],
            "title": t["title"],
            "description": f"{t['title']} detected in the system",
            "timestamp": now.isoformat(),
            "status": statuses[i % len(statuses)],
            "source": ["AI_ANALYTICS", "RULE_ENGINE", "GRAPH_ENGINE", "RISK_ENGINE"][i % 4],
            "confidence": 0.85,
            "evidence": [f"evidence-{j+1}" for j in range(2)],
            "metadata": {}
        })

    return alerts

@router.get("/stats")
async def get_alerts_stats(case_id: Optional[str] = Query(None)):
    """Get alert statistics"""
    alerts = await get_alerts(case_id, 20)

    return {
        "total": len(alerts),
        "new": len([a for a in alerts if a["status"] == "NEW"]),
        "acknowledged": len([a for a in alerts if a["status"] == "ACKNOWLEDGED"]),
        "resolved": len([a for a in alerts if a["status"] == "RESOLVED"]),
        "escalated": len([a for a in alerts if a["status"] == "ESCALATED"]),
        "critical": len([a for a in alerts if a["severity"] == "CRITICAL"]),
        "high": len([a for a in alerts if a["severity"] == "HIGH"]),
        "medium": len([a for a in alerts if a["severity"] == "MEDIUM"]),
        "low": len([a for a in alerts if a["severity"] == "LOW"])
    }

@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """Get alert by ID"""
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

# ============================================================
# ALERT ACTIONS - SINGLE DEFINITION
# ============================================================

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    payload: AlertActionPayload | None = None
):
    """
    Acknowledge alert
    """
    return {
        "status": "success",
        "id": alert_id,
        "action": "ACKNOWLEDGED",
        "level": payload.level if payload else None,
        "reason": payload.reason if payload else None,
        "message": f"Alert {alert_id} acknowledged"
    }

@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    payload: AlertActionPayload | None = None
):
    """
    Resolve alert
    """
    return {
        "status": "success",
        "id": alert_id,
        "action": "RESOLVED",
        "reason": payload.reason if payload else None,
        "message": f"Alert {alert_id} resolved"
    }

@router.post("/{alert_id}/escalate")
async def escalate_alert(
    alert_id: str,
    payload: AlertActionPayload | None = None
):
    """
    Escalate alert
    """
    return {
        "status": "success",
        "id": alert_id,
        "action": "ESCALATED",
        "level": payload.level if payload else "HIGH",
        "reason": payload.reason if payload else None,
        "message": f"Alert {alert_id} escalated"
    }
