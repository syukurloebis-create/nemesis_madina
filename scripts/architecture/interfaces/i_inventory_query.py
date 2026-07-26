# scripts/architecture/interfaces/i_inventory_query.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IInventoryQuery(ABC):
    """Interface for inventory queries"""
    
    @abstractmethod
    def get_aggregates(self) -> List[Dict[str, Any]]:
        """Get all aggregates"""
        pass
    
    @abstractmethod
    def get_value_objects(self) -> List[Dict[str, Any]]:
        """Get all value objects"""
        pass
    
    @abstractmethod
    def get_legacy_imports(self) -> List[Dict[str, Any]]:
        """Get all legacy imports"""
        pass
    
    @abstractmethod
    def find_circular_imports(self) -> List[Dict[str, Any]]:
        """Find circular imports"""
        pass
    
    @abstractmethod
    def get_modules_without_tests(self) -> List[Dict[str, Any]]:
        """Get modules with no tests"""
        pass
    
    @abstractmethod
    def get_dependency_path(self, source: str, target: str) -> List[str]:
        """Get dependency path between modules"""
        pass
    
    @abstractmethod
    def search(self, query: str) -> List[Dict[str, Any]]:
        """FTS5 search"""
        pass