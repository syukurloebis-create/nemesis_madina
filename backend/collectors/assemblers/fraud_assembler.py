"""
Fraud Assembler — Row → DTO.
"""

from typing import Tuple, Optional

from backend.repositories.rows.fraud_rows import FraudSummaryRow, FraudPatternRow
from backend.dtos.collector_dtos import FraudCollectorDTO, PatternDTO
from backend.domain.enums import EngineStatus, FallbackReason, Severity


class FraudAssembler:
    """Fraud Assembler — Row → DTO."""
    
    @classmethod
    def assemble(
        cls,
        summary_row: FraudSummaryRow,
        pattern_rows: Tuple[FraudPatternRow, ...],
        engine_status: EngineStatus = EngineStatus.OK,
        fallback_reason: Optional[FallbackReason] = None,
        error: Optional[str] = None
    ) -> FraudCollectorDTO:
        """Assemble Row Objects into DTO."""
        patterns = tuple(
            PatternDTO(
                pattern_type=row.pattern_type,
                severity=Severity.from_db(row.severity),  # ✅ Normalisasi enum
                confidence=float(row.confidence_score or 0),
                validated=row.is_validated or False,
                detected_at=row.detected_at
            )
            for row in pattern_rows
        )
        
        return FraudCollectorDTO(
            total_patterns=summary_row.total_patterns,
            critical=summary_row.critical,
            high=summary_row.high,
            medium=summary_row.medium,
            low=summary_row.low,
            avg_confidence=summary_row.avg_confidence,
            highest_confidence=summary_row.highest_confidence,
            validated_patterns=summary_row.validated,
            patterns=patterns,
            engine_status=engine_status,
            fallback_reason=fallback_reason,
            error=error
        )
    
    @classmethod
    def assemble_empty(cls) -> FraudCollectorDTO:
        return FraudCollectorDTO(
            total_patterns=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            avg_confidence=0,
            highest_confidence=0,
            validated_patterns=0,
            patterns=(),
            engine_status=EngineStatus.OK
        )