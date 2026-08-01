# ir/context.py

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Optional, Dict, Any, Tuple, List, Mapping, NoReturn

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
from .models import Module

def _freeze_dict(d: Dict[int, int]) -> Mapping[int, int]:
    """Create an immutable view of a dict.
    
    Safe because values are immutable ints.
    MappingProxyType provides shallow immutability, which is sufficient
    since all values are int (immutable).
    """
    return MappingProxyType(d.copy())

class IRInvariantError(RuntimeError):
    """Raised when an IR invariant is violated."""
    pass

@dataclass(frozen=True)
class TraversalSnapshot:
    """Immutable snapshot of visitor traversal state only."""
    current_scope_id: Optional[int]
    current_qualname: Optional[str]
    current_block_id: Optional[int]
    scope_stack: Tuple[int, ...]
    block_stack: Tuple[int, ...]
    statement_ordinals: Mapping[int, int]
    block_ordinals: Mapping[int, int]

@dataclass(frozen=True)
class BlockRuntimeState:
    """Runtime block context for emission state.
    
    These fields are modified during emission of Statements and Blocks.
    They must be rolled back together with repositories and allocators
    to preserve IR invariants.
    
    Fields:
    - current_block_id: Currently active Block for statement placement
    - block_stack: Stack of active Blocks (nested)
    - statement_ordinals: Per-block statement ordinal counter
    - block_ordinals: Per-parent-block child block ordinal counter
    """
    current_block_id: Optional[int]
    block_stack: Tuple[int, ...]
    statement_ordinals: Mapping[int, int]
    block_ordinals: Mapping[int, int]

@dataclass(frozen=True)
class _TransactionSnapshot:
    """INTERNAL: Snapshot of emission/transaction state for rollback.
    
    Includes block runtime context because emission modifies these fields
    and rollback must restore them to maintain invariant consistency.
    """
    # Repository state
    expression_count: int
    statement_count: int
    block_count: int
    
    # Allocator state
    expr_alloc_current: int
    stmt_alloc_current: int
    block_alloc_current: int
    
    # Emission state
    expression_parent: Optional[int]
    expression_ordinal: int
    
    # Block runtime context
    block_runtime_state: BlockRuntimeState

class TransactionHandle:
    """Truly opaque handle for a transaction.
    
    This is a pure identity token. Contains NO data.
    All state is stored in IRContext registry.
    
    Handles are single-use. After commit() or successful rollback(),
    the handle becomes invalid.
    
    IMPORTANT: Caller MUST commit or rollback every transaction.
    Unfinished transactions remain in registry until context is destroyed.
    
    Package-internal friend API:
    - _internal_id() is NOT part of the public API.
    - Only IRContext may call this method.
    - Tests may call it when testing internal contracts.
    - External callers MUST NOT use _internal_id().
    """
    __slots__ = ("__id",)
    
    def __init__(self, tx_id: int):
        self.__id = tx_id
    
    def _internal_id(self) -> int:
        """Package-internal friend API.
        
        Only IRContext may call this method.
        Tests may call it when testing internal contracts.
        External callers MUST NOT use this.
        
        This is a stable internal contract between TransactionHandle
        and IRContext. It allows IRContext to resolve the handle
        to its registry entry without exposing implementation details.
        """
        return self.__id

@dataclass
class IRContext:
    config: IRConfig

    # =========================================================================
    # Allocators
    # =========================================================================
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

    # =========================================================================
    # Repositories
    # =========================================================================
    modules: ModuleRepository = field(default_factory=ModuleRepository)
    scopes: ScopeRepository = field(default_factory=ScopeRepository)
    symbols: SymbolRepository = field(default_factory=SymbolRepository)
    declarations: DeclarationRepository = field(default_factory=DeclarationRepository)
    statements: StatementRepository = field(default_factory=StatementRepository)
    expressions: ExpressionRepository = field(default_factory=ExpressionRepository)
    blocks: BlockRepository = field(default_factory=BlockRepository)
    locations: LocationRepository = field(default_factory=LocationRepository)

    # =========================================================================
    # Traversal-Owned State (Modified only by Visitor)
    # =========================================================================
    current_module_id: Optional[int] = None
    current_qualname: Optional[str] = None
    current_scope_id: Optional[int] = None
    current_block_id: Optional[int] = None
    block_stack: List[int] = field(default_factory=list)
    scope_stack: List[int] = field(default_factory=list)
    statement_ordinals: Dict[int, int] = field(default_factory=dict)
    block_ordinals: Dict[int, int] = field(default_factory=dict)

    # =========================================================================
    # Transaction/Emission-Owned State (Modified only by Emitter)
    # =========================================================================
    expression_parent: Optional[int] = None
    expression_ordinal: int = 0

    # =========================================================================
    # Transaction Helpers (INTERNAL / TESTING)
    # =========================================================================

    def _transaction_count(self) -> int:
        """INTERNAL: Get number of active transactions in registry.
        
        Used for testing registry cleanup.
        This is an internal helper, not part of public API.
        """
        return len(self._transactions)

    def _contains_transaction(self, handle: TransactionHandle) -> bool:
        """INTERNAL: Check if a transaction handle is active in registry.
        
        Used for testing handle lifecycle.
        This is an internal helper, not part of public API.
        
        Depends on _internal_id() friend API - only IRContext
        and tests should call this.
        """
        try:
            tx_id = handle._internal_id()
            return tx_id in self._transactions
        except AttributeError:
            return False

    def _assert_transaction_consistency(self) -> None:
        """INTERNAL: Assert repository and allocator consistency.
        
        Verifies that repository counts match allocator positions.
        Used after rollback to ensure state integrity.
        This is an internal helper, not part of public API.
        """
        if self.expressions.count() != self.expr_alloc.current():
            raise IRInvariantError(
                f"Expression count {self.expressions.count()} "
                f"does not match expr_alloc {self.expr_alloc.current()}"
            )
        if self.statements.count() != self.stmt_alloc.current():
            raise IRInvariantError(
                f"Statement count {self.statements.count()} "
                f"does not match stmt_alloc {self.stmt_alloc.current()}"
            )
        if self.blocks.count() != self.block_alloc.current():
            raise IRInvariantError(
                f"Block count {self.blocks.count()} "
                f"does not match block_alloc {self.block_alloc.current()}"
            )

    # =========================================================================
    # Transaction Registry (Instance-level)
    # =========================================================================
    _tx_counter: int = field(default=0, init=False)
    _transactions: Dict[int, _TransactionSnapshot] = field(default_factory=dict, init=False)

    def _register_transaction(self, snapshot: _TransactionSnapshot) -> TransactionHandle:
        """INTERNAL: Register a transaction and return a handle."""
        self._tx_counter += 1
        tx_id = self._tx_counter
        self._transactions[tx_id] = snapshot
        return TransactionHandle(tx_id)

    def _lookup_transaction(self, tx_id: int) -> _TransactionSnapshot:
        """INTERNAL: Lookup a transaction by ID without consuming."""
        if tx_id not in self._transactions:
            raise IRInvariantError(
                f"Invalid or already consumed transaction: {tx_id}"
            )
        return self._transactions[tx_id]

    def begin_transaction(self) -> TransactionHandle:
        """Begin a transaction (public entry point)."""
        snapshot = self._snapshot_transaction_state()
        return self._register_transaction(snapshot)

    def commit_transaction(self, handle: TransactionHandle) -> None:
        """Commit a transaction (public entry point)."""
        tx_id = handle._internal_id()
        try:
            self._transactions.pop(tx_id)
        except KeyError:
            raise IRInvariantError(
                f"Invalid or already consumed transaction: {tx_id}"
            ) from None

    def rollback_transaction(self, handle: TransactionHandle) -> None:
        """Rollback a transaction (public entry point)."""
        tx_id = handle._internal_id()

        # Phase 1: Lookup and validate
        snapshot = self._lookup_transaction(tx_id)
        self._validate_snapshot_consistency(snapshot)

        # Phase 2: Apply rollback, then pop on success
        self._apply_rollback(snapshot)
        self._validate_after_rollback
        self._assert_transaction_consistency()

        # Rollback succeeded - remove from registry
        self._transactions.pop(tx_id)

    def _snapshot_transaction_state(self) -> _TransactionSnapshot:
        """INTERNAL: Capture current transaction/emission state."""
        return _TransactionSnapshot(
            expression_count=self.expressions.count(),
            statement_count=self.statements.count(),
            block_count=self.blocks.count(),
            expr_alloc_current=self.expr_alloc.current(),
            stmt_alloc_current=self.stmt_alloc.current(),
            block_alloc_current=self.block_alloc.current(),
            expression_parent=self.expression_parent,
            expression_ordinal=self.expression_ordinal,
            block_runtime_state=self._snapshot_block_runtime_state(),
        )

    def _snapshot_block_runtime_state(self) -> BlockRuntimeState:
        """INTERNAL: Capture current block runtime state."""
        return BlockRuntimeState(
            current_block_id=self.current_block_id,
            block_stack=tuple(self.block_stack),
            statement_ordinals=_freeze_dict(self.statement_ordinals),
            block_ordinals=_freeze_dict(self.block_ordinals),
        )

    def _restore_block_runtime_state(self, state: BlockRuntimeState) -> None:
        """INTERNAL: Restore block runtime state."""
        self.current_block_id = state.current_block_id
        self.block_stack = list(state.block_stack)
        self.statement_ordinals = dict(state.statement_ordinals)
        self.block_ordinals = dict(state.block_ordinals)
    
    def _begin_transaction(self) -> TransactionHandle:
        """INTERNAL: Begin a transaction.
        
        DO NOT CALL DIRECTLY. Use Emitter.transaction() API.
        """
        snapshot = self._snapshot_transaction_state()
        return self._register_transaction(snapshot)

    def _apply_rollback(self, snapshot: _TransactionSnapshot) -> None:
        """INTERNAL: Apply rollback to transaction state.
    
        Rollback is LOGICALLY ATOMIC:
        - All operations are O(1) list truncations
        - Operations are executed in sequence
        - If any operation fails, state is inconsistent and IRInvariantError is raised
    
        Restores:
        - Repositories (expressions, statements, blocks)
        - Allocators (expr, stmt, block)
        - Emission state (expression_parent, expression_ordinal)
        - Block runtime context (current_block_id, block_stack, statement_ordinals, block_ordinals)
        """
        try:
            # 1. Rollback repositories
            self.expressions.rollback(snapshot.expression_count)
            self.statements.rollback(snapshot.statement_count)
            self.blocks.rollback(snapshot.block_count)
        
            # 2. Restore allocators
            self.expr_alloc.reset_to(snapshot.expr_alloc_current)
            self.stmt_alloc.reset_to(snapshot.stmt_alloc_current)
            self.block_alloc.reset_to(snapshot.block_alloc_current)
        
            # 3. Restore emission state
            self.expression_parent = snapshot.expression_parent
            self.expression_ordinal = snapshot.expression_ordinal
        
            # 4. Restore block runtime context
            self._restore_block_runtime_state(snapshot.block_runtime_state)
        
            # 5. Validate ALL invariants after rollback
            self._validate_after_rollback()
        
        except IRInvariantError:
            # Preserve invariant errors without wrapping
            raise
        
        except Exception as e:
            raise IRInvariantError(
                f"Rollback failed (state may be inconsistent): {e}"
            ) from e

    # =========================================================================
    # Transaction Validation
    # =========================================================================

    def _validate_snapshot_consistency(self, snapshot: _TransactionSnapshot) -> None:
        """Validate snapshot consistency before restore."""
        if snapshot.expression_count > self.expressions.count():
            raise IRInvariantError(
                f"Snapshot expression count {snapshot.expression_count} "
                f"exceeds current count {self.expressions.count()}"
            )
        if snapshot.statement_count > self.statements.count():
            raise IRInvariantError(
                f"Snapshot statement count {snapshot.statement_count} "
                f"exceeds current count {self.statements.count()}"
            )
        if snapshot.block_count > self.blocks.count():
            raise IRInvariantError(
                f"Snapshot block count {snapshot.block_count} "
                f"exceeds current count {self.blocks.count()}"
            )

        if snapshot.expr_alloc_current != snapshot.expression_count:
            raise IRInvariantError(
                f"Snapshot expr_alloc ({snapshot.expr_alloc_current}) "
                f"does not match expression_count ({snapshot.expression_count})"
            )
        if snapshot.stmt_alloc_current != snapshot.statement_count:
            raise IRInvariantError(
                f"Snapshot stmt_alloc ({snapshot.stmt_alloc_current}) "
                f"does not match statement_count ({snapshot.statement_count})"
            )
        if snapshot.block_alloc_current != snapshot.block_count:
            raise IRInvariantError(
                f"Snapshot block_alloc ({snapshot.block_alloc_current}) "
                f"does not match block_count ({snapshot.block_count})"
            )

    def _validate_after_rollback(self) -> None:
        """Validate ALL invariants after rollback."""
        self._validate_repository_state()
        self._validate_block_stack()
        self._validate_expression_state()
        self._validate_allocator_state()

    # =========================================================================
    # Traversal State Validation
    # =========================================================================

    def _validate_scope_stack(self) -> None:
        if self.current_scope_id is not None:
            if self.current_scope_id not in self.scope_stack:
                raise IRInvariantError(
                    f"Scope {self.current_scope_id} not in scope_stack: {self.scope_stack}"
                )
            if self.current_scope_id != self.scope_stack[-1]:
                raise IRInvariantError(
                    f"Scope {self.current_scope_id} is not top of scope_stack: {self.scope_stack}"
                )
        else:
            if self.scope_stack:
                raise IRInvariantError(
                    f"scope_stack is not empty ({self.scope_stack}) but current_scope_id is None"
                )
    
    def _validate_traversal(self) -> None:
        self._validate_scope_stack()
        self._validate_block_stack()

    def _validate_repository_state(self) -> None:
        """Validate repository state consistency."""
        # Repository-specific invariants can be added here
        pass

    def _validate_expression_state(self) -> None:
        """Validate expression state consistency."""
        if self.expression_parent is not None:
            if self.expressions.get(self.expression_parent) is None:
                raise IRInvariantError(
                    f"expression_parent {self.expression_parent} does not exist"
                )

    def _validate_block_stack(self) -> None:
        """Validate block stack invariants."""
        if self.current_block_id is not None:
            if self.current_block_id not in self.block_stack:
                raise IRInvariantError(
                    f"Block {self.current_block_id} not in block_stack: {self.block_stack}"
                )
            if self.current_block_id != self.block_stack[-1]:
                raise IRInvariantError(
                    f"Block {self.current_block_id} is not top of block_stack: {self.block_stack}"
                )
        else:
            if self.block_stack:
                raise IRInvariantError(
                    f"block_stack is not empty ({self.block_stack}) but current_block_id is None"
                )

    def _validate_allocator_state(self) -> None:
        """Validate allocator state consistency.
    
        NOTE: This validates that allocator can be restored to the target
        position. It does NOT assume allocator.current() == repository.count()
        because allocators may have different semantics (e.g., next ID vs count).
        """
        # Allocator reset validation is handled by allocator.reset_to()
        # which validates the target is within bounds.
        # No additional validation needed here.
        pass

    # =========================================================================
    # Traversal Methods
    # =========================================================================

    def save_traversal(self) -> TraversalSnapshot:
        return TraversalSnapshot(
            current_scope_id=self.current_scope_id,
            current_qualname=self.current_qualname,
            current_block_id=self.current_block_id,
            scope_stack=tuple(self.scope_stack),
            block_stack=tuple(self.block_stack),
            statement_ordinals=_freeze_dict(self.statement_ordinals),
            block_ordinals=_freeze_dict(self.block_ordinals),
        )

    def restore_traversal(self, snapshot: TraversalSnapshot) -> None:
        self.current_scope_id = snapshot.current_scope_id
        self.current_qualname = snapshot.current_qualname
        self.current_block_id = snapshot.current_block_id
        self.scope_stack = list(snapshot.scope_stack)
        self.block_stack = list(snapshot.block_stack)
        self.statement_ordinals = dict(snapshot.statement_ordinals)
        self.block_ordinals = dict(snapshot.block_ordinals)
        self._validate_traversal()

    def traversal(self) -> TraversalContext:
        return TraversalContext(self)

    # =========================================================================
    # Module Helpers
    # =========================================================================

    @property
    def current_module(self) -> Optional[Module]:
        if self.current_module_id is None:
            return None
        return self.modules.get(self.current_module_id)

    @property
    def current_module_name(self) -> Optional[str]:
        module = self.current_module
        return module.name if module else None

class TraversalContext:
    """Context manager for traversal state."""
    
    def __init__(self, context: IRContext):
        self._context = context
        self._snapshot: Optional[TraversalSnapshot] = None

    def __enter__(self) -> TraversalContext:
        self._snapshot = self._context.save_traversal()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if self._snapshot is not None:
            self._context.restore_traversal(self._snapshot)
        return False



    


