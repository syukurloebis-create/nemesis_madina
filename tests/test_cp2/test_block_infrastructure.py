# tests/test_cp2/test_block_infrastructure.py

import ast
import pytest

from ir.config import IRConfig
from ir.context import IRContext
from ir.visitor import Visitor
from ir.models import BlockKind, BlockRole, StatementKind, ExpressionKind, Module
from .conftest import make_test_context


class TestBlockInfrastructure:
    def _make_context(self) -> IRContext:
        context = IRContext(config=IRConfig())
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
        """Module Scope → ROOT Block created at scope creation."""
        context = self._make_context()
        visitor = Visitor(context)

        visitor.visit(ast.parse("x = 1"))

        blocks = context.blocks.all()
        assert len(blocks) == 1

        root = blocks[0]
        assert root.kind == BlockKind.MODULE
        assert root.role == BlockRole.ROOT
        assert root.parent_block_id is None
        assert root.ordinal == 0
        assert root.scope_id == context.current_scope_id
        assert root.stable_id != ""
        assert context.current_block_id == root.block_id
        assert context.block_stack == [root.block_id]

    def test_root_block_created_for_empty_module(self):
        """Empty module must still have ROOT Block."""
        context = self._make_context()
        visitor = Visitor(context)

        visitor.visit(ast.parse(""))

        blocks = context.blocks.all()
        assert len(blocks) == 1
        assert blocks[0].role == BlockRole.ROOT
        assert blocks[0].kind == BlockKind.MODULE

    def test_class_and_function_root_blocks(self):
        """Class and Function Scopes must have ROOT Blocks."""
        context = self._make_context()
        visitor = Visitor(context)

        visitor.visit(ast.parse("class Foo: pass\ndef bar(): pass"))

        blocks = context.blocks.all()
        # Module root + Class root + Function root
        assert len(blocks) == 3

        root_roles = [b.role for b in blocks]
        assert root_roles.count(BlockRole.ROOT) == 3

        # Kinds: MODULE, FUNCTION, FUNCTION
        kinds = [b.kind for b in blocks]
        assert BlockKind.MODULE in kinds
        assert kinds.count(BlockKind.FUNCTION) == 2

    def test_statement_block_linkage_and_ordinals(self):
        """Statement.block_id must reference existing Block."""
        context = self._make_context()
        visitor = Visitor(context)

        visitor.visit(ast.parse("x = 1\ny = 2"))

        stmts = context.statements.all()
        assert len(stmts) == 2

        block_id = context.current_block_id
        assert block_id is not None

        assert stmts[0].block_id == block_id
        assert stmts[1].block_id == block_id
        assert stmts[0].ordinal == 0
        assert stmts[1].ordinal == 1
        assert stmts[0].stable_id != ""
        assert stmts[1].stable_id != ""

    def test_import_statement_block_linkage(self):
        """Import statements must have block_id set."""
        context = self._make_context()
        visitor = Visitor(context)

        visitor.visit(ast.parse("import os\nfrom backend import services"))

        stmts = context.statements.all()
        assert len(stmts) == 2
        for stmt in stmts:
            assert stmt.block_id is not None
            assert stmt.stable_id != ""
            assert stmt.ordinal in (0, 1)

    def test_statement_stable_id_deterministic(self):
        """Statement.stable_id must be deterministic across fresh contexts."""
        source = "x = 1"
        node = ast.parse(source).body[0]

        context1 = self._make_context()
        visitor1 = Visitor(context1)
        visitor1.visit(node)

        context2 = self._make_context()
        visitor2 = Visitor(context2)
        visitor2.visit(node)

        stmt1 = context1.statements.all()[0]
        stmt2 = context2.statements.all()[0]

        # Stable IDs must be identical
        assert stmt1.stable_id == stmt2.stable_id

        # Runtime IDs are allocator-dependent, both start at 1
        assert stmt1.stmt_id == stmt2.stmt_id

        # Both must have block_id
        assert stmt1.block_id is not None
        assert stmt2.block_id is not None

    def test_block_stable_id_deterministic(self):
        """Block.stable_id must be deterministic across fresh contexts."""
        source = "x = 1"
        node = ast.parse(source)

        context1 = self._make_context()
        visitor1 = Visitor(context1)
        visitor1.visit(node)

        context2 = self._make_context()
        visitor2 = Visitor(context2)
        visitor2.visit(node)

        block1 = context1.blocks.all()[0]
        block2 = context2.blocks.all()[0]

        assert block1.stable_id == block2.stable_id
        assert block1.block_id == block2.block_id  # Both start at 1

    def test_block_ordinal_separate_from_statement_ordinal(self):
        """Block ordinal and statement ordinal must be separate counters."""
        context = self._make_context()
        visitor = Visitor(context)

        visitor.visit(ast.parse("x = 1\ny = 2"))

        # Block ordinal = 0 (root), statements have their own ordinals
        blocks = context.blocks.all()
        assert len(blocks) == 1
        assert blocks[0].ordinal == 0

        stmts = context.statements.all()
        assert stmts[0].ordinal == 0
        assert stmts[1].ordinal == 1

    def test_transaction_rollback_restores_all_state(self):
        """Transaction rollback must restore all CP2.5 state."""
        context = self._make_context()
        visitor = Visitor(context)

        # Set initial state
        context.current_block_id = 42
        context.block_stack = [42, 43]
        context.statement_ordinals = {42: 5, 43: 3}
        context.block_ordinals = {42: 2, 43: 1}
        context.expression_parent = 99
        context.expression_ordinal = 7

        snapshot = context.snapshot()

        try:
            # Emit block (allocates)
            block_id = visitor._emitter.emit_block(
                kind=BlockKind.MODULE,
                role=BlockRole.ROOT,
                module_id=1,
                scope_id=1,
                ordinal=0,
                parent_block_id=None,
                stable_id="test_block_stable",
                location_id=0,
            )

            # Emit statement (allocates)
            visitor._emitter.emit_statement(
                kind=StatementKind.PASS,
                module_id=1,
                scope_id=1,
                block_id=block_id,
                ordinal=0,
                location_id=0,
                stable_id="test_stmt_stable",
            )

            # Emit expression (allocates)
            visitor._emitter.emit_expression(
                kind=ExpressionKind.CONSTANT,
                module_id=1,
                parent_expr=None,
                ordinal=0,
                location_id=0,
                stable_id="test_expr_stable",
                payload={"value": 0, "value_type": "int"},
            )

            # Mutate context state
            context.current_block_id = block_id
            context.block_stack = [42, block_id]
            context.statement_ordinals[block_id] = 10
            context.block_ordinals[block_id] = 5
            context.expression_parent = 88
            context.expression_ordinal = 99

            # Verify mutations occurred
            assert context.expressions.count() == snapshot["expression_count"] + 1
            assert context.statements.count() == snapshot["statement_count"] + 1
            assert context.blocks.count() == snapshot["block_count"] + 1
            assert context.current_block_id != snapshot["current_block_id"]

            raise ValueError("Forced rollback test")

        except ValueError:
            context.restore(snapshot)

        # Verify all state restored
        assert context.expressions.count() == snapshot["expression_count"]
        assert context.statements.count() == snapshot["statement_count"]
        assert context.blocks.count() == snapshot["block_count"]

        assert context.expr_alloc.current() == snapshot["expr_alloc_current"]
        assert context.stmt_alloc.current() == snapshot["stmt_alloc_current"]
        assert context.block_alloc.current() == snapshot["block_alloc_current"]

        assert context.current_block_id == snapshot["current_block_id"]
        assert context.block_stack == snapshot["block_stack"]
        assert context.statement_ordinals == snapshot["statement_ordinals"]
        assert context.block_ordinals == snapshot["block_ordinals"]
        assert context.expression_parent == snapshot["expression_parent"]
        assert context.expression_ordinal == snapshot["expression_ordinal"]

    def test_root_block_validation_multiple_roots(self):
        """Multiple ROOT Blocks in same Scope must raise ValueError."""
        context = self._make_context()
        visitor = Visitor(context)

        # Create first ROOT Block
        block_id1 = visitor._emitter.emit_block(
            kind=BlockKind.MODULE,
            role=BlockRole.ROOT,
            module_id=1,
            scope_id=1,
            ordinal=0,
            parent_block_id=None,
            stable_id="root1_stable",
            location_id=0,
        )
        context.block_ordinals[block_id1] = 0
        context.statement_ordinals[block_id1] = 0

        # Attempt to create second ROOT Block should fail
        with pytest.raises(ValueError, match="already has a ROOT Block"):
            visitor._create_root_block(scope_id=1, node=None)

    def test_non_root_block_requires_parent(self):
        """Non-root Block must have parent_block_id."""
        context = self._make_context()
        visitor = Visitor(context)

        with pytest.raises(ValueError, match="requires parent_block_id"):
            visitor._emitter.emit_block(
                kind=BlockKind.IF,
                role=BlockRole.BODY,
                module_id=1,
                scope_id=1,
                ordinal=0,
                parent_block_id=None,
                stable_id="body_stable",
                location_id=0,
            )

    def test_parent_block_scope_validation(self):
        """Child Block scope_id must equal parent scope_id."""
        context = self._make_context()
        visitor = Visitor(context)

        # Create parent block in scope 1
        parent_id = visitor._emitter.emit_block(
            kind=BlockKind.MODULE,
            role=BlockRole.ROOT,
            module_id=1,
            scope_id=1,
            ordinal=0,
            parent_block_id=None,
            stable_id="parent_stable",
            location_id=0,
        )

        # Attempt child with different scope_id
        with pytest.raises(ValueError, match="must equal parent Block scope_id"):
            visitor._emitter.emit_block(
                kind=BlockKind.IF,
                role=BlockRole.BODY,
                module_id=1,
                scope_id=2,  # Different scope
                ordinal=0,
                parent_block_id=parent_id,
                stable_id="child_stable",
                location_id=0,
            )

    def test_block_stack_scope_local_replacement(self):
        """Scope entry replaces block stack (not append)."""
        context = self._make_context()
        visitor = Visitor(context)

        # Module scope
        visitor.visit(ast.parse("class Foo: pass"))

        # After module: block_stack = [module_root]
        initial_stack = context.block_stack.copy()
        assert len(initial_stack) == 1

        # Enter function scope - should REPLACE, not append
        visitor.visit(ast.parse("def bar(): pass"))

        # block_stack should be replaced, not accumulated
        assert len(context.block_stack) == 1
        assert context.block_stack[0] != initial_stack[0]