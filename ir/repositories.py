# ir/repositories.py

from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')

class Repository(Generic[T]):
    def __init__(self):
        self._items: List[T] = []
        self._frozen: bool = False
        self._index: dict = {}
    
    def insert(self, item: T) -> None:
        if self._frozen:
            raise RuntimeError("Repository is frozen")
        self._items.append(item)
        self._update_index(item)
    
    def get(self, id: int) -> Optional[T]:
        return self._index.get(id)
    
    def find(self, **kwargs) -> List[T]:
        # Find by field values
        pass
    
    def exists(self, id: int) -> bool:
        return id in self._index
    
    def all(self) -> List[T]:
        return self._items.copy()
    
    def count(self) -> int:
        return len(self._items)
    
    def freeze(self) -> None:
        self._frozen = True
        self._items = self._items.copy()  # Ensure immutability
        self._sort_items()
    
    def is_frozen(self) -> bool:
        return self._frozen
    
    def _update_index(self, item: T) -> None:
        # Override in subclasses
        pass
    
    def _sort_items(self) -> None:
        # Override in subclasses for deterministic ordering
        pass