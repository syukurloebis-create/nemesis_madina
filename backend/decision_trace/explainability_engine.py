"""Explainability Engine - Generate human-readable explanations"""

from typing import Dict, Any, List
from backend.decision_trace.models import DecisionTrace, ExplainabilityResult


class ExplainabilityEngine:
    """Engine untuk menghasilkan penjelasan yang dapat diaudit"""
    
    @staticmethod
    def generate_audit_narrative(explanation: ExplainabilityResult) -> str:
        """Generate audit-ready narrative"""
        lines = []
        lines.append("=" * 60)
        lines.append(f"AUDIT TRAIL: {explanation.decision_type.value.upper()}")
        lines.append("=" * 60)
        lines.append(f"Entity ID: {explanation.entity_id}")
        lines.append(f"Score: {explanation.score:.3f}")
        lines.append(f"Confidence: {explanation.confidence:.3f}")
        lines.append(f"Decision Time: {explanation.created_at.isoformat()}")
        lines.append("")
        lines.append("CONTRIBUTING FACTORS:")
        
        for exp in explanation.explanations:
            direction = "INCREASES" if exp['direction'] == 'positive' else "DECREASES"
            lines.append(f"  - {exp['factor']}: {exp['contribution']:+.3f} ({direction})")
            lines.append(f"    {exp['description']}")
        
        lines.append("")
        lines.append(f"Total Evidence References: {explanation.evidence_count}")
        lines.append(f"Trace ID: {explanation.trace_id}")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_json_report(explanation: ExplainabilityResult) -> Dict[str, Any]:
        """Generate JSON report for API response"""
        return {
            "audit_id": str(explanation.trace_id),
            "entity_id": explanation.entity_id,
            "score": explanation.score,
            "confidence": explanation.confidence,
            "factors": [
                {
                    "name": exp['factor'],
                    "contribution": exp['contribution'],
                    "percentage": exp['percentage'],
                    "direction": exp['direction'],
                    "description": exp['description']
                }
                for exp in explanation.explanations
            ],
            "evidence_count": explanation.evidence_count,
            "timestamp": explanation.created_at.isoformat()
        }
