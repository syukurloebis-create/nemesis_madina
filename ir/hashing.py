# ir/hashing.py

import hashlib
from pathlib import Path
from typing import List, Tuple, Union, Optional
from enum import Enum

from .version import (
    SCHEMA_VERSION,
    CURRENT_VERSION,
    DEFAULT_HASH_ALGORITHM,
    HASHING_SCHEMA_VERSION,
)
from .models import (
    DeclarationKind, StatementKind, ExpressionKind, SymbolKind,
    BlockKind, BlockRole,
)


class NodeCategory(Enum):
    SYMBOL = "symbol"
    DECLARATION = "decl"
    STATEMENT = "stmt"
    EXPRESSION = "expr"
    BLOCK = "block"


def _stable_id_base(
    module_path: str,
    category: NodeCategory,
    kind: Union[DeclarationKind, StatementKind, ExpressionKind, SymbolKind, BlockKind],
    qualname: str,
    lineno: int,
    col_offset: int,
    schema_version: Optional[str] = None,
) -> str:
    """Base stable ID generator

    Spesifikasi final:
    - Separator: '|'
    - Urutan: schema_version | module_path | category.value | kind.value | qualname | lineno | col_offset
    - Encoding: UTF-8
    - Algoritma: SHA256
    - Output: hex digest (64 karakter)
    """
    if schema_version is None:
        schema_version = HASHING_SCHEMA_VERSION
    content = f"{schema_version}|{module_path}|{category.value}|{kind.value}|{qualname}|{lineno}|{col_offset}"
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def stable_block_id(
    module_path: str,
    kind: BlockKind,
    role: BlockRole,
    structural_slot: str,
    lineno: int,
    col_offset: int,
    schema_version: Optional[str] = None,
) -> str:
    """Generate stable ID for a Block entity.

    Inputs (deterministic):
    - module_path
    - BlockKind
    - BlockRole
    - structural_slot: e.g., "root", "body", "orelse", "handler:0"
    - lineno
    - col_offset
    - schema_version

    NOT used:
    - block_id
    - parent_block_id
    - ordinal
    - traversal order
    """
    if schema_version is None:
        schema_version = SCHEMA_VERSION
    
    identifier = f"block_{kind.value}_{role.value}_{structural_slot}"
    return _stable_id_base(
        module_path=module_path,
        category=NodeCategory.BLOCK,
        kind=kind,
        qualname=identifier,
        lineno=lineno,
        col_offset=col_offset,
        schema_version=schema_version,
    )


def stable_symbol_id(
    module_path: str,
    kind: SymbolKind,
    qualname: str,
    lineno: int,
    col_offset: int,
    schema_version: Optional[str] = None,
) -> str:
    return _stable_id_base(module_path, NodeCategory.SYMBOL, kind, qualname, lineno, col_offset, schema_version)


def stable_declaration_id(
    module_path: str,
    kind: DeclarationKind,
    qualname: str,
    lineno: int,
    col_offset: int,
    schema_version: Optional[str] = None,
) -> str:
    return _stable_id_base(module_path, NodeCategory.DECLARATION, kind, qualname, lineno, col_offset, schema_version)


def stable_statement_id(
    module_path: str,
    kind: StatementKind,
    qualname: str,
    lineno: int,
    col_offset: int,
    schema_version: Optional[str] = None,
) -> str:
    return _stable_id_base(module_path, NodeCategory.STATEMENT, kind, qualname, lineno, col_offset, schema_version)


def stable_expression_id(
    module_path: str,
    kind: ExpressionKind,
    identifier: str,
    lineno: int,
    col_offset: int,
    schema_version: str = HASHING_SCHEMA_VERSION,
) -> str:
    """Generate stable ID for expression nodes."""
    return _stable_id_base(
        module_path=module_path,
        category=NodeCategory.EXPRESSION,
        kind=kind,
        qualname=identifier,
        lineno=lineno,
        col_offset=col_offset,
        schema_version=schema_version,
    )


def file_hash(file_path: Path, algorithm: str = DEFAULT_HASH_ALGORITHM) -> str:
    """Generate file hash for source tracking"""
    hasher = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hasher.update(chunk)
    return f"{algorithm}:{hasher.hexdigest()}"


def source_hash(files: List[Tuple[str, str]], algorithm: str = DEFAULT_HASH_ALGORITHM) -> str:
    """Generate source hash from list of file hashes"""
    hasher = hashlib.new(algorithm)
    for file_path, file_hash in sorted(files):
        hasher.update(file_path.encode('utf-8'))
        hasher.update(file_hash.encode('utf-8'))
    return f"{algorithm}:{hasher.hexdigest()}"