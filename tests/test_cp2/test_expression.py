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

    # ============ UnaryExpr Tests ============

    def test_unary_not(self):
        """not a → UnaryExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("not a")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        unary_expr = next(e for e in exprs if e.kind == ExpressionKind.UNARY)
        assert unary_expr.payload["op"] == "not"
        assert unary_expr.payload["operand"] is not None

    def test_unary_usub(self):
        """-a → UnaryExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("-a")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        unary_expr = next(e for e in exprs if e.kind == ExpressionKind.UNARY)
        assert unary_expr.payload["op"] == "-"

    def test_unary_uadd(self):
        """+a → UnaryExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("+a")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        unary_expr = next(e for e in exprs if e.kind == ExpressionKind.UNARY)
        assert unary_expr.payload["op"] == "+"

    def test_unary_invert(self):
        """~a → UnaryExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("~a")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        unary_expr = next(e for e in exprs if e.kind == ExpressionKind.UNARY)
        assert unary_expr.payload["op"] == "~"

    def test_unary_parent_child(self):
        """UnaryExpr parent-child relationship"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("not a")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        unary_expr = next(e for e in exprs if e.kind == ExpressionKind.UNARY)

        # Verify operand
        operand_id = unary_expr.payload["operand"]
        operand = next(e for e in exprs if e.expr_id == operand_id)
        assert operand.kind == ExpressionKind.NAME
        assert operand.payload["id"] == "a"
        assert operand.parent_expr == unary_expr.expr_id
        assert operand.ordinal == 0

    def test_unary_ordinal_on_success(self):
        """UnaryExpr ordinal advances on success"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Set initial ordinal
        context.expression_ordinal = 5

        tree = ast.parse("not a")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is not None
        # Ordinal should advance (success case)
        assert context.expression_ordinal == 6

    def test_unary_ordinal_on_failure(self):
        """UnaryExpr ordinal does NOT advance on failure"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Set initial ordinal
        context.expression_ordinal = 5

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("not (1, 2)")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        assert expr_id is None
        # Ordinal should NOT advance (failure case)
        assert context.expression_ordinal == 5

    def test_unary_fail_closed(self):
        """UnaryExpr should be fail-closed: no malformed Expression remains."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("not (1, 2)")
        unary_node = tree.body[0].value
        expr_id = visitor.visit_UnaryOp(unary_node)

        # Should return None (no expression emitted)
        assert expr_id is None

        # No UnaryExpr should remain in repository
        exprs = context.expressions.all()
        unary_exprs = [e for e in exprs if e.kind == ExpressionKind.UNARY]
        assert len(unary_exprs) == 0

        # Should have error diagnostics
        errors = context.diagnostics.get_errors()
        assert any(e.code == "VISITOR-017" for e in errors)

    def test_unary_stable_id_deterministic(self):
        """Stable ID for UnaryExpr should be deterministic"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree = ast.parse("not a")
        unary_node = tree.body[0].value

        visitor1.visit_UnaryOp(unary_node)
        visitor2.visit_UnaryOp(unary_node)

        unary1 = next(e for e in context1.expressions.all() if e.kind == ExpressionKind.UNARY)
        unary2 = next(e for e in context2.expressions.all() if e.kind == ExpressionKind.UNARY)

        assert unary1.stable_id == unary2.stable_id

    # ============ CompareExpr Tests ============

    def test_compare_eq(self):
        """a == b → CompareExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a == b")
        compare_node = tree.body[0].value
        expr_id = visitor.visit_Compare(compare_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        cmp_expr = next(e for e in exprs if e.kind == ExpressionKind.COMPARE)
        assert cmp_expr.payload["ops"] == ["=="]
        assert cmp_expr.payload["left"] is not None
        assert len(cmp_expr.payload["comparators"]) == 1

    def test_compare_chain(self):
        """a < b < c → CompareExpr with two comparators"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a < b < c")
        compare_node = tree.body[0].value
        expr_id = visitor.visit_Compare(compare_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        cmp_expr = next(e for e in exprs if e.kind == ExpressionKind.COMPARE)
        assert cmp_expr.payload["ops"] == ["<", "<"]
        assert len(cmp_expr.payload["comparators"]) == 2

    def test_compare_all_ops(self):
        """Test all comparison operators"""
        operators = [
            ("==", ast.Eq),
            ("!=", ast.NotEq),
            ("<", ast.Lt),
            ("<=", ast.LtE),
            (">", ast.Gt),
            (">=", ast.GtE),
            ("is", ast.Is),
            ("is not", ast.IsNot),
            ("in", ast.In),
            ("not in", ast.NotIn),
        ]

        for op_str, op_cls in operators:
            context = IRContext(config=IRConfig())
            context.current_module_id = 1
            context.current_module_name = "test"

            visitor = Visitor(context)

            tree = ast.parse(f"a {op_str} b")
            compare_node = tree.body[0].value
            expr_id = visitor.visit_Compare(compare_node)

            assert expr_id is not None

            exprs = context.expressions.all()
            cmp_expr = next(e for e in exprs if e.kind == ExpressionKind.COMPARE)
            assert cmp_expr.payload["ops"] == [op_str], f"Operator {op_str} failed"

    def test_compare_parent_child(self):
        """CompareExpr parent-child relationship"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a < b")
        compare_node = tree.body[0].value
        expr_id = visitor.visit_Compare(compare_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        cmp_expr = next(e for e in exprs if e.kind == ExpressionKind.COMPARE)

        # Verify left
        left_id = cmp_expr.payload["left"]
        left = next(e for e in exprs if e.expr_id == left_id)
        assert left.kind == ExpressionKind.NAME
        assert left.payload["id"] == "a"
        assert left.parent_expr == cmp_expr.expr_id
        assert left.ordinal == 0

        # Verify comparator
        comp_id = cmp_expr.payload["comparators"][0]
        comp = next(e for e in exprs if e.expr_id == comp_id)
        assert comp.kind == ExpressionKind.NAME
        assert comp.payload["id"] == "b"
        assert comp.parent_expr == cmp_expr.expr_id
        assert comp.ordinal == 1

    def test_compare_ordinal_on_failure(self):
        """CompareExpr ordinal does NOT advance on failure"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Set initial ordinal
        context.expression_ordinal = 5

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("(1, 2) < b")
        compare_node = tree.body[0].value
        expr_id = visitor.visit_Compare(compare_node)

        assert expr_id is None
        assert context.expression_ordinal == 5

    def test_compare_fail_closed(self):
        """CompareExpr should be fail-closed: no malformed Expression remains."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("(1, 2) < b")
        compare_node = tree.body[0].value
        expr_id = visitor.visit_Compare(compare_node)

        assert expr_id is None

        exprs = context.expressions.all()
        cmp_exprs = [e for e in exprs if e.kind == ExpressionKind.COMPARE]
        assert len(cmp_exprs) == 0

        errors = context.diagnostics.get_errors()
        # Either VISITOR-021 (left failed) and/or VISITOR-023 (incomplete comparison)
        assert any(e.code in ("VISITOR-021", "VISITOR-023") for e in errors)

    def test_compare_stable_id_deterministic(self):
        """Stable ID for CompareExpr should be deterministic"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree = ast.parse("a < b")
        compare_node = tree.body[0].value

        visitor1.visit_Compare(compare_node)
        visitor2.visit_Compare(compare_node)

        cmp1 = next(e for e in context1.expressions.all() if e.kind == ExpressionKind.COMPARE)
        cmp2 = next(e for e in context2.expressions.all() if e.kind == ExpressionKind.COMPARE)

        assert cmp1.stable_id == cmp2.stable_id

    def test_compare_malformed_structure(self):
        """Malformed Compare AST should be rejected"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Create malformed Compare node
        malformed = ast.Compare(
            left=ast.Name(id="a", ctx=ast.Load()),
            ops=[ast.Lt()],
            comparators=[],  # Empty comparators - malformed
            lineno=1,
            col_offset=0
        )

        expr_id = visitor.visit_Compare(malformed)

        assert expr_id is None
        errors = context.diagnostics.get_errors()
        assert any(e.code == "VISITOR-019" for e in errors)

    # ============ BoolExpr Tests ============

    def test_bool_and(self):
        """a and b → BoolExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a and b")
        bool_node = tree.body[0].value
        expr_id = visitor.visit_BoolOp(bool_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        bool_expr = next(e for e in exprs if e.kind == ExpressionKind.BOOL)
        assert bool_expr.payload["op"] == "and"
        assert len(bool_expr.payload["values"]) == 2

    def test_bool_or(self):
        """a or b → BoolExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a or b")
        bool_node = tree.body[0].value
        expr_id = visitor.visit_BoolOp(bool_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        bool_expr = next(e for e in exprs if e.kind == ExpressionKind.BOOL)
        assert bool_expr.payload["op"] == "or"
        assert len(bool_expr.payload["values"]) == 2

    def test_bool_chain(self):
        """a and b and c → BoolExpr with 3 values (not nested)"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a and b and c")
        bool_node = tree.body[0].value
        expr_id = visitor.visit_BoolOp(bool_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        bool_expr = next(e for e in exprs if e.kind == ExpressionKind.BOOL)
        assert bool_expr.payload["op"] == "and"
        assert len(bool_expr.payload["values"]) == 3

    def test_bool_parent_child(self):
        """BoolExpr parent-child relationship"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("a and b")
        bool_node = tree.body[0].value
        expr_id = visitor.visit_BoolOp(bool_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        bool_expr = next(e for e in exprs if e.kind == ExpressionKind.BOOL)

        # Verify values
        for i, value_id in enumerate(bool_expr.payload["values"]):
            value = next(e for e in exprs if e.expr_id == value_id)
            assert value.kind == ExpressionKind.NAME
            assert value.payload["id"] == ["a", "b"][i]
            assert value.parent_expr == bool_expr.expr_id
            assert value.ordinal == i

    def test_bool_ordinal_on_failure(self):
        """BoolExpr ordinal does NOT advance on failure"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Set initial ordinal
        context.expression_ordinal = 5

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("(1, 2) and b")
        bool_node = tree.body[0].value
        expr_id = visitor.visit_BoolOp(bool_node)

        assert expr_id is None
        assert context.expression_ordinal == 5

    def test_bool_fail_closed(self):
        """BoolExpr should be fail-closed: no malformed Expression remains."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        # Tuple is not supported in VS2 yet, causing failure
        tree = ast.parse("(1, 2) and b")
        bool_node = tree.body[0].value
        expr_id = visitor.visit_BoolOp(bool_node)

        assert expr_id is None

        exprs = context.expressions.all()
        bool_exprs = [e for e in exprs if e.kind == ExpressionKind.BOOL]
        assert len(bool_exprs) == 0

        errors = context.diagnostics.get_errors()
        # VISITOR-027: child failure, VISITOR-028: incomplete expression
        assert any(e.code in ("VISITOR-027", "VISITOR-028") for e in errors)

    def test_bool_stable_id_deterministic(self):
        """Stable ID for BoolExpr should be deterministic"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree = ast.parse("a and b")
        bool_node = tree.body[0].value

        visitor1.visit_BoolOp(bool_node)
        visitor2.visit_BoolOp(bool_node)

        bool1 = next(e for e in context1.expressions.all() if e.kind == ExpressionKind.BOOL)
        bool2 = next(e for e in context2.expressions.all() if e.kind == ExpressionKind.BOOL)

        assert bool1.stable_id == bool2.stable_id

    # ============ SliceExpr Tests ============

    def _get_slice_from_subscript(self, source: str) -> ast.Slice:
        """Helper to extract Slice node from subscript expression."""
        tree = ast.parse(source)
        return tree.body[0].value.slice

    def test_slice_empty(self):
        """[:] → SliceExpr with empty payload"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        slice_node = self._get_slice_from_subscript("x[:]")
        expr_id = visitor.visit_Slice(slice_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 1
        slice_expr = slice_exprs[0]
        assert slice_expr.payload == {}

    def test_slice_upper_only(self):
        """[:2] → SliceExpr with only upper (ordinal=1)"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        slice_node = self._get_slice_from_subscript("x[:2]")
        expr_id = visitor.visit_Slice(slice_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 1
        slice_expr = slice_exprs[0]

        assert "lower" not in slice_expr.payload
        assert "upper" in slice_expr.payload
        assert "step" not in slice_expr.payload

        upper_id = slice_expr.payload["upper"]
        upper_expr = next(e for e in exprs if e.expr_id == upper_id)
        assert upper_expr.kind == ExpressionKind.CONSTANT
        assert upper_expr.payload["value"] == 2
        assert upper_expr.parent_expr == slice_expr.expr_id
        assert upper_expr.ordinal == 1

    def test_slice_lower_only(self):
        """[1:] → SliceExpr with only lower (ordinal=0)"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        slice_node = self._get_slice_from_subscript("x[1:]")
        expr_id = visitor.visit_Slice(slice_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 1
        slice_expr = slice_exprs[0]

        assert "lower" in slice_expr.payload
        assert "upper" not in slice_expr.payload
        assert "step" not in slice_expr.payload

        lower_id = slice_expr.payload["lower"]
        lower_expr = next(e for e in exprs if e.expr_id == lower_id)
        assert lower_expr.kind == ExpressionKind.CONSTANT
        assert lower_expr.payload["value"] == 1
        assert lower_expr.parent_expr == slice_expr.expr_id
        assert lower_expr.ordinal == 0

    def test_slice_step_only(self):
        """[::2] → SliceExpr with only step (ordinal=2)"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        slice_node = self._get_slice_from_subscript("x[::2]")
        expr_id = visitor.visit_Slice(slice_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 1
        slice_expr = slice_exprs[0]

        assert "lower" not in slice_expr.payload
        assert "upper" not in slice_expr.payload
        assert "step" in slice_expr.payload

        step_id = slice_expr.payload["step"]
        step_expr = next(e for e in exprs if e.expr_id == step_id)
        assert step_expr.kind == ExpressionKind.CONSTANT
        assert step_expr.payload["value"] == 2
        assert step_expr.parent_expr == slice_expr.expr_id
        assert step_expr.ordinal == 2

    def test_slice_full(self):
        """[1:2:3] → SliceExpr with lower=0, upper=1, step=2"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        slice_node = self._get_slice_from_subscript("x[1:2:3]")
        expr_id = visitor.visit_Slice(slice_node)

        assert expr_id is not None
        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 1
        slice_expr = slice_exprs[0]

        assert "lower" in slice_expr.payload
        assert "upper" in slice_expr.payload
        assert "step" in slice_expr.payload

        lower_id = slice_expr.payload["lower"]
        upper_id = slice_expr.payload["upper"]
        step_id = slice_expr.payload["step"]

        lower_expr = next(e for e in exprs if e.expr_id == lower_id)
        upper_expr = next(e for e in exprs if e.expr_id == upper_id)
        step_expr = next(e for e in exprs if e.expr_id == step_id)

        assert lower_expr.kind == ExpressionKind.CONSTANT
        assert lower_expr.payload["value"] == 1
        assert lower_expr.ordinal == 0

        assert upper_expr.kind == ExpressionKind.CONSTANT
        assert upper_expr.payload["value"] == 2
        assert upper_expr.ordinal == 1

        assert step_expr.kind == ExpressionKind.CONSTANT
        assert step_expr.payload["value"] == 3
        assert step_expr.ordinal == 2

    def test_slice_stable_id_uniqueness(self):
        """Two different SliceExpr should have different stable IDs via Subscript location"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[1:2] + y[3:4]")
        subscript1 = tree.body[0].value.left
        subscript2 = tree.body[0].value.right

        visitor.visit_Subscript(subscript1)
        visitor.visit_Subscript(subscript2)

        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 2
        assert slice_exprs[0].stable_id != slice_exprs[1].stable_id

    def test_slice_stable_id_deterministic_from_subscript_location(self):
        """Same SliceExpr from same location → same stable ID"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree1 = ast.parse("x[1:2]")
        tree2 = ast.parse("x[1:2]")

        visitor1.visit_Subscript(tree1.body[0].value)
        visitor2.visit_Subscript(tree2.body[0].value)

        slice1 = next(e for e in context1.expressions.all() if e.kind == ExpressionKind.SLICE)
        slice2 = next(e for e in context2.expressions.all() if e.kind == ExpressionKind.SLICE)

        assert slice1.stable_id == slice2.stable_id

    def test_slice_fail_closed(self):
        """SliceExpr should be fail-closed: no malformed Expression remains."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[(1, 2):]")
        slice_node = tree.body[0].value.slice

        expr_id = visitor.visit_Slice(slice_node)

        assert expr_id is None
        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 0

        errors = context.diagnostics.get_errors()
        assert any(e.code == "VISITOR-036" for e in errors)

    # ============ SubscriptExpr Tests ============

    def test_subscript_load(self):
        """x[1] → SubscriptExpr with load context"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[1]")
        subscript_node = tree.body[0].value
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        sub_expr = next(e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT)
        assert sub_expr.payload["ctx"] == "load"
        assert sub_expr.payload["value"] is not None
        assert sub_expr.payload["slice"] is not None

    def test_subscript_store(self):
        """x[0] = 1 → SubscriptExpr with store context"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[0] = 1")
        subscript_node = tree.body[0].targets[0]
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        sub_expr = next(e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT)
        assert sub_expr.payload["ctx"] == "store"

    def test_subscript_del(self):
        """del x[0] → SubscriptExpr with del context"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("del x[0]")
        subscript_node = tree.body[0].targets[0]
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        sub_expr = next(e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT)
        assert sub_expr.payload["ctx"] == "del"

    def test_subscript_parent_child(self):
        """SubscriptExpr parent-child relationship"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[1]")
        subscript_node = tree.body[0].value
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        sub_expr = next(e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT)

        # Verify value
        value_id = sub_expr.payload["value"]
        value_expr = next(e for e in exprs if e.expr_id == value_id)
        assert value_expr.kind == ExpressionKind.NAME
        assert value_expr.payload["id"] == "x"
        assert value_expr.parent_expr == sub_expr.expr_id
        assert value_expr.ordinal == 0

        # Verify slice
        slice_id = sub_expr.payload["slice"]
        slice_expr = next(e for e in exprs if e.expr_id == slice_id)
        assert slice_expr.kind == ExpressionKind.CONSTANT
        assert slice_expr.payload["value"] == 1
        assert slice_expr.parent_expr == sub_expr.expr_id
        assert slice_expr.ordinal == 1

    def test_subscript_with_slice(self):
        """x[1:2] → SubscriptExpr with Slice child and location propagation"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[1:2]")
        subscript_node = tree.body[0].value
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        sub_expr = next(e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT)

        # Verify slice is SliceExpr with parent relationship
        slice_id = sub_expr.payload["slice"]
        slice_expr = next(e for e in exprs if e.expr_id == slice_id)
        assert slice_expr.kind == ExpressionKind.SLICE
        assert slice_expr.parent_expr == sub_expr.expr_id
        assert slice_expr.ordinal == 1

        # Verify Slice children
        lower_id = slice_expr.payload["lower"]
        upper_id = slice_expr.payload["upper"]
        lower_expr = next(e for e in exprs if e.expr_id == lower_id)
        upper_expr = next(e for e in exprs if e.expr_id == upper_id)

        assert lower_expr.payload["value"] == 1
        assert lower_expr.ordinal == 0
        assert lower_expr.parent_expr == slice_expr.expr_id

        assert upper_expr.payload["value"] == 2
        assert upper_expr.ordinal == 1
        assert upper_expr.parent_expr == slice_expr.expr_id

    def test_subscript_nested(self):
        """x[y[0]] → nested SubscriptExpr"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[y[0]]")
        subscript_node = tree.body[0].value
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is not None

        exprs = context.expressions.all()
        sub_expr = next(e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT)

        # Value should be NameExpr(x)
        value_id = sub_expr.payload["value"]
        value_expr = next(e for e in exprs if e.expr_id == value_id)
        assert value_expr.kind == ExpressionKind.NAME
        assert value_expr.payload["id"] == "x"

        # Slice should be another SubscriptExpr (y[0])
        slice_id = sub_expr.payload["slice"]
        slice_expr = next(e for e in exprs if e.expr_id == slice_id)
        assert slice_expr.kind == ExpressionKind.SUBSCRIPT
        assert slice_expr.parent_expr == sub_expr.expr_id
        assert slice_expr.ordinal == 1

        # Inner SubscriptExpr value should be NameExpr(y)
        inner_value_id = slice_expr.payload["value"]
        inner_value = next(e for e in exprs if e.expr_id == inner_value_id)
        assert inner_value.kind == ExpressionKind.NAME
        assert inner_value.payload["id"] == "y"

    def test_subscript_ordinal_on_failure(self):
        """SubscriptExpr ordinal does NOT advance on failure"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        context.expression_ordinal = 5

        # Malformed subscript (unsupported slice type)
        tree = ast.parse("x[(1, 2)]")
        subscript_node = tree.body[0].value
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is None
        assert context.expression_ordinal == 5

    def test_subscript_fail_closed(self):
        """SubscriptExpr should be fail-closed: no malformed Expression remains."""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        before_count = context.expressions.count()

        tree = ast.parse("x[(1, 2)]")
        subscript_node = tree.body[0].value
        expr_id = visitor.visit_Subscript(subscript_node)

        assert expr_id is None
        assert context.expressions.count() == before_count

        sub_exprs = [e for e in context.expressions.all() if e.kind == ExpressionKind.SUBSCRIPT]
        assert len(sub_exprs) == 0

        errors = context.diagnostics.get_errors()
        assert any(e.code in ("VISITOR-041", "VISITOR-042") for e in errors)

    def test_subscript_stable_id_deterministic(self):
        """Same SubscriptExpr from same location → same stable ID"""
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1
        context1.current_module_name = "test"

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1
        context2.current_module_name = "test"

        visitor1 = Visitor(context1)
        visitor2 = Visitor(context2)

        tree1 = ast.parse("x[1]")
        tree2 = ast.parse("x[1]")

        visitor1.visit_Subscript(tree1.body[0].value)
        visitor2.visit_Subscript(tree2.body[0].value)

        sub1 = next(e for e in context1.expressions.all() if e.kind == ExpressionKind.SUBSCRIPT)
        sub2 = next(e for e in context2.expressions.all() if e.kind == ExpressionKind.SUBSCRIPT)

        assert sub1.stable_id == sub2.stable_id

    def test_subscript_stable_id_uniqueness(self):
        """x[1] and y[1] at different locations → different stable IDs"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[1] + y[1]")
        subscript1 = tree.body[0].value.left
        subscript2 = tree.body[0].value.right

        visitor.visit_Subscript(subscript1)
        visitor.visit_Subscript(subscript2)

        exprs = context.expressions.all()
        sub_exprs = [e for e in exprs if e.kind == ExpressionKind.SUBSCRIPT]
        assert len(sub_exprs) == 2
        assert sub_exprs[0].stable_id != sub_exprs[1].stable_id

    def test_subscript_slice_location_propagation(self):
        """x[1:2] and y[1:2] → SliceExpr stable IDs different due to location"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1
        context.current_module_name = "test"

        visitor = Visitor(context)

        tree = ast.parse("x[1:2] + y[1:2]")
        subscript1 = tree.body[0].value.left
        subscript2 = tree.body[0].value.right

        visitor.visit_Subscript(subscript1)
        visitor.visit_Subscript(subscript2)

        exprs = context.expressions.all()
        slice_exprs = [e for e in exprs if e.kind == ExpressionKind.SLICE]
        assert len(slice_exprs) == 2
        assert slice_exprs[0].stable_id != slice_exprs[1].stable_id
