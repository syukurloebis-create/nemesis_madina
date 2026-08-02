# ir/__init__.py

# Import version constants from version.py (single source of truth)
from .version import (
    CURRENT_VERSION,
    SCHEMA_VERSION,
    DEFAULT_HASH_ALGORITHM,
)

# Clean imports - no duplicates
from .config import IRConfig
from .context import IRContext
from .diagnostics import DiagnosticCollector
from .models import (
    Block,
    BlockKind,
    BlockRole,
    Declaration,
    DeclarationKind,
    Expression,
    ExpressionKind,
    Scope,
    ScopeKind,
    Statement,
    StatementKind,
    Symbol,
    SymbolKind,
    Visibility,
    SymbolOrigin,
)
from .repositories import (
    BlockRepository,
    DeclarationRepository,
    ExpressionRepository,
    LocationRepository,
    ModuleRepository,
    ScopeRepository,
    StatementRepository,
    SymbolRepository,
)
from .allocators import (
    BlockAllocator,
    DeclAllocator,
    ExprAllocator,
    LocationAllocator,
    ModuleAllocator,
    ScopeAllocator,
    StmtAllocator,
    SymbolAllocator,
)
from .hashing import (
    stable_block_id,
    stable_declaration_id,
    stable_expression_id,
    stable_statement_id,
    stable_symbol_id,
    file_hash,
    source_hash,
)
from .emitter import Emitter, UNRESOLVED_LOCATION_ID
from .visitor import Visitor
from .parser import Parser
from .serializer import Serializer  # ← Should work after alias added

# Use CURRENT_VERSION as single source of truth
__version__ = CURRENT_VERSION.ir