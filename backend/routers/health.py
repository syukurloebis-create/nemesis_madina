from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    return {"status": "healthy", "service": "NEMESIS V8"}

@router.get("/health/runtime")
async def health_runtime():
    return {
        "status": "healthy",
        "runtime": "active",
        "timestamp": "2026-06-02T00:00:00Z"
    }
