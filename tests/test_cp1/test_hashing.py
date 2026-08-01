from ir.hashing import (
    stable_symbol_id, stable_declaration_id,
    stable_statement_id, stable_expression_id,
    file_hash, source_hash
)
from ir.models import DeclarationKind, SymbolKind, StatementKind, ExpressionKind
from ir import CURRENT_VERSION

# ============================================================================
# Regression Hashes - Frozen from actual implementation
# These values are the actual SHA-256 hashes produced by the current algorithm
# DO NOT change these unless the hashing algorithm is intentionally modified
# ============================================================================

EXPECTED_SYMBOL_ID = (
    "e1b6be92d5428c42528da6a0ca6535c07987c28550d69c8053d5e19f3a3738e0"
)

EXPECTED_DECL_ID = (
    "b26a5322d0fdcaed78f7c6db74d2c4f8d80f1cbaaec11d7eb249a5a146d728b3"
)

EXPECTED_STMT_ID = (
    "8d1a24f0e0b3e94bc38d94edcb3d6e7c3256e4085e6263519d846eace92da26e"
)

EXPECTED_EXPR_ID = (
    "4a3fffdcd8d4e5766f14f457980e9bad82bbb93673f5d463bd405c38beab82d4"
)

# Schema version should match CURRENT_VERSION.schema
assert CURRENT_VERSION.schema == "1.0.0"


def test_stable_symbol_id_consistent():
    id1 = stable_symbol_id(
        "backend.test",
        SymbolKind.CLASS,
        "TestClass",
        10,
        0
    )
    id2 = stable_symbol_id(
        "backend.test",
        SymbolKind.CLASS,
        "TestClass",
        10,
        0
    )
    assert id1 == id2


def test_stable_symbol_id_regression():
    """Ensure stable ID algorithm doesn't change unexpectedly"""
    actual = stable_symbol_id(
        "backend.test",
        SymbolKind.CLASS,
        "TestClass",
        10,
        0
    )
    assert actual == EXPECTED_SYMBOL_ID


def test_stable_declaration_id_regression():
    actual = stable_declaration_id(
        "backend.test",
        DeclarationKind.CLASS,
        "TestClass",
        10,
        0
    )
    assert actual == EXPECTED_DECL_ID


def test_stable_statement_id_regression():
    actual = stable_statement_id(
        "backend.test",
        StatementKind.ASSIGN,
        "x",
        10,
        0
    )
    assert actual == EXPECTED_STMT_ID


def test_stable_expression_id_regression():
    actual = stable_expression_id(
        "backend.test",
        ExpressionKind.NAME,
        "x",
        10,
        0
    )
    assert actual == EXPECTED_EXPR_ID


def test_stable_id_different_kind():
    id1 = stable_declaration_id(
        "backend.test",
        DeclarationKind.CLASS,
        "TestClass",
        10,
        0
    )
    id2 = stable_declaration_id(
        "backend.test",
        DeclarationKind.FUNCTION,
        "TestClass",
        10,
        0
    )
    assert id1 != id2


def test_stable_id_different_line():
    id1 = stable_declaration_id(
        "backend.test",
        DeclarationKind.CLASS,
        "TestClass",
        10,
        0
    )
    id2 = stable_declaration_id(
        "backend.test",
        DeclarationKind.CLASS,
        "TestClass",
        20,
        0
    )
    assert id1 != id2


def test_stable_id_schema_version():
    id1 = stable_expression_id(
        "backend.test",
        ExpressionKind.NAME,
        "x",
        10,
        0,
        schema_version="3.1"
    )
    id2 = stable_expression_id(
        "backend.test",
        ExpressionKind.NAME,
        "x",
        10,
        0,
        schema_version="3.2"
    )
    assert id1 != id2


def test_file_hash_deterministic(tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("print('hello')")

    hash1 = file_hash(test_file)
    hash2 = file_hash(test_file)
    assert hash1 == hash2


def test_source_hash_deterministic(tmp_path):
    f1 = tmp_path / "a.py"
    f2 = tmp_path / "b.py"
    f1.write_text("x=1")
    f2.write_text("y=2")

    files = [
        (str(f1), file_hash(f1)),
        (str(f2), file_hash(f2)),
    ]

    hash1 = source_hash(files)
    hash2 = source_hash(files)
    assert hash1 == hash2