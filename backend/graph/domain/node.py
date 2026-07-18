"""
Graph Domain - Node (Value Object)

Immutable value object representing a graph node.
No ORM dependencies. Pure Domain.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime, timezone


@dataclass(frozen=True)
class GraphNode:
    """
    Graph Node - Domain Value Object.
    
    Immutable. Built using Business Keys (not database IDs).
    
    Attributes:
        business_key: Unique business identifier
        entity_type: Type of entity (vendor, package, officer, etc.)
        name: Display name
        extra_data: Additional metadata (business-specific)
    """
    
    business_key: str
    entity_type: str
    name: str
    extra_data: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate invariants."""
        if not self.business_key:
            raise ValueError("business_key is required")
        if not self.entity_type:
            raise ValueError("entity_type is required")
        if not self.name:
            raise ValueError("name is required")
        if self.extra_data is None:
            object.__setattr__(self, 'extra_data', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "business_key": self.business_key,
            "entity_type": self.entity_type,
            "name": self.name,
            "extra_data": self.extra_data,
        }