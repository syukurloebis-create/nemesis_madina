# scripts/inventory/query.py
from typing import List, Dict, Any, Optional
from scripts.inventory.storage.sqlite_storage import SQLiteStorage
from scripts.architecture.interfaces.i_inventory_query import IInventoryQuery

class InventoryQuery(IInventoryQuery):
    def __init__(self, storage: SQLiteStorage = None):
        self.storage = storage or SQLiteStorage()
    
    def get_aggregates(self) -> List[Dict[str, Any]]:
        """Get all aggregate classes"""
        return self.storage.query(
            "SELECT * FROM classes WHERE type = 'aggregate'"
        )
    
    def get_value_objects(self) -> List[Dict[str, Any]]:
        """Get all value object classes"""
        return self.storage.query(
            "SELECT * FROM classes WHERE type = 'value_object'"
        )
    
    def get_legacy_imports(self) -> List[Dict[str, Any]]:
        """Get all legacy imports"""
        return self.storage.query(
            "SELECT * FROM relations WHERE target LIKE 'backend.repositories.%'"
        )
    
    def find_circular_imports(self) -> List[Dict[str, Any]]:
        """Find circular imports using recursive CTE"""
        # This is a placeholder - full implementation in v9.x
        return []
    
    def get_modules_without_tests(self) -> List[Dict[str, Any]]:
        """Get modules with no tests"""
        # This is a placeholder - full implementation in v9.x
        return []
    
    def get_dependency_path(self, source: str, target: str) -> List[str]:
        """Find dependency path between modules"""
        # This is a placeholder - full implementation in v9.x
        return []
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """FTS5 search"""
        return self.storage.query(
            "SELECT * FROM modules_fts WHERE modules_fts MATCH ?",
            (query,)
        )
    
    def get_module_by_id(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get module by ID"""
        result = self.storage.query("SELECT * FROM modules WHERE id = ?", (module_id,))
        return result[0] if result else None
    
    def get_modules_by_type(self, module_type: str) -> List[Dict[str, Any]]:
        """Get modules by type"""
        return self.storage.query(
            "SELECT * FROM modules WHERE type = ?",
            (module_type,)
        )