# ir/repositories.py

from typing import Generic, TypeVar, Optional, List, Dict

T = TypeVar('T')


class Repository(Generic[T]):
    """Base repository with CRUD operations."""

    def __init__(self) -> None:
        self._items: List[T] = []
        self._frozen: bool = False
        self._index: Dict[int, T] = {}

    def insert(self, item: T) -> None:
        """Insert an item into the repository."""
        if self._frozen:
            raise RuntimeError("Repository is frozen")
        self._items.append(item)
        # Index by id if available
        if hasattr(item, 'module_id'):
            self._index[getattr(item, 'module_id')] = item
        elif hasattr(item, 'scope_id'):
            self._index[getattr(item, 'scope_id')] = item
        elif hasattr(item, 'symbol_id'):
            self._index[getattr(item, 'symbol_id')] = item
        elif hasattr(item, 'decl_id'):
            self._index[getattr(item, 'decl_id')] = item
        elif hasattr(item, 'stmt_id'):
            self._index[getattr(item, 'stmt_id')] = item
        elif hasattr(item, 'expr_id'):
            self._index[getattr(item, 'expr_id')] = item
        elif hasattr(item, 'block_id'):
            self._index[getattr(item, 'block_id')] = item
        elif hasattr(item, 'location_id'):
            self._index[getattr(item, 'location_id')] = item

    def get(self, item_id: int) -> Optional[T]:
        """Get an item by ID."""
        return self._index.get(item_id)

    def find(self, **kwargs) -> List[T]:
        """Find items by field values."""
        results = []
        for item in self._items:
            match = True
            for key, value in kwargs.items():
                if not hasattr(item, key) or getattr(item, key) != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results

    def exists(self, item_id: int) -> bool:
        """Check if an item exists by ID."""
        return item_id in self._index

    def all(self) -> List[T]:
        """Get all items."""
        return self._items.copy()

    def count(self) -> int:
        """Get the number of items."""
        return len(self._items)

    def freeze(self) -> None:
        """Freeze the repository (make immutable)."""
        self._frozen = True

    def is_frozen(self) -> bool:
        """Check if the repository is frozen."""
        return self._frozen


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