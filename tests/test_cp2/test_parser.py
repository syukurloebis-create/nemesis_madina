# tests/test_cp2/test_parser.py

import ast

from ir.parser import Parser


class TestParser:
    def test_parse_empty(self):
        parser = Parser()
        result = parser.parse("")
        assert result is not None
        assert isinstance(result, ast.Module)
        assert len(result.body) == 0

    def test_parse_comments_only(self):
        parser = Parser()
        result = parser.parse(
            "# comment\n"
            "# another comment\n"
        )
        assert result is not None
        assert len(result.body) == 0

    def test_parse_syntax_valid(self):
        parser = Parser()
        result = parser.parse("x = 1")
        assert result is not None
        assert len(result.body) == 1

    def test_parse_syntax_error(self):
        parser = Parser()
        result = parser.parse("x =")
        assert result is None
        errors = parser.get_diagnostics().get_errors()
        assert len(errors) > 0
        assert errors[0].code == "PARSER-001"

    def test_parse_utf8(self):
        parser = Parser()
        result = parser.parse("# -*- coding: utf-8 -*-\nx = '日本語'")
        assert result is not None

    def test_parse_multiline_string(self):
        parser = Parser()
        result = parser.parse('x = """multiline\nstring"""')
        assert result is not None

    def test_parse_async(self):
        parser = Parser()
        result = parser.parse("async def foo(): return 1")
        assert result is not None

    def test_parse_match_case(self):
        parser = Parser()
        result = parser.parse("match x:\n    case 1: pass")
        assert result is not None

    def test_parse_walrus(self):
        parser = Parser()
        result = parser.parse("if (x := 1): pass")
        assert result is not None

    def test_parse_decorators(self):
        parser = Parser()
        result = parser.parse("@decorator\ndef foo(): pass")
        assert result is not None

    def test_parse_type_annotations(self):
        parser = Parser()
        result = parser.parse("def foo(x: int) -> str: return str(x)")
        assert result is not None

    def test_parse_file_not_found(self, tmp_path):
        parser = Parser()
        result = parser.parse_file(tmp_path / "nonexistent.py")
        assert result is None
        errors = parser.get_diagnostics().get_errors()
        assert any(e.code == "PARSER-003" for e in errors)

    def test_parser_deterministic(self):
        parser1 = Parser()
        parser2 = Parser()
        source = "x = 1\ny = 2\nz = x + y"

        result1 = parser1.parse(source)
        result2 = parser2.parse(source)

        assert ast.dump(result1) == ast.dump(result2)

    def test_parser_no_semantic_analysis(self):
        """Parser should NOT perform semantic analysis."""
        parser = Parser()
        source = "x = 1"

        result = parser.parse(source)

        assert result is not None
        # No symbols, no binding, no resolution
        # Parser should not know or care about types