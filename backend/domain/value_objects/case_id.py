"""
NEMESIS Madina - Case ID Value Object
"""

from dataclasses import dataclass
from uuid import UUID, uuid4
from typing import Union, Optional, Dict, Any

from backend.domain.exceptions import InvalidCaseId


@dataclass(frozen=True)
class CaseId:
    """Case ID value object."""
    
    value: UUID
    
    def __init__(self, value: Union[str, UUID]):
        try:
            if isinstance(value, str):
                object.__setattr__(self, "value", UUID(value))
            else:
                object.__setattr__(self, "value", value)
        except ValueError as e:
            raise InvalidCaseId(f"Invalid UUID: {value}") from e
    
    @classmethod
    def generate(cls) -> "CaseId":
        return cls(uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> "CaseId":
        return cls(value)
    
    @classmethod
    def nil(cls) -> "CaseId":
        return cls(UUID("00000000-0000-0000-0000-000000000000"))
    
    def as_uuid(self) -> UUID:
        return self.value
    
    def is_nil(self) -> bool:
        return self.value == UUID("00000000-0000-0000-0000-000000000000")
    
    def to_json(self) -> Dict[str, Any]:
        """For serialization."""
        return {"value": str(self.value)}
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CaseId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)