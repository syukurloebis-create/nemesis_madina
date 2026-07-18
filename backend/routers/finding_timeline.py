from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from backend.infrastructure.database import get_db
from backend.services.finding_timeline_service import (
    FindingTimelineService
)


router = APIRouter(
    prefix="/findings",
    tags=["finding-timeline"]
)



@router.get("/{finding_id}/timeline")
async def get_finding_timeline(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):

    service = FindingTimelineService(db)


    return await service.get_timeline(
        finding_id
    )