# backend/mappers/dashboard_projection_mapper.py

from datetime import datetime
from typing import Optional
from backend.application.queries.dashboard_query import DashboardProjection
from backend.mappers.projection_mapping_result import ProjectionMappingResult
from backend.domain.summary_objects import (
    FraudSummary,
    RiskSummary,
    FraudPatternSummary,
    GraphSummary,
    ProcurementSummary,
    EvidenceSummary,
)
from backend.domain.enums.severity import Severity


class DashboardProjectionMapper:
    """Pure transformer: Projection → MappingResult."""

    def map(self, projection: DashboardProjection) -> ProjectionMappingResult:
        return ProjectionMappingResult(
            fraud_summary=self._to_fraud_summary(projection),
            risk_summary=self._to_risk_summary(projection),
            status=projection.status,
            updated_at=self._parse_timestamp(projection.last_updated),
            has_data=projection.analysis_count > 0,
            # ✅ FIXED: Use risk_score, not fraud_score
            risk_score=projection.risk_score or 0.0,
            graph_summary=self._to_graph_summary(projection),
            procurement_summary=self._to_procurement_summary(projection),
            evidence_summary=self._to_evidence_summary(projection),
        )

    def _to_fraud_summary(self, projection: DashboardProjection) -> FraudSummary:
        if projection.latest_fraud:
            fraud_data = projection.latest_fraud
            patterns = []
            raw_patterns = fraud_data.get('patterns', [])
            for p in raw_patterns:
                patterns.append(
                    FraudPatternSummary(
                        type=p.get('type', 'unknown'),
                        severity=Severity.from_string(p.get('severity', 'UNKNOWN')),
                        confidence=p.get('confidence', 0.0),
                        detected_at=self._parse_timestamp(p.get('detected_at', '')),
                        validated=p.get('validated', False),
                        description=p.get('description', ''),
                    )
                )
            return FraudSummary(
                overall_risk=Severity.from_string(fraud_data.get('overall_risk', 'UNKNOWN')),
                score=fraud_data.get('score', 0.0),
                total_patterns=fraud_data.get('total_patterns', 0),
                validated_patterns=fraud_data.get('validated_patterns', 0),
                highest_confidence=fraud_data.get('highest_confidence', 0.0),
                average_confidence=fraud_data.get('average_confidence', 0.0),
                active_alerts=fraud_data.get('active_alerts', 0),
                high_confidence=fraud_data.get('high_confidence', 0),
                patterns=patterns,
                engine='fraud',
                engine_status='OK',
            )
        return FraudSummary.empty()

    def _to_risk_summary(self, projection: DashboardProjection) -> RiskSummary:
        if projection.latest_risk:
            risk_data = projection.latest_risk
            return RiskSummary(
                level=projection.risk_level,
                # ✅ FIXED: Use risk_score, not fraud_score
                score=projection.risk_score or risk_data.get('score', 0.0),
                anomaly_score=risk_data.get('anomaly_score', 0.0),
                collusion_score=risk_data.get('collusion_score', 0.0),
                financial_score=risk_data.get('financial_score', 0.0),
                recommendations=risk_data.get('recommendations', []),
                engine='risk',
                engine_status='OK',
            )
        return RiskSummary.empty()

    def _to_graph_summary(self, projection: DashboardProjection) -> GraphSummary:
        if projection.latest_graph:
            graph_data = projection.latest_graph
            return GraphSummary(
                entities=graph_data.get('entities', 0),
                relationships=graph_data.get('relationships', 0),
                engine='graph',
                engine_status='OK',
            )
        return GraphSummary.empty()

    def _to_procurement_summary(self, projection: DashboardProjection) -> ProcurementSummary:
        if projection.latest_procurement:
            proc_data = projection.latest_procurement
            return ProcurementSummary(
                packages=proc_data.get('packages', 0),
                vendors=proc_data.get('vendors', 0),
                instansi_count=proc_data.get('instansi_count', 0),
                total_value=proc_data.get('total_value', 0.0),
                avg_value=proc_data.get('avg_value', 0.0),
                completed=proc_data.get('completed', 0),
                engine='procurement',
                engine_status='OK',
            )
        return ProcurementSummary.empty()

    def _to_evidence_summary(self, projection: DashboardProjection) -> EvidenceSummary:
        if projection.latest_evidence:
            ev_data = projection.latest_evidence
            return EvidenceSummary(
                total=ev_data.get('total', 0),
                verified=ev_data.get('verified', 0),
                rejected=ev_data.get('rejected', 0),
                pending=ev_data.get('pending', 0),
                avg_trust=ev_data.get('avg_trust', 0.0),
                avg_confidence=ev_data.get('avg_confidence', 0.0),
                engine='evidence',
                engine_status='OK',
            )
        return EvidenceSummary.empty()

    def _parse_timestamp(self, value: str) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return None
