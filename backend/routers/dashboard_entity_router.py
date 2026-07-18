from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db

from backend.services.dashboard_intelligence_analytics_service import (
    dashboard_intelligence_analytics_service,
)

router = APIRouter(
    prefix="/dashboard/intelligence",
    tags=["Dashboard Entity Intelligence"]
)


@router.get("/entities/{entity_name}/history")
async def history(
    entity_name: str,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_entity_history(
            entity_name,
            db
        )
    )


@router.get("/entities/{entity_name}/network-summary")
async def network_summary(
    entity_name: str,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_network_summary(
            entity_name,
            db
        )
    )


@router.get("/entities/{entity_name}/network")
async def network(
    entity_name: str,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .get_entity_network(
            entity_name,
            db
        )
    )


@router.get("/entities/{entity_name}/explain")
async def explain(
    entity_name: str,
    db: AsyncSession = Depends(get_db)
):
    return await (
        dashboard_intelligence_analytics_service
        .explain_entity(
            entity_name,
            db
        )
    )