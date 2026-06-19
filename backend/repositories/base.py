from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from uuid import UUID

T = TypeVar('T')

class TenantAwareRepository(ABC, Generic[T]):
    """Base repository with mandatory tenant filtering"""
    
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id
    
    @abstractmethod
    async def get_by_id(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID - MUST include tenant filter"""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List entities - MUST include tenant filter"""
        pass
    
    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> T:
        """Create entity - MUST set tenant_id"""
        pass
    
    def _add_tenant_filter(self, query: Any) -> Any:
        """Helper to add tenant filter to query"""
        return query.where(f"tenant_id = '{self.tenant_id}'")