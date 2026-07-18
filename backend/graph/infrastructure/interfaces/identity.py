"""
Graph Infrastructure - Identity Generator Interface
"""

from abc import ABC, abstractmethod
import uuid


class IdentityGenerator(ABC):
    """Identity Generator Interface."""
    
    @abstractmethod
    def generate_node_id(self) -> str:
        """Generate ID for a graph node."""
        pass
    
    @abstractmethod
    def generate_edge_id(self) -> str:
        """Generate ID for a graph edge."""
        pass


class UUIDIdentityGenerator(IdentityGenerator):
    """UUID-based identity generator."""
    
    def generate_node_id(self) -> str:
        return str(uuid.uuid4())
    
    def generate_edge_id(self) -> str:
        return str(uuid.uuid4())