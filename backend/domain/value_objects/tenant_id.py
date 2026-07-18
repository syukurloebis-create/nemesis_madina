"""
NEMESIS Madina - Tenant ID Value Object
"""

from backend.domain.value_objects.base_uuid import BaseUUID


class TenantId(BaseUUID):
    """Tenant ID - for multi-tenant isolation."""
    pass