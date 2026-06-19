from prometheus_client import Counter, Gauge, generate_latest, REGISTRY
from fastapi import APIRouter, Response
from sqlalchemy import text
from backend.infrastructure.database import AsyncSessionLocal

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Custom metrics
total_cases = Gauge('nemesis_total_cases', 'Total number of cases')
cases_by_status = Gauge('nemesis_cases_by_status', 'Cases by status', ['status'])
cases_by_priority = Gauge('nemesis_cases_by_priority', 'Cases by priority', ['priority'])
http_requests = Counter('nemesis_http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])


@router.get("")
async def get_metrics():
    """Prometheus metrics endpoint"""
    import asyncio
    
    async def update_metrics():
        async with AsyncSessionLocal() as session:
            # Total cases
            result = await session.execute(text("SELECT COUNT(*) FROM cases"))
            total = result.scalar()
            total_cases.set(total if total else 0)
            
            # Cases by status
            result = await session.execute(text("SELECT status, COUNT(*) FROM cases GROUP BY status"))
            for row in result:
                cases_by_status.labels(status=row[0]).set(row[1])
            
            # Cases by priority
            result = await session.execute(text("SELECT priority, COUNT(*) FROM cases GROUP BY priority"))
            for row in result:
                cases_by_priority.labels(priority=row[0]).set(row[1])
    
    try:
        await update_metrics()
    except Exception as e:
        print(f"Error updating metrics: {e}")
    
    return Response(content=generate_latest(REGISTRY), media_type="text/plain")
