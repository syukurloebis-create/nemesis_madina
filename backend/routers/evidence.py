"""
Evidence Router - Evidence management endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.services.evidence_service import EvidenceService

router = APIRouter(
    prefix="/evidence",
    tags=["evidence"],
)


def get_evidence_service(
    db: AsyncSession = Depends(get_db),
) -> EvidenceService:
    """Provider for EvidenceService."""
    return EvidenceService(db)


@router.get("/{case_id}")
async def get_evidence(
    case_id: str,
    service: EvidenceService = Depends(get_evidence_service),
):
    """Get evidence for a case."""
    return await service.list_evidence(case_id)


@router.get("/stats")
async def get_evidence_stats():
    """Get evidence statistics."""
    return {
        "total": 28,
        "verified": 10,
        "pending": 8,
        "rejected": 10,
        "avg_trust_score": 74.07,
    }