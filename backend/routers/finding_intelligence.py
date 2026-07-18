from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.database import get_db

from backend.services.finding_intelligence_service import (
    FindingIntelligenceService
)


router = APIRouter(
    prefix="/findings",
    tags=["Finding Intelligence"]
)


@router.get("/{finding_id}/intelligence")
async def finding_intelligence(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):

    service = FindingIntelligenceService()

    return await service.get_intelligence(
        finding_id,
        db
    )