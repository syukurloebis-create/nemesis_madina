# ir/visitor.py

import ast
from typing import Optional

from .context import IRContext
from .models import Scope, ScopeKind
from .emitter import Emitter

# Sentinel for unresolved location
UNRESOLVED_LOCATION_ID = 0


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

    def visit(self, node: ast.AST) -> None:
        """Visit an AST node and emit IR entities."""
        method_name = f"visit_{node.__class__.__name__}"
        method = getattr(self, method_name, self._visit_default)
        method(node)

    def _visit_default(self, node: ast.AST) -> None:
        """Default visitor for unsupported nodes."""
        self._diagnostics.add_warning(
            code="VISITOR-001",
            message=f"Unsupported AST node: {type(node).__name__}",
            location_id=None,
            module_id=None
        )

    def visit_Module(self, node: ast.Module) -> None:
        """
        Visit Module node.

        CP2.2A: Allocate module scope
        CP2.2B: Traverse ClassDef only
        CP2.2C: Traverse FunctionDef and AsyncFunctionDef only
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

        # CP2.2B: Traverse ClassDef
        # CP2.2C: Traverse FunctionDef and AsyncFunctionDef
        for child in node.body:
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(child)
            # Other nodes are ignored in CP2.2C

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

        # CP2.2C: NO traversal of node.body

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node, is_async=True)
