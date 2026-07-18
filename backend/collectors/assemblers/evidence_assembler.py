"""
Evidence Assembler — Row → DTO.
"""

from typing import Tuple, Optional  # ← TAMBAHKAN Optional
from backend.repositories.rows.evidence_rows import EvidenceSummaryRow
from backend.dtos.collector_dtos import EvidenceCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason


class EvidenceAssembler:
    """Evidence Assembler — Row → DTO."""

    @classmethod
    def assemble(
        cls,
        row: EvidenceSummaryRow,
        engine_status: EngineStatus = EngineStatus.OK,
        fallback_reason: Optional[FallbackReason] = None,
        error: Optional[str] = None
    ) -> EvidenceCollectorDTO:
        return EvidenceCollectorDTO(
            total=row.total,
            verified=row.verified,
            rejected=row.rejected,
            pending=row.pending,
            avg_trust=row.avg_trust,
            avg_confidence=row.avg_confidence,
            engine_status=engine_status,
            fallback_reason=fallback_reason,
            error=error
        )

    @classmethod
    def assemble_empty(cls) -> EvidenceCollectorDTO:
        return EvidenceCollectorDTO(
            total=0,
            verified=0,
            rejected=0,
            pending=0,
            avg_trust=0,
            avg_confidence=0,
            engine_status=EngineStatus.OK
        )