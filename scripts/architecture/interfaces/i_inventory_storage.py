# scripts/architecture/interfaces/i_inventory_storage.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from scripts.architecture.models.module import Module
from scripts.architecture.models.relation import Relation

class IInventoryStorage(ABC):
    """Interface for inventory storage"""
    
    @abstractmethod
    def save_module(self, module: Module) -> None:
        """Save a module to inventory"""
        pass
    
    @abstractmethod
    def save_relation(self, relation: Relation) -> None:
        """Save a relation to inventory"""
        pass
    
    @abstractmethod
    def get_modules(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get modules matching filters"""
        pass
    
    @abstractmethod
    def get_relations(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get relations matching filters"""
        pass
    
    @abstractmethod
    def query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all data"""
        pass