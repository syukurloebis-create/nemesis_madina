"""
NEMESIS V8+ - Main Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os

# Set encoding untuk Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NEMESIS Intelligence API",
    description="NEMESIS V8+ - Autonomous Risk Intelligence Platform",
    version="8.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# REGISTER ALL ROUTERS
# ============================================

# 1. Investigation Router
try:
    from routers.investigations import router as investigation_router
    app.include_router(investigation_router, prefix="/api/v1/investigation", tags=["Investigation"])
    print("[OK] Investigation router registered")
except Exception as e:
    print(f"[WARN] Failed to load investigation router: {e}")

# 2. Cases Router
try:
    from routers.cases import router as cases_router
    app.include_router(cases_router, prefix="/api/v1/cases", tags=["Cases"])
    print("[OK] Cases router registered")
except Exception as e:
    print(f"[WARN] Failed to load cases router: {e}")

# 2b. Cases List Router (additional)
try:
    from routers.cases_list import router as cases_list_router
    app.include_router(cases_list_router, prefix="/api/v1/cases/list", tags=["Cases List"])
    print("[OK] Cases List router registered")
except Exception as e:
    print(f"[WARN] Failed to load cases list router: {e}")

# 3. Evidence Router
try:
    from routers.evidence import router as evidence_router
    app.include_router(evidence_router, prefix="/api/v1/evidence", tags=["Evidence"])
    print("[OK] Evidence router registered")
except Exception as e:
    print(f"[WARN] Failed to load evidence router: {e}")

# 4. Graph Router
try:
    from routers.graph import router as graph_router
    app.include_router(graph_router, prefix="/api/v1/graph", tags=["Graph"])
    print("[OK] Graph router registered")
except Exception as e:
    print(f"[WARN] Failed to load graph router: {e}")

# 5. Fraud Router
try:
    from routers.fraud import router as fraud_router
    app.include_router(fraud_router, prefix="/api/v1/fraud", tags=["Fraud"])
    print("[OK] Fraud router registered")
except Exception as e:
    print(f"[WARN] Failed to load fraud router: {e}")

# 6. Risk Router
try:
    from routers.risk import router as risk_router
    app.include_router(risk_router, prefix="/api/v1/risk", tags=["Risk"])
    print("[OK] Risk router registered")
except Exception as e:
    print(f"[WARN] Failed to load risk router: {e}")

# 7. Procurement Router
try:
    from routers.procurement import router as procurement_router
    app.include_router(procurement_router, prefix="/api/v1/procurement", tags=["Procurement"])
    print("[OK] Procurement router registered")
except Exception as e:
    print(f"[WARN] Failed to load procurement router: {e}")

# 8. Recommendations Router
try:
    from routers.recommendations import router as recommendations_router
    app.include_router(recommendations_router, prefix="/api/v1/recommendations", tags=["Recommendations"])
    print("[OK] Recommendations router registered")
except Exception as e:
    print(f"[WARN] Failed to load recommendations router: {e}")

# 9. Alerts Router
try:
    from routers.alerts import router as alerts_router
    app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["Alerts"])
    print("[OK] Alerts router registered")
except Exception as e:
    print(f"[WARN] Failed to load alerts router: {e}")

# 10. Vendors Router
try:
    from routers.vendors import router as vendors_router
    app.include_router(vendors_router, prefix="/api/v1/vendors", tags=["Vendors"])
    print("[OK] Vendors router registered")
except Exception as e:
    print(f"[WARN] Failed to load vendors router: {e}")

# 11. Health Router
try:
    from routers.health import router as health_router
    app.include_router(health_router, prefix="/api/v1/health", tags=["Health"])
    print("[OK] Health router registered")
except Exception as e:
    print(f"[WARN] Failed to load health router: {e}")

# 12. Auth Router
try:
    from routers.auth import router as auth_router
    app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
    print("[OK] Auth router registered")
except Exception as e:
    print(f"[WARN] Failed to load auth router: {e}")

# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "nemesis-api",
        "version": "8.0.0"
    }

@app.get("/")
async def root():
    return {
        "message": "NEMESIS V8+ Intelligence API",
        "version": "8.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
