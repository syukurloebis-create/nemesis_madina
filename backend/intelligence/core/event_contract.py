# backend/intelligence/core/event_contract.py

from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime

@dataclass
class IntelligenceEvent:
    """
    Unified event contract for ALL intelligence pipeline usage.
    """
    aggregate_id: str  # = case_id semantic
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    tenant_id: str | None = None

    @property
    def case_id(self) -> str:
        # backward compatibility alias
        return self.aggregate_id