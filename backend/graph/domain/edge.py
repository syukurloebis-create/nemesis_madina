"""
Graph Domain - Edge (Value Object)

Immutable value object representing a graph edge.
No ORM dependencies. Pure Domain.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class GraphEdge:
    """
    Graph Edge - Domain Value Object.
    
    Immutable. Uses Business Keys (not database IDs) for source and target.
    
    Attributes:
        source_key: Business key of source node
        target_key: Business key of target node
        relationship_type: Type of relationship
        weight: Relationship weight (0.0 - 1.0)
        amount: Monetary amount (optional)
        description: Human-readable description
        extra_data: Additional metadata
    """
    
    source_key: str
    target_key: str
    relationship_type: str
    weight: float = 1.0
    amount: Optional[float] = None
    description: Optional[str] = None
    extra_data: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate invariants."""
        if not self.source_key:
            raise ValueError("source_key is required")
        if not self.target_key:
            raise ValueError("target_key is required")
        if not self.relationship_type:
            raise ValueError("relationship_type is required")
        if self.source_key == self.target_key:
            raise ValueError("Self-loop is prohibited")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")
        if self.amount is not None and self.amount < 0:
            raise ValueError("amount must be non-negative")
        if self.extra_data is None:
            object.__setattr__(self, 'extra_data', {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source_key": self.source_key,
            "target_key": self.target_key,
            "relationship_type": self.relationship_type,
            "weight": self.weight,
            "amount": self.amount,
            "description": self.description,
            "extra_data": self.extra_data,
        }