"""
Intelligence Endpoints — Thin Controllers.

ARCHITECTURE:
- Router = Thin Controller
- NO business logic
- NO SQL directly
- NO manual DI
- Delegates to RiskApplicationService from container

FLOW:
Router → RiskApplicationService (from container) → IntelligenceService → RiskProjectionService → CommandRepository
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
import logging

from backend.domain.enums.risk_calculation_source import RiskCalculationSource

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/score")
async def calculate_risk_score(
    request: Request,
    case_id: str = Query(..., description="Case ID"),
    fraud_score: Optional[float] = Query(0, description="Fraud score from ML"),
):
    """
    Calculate and persist risk score.

    ARCHITECTURE:
    - Router = Thin Controller (NO business logic)
    - Delegates to RiskApplicationService from container
    - Uses pure IntelligenceService for calculation
    - Persists via RiskProjectionService
    - Dashboard reads from risk_scores (unchanged)
    """
    try:
        # ✅ Ambil service dari container (SINGLE SOURCE OF TRUTH)
        container = request.app.state.container
        service = container.services.risk_application

        result = await service.calculate_and_persist(
            case_id=UUID(case_id),
            fraud_score=fraud_score or 0,
            calculated_by=RiskCalculationSource.API,
        )

        return {
            **result,
            "timestamp": datetime.now().isoformat(),
            "version": "v3.0",
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error calculating risk score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph-risk/{case_id}")
async def get_graph_risk(
    case_id: str,
    request: Request,
):
    """
    Get graph risk analysis.

    ⚠️ LEGACY: This endpoint still uses GraphRiskAnalyzer directly.
    Will be migrated to use GraphRepository in Phase 2.
    """
    try:
        from intelligence.graph.risk_analyzer import GraphRiskAnalyzer
        
        # ✅ Ambil db dari container (via session_factory)
        container = request.app.state.container
        async with container.infrastructure.session_factory() as session:
            result = await GraphRiskAnalyzer.calculate_graph_risk(case_id, session)
            return result
            
    except Exception as e:
        logger.error(f"Error getting graph risk: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "intelligence",
        "version": "v3.0",
        "timestamp": datetime.now().isoformat(),
    }