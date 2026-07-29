# ir/emitter.py

from typing import Optional

from .context import IRContext
from .models import (
    Scope, ScopeKind,
    Declaration, DeclarationKind,
    Symbol, SymbolKind, Visibility, SymbolOrigin,
)


class Emitter:
    """
    Thin layer between Visitor and Repositories.

    Responsibilities:
    - Create IR entities from AST nodes
    - Allocate IDs via context allocators
    - Insert entities into repositories
    - Does NOT perform semantic analysis
    - Does NOT normalize IR
    - Does NOT serialize
    """

    def __init__(self, context: IRContext):
        self._context = context
        self._diagnostics = context.diagnostics

    def emit_class(
        self,
        name: str,
        qualname: str,
        module_id: int,
        parent_scope_id: Optional[int],
        depth: int,
        location_id: int = 0,
    ) -> tuple[int, int, int]:
        """
        Emit class entities.

        Returns:
            Tuple of (scope_id, decl_id, symbol_id)
        """
        # 1. Allocate IDs
        scope_id = self._context.scope_alloc.allocate()
        decl_id = self._context.decl_alloc.allocate()
        symbol_id = self._context.symbol_alloc.allocate()

        # 2. Create Scope
        scope = Scope(
            scope_id=scope_id,
            kind=ScopeKind.CLASS,
            name=name,
            qualname=qualname,
            module_id=module_id,
            parent_scope=parent_scope_id,
            depth=depth,
            location_id=location_id,
        )
        self._context.scopes.insert(scope)

        # 3. Create Declaration
        decl = Declaration(
            decl_id=decl_id,
            stable_id="",  # Will be filled by hashing
            kind=DeclarationKind.CLASS,
            module_id=module_id,
            name=name,
            scope_id=scope_id,
            symbol_id=symbol_id,
            block_id=None,
            location_id=location_id,
            bases=[],
            decorators=[],
        )
        self._context.declarations.insert(decl)

        # 4. Create Symbol
        symbol = Symbol(
            symbol_id=symbol_id,
            stable_id="",  # Will be filled by hashing
            kind=SymbolKind.CLASS,
            name=name,
            qualname=qualname,
            module_id=module_id,
            scope_id=scope_id,
            decl_id=decl_id,
            visibility=Visibility.PUBLIC,
            is_abstract=False,
            is_protocol=False,
            is_async=False,
            is_dataclass=False,
            origin=SymbolOrigin.USER,
            location_id=location_id,
        )
        self._context.symbols.insert(symbol)

        return scope_id, decl_id, symbol_id