# ir/parser.py

import ast
from pathlib import Path
from typing import Optional

from .diagnostics import DiagnosticCollector


class Parser:
    """
    Python source code parser.

    Responsibilities:
    - Parse Python source code into AST using ast.parse
    - Capture syntax errors as diagnostics
    - Does NOT perform semantic analysis
    - Does NOT emit IR
    - Does NOT allocate IDs

    Contract:
    - SyntaxError → recorded in DiagnosticCollector, returns None
    - No ParseError exception
    - Deterministic: same source → same AST
    """

    def __init__(self, diagnostics: Optional[DiagnosticCollector] = None):
        self._diagnostics = diagnostics or DiagnosticCollector()

    def parse(self, source: str, filename: str = "<memory>") -> Optional[ast.Module]:
        """
        Parse Python source code into AST.

        Args:
            source: Python source code as string
            filename: Source filename (for error reporting)

        Returns:
            ast.Module if parsing succeeds, None if syntax error
        """
        try:
            return ast.parse(source, filename=filename)
        except SyntaxError as e:
            self._diagnostics.add_error(
                code="PARSER-001",
                message=f"Syntax error: {e}",
                location_id=None,
                module_id=None
            )
            return None

    def parse_file(self, path: Path) -> Optional[ast.Module]:
        """
        Parse Python file into AST.

        Args:
            path: Path to Python file

        Returns:
            ast.Module if parsing succeeds, None if syntax error
        """
        try:
            source = path.read_text(encoding='utf-8')
            return self.parse(source, filename=str(path))
        except UnicodeDecodeError as e:
            self._diagnostics.add_error(
                code="PARSER-002",
                message=f"Unicode decode error: {e}",
                location_id=None,
                module_id=None
            )
            return None
        except FileNotFoundError as e:
            self._diagnostics.add_error(
                code="PARSER-003",
                message=f"File not found: {e}",
                location_id=None,
                module_id=None
            )
            return None

    def get_diagnostics(self) -> DiagnosticCollector:
        """Return the diagnostic collector."""
        return self._diagnostics