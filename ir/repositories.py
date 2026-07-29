# ir/repositories.py

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')


class Repository(Generic[T], ABC):
    """Base repository with CRUD operations."""

    @abstractmethod
    def insert(self, item: T) -> None:
        """Insert an item into the repository."""
        ...

    @abstractmethod
    def get(self, item_id: int) -> Optional[T]:
        """Get an item by ID."""
        ...

    @abstractmethod
    def find(self, **kwargs) -> List[T]:
        """Find items by field values."""
        ...

    @abstractmethod
    def exists(self, item_id: int) -> bool:
        """Check if an item exists by ID."""
        ...

    @abstractmethod
    def all(self) -> List[T]:
        """Get all items."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Get the number of items."""
        ...

    @abstractmethod
    def freeze(self) -> None:
        """Freeze the repository (make immutable)."""
        ...

    @abstractmethod
    def is_frozen(self) -> bool:
        """Check if the repository is frozen."""
        ...


class ModuleRepository(Repository):
    pass


class ScopeRepository(Repository):
    pass


class SymbolRepository(Repository):
    pass


class DeclarationRepository(Repository):
    pass


class StatementRepository(Repository):
    pass


class ExpressionRepository(Repository):
    pass


class BlockRepository(Repository):
    pass


class LocationRepository(Repository):
    pass