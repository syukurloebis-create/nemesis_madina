"""
Risk Command Repository — WRITE only.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Dict, Any

from backend.dtos.risk_snapshot_projection import RiskSnapshotProjection
from backend.domain.enums.risk_calculation_source import RiskCalculationSource
from backend.infrastructure.unit_of_work import IUnitOfWork


class IRiskCommandRepository(ABC):
    """Risk Command Repository — WRITE only."""

    @abstractmethod
    async def save_or_update(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        data: Dict[str, Any],
        calculated_by: RiskCalculationSource = RiskCalculationSource.SYSTEM,
    ) -> None:
        """Save or update risk score."""
        pass

    @abstractmethod
    async def update_case_snapshot(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        snapshot: RiskSnapshotProjection,  # ← DTO, bukan RiskResult
    ) -> None:
        """Update cases.latest_risk for dashboard."""
        pass