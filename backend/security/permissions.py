# backend/security/permissions.py
from typing import Dict, List, Set, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

from .rbac import Role, Permission, get_rbac, get_role_definition


@dataclass
class ResourcePermission:
    """Permission configuration untuk suatu resource"""
    resource: str
    actions: List[str]
    role_permissions: Dict[Role, List[str]] = field(default_factory=dict)
    
    def get_allowed_actions(self, role: Role) -> List[str]:
        """Get allowed actions for a role"""
        return self.role_permissions.get(role, [])
    
    def can_perform(self, role: Role, action: str) -> bool:
        """Check if role can perform action on resource"""
        return action in self.get_allowed_actions(role)


class PermissionMatrix:
    """Matrix permissions untuk semua resource"""
    
    def __init__(self):
        self._resources: Dict[str, ResourcePermission] = {}
        self._init_matrix()
    
    def _init_matrix(self):
        """Initialize permission matrix"""
        
        # Case Resource
        self._resources["case"] = ResourcePermission(
            resource="case",
            actions=["view", "create", "update", "delete", "assign", "reassign", 
                     "approve", "reject", "close", "escalate"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "create", "update", "assign"],
                Role.IRBAN: ["view", "reassign", "approve", "reject"],
                Role.INSPEKTUR: ["view", "approve", "reject", "close", "escalate"],
                Role.ADMIN: ["view", "create", "update", "delete", "assign", 
                            "reassign", "approve", "reject", "close", "escalate"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Evidence Resource
        self._resources["evidence"] = ResourcePermission(
            resource="evidence",
            actions=["view", "upload", "update", "delete", "verify", "transfer"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "upload", "update"],
                Role.IRBAN: ["view", "verify", "transfer"],
                Role.INSPEKTUR: ["view"],
                Role.ADMIN: ["view", "upload", "update", "delete", "verify", "transfer"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Entity Resource
        self._resources["entity"] = ResourcePermission(
            resource="entity",
            actions=["view", "create", "update", "merge", "blacklist"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "create", "update"],
                Role.IRBAN: ["view", "merge"],
                Role.INSPEKTUR: ["view", "blacklist"],
                Role.ADMIN: ["view", "create", "update", "merge", "blacklist"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Finding Resource
        self._resources["finding"] = ResourcePermission(
            resource="finding",
            actions=["view", "create", "update", "approve", "reject"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "create", "update"],
                Role.IRBAN: ["view", "approve", "reject"],
                Role.INSPEKTUR: ["view", "approve"],
                Role.ADMIN: ["view", "create", "update", "approve", "reject"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Recommendation Resource
        self._resources["recommendation"] = ResourcePermission(
            resource="recommendation",
            actions=["view", "create", "update", "approve"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "create", "update"],
                Role.IRBAN: ["view", "approve"],
                Role.INSPEKTUR: ["view", "approve"],
                Role.ADMIN: ["view", "create", "update", "approve"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Report Resource
        self._resources["report"] = ResourcePermission(
            resource="report",
            actions=["view", "export", "generate"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "export"],
                Role.IRBAN: ["view", "export", "generate"],
                Role.INSPEKTUR: ["view", "export", "generate"],
                Role.ADMIN: ["view", "export", "generate"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Dashboard Resource
        self._resources["dashboard"] = ResourcePermission(
            resource="dashboard",
            actions=["executive", "strategic", "operational"],
            role_permissions={
                Role.INVESTIGATOR: ["operational"],
                Role.IRBAN: ["operational"],
                Role.INSPEKTUR: ["executive", "strategic"],
                Role.ADMIN: ["executive", "strategic", "operational"],
                Role.EXECUTIVE: ["executive", "strategic"]
            }
        )
        
        # Intelligence Resource
        self._resources["intelligence"] = ResourcePermission(
            resource="intelligence",
            actions=["view", "graph", "risk"],
            role_permissions={
                Role.INVESTIGATOR: ["view", "graph"],
                Role.IRBAN: ["view", "graph", "risk"],
                Role.INSPEKTUR: ["view", "graph", "risk"],
                Role.ADMIN: ["view", "graph", "risk"],
                Role.EXECUTIVE: ["view"]
            }
        )
        
        # Admin Resource
        self._resources["admin"] = ResourcePermission(
            resource="admin",
            actions=["user_manage", "role_manage", "system_config", "audit_view"],
            role_permissions={
                Role.ADMIN: ["user_manage", "role_manage", "system_config", "audit_view"]
            }
        )
    
    def get_resource_permission(self, resource: str) -> Optional[ResourcePermission]:
        """Get permission config for resource"""
        return self._resources.get(resource)
    
    def can_access(self, role: Role, resource: str, action: str) -> bool:
        """Check if role can access resource with specific action"""
        resource_perm = self._resources.get(resource)
        if not resource_perm:
            return False
        return resource_perm.can_perform(role, action)
    
    def get_role_matrix(self, role: Role) -> Dict[str, List[str]]:
        """Get permission matrix for a specific role"""
        matrix = {}
        for resource, perm in self._resources.items():
            actions = perm.get_allowed_actions(role)
            if actions:
                matrix[resource] = actions
        return matrix
    
    def get_all_matrices(self) -> Dict[Role, Dict[str, List[str]]]:
        """Get permission matrices for all roles"""
        matrices = {}
        for role in Role:
            matrices[role] = self.get_role_matrix(role)
        return matrices


# Singleton instance
_permission_matrix = None

def get_permission_matrix() -> PermissionMatrix:
    """Get singleton permission matrix"""
    global _permission_matrix
    if _permission_matrix is None:
        _permission_matrix = PermissionMatrix()
    return _permission_matrix


# Decorator for permission checking
def require_permission(permission: Permission):
    """Decorator untuk memeriksa permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user_id from request state
            request = kwargs.get('request')
            if request and hasattr(request, 'state') and hasattr(request.state, 'user_id'):
                user_id = request.state.user_id
                rbac = get_rbac()
                if rbac.has_permission(user_id, permission):
                    return await func(*args, **kwargs)
                else:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=403, detail=f"Permission denied: {permission.value}")
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
        return wrapper
    return decorator


def require_any_permission(permissions: List[Permission]):
    """Decorator untuk memeriksa salah satu permission"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if request and hasattr(request, 'state') and hasattr(request.state, 'user_id'):
                user_id = request.state.user_id
                rbac = get_rbac()
                if rbac.has_any_permission(user_id, permissions):
                    return await func(*args, **kwargs)
                else:
                    from fastapi import HTTPException
                    raise HTTPException(status_code=403, detail=f"Permission denied. Required one of: {[p.value for p in permissions]}")
            else:
                from fastapi import HTTPException
                raise HTTPException(status_code=401, detail="Authentication required")
        return wrapper
    return decorator