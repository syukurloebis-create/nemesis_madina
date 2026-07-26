# backend/domain/value_objects/legacy_fraud_pattern.py
"""
NEMESIS Madina - Legacy Fraud Pattern Adapter
✅ For test compatibility only
✅ Converts old-style to new domain model
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from backend.domain.value_objects.fraud_pattern import (
    FraudPattern,
    FraudPatternType,
    FraudPatternSeverity,
)


@dataclass(frozen=True)
class LegacyFraudPattern:
    """
    Legacy fraud pattern adapter.
    ✅ Mimics old contract for tests
    ✅ Converts to domain FraudPattern
    """
    
    type: str
    severity: str
    confidence: float
    validated: bool = False
    pattern_id: Optional[str] = None
    
    def to_domain(self) -> FraudPattern:
        """Convert to domain FraudPattern."""
        return FraudPattern(
            pattern_id=self.pattern_id or f"legacy_{self.type}",
            name=self.type,
            pattern_type=self._get_pattern_type(),
            severity=self._get_severity(),
            description=f"Legacy pattern: {self.type}",
            indicators=["legacy"],  # ← CHANGE: [] → ["legacy"]
            confidence_score=self.confidence,  # ← CHANGE: self.confidence / 100.0 → self.confidence
            detected_at=datetime.now(),
            metadata={
                "validated": self.validated,
                "legacy": True,
            },
        )
    
    def _get_pattern_type(self) -> FraudPatternType:
        mapping = {
            "COLLUSION": FraudPatternType.COLLUSION,
            "ANOMALY": FraudPatternType.ANOMALY,
            "SYNDICATE": FraudPatternType.SYNDICATE,
            "SHELL_COMPANY": FraudPatternType.SHELL_COMPANY,
            "BID_RIGGING": FraudPatternType.BID_RIGGING,
            "CONFLICT_OF_INTEREST": FraudPatternType.CONFLICT_OF_INTEREST,
        }
        return mapping.get(self.type.upper(), FraudPatternType.UNKNOWN)
    
    def _get_severity(self) -> FraudPatternSeverity:
        mapping = {
            "LOW": FraudPatternSeverity.LOW,
            "MEDIUM": FraudPatternSeverity.MEDIUM,
            "HIGH": FraudPatternSeverity.HIGH,
            "CRITICAL": FraudPatternSeverity.CRITICAL,
        }
        return mapping.get(self.severity.upper(), FraudPatternSeverity.LOW)