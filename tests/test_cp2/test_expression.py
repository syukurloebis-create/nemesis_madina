# tests/test_cp2/test_expression.py

import ast

from ir.context import IRContext
from ir.config import IRConfig
from ir.visitor import Visitor
from ir.models import ExpressionKind


class TestExpressionIR:
    def test_name_expr_load(self):
        """NameExpr with load context."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x")
        name_node = tree.body[0].value
        expr_id = visitor.visit_Name(name_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        assert len(exprs) == 1
        assert exprs[0].kind == ExpressionKind.NAME
        assert exprs[0].payload["id"] == "x"
        assert exprs[0].payload["ctx"] == "load"
        assert exprs[0].parent_expr is None
        assert exprs[0].ordinal == 0
        assert len(exprs[0].stable_id) > 0

    def test_name_expr_store(self):
        """NameExpr with store context."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x = 1")
        assign_node = tree.body[0]
        target_name = assign_node.targets[0]

        expr_id = visitor.visit_Name(target_name)

        assert expr_id is not None
        exprs = context.expressions.all()
        name_exprs = [e for e in exprs if e.kind == ExpressionKind.NAME]
        assert len(name_exprs) == 1
        assert name_exprs[0].payload["id"] == "x"
        assert name_exprs[0].payload["ctx"] == "store"

    def test_name_expr_del(self):
        """NameExpr with del context."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("del x")
        del_node = tree.body[0]
        target_name = del_node.targets[0]

        expr_id = visitor.visit_Name(target_name)

        assert expr_id is not None
        exprs = context.expressions.all()
        name_exprs = [e for e in exprs if e.kind == ExpressionKind.NAME]
        assert len(name_exprs) == 1
        assert name_exprs[0].payload["ctx"] == "del"

    def test_name_expr_parent_ordinal(self):
        """NameExpr with parent and ordinal."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Create a parent expression (returns expr_id integer)
        parent_expr_id = visitor._emitter.emit_expression(
            kind=ExpressionKind.CONSTANT,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test_stable_id",
            payload={"value": 0, "value_type": "int"},
        )

        context.expression_parent = parent_expr_id
        context.expression_ordinal = 5

        tree = ast.parse("x")
        name_node = tree.body[0].value
        expr_id = visitor.visit_Name(name_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        name_expr = [e for e in exprs if e.kind == ExpressionKind.NAME][0]

        assert name_expr.parent_expr == parent_expr_id
        assert name_expr.ordinal == 5

    def test_name_expr_stable_id_deterministic(self):
        """Stable ID should be deterministic for same input."""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree = ast.parse("x")
        name_node = tree.body[0].value

        visitor1.visit_Name(name_node)
        visitor2.visit_Name(name_node)

        id1 = context1.expressions.all()[0].stable_id
        id2 = context2.expressions.all()[0].stable_id
        assert id1 == id2

    # ============ ConstantExpr Tests ============

    def test_constant_none(self):
        """None → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=None, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] is None
        assert const_expr.payload["value_type"] == "none"

    def test_constant_bool(self):
        """True → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=True, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] is True
        assert const_expr.payload["value_type"] == "bool"

    def test_constant_int(self):
        """42 → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=42, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] == 42
        assert const_expr.payload["value_type"] == "int"

    def test_constant_float(self):
        """3.14 → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=3.14, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] == 3.14
        assert const_expr.payload["value_type"] == "float"

    def test_constant_complex(self):
        """1+2j → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=1 + 2j, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] == [1.0, 2.0]
        assert const_expr.payload["value_type"] == "complex"

    def test_constant_str(self):
        """'hello' → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value="hello", lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] == "hello"
        assert const_expr.payload["value_type"] == "str"

    def test_constant_bytes(self):
        """b'abc' → ConstantExpr with hex"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=b"abc", lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] == "616263"
        assert const_expr.payload["value_type"] == "bytes"

    def test_constant_ellipsis(self):
        """... → ConstantExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        const_node = ast.Constant(value=Ellipsis, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        const_expr = [e for e in exprs if e.kind == ExpressionKind.CONSTANT][0]
        assert const_expr.payload["value"] is None
        assert const_expr.payload["value_type"] == "ellipsis"

    def test_constant_unsupported_type(self):
        """Unsupported constant type → diagnostic + no expression"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        class UnsupportedType:
            pass

        const_node = ast.Constant(value=UnsupportedType(), lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is None
        exprs = context.expressions.all()
        const_exprs = [e for e in exprs if e.kind == ExpressionKind.CONSTANT]
        assert len(const_exprs) == 0

        warnings = context.diagnostics.get_warnings()
        assert any(w.code == "VISITOR-004" for w in warnings)

    def test_constant_parent_ordinal(self):
        """Constant with parent and ordinal."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        parent_expr_id = visitor._emitter.emit_expression(
            kind=ExpressionKind.CONSTANT,
            module_id=1,
            parent_expr=None,
            ordinal=0,
            location_id=0,
            stable_id="test_stable_id",
            payload={"value": 0, "value_type": "int"},
        )

        context.expression_parent = parent_expr_id
        context.expression_ordinal = 3

        const_node = ast.Constant(value=42, lineno=1, col_offset=0)
        expr_id = visitor.visit_Constant(const_node)

        assert expr_id is not None
        assert expr_id != parent_expr_id

        exprs = context.expressions.all()
        const_expr = next(e for e in exprs if e.expr_id == expr_id)

        assert const_expr.kind == ExpressionKind.CONSTANT
        assert const_expr.parent_expr == parent_expr_id
        assert const_expr.ordinal == 3

    def test_constant_stable_id_deterministic(self):
        """Stable ID should be deterministic"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        const_node = ast.Constant(value=42, lineno=1, col_offset=0)

        visitor1.visit_Constant(const_node)
        visitor2.visit_Constant(const_node)

        id1 = context1.expressions.all()[0].stable_id
        id2 = context2.expressions.all()[0].stable_id
        assert id1 == id2