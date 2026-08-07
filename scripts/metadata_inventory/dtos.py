# scripts/metadata_inventory/dtos.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from .enums import Severity, FindingID

@dataclass(frozen=True)
class Evidence:
    """Bukti untuk finding."""
    description: str
    source: str
    details: dict = field(default_factory=dict)

@dataclass(frozen=True)
class Finding:
    """Finding immutable (tanpa recommendation)."""
    id: FindingID
    severity: Severity
    title: str
    description: str
    evidence: List[Evidence]
    affected_modules: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class Recommendation:
    """Recommendation terpisah dari Finding."""
    finding_id: FindingID
    policy_mode: str  # "enterprise", "strict", "community"
    recommendation: str
    documentation_url: Optional[str] = None
    
    def __post_init__(self):
        if not self.recommendation:
            raise ValueError("Recommendation cannot be empty")