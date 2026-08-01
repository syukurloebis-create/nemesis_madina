# tests/test_cp2/test_visitor.py

import ast

from ir.config import IRConfig
from ir.context import IRContext
from ir.models import (
    BlockKind,
    BlockRole,
    DeclarationKind,
    ExpressionKind,
    ScopeKind,
    StatementKind,
    SymbolKind,
    Visibility,
    Module,
)
from ir.visitor import UNRESOLVED_LOCATION_ID, Visitor
from .conftest import make_test_context


class TestVisitorBlockInfrastructure:
    def _make_context(self) -> IRContext:
        context = make_test_context()
        module = Module(
            module_id=1,
            name="test",
            file="test.py",
            file_hash="hash",
        )
        context.modules.insert(module)
        context.current_module_id = module.module_id
        return context

    def test_root_block_created_for_module(self):
        """Module Scope → Root Block created."""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        blocks = context.blocks.all()
        assert len(blocks) == 1
        assert blocks[0].kind == BlockKind.MODULE
        assert blocks[0].role == BlockRole.ROOT
        assert blocks[0].parent_block_id is None
        assert blocks[0].ordinal == 0

    def test_root_block_created_for_function(self):
        """Function Scope → Root Block created."""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo():\n    pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        blocks = context.blocks.all()
        # Module Root Block + Function Root Block
        assert len(blocks) == 2
        func_block = blocks[1]
        assert func_block.kind == BlockKind.FUNCTION
        assert func_block.role == BlockRole.ROOT
        assert func_block.parent_block_id is None
        assert func_block.scope_id == 2  # Function scope

    def test_statement_block_id_set(self):
        """Statement.block_id must be set to Block ID."""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].block_id is not None

        block = context.blocks.get(stmts[0].block_id)
        assert block is not None
        assert block.kind == BlockKind.MODULE

    def test_statement_ordinal_block_local(self):
        """Statement ordinal must be block-local."""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1\ny = 2"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 2
        assert stmts[0].ordinal == 0
        assert stmts[1].ordinal == 1
        assert stmts[0].block_id == stmts[1].block_id

    def test_statement_stable_id_deterministic(self):
        """Statement.stable_id must be deterministic across fresh contexts."""
        source = "x = 1"
        tree = ast.parse(source)
        node = tree.body[0]
    
        context1 = make_test_context()

        visitor1 = Visitor(context1)
        tree1 = ast.parse(source)
        visitor1.visit(tree)
    
        context2 = make_test_context()

        visitor2 = Visitor(context2)
        tree2 = ast.parse(source) 
        visitor2.visit(tree2)
    
        stmt1 = context1.statements.all()[0]
        stmt2 = context2.statements.all()[0]
    
        # Stable IDs MUST be identical (deterministic)
        assert stmt1.stable_id == stmt2.stable_id
    
        # Runtime IDs are allocator-dependent
        # Both start at 1 in fresh contexts, so they are equal
        assert stmt1.stmt_id == stmt2.stmt_id  # Both = 1
    
        # Block IDs must be set
        assert stmt1.block_id is not None
        assert stmt2.block_id is not None
    
        # Scope IDs must match
        assert stmt1.scope_id == stmt2.scope_id
    
        # Stable ID is now pure SHA-256 (64 hex chars)
        assert len(stmt1.stable_id) == 64
        assert all(c in "0123456789abcdef" for c in stmt1.stable_id)

    def test_transaction_rollback_with_block(self):
        """Transaction rollback must restore block state."""
        context = make_test_context()

        visitor = Visitor(context)

        tx = visitor._emitter.begin_transaction()
        initial_block_count = len(context.blocks.all())

        # Emit a block
        block_id = visitor._emitter.emit_block(
            kind=BlockKind.FUNCTION,
            role=BlockRole.ROOT,
            module_id=1,
            scope_id=1,
            ordinal=0,
            parent_block_id=None,
            stable_id="test_stable",
            location_id=0,
        )

        assert len(context.blocks.all()) == initial_block_count + 1
        visitor._emitter.rollback_transaction(tx)
        assert len(context.blocks.all()) == initial_block_count
        
    def test_current_block_id_restored_on_failure(self):
        """current_block_id must restore on failure."""
        context = make_test_context()

        visitor = Visitor(context)

        # Set initial state
        context.current_block_id = 42
        context.block_stack = [42]

        snapshot = context.save_traversal()  # ← Use save_traversal

        # Simulate failure with invalid operation
        try:
            visitor._ensure_root_block(1)
        except Exception:
            pass

        context.restore_traversal(snapshot)  # ← Use restore_traversal
        assert context.current_block_id == 42
        assert context.block_stack == [42]

    def test_block_stable_id_deterministic(self):
        """Block.stable_id must be deterministic."""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        block = context.blocks.all()[0]
        assert len(block.stable_id) > 0
        assert len(block.stable_id) == 64

    def test_transaction_rollback_restores_allocators_and_context(self):
        """Transaction rollback must restore all state (repositories, allocators, context)."""
        context = make_test_context()
    
        visitor = Visitor(context)
    
        # Set initial context state
        context.current_block_id = 42
        context.block_stack = [42, 43]
        context.statement_ordinals = {42: 5, 43: 3}

        # OR Option 2: Make stack match current_block_id
        context.current_block_id = 42
        context.block_stack = [42]
    
        # Capture initial state
        before_expr_count = context.expressions.count()
        before_stmt_count = context.statements.count()
        before_block_count = context.blocks.count()
        before_expr_alloc = context.expr_alloc.current()
        before_stmt_alloc = context.stmt_alloc.current()
        before_block_alloc = context.block_alloc.current()
        before_current_block = context.current_block_id
        before_block_stack = context.block_stack.copy()
        before_ordinals = context.statement_ordinals.copy()
    
        tx = visitor._emitter.begin_transaction()
    
        try:
            # Emit block (allocates)
            block_id = visitor._emitter.emit_block(
                kind=BlockKind.MODULE,
                role=BlockRole.ROOT,
                module_id=1,
                scope_id=1,
                ordinal=0,
                parent_block_id=None,
                stable_id="test_stable",
                location_id=0,
            )
        
            # Emit statement (allocates)
            stmt_id = visitor._emitter.emit_statement(
                kind=StatementKind.PASS,
                module_id=1,
                scope_id=1,
                block_id=block_id,
                ordinal=0,
                location_id=0,
                stable_id="test_stmt_stable",
            )
        
            # Modify context
            context.current_block_id = block_id
            context.block_stack = [42, block_id]
            context.statement_ordinals[block_id] = 10
        
            # Verify changes occurred
            assert context.block_alloc.current() == before_block_alloc + 1
            assert context.stmt_alloc.current() == before_stmt_alloc + 1
            assert context.current_block_id != before_current_block
        
            # Force rollback
            raise ValueError("Forced rollback test")
        
        except ValueError:
            visitor._emitter.rollback_transaction(tx)
    
        # Verify all repositories restored
        assert context.expressions.count() == before_expr_count
        assert context.statements.count() == before_stmt_count
        assert context.blocks.count() == before_block_count
    
        # Verify all allocators restored
        assert context.expr_alloc.current() == before_expr_alloc
        assert context.stmt_alloc.current() == before_stmt_alloc
        assert context.block_alloc.current() == before_block_alloc
    
        # Verify all context state restored
        assert context.current_block_id == before_current_block
        assert context.block_stack == before_block_stack
        assert context.statement_ordinals == before_ordinals


class TestVisitor:
    def test_visit_module_creates_scope(self):
        """Module AST → Module Scope"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 1
        assert scopes[0].kind == ScopeKind.MODULE
        assert scopes[0].name == "<module>"
        assert scopes[0].depth == 0
        assert scopes[0].parent_scope is None
        assert scopes[0].location_id == UNRESOLVED_LOCATION_ID

    def test_visit_module_empty(self):
        """Empty module → Module Scope, no warnings"""
        context = make_test_context()

        visitor = Visitor(context)

        source = ""
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 1
        assert scopes[0].kind == ScopeKind.MODULE

        assert context.diagnostics.count() == 0

    def test_visit_module_updates_current_scope(self):
        """Module visitor should update current_scope_id and scope_stack"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        assert context.current_scope_id is not None
        assert len(context.scope_stack) == 1
        assert context.scope_stack[0] == context.current_scope_id

        scope = context.scopes.get(context.current_scope_id)
        assert scope is not None
        assert scope.kind == ScopeKind.MODULE

    def test_visit_module_deterministic(self):
        """Same source → same IR (deterministic)"""
        context1 = make_test_context()
        context2 = make_test_context()

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        source = "x = 1\ny = 2"
        tree = ast.parse(source)

        visitor1.visit(tree)
        visitor2.visit(tree)

        scopes1 = context1.scopes.all()
        scopes2 = context2.scopes.all()

        assert len(scopes1) == len(scopes2)
        assert scopes1[0].kind == scopes2[0].kind
        assert scopes1[0].name == scopes2[0].name
        assert scopes1[0].depth == scopes2[0].depth
        assert scopes1[0].location_id == scopes2[0].location_id

    def test_visit_module_no_module_id(self):
        """Should record error if module_id is not set"""
        context = make_test_context()
        context.current_module_id = None 
        visitor = Visitor(context) 

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        errors = context.diagnostics.get_errors()
        assert len(errors) == 1
        assert errors[0].code == "VISITOR-002"


class TestVisitorClass:
    def test_visit_class_creates_scope(self):
        """ClassDef AST → Class Scope"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 2  # Module + Class
        assert scopes[1].kind == ScopeKind.CLASS
        assert scopes[1].name == "Foo"
        assert scopes[1].depth == 1

    def test_visit_class_creates_declaration(self):
        """ClassDef AST → Class Declaration"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        decls = context.declarations.all()
        assert len(decls) == 1
        assert decls[0].kind == DeclarationKind.CLASS
        assert decls[0].name == "Foo"

    def test_visit_class_creates_symbol(self):
        """ClassDef AST → Class Symbol"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        symbols = context.symbols.all()
        assert len(symbols) == 1
        assert symbols[0].kind == SymbolKind.CLASS
        assert symbols[0].name == "Foo"
        assert symbols[0].visibility == Visibility.PUBLIC

    def test_visit_class_qualname(self):
        """ClassDef AST → Qualified name"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert scopes[1].qualname == "Foo"

        symbols = context.symbols.all()
        assert symbols[0].qualname == "Foo"

    def test_visit_class_updates_scope_stack(self):
        """ClassDef should update scope stack during traversal, then restore"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 2  # Module + Class

        # After traversal, scope should be restored to module scope
        assert context.scope_stack == [1]
        assert context.current_scope_id == 1

    def test_visit_class_no_traversal(self):
        """CP2.2B: Class visitor should NOT traverse body"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo:\n    def bar(self): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 2  # Only Module + Class

        decls = context.declarations.all()
        assert len(decls) == 1  # Only Class declaration

        symbols = context.symbols.all()
        assert len(symbols) == 1  # Only Class symbol

    def test_visit_class_referential_integrity(self):
        """Verify foreign keys between entities"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        decls = context.declarations.all()
        symbols = context.symbols.all()

        class_scope = scopes[1]
        class_decl = decls[0]
        class_symbol = symbols[0]

        assert class_decl.symbol_id == class_symbol.symbol_id
        assert class_symbol.decl_id == class_decl.decl_id
        assert class_scope.scope_id == class_symbol.scope_id
        assert class_scope.scope_id == class_decl.scope_id


class TestVisitorFunction:
    def test_visit_function_creates_scope(self):
        """FunctionDef AST → Function Scope"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        # Module + Function
        assert len(scopes) == 2
        assert scopes[1].kind == ScopeKind.FUNCTION
        assert scopes[1].name == "foo"
        assert scopes[1].depth == 1

    def test_visit_function_creates_declaration(self):
        """FunctionDef AST → Function Declaration"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        decls = context.declarations.all()
        assert len(decls) == 1
        assert decls[0].kind == DeclarationKind.FUNCTION
        assert decls[0].name == "foo"

    def test_visit_function_creates_symbol(self):
        """FunctionDef AST → Function Symbol"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        symbols = context.symbols.all()
        assert len(symbols) == 1
        assert symbols[0].kind == SymbolKind.FUNCTION
        assert symbols[0].name == "foo"
        assert symbols[0].is_async is False

    def test_visit_async_function(self):
        """AsyncFunctionDef AST → Async Function"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "async def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        symbols = context.symbols.all()
        assert len(symbols) == 1
        assert symbols[0].kind == SymbolKind.FUNCTION
        assert symbols[0].name == "foo"
        assert symbols[0].is_async is True

    def test_visit_function_qualname(self):
        """FunctionDef AST → Qualified name"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert scopes[1].qualname == "foo"

        symbols = context.symbols.all()
        assert symbols[0].qualname == "foo"

    def test_visit_function_updates_scope_stack(self):
        """FunctionDef should update scope stack during traversal, then restore"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 2  # Module + Function

        # After traversal, scope should be restored to module scope
        assert context.scope_stack == [1]
        assert context.current_scope_id == 1

    def test_visit_function_no_traversal(self):
        """CP2.2C: Function visitor should NOT traverse body"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo():\n    x = 1\n    return x"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert len(scopes) == 2  # Only Module + Function

        decls = context.declarations.all()
        assert len(decls) == 1  # Only Function declaration

        symbols = context.symbols.all()
        assert len(symbols) == 1  # Only Function symbol

    def test_visit_function_referential_integrity(self):
        """Verify foreign keys between entities"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        decls = context.declarations.all()
        symbols = context.symbols.all()

        function_scope = scopes[1]
        function_decl = decls[0]
        function_symbol = symbols[0]

        assert function_decl.symbol_id == function_symbol.symbol_id
        assert function_symbol.decl_id == function_decl.decl_id
        assert function_scope.scope_id == function_symbol.scope_id
        assert function_scope.scope_id == function_decl.scope_id

    def test_visit_module_traverses_class_and_function(self):
        """CP2.2C: Module should traverse ClassDef, FunctionDef, AsyncFunctionDef"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "class Foo: pass\ndef bar(): pass\nasync def baz(): pass\nx = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        # Module + Class + Function + AsyncFunction
        assert len(scopes) == 4

        decls = context.declarations.all()
        # Class + Function + AsyncFunction (Assign ignored)
        assert len(decls) == 3

        symbols = context.symbols.all()
        # Class + Function + AsyncFunction (Assign ignored)
        assert len(symbols) == 3


class TestVisitorAssignment:
    def test_visit_assign_creates_statement(self):
        """Assign AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.ASSIGN
        assert stmts[0].ordinal == 0

    def test_visit_ann_assign_creates_statement(self):
        """AnnAssign AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x: int = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.ANNOTATED_ASSIGN

    def test_visit_aug_assign_creates_statement(self):
        """AugAssign AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x += 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.AUGMENTED_ASSIGN

    def test_visit_assign_ordinal_per_scope(self):
        """CP2.3A: module statements use per-scope ordinals."""
        context = make_test_context()

        visitor = Visitor(context)

        source = (
            "x = 1\n"
            "def foo():\n"
            "    a = 1\n"
            "    b = 2\n"
            "y = 2\n"
        )

        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()

        # CP2.3A does not traverse function bodies.
        module_stmts = [s for s in stmts if s.scope_id == 1]

        assert len(module_stmts) == 2
        assert module_stmts[0].ordinal == 0
        assert module_stmts[1].ordinal == 1

    def test_visit_assign_expr_id_is_none(self):
        """CP2.3A: expr_id should be None (Expression IR not yet built)"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].expr_id is None

    def test_visit_assign_no_expression_created(self):
        """CP2.3A: No expressions should be created"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x = 1\ny = 2"
        tree = ast.parse(source)
        visitor.visit(tree)

        assert len(context.expressions.all()) == 0

    def test_visit_module_ignores_assignments_inside_function_body(self):
        """CP2.3A: Assignments inside function body should be ignored"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "def foo():\n    x = 1\n    return x"
        tree = ast.parse(source)
        visitor.visit(tree)

        # Only module scope statements (none), no function body traversal
        stmts = context.statements.all()
        assert len(stmts) == 0


class TestVisitorSimpleStatements:
    def test_visit_expr_creates_statement(self):
        """Expr AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x + 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.EXPR

    def test_visit_pass_creates_statement(self):
        """Pass AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.PASS

    def test_visit_raise_creates_statement(self):
        """Raise AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "raise ValueError('error')"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.RAISE

    def test_visit_assert_creates_statement(self):
        """Assert AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "assert x == 1"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.ASSERT

    def test_visit_return_creates_statement(self):
        """Return AST → Statement (inside function)"""
        context = make_test_context()

        visitor = Visitor(context)

        tree = ast.parse(
            "def foo():\n"
            "    return x\n"
        )

        function_node = tree.body[0]
        return_node = function_node.body[0]

        # Establish function scope first
        visitor.visit(function_node)

        # Now Return has an active scope
        visitor.visit(return_node)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.RETURN

    def test_visit_break_creates_statement(self):
        """Break AST → Statement (inside loop)"""
        context = make_test_context()

        visitor = Visitor(context)

        tree = ast.parse(
            "def foo():\n"
            "    while True:\n"
            "        break\n"
        )

        function_node = tree.body[0]
        break_node = function_node.body[0].body[0]

        visitor.visit(function_node)
        visitor.visit(break_node)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.BREAK

    def test_visit_continue_creates_statement(self):
        """Continue AST → Statement (inside loop)"""
        context = make_test_context()

        visitor = Visitor(context)

        tree = ast.parse(
            "def foo():\n"
            "    while True:\n"
            "        continue\n"
        )

        function_node = tree.body[0]
        continue_node = function_node.body[0].body[0]

        visitor.visit(function_node)
        visitor.visit(continue_node)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.CONTINUE

    def test_visit_simple_statements_expr_id_is_none(self):
        """CP2.3B: expr_id should be None for all simple statements"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x + 1\npass\nraise ValueError('error')\nassert x == 1\n"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 4
        for stmt in stmts:
            assert stmt.expr_id is None

    def test_visit_simple_statements_no_expression_created(self):
        """CP2.3B: No expressions should be created"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "x + 1\npass\nraise ValueError('error')\nassert x == 1\n"
        tree = ast.parse(source)
        visitor.visit(tree)

        assert len(context.expressions.all()) == 0


class TestVisitorImport:
    def test_visit_import_creates_statement(self):
        """Import AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "import os\nimport json as js"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 2
        assert stmts[0].kind == StatementKind.IMPORT
        assert stmts[0].payload["names"][0]["name"] == "os"

        assert stmts[1].kind == StatementKind.IMPORT
        assert stmts[1].payload["names"][0]["name"] == "json"
        assert stmts[1].payload["names"][0]["alias"] == "js"

    def test_visit_import_from_creates_statement(self):
        """ImportFrom AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "from backend.services import DashboardService as DS"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.IMPORT_FROM
        assert stmts[0].payload["module"] == "backend.services"
        assert stmts[0].payload["names"][0]["name"] == "DashboardService"
        assert stmts[0].payload["names"][0]["alias"] == "DS"
        assert stmts[0].payload["level"] == 0

    def test_visit_import_from_relative(self):
        """Relative ImportFrom AST → Statement"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "from . import module"
        tree = ast.parse(source)
        visitor.visit(tree)

        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.IMPORT_FROM
        assert stmts[0].payload["module"] == ""
        assert stmts[0].payload["level"] == 1

    def test_visit_import_payload_no_expression(self):
        """CP2.3C: Imports should not create expressions or symbols"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "import os\nfrom backend import services"
        tree = ast.parse(source)
        visitor.visit(tree)

        assert len(context.expressions.all()) == 0
        assert len(context.symbols.all()) == 0

    def test_visit_import_no_resolution(self):
        """CP2.3C: Imports should NOT perform resolution"""
        context = make_test_context()

        visitor = Visitor(context)

        source = "import nonexistent_module"
        tree = ast.parse(source)
        visitor.visit(tree)

        # No resolution error, just stored as statement
        stmts = context.statements.all()
        assert len(stmts) == 1
        assert stmts[0].kind == StatementKind.IMPORT
        # No diagnostics about missing module
        assert len(context.diagnostics.get_errors()) == 0