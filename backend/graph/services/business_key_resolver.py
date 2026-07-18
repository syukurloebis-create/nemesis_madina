"""
Business Key Resolver - Domain Service

Resolves business keys to persistence IDs.
"""

from typing import Dict, List, Optional, Set
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.models import GraphEntity


class BusinessKeyResolver:
    """
    Resolves business keys to persistence IDs.
    
    Responsibilities:
    - Query database for entities by business_key
    - Return mapping: business_key → persistence_id
    - Handle missing keys gracefully
    
    Does NOT:
    - Create new entities
    - Validate business keys
    - Persist data
    """
    
    async def resolve(
        self,
        uow: IUnitOfWork,
        business_keys: List[str],
        entity_type: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Resolve business keys to persistence IDs.
        
        Args:
            uow: Unit of Work (provides session)
            business_keys: List of business keys to resolve
            entity_type: Optional filter by entity_type
            
        Returns:
            Dictionary mapping business_key → persistence_id
            
        Raises:
            ValueError: If any business key cannot be resolved
        """
        if not business_keys:
            return {}
        
        # Build query
        query = select(GraphEntity).where(
            GraphEntity.extra_data['business_key'].astext.in_(business_keys)
        )
        
        if entity_type:
            query = query.where(GraphEntity.entity_type == entity_type)
        
        result = await uow.session.execute(query)
        entities = result.scalars().all()
        
        # Build mapping
        mapping = {}
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if business_key:
                mapping[business_key] = entity.id
        
        # Check for missing keys
        missing = set(business_keys) - set(mapping.keys())
        if missing:
            raise ValueError(f"Business keys not found: {missing}")
        
        return mapping
    
    async def resolve_batch(
        self,
        uow: IUnitOfWork,
        business_keys_by_type: Dict[str, List[str]],
    ) -> Dict[str, Dict[str, str]]:
        """
        Resolve business keys grouped by entity_type.
        
        Args:
            uow: Unit of Work
            business_keys_by_type: {entity_type: [business_key1, business_key2, ...]}
            
        Returns:
            {entity_type: {business_key: persistence_id}}
        """
        result = {}
        for entity_type, keys in business_keys_by_type.items():
            result[entity_type] = await self.resolve(uow, keys, entity_type)
        return result