"""
Risk Application Service — Pure Orchestration.

SINGLE UNIT OF WORK per use case.
Atomic: risk_scores + latest_risk dalam satu transaksi.
"""

from uuid import UUID
from typing import Dict, Any, Optional
import logging

from backend.intelligence.service import IntelligenceService, RiskResult
from backend.services.risk_projection_service import RiskProjectionService
from backend.repositories.interfaces.graph_repository import IGraphRepository
from backend.repositories.interfaces.evidence_repository import IEvidenceRepository
from backend.domain.enums.risk_calculation_source import RiskCalculationSource
from backend.domain.value_objects.case_id import CaseId
from backend.infrastructure.unit_of_work import UnitOfWorkFactory

# ===== TAMBAHKAN SEMUA IMPORT =====
from backend.collectors.assemblers.graph_assembler import GraphAssembler
from backend.collectors.assemblers.evidence_assembler import EvidenceAssembler
from backend.calculators.graph_score_calculator import GraphScoreCalculator
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator
from backend.calculators.config import CalculatorConfig
# ================================

logger = logging.getLogger(__name__)


class RiskApplicationService:
    """Pure Orchestration — NO business logic."""

    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        graph_repo: IGraphRepository,
        evidence_repo: IEvidenceRepository,
        projection_service: RiskProjectionService,
        config: CalculatorConfig,  # ← TAMBAHKAN
    ):
        self._uow_factory = uow_factory
        self._graph_repo = graph_repo
        self._evidence_repo = evidence_repo
        self._projection_service = projection_service
        self._config = config  # ← TAMBAHKAN

    async def calculate_and_persist(
        self,
        case_id: UUID,
        fraud_score: float = 0,
        weights: Optional[Dict[str, float]] = None,
        calculated_by: RiskCalculationSource = RiskCalculationSource.API,
    ) -> Dict[str, Any]:
        """Calculate risk and persist to projection in a single transaction."""

        async with self._uow_factory() as uow:
            # 1. Get aggregate
            aggregate = await uow.cases.get(CaseId(case_id))
            case_risk = aggregate.latest_risk.score if aggregate and aggregate.latest_risk else 0

            # 2. Get graph → DTO → Calculator → score
            graph_summary = await self._graph_repo.get_summary(uow, case_id)
            graph_dto = GraphAssembler.assemble(graph_summary)
            graph_calc = GraphScoreCalculator.calculate(
                graph_dto,
                self._config.get_graph_weights()
            )
            graph_risk = graph_calc.score  # ← SEKARANG graph_risk TERDEFINISI

            # 3. Get evidence → DTO → Calculator → trust_score
            evidence_summary = await self._evidence_repo.get_summary(uow, case_id)
            evidence_dto = EvidenceAssembler.assemble(evidence_summary)
            evidence_calc = EvidenceScoreCalculator.calculate(
                evidence_dto,
                self._config.get_evidence_weights()
            )
            evidence_trust = evidence_calc.trust_score

            logger.info(
                "RiskApplicationService: Fetched data for case %s (case=%.2f, graph=%.2f, evidence=%.2f)",
                case_id,
                case_risk,
                graph_risk,
                evidence_trust,
            )

            # 4. Calculate via IntelligenceService
            result = IntelligenceService.calculate(
                case_risk=case_risk,
                graph_risk=graph_risk,
                fraud_score=fraud_score,
                evidence_trust=evidence_trust,
                weights=weights,
            )

            logger.info(
                "RiskApplicationService: Calculated risk for case %s (score=%.2f, level=%s)",
                case_id,
                result.score,
                result.level,
            )

            # 5. Save via ProjectionService
            await self._projection_service.save_projection(
                uow=uow,
                case_id=case_id,
                result=result,
                calculated_by=calculated_by,
            )

            # 6. SINGLE COMMIT
            await uow.commit()

            return result.to_dict()