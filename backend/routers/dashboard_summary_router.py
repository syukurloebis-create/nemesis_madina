from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db

from backend.services.dashboard_intelligence_analytics_service import (
    dashboard_intelligence_analytics_service,
)

router = APIRouter(
    prefix="/dashboard/intelligence",
    tags=["Dashboard Intelligence"]
)


@router.get("/summary")
async def summary(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_dashboard_summary(db)
    )


@router.get("/overview")
async def overview(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_overview(db)
    )


@router.get("/kpi")
async def kpi(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_dashboard_kpi(db)
    )


@router.get("/status")
async def status(
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_dashboard_status(db)
    )


@router.get("/entities/top-risk")
async def top_risk(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_top_risk_entities(
            db,
            limit
        )
    )

# routers/dashboard_summary_router.py

@router.post("/refresh")
async def refresh_intelligence_cache(
    db: AsyncSession = Depends(get_db)
):
    """Refresh intelligence cache"""
    result = await dashboard_intelligence_analytics_service.refresh_cache(db)
    return result