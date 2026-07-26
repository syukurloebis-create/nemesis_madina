# scripts/architecture/interfaces/i_generator.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from scripts.architecture.interfaces.i_inventory_query import IInventoryQuery

class IGenerator(ABC):
    """Interface for generators"""
    
    @abstractmethod
    def generate(self, inventory: IInventoryQuery) -> None:
        """Generate artifact from inventory"""
        pass
    
    @abstractmethod
    def save(self) -> None:
        """Save generated artifact"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Generator name"""
        pass
    
    @property
    @abstractmethod
    def output_path(self) -> str:
        """Output file path"""
        pass