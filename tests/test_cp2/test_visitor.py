# tests/test_cp2/test_visitor.py

import ast

from ir.context import IRContext
from ir.config import IRConfig
from ir.visitor import Visitor, UNRESOLVED_LOCATION_ID
from ir.models import (
    ScopeKind,
    DeclarationKind,
    SymbolKind,
    Visibility,
)


class TestVisitor:
    def test_visit_module_creates_scope(self):
        """Module AST → Module Scope"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context1 = IRContext(config=IRConfig())
        context1.current_module_id = 1

        context2 = IRContext(config=IRConfig())
        context2.current_module_id = 1

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
        context = IRContext(config=IRConfig())

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert scopes[1].qualname == "Foo"

        symbols = context.symbols.all()
        assert symbols[0].qualname == "Foo"

    def test_visit_class_updates_scope_stack(self):
        """ClassDef should update scope_stack"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

        visitor = Visitor(context)

        source = "class Foo: pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        assert len(context.scope_stack) == 2  # Module + Class
        assert context.scope_stack[-1] == context.current_scope_id

    def test_visit_class_no_traversal(self):
        """CP2.2B: Class visitor should NOT traverse body"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        scopes = context.scopes.all()
        assert scopes[1].qualname == "foo"

        symbols = context.symbols.all()
        assert symbols[0].qualname == "foo"

    def test_visit_function_updates_scope_stack(self):
        """FunctionDef should update scope_stack"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

        visitor = Visitor(context)

        source = "def foo(): pass"
        tree = ast.parse(source)
        visitor.visit(tree)

        assert len(context.scope_stack) == 2  # Module + Function
        assert context.scope_stack[-1] == context.current_scope_id

    def test_visit_function_no_traversal(self):
        """CP2.2C: Function visitor should NOT traverse body"""
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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
        context = IRContext(config=IRConfig())
        context.current_module_id = 1

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