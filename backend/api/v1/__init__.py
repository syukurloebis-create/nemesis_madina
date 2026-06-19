"""API V1 - Router Container (SINGLE ROUTER)"""

from fastapi import APIRouter

# ============================================
# MAIN V1 ROUTER
# ============================================
router = APIRouter(prefix="/api/v1", tags=["v1"])

# ============================================
# REGISTER ROUTERS - HANYA YANG DIPERLUKAN
# ============================================
try:
    from backend.api.v1.intelligence import router as intelligence_router
    router.include_router(intelligence_router, prefix="/intelligence")
    print("✅ Intelligence router registered")
except Exception as e:
    print(f"❌ Failed to load intelligence router: {e}")

# Hanya register router yang benar-benar diperlukan
# Comment router lain jika tidak digunakan
"""
try:
    from backend.api.v1.evidence import router as evidence_router
    router.include_router(evidence_router, prefix="/evidence")
    print("✅ Evidence router registered")
except Exception as e:
    print(f"⚠️ Failed to load evidence router: {e}")
"""

# ============================================
# ROOT ENDPOINT
# ============================================
@router.get("/")
async def v1_root():
    return {
        "version": "2.0.0",
        "name": "NEMESIS API V1",
        "status": "operational",
        "endpoints": {
            "intelligence": "/api/v1/intelligence",
            "health": "/api/v1/intelligence/health"
        }
    }
