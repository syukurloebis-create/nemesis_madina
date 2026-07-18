"""
Procurement Mapper — HANYA mapping, TIDAK ada perhitungan.
"""

from backend.dtos.collector_dtos import ProcurementCollectorDTO
from backend.domain.summary_objects import ProcurementSummary
from backend.domain.enums import EngineType


class ProcurementMapper:
    """Procurement Mapper — HANYA mapping."""

    @staticmethod
    def to_summary(dto: ProcurementCollectorDTO) -> ProcurementSummary:
        """Convert DTO to ProcurementSummary."""
        return ProcurementSummary(
            packages=dto.packages,
            vendors=dto.vendors,
            instansi_count=dto.instansi_count,
            avg_value=dto.avg_value,
            total_value=dto.total_value,
            completed=0,
            engine=EngineType.PROCUREMENT,
            engine_status=dto.engine_status
        )