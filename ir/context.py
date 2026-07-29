# ir/context.py

from dataclasses import dataclass, field
from typing import Optional
from .config import IRConfig
from .diagnostics import DiagnosticCollector

from .allocators import (
    ModuleAllocator, ScopeAllocator, SymbolAllocator,
    DeclAllocator, StmtAllocator, ExprAllocator,
    BlockAllocator, LocationAllocator
)
from .repositories import (
    ModuleRepository, ScopeRepository, SymbolRepository,
    DeclarationRepository, StatementRepository,
    ExpressionRepository, BlockRepository, LocationRepository
)


@dataclass
class IRContext:
    config: IRConfig
    module_alloc: ModuleAllocator = field(default_factory=ModuleAllocator)
    scope_alloc: ScopeAllocator = field(default_factory=ScopeAllocator)
    symbol_alloc: SymbolAllocator = field(default_factory=SymbolAllocator)
    decl_alloc: DeclAllocator = field(default_factory=DeclAllocator)
    stmt_alloc: StmtAllocator = field(default_factory=StmtAllocator)
    expr_alloc: ExprAllocator = field(default_factory=ExprAllocator)
    block_alloc: BlockAllocator = field(default_factory=BlockAllocator)
    loc_alloc: LocationAllocator = field(default_factory=LocationAllocator)
    diagnostics: DiagnosticCollector = field(default_factory=DiagnosticCollector)
    
    # Repositories
    modules: ModuleRepository = field(default_factory=ModuleRepository)
    scopes: ScopeRepository = field(default_factory=ScopeRepository)
    symbols: SymbolRepository = field(default_factory=SymbolRepository)
    declarations: DeclarationRepository = field(default_factory=DeclarationRepository)
    statements: StatementRepository = field(default_factory=StatementRepository)
    expressions: ExpressionRepository = field(default_factory=ExpressionRepository)
    blocks: BlockRepository = field(default_factory=BlockRepository)
    locations: LocationRepository = field(default_factory=LocationRepository)
    
    # State for visitor
    current_module_id: Optional[int] = None
    current_scope_id: Optional[int] = None
    current_block_id: Optional[int] = None
    statement_ordinal: int = 0
    expression_parent: Optional[int] = None
    scope_stack: list = field(default_factory=list)