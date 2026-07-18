"""
Finding Intelligence Engine - PURE FUNCTION (Stateless)
"""

from typing import List, Optional

from backend.domain.finding_intelligence import (
    FindingIntelligence,
    IntelligenceTimeline,
    IntelligenceEvidence,
    IntelligenceDecision,
    IntelligenceDrivers
)
from backend.application.dto.finding_analysis_input import FindingAnalysisInput
from backend.domain.policies.intelligence_policy import IntelligencePolicy


class FindingIntelligenceEngine:
    """
    Finding Intelligence Engine - PURE FUNCTION.
    """

    @staticmethod
    def process(
        self,
        data: FindingAnalysisInput,
        config: Optional[IntelligencePolicy] = None
    ) -> FindingIntelligence:
        """Proses data menjadi FindingIntelligence domain object."""
        cfg = config or self.config

        finding = data.finding
        timeline = data.timeline
        evidence = data.evidence
        decision = data.decision
        actions = data.actions
        sla_breaches = data.sla_breaches

        # Timeline summary (dengan data kosong)
        timeline_summary = IntelligenceTimeline(
            events=len(timeline),
            sla_breach=len(sla_breaches),
            evidence_actions=len(actions),
            last_event=timeline[-1].created_at if timeline else None
        )

        # Evidence summary - menggunakan data aktual
        evidence_summary = self._generate_evidence_summary(evidence)

        # Decision summary
        decision_summary = IntelligenceDecision(
            status=decision.status if decision else cfg.DEFAULT_DECISION_STATUS,
            confidence=decision.confidence if decision else 0,
            actor=decision.actor if decision else None
        )

        # Base score
        base_score = FindingIntelligenceEngine._calculate_base_score(
            evidence_summary,
            decision_summary,
            len(sla_breaches),
            cfg
        )
        intelligence_score = min(base_score + cfg.SCORE_DELTA, cfg.MAX_SCORE)

        # Level
        level = FindingIntelligenceEngine._determine_level(intelligence_score, cfg)

        # Drivers
        drivers = IntelligenceDrivers(
            finding_risk=base_score,
            sla_breach=len(sla_breaches),
            evidence_confidence=evidence_summary.confidence,
            decision_status=decision_summary.status,
            decision_confidence=decision_summary.confidence
        )

        # Explanations
        explanations = FindingIntelligenceEngine._generate_explanations(
            timeline_summary,
            evidence_summary,
            decision_summary,
            len(sla_breaches)
        )

        # Recommendations
        recommendations = FindingIntelligenceEngine._generate_recommendations(
            evidence_summary,
            decision_summary,
            len(sla_breaches)
        )

        return FindingIntelligence(
            finding_id=finding.id,
            base_score=base_score,
            intelligence_score=intelligence_score,
            delta=intelligence_score - base_score,
            level=level,
            drivers=drivers,
            explanations=explanations,
            timeline=timeline_summary,
            evidence=evidence_summary,
            decision=decision_summary,
            recommendations=recommendations
        )


    @staticmethod
    def _calculate_base_score(
        evidence: IntelligenceEvidence,
        decision: IntelligenceDecision,
        sla_breach_count: int,
        policy: IntelligencePolicy
    ) -> float:
        """Calculate base score using policy."""
        score = policy.BASE_SCORE

        if evidence.total > 0:
            score += min(evidence.confidence * policy.EVIDENCE_WEIGHT, policy.MAX_EVIDENCE_BONUS)
        else:
            score -= policy.NO_EVIDENCE_PENALTY

        if decision.status == "CONFIRMED":
            score += policy.DECISION_CONFIRMED_BONUS
        elif decision.status == "REJECTED":
            score -= policy.DECISION_REJECTED_PENALTY

        score -= min(sla_breach_count * policy.SLA_BREACH_WEIGHT, policy.MAX_SLA_PENALTY)

        return max(policy.MIN_SCORE, min(policy.MAX_SCORE, score))

    @staticmethod
    def _determine_level(score: float, policy: IntelligencePolicy) -> str:
        """Determine level based on policy thresholds."""
        if score >= policy.LEVEL_CRITICAL_THRESHOLD:
            return "CRITICAL"
        elif score >= policy.LEVEL_HIGH_THRESHOLD:
            return "HIGH"
        elif score >= policy.LEVEL_MEDIUM_THRESHOLD:
            return "MEDIUM"
        else:
            return "LOW"

    @staticmethod
    def _generate_explanations(
        timeline: IntelligenceTimeline,
        evidence: IntelligenceEvidence,
        decision: IntelligenceDecision,
        sla_breach_count: int
    ) -> List[str]:
        """Generate explanations based on data."""
        explanations = []

        if sla_breach_count > 0:
            explanations.append(f"SLA breach detected: {sla_breach_count} times")
        if evidence.total == 0:
            explanations.append("No evidence associated with this finding")
        if evidence.confidence < 30:
            explanations.append("Low evidence confidence requires additional validation")
        if timeline.events == 0:
            explanations.append("No timeline events recorded")

        if not explanations:
            explanations.append("Finding is well-documented")

        return explanations

    @staticmethod
    def _generate_recommendations(
        evidence: IntelligenceEvidence,
        decision: IntelligenceDecision,
        sla_breach_count: int
    ) -> List[str]:
        """Generate recommendations based on data."""
        recommendations = []

        if evidence.total == 0:
            recommendations.append("Collect additional evidence to support this finding")

        if evidence.confidence < 30:
            recommendations.append("Perform additional evidence validation")

        if decision.status == "PENDING":
            recommendations.append("Await analyst decision")

        if sla_breach_count > 0:
            recommendations.append("Review SLA breach cause and implement corrective actions")

        if not recommendations:
            recommendations.append("Continue monitoring")

        return recommendations

    def _generate_evidence_summary(self, evidence_data: List) -> IntelligenceEvidence:
        """
        Generate evidence summary dari data aktual di database.
        Menggunakan confidence_score dan trust_score dari tabel evidence.
        """
        if not evidence_data:
            return IntelligenceEvidence(
                total=0,
                confidence=0.0,
                source="evidence",
                verified=0,
                trust_score=0.0,
                avg_confidence=0.0
            )
    
        total = len(evidence_data)
        verified_count = 0
        confidence_sum = 0
        trust_sum = 0
    
        for e in evidence_data:
            if hasattr(e, 'confidence_score'):
                confidence_sum += e.confidence_score or 0
                trust_sum += getattr(e, 'trust_score', 0) or 0
                if hasattr(e, 'status') and e.status == 'verified':
                    verified_count += 1
            elif isinstance(e, dict):
                confidence_sum += e.get("confidence_score", 0)
                trust_sum += e.get("trust_score", 0)
                if e.get("status") == 'verified':
                    verified_count += 1
    
        avg_confidence = confidence_sum / total if total > 0 else 0
        avg_trust = trust_sum / total if total > 0 else 0
    
        # Weighted score: 75% confidence, 25% trust
        confidence = (avg_confidence * 0.75) + (avg_trust * 0.25)
    
        return IntelligenceEvidence(
            total=total,
            confidence=round(confidence, 2),
            source="evidence",
            verified=verified_count,
            trust_score=round(avg_trust, 2),
            avg_confidence=round(avg_confidence, 2)
        )