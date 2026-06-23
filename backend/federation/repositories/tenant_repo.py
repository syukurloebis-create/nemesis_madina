"""Federation Tenant Repository"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
import json
import secrets

from federation.models import FederationTenant, InstitutionType


class TenantRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create_tenant(self, tenant: FederationTenant) -> FederationTenant:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO federation_tenants (
                    tenant_id, institution_name, institution_type, region, level,
                    api_key, is_active, quota_limit, quota_used, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
                tenant.tenant_id,
                tenant.institution_name,
                tenant.institution_type.value,
                tenant.region,
                tenant.level,
                tenant.api_key,
                tenant.is_active,
                tenant.quota_limit,
                tenant.quota_used,
                json.dumps(tenant.metadata)
            )
            return tenant
    
    async def get_tenant_by_api_key(self, api_key: str) -> Optional[FederationTenant]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM federation_tenants WHERE api_key = $1 AND is_active = true",
                api_key
            )
            if row:
                return self._row_to_tenant(row)
            return None
    
    async def update_quota(self, tenant_id: UUID, increment: int = 1) -> bool:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE federation_tenants 
                SET quota_used = quota_used + $2, updated_at = NOW()
                WHERE tenant_id = $1
            """, tenant_id, increment)
            return True
    
    def _row_to_tenant(self, row) -> FederationTenant:
        return FederationTenant(
            tenant_id=row['tenant_id'],
            institution_name=row['institution_name'],
            institution_type=row['institution_type'],
            region=row['region'],
            level=row['level'],
            api_key=row['api_key'],
            is_active=row['is_active'],
            quota_limit=row['quota_limit'],
            quota_used=row['quota_used'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            metadata=row['metadata'] or {}
        )
