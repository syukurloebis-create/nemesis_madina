from fastapi import APIRouter

router = APIRouter()


async def procurement_summary():
    return {
        "total_vendors":549,
        "high_risk_vendors":22,
        "risk_score":64
    }

@router.get("/stats")
async def get_procurement_stats():
    return {
        "total_vendors": 549,
        "total_packages": 3630,
        "total_value": 583974259200.0,
        "avg_value": 160918781.81
    }

@router.get("/vendors")
async def get_vendors():
    return [
        {"name": "PT Tech Solutions", "package_count": 8, "total_value": 5000000000},
        {"name": "PT Office Mart", "package_count": 12, "total_value": 3000000000},
        {"name": "PT Secure Solutions", "package_count": 5, "total_value": 4500000000}
    ]
