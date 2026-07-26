"""
Graph Infrastructure - Unit of Work Interface
"""

from abc import ABC, abstractmethod
from typing import AsyncContextManager


class IUnitOfWork(ABC):
    """
    Unit of Work Interface.
    
    Transaction boundary for write operations.
    Implemented by infrastructure.
    """
    
    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction."""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction."""
        pass
    
    @abstractmethod
    async def flush(self) -> None:
        """Flush pending changes."""
        pass
    
    @abstractmethod
    def session(self):
        """Get session for repository operations."""
        pass


class IUnitOfWorkFactory(ABC):
    """Factory for creating Unit of Work instances."""
    
    @abstractmethod
    def create(self) -> AsyncContextManager[IUnitOfWork]:
        """Create a new Unit of Work context."""
        passs