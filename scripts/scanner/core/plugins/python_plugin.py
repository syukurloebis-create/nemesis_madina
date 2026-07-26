# scripts/scanner/plugins/python_plugin.py
import ast
from pathlib import Path
from typing import List, Dict, Any
from scripts.architecture.interfaces.i_scanner_plugin import IScannerPlugin

class PythonPlugin(IScannerPlugin):
    @property
    def name(self) -> str:
        return "python"
    
    @property
    def extensions(self) -> List[str]:
        return ['.py']
    
    def scan_file(self, filepath: Path) -> Dict[str, Any]:
        """Scan a Python file using AST"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        return {
            'id': str(filepath),
            'name': filepath.stem,
            'path': str(filepath),
            'type': self._detect_module_type(filepath),
            'language': 'python',
            'lines': len(content.splitlines()),
            'complexity': self._calculate_complexity(tree),
            'imports': self._get_imports(tree),
            'classes': self._get_classes(tree),
            'functions': self._get_functions(tree)
        }
    
    def _detect_module_type(self, filepath: Path) -> str:
        path_str = str(filepath)
        if 'domain' in path_str:
            return 'domain'
        elif 'application' in path_str:
            return 'application'
        elif 'infrastructure' in path_str:
            return 'infrastructure'
        elif 'api' in path_str:
            return 'api'
        elif 'tests' in path_str:
            return 'test'
        elif 'repositories' in path_str:
            return 'legacy'
        return 'unknown'
    
    def _get_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    
    def _get_classes(self, tree: ast.AST) -> List[str]:
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    
    def _get_functions(self, tree: ast.AST) -> List[str]:
        return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.And, ast.Or)):
                complexity += 1
        return complexity