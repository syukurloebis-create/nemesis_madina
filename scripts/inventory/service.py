# scripts/inventory/service.py
from typing import List, Dict, Any, Optional
from scripts.architecture.models.module import Module
from scripts.architecture.models.relation import Relation
from scripts.inventory.storage.sqlite_storage import SQLiteStorage
from scripts.architecture.logging.logger import NemesisLogger

class InventoryService:
    def __init__(self, storage: SQLiteStorage = None):
        self.storage = storage or SQLiteStorage()
        self.logger = NemesisLogger()
    
    def add_module(self, module: Module) -> None:
        """Add a module to inventory"""
        self.storage.save_module(module)
        self.logger.debug(f"Added module: {module.name}")
    
    def add_relation(self, relation: Relation) -> None:
        """Add a relation to inventory"""
        self.storage.save_relation(relation)
        self.logger.debug(f"Added relation: {relation.source} -> {relation.target}")
    
    def get_modules(self, type: str = None, language: str = None) -> List[Dict[str, Any]]:
        """Get modules with optional filters"""
        filters = {}
        if type:
            filters['type'] = type
        if language:
            filters['language'] = language
        return self.storage.get_modules(filters if filters else None)
    
    def get_relations(self, source: str = None, target: str = None) -> List[Dict[str, Any]]:
        """Get relations with optional filters"""
        filters = {}
        if source:
            filters['source'] = source
        if target:
            filters['target'] = target
        return self.storage.get_relations(filters if filters else None)
    
    def get_legacy_imports(self) -> List[Dict[str, Any]]:
        """Get all legacy repository imports"""
        return self.storage.query(
            "SELECT * FROM relations WHERE target LIKE 'backend.repositories.%'"
        )
    
    def get_module_count(self) -> int:
        """Get total module count"""
        result = self.storage.query("SELECT COUNT(*) as count FROM modules")
        return result[0]['count'] if result else 0
    
    def clear(self) -> None:
        """Clear all data (for rebuilding)"""
        with sqlite3.connect(self.storage.db_path) as conn:
            conn.execute("DELETE FROM modules")
            conn.execute("DELETE FROM relations")
            conn.execute("DELETE FROM classes")
            conn.execute("DELETE FROM functions")
            conn.commit()
        self.logger.info("Inventory cleared")