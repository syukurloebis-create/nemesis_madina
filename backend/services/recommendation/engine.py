"""
Recommendation Engine
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)


class RecommendationPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"


@dataclass
class Recommendation:
    id: UUID = field(default_factory=uuid4)
    case_id: str = ""
    title: str = ""
    description: str = ""
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    impact: float = 0.0
    confidence: float = 0.0
    estimated_recovery: float = 0.0
    actions: List[Dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""
    evidence_ids: List[str] = field(default_factory=list)
    status: RecommendationStatus = RecommendationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "impact": self.impact,
            "confidence": self.confidence,
            "estimated_recovery": self.estimated_recovery,
            "actions": self.actions,
            "reasoning": self.reasoning,
            "evidence_ids": self.evidence_ids,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class RecommendationEngine:
    def __init__(self):
        self.recommendations: Dict[str, Recommendation] = {}
        self.templates = {
            "audit_vendor": {
                "title": "Audit Vendor",
                "description": "Conduct comprehensive audit of vendor activities",
                "actions": [
                    {"label": "Start Vendor Audit", "endpoint": "/api/v1/vendors/{vendor_id}/audit"},
                    {"label": "View Vendor Profile", "endpoint": "/api/v1/vendors/{vendor_id}"}
                ]
            },
            "investigate_collusion": {
                "title": "Investigate Collusion",
                "description": "Investigate potential collusion between entities",
                "actions": [
                    {"label": "Start Investigation", "endpoint": "/api/v1/investigation/start"},
                    {"label": "View Graph", "endpoint": "/api/v1/graph/{case_id}"}
                ]
            },
            "secure_evidence": {
                "title": "Secure Evidence",
                "description": "Secure and preserve evidence for legal proceedings",
                "actions": [
                    {"label": "Secure Evidence", "endpoint": "/api/v1/evidence/{case_id}/secure"},
                    {"label": "View Evidence", "endpoint": "/api/v1/evidence/{case_id}"}
                ]
            }
        }

    async def generate_recommendations(
        self,
        case_id: str,
        risk_score,
        evidence_data: List[Dict[str, Any]],
        graph_data: Dict[str, Any]
    ) -> List[Recommendation]:
        recommendations = []

        if risk_score.overall > 70:
            rec = self._create_recommendation(case_id, "investigate_collusion", risk_score, evidence_data)
            if rec:
                recommendations.append(rec)

        if risk_score.components.get("evidence_score", 0) < 30:
            rec = self._create_recommendation(case_id, "secure_evidence", risk_score, evidence_data)
            if rec:
                recommendations.append(rec)

        if risk_score.components.get("fraud_score", 0) > 60:
            rec = self._create_recommendation(case_id, "audit_vendor", risk_score, evidence_data)
            if rec:
                recommendations.append(rec)

        return recommendations

    def _create_recommendation(self, case_id: str, template_key: str, risk_score, evidence_data: List[Dict[str, Any]]) -> Optional[Recommendation]:
        template = self.templates.get(template_key)
        if not template:
            return None

        priority = RecommendationPriority.CRITICAL if risk_score.overall > 80 else RecommendationPriority.HIGH
        impact = min(risk_score.overall * 1.2, 100)

        return Recommendation(
            case_id=case_id,
            title=template["title"],
            description=template["description"],
            priority=priority,
            impact=impact,
            confidence=risk_score.confidence,
            estimated_recovery=impact * 1000000,
            actions=template["actions"],
            reasoning=f"Based on risk assessment (Score: {risk_score.overall:.1f})",
            evidence_ids=[e.get("id") for e in evidence_data[:3] if e.get("id")]
        )


recommendation_engine = RecommendationEngine()
