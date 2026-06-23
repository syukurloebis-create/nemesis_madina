"""
NEMESIS V8+ - Risk Router
Endpoint untuk risk intelligence
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime, timedelta
import random

router = APIRouter()

@router.get("/exposure")
async def get_exposure(case_id: Optional[str] = None):
    """
    Get exposure data for dashboard
    """
    # Generate realistic exposure data
    total_exposure = random.randint(5000000000, 20000000000)  # Rp 5B - 20B
    recovered = random.randint(1000000000, 5000000000)  # Rp 1B - 5B
    
    return {
        "case_id": case_id,
        "total_exposure": total_exposure,
        "recovered_value": recovered,
        "potential_loss": total_exposure - recovered,
        "recovery_rate": round((recovered / total_exposure * 100) if total_exposure > 0 else 0, 1),
        "exposure_breakdown": {
            "high_risk": round(total_exposure * 0.5),
            "medium_risk": round(total_exposure * 0.3),
            "low_risk": round(total_exposure * 0.2),
        },
        "recovery_timeline": [
            {"month": "Jan", "recovered": random.randint(100000000, 500000000)},
            {"month": "Feb", "recovered": random.randint(100000000, 500000000)},
            {"month": "Mar", "recovered": random.randint(100000000, 500000000)},
            {"month": "Apr", "recovered": random.randint(100000000, 500000000)},
            {"month": "May", "recovered": random.randint(100000000, 500000000)},
            {"month": "Jun", "recovered": random.randint(100000000, 500000000)},
        ],
        "updated_at": datetime.now().isoformat()
    }

@router.get("/recovery")
async def get_recovery(case_id: Optional[str] = None):
    """
    Get recovery data for dashboard
    """
    total_recovered = random.randint(1000000000, 5000000000)
    
    return {
        "case_id": case_id,
        "total_recovered": total_recovered,
        "recovered_by_type": {
            "cash": round(total_recovered * 0.4),
            "assets": round(total_recovered * 0.3),
            "contracts": round(total_recovered * 0.2),
            "other": round(total_recovered * 0.1),
        },
        "recovery_timeline": [
            {"month": "Jan", "value": random.randint(50000000, 200000000)},
            {"month": "Feb", "value": random.randint(50000000, 200000000)},
            {"month": "Mar", "value": random.randint(50000000, 200000000)},
            {"month": "Apr", "value": random.randint(50000000, 200000000)},
            {"month": "May", "value": random.randint(50000000, 200000000)},
            {"month": "Jun", "value": random.randint(50000000, 200000000)},
        ],
        "success_rate": round(random.uniform(60, 90), 1),
        "updated_at": datetime.now().isoformat()
    }

@router.get("/stats")
async def get_risk_stats():
    """
    Get risk statistics summary
    """
    return {
        "total_cases": 6,
        "high_risk_cases": 2,
        "medium_risk_cases": 2,
        "low_risk_cases": 2,
        "avg_risk_score": 13.33,
        "risk_distribution": {
            "CRITICAL": 1,
            "HIGH": 2,
            "MEDIUM": 2,
            "LOW": 1
        },
        "trend": {
            "direction": "decreasing",
            "percentage": 12.5,
            "period": "30 days"
        }
    }
