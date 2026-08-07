# tests/integration/test_pipeline.py

import pytest

try:
    from scripts.inventory.service import InventoryService
except ImportError:
    pytest.skip("InventoryService module not available", allow_module_level=True)

from pathlib import Path
from scripts.scanner.core.scanner import Scanner
from scripts.scanner.core.plugin_manager import PluginManager
from scripts.scanner.plugins.python_plugin import PythonPlugin
from scripts.normalizer import Normalizer
from scripts.inventory.storage.sqlite_storage import SQLiteStorage
from scripts.rules.engine import RuleEngine
from scripts.inventory.query import InventoryQuery

class TestPipeline:
    def test_full_pipeline(self, tmp_path):
        # Setup
        plugin_manager = PluginManager()
        plugin_manager.register(PythonPlugin())
        scanner = Scanner(plugin_manager)
        
        # Create test files
        test_file = tmp_path / "test.py"
        test_file.write_text("""
import os
from fastapi import FastAPI

class TestClass:
    pass
""")
        
        # Scan
        results = scanner.scan_directory(tmp_path)
        
        # Normalize
        normalizer = Normalizer()
        normalized = normalizer.normalize_all(results)
        
        # Save to inventory
        storage = SQLiteStorage(str(tmp_path / "inventory.sqlite"))
        service = InventoryService(storage)
        
        for module in normalized['modules']:
            service.add_module(module)
        for relation in normalized['relations']:
            service.add_relation(relation)
        
        # Query
        query = InventoryQuery(storage)
        modules = query.get_modules()
        
        # Assert
        assert len(modules) > 0
        assert modules[0]['name'] == 'test'
        
        # Rules
        rules = [
            {
                'id': 'DOMAIN-001',
                'type': 'domain_purity',
                'severity': 'critical',
                'forbidden_imports': ['fastapi', 'sqlalchemy']
            }
        ]
        
        rule_engine = RuleEngine(query)
        rule_engine.load_rules(rules)
        violations = rule_engine.evaluate()
        
        # Assert violations found
        assert len(violations) > 0