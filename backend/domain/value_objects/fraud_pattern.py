# backend/domain/value_objects/fraud_pattern.py
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum

class FraudPatternType(Enum):
    """Types of fraud patterns"""
    COLLUSION = "collusion"
    ANOMALY = "anomaly"
    SYNDICATE = "syndicate"
    SHELL_COMPANY = "shell_company"
    BID_RIGGING = "bid_rigging"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    UNKNOWN = "unknown"

class FraudPatternSeverity(Enum):
    """Severity levels for fraud patterns"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass(frozen=True)
class FraudPattern:
    """Fraud pattern value object (immutable)"""
    pattern_id: str
    name: str
    pattern_type: FraudPatternType
    severity: FraudPatternSeverity
    description: str
    indicators: List[str]
    confidence_score: float = 0.0
    detected_at: Optional[datetime] = None
    metadata: Optional[dict] = None
    
    def __post_init__(self):
        # Validate confidence score
        if not (0 <= self.confidence_score <= 100):
            raise ValueError(f"Confidence score must be between 0 and 100, got {self.confidence_score}")
        
        # Validate indicators
        if not self.indicators:
            raise ValueError("Fraud pattern must have at least one indicator")
    
    def is_high_confidence(self) -> bool:
        """Check if pattern has high confidence"""
        return self.confidence_score >= 0.8
    
    def is_critical(self) -> bool:
        """Check if pattern is critical severity"""
        return self.severity == FraudPatternSeverity.CRITICAL
    
    def get_indicator_count(self) -> int:
        """Get number of indicators"""
        return len(self.indicators)