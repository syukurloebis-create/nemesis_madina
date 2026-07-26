# scripts/architecture/registries/engine.py
import yaml
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class IRegistry(ABC):
    """Base interface for all registries"""
    
    @abstractmethod
    def get(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def list(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List entities with optional filters"""
        pass
    
    @abstractmethod
    def find_by_module(self, module_path: str) -> List[Dict[str, Any]]:
        """Find entities referencing a module"""
        pass
    
    @abstractmethod
    def validate(self, entity: Dict[str, Any]) -> List[str]:
        """Validate entity schema"""
        pass

class RegistryProvider(ABC):
    """Abstract registry provider (YAML, JSON, DB, etc.)"""
    
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Load registry data"""
        pass
    
    @abstractmethod
    def save(self, data: Dict[str, Any]) -> None:
        """Save registry data"""
        pass
    
    @abstractmethod
    def refresh(self) -> None:
        """Refresh registry data"""
        pass

class YamlRegistryProvider(RegistryProvider):
    """YAML file provider"""
    def __init__(self, path: str):
        self.path = path
    
    def load(self) -> Dict[str, Any]:
        with open(self.path) as f:
            return yaml.safe_load(f)
    
    def save(self, data: Dict[str, Any]) -> None:
        with open(self.path, 'w') as f:
            yaml.dump(data, f)
    
    def refresh(self) -> None:
        # Reload from file
        pass

class DatabaseRegistryProvider(RegistryProvider):
    """Database provider (future)"""
    def __init__(self, connection: Any):
        self.conn = connection
    
    def load(self) -> Dict[str, Any]:
        # Load from database
        pass
    
    def save(self, data: Dict[str, Any]) -> None:
        # Save to database
        pass
    
    def refresh(self) -> None:
        # Refresh from database
        pass

class CapabilityRegistry(IRegistry):
    """Capability registry implementation"""
    
    def __init__(self, provider: RegistryProvider):
        self.provider = provider
        self._cache = None
        self._load()
    
    def _load(self):
        data = self.provider.load()
        self._cache = data.get('capabilities', {})
    
    def get(self, capability_id: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(capability_id)
    
    def list(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        result = list(self._cache.values())
        if filters:
            for key, value in filters.items():
                result = [r for r in result if r.get(key) == value]
        return result
    
    def find_by_module(self, module_path: str) -> List[Dict[str, Any]]:
        result = []
        for capability in self._cache.values():
            if module_path in capability.get('modules', []):
                result.append(capability)
        return result
    
    def validate(self, entity: Dict[str, Any]) -> List[str]:
        errors = []
        required = ['id', 'name', 'owner', 'maturity']
        for field in required:
            if field not in entity:
                errors.append(f"Missing required field: {field}")
        return errors
    
    def refresh(self):
        self.provider.refresh()
        self._load()