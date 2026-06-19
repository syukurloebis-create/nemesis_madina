"""Evidence API Endpoints (V8+ FIXED)"""

from fastapi import APIRouter, HTTPException
from backend.evidence.service import EvidenceService
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(tags=["evidence"])

# ======================
# SCHEMA
# ======================
class EvidenceCreate(BaseModel):
    payload: Dict[str, Any]
    source: str
    actor: str = "api"


# ======================
# CREATE EVIDENCE
# ======================
@router.post("/")
async def create_evidence(data: EvidenceCreate):
    service = EvidenceService()
    return service.create_evidence(
        data.payload,
        data.source,
        data.actor
    )


# ======================
# LIST EVIDENCE (FIX #1)
# ======================
@router.get("/")
async def list_evidence():
    service = EvidenceService()
    return service.list_evidence()


# ======================
# GET BY ID
# ======================
@router.get("/{evidence_id}")
async def get_evidence(evidence_id: str):
    service = EvidenceService()
    result = service.get_evidence(evidence_id)

    if not result:
        raise HTTPException(status_code=404, detail="Evidence not found")

    return result


# ======================
# VERIFY EVIDENCE
# ======================
@router.get("/{evidence_id}/verify")
async def verify_evidence(evidence_id: str):
    service = EvidenceService()
    return {
        "evidence_id": evidence_id,
        "verified": service.verify_evidence(evidence_id)
    }

@router.get("/")
async def list_cases():
    return service.list_cases()