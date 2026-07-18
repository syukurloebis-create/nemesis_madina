"""
Risk Projection Service — Pure Orchestration.

Menerima RiskResult, menyimpan ke risk_scores via CommandRepository.
TIDAK ada business logic.
"""

from uuid import UUID
import logging

from backend.intelligence.service import RiskResult
from backend.domain.enums.risk_calculation_source import RiskCalculationSource
from backend.repositories.interfaces.risk_command_repository import IRiskCommandRepository
from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.mappers.risk_projection_mapper import RiskProjectionMapper

logger = logging.getLogger(__name__)


class RiskProjectionService:
    """Pure Orchestration — NO business logic, NO SQLAlchemy."""

    def __init__(
        self,
        command_repo: IRiskCommandRepository,
    ):
        self._command_repo = command_repo

    async def save_projection(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        result: RiskResult,
        calculated_by: RiskCalculationSource = RiskCalculationSource.SYSTEM,
    ) -> None:
        # 1. risk_scores
        data = RiskProjectionMapper.to_projection_data(result)
        await self._command_repo.save_or_update(uow, case_id, data, calculated_by)

        # 2. cases.latest_risk (via DTO) - HANYA SEKALI
        snapshot = RiskProjectionMapper.to_case_snapshot(result)
        await self._command_repo.update_case_snapshot(uow, case_id, snapshot)

        # ✅ HAPUS duplikasi call kedua
        logger.info("Successfully saved risk for case %s", case_id)
