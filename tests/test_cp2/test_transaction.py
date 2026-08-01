# tests/test_cp2/test_transaction.py

import pytest

from ir.config import IRConfig
from ir.context import IRContext, IRInvariantError, TransactionHandle
from ir.emitter import Emitter
from ir.models import BlockKind, BlockRole, StatementKind, ExpressionKind, Module


class TestTransactionFoundation:
    """Test CP2.5-INFRA-TX v1.0 Transaction Foundation."""

    def _make_context(self) -> IRContext:
        context = IRContext(config=IRConfig())
        # Use Module repository as single source of truth
        module = Module(
            module_id=1,
            name="test",
            file="test.py",
            file_hash="hash",
        )
        context.modules.insert(module)
        context.current_module_id = module.module_id
        # current_module_name is a read-only property from repository
        return context

    def _make_emitter(self, context: IRContext) -> Emitter:
        return Emitter(context)

    # =========================================================================
    # Transaction Lifecycle Tests
    # =========================================================================

    def test_begin_transaction_returns_handle(self):
        """begin_transaction() returns a TransactionHandle."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        assert isinstance(handle, TransactionHandle)

        emitter.commit_transaction(handle)

    def test_commit_consumes_handle(self):
        """commit_transaction() consumes the handle (removes from registry)."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        assert context._contains_transaction(handle)

        emitter.commit_transaction(handle)

        assert not context._contains_transaction(handle)

    def test_rollback_consumes_handle(self):
        """rollback_transaction() consumes the handle (removes from registry)."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        assert context._contains_transaction(handle)

        emitter.rollback_transaction(handle)

        assert not context._contains_transaction(handle)

    def test_double_commit_raises_error(self):
        """commit_transaction() twice raises IRInvariantError."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        emitter.commit_transaction(handle)

        with pytest.raises(IRInvariantError, match="Invalid or already consumed"):
            emitter.commit_transaction(handle)

    def test_double_rollback_raises_error(self):
        """rollback_transaction() twice raises IRInvariantError."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        emitter.rollback_transaction(handle)

        with pytest.raises(IRInvariantError, match="Invalid or already consumed"):
            emitter.rollback_transaction(handle)

    def test_commit_after_rollback_raises_error(self):
        """commit_transaction() after rollback_transaction() raises IRInvariantError."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        emitter.rollback_transaction(handle)

        with pytest.raises(IRInvariantError, match="Invalid or already consumed"):
            emitter.commit_transaction(handle)

    def test_rollback_after_commit_raises_error(self):
        """rollback_transaction() after commit_transaction() raises IRInvariantError."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        emitter.commit_transaction(handle)

        with pytest.raises(IRInvariantError, match="Invalid or already consumed"):
            emitter.rollback_transaction(handle)

    # =========================================================================
    # Registry Cleanup Tests
    # =========================================================================

    def test_registry_empty_after_commit(self):
        """Registry should be empty after commit."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        assert context._transaction_count() == 1

        emitter.commit_transaction(handle)
        assert context._transaction_count() == 0

    def test_registry_empty_after_rollback(self):
        """Registry should be empty after rollback."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()
        assert context._transaction_count() == 1

        emitter.rollback_transaction(handle)
        assert context._transaction_count() == 0

    def test_registry_growth_prevention(self):
        """Registry should not leak transactions."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        for _ in range(5):
            handle = emitter.begin_transaction()
            assert context._transaction_count() == 1
            emitter.commit_transaction(handle)
            assert context._transaction_count() == 0

        assert context._transaction_count() == 0

    # =========================================================================
    # Rollback State Restoration Tests
    # =========================================================================

    def test_rollback_restores_repositories(self):
        """rollback_transaction() restores expression/statement/block repositories."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        initial_expr_count = context.expressions.count()
        initial_stmt_count = context.statements.count()
        initial_block_count = context.blocks.count()

        tx = emitter.begin_transaction()

        block_id = emitter.emit_block(
            kind=BlockKind.MODULE,
            role=BlockRole.ROOT,
            module_id=1,
            scope_id=1,
            ordinal=0,
            parent_block_id=None,
            stable_id="test_block",
        )
        emitter.emit_statement(
            kind=StatementKind.PASS,
            module_id=1,
            scope_id=1,
            block_id=block_id,
            ordinal=0,
            location_id=0,
            stable_id="test_stmt",
        )
        emitter.emit_expression(
            kind=ExpressionKind.CONSTANT,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test_expr",
            payload={"value": 0, "value_type": "int"},
        )

        assert context.expressions.count() > initial_expr_count
        assert context.statements.count() > initial_stmt_count
        assert context.blocks.count() > initial_block_count

        emitter.rollback_transaction(tx)

        assert context.expressions.count() == initial_expr_count
        assert context.statements.count() == initial_stmt_count
        assert context.blocks.count() == initial_block_count

    def test_rollback_restores_allocators(self):
        """rollback_transaction() restores allocator positions."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        tx = emitter.begin_transaction()

        initial_expr_alloc = context.expr_alloc.current()
        initial_stmt_alloc = context.stmt_alloc.current()
        initial_block_alloc = context.block_alloc.current()

        block_id = emitter.emit_block(
            kind=BlockKind.MODULE,
            role=BlockRole.ROOT,
            module_id=1,
            scope_id=1,
            ordinal=0,
            parent_block_id=None,
            stable_id="test_block",
        )
        emitter.emit_statement(
            kind=StatementKind.PASS,
            module_id=1,
            scope_id=1,
            block_id=block_id,
            ordinal=0,
            location_id=0,
            stable_id="test_stmt",
        )
        emitter.emit_expression(
            kind=ExpressionKind.CONSTANT,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test_expr",
            payload={"value": 0, "value_type": "int"},
        )

        assert context.expr_alloc.current() > initial_expr_alloc
        assert context.stmt_alloc.current() > initial_stmt_alloc
        assert context.block_alloc.current() > initial_block_alloc

        emitter.rollback_transaction(tx)

        assert context.expr_alloc.current() == initial_expr_alloc
        assert context.stmt_alloc.current() == initial_stmt_alloc
        assert context.block_alloc.current() == initial_block_alloc

    def test_rollback_maintains_allocator_repository_consistency(self):
        """After rollback, allocator positions must match repository counts."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        tx = emitter.begin_transaction()

        block_id = emitter.emit_block(
            kind=BlockKind.MODULE,
            role=BlockRole.ROOT,
            module_id=1,
            scope_id=1,
            ordinal=0,
            parent_block_id=None,
            stable_id="test_block",
        )
        emitter.emit_statement(
            kind=StatementKind.PASS,
            module_id=1,
            scope_id=1,
            block_id=block_id,
            ordinal=0,
            location_id=0,
            stable_id="test_stmt",
        )
        emitter.emit_expression(
            kind=ExpressionKind.CONSTANT,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test_expr",
            payload={"value": 0, "value_type": "int"},
        )

        emitter.rollback_transaction(tx)

        # Consistency check: repository count == allocator position
        assert context.expressions.count() == context.expr_alloc.current()
        assert context.statements.count() == context.stmt_alloc.current()
        assert context.blocks.count() == context.block_alloc.current()

    def test_rollback_restores_emission_state(self):
        """rollback_transaction() restores expression_parent and expression_ordinal."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        context.expression_parent = 42
        context.expression_ordinal = 99

        tx = emitter.begin_transaction()

        context.expression_parent = 100
        context.expression_ordinal = 200

        emitter.rollback_transaction(tx)

        assert context.expression_parent == 42
        assert context.expression_ordinal == 99

    # =========================================================================
    # Transaction Handle Opaqueness Tests
    # =========================================================================

    def test_handle_is_opaque(self):
        """TransactionHandle should not expose internal state."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()

        # __id should not be accessible
        with pytest.raises(AttributeError):
            handle.__id  # type: ignore

        # _id should not be accessible
        with pytest.raises(AttributeError):
            handle._id  # type: ignore

        # _internal_id() is friend API (internal contract)
        # It exists for IRContext and testing
        assert handle._internal_id() is not None

        emitter.commit_transaction(handle)

    def test_handle_has_no_snapshot(self):
        """TransactionHandle should not contain snapshot data."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        handle = emitter.begin_transaction()

        # Should not have snapshot attributes
        assert not hasattr(handle, "_snapshot")
        assert not hasattr(handle, "__snapshot")

        emitter.commit_transaction(handle)

    # =========================================================================
    # Context Manager Tests
    # =========================================================================

    def test_transaction_context_manager_auto_commits(self):
        """with emitter.transaction() should auto-commit on success."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        with emitter.transaction() as tx:
            assert isinstance(tx, TransactionHandle)
            assert context._transaction_count() == 1

        assert context._transaction_count() == 0

    def test_transaction_context_manager_auto_rollbacks(self):
        """with emitter.transaction() should auto-rollback on exception."""
        context = self._make_context()
        emitter = self._make_emitter(context)

        with pytest.raises(ValueError, match="test exception"):
            with emitter.transaction() as tx:
                assert context._transaction_count() == 1
                raise ValueError("test exception")

        assert context._transaction_count() == 0

    def test_traversal_context_manager_restores(self):
        """with context.traversal() should restore traversal state."""
        context = self._make_context()
        context.current_scope_id = 42
        context.current_qualname = "test"

        with context.traversal():
            context.current_scope_id = 100
            context.current_qualname = "modified"

            assert context.current_scope_id == 100
            assert context.current_qualname == "modified"

        assert context.current_scope_id == 42
        assert context.current_qualname == "test"

    # =========================================================================
    # Snapshot Validation Tests (Internal Contract Testing)
    # =========================================================================

    def test_rollback_validation_before_apply(self):
        """rollback_transaction() should validate snapshot consistency before apply.
        
        This test intentionally manipulates internal registry state to
        test the validation mechanism. This is an internal contract test.
        """
        context = self._make_context()
        emitter = self._make_emitter(context)

        tx = emitter.begin_transaction()
        tx_id = tx._internal_id()

        # Intentionally corrupt the snapshot with mismatched expression count
        # This tests the internal validation mechanism
        snapshot = context._transactions[tx_id]
        corrupt_snapshot = snapshot.__class__(
            expression_count=snapshot.expression_count + 100,
            statement_count=snapshot.statement_count,
            block_count=snapshot.block_count,
            expr_alloc_current=snapshot.expr_alloc_current,
            stmt_alloc_current=snapshot.stmt_alloc_current,
            block_alloc_current=snapshot.block_alloc_current,
            expression_parent=snapshot.expression_parent,
            expression_ordinal=snapshot.expression_ordinal,
        )
        context._transactions[tx_id] = corrupt_snapshot

        with pytest.raises(IRInvariantError, match="exceeds current count"):
            emitter.rollback_transaction(tx)

        # Handle should remain in registry (not consumed on validation failure)
        assert context._contains_transaction(tx)

        # Clean up
        context._transactions.pop(tx_id, None)

    def test_rollback_validation_after_apply(self):
        """rollback_transaction() should validate state after apply.
        
        This test intentionally manipulates internal registry state to
        test the validation mechanism. This is an internal contract test.
        """
        context = self._make_context()
        emitter = self._make_emitter(context)

        tx = emitter.begin_transaction()
        tx_id = tx._internal_id()

        # Intentionally corrupt snapshot with non-existent expression_parent
        # This tests the post-rollback validation mechanism
        snapshot = context._transactions[tx_id]
        corrupt_snapshot = snapshot.__class__(
            expression_count=snapshot.expression_count,
            statement_count=snapshot.statement_count,
            block_count=snapshot.block_count,
            expr_alloc_current=snapshot.expr_alloc_current,
            stmt_alloc_current=snapshot.stmt_alloc_current,
            block_alloc_current=snapshot.block_alloc_current,
            expression_parent=999,  # Non-existent
            expression_ordinal=snapshot.expression_ordinal,
        )
        context._transactions[tx_id] = corrupt_snapshot

        with pytest.raises(IRInvariantError, match="does not exist after rollback"):
            emitter.rollback_transaction(tx)

        # Handle should be removed from registry (rollback was applied)
        assert not context._contains_transaction(tx)