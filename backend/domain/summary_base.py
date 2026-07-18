# backend/domain/summary_base.py

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable
from backend.domain.enums import EngineStatus


@runtime_checkable
class Summary(Protocol):
    """Protocol untuk semua summary objects."""
    engine_status: EngineStatus
    score: float
    has_data: bool

    @classmethod
    def empty(cls) -> "Summary":
        """Return empty summary."""
        ...


class BaseSummary(ABC):
    """Abstract base class untuk summary objects."""
    
    @property
    @abstractmethod
    def engine_status(self) -> EngineStatus:
        ...
    
    @property
    @abstractmethod
    def score(self) -> float:
        ...
    
    @property
    @abstractmethod
    def has_data(self) -> bool:
        ...
    
    @classmethod
    @abstractmethod
    def empty(cls) -> "BaseSummary":
        ...