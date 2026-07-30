class Allocator:
    __slots__ = ("_counter",)

    def __init__(self):
        self._counter: int = 0

    def allocate(self) -> int:
        self._counter += 1
        return self._counter

    def current(self) -> int:
        return self._counter

    def reset(self) -> None:
        self._counter = 0

    def reset_to(self, target: int) -> None:
        """Reset allocator to a previous value only."""
        if target < 0:
            raise ValueError(f"Invalid reset target: {target}")
        if target > self._counter:
            raise ValueError(
                f"Cannot reset allocator forward: {target} > {self._counter}"
            )
        self._counter = target

class ModuleAllocator(Allocator):
    pass

class ScopeAllocator(Allocator):
    pass

class SymbolAllocator(Allocator):
    pass

class DeclAllocator(Allocator):
    pass

class StmtAllocator(Allocator):
    pass

class ExprAllocator(Allocator):
    pass

class BlockAllocator(Allocator):
    pass

class LocationAllocator(Allocator):
    pass