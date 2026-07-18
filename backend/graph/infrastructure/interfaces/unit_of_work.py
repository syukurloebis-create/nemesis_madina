"""
Graph Infrastructure - Unit of Work Interface
"""

from typing import AsyncContextManager
from abc import ABC, abstractmethod


class IUnitOfWork(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        pass
    
    @abstractmethod
    async def flush(self) -> None:
        pass
    
    @property
    @abstractmethod
    def session(self):
        pass


class IUnitOfWorkFactory(ABC):
    @abstractmethod
    def create(self) -> AsyncContextManager[IUnitOfWork]:
        pass