"""
Procurement Assembler — Row → DTO.
"""

from typing import Tuple, Optional  # ← TAMBAHKAN Optional
from backend.repositories.rows.procurement_rows import ProcurementSummaryRow
from backend.dtos.collector_dtos import ProcurementCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason


class ProcurementAssembler:
    """Procurement Assembler — Row → DTO."""

    @classmethod
    def assemble(
        cls,
        row: ProcurementSummaryRow,
        engine_status: EngineStatus = EngineStatus.OK,
        fallback_reason: Optional[FallbackReason] = None,
        error: Optional[str] = None
    ) -> ProcurementCollectorDTO:
        return ProcurementCollectorDTO(
            packages=row.packages,
            vendors=row.vendors,
            instansi_count=row.instansi_count,
            avg_value=row.avg_value,
            total_value=row.total_value,
            engine_status=engine_status,
            fallback_reason=fallback_reason,
            error=error
        )

    @classmethod
    def assemble_empty(cls) -> ProcurementCollectorDTO:
        return ProcurementCollectorDTO(
            packages=0,
            vendors=0,
            instansi_count=0,
            avg_value=0,
            total_value=0,
            engine_status=EngineStatus.OK
        )