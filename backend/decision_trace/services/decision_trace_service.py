"""Decision Trace Service - Business logic untuk decision trace"""

from typing import Optional, List, Dict, Any
from uuid import UUID

from decision_trace.models import (
    DecisionTrace, DecisionTraceCreate, ExplainabilityResult, DecisionType
)
from decision_trace.repositories.decision_trace_repo import DecisionTraceRepository
from core.hash.hasher import UnifiedHasher


class DecisionTraceService:
    def __init__(self, repository: DecisionTraceRepository):
        self.repository = repository
    
    async def create_trace(self, trace_data: DecisionTraceCreate) -> DecisionTrace:
        """Create new decision trace"""
        trace = DecisionTrace(
            entity_id=trace_data.entity_id,
            entity_type=trace_data.entity_type,
            decision_type=trace_data.decision_type,
            score=trace_data.score,
            confidence=trace_data.confidence,
            reasons=trace_data.reasons,
            evidence_ids=trace_data.evidence_ids,
            feature_importance=trace_data.feature_importance,
            model_version=trace_data.model_version,
            metadata=trace_data.metadata
        )
        return await self.repository.create(trace)
    
    async def get_trace(self, trace_id: UUID) -> Optional[DecisionTrace]:
        """Get decision trace by ID"""
        return await self.repository.get_by_id(trace_id)
    
    async def explain_decision(
        self,
        trace_id: UUID,
        top_k: int = 5
    ) -> ExplainabilityResult:
        """Generate explanation for a decision"""
        trace = await self.repository.get_by_id(trace_id)
        if not trace:
            raise ValueError(f"Decision trace {trace_id} not found")
        
        # Sort features by contribution
        sorted_features = sorted(
            trace.feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:top_k]
        
        # Generate explanations
        explanations = []
        total_contribution = sum(abs(v) for _, v in sorted_features)
        
        for feature, importance in sorted_features:
            explanations.append({
                "factor": feature,
                "contribution": importance,
                "percentage": round(abs(importance) / total_contribution * 100, 1) if total_contribution > 0 else 0,
                "direction": "positive" if importance > 0 else "negative",
                "description": self._get_feature_description(feature)
            })
        
        return ExplainabilityResult(
            entity_id=trace.entity_id,
            decision_type=trace.decision_type,
            score=trace.score or 0.0,
            confidence=trace.confidence,
            explanations=explanations,
            evidence_count=len(trace.evidence_ids),
            trace_id=trace.trace_id,
            created_at=trace.created_at
        )
    
    async def get_entity_decisions(
        self,
        entity_id: str,
        limit: int = 50
    ) -> List[DecisionTrace]:
        """Get all decisions for an entity"""
        return await self.repository.get_by_entity(entity_id, limit)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get decision trace statistics"""
        return await self.repository.get_statistics()
    
    def _get_feature_description(self, feature: str) -> str:
        """Get human-readable description for a feature"""
        descriptions = {
            "single_bidder": "Hanya satu peserta yang mengikuti tender",
            "repeat_winner": "Vendor yang sama menang berulang kali",
            "price_anomaly": "Harga penawaran tidak wajar",
            "time_compression": "Waktu pengerjaan terlalu singkat",
            "shared_director": "Direktur yang sama dengan vendor lain",
            "collusion_risk": "Indikasi kolusi dengan peserta lain",
            "related_entity": "Hubungan kepemilikan dengan vendor lain"
        }
        return descriptions.get(feature, feature.replace("_", " ").title())
