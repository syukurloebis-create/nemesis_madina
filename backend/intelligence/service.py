"""
Intelligence Service — Pure Risk Calculation.

Architecture Decision (ADR-018, ADR-019, ADR-020):
- Service adalah PURE CALCULATION
- TIDAK ada SQL langsung
- TIDAK ada persistence
- TIDAK ada session
- Menerima data dari repository (dari caller)
- Menghasilkan RiskResult (Value Object)

Flow:
1. Caller fetch data via repositories
2. Caller panggil IntelligenceService.calculate()
3. Caller simpan hasil via ProjectionService
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

# ===== TAMBAHKAN IMPORT INI =====
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
# ================================

logger = logging.getLogger(__name__)


# ============================================================================
# 1. RISK RESULT — Value Object (Immutable)
# ============================================================================

@dataclass(frozen=True)
class RiskResult:
    """
    Risk Result — Immutable Value Object.
    
    Output dari IntelligenceService.calculate().
    Tidak mengandung informasi tentang sumber data atau persistence.
    """
    score: float
    level: str
    components: Dict[str, float]
    weights: Dict[str, float]
    factors: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        """Validate invariants."""
        if not (0 <= self.score <= 100):
            raise ValueError(f"score must be between 0 and 100, got {self.score}")
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if self.level not in valid_levels:
            raise ValueError(f"level must be one of {valid_levels}, got {self.level}")
        if self.factors is None:
            object.__setattr__(self, 'factors', [])
        if self.recommendations is None:
            object.__setattr__(self, 'recommendations', [])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for API response."""
        return {
            "score": self.score,
            "level": self.level,
            "components": self.components,
            "weights": self.weights,
            "factors": self.factors or [],
            "recommendations": self.recommendations or [],
        }


# ============================================================================
# 2. INTELLIGENCE SERVICE — Pure Calculation
# ============================================================================

class IntelligenceService:
    """
    Intelligence Service — Pure Risk Calculation.
    
    STATELESS: Tidak ada session, tidak ada repository.
    PURE FUNCTION: Input → Output.
    TIDAK ada SQL, TIDAK ada persistence.
    """
    
    # ===== Default Weights =====
    DEFAULT_WEIGHTS = {
        "case": 0.30,
        "graph": 0.25,
        "fraud": 0.30,
        "evidence": 0.15,
    }
    
    # ===== Thresholds =====
    THRESHOLDS = {
        "CRITICAL": 80,
        "HIGH": 60,
        "MEDIUM": 40,
        "LOW": 0,
    }
    
    @classmethod
    def calculate(
        cls,
        case_risk: float = 0,
        graph_risk: float = 0,
        fraud_score: float = 0,
        evidence_trust: float = 0,
        weights: Optional[Dict[str, float]] = None,
    ) -> RiskResult:
        """
        Calculate risk score — PURE FUNCTION.
        
        Formula:
        - Case Risk: 30%
        - Graph Risk: 25%
        - Fraud Score: 30%
        - Evidence Trust: 15%
        
        Args:
            case_risk: Risk score from case (0-100)
            graph_risk: Risk score from graph (0-100)
            fraud_score: Fraud detection score (0-100)
            evidence_trust: Evidence trust score (0-100)
            weights: Optional custom weights (defaults to DEFAULT_WEIGHTS)
            
        Returns:
            RiskResult: Immutable calculation result
        """
        # ===== 1. Validate inputs =====
        case_risk = cls._validate_score(case_risk, "case_risk")
        graph_risk = cls._validate_score(graph_risk, "graph_risk")
        fraud_score = cls._validate_score(fraud_score, "fraud_score")
        evidence_trust = cls._validate_score(evidence_trust, "evidence_trust")
        
        # ===== 2. Use weights =====
        if weights is None:
            weights = cls.DEFAULT_WEIGHTS.copy()
        else:
            weights = cls._validate_weights(weights)
        
        # ===== 3. Calculate weighted score =====
        final_score = (
            case_risk * weights["case"] +
            graph_risk * weights["graph"] +
            fraud_score * weights["fraud"] +
            evidence_trust * weights["evidence"]
        )
        
        # ===== 4. Clamp to 0-100 =====
        final_score = min(max(final_score, 0), 100)
        
        # ===== 5. Determine level =====
        level = cls._determine_level(final_score)
        
        # ===== 6. Generate factors =====
        factors = cls._generate_factors(
            case_risk=case_risk,
            graph_risk=graph_risk,
            fraud_score=fraud_score,
            evidence_trust=evidence_trust,
            final_score=final_score,
        )
        
        # ===== 7. Generate recommendations =====
        recommendations = cls._generate_recommendations(
            level=level,
            case_risk=case_risk,
            graph_risk=graph_risk,
            evidence_trust=evidence_trust,
        )
        
        # ===== 8. Return Result =====
        return RiskResult(
            score=round(final_score, 2),
            level=level,
            components={
                "case_risk": round(case_risk, 2),
                "graph_risk": round(graph_risk, 2),
                "fraud_score": round(fraud_score, 2),
                "evidence_trust": round(evidence_trust, 2),
            },
            weights=weights,
            factors=factors,
            recommendations=recommendations,
        )
    
    # ===== Private Helpers =====
    
    @classmethod
    def _validate_score(cls, value: float, name: str) -> float:
        """Validate score is between 0-100."""
        if value < 0 or value > 100:
            logger.warning(f"{name}={value} out of range (0-100), clamping")
            return min(max(value, 0), 100)
        return value
    
    @classmethod
    def _validate_weights(cls, weights: Dict[str, float]) -> Dict[str, float]:
        """Validate weights sum to 1.0."""
        required_keys = {"case", "graph", "fraud", "evidence"}
        missing = required_keys - set(weights.keys())
        if missing:
            raise ValueError(f"Missing weights: {missing}")
        
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        return weights
    
    @classmethod
    def _determine_level(cls, score: float) -> str:
        """Determine risk level from score."""
        if score >= cls.THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif score >= cls.THRESHOLDS["HIGH"]:
            return "HIGH"
        elif score >= cls.THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    @classmethod
    def _generate_factors(
        cls,
        case_risk: float,
        graph_risk: float,
        fraud_score: float,
        evidence_trust: float,
        final_score: float,
    ) -> List[str]:
        """Generate contributing factors."""
        factors = []
        
        if case_risk > 70:
            factors.append(f"High case risk detected ({case_risk:.1f})")
        elif case_risk > 50:
            factors.append(f"Moderate case risk detected ({case_risk:.1f})")
        
        if graph_risk > 70:
            factors.append(f"High graph risk detected ({graph_risk:.1f})")
        elif graph_risk > 50:
            factors.append(f"Moderate graph risk detected ({graph_risk:.1f})")
        
        if fraud_score > 70:
            factors.append(f"High fraud score detected ({fraud_score:.1f})")
        elif fraud_score > 50:
            factors.append(f"Moderate fraud score detected ({fraud_score:.1f})")
        
        if evidence_trust < 30:
            factors.append(f"Low evidence trust ({evidence_trust:.1f})")
        elif evidence_trust < 50:
            factors.append(f"Moderate evidence trust ({evidence_trust:.1f})")
        
        if not factors:
            factors.append("No significant risk factors detected")
        
        return factors
    
    @classmethod
    def _generate_recommendations(
        cls,
        level: str,
        case_risk: float,
        graph_risk: float,
        evidence_trust: float,
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if level == "CRITICAL":
            recommendations.append("🚨 Immediate investigation required")
            recommendations.append("📋 Escalate to senior investigator")
            recommendations.append("🔒 Secure all evidence immediately")
        
        elif level == "HIGH":
            recommendations.append("🔍 Prioritize investigation")
            recommendations.append("📊 Review all connected entities")
            recommendations.append("📝 Document all findings")
        
        elif level == "MEDIUM":
            recommendations.append("📋 Schedule follow-up review")
            recommendations.append("🔎 Monitor for escalation")
        
        else:  # LOW
            recommendations.append("✅ Routine monitoring continues")
            recommendations.append("📝 Schedule periodic risk reassessment")
        
        # Additional context-based recommendations
        if evidence_trust < 30:
            recommendations.append("📎 Collect additional evidence to increase trust score")
        
        if graph_risk > 70:
            recommendations.append("🔗 Investigate network connections for collusion patterns")
        
        return recommendations


# ============================================================================
# 3. LEGACY COMPATIBILITY (Untuk transisi)
# ============================================================================

class LegacyIntelligenceService:
    """
    LEGACY — Hanya untuk kompatibilitas selama transisi.
    
    Will be removed after Phase 2.
    """
    
    def __init__(self, session: AsyncSession):  # ← SEKARANG AsyncSession TERDEFINISI
        self.session = session
    
    async def analyze_case(self, case_id: str, fraud_score: float = 0) -> Dict[str, Any]:
        """
        Legacy analyze_case — still uses direct SQL.
        
        ⚠️ DEPRECATED: Use IntelligenceService.calculate() instead.
        """
        import warnings
        warnings.warn(
            "LegacyIntelligenceService.analyze_case() is deprecated. "
            "Use IntelligenceService.calculate() with repository-fetched data.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # 1. Get case risk
        result = await self.session.execute(
            text("SELECT risk_score FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        row = result.fetchone()
        case_risk = float(row[0]) if row and row[0] else 0
        
        # 2. Get graph risk
        from intelligence.graph.risk_analyzer import GraphRiskAnalyzer
        graph_data = await GraphRiskAnalyzer.calculate_graph_risk(case_id, self.session)
        graph_risk = graph_data.get("graph_risk", 0)
        
        # 3. Get evidence trust
        evidence_trust = await self.get_evidence_trust(case_id)
        
        # 4. Calculate using new pure service
        result = IntelligenceService.calculate(
            case_risk=case_risk,
            graph_risk=graph_risk,
            fraud_score=fraud_score,
            evidence_trust=evidence_trust,
        )
        
        return result.to_dict()
    
    async def get_evidence_trust(self, case_id: str) -> float:
        """Legacy evidence trust calculation."""
        result = await self.session.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN LOWER(status) = 'verified' THEN 1 END) as verified,
                COALESCE(AVG(trust_score), 0) as avg_trust
            FROM evidence 
            WHERE case_id = :case_id
        """), {"case_id": case_id})
        row = result.fetchone()
        
        total_evidence = row[0] or 0
        verified_evidence = row[1] or 0
        avg_trust = float(row[2]) if row[2] else 0
        
        if total_evidence > 0:
            verification_ratio = verified_evidence / total_evidence
            evidence_trust = (avg_trust * 0.7) + (verification_ratio * 100 * 0.3)
            return min(max(evidence_trust, 0), 100)
        return 0


# ============================================================================
# 4. FORMAT RESPONSE (Utility)
# ============================================================================

def format_risk_response(case_id: str, result: RiskResult) -> Dict[str, Any]:
    """Format RiskResult as API response."""
    return {
        "case_id": case_id,
        "risk_score": result.score,
        "risk_level": result.level,
        "components": result.components,
        "factors": result.factors,
        "recommendations": result.recommendations,
        "timestamp": datetime.now().isoformat(),
        "version": "v3.0",
    }