"""
NEMESIS Madina - Fraud Domain Events
✅ Uses payload pattern (consistent with Risk, Evidence, Application)
✅ Carries Value Objects, not dict
"""

from dataclasses import dataclass
from typing import ClassVar, Optional
from datetime import datetime, timezone

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.fraud_payload import FraudPayload
from backend.domain.value_objects.fraud_pattern import FraudPattern, FraudPatternType, FraudPatternSeverity
from backend.domain.value_objects.legacy_fraud_pattern import LegacyFraudPattern
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis


@dataclass(frozen=True)
class FraudAnalysisCompleted(DomainEvent[FraudPayload]):
    """New-style event — DomainEvent[FraudPayload]."""
    EVENT_NAME = "FraudAnalysisCompleted"
    EVENT_VERSION = "1"

# ============================================================================
# NEW-STYLE EVENT (Target Architecture)
# ============================================================================

class FraudAnalysisRecorded(FraudAnalysisCompleted):
    """
    Compatibility adapter for old aggregate calls.

    Old: FraudAnalysisRecorded(case_id=..., analysis=...)
    New: FraudAnalysisCompleted(payload=FraudPayload(...))

    ✅ Plain class (not dataclass) - no field ordering issues
    ✅ Inherits from new event
    ✅ Constructor matches old contract
    ✅ Produces valid DomainEvent
    ✅ Temporary - will be removed after migration
    """

    def __init__(self, case_id: CaseId, analysis: FraudAnalysis):
        payload = FraudPayload(
            case_id=case_id,
            analysis=analysis,
        )
        super().__init__(payload=payload)

    @property
    def event_name(self) -> str:
        return "FraudAnalysisRecorded"

    @property
    def case_id(self):
        """Convenience property for backward compatibility"""
        return self.payload.case_id

    @property
    def analysis(self):
        """Convenience property for backward compatibility"""
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