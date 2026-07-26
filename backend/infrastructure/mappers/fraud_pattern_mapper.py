"""
FraudPattern Mapper — Value Object ↔ JSONB
✅ Pure infrastructure mapper
"""

from datetime import datetime
from typing import Optional, Dict, Any

from backend.domain.value_objects.fraud_pattern import FraudPattern, FraudPatternType, FraudPatternSeverity


class FraudPatternMapper:
    @staticmethod
    def to_dict(pattern: FraudPattern) -> Dict[str, Any]:
        return {
            "pattern_id": pattern.pattern_id,
            "name": pattern.name,
            "pattern_type": pattern.pattern_type.value,
            "severity": pattern.severity.value,
            "description": pattern.description,
            "indicators": pattern.indicators,
            "confidence_score": pattern.confidence_score,
            "detected_at": pattern.detected_at.isoformat() if pattern.detected_at else None,
            "metadata": pattern.metadata,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> FraudPattern:
        return FraudPattern(
            pattern_id=data.get("pattern_id", ""),
            name=data.get("name", ""),
            pattern_type=FraudPatternType(data.get("pattern_type", "unknown")),
            severity=FraudPatternSeverity(data.get("severity", "low")),
            description=data.get("description", ""),
            indicators=data.get("indicators", []),
            confidence_score=float(data.get("confidence_score", 0.0)),
            detected_at=datetime.fromisoformat(data["detected_at"]) if data.get("detected_at") else None,
            metadata=data.get("metadata"),
        )