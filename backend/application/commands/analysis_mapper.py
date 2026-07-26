# backend/application/commands/analysis_mapper.py

"""
NEMESIS Madina - Analyze Case Command
✅ Command for domain operations
✅ Separated from query
"""

from dataclasses import dataclass
from uuid import UUID
from typing import Any, Optional

from backend.application.mappers.analysis_mapper import map_to_analysis_bundle
from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.services.intelligence_service import IntelligenceDomainService
from backend.domain.value_objects.case_id import CaseId
from backend.infrastructure.domain_command_uow_factory import DomainCommandUoWFactory
from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.risk_score_calculator import RiskScoreCalculator
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator
from backend.calculators.graph_score_calculator import (
    GraphScoreCalculator,
    CalculatedGraph,
)
from backend.calculators.procurement_score_calculator import (
    ProcurementScoreCalculator,
    CalculatedProcurement,
)


@dataclass(frozen=True)
class AnalyzeCaseCommand:
    """Command to analyze a case."""
    case_id: UUID
    collector_results: Any  # CollectorResultRegistry


class AnalyzeCaseCommandHandler:
    def __init__(
        self,
        uow_factory: DomainCommandUoWFactory,
        fraud_calculator: FraudScoreCalculator,
        risk_calculator: RiskScoreCalculator,
        evidence_calculator: EvidenceScoreCalculator,
        graph_calculator: GraphScoreCalculator,       # ✅ Add
        procurement_calculator: ProcurementScoreCalculator,  # ✅ Add
    ):
        self._uow_factory = uow_factory
        self._fraud_calculator = fraud_calculator
        self._risk_calculator = risk_calculator
        self._evidence_calculator = evidence_calculator
        self._graph_calculator = graph_calculator
        self._procurement_calculator = procurement_calculator

    async def execute(self, command: AnalyzeCaseCommand) -> None:
        async with self._uow_factory.create() as uow:
            case_id_vo = CaseId(command.case_id)

            existing = await uow.cases.get(case_id_vo)

            if existing:
                aggregate = existing
                expected_version = existing.version
            else:
                aggregate = CaseIntelligenceAggregate(case_id=case_id_vo)
                expected_version = 0

            results = command.collector_results

            fraud_result = self._fraud_calculator.calculate(results.fraud) if results.fraud else None
            risk_result = self._risk_calculator.calculate(results.risk) if results.risk else None
            evidence_result = self._evidence_calculator.calculate(results.evidence) if results.evidence else None
            graph_result = self._graph_calculator.calculate(results.graph) if results.graph else None
            procurement_result = self._procurement_calculator.calculate(results.procurement) if results.procurement else None

            bundle = map_to_analysis_bundle(
                case_id=case_id_vo,
                collector_results=results,
                fraud_result=fraud_result,
                risk_result=risk_result,
                evidence_result=evidence_result,
                graph_result=graph_result,
                procurement_result=procurement_result,
            )

            IntelligenceDomainService.record_bundle(aggregate, bundle)
            uow.register_aggregate(aggregate, expected_version)