# scripts/architecture/models/violation.py
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Violation:
    """Architecture violation"""
    rule_id: str
    message: str
    severity: str  # critical, high, medium, low
    module: Optional[str] = None
    details: Optional[Dict[str, Any]] = None