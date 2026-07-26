# scripts/architecture/models/metric.py
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Metric:
    """Architecture metric"""
    name: str
    value: float
    unit: str
    timestamp: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp or datetime.now().isoformat()
        }