# ir/repositories.py

from typing import Generic, TypeVar, Optional, List, Dict, Any

T = TypeVar('T')


class Repository(Generic[T]):
    """Base repository with deterministic primary-key indexing."""

    id_field: Optional[str] = None

    def __init__(self) -> None:
        self._items: List[T] = []
        self._frozen: bool = False
        self._index: Dict[int, T] = {}

    def insert(self, item: T) -> None:
        if self._frozen:
            raise RuntimeError("Repository is frozen")

        self._items.append(item)

        if self.id_field is None:
            return

        item_id = getattr(item, self.id_field, None)
        if isinstance(item_id, int):
            self._index[item_id] = item

    def get(self, item_id: int) -> Optional[T]:
        return self._index.get(item_id)

    def find(self, **kwargs: Any) -> List[T]:
        results: List[T] = []

        for item in self._items:
            if all(
                hasattr(item, key) and getattr(item, key) == value
                for key, value in kwargs.items()
            ):
                results.append(item)

        return results

    def exists(self, item_id: int) -> bool:
        return item_id in self._index

    def all(self) -> List[T]:
        return self._items.copy()

    def count(self) -> int:
        return len(self._items)

    def freeze(self) -> None:
        self._frozen = True

    def is_frozen(self) -> bool:
        return self._frozen


class ModuleRepository(Repository):
    id_field = "module_id"


class ScopeRepository(Repository):
    id_field = "scope_id"


class SymbolRepository(Repository):
    id_field = "symbol_id"


class DeclarationRepository(Repository):
    id_field = "decl_id"


class StatementRepository(Repository):
    id_field = "stmt_id"


class ExpressionRepository(Repository):
    id_field = "expr_id"


class BlockRepository(Repository):
    id_field = "block_id"


class LocationRepository(Repository):
    id_field = "location_id"