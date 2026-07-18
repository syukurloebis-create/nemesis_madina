"""
Fraud Detail Router - Endpoint untuk detail fraud signals
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from backend.database import get_db
from backend.graph.intelligence.fraud_detector import FraudDetector

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/fraud/signals",
    tags=["fraud", "signals"]
)


@router.get("/{case_id}")
async def get_fraud_signals(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed fraud signals for a case.
    
    Returns complete signals including:
    - high_risk_clusters
    - hub_entities
    - shared_package_patterns
    - method_similarity_patterns
    """
    try:
        detector = FraudDetector(db, case_id)
        signals = await detector.detect_fraud_signals()
        
        return {
            "case_id": case_id,
            "signals": signals.to_dict().get("signals", {}),
            "overall_risk": signals.summary.overall_risk,
            "confidence": signals.summary.confidence
        }
    except Exception as e:
        logger.exception(f"Error getting fraud signals for case {case_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get fraud signals: {str(e)}"
        )