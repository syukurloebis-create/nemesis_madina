"""Intelligence Router — Graph Risk Analysis."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_db
from backend.dependencies.auth import get_current_active_user
from backend.security.models import User
from backend.services.entity_graph_intelligence_service import (
    EntityGraphIntelligenceService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def get_intelligence_service() -> EntityGraphIntelligenceService:
    """Get Entity Graph Intelligence Service."""
    return EntityGraphIntelligenceService()


@router.get("/graph-risk/{case_id}")
async def get_graph_risk(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    service: EntityGraphIntelligenceService = Depends(get_intelligence_service),
) -> dict:
    """Get graph-based risk analysis for a case."""
    logger.info("Graph risk analysis for case: %s", case_id)

    try:
        # Get graph nodes for the case
        from sqlalchemy import text

        result = await db.execute(
            text("""
                SELECT
                    id,
                    name,
                    entity_type,
                    risk_score,
                    extra_data
                FROM graph_entities
                WHERE case_id = :case_id
                AND entity_type = 'vendor'
            """),
            {"case_id": str(case_id)}
        )

        vendors = result.mappings().all()

        if not vendors:
            return {
                "case_id": str(case_id),
                "risk_score": 0,
                "level": "UNKNOWN",
                "vendors": [],
                "analysis": "No vendor data found"
            }

        # Analyze each vendor
        vendor_analysis = []
        total_risk = 0

        for vendor in vendors:
            analysis = await service.analyze_entity(
                vendor["name"],
                db
            )
            vendor_analysis.append(analysis)
            total_risk += analysis.get("entity", {}).get("risk_score", 0)

        avg_risk = total_risk / len(vendors) if vendors else 0

        # Determine risk level
        if avg_risk >= 70:
            level = "HIGH"
        elif avg_risk >= 40:
            level = "MEDIUM"
        elif avg_risk > 0:
            level = "LOW"
        else:
            level = "UNKNOWN"

        return {
            "case_id": str(case_id),
            "risk_score": round(avg_risk, 2),
            "level": level,
            "vendor_count": len(vendors),
            "vendors": vendor_analysis,
            "analysis": f"Analyzed {len(vendors)} vendors with average risk {avg_risk:.1f}"
        }

    except Exception as e:
        logger.exception("Graph risk analysis failed for case %s", case_id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze graph risk: {str(e)}"
        )
