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

    def _op_to_string(self, op: ast.operator) -> str | None:
        mapping = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "//",
            ast.Mod: "%",
            ast.Pow: "**",
            ast.MatMult: "@",
            ast.LShift: "<<",
            ast.RShift: ">>",
            ast.BitOr: "|",
            ast.BitXor: "^",
            ast.BitAnd: "&",
        }
        return mapping.get(type(op))

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

    def visit_BinOp(self, node: ast.BinOp) -> int | None:
        """
        Visit BinOp node with transactional fail-closed behavior.

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

        # Validate operator
        op = self._op_to_string(node.op)
        if op is None:
            self._diagnostics.add_error(
                code="VISITOR-010",
                message=f"Unsupported binary operator: {type(node.op).__name__}",
                location_id=None,
                module_id=None
            )
            return None

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.BINARY,
            identifier=f"binop_{op}",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit parent expression (within transaction)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.BINARY,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "op": op,
                "left": None,
                "right": None,
            },
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        left_expr_id: int | None = None
        right_expr_id: int | None = None
        success = True

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0

            # 1. Visit left child (ordinal 0)
            left_expr_id = self.visit(node.left)
            if left_expr_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-011",
                    message="Failed to visit left child of binary operation",
                    location_id=None,
                    module_id=None,
                )
                success = False

            # 2. Visit right child (ordinal 1)
            if success:
                self._context.expression_ordinal = 1
                right_expr_id = self.visit(node.right)
                if right_expr_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-012",
                        message="Failed to visit right child of binary operation",
                        location_id=None,
                        module_id=None,
                    )
                    success = False

            # 3. Only commit if both children are valid
            if success and left_expr_id is not None and right_expr_id is not None:
                self._emitter.update_expression_payload(
                    expr_id,
                    {
                        "op": op,
                        "left": left_expr_id,
                        "right": right_expr_id,
                    },
                )
                self._emitter.commit_transaction(snapshot)
                return expr_id
            else:
                # Rollback entire transaction
                self._emitter.rollback_transaction(snapshot)
                self._diagnostics.add_error(
                    code="VISITOR-013",
                    message="Binary operation has incomplete children",
                    location_id=None,
                    module_id=None,
                )
                return None

        except Exception:
            # Rollback on any exception
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-014",
                message="Unexpected error during binary operation",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            # Restore parent context regardless of success
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = previous_ordinal + 1

    def visit_UnaryOp(self, node: ast.UnaryOp) -> int | None:
        """
        Visit UnaryOp node.

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

        # Validate operator
        op = self._unary_op_to_string(node.op)
        if op is None:
            self._diagnostics.add_error(
                code="VISITOR-015",
                message=f"Unsupported unary operator: {type(node.op).__name__}",
                location_id=None,
                module_id=None
            )
            return None

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.UNARY,
            identifier=f"unaryop_{op}",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit parent expression (payload will be filled after child is verified)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.UNARY,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "op": op,
                "operand": None,
            },
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        operand_expr_id: int | None = None
        success = False

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0

            # Visit operand (ordinal 0)
            operand_expr_id = self.visit(node.operand)
            if operand_expr_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-016",
                    message="Failed to visit operand of unary operation",
                    location_id=None,
                    module_id=None,
                )
                success = False
            else:
                success = True

            # Only commit if operand is valid
            if success and operand_expr_id is not None:
                self._emitter.update_expression_payload(
                    expr_id,
                    {
                        "op": op,
                        "operand": operand_expr_id,
                    },
                )
                self._emitter.commit_transaction(snapshot)
                return expr_id
            else:
                # Rollback entire transaction
                self._emitter.rollback_transaction(snapshot)
                self._diagnostics.add_error(
                    code="VISITOR-017",
                    message="Unary operation has incomplete operand",
                    location_id=None,
                    module_id=None,
                )
                return None

        except Exception:
            # Rollback on any exception
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-018",
                message="Unexpected error during unary operation",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            # Restore parent context
            # On success: ordinal advances
            # On failure: ordinal stays the same (no expression emitted)
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = (
                previous_ordinal + 1 if success else previous_ordinal
            )

    def _unary_op_to_string(self, op: ast.unaryop) -> str | None:
        mapping = {
            ast.Not: "not",
            ast.UAdd: "+",
            ast.USub: "-",
            ast.Invert: "~",
        }
        return mapping.get(type(op))

    def visit_Compare(self, node: ast.Compare) -> int | None:
        """
        Visit Compare node.

        Returns:
            expr_id of the emitted expression, or None on failure
        """
        module_id = self._context.current_module_id
        if module_id is None:
            self._diagnostics.add_error(
                code="VISITOR-002",
                message="No module_id set in context",
                location_id=None,
                module_id=None,
            )
            return None

        # Validate AST structure before opening transaction.
        if not node.comparators or len(node.ops) != len(node.comparators):
            self._diagnostics.add_error(
                code="VISITOR-019",
                message="Malformed comparison expression",
                location_id=None,
                module_id=module_id,
            )
            return None

        # Map operators explicitly.
        mapped_ops: list[str] = []
        for ast_op in node.ops:
            op = self._compare_op_to_string(ast_op)
            if op is None:
                self._diagnostics.add_error(
                    code="VISITOR-020",
                    message=(
                        "Unsupported comparison operator: "
                        f"{type(ast_op).__name__}"
                    ),
                    location_id=None,
                    module_id=module_id,
                )
                return None
            mapped_ops.append(op)

        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        module_path = self._context.current_module_name or "<module>"
        ops_str = "_".join(mapped_ops)

        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.COMPARE,
            identifier=f"compare_{ops_str}",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.COMPARE,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=previous_ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "ops": mapped_ops,
                "left": None,
                "comparators": [],
            },
        )

        success = False
        left_expr_id: int | None = None
        comparators: list[int] = []

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0

            # ---------------------------------------------------------
            # 1. Left operand
            # ---------------------------------------------------------
            left_expr_id = self.visit(node.left)

            if left_expr_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-021",
                    message="Failed to visit left of comparison",
                    location_id=None,
                    module_id=module_id,
                )
            else:
                # -----------------------------------------------------
                # 2. Comparators
                # -----------------------------------------------------
                for index, comparator in enumerate(node.comparators):
                    self._context.expression_ordinal = index + 1

                    comp_expr_id = self.visit(comparator)

                    if comp_expr_id is None:
                        self._diagnostics.add_error(
                            code="VISITOR-022",
                            message=(
                                "Failed to visit comparator "
                                f"{index} of comparison"
                            ),
                            location_id=None,
                            module_id=module_id,
                        )
                        break

                    comparators.append(comp_expr_id)

            # ---------------------------------------------------------
            # 3. Validate complete subtree
            # ---------------------------------------------------------
            if (
                left_expr_id is not None
                and len(comparators) == len(node.comparators)
            ):
                self._emitter.update_expression_payload(
                    expr_id,
                    {
                        "ops": mapped_ops,
                        "left": left_expr_id,
                        "comparators": comparators,
                    },
                )

                self._emitter.commit_transaction(snapshot)
                success = True
                return expr_id

            # ---------------------------------------------------------
            # 4. Fail closed: rollback entire subtree
            # ---------------------------------------------------------
            self._emitter.rollback_transaction(snapshot)

            self._diagnostics.add_error(
                code="VISITOR-023",
                message="Comparison has incomplete children",
                location_id=None,
                module_id=module_id,
            )

            return None

        except Exception:
            self._emitter.rollback_transaction(snapshot)

            self._diagnostics.add_error(
                code="VISITOR-024",
                message="Unexpected error during comparison",
                location_id=None,
                module_id=module_id,
            )

            return None

        finally:
            self._context.expression_parent = parent_expr
            self._context.expression_ordinal = (
                previous_ordinal + 1
                if success
                else previous_ordinal
            )

    def _compare_op_to_string(self, op: ast.cmpop) -> str | None:
        mapping = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
            ast.Is: "is",
            ast.IsNot: "is not",
            ast.In: "in",
            ast.NotIn: "not in",
        }
        return mapping.get(type(op))

    def visit_BoolOp(self, node: ast.BoolOp) -> int | None:
        """
        Visit BoolOp node.

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

        # Validate operator
        op = self._bool_op_to_string(node.op)
        if op is None:
            self._diagnostics.add_error(
                code="VISITOR-025",
                message=f"Unsupported boolean operator: {type(node.op).__name__}",
                location_id=None,
                module_id=None
            )
            return None

        # Validate values
        if not node.values or len(node.values) < 2:
            self._diagnostics.add_error(
                code="VISITOR-026",
                message="Boolean operation must have at least 2 values",
                location_id=None,
                module_id=None
            )
            return None

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.BOOL,
            identifier=f"boolop_{op}",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit parent expression (payload will be filled after children are verified)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.BOOL,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "op": op,
                "values": [],
            },
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        values: list[int] = []
        success = False

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0

            # Visit all values (ordinals 0..N-1)
            for i, value_node in enumerate(node.values):
                self._context.expression_ordinal = i
                value_expr_id = self.visit(value_node)
                if value_expr_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-027",
                        message=f"Failed to visit value {i} of boolean operation",
                        location_id=None,
                        module_id=None,
                    )
                    break
                values.append(value_expr_id)

            # Check if all children are valid
            if len(values) != len(node.values):
                self._emitter.rollback_transaction(snapshot)
                self._diagnostics.add_error(
                    code="VISITOR-028",
                    message="Boolean operation has incomplete children",
                    location_id=None,
                    module_id=None,
                )
                return None

            # All children are valid
            success = True

            # Update payload
            self._emitter.update_expression_payload(
                expr_id,
                {
                    "op": op,
                    "values": values,
                },
            )
            self._emitter.commit_transaction(snapshot)
            return expr_id

        except Exception:
            # Rollback on any exception
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-029",
                message="Unexpected error during boolean operation",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            # Restore parent context
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = (
                previous_ordinal + 1 if success else previous_ordinal
            )

    def _bool_op_to_string(self, op: ast.boolop) -> str | None:
        mapping = {
            ast.And: "and",
            ast.Or: "or",
        }
        return mapping.get(type(op))

    def visit_IfExp(self, node: ast.IfExp) -> int | None:
        """
        Visit IfExp node.

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

        # Validate structure
        if node.test is None or node.body is None or node.orelse is None:
            self._diagnostics.add_error(
                code="VISITOR-030",
                message="Malformed if expression: missing test, body, or orelse",
                location_id=None,
                module_id=None
            )
            return None

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.IF,
            identifier="ifexpr",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit parent expression (payload will be filled after children are verified)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.IF,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "test": None,
                "body": None,
                "orelse": None,
            },
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        test_expr_id: int | None = None
        body_expr_id: int | None = None
        orelse_expr_id: int | None = None
        success = False

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0

            # 1. Visit test (ordinal 0)
            test_expr_id = self.visit(node.test)
            if test_expr_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-031",
                    message="Failed to visit test of if expression",
                    location_id=None,
                    module_id=None,
                )
            else:
                # 2. Visit body (ordinal 1)
                self._context.expression_ordinal = 1
                body_expr_id = self.visit(node.body)
                if body_expr_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-032",
                        message="Failed to visit body of if expression",
                        location_id=None,
                        module_id=None,
                    )
                else:
                    # 3. Visit orelse (ordinal 2)
                    self._context.expression_ordinal = 2
                    orelse_expr_id = self.visit(node.orelse)
                    if orelse_expr_id is None:
                        self._diagnostics.add_error(
                            code="VISITOR-033",
                            message="Failed to visit orelse of if expression",
                            location_id=None,
                            module_id=None,
                        )
                    else:
                        success = True

            # Check if all children are valid
            if not success:
                self._emitter.rollback_transaction(snapshot)
                self._diagnostics.add_error(
                    code="VISITOR-035",
                    message="If expression has incomplete children",
                    location_id=None,
                    module_id=None,
                )
                return None

            # All children are valid
            self._emitter.update_expression_payload(
                expr_id,
                {
                    "test": test_expr_id,
                    "body": body_expr_id,
                    "orelse": orelse_expr_id,
                },
            )
            self._emitter.commit_transaction(snapshot)
            return expr_id

        except Exception:
            # Rollback on any exception
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-034",
                message="Unexpected error during if expression",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            # Restore parent context
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = (
                previous_ordinal + 1 if success else previous_ordinal
            )

    def visit_Slice(
        self,
        node: ast.Slice,
        source_lineno: int = 0,
        source_col_offset: int = 0,
    ) -> int | None:
        """
        Visit Slice node.

        Args:
            node: The Slice AST node
            source_lineno: Line number from parent SubscriptExpr (if available)
            source_col_offset: Column offset from parent SubscriptExpr (if available)

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

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID using source location from parent SubscriptExpr
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.SLICE,
            identifier="slice",
            lineno=source_lineno,
            col_offset=source_col_offset,
        )

        # Emit parent expression
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.SLICE,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={},
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        payload: dict = {}
        success = False

        try:
            self._context.expression_parent = expr_id

            # 1. Lower (ordinal 0) — only if present
            if node.lower is not None:
                self._context.expression_ordinal = 0
                lower_id = self.visit(node.lower)
                if lower_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-036",
                        message="Failed to visit slice lower bound",
                        location_id=None,
                        module_id=None,
                    )
                    self._emitter.rollback_transaction(snapshot)
                    return None
                payload["lower"] = lower_id

            # 2. Upper (ordinal 1) — only if present
            if node.upper is not None:
                self._context.expression_ordinal = 1
                upper_id = self.visit(node.upper)
                if upper_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-037",
                        message="Failed to visit slice upper bound",
                        location_id=None,
                        module_id=None,
                    )
                    self._emitter.rollback_transaction(snapshot)
                    return None
                payload["upper"] = upper_id

            # 3. Step (ordinal 2) — only if present
            if node.step is not None:
                self._context.expression_ordinal = 2
                step_id = self.visit(node.step)
                if step_id is None:
                    self._diagnostics.add_error(
                        code="VISITOR-038",
                        message="Failed to visit slice step",
                        location_id=None,
                        module_id=None,
                    )
                    self._emitter.rollback_transaction(snapshot)
                    return None
                payload["step"] = step_id

            success = True

            self._emitter.update_expression_payload(expr_id, payload)
            self._emitter.commit_transaction(snapshot)
            return expr_id

        except Exception:
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-039",
                message="Unexpected error during slice expression",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = (
                previous_ordinal + 1 if success else previous_ordinal
            )

    def visit_Subscript(self, node: ast.Subscript) -> int | None:
        """
        Visit Subscript node.

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

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID for SubscriptExpr
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.SUBSCRIPT,
            identifier="subscript",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Emit parent expression (payload will be filled after children are verified)
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.SUBSCRIPT,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload={
                "value": None,
                "slice": None,
                "ctx": ctx,
            },
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        value_id: int | None = None
        slice_id: int | None = None
        success = False

        try:
            self._context.expression_parent = expr_id
            self._context.expression_ordinal = 0

            # 1. Visit value (ordinal 0)
            value_id = self.visit(node.value)
            if value_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-041",
                    message="Failed to visit subscript value",
                    location_id=None,
                    module_id=None,
                )
                self._emitter.rollback_transaction(snapshot)
                return None

            # 2. Visit slice (ordinal 1) — with location propagation for Slice nodes
            self._context.expression_ordinal = 1

            if isinstance(node.slice, ast.Slice):
                slice_id = self.visit_Slice(
                    node.slice,
                    source_lineno=node.lineno,
                    source_col_offset=node.col_offset,
                )
            else:
                slice_id = self.visit(node.slice)

            if slice_id is None:
                self._diagnostics.add_error(
                    code="VISITOR-042",
                    message="Failed to visit subscript slice",
                    location_id=None,
                    module_id=None,
                )
                self._emitter.rollback_transaction(snapshot)
                return None

            # All children are valid
            success = True

            self._emitter.update_expression_payload(
                expr_id,
                {
                    "value": value_id,
                    "slice": slice_id,
                    "ctx": ctx,
                },
            )
            self._emitter.commit_transaction(snapshot)
            return expr_id

        except Exception:
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-043",
                message="Unexpected error during subscript expression",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = (
                previous_ordinal + 1 if success else previous_ordinal
            )

    def _slice_identifier(self, node: ast.Slice) -> str:
        """Generate deterministic identifier for slice structure."""
        parts = []
        if node.lower is not None:
            parts.append("l")
        if node.upper is not None:
            parts.append("u")
        if node.step is not None:
            parts.append("s")

        if not parts:
            return "slice_empty"
        return f"slice_{''.join(parts)}"

    def _visit_container(
        self,
        node: ast.List | ast.Tuple | ast.Set | ast.Dict,
        kind: str,
    ) -> int | None:
        """
        Common implementation for List, Tuple, Set, Dict.
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

        # Determine ctx for List/Tuple/Set (Dict has no ctx)
        ctx: str | None = None
        if hasattr(node, "ctx") and node.ctx is not None:
            if isinstance(node.ctx, ast.Store):
                ctx = "store"
            elif isinstance(node.ctx, ast.Del):
                ctx = "del"
            else:
                ctx = "load"

        # Begin transaction
        snapshot = self._emitter.begin_transaction()

        parent_expr = self._context.expression_parent
        ordinal = self._context.expression_ordinal

        # Generate stable ID
        module_path = self._context.current_module_name or "<module>"
        stable_id = stable_expression_id(
            module_path=module_path,
            kind=ExpressionKind.CONTAINER,
            identifier=f"container_{kind}",
            lineno=node.lineno,
            col_offset=node.col_offset,
        )

        # Determine payload structure
        if kind in ("list", "tuple", "set"):
            payload: dict = {
                "kind": kind,
                "elements": [],
                "ctx": ctx,
            }
        else:  # dict
            payload = {
                "kind": kind,
                "entries": [],
            }

        # Emit parent expression
        expr_id = self._emitter.emit_expression(
            kind=ExpressionKind.CONTAINER,
            module_id=module_id,
            parent_expr=parent_expr,
            ordinal=ordinal,
            location_id=UNRESOLVED_LOCATION_ID,
            stable_id=stable_id,
            payload=payload,
        )

        previous_parent = self._context.expression_parent
        previous_ordinal = self._context.expression_ordinal

        elements: list[int] = []
        entries: list[dict] = []
        success = False

        try:
            self._context.expression_parent = expr_id

            if kind in ("list", "tuple", "set"):
                # List/Tuple/Set: elements
                # Extract elts based on node type
                if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
                    elts = node.elts
                else:
                    self._diagnostics.add_error(
                        code="VISITOR-048",
                        message=f"Unexpected node type for {kind}: {type(node).__name__}",
                        location_id=None,
                        module_id=None,
                    )
                    self._emitter.rollback_transaction(snapshot)
                    return None

                for i, elt in enumerate(elts):
                    self._context.expression_ordinal = i
                    elt_id = self.visit(elt)
                    if elt_id is None:
                        self._diagnostics.add_error(
                            code="VISITOR-044",
                            message=f"Failed to visit element {i} of {kind}",
                            location_id=None,
                            module_id=None,
                        )
                        self._emitter.rollback_transaction(snapshot)
                        return None
                    elements.append(elt_id)

                success = True
                self._emitter.update_expression_payload(
                    expr_id,
                    {
                        "kind": kind,
                        "elements": elements,
                        "ctx": ctx,
                    },
                )

            else:  # dict
                # Dict: keys and values
                if not isinstance(node, ast.Dict):
                    self._diagnostics.add_error(
                        code="VISITOR-049",
                        message=f"Expected Dict node, got {type(node).__name__}",
                        location_id=None,
                        module_id=None,
                    )
                    self._emitter.rollback_transaction(snapshot)
                    return None

                for i, (key_node, value_node) in enumerate(zip(node.keys, node.values)):
                    # key ordinal: 2*i
                    self._context.expression_ordinal = 2 * i
                    key_id = None
                    if key_node is not None:
                        key_id = self.visit(key_node)
                        if key_id is None:
                            self._diagnostics.add_error(
                                code="VISITOR-045",
                                message=f"Failed to visit key {i} of dict",
                                location_id=None,
                                module_id=None,
                            )
                            self._emitter.rollback_transaction(snapshot)
                            return None

                    # value ordinal: 2*i + 1
                    self._context.expression_ordinal = 2 * i + 1
                    value_id = self.visit(value_node)
                    if value_id is None:
                        self._diagnostics.add_error(
                            code="VISITOR-046",
                            message=f"Failed to visit value {i} of dict",
                            location_id=None,
                            module_id=None,
                        )
                        self._emitter.rollback_transaction(snapshot)
                        return None

                    entries.append({
                        "key": key_id,
                        "value": value_id,
                    })

                success = True
                self._emitter.update_expression_payload(
                    expr_id,
                    {
                        "kind": kind,
                        "entries": entries,
                    },
                )

            self._emitter.commit_transaction(snapshot)
            return expr_id

        except Exception:
            self._emitter.rollback_transaction(snapshot)
            self._diagnostics.add_error(
                code="VISITOR-047",
                message=f"Unexpected error during {kind} expression",
                location_id=None,
                module_id=None,
            )
            return None

        finally:
            self._context.expression_parent = previous_parent
            self._context.expression_ordinal = (
                previous_ordinal + 1 if success else previous_ordinal
            )

    def visit_List(self, node: ast.List) -> int | None:
        return self._visit_container(node, "list")

    def visit_Tuple(self, node: ast.Tuple) -> int | None:
        return self._visit_container(node, "tuple")

    def visit_Set(self, node: ast.Set) -> int | None:
        return self._visit_container(node, "set")

    def visit_Dict(self, node: ast.Dict) -> int | None:
        return self._visit_container(node, "dict")