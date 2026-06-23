"""Evidence API Endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from evidence.service import EvidenceService
from evidence.registry import EvidenceStatus

router = APIRouter(prefix="/evidence", tags=["evidence"])

# ============================================================================
# Request/Response Models
# ============================================================================

class EvidenceCreateRequest(BaseModel):
    payload: Dict[str, Any]
    source: str
    actor: str = "api"

class EvidenceResponse(BaseModel):
    id: str
    hash: str
    created_at: datetime
    source: str
    payload: Dict[str, Any]
    status: str
    version: int
    previous_hash: Optional[str] = None

class CustodyEventRequest(BaseModel):
    action: str
    actor: str
    reason: Optional[str] = None

class CustodyEventResponse(BaseModel):
    action: str
    actor: str
    timestamp: datetime
    reason: Optional[str] = None

class VerifyResponse(BaseModel):
    verified: bool
    evidence_id: str
    message: str

# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=EvidenceResponse)
async def create_evidence(request: EvidenceCreateRequest):
    """Create new evidence record with hash and custody chain"""
    service = EvidenceService()
    evidence = service.create_evidence(request.payload, request.source, request.actor)
    return evidence


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(evidence_id: str):
    """Get evidence by ID"""
    service = EvidenceService()
    evidence = service.get_evidence(evidence_id)
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return evidence


@router.get("/{evidence_id}/verify", response_model=VerifyResponse)
async def verify_evidence(evidence_id: str):
    """Verify evidence integrity using hash chain"""
    service = EvidenceService()
    verified = service.verify_evidence(evidence_id)
    
    return VerifyResponse(
        verified=verified,
        evidence_id=evidence_id,
        message="Evidence integrity verified" if verified else "Evidence tampered or corrupted"
    )


@router.post("/{evidence_id}/custody", response_model=CustodyEventResponse)
async def add_custody_event(evidence_id: str, request: CustodyEventRequest):
    """Add custody chain event to evidence"""
    service = EvidenceService()
    evidence = service.add_custody_event(evidence_id, request.action, request.actor, request.reason)
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    custody_chain = service.get_custody_chain(evidence_id)
    if custody_chain:
        last_event = custody_chain[-1]
        return CustodyEventResponse(**last_event)
    
    raise HTTPException(status_code=500, detail="Failed to add custody event")


@router.get("/{evidence_id}/custody", response_model=List[CustodyEventResponse])
async def get_custody_chain(evidence_id: str):
    """Get full custody chain for evidence"""
    service = EvidenceService()
    chain = service.get_custody_chain(evidence_id)
    
    if chain is None:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return chain


@router.get("/{evidence_id}/hash")
async def get_evidence_hash(evidence_id: str):
    """Get evidence hash for deterministic verification"""
    service = EvidenceService()
    evidence = service.get_evidence(evidence_id)
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return {"evidence_id": evidence_id, "hash": evidence["hash"]}


@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """List all evidence with pagination"""
    service = EvidenceService()
    all_evidence = service.list_all_evidence()
    paginated = all_evidence[offset:offset + limit]
    return paginated


@router.post("/bulk")
async def bulk_create_evidence(items: List[EvidenceCreateRequest]):
    """Bulk create evidence records"""
    service = EvidenceService()
    results = []
    
    for item in items:
        evidence = service.create_evidence(item.payload, item.source, item.actor)
        results.append(evidence)
    
    return {
        "message": f"Created {len(results)} evidence records",
        "evidence_ids": [e["id"] for e in results]
    }


@router.get("/search")
async def search_evidence(
    source: Optional[str] = None,
    status: Optional[str] = None,
    days: int = Query(30, ge=1, le=365)
):
    """Search evidence by criteria"""
    service = EvidenceService()
    all_evidence = service.list_all_evidence()
    
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)
    
    filtered = []
    for e in all_evidence:
        created_at = datetime.fromisoformat(e["created_at"])
        if created_at < cutoff:
            continue
        if source and e["source"] != source:
            continue
        if status and e["status"] != status:
            continue
        filtered.append(e)
    
    return {
        "total": len(filtered),
        "results": filtered[:100]
    }
