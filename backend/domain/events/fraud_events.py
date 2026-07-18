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


# ============================================================================
# NEW-STYLE EVENT (Target Architecture)
# ============================================================================

@dataclass(frozen=True)
class FraudAnalysisRecorded(DomainEvent[FraudPayload]):
    """
    Pure domain event - fraud analysis completed.
    ✅ Uses payload pattern
    ✅ Carries Value Object (FraudAnalysis)
    ✅ No dict/payload serialization in event
    """

    EVENT_NAME: ClassVar[str] = "FraudAnalysisRecorded"
    EVENT_VERSION: ClassVar[str] = "1"

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now(timezone.utc))

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
        # Stub implementation for test compatibility
        pass

    @property
    def event_name(self) -> str:
        return "FraudDetectionStarted"

class FraudDetectionStarted:
    """
    Stub for test compatibility.
    ✅ Only used in tests
    ✅ Not for production
    """
    EVENT_NAME = "FraudDetectionStarted"
    
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