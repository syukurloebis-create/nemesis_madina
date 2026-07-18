from fastapi import APIRouter

router = APIRouter()

@router.get("/summary")
async def get_recommendations_summary():
    return {
        "CRITICAL": 3,
        "HIGH": 1,
        "MEDIUM": 0,
        "LOW": 0
    }
