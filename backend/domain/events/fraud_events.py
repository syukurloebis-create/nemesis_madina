"""
NEMESIS Madina - Fraud Domain Events
✅ Uses payload pattern (consistent with Risk, Evidence, Application)
✅ Carries Value Objects, not dict
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional, Mapping
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.legacy_fraud_pattern import LegacyFraudPattern
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.fraud_payload import FraudPayload
from backend.domain.value_objects.fraud_pattern import (
    FraudPattern,
    FraudPatternType,
    FraudPatternSeverity,
)
from backend.domain.events.base import DomainEvent


@dataclass(frozen=True)
class FraudAnalysisCompleted(DomainEvent[FraudPayload]):
    """New-style event — DomainEvent[FraudPayload]."""
    EVENT_NAME = "FraudAnalysisCompleted"
    EVENT_VERSION = "1"


class FraudAnalysisRecorded(FraudAnalysisCompleted):
    """
    Compatibility adapter for old aggregate calls.

    Supports both:
    - Legacy: FraudAnalysisRecorded(case_id=..., analysis=...)
    - Modern: FraudAnalysisRecorded(payload=..., metadata=...)
    """

    def __init__(
        self,
        case_id: Optional[CaseId] = None,
        analysis: Optional[FraudAnalysis] = None,
        payload: Optional[FraudPayload] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ):
        # Build payload if not provided
        if payload is None:
            if case_id is None or analysis is None:
                raise ValueError(
                    "FraudAnalysisRecorded requires either "
                    "(case_id, analysis) or payload"
                )
            payload = FraudPayload(
                case_id=case_id,
                analysis=analysis,
                patterns=tuple(analysis.patterns) if analysis and analysis.patterns else (),
            )

        super().__init__(
            payload=payload,
            metadata=metadata,
        )

    @property
    def event_name(self) -> str:
        return "FraudAnalysisRecorded"

    @property
    def case_id(self):
        return self.payload.case_id

    @property
    def analysis(self):
        return self.payload.analysis


# ============================================================================
# COMPATIBILITY LAYER (Old Contract)
# ============================================================================

# Re-export FraudPattern for backward compatibility
FraudPattern = FraudPattern
FraudPatternType = FraudPatternType
FraudPatternSeverity = FraudPatternSeverity


class FraudDetectionCompleted(FraudAnalysisRecorded):
    """
    Compatibility adapter for old test contract.
    ✅ Inherits from FraudAnalysisRecorded
    ✅ Maintains old event name
    """
    EVENT_NAME = "FraudDetectionCompleted"
    EVENT_VERSION = "1"

    @property
    def event_name(self) -> str:
        return "FraudDetectionCompleted"


class FraudDetectionStarted(DomainEvent):
    """
    Compatibility adapter for old test contract.
    ✅ Stub event for tests that expect it
    """
    EVENT_NAME = "FraudDetectionStarted"
    EVENT_VERSION = "1"

    def __init__(self, metadata=None, payload=None):
        self.metadata = metadata
        self.payload = payload
    
    @property
    def event_name(self) -> str:
        return "FraudDetectionStarted"

    def FraudPattern(
        type: str,
        severity: str,
        confidence: float,
        validated: bool = False,
    ) -> LegacyFraudPattern:
        """
        Legacy fraud pattern constructor for test compatibility.
        ✅ Returns LegacyFraudPattern (which converts to domain)
        """
        return LegacyFraudPattern(
            type=type,
            severity=severity,
            confidence=confidence,
            validated=validated,
        )


# Export old names
__all__ = [
    # New
    'FraudAnalysisRecorded',
    'FraudPayload',
    # Compatibility
    'FraudPattern',
    'FraudPatternType',
    'FraudPatternSeverity',
    'FraudDetectionStarted',
    'FraudDetectionCompleted',
]