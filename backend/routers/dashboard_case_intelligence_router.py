"""
Dashboard Case Intelligence Router.
"""

from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.domain.models.case_intelligence import CaseIntelligence
from backend.services.interfaces import IDashboardService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_dashboard_service(request: Request) -> IDashboardService:
    """
    Resolve Dashboard Service dari ApplicationContainer.
    """
    return request.app.state.container.services.dashboard


@router.get(
    "/intelligence/{case_id}",
    response_model=CaseIntelligence,
)
async def get_case_intelligence(
    case_id: UUID,
    service: IDashboardService = Depends(get_dashboard_service),
) -> CaseIntelligence:
    try:
        return await service.get_case_intelligence(case_id)

    except Exception:
        logger.exception(
            "Failed to generate dashboard intelligence for %s",
            case_id,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate dashboard intelligence",
        )