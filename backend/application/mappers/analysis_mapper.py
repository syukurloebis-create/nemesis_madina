# backend/application/mappers/analysis_mapper.py

"""
NEMESIS Madina - Analysis Mapper
Maps DTOs + Calculated Results → Domain Value Objects.
✅ Mapper is in application layer (not domain)
✅ Domain does NOT know DTOs
✅ Uses calculators for business logic
"""

from typing import Optional

from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.legacy_fraud_pattern import LegacyFraudPattern
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.graph_analysis import GraphAnalysis
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis
from backend.domain.value_objects.analysis_bundle import AnalysisBundle
from backend.domain.enums.risk_level import RiskLevel

from backend.dtos.collector_dtos import (
    FraudCollectorDTO,
    RiskCollectorDTO,
    EvidenceCollectorDTO,
    GraphCollectorDTO,
    ProcurementCollectorDTO,
)
from backend.calculators.risk_score_calculator import (
    RiskScoreCalculator,
    CalculatedRisk,
)
from backend.calculators.fraud_score_calculator import FraudScoreCalculator, CalculatedFraud
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator, CalculatedEvidence
from backend.calculators.graph_score_calculator import CalculatedGraph
from backend.calculators.procurement_score_calculator import CalculatedProcurement  # Also add this
from backend.infrastructure.parallel_executor import CollectorResultRegistry


def map_to_fraud_analysis(
    case_id: CaseId,
    dto: Optional[FraudCollectorDTO],
    result: Optional[CalculatedFraud],
) -> Optional[FraudAnalysis]:
    """Map FraudCollectorDTO + CalculatedFraud → FraudAnalysis."""
    if dto is None or result is None:
        return None

    patterns = []
    for p in dto.patterns:
        legacy = LegacyFraudPattern(
            type=p.pattern_type,
            severity=p.severity.value if hasattr(p.severity, 'value') else str(p.severity),
            confidence=p.confidence,
            validated=p.validated,
            pattern_id=None,
        )
        patterns.append(legacy.to_domain())

    return FraudAnalysis(
        case_id=str(case_id),
        patterns=patterns,
        overall_risk=RiskLevel.from_severity(result.overall_risk),
        score=result.score,
        total_patterns=dto.total_patterns,
        active_alerts=result.active_alerts,
        high_confidence=result.high_confidence,
        validated_patterns=dto.validated_patterns,
        highest_confidence=dto.highest_confidence,
        average_confidence=dto.avg_confidence,
    )


def map_to_risk_assessment(
    case_id: CaseId,
    dto: Optional[RiskCollectorDTO],
    result: Optional[CalculatedRisk],
) -> Optional[RiskAssessment]:
    """Map RiskCollectorDTO + CalculatedRisk → RiskAssessment.
    
    This is a COMPATIBILITY ADAPTER between the new ADR-018 calculator
    and the old RiskAssessment VO contract.
    
    TODO: Migrate RiskAssessment to ADR-018 contract.
    """
    if dto is None or result is None:
        return None

    return RiskAssessment(
        case_id=str(case_id),
        
        score=result.score,
        level=result.level,
        
        confidence=result.score,
        
        anomaly_score=dto.anomaly_score,
        collusion_score=dto.collusion_score,
        financial_score=dto.financial_score,
        
        status=result.engine_status.value if hasattr(result.engine_status, 'value') else str(result.engine_status),
        
        factors=list(result.recommendations) if result.recommendations else [],
    )


def map_to_evidence_verification(
    case_id: CaseId,
    dto: Optional[EvidenceCollectorDTO],
    result: Optional[CalculatedEvidence],
) -> Optional[EvidenceVerification]:
    """Map EvidenceCollectorDTO + CalculatedEvidence → EvidenceVerification."""
    if dto is None or result is None:
        return None

    return EvidenceVerification(
        case_id=str(case_id),
        verified_count=dto.verified,
        pending_count=dto.pending,
        rejected_count=dto.rejected,
        total_count=dto.total,
        avg_trust=dto.avg_trust,
        avg_confidence=dto.avg_confidence,
        score=result.score,
        level=result.level,
        confidence_level=result.confidence_level,
    )


def map_to_graph_analysis(
    case_id: CaseId,
    dto: GraphCollectorDTO,
    result: Optional[CalculatedGraph] = None, 
) -> Optional[GraphAnalysis]:
    """Map GraphCollectorDTO + CalculatedGraph → GraphAnalysis."""
    if dto is None:
        return None

    return GraphAnalysis(
        case_id=str(case_id),
        entities=dto.entities,
        relationships=dto.relationships,
        density=result.density if result else 0.0,
        complexity_score=result.score if result else 0.0,
        engine_status=(
            result.engine_status.value
            if result and hasattr(result.engine_status, 'value')
            else str(dto.engine_status)
        ),
    )


def map_to_procurement_analysis(
    case_id: CaseId,
    dto: ProcurementCollectorDTO,
    result: Optional[CalculatedProcurement] = None,
) -> Optional[ProcurementAnalysis]:
    """Map ProcurementCollectorDTO + CalculatedProcurement → ProcurementAnalysis."""
    if dto is None:
        return None

    return ProcurementAnalysis(
        case_id=str(case_id),
        packages=dto.packages,
        vendors=dto.vendors,
        instansi_count=dto.instansi_count,
        total_value=dto.total_value,
        avg_value=dto.avg_value,

        risk_score=result.risk_score if result else 0.0,
        confidence=result.confidence if result else 0.0,

        completed=False,  # TODO: Determine from data
        engine_status=(
            result.engine_status.value
            if result and hasattr(result.engine_status, 'value')
            else str(dto.engine_status)
        ),
    )


def map_to_analysis_bundle(
    case_id: CaseId,
    collector_results: CollectorResultRegistry,
    fraud_result: Optional[CalculatedFraud],
    risk_result: Optional[CalculatedRisk],
    evidence_result: Optional[CalculatedEvidence],
    graph_result: Optional[CalculatedGraph] = None,
    procurement_result: Optional[CalculatedProcurement] = None,
) -> AnalysisBundle:
    """Pure transformation — NO calculator logic."""
    return AnalysisBundle(
        fraud=map_to_fraud_analysis(case_id, collector_results.fraud, fraud_result),
        risk=map_to_risk_assessment(case_id, collector_results.risk, risk_result),
        evidence=map_to_evidence_verification(case_id, collector_results.evidence, evidence_result),
        graph=map_to_graph_analysis(case_id, collector_results.graph, graph_result),
        procurement=map_to_procurement_analysis(case_id, collector_results.procurement, procurement_result),
    )
