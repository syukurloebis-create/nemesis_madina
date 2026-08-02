from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

# ============================================================================
# Enums (semua Enum, bukan StrEnum)
# ============================================================================

class DeclarationKind(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    PARAMETER = "parameter"
    IMPORT = "import"
    IMPORT_FROM = "import_from"

class ScopeKind(Enum):
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    COMPREHENSION = "comprehension"
    LAMBDA = "lambda"
    BLOCK = "block"

class StatementKind(Enum):
    ASSIGN = "assign"
    ANNOTATED_ASSIGN = "annotated_assign"
    AUGMENTED_ASSIGN = "augmented_assign"
    IMPORT = "import"
    IMPORT_FROM = "import_from"
    RETURN = "return"
    IF = "if"
    FOR = "for"
    WHILE = "while"
    TRY = "try"
    WITH = "with"
    MATCH = "match"
    EXPR = "expr"
    PASS = "pass"
    BREAK = "break"
    CONTINUE = "continue"
    RAISE = "raise"
    ASSERT = "assert"
    DELETE = "delete"

class ExpressionKind(Enum):
    NAME = "name"
    ATTRIBUTE = "attribute"
    CALL = "call"
    CONSTANT = "constant"
    BINARY = "binary"
    UNARY = "unary"
    COMPARE = "compare"
    BOOL = "bool"
    IF = "if"
    SUBSCRIPT = "subscript"
    SLICE = "slice"
    CONTAINER = "container"
    LAMBDA = "lambda"
    COMPREHENSION = "comprehension"
    AWAIT = "await"
    YIELD = "yield"
    NAMED = "named"
    STARRED = "starred"
    FSTRING = "fstring"
    FORMATTED_VALUE = "formatted_value"

class SymbolKind(Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    PARAMETER = "parameter"
    IMPORT = "import"
    MODULE = "module"

class Visibility(Enum):
    PUBLIC = "public"
    PROTECTED = "protected"
    PRIVATE = "private"

class SymbolOrigin(Enum):
    USER = "user"
    BUILTIN = "builtin"
    LIBRARY = "library"
    GENERATED = "generated"

class BlockKind(Enum):
    MODULE = "module"
    FUNCTION = "function"
    LOOP = "loop"
    IF = "if"
    TRY = "try"
    WITH = "with"

class BlockRole(Enum):
    ROOT = "root"
    BODY = "body"
    ORELSE = "orelse"
    HANDLER = "handler"
    FINALLY = "finally"

# ============================================================================
# Core Models (slots=True, kw_only=True)
# ============================================================================

@dataclass(slots=True, kw_only=True)
class Location:
    location_id: int
    module_id: int
    file: str
    line: int
    column: int
    end_line: int
    end_column: int

@dataclass(slots=True, kw_only=True)
class Module:
    module_id: int
    name: str
    file: str
    file_hash: str

@dataclass(slots=True, kw_only=True)
class Scope:
    scope_id: int
    kind: ScopeKind
    name: str
    qualname: str
    module_id: int
    parent_scope: Optional[int]
    depth: int
    location_id: int

@dataclass(slots=True, kw_only=True)
class Symbol:
    symbol_id: int
    stable_id: str
    kind: SymbolKind
    name: str
    qualname: str
    module_id: int
    scope_id: int
    decl_id: int
    visibility: Visibility
    is_abstract: bool
    is_protocol: bool
    is_async: bool
    is_dataclass: bool
    origin: SymbolOrigin
    location_id: int

@dataclass(slots=True, kw_only=True)
class Declaration:
    decl_id: int
    stable_id: str
    kind: DeclarationKind
    module_id: int
    name: str
    scope_id: int
    symbol_id: Optional[int]
    block_id: Optional[int]
    location_id: int
    bases: list[int] = field(default_factory=list)
    decorators: list[int] = field(default_factory=list)

@dataclass(slots=True, kw_only=True)
class Statement:
    stmt_id: int
    stable_id: str
    kind: StatementKind
    module_id: int
    scope_id: int
    ordinal: int
    block_id: Optional[int]
    location_id: int
    expr_id: Optional[int]
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True, kw_only=True)
class Expression:
    expr_id: int
    stable_id: str
    kind: ExpressionKind
    module_id: int
    parent_expr: Optional[int]
    ordinal: int
    location_id: int
    payload: Dict[str, Any] = field(default_factory=dict)

@dataclass(slots=True, kw_only=True)
class Block:
    block_id: int
    stable_id: str
    module_id: int
    scope_id: int
    kind: BlockKind
    role: BlockRole
    ordinal: int
    parent_block_id: Optional[int]
    location_id: int