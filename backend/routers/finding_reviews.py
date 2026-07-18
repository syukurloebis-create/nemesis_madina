from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.database import get_db
from backend.services.finding_review_service import (
    FindingReviewService
)

from pydantic import BaseModel


router = APIRouter(
    prefix="/findings",
    tags=["finding-review"]
)



class DecisionRequest(BaseModel):

    decision: str

    rationale: str

    confidence_score: float | None = None

    decided_by: str

    assignment_id: str | None = None




@router.post("/{finding_id}/decision")
async def create_decision(
    finding_id: str,
    data: DecisionRequest,
    db: AsyncSession = Depends(get_db),
):

    service = FindingReviewService(
        db
    )


    return await service.create_decision(
        finding_id=finding_id,
        **data.model_dump()
    )



@router.get("/{finding_id}/decisions")
async def get_decisions(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):

    service = FindingReviewService(
        db
    )

    return await service.get_history(
        finding_id
    )