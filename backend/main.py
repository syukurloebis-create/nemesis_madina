"""
NEMESIS V8+ - Main Application
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ============================================================
# STDOUT PATCH — Windows UTF-8 Compatibility
# ============================================================
# Only apply when NOT running under pytest to avoid capture conflicts
if (
    sys.platform == "win32"
    and "pytest" not in sys.modules
    and hasattr(sys.stdout, "buffer")
):
    import io

    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        line_buffering=True,
    )

# ============================================================
# LOGGING — Setup logging before logger usage
# ============================================================
from backend.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


# ============================================================
# IMPORTS — All imports with backend prefix
# ============================================================
# Core
from backend.core.version import VersionInfo
from backend.infrastructure.sql_repository import SQLRepository
from backend.middleware.request_id_middleware import RequestIDMiddleware
from backend.middleware.canonical_tenant import CanonicalTenantMiddleware

# Routers — Finding
from backend.routers.finding import router as finding_router
from backend.routers import finding_actions
from backend.routers import finding_assignments
from backend.routers import finding_intelligence
from backend.routers import finding_reviews
from backend.routers import finding_timeline

# Routers — Dashboard & Intelligence
from backend.routers.dashboard_intelligence import router as dashboard_intelligence_router
from backend.routers.intelligence import router as intelligence_router

# Routers — Auth
from backend.routers.auth_router import router as auth_router

# Routers — Domain
from backend.routers.alerts import router as alerts_router
from backend.routers.cases import router as cases_router
from backend.routers.cases_list import router as cases_list_router
from backend.routers.evidence import router as evidence_router
from backend.routers.fraud import router as fraud_router
from backend.routers.fraud_detail_router import router as fraud_detail_router
from backend.routers.graph import router as graph_router
from backend.routers.investigation import router as investigation_router
from backend.routers.procurement import router as procurement_router
from backend.routers.recommendations import router as recommendations_router
from backend.routers.risk import router as risk_router
from backend.routers.vendors import router as vendors_router
from backend.routers.historical import router as historical_router
from backend.routers.snapshot import router as snapshot_router


# ============================================================
# FEATURE FLAGS
# ============================================================
ENABLE_LEGACY_HEALTH_ROUTER = os.getenv(
    "ENABLE_LEGACY_HEALTH_ROUTER",
    "false"
).lower() == "true"

if ENABLE_LEGACY_HEALTH_ROUTER:
    from backend.routers.health_intelligence import router as health_intelligence_router
    logger.info("Legacy Health Intelligence Router: ENABLED")
else:
    logger.info("Legacy Health Intelligence Router: DISABLED (use ENABLE_LEGACY_HEALTH_ROUTER=true to enable)")


# ============================================================
# LIFESPAN MANAGER — SINGLE COMPOSITION ROOT
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager — SINGLE COMPOSITION ROOT."""
    from backend.bootstrap.container_builder import build_application_container
    from backend.bootstrap.functions import bootstrap_infrastructure
    from backend.bootstrap.validator import ContainerValidator
    from backend.health.dependencies import HealthDependencies

    logger.info("=" * 50)
    logger.info("NEMESIS MADINA V8+ Starting...")
    logger.info("=" * 50)

    engine = None

    try:
        # 1. Bootstrap Infrastructure
        result = bootstrap_infrastructure()
        infra = result.infrastructure
        engine = result.engine
        logger.info("Infrastructure bootstrapped")

        # 2. Health Config (dibaca di Composition Root)
        health_enabled = os.getenv("ENABLE_HEALTH", "true").lower() == "true"
        health_deps = HealthDependencies(
            enabled=health_enabled,
            sql_repo=infra.sql_repo,
        )

        # 3. Build Application Container (pure function)
        container = build_application_container(infra)
        logger.info("Application container built")

        # 4. Validate Container
        ContainerValidator.validate(container)
        logger.info("Container validation passed")

        # 5. Store Container (ONLY ONE)
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
        logger.info("NEMESIS MADINA V8+ Shutdown complete")


# ============================================================
# CREATE APP
# ============================================================
app = FastAPI(
    title="NEMESIS Intelligence API",
    description="NEMESIS V8+ - Autonomous Risk Intelligence Platform",
    version="8.0.0",
    lifespan=lifespan,
)


# ============================================================
# MIDDLEWARE
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(CanonicalTenantMiddleware)

# ============================================================
# REGISTER ROUTERS — DETERMINISTIC
# ============================================================
logger.info("=" * 50)
logger.info("Registering Routers...")
logger.info("=" * 50)

# --- Finding Routers ---
app.include_router(finding_router)
app.include_router(finding_assignments.router)
app.include_router(finding_actions.router)
app.include_router(finding_reviews.router)
app.include_router(finding_timeline.router)
app.include_router(finding_intelligence.router)
logger.info("[OK] Finding routers registered")

# --- Core Domain Routers ---
app.include_router(cases_router, prefix="/api/v1/cases", tags=["Cases"])
logger.info("[OK] Cases router registered at /api/v1/cases")

app.include_router(fraud_router, prefix="/api/v1/fraud", tags=["Fraud"])
logger.info("[OK] Fraud router registered at /api/v1/fraud")

app.include_router(fraud_detail_router, prefix="/api/v1/fraud", tags=["Fraud Detail"])
logger.info("[OK] Fraud Detail router registered")

app.include_router(graph_router, prefix="/api/v1/graph", tags=["Graph"])
logger.info("[OK] Graph router registered at /api/v1/graph")

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

app.include_router(
    intelligence_router,
    prefix="/api/v1",
    tags=["Intelligence"],
)
logger.info("[OK] Intelligence router registered at /api/v1/intelligence")

app.include_router(
    dashboard_intelligence_router,
    prefix="/api/v1",
    tags=["Dashboard Intelligence"],
)
logger.info("[OK] Dashboard Intelligence router registered at /api/v1/dashboard/intelligence")

# --- Auth ---
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
logger.info("[OK] Auth router registered at /api/v1/auth")

# --- Cases List ---
app.include_router(cases_list_router, prefix="/api/v1/cases/list", tags=["Cases List"])
logger.info("[OK] Cases List router registered at /api/v1/cases/list")

# --- Alerts ---
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])
logger.info("[OK] Alerts router registered at /api/v1/alerts")

# --- Recommendations ---
app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Recommendations"])
logger.info("[OK] Recommendations router registered at /api/v1/recommendations")

# --- Legacy Health Intelligence (Feature Flag) ---
if ENABLE_LEGACY_HEALTH_ROUTER:
    app.include_router(
        health_intelligence_router,
        prefix="/api/v1",
        tags=["Health Intelligence (Legacy)"],
    )
    logger.info("[OK] Legacy Health Intelligence router registered (feature flag enabled)")
else:
    logger.info("[SKIP] Legacy Health Intelligence router skipped (feature flag disabled)")

logger.info("=" * 50)
logger.info("✅ ALL ROUTERS REGISTERED")
logger.info("=" * 50)


# ============================================================
# HEALTH ENDPOINTS
# ============================================================
@app.get("/health/live")
async def live():
    """Liveness probe."""
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/ready")
async def ready():
    """Readiness probe with database check."""
    db_status = "connected"
    try:
        from backend.database import get_db

        async for _ in get_db():
            db_status = "connected"
            break
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ready" if db_status == "connected" else "degraded",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/dashboard")
async def dashboard_health():
    """Dashboard health status."""
    container = getattr(app.state, "container", None)
    dashboard = None
    version = None

    if container:
        dashboard = getattr(container.services, "dashboard", None)
        version = getattr(container.infrastructure, "version", None)

    return {
        "status": "healthy" if dashboard else "unavailable",
        "service": "dashboard-intelligence",
        "service_initialized": dashboard is not None,
        "legacy_health_router": ENABLE_LEGACY_HEALTH_ROUTER,
        "version": (
            version.to_dict()
            if version
            else {"api_version": "unknown"}
        ),
        "endpoint": "/api/v1/dashboard/intelligence/{case_id}",
    }


# ============================================================
# ROOT ENDPOINT
# ============================================================
@app.get("/")
async def root():
    """Root endpoint with API information."""
    container = getattr(app.state, "container", None)
    version = (
        container.infrastructure.version
        if container and hasattr(container.infrastructure, "version")
        else None
    )

    return {
        "message": "NEMESIS V8+ Intelligence API",
        "version": version.api_version if version else "8.0.0",
        "docs": "/docs",
        "health": "/health",
        "dashboard_intelligence": "/api/v1/dashboard/intelligence/{case_id}",
    }


# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )