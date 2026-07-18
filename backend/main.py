"""
NEMESIS V8+ - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import logging
import sys
import os
from contextlib import asynccontextmanager


# ============================================================
# LOGGING — Gunakan setup_logging() saja
# ============================================================

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ✅ Hanya import logger, konfigurasi dilakukan oleh setup_logging()
from backend.core.logging_config import setup_logging

# Setup logging sebelum logger digunakan
setup_logging()
logger = logging.getLogger(__name__)


# ============================================================
# IMPORT DENGAN PREFIX BACKEND — SEMUA IMPORT NORMAL DAHULU
# ============================================================

from backend.routers.auth_router import router as auth_router
from backend.routers.finding import router as finding_router
from backend.routers import finding_assignments
from backend.routers import finding_actions
from backend.routers import finding_reviews
from backend.routers import finding_timeline
from backend.routers import finding_intelligence
from backend.middleware.request_id_middleware import RequestIDMiddleware
from backend.routers.fraud_detail_router import router as fraud_detail_router

# ===== TAMBAHKAN INI =====
from backend.routers.intelligence import router as intelligence_router
# =========================


# ============================================================
# DASHBOARD INTELLIGENCE IMPORTS
# ============================================================

from backend.infrastructure.sql_repository import SQLRepository
from backend.core.version import VersionInfo
from backend.routers.dashboard_intelligence import router as dashboard_router


# ============================================================
# FEATURE FLAGS — Setelah semua import normal selesai
# ============================================================

# TODO: Remove after Health Intelligence V8 migration
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
    from backend.bootstrap.functions import bootstrap_infrastructure
    from backend.bootstrap.container_builder import build_application_container
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
        engine = result.engine  # ✅ Dari DTO
        logger.info("Infrastructure bootstrapped")
        
        # 2. Health Config (dibaca di Composition Root, bukan di builder)
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
    lifespan=lifespan
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


# ============================================================
# REGISTER EXISTING ROUTERS
# ============================================================

# Finding Router
app.include_router(finding_router)
app.include_router(finding_assignments.router)
app.include_router(finding_actions.router)
app.include_router(finding_reviews.router)
app.include_router(finding_timeline.router)
app.include_router(finding_intelligence.router)


# TODO: Remove after Health Intelligence V8 migration
if ENABLE_LEGACY_HEALTH_ROUTER:
    app.include_router(
        health_intelligence_router,
        prefix="/api/v1",
        tags=["Health"]
    )
    logger.info("Legacy Health Intelligence Router registered")
else:
    logger.info("Legacy Health Intelligence Router skipped (feature flag disabled)")

# ✅ Dashboard Intelligence Router (New)
app.include_router(
    dashboard_router,
    prefix="/api/v1"
)

# ===== TAMBAHKAN INI =====
# ✅ Intelligence Router (New)
app.include_router(
    intelligence_router,
    prefix="/api/v1",
    tags=["Intelligence"]
)
logger.info("✅ Intelligence router registered at /api/v1/intelligence")
# =========================


# ============================================================
# REGISTER ALL ROUTERS - DYNAMIC
# ============================================================

print("\n🔧 REGISTERING ROUTERS...")
print("=" * 40)

# 1. Cases Router
try:
    from backend.routers.cases import router as cases_router
    app.include_router(cases_router, prefix="/api/v1/cases", tags=["Cases"])
    print("[OK] Cases router registered at /api/v1/cases")
except Exception as e:
    print(f"[WARN] Failed to load cases router: {e}")

# 2. Fraud Router
try:
    from backend.routers.fraud import router as fraud_router
    app.include_router(fraud_router, prefix="/api/v1/fraud", tags=["Fraud"])
    print("[OK] Fraud router registered at /api/v1/fraud")
except Exception as e:
    print(f"[WARN] Failed to load fraud router: {e}")

# 3. Graph Router
try:
    from backend.routers.graph import router as graph_router
    app.include_router(graph_router, prefix="/api/v1/graph", tags=["Graph"])
    print("[OK] Graph router registered at /api/v1/graph")
except Exception as e:
    print(f"[WARN] Failed to load graph router: {e}")

# 4. Risk Router
try:
    from backend.routers.risk import router as risk_router
    app.include_router(risk_router, prefix="/api/v1/risk", tags=["Risk"])
    print("[OK] Risk router registered at /api/v1/risk")
except Exception as e:
    print(f"[WARN] Failed to load risk router: {e}")

# 5. Procurement Router
try:
    from backend.routers.procurement import router as procurement_router
    app.include_router(procurement_router, prefix="/api/v1/procurement", tags=["Procurement"])
    print("[OK] Procurement router registered at /api/v1/procurement")
except Exception as e:
    print(f"[WARN] Failed to load procurement router: {e}")

# 6. Recommendations Router
try:
    from backend.routers.recommendations import router as recommendations_router
    app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Recommendations"])
    print("[OK] Recommendations router registered at /api/v1/recommendations")
except Exception as e:
    print(f"[WARN] Failed to load recommendations router: {e}")

# 7. Evidence Router
try:
    from backend.routers.evidence import router as evidence_router
    app.include_router(evidence_router, prefix="/api/v1/evidence", tags=["Evidence"])
    print("[OK] Evidence router registered at /api/v1/evidence")
except Exception as e:
    print(f"[WARN] Failed to load evidence router: {e}")

# 8. Investigation Router
try:
    from backend.routers.investigations import router as investigation_router
    app.include_router(investigation_router, prefix="/api/v1/investigation", tags=["Investigation"])
    print("[OK] Investigation router registered at /api/v1/investigation")
except Exception as e:
    print(f"[WARN] Failed to load investigation router: {e}")

# 9. Vendors Router
try:
    from backend.routers.vendors import router as vendors_router
    app.include_router(vendors_router, prefix="/api/v1/vendors", tags=["Vendors"])
    print("[OK] Vendors router registered at /api/v1/vendors")
except Exception as e:
    print(f"[WARN] Failed to load vendors router: {e}")

# 10. Health Router
try:
    from backend.routers.health import router as health_router
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
    print("[OK] Health router registered at /api/v1/health")
except Exception as e:
    print(f"[WARN] Failed to load health router: {e}")

# 11. Auth Router (additional)
try:
    from backend.routers.auth import router as auth_router2
    app.include_router(auth_router2, prefix="/api/v1/auth", tags=["Auth"])
    print("[OK] Auth router registered at /api/v1/auth")
except Exception as e:
    print(f"[WARN] Failed to load auth router: {e}")

# 12. Cases List Router
try:
    from backend.routers.cases_list import router as cases_list_router
    app.include_router(cases_list_router, prefix="/api/v1/cases/list", tags=["Cases List"])
    print("[OK] Cases List router registered at /api/v1/cases/list")
except Exception as e:
    print(f"[WARN] Failed to load cases list router: {e}")

# 13. Alerts Router
try:
    from backend.routers.alerts import router as alerts_router
    app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])
    print("[OK] Alerts router registered at /api/v1/alerts")
except Exception as e:
    print(f"[WARN] Failed to load alerts router: {e}")

print("=" * 40)
print("✅ ALL ROUTERS REGISTERED\n")


# ============================================================
# HEALTH ENDPOINTS
# ============================================================

@app.get("/health/live")
def live():
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health/ready")
async def ready():
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
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health/dashboard")
async def dashboard_health():
    container = getattr(app.state, "container", None)

    version = (
        container.infrastructure.version
        if container
        else None
    )

    if container:
        dashboard = container.services.dashboard
        version = container.infrastructure.version

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
        "endpoint": "/api/v1/dashboard/intelligence/{case_id}"
    }


# ===== PERBAIKAN ROOT ENDPOINT =====
@app.get("/")
async def root():
    container = getattr(app.state, "container", None)
    version = container.infrastructure.version if container else None
    return {
        "message": "NEMESIS V8+ Intelligence API",
        "version": version.api_version if version else "8.0.0",
        "docs": "/docs",
        "health": "/health",
        "dashboard_intelligence": "/api/v1/dashboard/intelligence/{case_id}"
    }
# ==================================


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

print("\n===== REGISTERED ROUTES =====")
for route in app.routes:
    methods = ",".join(route.methods) if hasattr(route, "methods") else ""
    print(f"{methods:10} {route.path}")
print("=============================\n")