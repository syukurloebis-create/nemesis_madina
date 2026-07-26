# scripts/architecture/models/dependency.py
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Dependency:
    """Module dependency information"""
    source: str
    target: str
    type: str
    is_circular: bool = False
    path: List[str] = None
    
    def __post_init__(self):
        if self.path is None:
            self.path = []