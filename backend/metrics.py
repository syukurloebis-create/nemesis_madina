"""
Prometheus metrics exporter untuk Nemesis Madina V8
Menyediakan semua metric untuk dashboard lengkap
"""
from prometheus_client import Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response, Request
from sqlalchemy import select, func
import logging
import time

from backend.infrastructure.database import AsyncSessionLocal
from backend.cases.models import Case

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["metrics"])

# ============================================
# METRIC DEFINITIONS
# ============================================

# Core metrics
total_cases_gauge = Gauge("nemesis_total_cases", "Total cases in system")
cases_by_priority_gauge = Gauge("nemesis_cases_by_priority", "Cases grouped by priority", ["priority"])
cases_by_status_gauge = Gauge("nemesis_cases_by_status", "Cases grouped by status", ["status"])

# HTTP metrics (akan diupdate via middleware)
http_request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "status"]
)

# Health metrics
api_health_gauge = Gauge("nemesis_api_health", "API instance health status", ["instance"])


# ============================================
# METRICS UPDATE FUNCTION
# ============================================

async def update_metrics():
    """Update all metrics from database"""
    try:
        async with AsyncSessionLocal() as session:
            # 1. Total cases
            result = await session.execute(select(func.count()).select_from(Case))
            total = result.scalar() or 0
            total_cases_gauge.set(total)
            logger.debug(f"Updated nemesis_total_cases: {total}")
            
            # 2. Cases by priority
            priority_result = await session.execute(
                select(Case.priority, func.count())
                .group_by(Case.priority)
            )
            # Reset all priority metrics first
            for priority in ["critical", "high", "medium", "low", "none"]:
                cases_by_priority_gauge.labels(priority=priority).set(0)
            # Set actual values
            for priority, count in priority_result.all():
                prio = priority if priority else "none"
                cases_by_priority_gauge.labels(priority=prio).set(count)
                logger.debug(f"Updated priority {prio}: {count}")
            
            # 3. Cases by status
            status_result = await session.execute(
                select(Case.status, func.count())
                .group_by(Case.status)
            )
            # Reset all status metrics first
            for status in ["draft", "open", "investigating", "verifying", "resolved", "closed"]:
                cases_by_status_gauge.labels(status=status).set(0)
            # Set actual values
            for status, count in status_result.all():
                stat = status if status else "unknown"
                cases_by_status_gauge.labels(status=stat).set(count)
                logger.debug(f"Updated status {stat}: {count}")
                
    except Exception as e:
        logger.error(f"Failed to update metrics: {e}")


# ============================================
# METRICS ENDPOINT
# ============================================

@router.get("")
async def metrics_endpoint():
    """Prometheus metrics endpoint - called by Grafana"""
    await update_metrics()
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ============================================
# HEALTH CHECK ENDPOINT
# ============================================

@router.get("/health")
async def metrics_health():
    """Health check for metrics endpoint"""
    return {"status": "healthy", "metrics": "operational"}
