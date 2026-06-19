"""Evidence API Endpoints"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from typing import List, Optional
from uuid import UUID

from backend.evidence.services.evidence_service import EvidenceService
from backend.evidence.models import Evidence, EvidenceVerification, CustodyRecord, SourceSystem, EvidenceType

router = APIRouter(prefix="/evidence", tags=["evidence"])


@router.post("/upload", response_model=Evidence, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    file: UploadFile = File(...),
    source_system: SourceSystem = Form(...),
    source_type: EvidenceType = Form(...),
    source_uri: Optional[str] = Form(None),
    uploaded_by: str = Form("system"),
    service: EvidenceService = Depends(get_evidence_service)
):
    """Upload new evidence file"""
    content = await file.read()
    
    evidence = await service.upload_evidence(
        content=content,
        filename=file.filename,
        source_system=source_system,
        source_type=source_type,
        uploaded_by=uploaded_by,
        source_uri=source_uri
    )
    
    return evidence


@router.post("/{evidence_id}/verify", response_model=EvidenceVerification)
async def verify_evidence(
    evidence_id: UUID,
    file: UploadFile = File(...),
    verified_by: str = Form("system"),
    service: EvidenceService = Depends(get_evidence_service)
):
    """Verify evidence integrity"""
    content = await file.read()
    
    result = await service.verify_evidence(evidence_id, content, verified_by)
    return result


@router.get("/{evidence_id}", response_model=Evidence)
async def get_evidence(
    evidence_id: UUID,
    service: EvidenceService = Depends(get_evidence_service)
):
    """Get evidence by ID"""
    evidence = await service.get_evidence(evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.get("/{evidence_id}/custody", response_model=List[CustodyRecord])
async def get_custody_chain(
    evidence_id: UUID,
    service: EvidenceService = Depends(get_evidence_service)
):
    """Get chain of custody for evidence"""
    chain = await service.get_custody_chain(evidence_id)
    return chain


@router.get("/", response_model=List[Evidence])
async def list_evidence(
    limit: int = 100,
    offset: int = 0,
    source_system: Optional[str] = None,
    service: EvidenceService = Depends(get_evidence_service)
):
    """List evidence"""
    return await service.list_evidence(limit, offset, source_system)


@router.get("/statistics/summary")
async def get_evidence_statistics(
    service: EvidenceService = Depends(get_evidence_service)
):
    """Get evidence statistics"""
    return await service.get_statistics()


# Dependency
async def get_evidence_service() -> EvidenceService:
    from backend.infrastructure.database import get_pool
    from backend.evidence.repositories.evidence_repo import EvidenceRepository
    from backend.evidence.repositories.custody_repo import CustodyRepository
    
    pool = await get_pool()
    evidence_repo = EvidenceRepository(pool)
    custody_repo = CustodyRepository(pool)
    return EvidenceService(evidence_repo, custody_repo)
