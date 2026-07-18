from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db

from backend.services.dashboard_intelligence_analytics_service import (
    dashboard_intelligence_analytics_service,
)

router = APIRouter(
    prefix="/dashboard/intelligence",
    tags=["Dashboard Intelligence Analytics"]
)


@router.get("/risk-distribution")
async def risk_distribution(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_risk_distribution(db)
    )


@router.get("/intelligence-types")
async def intelligence_types(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_intelligence_type_distribution(db)
    )


@router.get("/evidence-health")
async def evidence_health(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_evidence_health(db)
    )
