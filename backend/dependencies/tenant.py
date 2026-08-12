"""
Tenant Context Resolver - SEC-7.6 Phase 7B

Provides canonical tenant context for authenticated requests.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status

from backend.security.models import User
from backend.dependencies.auth import get_current_active_user


async def get_current_tenant(
    current_user: User = Depends(get_current_active_user),
) -> UUID:
    """
    Canonical tenant dependency.

    Resolves tenant_id from the authenticated user.

    SEC-7.6 Contract:
        - tenant_id = User.tenant_id
        - Missing tenant → HTTP 403
        - Invalid tenant → HTTP 403
        - tenant_id is canonical (NOT institution_id)
        - X-Tenant-ID is NOT authoritative
    """
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant context",
        )

    return current_user.tenant_id