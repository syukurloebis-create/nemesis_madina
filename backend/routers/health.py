from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

@router.get("/")
async def health():
    return {"status": "healthy", "service": "nemesis-api"}

@router.get("/live")
async def liveness():
    return {"status": "alive"}

@router.get("/ready")
async def readiness():
    return {"status": "ready"}
