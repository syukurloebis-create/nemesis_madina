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
        """Calculate canonical risk and persist it as a projection."""

        async with self._uow_factory.create() as uow:
            # ============================================================
            # 1. FINDINGS RISK
            # ============================================================
            findings_risk = await self._calculate_findings_risk(
                uow,
                case_id,
            )

            # ============================================================
            # 2. GRAPH RISK
            # ============================================================
            graph_summary = await self._graph_repo.get_summary(
                uow,
                case_id,
            )

            graph_dto = GraphAssembler.assemble(graph_summary)

            graph_calc = GraphScoreCalculator.calculate(
                graph_dto,
                self._config.get_graph_weights(),
            )

            graph_risk = graph_calc.score

            # ============================================================
            # 3. EVIDENCE RISK
            # ============================================================
            evidence_summary = await self._evidence_repo.get_summary(
                uow,
                case_id,
            )

            evidence_dto = EvidenceAssembler.assemble(
                evidence_summary,
            )

            evidence_calc = EvidenceScoreCalculator.calculate(
                evidence_dto,
                self._config.get_evidence_weights(),
            )

            # EvidenceScoreCalculator.score = evidence quality/trust.
            #
            # Canonical risk uses the opposite direction:
            # high evidence quality  -> low evidence risk
            # low evidence quality   -> high evidence risk
            #
            # NO_DATA is not automatically treated as maximum risk.
            if evidence_dto.total > 0:
                evidence_risk = max(
                    0.0,
                    min(
                        100.0,
                        100.0 - float(evidence_calc.score),
                    ),
                )
            else:
                evidence_risk = 0.0

            # ============================================================
            # 4. CANONICAL RISK ENGINE
            # ============================================================
            result = IntelligenceService.calculate(
                findings_risk=findings_risk,
                graph_risk=graph_risk,
                fraud_risk=fraud_score,
                evidence_risk=evidence_risk,
                weights=weights,
            )

            logger.info(
                (
                    "RiskApplicationService: "
                    "case=%s findings=%.2f graph=%.2f "
                    "fraud=%.2f evidence=%.2f "
                    "score=%.2f level=%s"
                ),
                case_id,
                findings_risk,
                graph_risk,
                fraud_score,
                evidence_risk,
                result.score,
                result.level,
            )

            # ============================================================
            # 5. PERSIST CANONICAL PROJECTION
            # ============================================================
            await self._projection_service.save_projection(
                uow=uow,
                case_id=case_id,
                result=result,
                calculated_by=calculated_by,
            )

            # ============================================================
            # 6. COMMIT
            # ============================================================
            await uow.commit()

            return result.to_dict()


    async def _calculate_findings_risk(
        self,
        uow,
        case_id: UUID,
    ) -> float:
        """
        Calculate case-level findings risk.

        Temporary inline SQL implementation.
        This can later move into FindingRepository/FindingScoreCalculator
        without changing the canonical Risk Engine contract.
        """
        from sqlalchemy import text

        result = await uow.session.execute(
            text(
                """
                SELECT
                    COUNT(*) AS total,
                    COUNT(
                        CASE
                            WHEN severity = 'CRITICAL' THEN 1
                        END
                    ) AS critical,
                    COUNT(
                        CASE
                            WHEN severity = 'HIGH' THEN 1
                        END
                    ) AS high
                FROM findings
                WHERE case_id = :case_id
                """
            ),
            {"case_id": str(case_id)},
        )

        row = result.fetchone()

        total = int(row[0]) if row and row[0] else 0
        critical = int(row[1]) if row and row[1] else 0
        high = int(row[2]) if row and row[2] else 0

        if total == 0:
            return 0.0

        return float(
            min(
                100,
                (critical * 30) + (high * 15),
            )
        )