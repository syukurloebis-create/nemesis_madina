# ir/emitter.py

from __future__ import annotations

from typing import Optional, Dict, Any, Iterator
from contextlib import contextmanager

from .context import IRContext, TransactionHandle, _TransactionSnapshot
from .models import (
    Scope, ScopeKind,
    Declaration, DeclarationKind,
    Symbol, SymbolKind, Visibility, SymbolOrigin,
    Statement, StatementKind,
    Expression, ExpressionKind,
    Block, BlockKind, BlockRole,
)

UNRESOLVED_LOCATION_ID = 0


class Emitter:
    """Thin layer between Visitor and Repositories."""

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
        location_id: int = UNRESOLVED_LOCATION_ID,
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

    def emit_function(
        self,
        name: str,
        qualname: str,
        module_id: int,
        parent_scope_id: Optional[int],
        depth: int,
        is_async: bool = False,
        location_id: int = UNRESOLVED_LOCATION_ID,
    ) -> tuple[int, int, int]:
        """
        Emit function entities.

        Returns:
            Tuple of (scope_id, decl_id, symbol_id)
        """
        scope_id = self._context.scope_alloc.allocate()
        decl_id = self._context.decl_alloc.allocate()
        symbol_id = self._context.symbol_alloc.allocate()

        scope = Scope(
            scope_id=scope_id,
            kind=ScopeKind.FUNCTION,
            name=name,
            qualname=qualname,
            module_id=module_id,
            parent_scope=parent_scope_id,
            depth=depth,
            location_id=location_id,
        )
        self._context.scopes.insert(scope)

        decl = Declaration(
            decl_id=decl_id,
            stable_id="",
            kind=DeclarationKind.FUNCTION,
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

        symbol = Symbol(
            symbol_id=symbol_id,
            stable_id="",
            kind=SymbolKind.FUNCTION,
            name=name,
            qualname=qualname,
            module_id=module_id,
            scope_id=scope_id,
            decl_id=decl_id,
            visibility=Visibility.PUBLIC,
            is_abstract=False,
            is_protocol=False,
            is_async=is_async,
            is_dataclass=False,
            origin=SymbolOrigin.USER,
            location_id=location_id,
        )
        self._context.symbols.insert(symbol)

        return scope_id, decl_id, symbol_id

    def emit_statement(
        self,
        *,
        kind: StatementKind,
        module_id: int,
        scope_id: int,
        block_id: int,
        ordinal: int,
        location_id: int,
        stable_id: str,
        expr_id: Optional[int] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Emit a statement entity with block_id."""
        stmt_id = self._context.stmt_alloc.allocate()
    
        statement = Statement(
            stmt_id=stmt_id,
            stable_id=stable_id,
            kind=kind,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            block_id=block_id,
            location_id=location_id,
            expr_id=expr_id,
            payload=payload or {},
        )
        self._context.statements.insert(statement)
        return stmt_id

    def emit_import_statement(
        self,
        *,
        kind: StatementKind,
        module_id: int,
        scope_id: int,
        block_id: int,
        ordinal: int,
        stable_id: str,
        payload: Dict[str, Any],
        location_id: int = UNRESOLVED_LOCATION_ID,
    ) -> int:
        """Emit an import statement entity with block_id and stable_id."""
        stmt_id = self._context.stmt_alloc.allocate()
    
        statement = Statement(
            stmt_id=stmt_id,
            stable_id=stable_id,
            kind=kind,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            block_id=block_id,
            location_id=location_id,
            expr_id=None,
            payload=payload,
        )
        self._context.statements.insert(statement)
        return stmt_id

    def emit_expression(
        self,
        *,
        kind: ExpressionKind,
        module_id: int,
        parent_expr: Optional[int],
        ordinal: int,
        location_id: int,
        stable_id: str,
        payload: dict,
    ) -> int:
        """
        Emit an expression entity to the expression repository.

        Args:
            kind: ExpressionKind
            module_id: Module ID
            parent_expr: Parent expression ID (None for root)
            ordinal: Child order within parent
            location_id: Location ID
            stable_id: Canonical stable ID
            payload: Expression-specific payload

        Returns:
            expr_id (integer)
        """
        expr_id = self._context.expr_alloc.allocate()

        expression = Expression(
            expr_id=expr_id,
            stable_id=stable_id,
            kind=kind,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=location_id,
            payload=payload,
        )

        self._context.expressions.insert(expression)
        return expr_id

    def update_expression_payload(
        self,
        expr_id: int,
        payload: dict,
    ) -> None:
        """
        Update an emitted expression payload.

        Args:
            expr_id: Expression ID to update
            payload: New payload (replaces existing)

        Raises:
            KeyError: If expression not found
        """
        expression = self._context.expressions.get(expr_id)
        if expression is None:
            raise KeyError(f"Expression {expr_id} not found")

        expression.payload = payload
    
    def emit_block(
        self,
        *,
        kind: BlockKind,
        role: BlockRole,
        module_id: int,
        scope_id: int,
        ordinal: int,
        parent_block_id: Optional[int],
        stable_id: str,
        location_id: int = UNRESOLVED_LOCATION_ID,
    ) -> int:    
        """Emit a Block entity with structural topology validation."""
    
        # Validate ROOT invariant
        if role == BlockRole.ROOT:
            if parent_block_id is not None:
                raise ValueError(
                    f"ROOT Block cannot have parent_block_id (got {parent_block_id})"
                )
        else:
            # Non-root must have parent
            if parent_block_id is None:
                raise ValueError(
                    f"Non-root Block (role={role}) requires parent_block_id"
                )
        
            # Parent must exist
            parent = self._context.blocks.get(parent_block_id)
            if parent is None:
                raise ValueError(
                    f"Parent Block {parent_block_id} does not exist"
                )
        
            # Scope must match
            if parent.scope_id != scope_id:
                raise ValueError(
                    f"Child Block scope_id ({scope_id}) must equal "
                    f"parent Block scope_id ({parent.scope_id})"
                )
    
        block_id = self._context.block_alloc.allocate()
    
        block = Block(
            block_id=block_id,
            stable_id=stable_id,
            module_id=module_id,
            scope_id=scope_id,
            kind=kind,
            role=role,
            ordinal=ordinal,
            parent_block_id=parent_block_id,
            location_id=location_id,
        )
    
        self._context.blocks.insert(block)
        return block_id

    # =========================================================================
    # Transaction API (Semantic)
    # =========================================================================

    def begin_transaction(self) -> TransactionHandle:
        """Begin a logical transaction.
        
        Returns:
            TransactionHandle (pure identity token, single-use).
        """
        return self._context.begin_transaction()

    def commit_transaction(self, handle: TransactionHandle) -> None:
        """Commit the logical transaction.
        
        Consumes the handle (removes from registry).
        The handle becomes invalid after this call.
        """
        self._context.commit_transaction(handle)

    def rollback_transaction(self, handle: TransactionHandle) -> None:
        """Rollback the logical transaction to the snapshot.
        
        Validates, applies rollback, then consumes the handle.
        If rollback fails, the handle remains in registry for debugging.
        The handle becomes invalid after successful rollback.
        """
        self._context.rollback_transaction(handle)

    # =========================================================================
    # High-Level Transaction API (Context Manager)
    # =========================================================================

    @contextmanager
    def transaction(self) -> Iterator[TransactionHandle]:
        """Context manager for transaction.
        
        Usage:
            with emitter.transaction() as tx:
                # ... emit ...
            # Auto-commits on success, auto-rollbacks on exception
        
        Returns:
            TransactionHandle for low-level operations if needed.
            Handle is single-use and becomes invalid after context exits.
        """
        handle = self.begin_transaction()
        try:
            yield handle
            self.commit_transaction(handle)
        except Exception:
            self.rollback_transaction(handle)
            raise