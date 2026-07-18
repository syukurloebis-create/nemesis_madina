from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.infrastructure.database import get_db
from backend.services.finding_action_log_service import (
    FindingActionLogService
)

from pydantic import BaseModel
from typing import Optional


router = APIRouter(
    prefix="/findings",
    tags=["finding-actions"]
)


class ActionCreate(BaseModel):

    action_type: str
    description: Optional[str] = None
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    assignment_id: Optional[str] = None
    metadata: Optional[dict] = None



@router.post("/{finding_id}/actions")
async def create_action(
    finding_id: str,
    data: ActionCreate,
    db: AsyncSession = Depends(get_db),
):

    service = FindingActionLogService(db)

    action_id = await service.create_action(
        finding_id=finding_id,
        **data.model_dump()
    )

    return {
        "message": "Action recorded",
        "action_id": action_id
    }



@router.get("/{finding_id}/actions")
async def get_actions(
    finding_id: str,
    db: AsyncSession = Depends(get_db),
):

    service = FindingActionLogService(db)

    return await service.get_actions(
        finding_id
    )