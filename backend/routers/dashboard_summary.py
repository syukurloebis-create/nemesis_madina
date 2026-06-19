from fastapi import APIRouter, Request
from backend.core.analytics.risk_engine import RiskEngine

router = APIRouter()

@router.get("/api/dashboard/summary")
async def dashboard_summary():

    pool = await create_pool()

    async with pool.acquire() as conn:

        total_events = await conn.fetchval(
            "SELECT COUNT(*) FROM event_lineage"
        )

        total_aggregates = await conn.fetchval(
            """
            SELECT COUNT(DISTINCT aggregate_id)
            FROM event_lineage
            """
        )

        broken = 0

    integrity_rate = 100

    return {
        "status": "ok",

        "total_events":
            total_events,

        "total_aggregates":
            total_aggregates,

        "integrity_rate":
            integrity_rate,

        "broken_chains":
            broken
    }
