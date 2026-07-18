"""
NEMESIS Madina - Analysis Mapper
Maps DTOs to Domain Value Objects.
✅ Mapper is in application layer (not domain)
✅ Domain does NOT know DTOs
✅ Returns Optional (may be None)
"""

from typing import Optional

from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.fraud_pattern import FraudPattern
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.graph_analysis import GraphAnalysis
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis
from backend.domain.value_objects.analysis_bundle import AnalysisBundle
from backend.domain.dtos.collector_dtos import CollectorResultRegistry


def map_to_fraud_analysis(results: CollectorResultRegistry) -> Optional[FraudAnalysis]:
    """Map collector result to FraudAnalysis VO."""
    fraud = results.fraud
    if not fraud:
        return None
    
    patterns = [
        FraudPattern(
            type=p.type,
            severity=p.severity,
            confidence=p.confidence,
            validated=p.validated,
            detected_at=p.detected_at,
        )
        for p in fraud.signals.patterns
    ]
    
    return FraudAnalysis(
        case_id=str(fraud.case_id),
        patterns=patterns,
        overall_risk=fraud.overall_risk,
        score=fraud.score,
        total_patterns=fraud.total_patterns,
        active_alerts=fraud.active_alerts,
        high_confidence=fraud.high_confidence,
        validated_patterns=fraud.validated_patterns,
        highest_confidence=fraud.highest_confidence,
        average_confidence=fraud.average_confidence,
    )


def map_to_risk_assessment(results: CollectorResultRegistry) -> Optional[RiskAssessment]:
    """Map collector result to RiskAssessment VO."""
    risk = results.risk
    if not risk:
        return None
    
    return RiskAssessment(
        case_id=str(risk.case_id),
        score=risk.score,
        level=risk.level,
        anomaly_score=risk.anomaly_score,
        collusion_score=risk.collusion_score,
        financial_score=risk.financial_score,
        status=risk.status,
    )


def map_to_evidence_verification(results: CollectorResultRegistry) -> Optional[EvidenceVerification]:
    """Map collector result to EvidenceVerification VO."""
    evidence = results.evidence
    if not evidence:
        return None
    
    return EvidenceVerification(
        case_id=str(evidence.case_id),
        score=evidence.score,
        level=evidence.level,
        total=evidence.total,
        verified=evidence.verified,
        rejected=evidence.rejected,
        pending=evidence.pending,
        avg_trust=evidence.avg_trust,
        avg_confidence=evidence.avg_confidence,
        confidence_level=evidence.confidence_level,
    )


def map_to_graph_analysis(results: CollectorResultRegistry) -> Optional[GraphAnalysis]:
    """Map collector result to GraphAnalysis VO."""
    graph = results.graph
    if not graph:
        return None
    
    return GraphAnalysis(
        case_id=str(graph.case_id),
        entities=graph.entities,
        relationships=graph.relationships,
        engine_status=graph.engine_status,
    )


def map_to_procurement_analysis(results: CollectorResultRegistry) -> Optional[ProcurementAnalysis]:
    """Map collector result to ProcurementAnalysis VO."""
    procurement = results.procurement
    if not procurement:
        return None
    
    return ProcurementAnalysis(
        case_id=str(procurement.case_id),
        packages=procurement.packages,
        vendors=procurement.vendors,
        instansi_count=procurement.instansi_count,
        total_value=procurement.total_value,
        avg_value=procurement.avg_value,
        completed=procurement.completed,
        engine_status=procurement.engine_status,
    )


def map_to_analysis_bundle(results: CollectorResultRegistry) -> AnalysisBundle:
    """Map all collector results to AnalysisBundle."""
    return AnalysisBundle(
        fraud=map_to_fraud_analysis(results),
        risk=map_to_risk_assessment(results),
        evidence=map_to_evidence_verification(results),
        graph=map_to_graph_analysis(results),
        procurement=map_to_procurement_analysis(results),
    )