# ir/context.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import IRConfig
from .diagnostics import DiagnosticCollector

from .allocators import (
    ModuleAllocator,
    ScopeAllocator,
    SymbolAllocator,
    DeclAllocator,
    StmtAllocator,
    ExprAllocator,
    BlockAllocator,
    LocationAllocator,
)

from .repositories import (
    ModuleRepository,
    ScopeRepository,
    SymbolRepository,
    DeclarationRepository,
    StatementRepository,
    ExpressionRepository,
    BlockRepository,
    LocationRepository,
)


@dataclass
class IRContext:
    config: IRConfig

    # Allocators
    module_alloc: ModuleAllocator = field(default_factory=ModuleAllocator)
    scope_alloc: ScopeAllocator = field(default_factory=ScopeAllocator)
    symbol_alloc: SymbolAllocator = field(default_factory=SymbolAllocator)
    decl_alloc: DeclAllocator = field(default_factory=DeclAllocator)
    stmt_alloc: StmtAllocator = field(default_factory=StmtAllocator)
    expr_alloc: ExprAllocator = field(default_factory=ExprAllocator)
    block_alloc: BlockAllocator = field(default_factory=BlockAllocator)
    loc_alloc: LocationAllocator = field(default_factory=LocationAllocator)

    # Diagnostics
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
    current_module_name: Optional[str] = None  # NEW
    current_scope_id: Optional[int] = None
    current_block_id: Optional[int] = None

    # Statement ordinals per scope
    statement_ordinals: Dict[int, int] = field(default_factory=dict)

    # Expression state
    expression_parent: Optional[int] = None
    expression_ordinal: int = 0

    # Scope stack
    scope_stack: List[int] = field(default_factory=list)


    def snapshot(self) -> dict:
        """Create a snapshot of the current state for rollback."""
        return {
            "expression_count": self.expressions.count(),
            "expression_parent": self.expression_parent,
            "expression_ordinal": self.expression_ordinal,
            "expr_alloc_current": self.expr_alloc.current(),
        }

    def restore(self, snapshot: dict) -> None:
        """Restore state from a valid rollback snapshot."""
        current_count = self.expressions.count()
        target_count = snapshot["expression_count"]

        if target_count < 0:
            raise ValueError(f"Invalid snapshot expression count: {target_count}")

        if target_count > current_count:
            raise ValueError(
                f"Snapshot expression count {target_count} "
                f"exceeds current count {current_count}"
            )

        if current_count > target_count:
            self.expressions.rollback(target_count)

        self.expression_parent = snapshot["expression_parent"]
        self.expression_ordinal = snapshot["expression_ordinal"]
        self.expr_alloc.reset_to(snapshot["expr_alloc_current"])
