# backend/security/rbac.py
from enum import Enum
from typing import List, Set, Optional, Dict, Any
from functools import wraps
from dataclasses import dataclass, field
import uuid


class Role(str, Enum):
    """User roles dalam sistem"""
    INVESTIGATOR = "INVESTIGATOR"     # Auditor/Investigator
    IRBAN = "IRBAN"                   # Inspektur Pembantu
    INSPEKTUR = "INSPEKTUR"           # Inspektur
    ADMIN = "ADMIN"                   # Administrator sistem
    EXECUTIVE = "EXECUTIVE"           # Pimpinan (Bupati/Sekda)


class Permission(str, Enum):
    """Permissions untuk setiap resource"""
    
    # Case permissions
    CASE_VIEW = "case:view"
    CASE_CREATE = "case:create"
    CASE_UPDATE = "case:update"
    CASE_DELETE = "case:delete"
    CASE_ASSIGN = "case:assign"
    CASE_REASSIGN = "case:reassign"
    CASE_APPROVE = "case:approve"
    CASE_REJECT = "case:reject"
    CASE_CLOSE = "case:close"
    CASE_ESCALATE = "case:escalate"
    
    # Evidence permissions
    EVIDENCE_VIEW = "evidence:view"
    EVIDENCE_UPLOAD = "evidence:upload"
    EVIDENCE_UPDATE = "evidence:update"
    EVIDENCE_DELETE = "evidence:delete"
    EVIDENCE_VERIFY = "evidence:verify"
    EVIDENCE_TRANSFER = "evidence:transfer"
    
    # Entity permissions
    ENTITY_VIEW = "entity:view"
    ENTITY_CREATE = "entity:create"
    ENTITY_UPDATE = "entity:update"
    ENTITY_MERGE = "entity:merge"
    ENTITY_BLACKLIST = "entity:blacklist"
    
    # Finding permissions
    FINDING_VIEW = "finding:view"
    FINDING_CREATE = "finding:create"
    FINDING_UPDATE = "finding:update"
    FINDING_APPROVE = "finding:approve"
    FINDING_REJECT = "finding:reject"
    
    # Recommendation permissions
    RECOMMENDATION_VIEW = "recommendation:view"
    RECOMMENDATION_CREATE = "recommendation:create"
    RECOMMENDATION_UPDATE = "recommendation:update"
    RECOMMENDATION_APPROVE = "recommendation:approve"
    
    # Outcome permissions
    OUTCOME_VIEW = "outcome:view"
    OUTCOME_UPDATE = "outcome:update"
    
    # Recovery permissions
    RECOVERY_VIEW = "recovery:view"
    RECOVERY_CREATE = "recovery:create"
    RECOVERY_UPDATE = "recovery:update"
    
    # Report permissions
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    REPORT_GENERATE = "report:generate"
    
    # Admin permissions
    ADMIN_USER_MANAGE = "admin:user:manage"
    ADMIN_ROLE_MANAGE = "admin:role:manage"
    ADMIN_SYSTEM_CONFIG = "admin:system:config"
    ADMIN_AUDIT_VIEW = "admin:audit:view"
    
    # Dashboard permissions
    DASHBOARD_EXECUTIVE = "dashboard:executive"
    DASHBOARD_STRATEGIC = "dashboard:strategic"
    DASHBOARD_OPERATIONAL = "dashboard:operational"
    
    # Intelligence permissions
    INTELLIGENCE_VIEW = "intelligence:view"
    INTELLIGENCE_GRAPH = "intelligence:graph"
    INTELLIGENCE_RISK = "intelligence:risk"


@dataclass
class RoleDefinition:
    """Definisi role beserta permissionsnya"""
    name: Role
    display_name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    inherited_from: List[Role] = field(default_factory=list)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has specific permission (including inherited)"""
        if permission in self.permissions:
            return True
        
        for inherited in self.inherited_from:
            role_def = get_role_definition(inherited)
            if role_def and role_def.has_permission(permission):
                return True
        
        return False
    
    def get_all_permissions(self) -> Set[Permission]:
        """Get all permissions including inherited"""
        all_perms = self.permissions.copy()
        
        for inherited in self.inherited_from:
            role_def = get_role_definition(inherited)
            if role_def:
                all_perms.update(role_def.get_all_permissions())
        
        return all_perms


# Role definitions registry
_role_definitions: Dict[Role, RoleDefinition] = {}


def get_role_definition(role: Role) -> Optional[RoleDefinition]:
    """Get role definition by role"""
    return _role_definitions.get(role)


def register_role(role_def: RoleDefinition):
    """Register role definition"""
    _role_definitions[role_def.name] = role_def


def init_role_definitions():
    """Initialize all role definitions"""
    
    # INVESTIGATOR - Base role untuk auditor
    investigator = RoleDefinition(
        name=Role.INVESTIGATOR,
        display_name="Investigator",
        description="Auditor/Investigator yang melakukan investigasi",
        permissions={
            # Case
            Permission.CASE_VIEW, Permission.CASE_CREATE, Permission.CASE_UPDATE,
            Permission.CASE_ASSIGN,
            # Evidence
            Permission.EVIDENCE_VIEW, Permission.EVIDENCE_UPLOAD, Permission.EVIDENCE_UPDATE,
            # Entity
            Permission.ENTITY_VIEW, Permission.ENTITY_CREATE, Permission.ENTITY_UPDATE,
            # Finding
            Permission.FINDING_VIEW, Permission.FINDING_CREATE, Permission.FINDING_UPDATE,
            # Recommendation
            Permission.RECOMMENDATION_VIEW, Permission.RECOMMENDATION_CREATE,
            Permission.RECOMMENDATION_UPDATE,
            # Outcome
            Permission.OUTCOME_VIEW,
            # Recovery
            Permission.RECOVERY_VIEW, Permission.RECOVERY_CREATE,
            # Report
            Permission.REPORT_VIEW, Permission.REPORT_EXPORT,
            # Dashboard
            Permission.DASHBOARD_OPERATIONAL,
            # Intelligence
            Permission.INTELLIGENCE_VIEW, Permission.INTELLIGENCE_GRAPH
        }
    )
    register_role(investigator)
    
    # IRBAN (Inspektur Pembantu)
    irban = RoleDefinition(
        name=Role.IRBAN,
        display_name="Irban",
        description="Inspektur Pembantu - Supervisor investigator",
        permissions={
            # Case
            Permission.CASE_VIEW, Permission.CASE_REASSIGN, Permission.CASE_APPROVE,
            Permission.CASE_REJECT,
            # Evidence
            Permission.EVIDENCE_VIEW, Permission.EVIDENCE_VERIFY, Permission.EVIDENCE_TRANSFER,
            # Entity
            Permission.ENTITY_VIEW, Permission.ENTITY_MERGE,
            # Finding
            Permission.FINDING_VIEW, Permission.FINDING_APPROVE, Permission.FINDING_REJECT,
            # Recommendation
            Permission.RECOMMENDATION_VIEW, Permission.RECOMMENDATION_APPROVE,
            # Outcome
            Permission.OUTCOME_VIEW, Permission.OUTCOME_UPDATE,
            # Recovery
            Permission.RECOVERY_VIEW, Permission.RECOVERY_UPDATE,
            # Report
            Permission.REPORT_VIEW, Permission.REPORT_EXPORT, Permission.REPORT_GENERATE,
            # Dashboard
            Permission.DASHBOARD_OPERATIONAL,
            # Intelligence
            Permission.INTELLIGENCE_VIEW, Permission.INTELLIGENCE_GRAPH, Permission.INTELLIGENCE_RISK
        },
        inherited_from=[Role.INVESTIGATOR]
    )
    register_role(irban)
    
    # INSPEKTUR
    inspektur = RoleDefinition(
        name=Role.INSPEKTUR,
        display_name="Inspektur",
        description="Inspektur - Kepala inspektorat",
        permissions={
            # Case
            Permission.CASE_VIEW, Permission.CASE_APPROVE, Permission.CASE_REJECT,
            Permission.CASE_ESCALATE, Permission.CASE_CLOSE,
            # Evidence
            Permission.EVIDENCE_VIEW,
            # Entity
            Permission.ENTITY_VIEW, Permission.ENTITY_BLACKLIST,
            # Finding
            Permission.FINDING_VIEW, Permission.FINDING_APPROVE,
            # Recommendation
            Permission.RECOMMENDATION_VIEW, Permission.RECOMMENDATION_APPROVE,
            # Outcome
            Permission.OUTCOME_VIEW,
            # Report
            Permission.REPORT_VIEW, Permission.REPORT_EXPORT, Permission.REPORT_GENERATE,
            # Dashboard
            Permission.DASHBOARD_EXECUTIVE, Permission.DASHBOARD_STRATEGIC,
            # Intelligence
            Permission.INTELLIGENCE_VIEW, Permission.INTELLIGENCE_GRAPH, 
            Permission.INTELLIGENCE_RISK
        },
        inherited_from=[Role.IRBAN]
    )
    register_role(inspektur)
    
    # ADMIN
    admin = RoleDefinition(
        name=Role.ADMIN,
        display_name="Administrator",
        description="Administrator sistem",
        permissions={
            # All admin permissions
            Permission.ADMIN_USER_MANAGE, Permission.ADMIN_ROLE_MANAGE,
            Permission.ADMIN_SYSTEM_CONFIG, Permission.ADMIN_AUDIT_VIEW,
            # Also inherits all from inspektur
        },
        inherited_from=[Role.INSPEKTUR]
    )
    register_role(admin)
    
    # EXECUTIVE (Bupati/Sekda)
    executive = RoleDefinition(
        name=Role.EXECUTIVE,
        display_name="Executive",
        description="Pimpinan daerah - Bupati/Sekda",
        permissions={
            # Dashboard only - strategic view
            Permission.DASHBOARD_EXECUTIVE, Permission.DASHBOARD_STRATEGIC,
            Permission.REPORT_VIEW, Permission.INTELLIGENCE_VIEW,
            Permission.OUTCOME_VIEW
        }
    )
    register_role(executive)


class RBAC:
    """Role-Based Access Control manager"""
    
    def __init__(self):
        self._user_roles: Dict[uuid.UUID, Set[Role]] = {}
        self._user_permissions_cache: Dict[uuid.UUID, Set[Permission]] = {}
    
    def assign_role(self, user_id: uuid.UUID, role: Role):
        """Assign role to user"""
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()
        self._user_roles[user_id].add(role)
        # Clear cache
        self._user_permissions_cache.pop(user_id, None)
    
    def revoke_role(self, user_id: uuid.UUID, role: Role):
        """Revoke role from user"""
        if user_id in self._user_roles:
            self._user_roles[user_id].discard(role)
            self._user_permissions_cache.pop(user_id, None)
    
    def get_user_roles(self, user_id: uuid.UUID) -> Set[Role]:
        """Get all roles for user"""
        return self._user_roles.get(user_id, set())
    
    def get_user_permissions(self, user_id: uuid.UUID) -> Set[Permission]:
        """Get all permissions for user (with caching)"""
        
        if user_id in self._user_permissions_cache:
            return self._user_permissions_cache[user_id]
        
        permissions = set()
        for role in self.get_user_roles(user_id):
            role_def = get_role_definition(role)
            if role_def:
                permissions.update(role_def.get_all_permissions())
        
        self._user_permissions_cache[user_id] = permissions
        return permissions
    
    def has_permission(self, user_id: uuid.UUID, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in self.get_user_permissions(user_id)
    
    def has_any_permission(self, user_id: uuid.UUID, permissions: List[Permission]) -> bool:
        """Check if user has any of the specified permissions"""
        user_perms = self.get_user_permissions(user_id)
        return any(p in user_perms for p in permissions)
    
    def has_all_permissions(self, user_id: uuid.UUID, permissions: List[Permission]) -> bool:
        """Check if user has all specified permissions"""
        user_perms = self.get_user_permissions(user_id)
        return all(p in user_perms for p in permissions)
    
    def clear_cache(self, user_id: Optional[uuid.UUID] = None):
        """Clear permission cache"""
        if user_id:
            self._user_permissions_cache.pop(user_id, None)
        else:
            self._user_permissions_cache.clear()


# Singleton instance
_rbac = None

def get_rbac() -> RBAC:
    """Get singleton RBAC instance"""
    global _rbac
    if _rbac is None:
        _rbac = RBAC()
        init_role_definitions()
    return _rbac