# ir/visitor.py

import ast
from typing import Any, Optional

from .context import IRContext
from .emitter import Emitter, UNRESOLVED_LOCATION_ID
from .hashing import stable_expression_id
from .models import (
    Scope,
    ScopeKind,
    StatementKind,
    ExpressionKind,
)


class Visitor:
    """
    AST → IR Visitor.

    Responsibilities:
    - Traverse AST in deterministic order
    - Emit IR entities via Emitter
    - Does NOT perform semantic analysis
    - Does NOT normalize IR
    - Does NOT serialize

    Contract:
    - Same AST → same IR entities
    - IDs allocated deterministically
    - No side effects outside repositories
    """

    def __init__(self, context: IRContext):
        self._context = context
        self._diagnostics = context.diagnostics
        self._emitter = Emitter(context)  # Thin layer

    def visit(self, node: ast.AST) -> int | None:
        """Visit an AST node and emit IR entities."""
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name, self._visit_default)
        return method(node)

    def _visit_default(self, node: ast.AST) -> int | None:
        """Default visitor for unsupported nodes."""
        self._diagnostics.add_warning(
            code="VISITOR-001",
            message=f"Unsupported AST node: {type(node).__name__}",
            location_id=None,
            module_id=None
        )
        return None

    def visit_Name(self, node: ast.Name) -> int | None:
        """
        Visit Name node.

        Returns:
            expr_id of the emitted expression, or None on failure
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return None

        # Determine context
        ctx = "load"
        if isinstance(node.ctx, ast.Store):
            ctx = "store"
        elif isinstance(node.ctx, ast.Del):
            ctx = "del"

        # Get parent and ordinal from context (managed by caller)
        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.NAME,
            identifier=node.id,
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit expression
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.NAME,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,  # Temporary
            stable_id=stable_id,
            payload={
                "id": node.id,
                "ctx": ctx,
            },
        )

        # Increment ordinal for next sibling
        self._context.expression_ordinal += 1

        return expr_id

    def visit_Module(self, node: ast.Module) -> None:
        """
        Visit Module node.

        CP2.2A: Allocate module scope
        CP2.2B: Traverse ClassDef only
        CP2.2C: Traverse FunctionDef and AsyncFunctionDef only
        CP2.3A: Traverse Assign, AnnAssign, AugAssign
        CP2.3B: Traverse Expr, Pass, Raise, Assert
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return

        module_name = "<module>"

        scope_id = self._context.scope_alloc.allocate()

        scope = Scope(
            scope_id=scope_id,
            kind=ScopeKind.MODULE,
            name=module_name,
            qualname=module_name,
            module_id=module_id,
            parent_scope=None,
            depth=0,
            location_id=UNRESOLVED_LOCATION_ID,
        )

        self._context.scopes.insert(scope)

        self._context.current_scope_id = scope_id
        self._context.scope_stack.append(scope_id)

        # Reset ordinal for module scope
        self._context.statement_ordinals[scope_id] = 0

        # Dispatch to supported child nodes
        # Each child is visited exactly ONCE
        for child in node.body:
            if not isinstance(
                child,
                (
                    ast.ClassDef,
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                    ast.Assign,
                    ast.AnnAssign,
                    ast.AugAssign,
                    ast.Expr,
                    ast.Pass,
                    ast.Raise,
                    ast.Assert,
                    ast.Import,
                    ast.ImportFrom,
                ),
            ):
                continue

            # Capture enclosing scope BEFORE visiting the child
            parent_scope_id = self._context.current_scope_id
            parent_stack_len = len(self._context.scope_stack)

            # Exactly one dispatch per child
            self.visit(child)

            # Restore enclosing scope after processing a top-level declaration
            self._context.current_scope_id = parent_scope_id
            del self._context.scope_stack[parent_stack_len:]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """
        Visit ClassDef node.

        CP2.2B Scope:
        - Allocate CLASS scope
        - Create CLASS declaration
        - Create CLASS symbol
        - Update scope_stack
        - NO traversal of node.body
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return

        parent_scope_id = self._context.current_scope_id

        # Calculate depth from parent scope
        parent_scope = self._context.scopes.get(parent_scope_id) if parent_scope_id else None
        depth = (parent_scope.depth + 1) if parent_scope else 1

        # Qualname: simple name for CP2.2B (nested will be handled later)
        qualname = node.name

        # Emit class entities via Emitter
        scope_id, decl_id, symbol_id = self._emitter.emit_class(
            name=node.name,
            qualname=qualname,
            module_id=module_id,
            parent_scope_id=parent_scope_id,
            depth=depth,
            location_id=UNRESOLVED_LOCATION_ID,
        )

        # Update context for children
        self._context.current_scope_id = scope_id
        self._context.scope_stack.append(scope_id)

        # CP2.2B: NO traversal of node.body

    def _get_qualname(self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> str:
        """Build qualified name for a node."""
        return node.name

    def _get_depth(self, parent_scope_id: Optional[int]) -> int:
        """Calculate depth from parent scope."""
        if parent_scope_id is None:
            return 0
        parent_scope = self._context.scopes.get(parent_scope_id)
        if parent_scope is None:
            return 1
        return parent_scope.depth + 1

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, is_async: bool) -> None:
        """
        Common implementation for FunctionDef and AsyncFunctionDef.
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return

        parent_scope_id = self._context.current_scope_id
        depth = self._get_depth(parent_scope_id)
        qualname = self._get_qualname(node)

        scope_id, decl_id, symbol_id = self._emitter.emit_function(
            name=node.name,
            qualname=qualname,
            module_id=module_id,
            parent_scope_id=parent_scope_id,
            depth=depth,
            is_async=is_async,
            location_id=UNRESOLVED_LOCATION_ID,
        )

        self._context.current_scope_id = scope_id
        self._context.scope_stack.append(scope_id)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node, is_async=True)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit Assign node."""
        self._visit_statement(node, StatementKind.ASSIGN)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit AnnAssign node."""
        self._visit_statement(node, StatementKind.ANNOTATED_ASSIGN)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        """Visit AugAssign node."""
        self._visit_statement(node, StatementKind.AUGMENTED_ASSIGN)

    def visit_Expr(self, node: ast.Expr) -> None:
        self._visit_statement(node, StatementKind.EXPR)

    def visit_Pass(self, node: ast.Pass) -> None:
        self._visit_statement(node, StatementKind.PASS)

    def visit_Raise(self, node: ast.Raise) -> None:
        self._visit_statement(node, StatementKind.RAISE)

    def visit_Assert(self, node: ast.Assert) -> None:
        self._visit_statement(node, StatementKind.ASSERT)

    def visit_Return(self, node: ast.Return) -> None:
        self._visit_statement(node, StatementKind.RETURN)

    def visit_Break(self, node: ast.Break) -> None:
        self._visit_statement(node, StatementKind.BREAK)

    def visit_Continue(self, node: ast.Continue) -> None:
        self._visit_statement(node, StatementKind.CONTINUE)

    def _get_ordinal(self, scope_id: int) -> int:
        """Get current ordinal for a scope and increment it."""
        ordinal = self._context.statement_ordinals.get(scope_id, 0)
        self._context.statement_ordinals[scope_id] = ordinal + 1
        return ordinal

    def _visit_statement(
        self,
        node: ast.AST,
        kind: StatementKind,
        expr_id: Optional[int] = None,
    ) -> None:
        """Common implementation for statement nodes."""
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return

        scope_id = self._context.current_scope_id
        if scope_id is None:
            self._diagnostics.add_error(
                code="VISITOR-003",
                message="No scope_id set in context",
                location_id=None,
                module_id=None
            )
            return

        ordinal = self._get_ordinal(scope_id)

        self._emitter.emit_statement(
            kind=kind,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            expr_id=None,  # Expression IR will be added in CP2.4
        )

    def visit_Import(self, node: ast.Import) -> None:
        """Visit Import node."""
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return

        scope_id = self._context.current_scope_id
        if scope_id is None:
            self._diagnostics.add_error(
                code="VISITOR-003",
                message="No scope_id set in context",
                location_id=None,
                module_id=None
            )
            return

        ordinal = self._get_ordinal(scope_id)

        payload = {
            "names": [
                {"name": alias.name, "alias": alias.asname}
                for alias in node.names
            ]
        }

        self._emitter.emit_import_statement(
            kind=StatementKind.IMPORT,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            payload=payload,
            location_id=UNRESOLVED_LOCATION_ID,
        )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit ImportFrom node."""
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return

        scope_id = self._context.current_scope_id
        if scope_id is None:
            self._diagnostics.add_error(
                code="VISITOR-003",
                message="No scope_id set in context",
                location_id=None,
                module_id=None
            )
            return

        ordinal = self._get_ordinal(scope_id)

        payload = {
            "module": node.module or "",
            "names": [
                {"name": alias.name, "alias": alias.asname}
                for alias in node.names
            ],
            "level": node.level or 0,
        }

        self._emitter.emit_import_statement(
            kind=StatementKind.IMPORT_FROM,
            module_id=module_id,
            scope_id=scope_id,
            ordinal=ordinal,
            payload=payload,
            location_id=UNRESOLVED_LOCATION_ID,
        )

    def visit_Constant(self, node: ast.Constant) -> int | None:
        """
        Visit Constant node.

        Returns:
            expr_id of the emitted expression, or None on failure
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return None

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Determine value_type and canonical value
        value = node.value
        value_type: str
        canonical_value: Any

        if value is None:
            value_type = "none"
            canonical_value = None
        elif isinstance(value, bool):
            value_type = "bool"
            canonical_value = value
        elif isinstance(value, int):
            value_type = "int"
            canonical_value = value
        elif isinstance(value, float):
            value_type = "float"
            canonical_value = value
        elif isinstance(value, complex):
            value_type = "complex"
            canonical_value = [value.real, value.imag]
        elif isinstance(value, str):
            value_type = "str"
            canonical_value = value
        elif isinstance(value, bytes):
            value_type = "bytes"
            canonical_value = value.hex()
        elif value is Ellipsis:
            value_type = "ellipsis"
            canonical_value = None
        else:
            self._diagnostics.add_warning(
                code="VISITOR-004",
                message=f"Unsupported constant type: {type(value).__name__}",
                location_id=None,
                module_id=None
            )
            return None

        # Generate stable ID with canonical identifier
        identifier = f"{value_type}:{canonical_value!r}"
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.CONSTANT,
            identifier=identifier,
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit expression
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.CONSTANT,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "value": canonical_value,
                "value_type": value_type,
            },
        )

        self._context.expression_ordinal += 1
        return expr_id

    def visit_Attribute(self, node: ast.Attribute) -> int | None:
        """
        Visit Attribute node.

        Returns:
            expr_id of the emitted expression, or None on failure
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return None

        # Determine context
        ctx = "load"
        if isinstance(node.ctx, ast.Store):
            ctx = "store"
        elif isinstance(node.ctx, ast.Del):
            ctx = "del"

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID for the attribute expression itself
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.ATTRIBUTE,
            identifier=node.attr,
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit the attribute expression (base will be filled after visiting child)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.ATTRIBUTE,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "base": None,  # Will be filled after visiting base
                "attr": node.attr,
                "ctx": ctx,
            },
        )

        # Save parent context for restoration
        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        try:
            # Visit base expression as a child
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0
            base_expr_id = self.visit(node.value)

            if base_expr_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-005",
                    message="Failed to visit base expression",
                    location_id=None,
                    module_id=None
                )
                # Return the attribute expression anyway, with base still None
                return expr_id

            # Update payload with base expr_id via Emitter
            self._emitter.update_expression_payload(
                expr_id,
                {
                    "base": base_expr_id,
                    "attr": node.attr,
                    "ctx": ctx,
                },
            )

            return expr_id

        finally:
            # Restore parent context
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = previous_ordinal + 1

    def visit_Call(self, node: ast.Call) -> int | None:
        """
        Visit Call node.

        Returns:
            expr_id of the emitted expression, or None on failure
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None
            )
            return None

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID for the call expression itself
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.CALL,
            identifier="call",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit call expression (payload will be filled after visiting children)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.CALL,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "callee": None,
                "args": [],
                "keywords": [],
            },
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0  # Reset for children

            # 1. Visit callee (ordinal 0)
            callee_expr_id = self.visit(node.func)
            if callee_expr_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-007",
                    message="Failed to visit callee expression",
                    location_id=None,
                    module_id=None,
                )
                return expr_id

            # Children increment ordinal themselves; no manual increment here

            # 2. Visit args (ordinals 1..N) — fail-fast
            args_ids: list[int] = []
            for arg in node.args:
                arg_expr_id = self.visit(arg)
                if arg_expr_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-008",
                        message="Failed to visit call argument",
                        location_id=None,
                        module_id=module_id,
                    )
                    return expr_id
                args_ids.append(arg_expr_id)

            # 3. Visit keywords (ordinals N+1..M) — fail-fast
            keywords: list[dict] = []
            for kw in node.keywords:
                if kw.value is not None:
                    kw_value_id = self.visit(kw.value)
                    if kw_value_id is None:
                        self._diagnostics.add_error(
                            code="VISITOR-009",
                            message="Failed to visit keyword value",
                            location_id=None,
                            module_id=module_id,
                        )
                        return expr_id
                    keywords.append({
                        "name": kw.arg,
                        "value": kw_value_id,
                    })

            # Update payload via Emitter
            self._emitter.update_expression_payload(
                expr_id,
                {
                    "callee": callee_expr_id,
                    "args": args_ids,
                    "keywords": keywords,
                },
            )

        finally:
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = previous_ordinal + 1

        return expr_id
