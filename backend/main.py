"""NEMESIS V8+ - Main Application"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if (sys.platform == "win32" and "pytest" not in sys.modules and hasattr(sys.stdout, "buffer")):
    import io
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        line_buffering=True,
    )

from backend.core.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

from backend.core.version import VersionInfo
from backend.infrastructure.sql_repository import SQLRepository
from backend.middleware.request_id_middleware import RequestIDMiddleware
from backend.middleware.canonical_tenant import CanonicalTenantMiddleware
from backend.config import settings

# Routers
from backend.routers.finding import router as finding_router
from backend.routers import finding_actions, finding_assignments, finding_intelligence, finding_reviews, finding_timeline
from backend.routers.export import router as export_router
from backend.routers.dashboard_intelligence import router as dashboard_intelligence_router
from backend.routers.dashboard_summary_router import router as dashboard_summary_router
from backend.routers.intelligence import router as intelligence_router
from backend.api.metrics import router as metrics_router
from backend.routers.auth_router import router as auth_router
from backend.routers.alerts import router as alerts_router
from backend.routers.cases import router as cases_router
from backend.routers.cases_list import router as cases_list_router
from backend.routers.decisions import router as decisions_router
from backend.routers.evidence import router as evidence_router
from backend.routers.fraud import router as fraud_router
from backend.routers.fraud_detail_router import router as fraud_detail_router
from backend.routers.investigation import router as investigation_router
from backend.routers.procurement import router as procurement_router
from backend.routers.recommendations import router as recommendations_router
from backend.routers.risk import router as risk_router
from backend.routers.vendors import router as vendors_router
from backend.routers.historical import router as historical_router
from backend.routers.snapshot import router as snapshot_router
from backend.routers.graph import router as graph_router
from backend.routers.graph_trigger import router as graph_trigger_router
from backend.trust_metrics import router as trust_metrics_router
from backend.risk_metrics import router as risk_metrics_router

ENABLE_LEGACY_HEALTH_ROUTER = os.getenv("ENABLE_LEGACY_HEALTH_ROUTER", "false").lower() == "true"
if ENABLE_LEGACY_HEALTH_ROUTER:
    from backend.routers.health_intelligence import router as health_intelligence_router
    logger.info("Legacy Health Intelligence Router: ENABLED")
else:
    logger.info("Legacy Health Intelligence Router: DISABLED")

@asynccontextmanager
async def lifespan(app: FastAPI):
    from backend.bootstrap.container_builder import build_application_container
    from backend.bootstrap.functions import bootstrap_infrastructure
    from backend.bootstrap.validator import ContainerValidator

    logger.info("=" * 50)
    logger.info("NEMESIS MADINA V8+ Starting...")
    logger.info("=" * 50)

    engine = None

    try:
        result = bootstrap_infrastructure()
        infra = result.infrastructure
        engine = result.engine
        logger.info("Infrastructure bootstrapped")

        container = build_application_container(infra)
        logger.info("Application container built")

        ContainerValidator.validate(container)
        logger.info("Container validation passed")

        app.state.container = container

        logger.info("=" * 50)
        logger.info("NEMESIS MADINA V8+ Startup Complete")
        logger.info("=" * 50)

        yield

    except Exception as e:
        logger.error("Startup failed: %s", e)
        raise
    finally:
        logger.info("NEMESIS MADINA V8+ Shutting down...")
        if engine:
            await engine.dispose()
            logger.info("AsyncEngine disposed")
        logger.info("Shutdown complete")

app = FastAPI(
    title="NEMESIS Intelligence API",
    description="NEMESIS V8+ - Autonomous Risk Intelligence Platform",
    version="8.0.0",
    lifespan=lifespan,
)

# ============================================================
# CORS MIDDLEWARE - UPDATED WITH PRODUCTION ORIGINS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Dev
        "http://127.0.0.1:5173",   # Dev (alt)
        "http://localhost:3000",   # Dev (alt)
        "http://localhost",        # Production via Nginx ✅
        "http://127.0.0.1",        # Production (alt)
        "http://localhost:8000",   # Backend itself
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)

app.add_middleware(RequestIDMiddleware)

secret_key = settings.auth.secret_key if hasattr(settings, 'auth') else "dev-secret-key-change-in-production"
logger.info(f"Using secret key: {secret_key[:10]}...")

app.add_middleware(
    CanonicalTenantMiddleware,
    secret_key=secret_key,
)

# ============================================================
# ROUTERS
# ============================================================
logger.info("=" * 50)
logger.info("Registering Routers...")
logger.info("=" * 50)

app.include_router(finding_router)
app.include_router(finding_assignments.router)
app.include_router(finding_actions.router)
app.include_router(finding_reviews.router)
app.include_router(finding_timeline.router)
app.include_router(finding_intelligence.router)
logger.info("[OK] Finding routers registered")

app.include_router(decisions_router, prefix="/api/v1", tags=["Decisions"])
app.include_router(cases_router, prefix="/api/v1/cases", tags=["Cases"])
logger.info("[OK] Cases router registered at /api/v1/cases")

app.include_router(fraud_router, prefix="/api/v1/fraud", tags=["Fraud"])
logger.info("[OK] Fraud router registered at /api/v1/fraud")

app.include_router(fraud_detail_router, prefix="/api/v1/fraud", tags=["Fraud Detail"])
logger.info("[OK] Fraud Detail router registered")

app.include_router(risk_router, prefix="/api/v1/risk", tags=["Risk"])
logger.info("[OK] Risk router registered at /api/v1/risk")

app.include_router(procurement_router, prefix="/api/v1/procurement", tags=["Procurement"])
logger.info("[OK] Procurement router registered at /api/v1/procurement")

app.include_router(evidence_router, prefix="/api/v1/evidence", tags=["Evidence"])
logger.info("[OK] Evidence router registered at /api/v1/evidence")

app.include_router(investigation_router, prefix="/api/v1/investigation", tags=["Investigation"])
logger.info("[OK] Investigation router registered at /api/v1/investigation")

app.include_router(vendors_router, prefix="/api/v1/vendors", tags=["Vendors"])
logger.info("[OK] Vendors router registered at /api/v1/vendors")

app.include_router(historical_router, prefix="/api/v1")
logger.info("[OK] Historical router registered at /api/v1/historical")

app.include_router(snapshot_router, prefix="/api/v1")
logger.info("[OK] Snapshot router registered at /api/v1/snapshots")

app.include_router(metrics_router)
app.include_router(trust_metrics_router)
app.include_router(risk_metrics_router)
logger.info("[OK] Trust/Risk metrics routers registered")

app.include_router(intelligence_router, prefix="/api/v1", tags=["Intelligence"])
logger.info("[OK] Intelligence router registered at /api/v1/intelligence")

app.include_router(dashboard_intelligence_router, prefix="/api/v1", tags=["Dashboard Intelligence"])
app.include_router(dashboard_summary_router, prefix="/api/v1", tags=["Dashboard Summary"])
logger.info("[OK] Dashboard Intelligence router registered at /api/v1/dashboard/intelligence")

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
logger.info("[OK] Auth router registered at /api/v1/auth")

app.include_router(cases_list_router, prefix="/api/v1/cases/list", tags=["Cases List"])
logger.info("[OK] Cases List router registered at /api/v1/cases/list")

app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])
logger.info("[OK] Alerts router registered at /api/v1/alerts")

app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Recommendations"])
logger.info("[OK] Recommendations router registered at /api/v1/recommendations")

app.include_router(graph_router, prefix="/api/v1/graph", tags=["Graph"])
app.include_router(graph_trigger_router, prefix="/api/v1/graph", tags=["Graph"])
logger.info("[OK] Graph router registered at /api/v1/graph")

app.include_router(export_router, prefix="/api/v1")

if ENABLE_LEGACY_HEALTH_ROUTER:
    app.include_router(health_intelligence_router, prefix="/api/v1", tags=["Health Intelligence (Legacy)"])
    logger.info("[OK] Legacy Health Intelligence router registered")

logger.info("=" * 50)
logger.info("✅ ALL ROUTERS REGISTERED")
logger.info("=" * 50)

# ============================================================
# HEALTH ENDPOINTS
# ============================================================
@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(), "version": "8.0.0"}

@app.get("/health/live")
async def live():
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health/ready")
async def ready():
    """
    Readiness probe — actually verify dependencies.

    Checks:
    - Database connectivity (via check_db_health)
    - Redis connectivity when the Redis client is available

    Redis is treated as "skipped" when redis-py is not installed.
    A real Redis connectivity error still makes the service not ready.

    Returns HTTP 200 if ready, HTTP 503 if not ready.
    """
    from fastapi import Response
    from backend.database import check_db_health

    timestamp = datetime.now(timezone.utc).isoformat()

    checks = {
        "database": False,
        "redis": False,
    }
    errors = {}

    # Database check
    try:
        db_result = await check_db_health()
        checks["database"] = db_result.get("ok", False)
        if not checks["database"]:
            errors["database"] = db_result.get("error", "unknown")
    except Exception as exc:
        checks["database"] = False
        errors["database"] = str(exc)

    # Redis check (via redis-py async client)
    try:
        import redis.asyncio as aioredis
        from backend.config import settings

        redis_url = getattr(settings, "REDIS_URL", None) or "redis://redis:6379/0"
        client = aioredis.from_url(redis_url, socket_timeout=2)
        try:
            await client.ping()
            checks["redis"] = True
        finally:
            await client.aclose()
    except ModuleNotFoundError as exc:
        # Redis activation is deferred. Missing redis-py is therefore
        # observable as "skipped", not as a real dependency failure.
        if exc.name == "redis" or (exc.name and exc.name.startswith("redis.")):
            checks["redis"] = "skipped"
        else:
            checks["redis"] = False
            errors["redis"] = str(exc)
    except Exception as exc:
        checks["redis"] = False
        errors["redis"] = str(exc)

    all_ok = all(value is True or value == "skipped" for value in checks.values())

    if all_ok:
        return {
            "status": "ready",
            "timestamp": timestamp,
            "checks": checks,
        }
    else:
        return Response(
            content=__import__("json").dumps({
                "status": "not_ready",
                "timestamp": timestamp,
                "checks": checks,
                "errors": errors,
            }),
            status_code=503,
            media_type="application/json",
        )

@app.get("/")
async def root():
    return {
        "message": "NEMESIS V8+ Intelligence API",
        "version": "8.0.0",
        "docs": "/docs",
        "health": "/health",
        "dashboard_intelligence": "/api/v1/dashboard/intelligence/{case_id}",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
