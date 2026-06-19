"""Explainability API Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.explainability.engine import explainer

router = APIRouter(prefix="/explain", tags=["explainability"])

# ============================================================================
# Request/Response Models
# ============================================================================

class ExplainRequest(BaseModel):
    evidence_id: str
    features: Dict[str, Any]
    score: Optional[float] = None
    confidence: Optional[float] = None

class ExplainResponse(BaseModel):
    id: str
    evidence_id: str
    score: float
    confidence: float
    reasons: List[str]
    feature_importance: Dict[str, float]
    timestamp: str
    hash: str

class ReasoningChainResponse(BaseModel):
    evidence_id: str
    explanations: List[Dict]
    chain_length: int
    latest_score: float
    latest_confidence: float
    primary_reason: str

# ============================================================================
# Endpoints
# ============================================================================

@router.post("/", response_model=ExplainResponse)
async def explain_finding(request: ExplainRequest):
    """Generate explanation for a finding"""
    result = explainer.explain(
        evidence_id=request.evidence_id,
        features=request.features,
        score=request.score,
        confidence=request.confidence
    )
    
    # Audit log
    from backend.audit.logger import AuditLogger
    AuditLogger.log(
        action="EXPLAIN",
        actor="system",
        resource=f"evidence/{request.evidence_id}",
        data={"explanation_id": result["id"], "score": result["score"]}
    )
    
    return result


@router.get("/{explanation_id}", response_model=ExplainResponse)
async def get_explanation(explanation_id: str):
    """Get stored explanation by ID"""
    result = explainer.get_explanation(explanation_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Explanation not found")
    
    return result


@router.get("/evidence/{evidence_id}", response_model=ExplainResponse)
async def get_latest_explanation(evidence_id: str):
    """Get latest explanation for an evidence"""
    # Get all explanations for this evidence
    from backend.explainability.engine import explainer as exp_engine
    all_exps = exp_engine._explanations.values()
    
    matching = [e for e in all_exps if e.evidence_id == evidence_id]
    
    if not matching:
        raise HTTPException(status_code=404, detail="No explanation found for this evidence")
    
    # Return latest
    latest = max(matching, key=lambda x: x.timestamp)
    
    return {
        "id": latest.id,
        "evidence_id": latest.evidence_id,
        "score": latest.score,
        "confidence": latest.confidence,
        "reasons": latest.reasons,
        "feature_importance": latest.feature_importance,
        "timestamp": latest.timestamp.isoformat(),
        "hash": latest.hash
    }


@router.get("/reasoning/{evidence_id}", response_model=ReasoningChainResponse)
async def get_reasoning_chain(evidence_id: str):
    """Get full reasoning chain for an evidence"""
    result = explainer.get_reasoning_chain(evidence_id)
    
    return ReasoningChainResponse(**result)


@router.post("/calibrate/{evidence_id}")
async def calibrate_confidence(evidence_id: str, actual_outcome: str):
    """Calibrate confidence based on actual outcome"""
    result = explainer.calibrate_confidence(evidence_id, actual_outcome)
    
    return result


@router.get("/feature/importance")
async def get_feature_importance():
    """Get feature importance reference"""
    return {
        "features": {
            "price_markup": "Persentase selisih harga dari rata-rata pasar",
            "vendor_risk": "Tingkat risiko vendor berdasarkan historis",
            "procurement_method": "Metode pengadaan (tender, direct, emergency)",
            "anomaly_score": "Skor anomali dari deteksi ML",
            "historical_issues": "Jumlah isu serupa dalam 12 bulan",
            "collusion_risk": "Risiko kolusi berdasarkan pola hubungan vendor"
        }
    }
