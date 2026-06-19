# backend/repositories/tenant_aware.py
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

T = TypeVar('T')


class TenantAwareRepository(ABC, Generic[T]):
    """Base repository with mandatory tenant filtering"""
    
    def __init__(self, session: AsyncSession, tenant_id: str):
        self.session = session
        self.tenant_id = tenant_id
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID - MUST include tenant filter"""
        pass
    
    @abstractmethod
    async def list(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """List entities - MUST include tenant filter"""
        pass
    
    async def _add_tenant_filter(self, query: str) -> str:
        """Add tenant filter to query"""
        if "WHERE" in query.upper():
            return query + f" AND tenant_id = '{self.tenant_id}'"
        else:
            return query + f" WHERE tenant_id = '{self.tenant_id}'"
    
    async def _validate_tenant_access(self, table: str, entity_id: str) -> bool:
        """Validate that entity belongs to tenant"""
        query = text(f"""
            SELECT COUNT(*) FROM {table}
            WHERE id = :entity_id AND tenant_id = :tenant_id
        """)
        
        result = await self.session.execute(query, {
            "entity_id": entity_id,
            "tenant_id": self.tenant_id
        })
        
        count = result.scalar()
        return count > 0