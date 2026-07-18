from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.infrastructure.database import get_db
from backend.finding.models import Finding
from backend.finding.service import (
    FindingService,
    AnomalyScoringService
)
from backend.services.finding_assignment_service import (
    FindingAssignmentService
)
from backend.security.auth import decode_token
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/findings", tags=["findings"])

class FindingCreate(BaseModel):
    case_id: str
    title: str
    description: str
    evidence_ids: List[str]
    financial_loss: Optional[float] = None

class FindingTransitionRequest(BaseModel):
    status: str
    notes: Optional[str] = None

class AnomalyRequest(BaseModel):
    evidence_ids: List[str]

class FindingAssignmentRequest(BaseModel):
    analyst_id: Optional[str] = None
    analyst_name: str
    role: Optional[str] = None
    assigned_by: str
    notes: Optional[str] = None


def get_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None, None
    token = auth_header[7:]
    payload = decode_token(token)
    if not payload:
        return None, None
    return payload.get("institution_id"), payload.get("sub")


@router.post("/create-from-evidence")
async def create_finding_from_evidence(
    finding_data: FindingCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    institution_id, user_id = get_user_info(request)
    
    try:
        finding = await FindingService.create_finding_from_evidence(
            session=db,
            case_id=finding_data.case_id,
            evidence_ids=finding_data.evidence_ids,
            title=finding_data.title,
            description=finding_data.description,
            financial_loss=finding_data.financial_loss,
            created_by=user_id,
            institution_id=institution_id  # ← KIRIMKAN institution_id
        )
        
        await db.commit()
        
        return {
            "id": finding.id,
            "title": finding.title,
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "anomaly_score": finding.anomaly_score,
            "risk_score": finding.risk_score,
            "message": "Finding created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating finding: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/case/{case_id}")
async def get_findings_by_case(
    case_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        findings = await FindingService.get_findings_by_case(db, case_id)
        
        return [
            {
                "id": f.id,
                "title": f.title,
                "description": f.description[:200] if f.description else "",
                "finding_type": f.finding_type,
                "severity": f.severity,
                "status": f.status,
                "anomaly_score": f.anomaly_score,
                "risk_score": f.risk_score,
                "evidence_count": len(f.evidence_ids) if f.evidence_ids else 0,
                "created_at": f.created_at.isoformat() if f.created_at else None
            }
            for f in findings
        ]
    except Exception as e:
        logger.error(f"Error getting findings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/summary")
async def get_findings_summary(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Finding))
        findings = result.scalars().all()
        
        severity_counts = {}
        status_counts = {}
        total_risk = 0
        
        for f in findings:
            sev = f.severity or "unknown"
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            status_counts[f.status] = status_counts.get(f.status, 0) + 1
            total_risk += f.risk_score or 0
        
        avg_risk = total_risk / len(findings) if findings else 0
        
        return {
            "total_findings": len(findings),
            "severity_distribution": severity_counts,
            "status_distribution": status_counts,
            "average_risk_score": round(avg_risk, 2)
        }
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{finding_id}/transition")
async def transition_finding(
    finding_id: str,
    request: FindingTransitionRequest,
    db: AsyncSession = Depends(get_db)
):

    from backend.services.finding_lifecycle_service import (
        FindingLifecycleService
    )


    service = FindingLifecycleService(db)


    try:

        await service.transition(
            finding_id=finding_id,
            new_status=request.status,
            actor="case_manager",
            notes=request.notes
        )


        return {
            "message":
                "Finding status updated",

            "finding_id":
                finding_id,

            "new_status":
                request.status
        }


    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/{finding_id}/assign")
async def assign_finding(
    finding_id: str,
    data: FindingAssignmentRequest,
    db: AsyncSession = Depends(get_db)
):

    try:

        service = FindingAssignmentService(db)

        result = await service.assign(
            finding_id=finding_id,
            analyst_id=data.analyst_id,
            analyst_name=data.analyst_name,
            assigned_by=data.assigned_by,
            role=data.role,
            notes=data.notes,
        )


        return {
            "message": "Finding assigned successfully",
            **result
        }


    except Exception as e:

        logger.error(
            f"Assignment error: {e}"
        )

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.get("/{finding_id}/assignments")
async def get_finding_assignments(
    finding_id: str,
    db: AsyncSession = Depends(get_db)
):

    try:

        service = FindingAssignmentService(db)

        return await service.get_assignments(
            finding_id
        )


    except Exception as e:

        logger.error(
            f"Get assignment error: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/anomaly/calculate")
async def calculate_anomaly(
    request: AnomalyRequest,
    db: AsyncSession = Depends(get_db)
):
    anomaly_score = AnomalyScoringService.calculate_anomaly_score(request.evidence_ids)
    severity = AnomalyScoringService.determine_severity(anomaly_score)
    finding_type = AnomalyScoringService.determine_finding_type("")
    
    return {
        "anomaly_score": anomaly_score,
        "severity": severity,
        "suggested_finding_type": finding_type,
        "risk_score": anomaly_score * 100
    }
