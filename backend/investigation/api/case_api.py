"""Investigation Case API Endpoints - Simplified"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from uuid import UUID

from investigation.services.case_service import InvestigationCaseService
from investigation.repositories.case_repo import InvestigationCaseRepository, FindingRepository
from investigation.models import InvestigationCase, InvestigationCaseCreate, Finding, FindingCreate

router = APIRouter(prefix="/cases", tags=["investigation-cases"])


async def get_case_service():
    from backend.infrastructure.database import get_pool
    pool = await get_pool()
    case_repo = InvestigationCaseRepository(pool)
    finding_repo = FindingRepository(pool)
    return InvestigationCaseService(case_repo, finding_repo)


@router.post("/", response_model=InvestigationCase)
async def create_case(
    case_data: InvestigationCaseCreate,
    service: InvestigationCaseService = Depends(get_case_service)
):
    return await service.create_case(case_data)


@router.get("/{case_id}", response_model=InvestigationCase)
async def get_case(                                    # ← FIXED
    case_id: UUID,
    service: InvestigationCaseService = Depends(get_case_service)
):
    case = await service.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/", response_model=List[InvestigationCase])
async def list_cases(
    limit: int = 100,
    offset: int = 0,
    service: InvestigationCaseService = Depends(get_case_service)
):
    return await service.list_cases(limit, offset)


@router.post("/{case_id}/findings", response_model=Finding)
async def add_finding(
    case_id: UUID,
    finding_data: FindingCreate,
    service: InvestigationCaseService = Depends(get_case_service)
):
    finding_data.case_id = case_id
    finding = await service.add_finding(finding_data)
    if not finding:
        raise HTTPException(status_code=404, detail="Case not found")
    return finding


@router.get("/{case_id}/findings", response_model=List[Finding])
async def get_case_findings(
    case_id: UUID,
    service: InvestigationCaseService = Depends(get_case_service)
):
    return await service.get_case_findings(case_id)


@router.get("/statistics/summary")
async def get_case_statistics(
    service: InvestigationCaseService = Depends(get_case_service)
):
    return await service.get_statistics()
