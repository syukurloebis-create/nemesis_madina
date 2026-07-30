# ir/emitter.py

from typing import Optional

from .context import IRContext
from .models import (
    Scope, ScopeKind,
    Declaration, DeclarationKind,
    Symbol, SymbolKind, Visibility, SymbolOrigin,
    Statement, StatementKind,
    Expression, ExpressionKind,
)

# Sentinel for unresolved location
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
        kind: StatementKind,
        module_id: int,
        scope_id: int,
        ordinal: int,
        location_id: int = UNRESOLVED_LOCATION_ID,
        expr_id: Optional[int] = None,
    ) -> int:
        """
        Emit a statement entity.

        Returns:
            stmt_id
        """
        stmt_id = self._context.stmt_alloc.allocate()

        statement = Statement(
            stmt_id=stmt_id,
            stable_id="",
            kind=kind,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            block_id=None,
            location_id=location_id,
            expr_id=expr_id,
        )

        self._context.statements.insert(statement)
        return stmt_id

    def emit_import_statement(
        self,
        kind: StatementKind,
        module_id: int,
        scope_id: int,
        ordinal: int,
        payload: dict,
        location_id: int = UNRESOLVED_LOCATION_ID,
    ) -> int:
        """
        Emit an import statement entity.

        Args:
            kind: IMPORT or IMPORT_FROM
            payload: Import metadata (module, names, alias, level)

        Returns:
            stmt_id
        """
        stmt_id = self._context.stmt_alloc.allocate()

        statement = Statement(
            stmt_id=stmt_id,
            stable_id="",
            kind=kind,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            block_id=None,
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
    ) -> bool:
        """
        Update an emitted expression payload.

        Args:
            expr_id: Expression ID to update
            payload: Payload fields to merge

        Returns:
            True if updated successfully, False if expression not found
        """
        expression = self._context.expressions.get(expr_id)

        if expression is None:
            return False

        expression.payload.update(payload)
        return True