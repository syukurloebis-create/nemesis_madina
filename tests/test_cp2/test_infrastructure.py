import pytest

from ir.allocators import Allocator
from ir.config import IRConfig
from ir.context import IRContext
from ir.emitter import Emitter
from ir.models import ExpressionKind
from ir.repositories import ExpressionRepository


class TestTransactionInfrastructure:
    def test_allocator_reset_to(self):
        alloc = Allocator()
        alloc.allocate()
        alloc.allocate()
        assert alloc.current() == 2
        alloc.reset_to(1)
        assert alloc.current() == 1
        alloc.reset_to(0)
        assert alloc.current() == 0

    def test_allocator_reset_to_invalid_forward(self):
        alloc = Allocator()
        alloc.allocate()
        alloc.allocate()
        with pytest.raises(ValueError, match="Cannot reset allocator forward"):
            alloc.reset_to(5)

    def test_allocator_reset_to_invalid_negative(self):
        alloc = Allocator()
        with pytest.raises(ValueError, match="Invalid reset target"):
            alloc.reset_to(-1)

    def test_repository_rollback(self):
        repo = ExpressionRepository()
        # Create expressions with valid IDs
        from ir.models import Expression, ExpressionKind
        expr1 = Expression(
            expr_id=1,
            stable_id="id1",
            kind=ExpressionKind.NAME,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            payload={"id": "x", "ctx": "load"},
        )
        expr2 = Expression(
            expr_id=2,
            stable_id="id2",
            kind=ExpressionKind.NAME,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            payload={"id": "y", "ctx": "load"},
        )
        repo.insert(expr1)
        repo.insert(expr2)
        assert repo.count() == 2
        assert repo.get(1) is not None
        assert repo.get(2) is not None

        repo.rollback(1)
        assert repo.count() == 1
        assert repo.get(1) is not None
        assert repo.get(2) is None

    def test_repository_rollback_invalid(self):
        repo = ExpressionRepository()
        with pytest.raises(ValueError, match="Invalid rollback target"):
            repo.rollback(5)

    def test_repository_rollback_frozen(self):
        repo = ExpressionRepository()
        repo.freeze()
        with pytest.raises(RuntimeError, match="Repository is frozen"):
            repo.rollback(0)

    def test_context_snapshot_restore(self):
        context = IRContext(config=IRConfig())
        context.expression_parent = 10
        context.expression_ordinal = 5

        snapshot = context.snapshot()

        context.expression_parent = 20
        context.expression_ordinal = 10
        context.expr_alloc.allocate()
        context.expr_alloc.allocate()

        context.restore(snapshot)

        assert context.expression_parent == 10
        assert context.expression_ordinal == 5
        assert context.expr_alloc.current() == 0
        assert context.expressions.count() == 0

    def test_context_snapshot_restore_invalid(self):
        context = IRContext(config=IRConfig())
        snapshot = context.snapshot()

        # Tidak ada mutation, restore dengan target yang sama
        # Harus tidak error
        context.restore(snapshot)

        # Harus error jika snapshot expression count > current
        context.expressions.rollback(0)  # kosongkan
        with pytest.raises(ValueError, match="exceeds current count"):
            context.restore({"expression_count": 5, "expression_parent": 0, "expression_ordinal": 0, "expr_alloc_current": 0})

    def test_emitter_transaction_rollback(self):
        context = IRContext(config=IRConfig())
        emitter = Emitter(context)

        snapshot = emitter.begin_transaction()

        emitter.emit_expression(
            kind=ExpressionKind.NAME,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test-stable-id",
            payload={"id": "x", "ctx": "load"},
        )

        assert context.expressions.count() == 1

        emitter.rollback_transaction(snapshot)

        assert context.expressions.count() == 0

        def test_emitter_transaction_commit(self):
            context = IRContext(config=IRConfig())
            emitter = Emitter(context)

            snapshot = emitter.begin_transaction()

            expr_id = emitter.emit_expression(
                kind=ExpressionKind.NAME,
                module_id=1,
                parent_expr=None,
                ordinal=0,
                location_id=0,
                stable_id="test-stable-id",
                payload={"id": "x", "ctx": "load"},
            )

            emitter.commit_transaction(snapshot)

            assert context.expressions.count() == 1
            assert context.expressions.get(expr_id) is not None

    def test_emitter_transaction_commit(self):
        context = IRContext(config=IRConfig())
        emitter = Emitter(context)

        snapshot = emitter.begin_transaction()

        expr_id = emitter.emit_expression(
            kind=ExpressionKind.NAME,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test-stable-id",
            payload={"id": "x", "ctx": "load"},
        )

        emitter.commit_transaction(snapshot)

        assert context.expressions.count() == 1
        assert context.expressions.get(expr_id) is not None