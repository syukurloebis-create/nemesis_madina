from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import uuid
import json
from datetime import datetime

from backend.database import get_db

# Buat router
router = APIRouter(prefix="/workflow", tags=["workflow"])


# ============================================================
# WORKFLOW STAGES
# ============================================================

WORKFLOW_STAGES = {
    "REPORTED": {"order": 1, "name": "Dilaporkan", "next": ["SCREENING", "CLOSED"]},
    "SCREENING": {"order": 2, "name": "Screening", "next": ["ASSESSMENT", "CLOSED"]},
    "ASSESSMENT": {"order": 3, "name": "Assessment", "next": ["INVESTIGATION", "CLOSED"]},
    "INVESTIGATION": {"order": 4, "name": "Investigasi", "next": ["FINDING", "CLOSED"]},
    "FINDING": {"order": 5, "name": "Temuan", "next": ["RECOMMENDATION"]},
    "RECOMMENDATION": {"order": 6, "name": "Rekomendasi", "next": ["FOLLOW_UP"]},
    "FOLLOW_UP": {"order": 7, "name": "Tindak Lanjut", "next": ["CLOSED"]},
    "CLOSED": {"order": 8, "name": "Ditutup", "next": []}
}


class StageTransition(BaseModel):
    case_id: str
    target_stage: str
    notes: Optional[str] = None


class FindingCreate(BaseModel):
    case_id: str
    finding_type: str
    severity: str
    description: str
    evidence_ids: Optional[List[str]] = None


class RecommendationCreate(BaseModel):
    finding_id: str
    recommendation_type: str
    target_entity: Optional[str]
    description: str
    due_date: Optional[str]
    priority: str = "MEDIUM"


# ============================================================
# WORKFLOW ENDPOINTS
# ============================================================

@router.get("/stages")
async def get_workflow_stages() -> Dict[str, Any]:
    """Get all workflow stages"""
    return {
        "stages": WORKFLOW_STAGES,
        "stage_list": list(WORKFLOW_STAGES.keys())
    }


@router.get("/case/{case_id}/stage")
async def get_case_stage(
    case_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get current workflow stage for a case"""
    try:
        result = await db.execute(
            text("""
                SELECT workflow_stage, assigned_to, assigned_at,
                       investigation_started_at, investigation_completed_at
                FROM cases WHERE id = :case_id
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        current_stage = row[0] or "REPORTED"
        stage_info = WORKFLOW_STAGES.get(current_stage, {})
        
        return {
            "case_id": case_id,
            "current_stage": current_stage,
            "stage_name": stage_info.get("name", current_stage),
            "stage_order": stage_info.get("order", 0),
            "available_transitions": stage_info.get("next", []),
            "assigned_to": str(row[1]) if row[1] else None,
            "assigned_at": row[2].isoformat() if row[2] else None,
            "investigation_started_at": row[3].isoformat() if row[3] else None,
            "investigation_completed_at": row[4].isoformat() if row[4] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@router.post("/case/transition")
async def transition_stage(
    transition: StageTransition,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Transition case to next workflow stage"""
    try:
        result = await db.execute(
            text("SELECT workflow_stage FROM cases WHERE id = :case_id"),
            {"case_id": transition.case_id}
        )
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        current_stage = row[0] or "REPORTED"
        stage_info = WORKFLOW_STAGES.get(current_stage, {})
        
        if transition.target_stage not in stage_info.get("next", []):
            return {
                "success": False,
                "error": f"Invalid transition from {current_stage} to {transition.target_stage}"
            }
        
        await db.execute(
            text("""
                UPDATE cases 
                SET workflow_stage = :target_stage,
                    updated_at = NOW()
                WHERE id = :case_id
            """),
            {"target_stage": transition.target_stage, "case_id": transition.case_id}
        )
        
        await db.execute(
            text("""
                INSERT INTO investigation_timeline (case_id, stage, from_stage, notes, created_at)
                VALUES (:case_id, :stage, :from_stage, :notes, NOW())
            """),
            {
                "case_id": transition.case_id,
                "stage": transition.target_stage,
                "from_stage": current_stage,
                "notes": transition.notes
            }
        )
        
        await db.commit()
        
        return {
            "success": True,
            "case_id": transition.case_id,
            "from_stage": current_stage,
            "to_stage": transition.target_stage,
            "message": f"Case transitioned from {current_stage} to {transition.target_stage}"
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/case/{case_id}/timeline")
async def get_investigation_timeline(
    case_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get full investigation timeline for a case"""
    try:
        result = await db.execute(
            text("""
                SELECT stage, from_stage, notes, created_at
                FROM investigation_timeline
                WHERE case_id = :case_id
                ORDER BY created_at ASC
            """),
            {"case_id": case_id}
        )
        rows = result.fetchall()
        
        timeline = []
        for row in rows:
            timeline.append({
                "stage": row[0],
                "stage_name": WORKFLOW_STAGES.get(row[0], {}).get("name", row[0]),
                "from_stage": row[1],
                "notes": row[2],
                "timestamp": row[3].isoformat() if row[3] else None
            })
        
        return {
            "case_id": case_id,
            "timeline": timeline,
            "total_events": len(timeline)
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/finding/create")
async def create_finding(
    finding: FindingCreate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new finding for a case"""
    try:
        finding_id = uuid.uuid4()
        
        evidence_json = json.dumps(finding.evidence_ids or [])
        
        await db.execute(
            text("""
                INSERT INTO investigation_findings (id, case_id, finding_type, severity, description, evidence_ids, status, created_at)
                VALUES (:id, :case_id, :type, :severity, :desc, CAST(:evidence AS JSONB), 'DRAFT', NOW())
            """),
            {
                "id": finding_id,
                "case_id": finding.case_id,
                "type": finding.finding_type,
                "severity": finding.severity,
                "desc": finding.description,
                "evidence": evidence_json
            }
        )
        
        await db.commit()
        
        return {
            "success": True,
            "finding_id": str(finding_id),
            "message": "Finding created successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/finding/case/{case_id}")
async def get_case_findings(
    case_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get all findings for a case"""
    try:
        result = await db.execute(
            text("""
                SELECT id, finding_type, severity, description, status, created_at
                FROM investigation_findings
                WHERE case_id = :case_id
                ORDER BY created_at DESC
            """),
            {"case_id": case_id}
        )
        rows = result.fetchall()
        
        findings = []
        for row in rows:
            findings.append({
                "id": str(row[0]),
                "finding_type": row[1],
                "severity": row[2],
                "description": row[3],
                "status": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            })
        
        return {
            "case_id": case_id,
            "findings": findings,
            "total": len(findings)
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/dashboard/summary")
async def get_workflow_dashboard(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get workflow summary dashboard"""
    try:
        stage_result = await db.execute(
            text("""
                SELECT 
                    COALESCE(workflow_stage, 'REPORTED') as stage,
                    COUNT(*) as count
                FROM cases
                GROUP BY workflow_stage
                ORDER BY MIN(CASE 
                    WHEN workflow_stage = 'REPORTED' THEN 1
                    WHEN workflow_stage = 'SCREENING' THEN 2
                    WHEN workflow_stage = 'ASSESSMENT' THEN 3
                    WHEN workflow_stage = 'INVESTIGATION' THEN 4
                    WHEN workflow_stage = 'FINDING' THEN 5
                    WHEN workflow_stage = 'RECOMMENDATION' THEN 6
                    WHEN workflow_stage = 'FOLLOW_UP' THEN 7
                    WHEN workflow_stage = 'CLOSED' THEN 8
                    ELSE 9
                END)
            """)
        )
        stage_rows = stage_result.fetchall()
        
        stage_counts = {}
        for row in stage_rows:
            stage_name = WORKFLOW_STAGES.get(row[0], {}).get("name", row[0])
            stage_counts[row[0]] = {
                "count": row[1],
                "display_name": stage_name
            }
        
        pending_findings = await db.execute(
            text("SELECT COUNT(*) FROM investigation_findings WHERE status = 'DRAFT'")
        )
        pending_findings_count = pending_findings.scalar() or 0
        
        active_count = await db.execute(
            text("SELECT COUNT(*) FROM cases WHERE workflow_stage NOT IN ('CLOSED')")
        )
        active_investigations = active_count.scalar() or 0
        
        return {
            "stage_distribution": stage_counts,
            "pending_approvals": pending_findings_count,
            "active_investigations": active_investigations,
            "total_cases": sum(s["count"] for s in stage_counts.values())
        }
    except Exception as e:
        return {"error": str(e)}
