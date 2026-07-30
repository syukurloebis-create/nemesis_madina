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

    # ============ AttributeExpr Tests ============

    def test_attribute_expr_load(self):
        """obj.attr → AttributeExpr with load context"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("obj.attr")
        attr_node = tree.body[0].value
        expr_id = visitor.visit_Attribute(attr_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        attr_exprs = [e for e in exprs if e.kind == ExpressionKind.ATTRIBUTE]
        assert len(attr_exprs) == 1
        attr_expr = attr_exprs[0]
        assert attr_expr.payload["attr"] == "attr"
        assert attr_expr.payload["ctx"] == "load"
        assert attr_expr.payload["base"] is not None
        assert attr_expr.parent_expr is None
        assert attr_expr.ordinal == 0

    def test_attribute_expr_store(self):
        """obj.attr = x → AttributeExpr with store context"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("obj.attr = 1")
        attr_node = tree.body[0].targets[0]
        expr_id = visitor.visit_Attribute(attr_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        attr_exprs = [e for e in exprs if e.kind == ExpressionKind.ATTRIBUTE]
        assert len(attr_exprs) == 1
        assert attr_exprs[0].payload["ctx"] == "store"

    def test_attribute_expr_del(self):
        """del obj.attr → AttributeExpr with del context"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("del obj.attr")
        del_node = tree.body[0]
        attr_node = del_node.targets[0]
        expr_id = visitor.visit_Attribute(attr_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        attr_exprs = [e for e in exprs if e.kind == ExpressionKind.ATTRIBUTE]
        assert len(attr_exprs) == 1
        assert attr_exprs[0].payload["ctx"] == "del"

    def test_attribute_expr_parent_child(self):
        """AttributeExpr should have base as child"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("obj.attr")
        attr_node = tree.body[0].value
        expr_id = visitor.visit_Attribute(attr_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        attr_expr = next(e for e in exprs if e.kind == ExpressionKind.ATTRIBUTE)
        base_expr_id = attr_expr.payload["base"]

        base_expr = next(e for e in exprs if e.expr_id == base_expr_id)
        assert base_expr.kind == ExpressionKind.NAME
        assert base_expr.payload["id"] == "obj"
        assert base_expr.parent_expr == attr_expr.expr_id
        assert base_expr.ordinal == 0

    def test_attribute_expr_nested(self):
        """Nested attribute: obj.a.b"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("obj.a.b")
        attr_node = tree.body[0].value

        root_id = visitor.visit_Attribute(attr_node)

        assert root_id is not None

        exprs = context.expressions.all()

        # Root: b
        root = next(e for e in exprs if e.expr_id == root_id)
        assert root.kind == ExpressionKind.ATTRIBUTE
        assert root.payload["attr"] == "b"
        assert root.parent_expr is None
        assert root.ordinal == 0

        # Middle: a
        middle = next(e for e in exprs if e.expr_id == root.payload["base"])
        assert middle.kind == ExpressionKind.ATTRIBUTE
        assert middle.payload["attr"] == "a"
        assert middle.parent_expr == root.expr_id
        assert middle.ordinal == 0

        # Base: obj
        base = next(e for e in exprs if e.expr_id == middle.payload["base"])
        assert base.kind == ExpressionKind.NAME
        assert base.payload["id"] == "obj"
        assert base.parent_expr == middle.expr_id
        assert base.ordinal == 0

    def test_attribute_expr_stable_id_deterministic(self):
        """Stable ID for AttributeExpr should be deterministic"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree = ast.parse("obj.attr")
        attr_node = tree.body[0].value

        visitor1.visit_Attribute(attr_node)
        visitor2.visit_Attribute(attr_node)

        id1 = context1.expressions.all()[0].stable_id
        id2 = context2.expressions.all()[0].stable_id
        assert id1 == id2

    # ============ CallExpr Tests ============

    def test_call_empty(self):
        """f() → CallExpr with empty args/keywords"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f()")
        call_node = tree.body[0].value
        expr_id = visitor.visit_Call(call_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        call_expr = next(e for e in exprs if e.kind == ExpressionKind.CALL)
        assert call_expr.payload["callee"] is not None
        assert call_expr.payload["args"] == []
        assert call_expr.payload["keywords"] == []

    def test_call_positional(self):
        """f(x) → CallExpr with positional arg"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f(x)")
        call_node = tree.body[0].value
        expr_id = visitor.visit_Call(call_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        call_expr = next(e for e in exprs if e.kind == ExpressionKind.CALL)
        assert len(call_expr.payload["args"]) == 1
        assert call_expr.payload["keywords"] == []

    def test_call_multiple_args(self):
        """f(x, y) → CallExpr with ordered args"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f(x, y)")
        call_node = tree.body[0].value
        expr_id = visitor.visit_Call(call_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        call_expr = next(e for e in exprs if e.kind == ExpressionKind.CALL)
        assert len(call_expr.payload["args"]) == 2

        # Verify order matches AST: x then y
        arg0 = next(e for e in exprs if e.expr_id == call_expr.payload["args"][0])
        arg1 = next(e for e in exprs if e.expr_id == call_expr.payload["args"][1])
        assert arg0.payload["id"] == "x"
        assert arg1.payload["id"] == "y"

    def test_call_keyword(self):
        """f(x, y=1) → CallExpr with keyword arg"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f(x, y=1)")
        call_node = tree.body[0].value
        expr_id = visitor.visit_Call(call_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        call_expr = next(e for e in exprs if e.kind == ExpressionKind.CALL)
        assert len(call_expr.payload["args"]) == 1
        assert len(call_expr.payload["keywords"]) == 1
        assert call_expr.payload["keywords"][0]["name"] == "y"

    def test_call_kwargs(self):
        """f(**kwargs) → CallExpr with keyword name:null"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f(**kwargs)")
        call_node = tree.body[0].value
        expr_id = visitor.visit_Call(call_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        call_expr = next(e for e in exprs if e.kind == ExpressionKind.CALL)
        assert len(call_expr.payload["keywords"]) == 1
        assert call_expr.payload["keywords"][0]["name"] is None

    def test_call_nested(self):
        """f(g(x)) → CallExpr with nested CallExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f(g(x))")
        call_node = tree.body[0].value
        root_id = visitor.visit_Call(call_node)

        assert root_id is not None

        exprs = context.expressions.all()

        # Root call: f(g(x))
        root = next(e for e in exprs if e.expr_id == root_id)
        assert root.kind == ExpressionKind.CALL
        assert root.parent_expr is None

        # Callee: f
        callee_id = root.payload["callee"]
        callee = next(e for e in exprs if e.expr_id == callee_id)
        assert callee.kind == ExpressionKind.NAME
        assert callee.payload["id"] == "f"
        assert callee.parent_expr == root.expr_id

        # Inner call: g(x)
        inner_id = root.payload["args"][0]
        inner = next(e for e in exprs if e.expr_id == inner_id)
        assert inner.kind == ExpressionKind.CALL
        assert inner.parent_expr == root.expr_id

        # Inner callee: g
        inner_callee_id = inner.payload["callee"]
        inner_callee = next(e for e in exprs if e.expr_id == inner_callee_id)
        assert inner_callee.kind == ExpressionKind.NAME
        assert inner_callee.payload["id"] == "g"
        assert inner_callee.parent_expr == inner.expr_id

        # Inner arg: x
        inner_arg_id = inner.payload["args"][0]
        inner_arg = next(e for e in exprs if e.expr_id == inner_arg_id)
        assert inner_arg.kind == ExpressionKind.NAME
        assert inner_arg.payload["id"] == "x"
        assert inner_arg.parent_expr == inner.expr_id

    def test_call_child_ordinals(self):
        """f(x, y) → CallExpr with correct child ordinals"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("f(x, y)")
        call_node = tree.body[0].value
        expr_id = visitor.visit_Call(call_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        call_expr = next(e for e in exprs if e.kind == ExpressionKind.CALL)

        # Find children by expr_id
        callee_id = call_expr.payload["callee"]
        arg0_id = call_expr.payload["args"][0]
        arg1_id = call_expr.payload["args"][1]

        callee = next(e for e in exprs if e.expr_id == callee_id)
        arg0 = next(e for e in exprs if e.expr_id == arg0_id)
        arg1 = next(e for e in exprs if e.expr_id == arg1_id)

        # Ordinals: callee=0, arg0=1, arg1=2
        assert callee.ordinal == 0
        assert arg0.ordinal == 1
        assert arg1.ordinal == 2

        # Parent relationships
        assert callee.parent_expr == call_expr.expr_id
        assert arg0.parent_expr == call_expr.expr_id
        assert arg1.parent_expr == call_expr.expr_id

    # ============ BinaryExpr Tests ============

    def test_binary_add(self):
        """a + b → BinaryExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a + b")
        binop_node = tree.body[0].value
        expr_id = visitor.visit_BinOp(binop_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        bin_expr = next(e for e in exprs if e.kind == ExpressionKind.BINARY)
        assert bin_expr.payload["op"] == "+"
        assert bin_expr.payload["left"] is not None
        assert bin_expr.payload["right"] is not None

    def test_binary_all_operators(self):
        """Test all binary operators"""
        operators = [
            ("+", ast.Add),
            ("-", ast.Sub),
            ("*", ast.Mult),
            ("/", ast.Div),
            ("//", ast.FloorDiv),
            ("%", ast.Mod),
            ("**", ast.Pow),
            ("@", ast.MatMult),
            ("<<", ast.LShift),
            (">>", ast.RShift),
            ("|", ast.BitOr),
            ("^", ast.BitXor),
            ("&", ast.BitAnd),
        ]

        for op_str, op_cls in operators:
            context = IRContext(config=IRConfig())
            context.current_module_id = 1
            context.current_module_name = "test"

            visitor = Visitor(context)

            tree = ast.parse(f"a {op_str} b")
            binop_node = tree.body[0].value
            expr_id = visitor.visit_BinOp(binop_node)

            assert expr_id is not None

            exprs = context.expressions.all()
            bin_expr = next(e for e in exprs if e.kind == ExpressionKind.BINARY)
            assert bin_expr.payload["op"] == op_str, f"Operator {op_str} failed"

    def test_binary_parent_child(self):
        """BinaryExpr parent-child relationship"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a + b")
        binop_node = tree.body[0].value
        expr_id = visitor.visit_BinOp(binop_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        bin_expr = next(e for e in exprs if e.kind == ExpressionKind.BINARY)

        # Verify left child
        left_id = bin_expr.payload["left"]
        left = next(e for e in exprs if e.expr_id == left_id)
        assert left.kind == ExpressionKind.NAME
        assert left.payload["id"] == "a"
        assert left.parent_expr == bin_expr.expr_id
        assert left.ordinal == 0

        # Verify right child
        right_id = bin_expr.payload["right"]
        right = next(e for e in exprs if e.expr_id == right_id)
        assert right.kind == ExpressionKind.NAME
        assert right.payload["id"] == "b"
        assert right.parent_expr == bin_expr.expr_id
        assert right.ordinal == 1

    def test_binary_nested(self):
        """(a + b) * c → nested binary expressions"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("(a + b) * c")
        binop_node = tree.body[0].value
        root_id = visitor.visit_BinOp(binop_node)

        assert root_id is not None

        exprs = context.expressions.all()

        # Root: (a + b) * c
        root = next(e for e in exprs if e.expr_id == root_id)
        assert root.kind == ExpressionKind.BINARY
        assert root.payload["op"] == "*"
        assert root.parent_expr is None

        # Left: a + b (inner binary)
        inner_id = root.payload["left"]
        inner = next(e for e in exprs if e.expr_id == inner_id)
        assert inner.kind == ExpressionKind.BINARY
        assert inner.payload["op"] == "+"
        assert inner.parent_expr == root.expr_id

        # Inner left: a
        inner_left_id = inner.payload["left"]
        inner_left = next(e for e in exprs if e.expr_id == inner_left_id)
        assert inner_left.kind == ExpressionKind.NAME
        assert inner_left.payload["id"] == "a"
        assert inner_left.parent_expr == inner.expr_id

        # Inner right: b
        inner_right_id = inner.payload["right"]
        inner_right = next(e for e in exprs if e.expr_id == inner_right_id)
        assert inner_right.kind == ExpressionKind.NAME
        assert inner_right.payload["id"] == "b"
        assert inner_right.parent_expr == inner.expr_id

        # Root right: c
        root_right_id = root.payload["right"]
        root_right = next(e for e in exprs if e.expr_id == root_right_id)
        assert root_right.kind == ExpressionKind.NAME
        assert root_right.payload["id"] == "c"
        assert root_right.parent_expr == root.expr_id

    def test_binary_stable_id_deterministic(self):
        """Stable ID for BinaryExpr should be deterministic"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree = ast.parse("a + b")
        binop_node = tree.body[0].value

        visitor1.visit_BinOp(binop_node)
        visitor2.visit_BinOp(binop_node)

        bin1 = next(e for e in context1.expressions.all() if e.kind == ExpressionKind.BINARY)
        bin2 = next(e for e in context2.expressions.all() if e.kind == ExpressionKind.BINARY)

        assert bin1.stable_id == bin2.stable_id

    def test_binary_fail_closed(self):
        """BinaryExpr should be fail-closed: no malformed Expression remains."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("a + (1, 2)")
        binop_node = tree.body[0].value
        expr_id = visitor.visit_BinOp(binop_node)

        # Should return None (no expression emitted)
        assert expr_id is None

        # No BinaryExpr should remain in repository
        exprs = context.expressions.all()
        bin_exprs = [e for e in exprs if e.kind == ExpressionKind.BINARY]
        assert len(bin_exprs) == 0

        # Should have error diagnostics
        errors = context.diagnostics.get_errors()
        assert any(e.code == "VISITOR-013" for e in errors)
