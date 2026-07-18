"""
Dashboard Intelligence Router — Registrasi endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from uuid import UUID
import logging

from backend.services.dashboard_intelligence_service import DashboardIntelligenceService
from backend.domain.models.case_intelligence import CaseIntelligence

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/dashboard/intelligence"
)

def get_dashboard_service(request: Request) -> DashboardIntelligenceService:
    """Get Dashboard Service from container."""
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise HTTPException(503, "Container not initialized")
    return container.services.dashboard


@router.get("/{case_id}", response_model=CaseIntelligence)
async def get_dashboard_intelligence(
    case_id: UUID,
    request: Request,
    service: DashboardIntelligenceService = Depends(get_dashboard_service)
) -> CaseIntelligence:
    """
    Get Dashboard Intelligence for a case.
    
    ✅ Endpoint yang benar: /api/v1/dashboard/intelligence/{case_id}
    """
    logger.error("========== ROUTER HIT ==========")
    logger.error("router file = %s", __file__)
    logger.error("case_id = %s", case_id)
    logger.info("Dashboard Intelligence request for case: %s", case_id)
    
    try:
        result = await service.get_case_intelligence(case_id)
        return result
    except Exception as e:
        logger.exception("Dashboard Intelligence failed for case %s: %s", case_id, e)
        raise HTTPException(500, detail=str(e))

def get_dashboard_service(request: Request) -> DashboardIntelligenceService:
    container = request.app.state.container
    logger.error("🚨🚨🚨 Router: container.services.dashboard = %s", container.services.dashboard)
    logger.error("🚨🚨🚨 Router: container type = %s", type(container))
    return container.services.dashboard