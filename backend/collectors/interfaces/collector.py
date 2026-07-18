"""
Collector Interface — Generic Contract.

Architecture Decision:
- ICollector[T] is the contract for all collectors
- Collector receives UoW (not repository directly)
- Repository is created inside collector using RepositoryFactory
"""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from backend.infrastructure.unit_of_work import UnitOfWork
from backend.core.context import ExecutionContext


T = TypeVar('T')


class ICollector(Generic[T], ABC):
    """
    Collector Interface — Generic Contract.
    
    All collectors implement this interface.
    Collector receives UoW + RepositoryFactory.
    """
    
    @abstractmethod
    async def collect(
        self,
        uow: UnitOfWork,
        context: ExecutionContext
    ) -> T:
        """
        Collect data using UnitOfWork.
        
        Args:
            uow: UnitOfWork for transaction boundary
            context: ExecutionContext with metadata
        
        Returns:
            T: Collector DTO (typed, immutable)
        """
        pass