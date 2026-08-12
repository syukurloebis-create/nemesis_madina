"""
Authentication Dependencies for FastAPI

SEC-6 Phase 3
- AsyncSession only
- JWT sub = immutable User.id
- SecurityRole is the single authorization source
- No is_superuser
- No legacy UserRole
"""

from typing import Optional, Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.security.models import User
from backend.services.jwt_service import JWTService
from backend.domain.enums.permission import Permission
from backend.domain.enums.security_role import SecurityRole
from backend.domain.registry.role_permissions import has_permission as role_has_permission

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Resolve the authenticated user from the JWT.

    SEC-5:
        JWT sub = immutable User.id
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = JWTService.verify_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the authenticated active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return current_user


def require_roles(*allowed_roles: SecurityRole):
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        try:
            current_role = SecurityRole.from_legacy(current_user.role)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid security role"
            )

        if current_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(role.value for role in allowed_roles)}"
            )
        return current_user
    return role_checker


async def get_optional_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Optional[User]:
    """
    Return the authenticated active user when a valid token exists.

    Invalid/missing authentication returns None by contract.
    """
    if not token:
        return None

    try:
        payload = JWTService.verify_access_token(token)

        user_id = payload.get("sub")
        if not user_id:
            return None

        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            return None

        return user

    except Exception:
        return None


# ============================================================
# SEC-7 CANONICAL PERMISSION DEPENDENCIES
# ============================================================

from backend.domain.enums.permission import Permission
from backend.domain.registry.role_permissions import has_permission as role_has_permission


def require_permission(permission: Permission):
    """
    Canonical permission-based authorization dependency.

    Flow:
        JWT → get_current_active_user() → User.role
        → SecurityRole.from_legacy() → ROLE_PERMISSIONS
        → has_permission() → 403 / current_user

    SEC-7 Contract:
        - Uses canonical SecurityRole (not legacy Role)
        - Uses canonical ROLE_PERMISSIONS (not legacy RBAC)
        - Fail closed: invalid role → 403
        - No fallback to VIEWER for invalid roles
    """

    async def dependency(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        # 1. Resolve canonical role from User.role
        try:
            user_role = SecurityRole.from_legacy(current_user.role)
        except (TypeError, ValueError):
            # Fail closed: invalid role → 403
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid security role",
            )

        # 2. Check canonical role-permission registry
        if not role_has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value}",
            )

        return current_user

    return dependency


# ============================================================
# CONVENIENCE DEPENDENCIES
# ============================================================

require_admin = require_roles(
    SecurityRole.ADMIN,
)

require_investigator = require_roles(
    SecurityRole.ADMIN,
    SecurityRole.INVESTIGATOR,
)

require_analyst = require_roles(
    SecurityRole.ADMIN,
    SecurityRole.INVESTIGATOR,
    SecurityRole.ANALYST,
)
require_case_view = require_permission(Permission.CASE_VIEW)
require_intelligence_view = require_permission(Permission.INTELLIGENCE_VIEW)
require_admin_user_manage = require_permission(Permission.ADMIN_USER_MANAGE)

# Additional convenience dependencies for common permissions
require_case_create = require_permission(Permission.CASE_CREATE)
require_case_update = require_permission(Permission.CASE_UPDATE)
require_case_assign = require_permission(Permission.CASE_ASSIGN)
require_case_approve = require_permission(Permission.CASE_APPROVE)
require_case_close = require_permission(Permission.CASE_CLOSE)

require_evidence_view = require_permission(Permission.EVIDENCE_VIEW)
require_evidence_upload = require_permission(Permission.EVIDENCE_UPLOAD)
require_evidence_verify = require_permission(Permission.EVIDENCE_VERIFY)

require_entity_view = require_permission(Permission.ENTITY_VIEW)
require_entity_blacklist = require_permission(Permission.ENTITY_BLACKLIST)

require_finding_view = require_permission(Permission.FINDING_VIEW)
require_finding_approve = require_permission(Permission.FINDING_APPROVE)

require_report_view = require_permission(Permission.REPORT_VIEW)
require_report_export = require_permission(Permission.REPORT_EXPORT)

require_dashboard_executive = require_permission(Permission.DASHBOARD_EXECUTIVE)
require_dashboard_strategic = require_permission(Permission.DASHBOARD_STRATEGIC)
require_dashboard_operational = require_permission(Permission.DASHBOARD_OPERATIONAL)