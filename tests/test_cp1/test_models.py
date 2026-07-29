from ir.models import Module, Scope, Symbol, Declaration
from ir.models import ScopeKind, DeclarationKind, SymbolKind, Visibility, SymbolOrigin


def test_module_model():
    module = Module(
        module_id=1,
        name="backend.api",
        file="backend/api.py",
        file_hash="sha256:abc123"
    )
    assert module.module_id == 1
    assert module.name == "backend.api"
    assert module.file == "backend/api.py"
    assert module.file_hash == "sha256:abc123"

def test_scope_model():
    scope = Scope(
        scope_id=1,
        kind=ScopeKind.CLASS,
        name="DashboardService",
        qualname="backend.services.dashboard.DashboardService",
        module_id=1,
        parent_scope=None,
        depth=1,
        location_id=1
    )
    assert scope.scope_id == 1
    assert scope.kind == ScopeKind.CLASS

def test_symbol_model():
    symbol = Symbol(
        symbol_id=1,
        stable_id="abc123",
        kind=SymbolKind.CLASS,
        name="DashboardService",
        qualname="backend.services.dashboard.DashboardService",
        module_id=1,
        scope_id=1,
        decl_id=1,
        visibility=Visibility.PUBLIC,
        is_abstract=False,
        is_protocol=False,
        is_async=False,
        is_dataclass=False,
        origin=SymbolOrigin.USER,
        location_id=1
    )
    assert symbol.symbol_id == 1
    assert symbol.kind == SymbolKind.CLASS
    assert symbol.visibility == Visibility.PUBLIC

def test_declaration_model():
    decl = Declaration(
        decl_id=1,
        stable_id="abc123",
        kind=DeclarationKind.CLASS,
        module_id=1,
        name="DashboardService",
        scope_id=1,
        symbol_id=1,
        block_id=None,
        location_id=1,
        bases=[1, 2],
        decorators=[]
    )
    assert decl.decl_id == 1
    assert decl.kind == DeclarationKind.CLASS
    assert decl.bases == [1, 2]