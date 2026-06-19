# backend/security/service.py
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .rbac import get_rbac, Role, Permission, get_role_definition
from .permissions import get_permission_matrix, require_permission, require_any_permission
from .audit import get_audit_service, AuditAction, AuditMiddleware


class SecurityService:
    """Integrated security service"""
    
    def __init__(self):
        self.rbac = get_rbac()
        self.permission_matrix = get_permission_matrix()
        self.audit = get_audit_service()
    
    def assign_role(self, user_id: uuid.UUID, role: Role, assigned_by: uuid.UUID):
        """Assign role to user (with audit)"""
        self.rbac.assign_role(user_id, role)
        
        # TODO: Audit log
        # await self.audit.log(
        #     user_id=assigned_by,
        #     action=AuditAction.ROLE_ASSIGNED,
        #     resource_type="user",
        #     resource_id=str(user_id),
        #     details={"role": role.value}
        # )
    
    def revoke_role(self, user_id: uuid.UUID, role: Role, revoked_by: uuid.UUID):
        """Revoke role from user (with audit)"""
        self.rbac.revoke_role(user_id, role)
        
        # TODO: Audit log
    
    def get_user_permissions(self, user_id: uuid.UUID) -> List[str]:
        """Get all permissions for user"""
        permissions = self.rbac.get_user_permissions(user_id)
        return [p.value for p in permissions]
    
    def get_user_roles(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get all roles for user with details"""
        roles = self.rbac.get_user_roles(user_id)
        return [
            {
                "role": r.value,
                "display_name": get_role_definition(r).display_name if get_role_definition(r) else r.value,
                "permissions": [p.value for p in get_role_definition(r).get_all_permissions()] if get_role_definition(r) else []
            }
            for r in roles
        ]
    
    def can_access(self, user_id: uuid.UUID, permission: Permission) -> bool:
        """Check if user can access"""
        return self.rbac.has_permission(user_id, permission)
    
    def can_access_resource(self, user_id: uuid.UUID, resource: str, action: str) -> bool:
        """Check if user can access resource with specific action"""
        # Get user's roles
        roles = self.rbac.get_user_roles(user_id)
        
        for role in roles:
            if self.permission_matrix.can_access(role, resource, action):
                return True
        
        return False
    
    async def get_user_security_profile(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Get complete security profile for user"""
        
        roles = self.get_user_roles(user_id)
        permissions = self.get_user_permissions(user_id)
        
        # Get activity summary
        activity = await self.audit.get_user_activity_summary(user_id, days=30)
        
        return {
            "user_id": str(user_id),
            "roles": roles,
            "permissions": permissions,
            "permission_count": len(permissions),
            "recent_activity": activity
        }
    
    def get_role_matrix(self, role: Role) -> Dict[str, List[str]]:
        """Get permission matrix for a role"""
        return self.permission_matrix.get_role_matrix(role)
    
    def get_all_role_matrices(self) -> Dict[str, Dict[str, List[str]]]:
        """Get permission matrices for all roles"""
        matrices = self.permission_matrix.get_all_matrices()
        return {k.value: v for k, v in matrices.items()}


# Singleton instance
_security_service = None

def get_security_service() -> SecurityService:
    """Get singleton security service"""
    global _security_service
    if _security_service is None:
        _security_service = SecurityService()
    return _security_service


# Authentication dependency for FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user from JWT token"""
    # TODO: Implement JWT validation
    # For now, return mock user
    
    token = credentials.credentials
    
    # Mock user for development
    mock_user = {
        "user_id": uuid.UUID("da338137-9091-48a8-85f9-a75e014fc32f"),
        "username": "admin",
        "role": Role.ADMIN,
        "email": "admin@nemesis.local"
    }
    
    return mock_user


async def require_role(required_role: Role, current_user: Dict = Depends(get_current_user)):
    """Dependency to require specific role"""
    if current_user["role"] != required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role {required_role.value} required"
        )
    return current_user


async def require_any_role(required_roles: List[Role], current_user: Dict = Depends(get_current_user)):
    """Dependency to require any of the roles"""
    if current_user["role"] not in required_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of roles {[r.value for r in required_roles]} required"
        )
    return current_user