"""
NEMESIS Madina - Base UUID Value Object
"""

from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Optional, Union


@dataclass(frozen=True)
class BaseUUID:
    """Base UUID value object with validation."""
    
    value: UUID
    
    def __init__(self, value: Optional[Union[UUID, str]] = None):
        if value is None:
            object.__setattr__(self, "value", uuid4())
        elif isinstance(value, UUID):
            object.__setattr__(self, "value", value)
        else:
            object.__setattr__(self, "value", UUID(value))
    
    @classmethod
    def generate(cls) -> "BaseUUID":
        """Generate a new UUID."""
        return cls(uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> "BaseUUID":
        """Create from string representation."""
        return cls(UUID(value))
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseUUID):
            return False
        return self.value == other.value
    
    def to_dict(self) -> str:
        """Convert to string for serialization."""
        return str(self.value)