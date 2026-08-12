"""Canonical Role-Permission Registry - SEC-4.5 Frozen Contract

Explicit final grants for each SecurityRole.
No inheritance - all permissions are explicitly listed.
"""

from typing import Set
from backend.domain.enums.security_role import SecurityRole
from backend.domain.enums.permission import Permission


# Explicit grants for each role
ROLE_PERMISSIONS: dict[SecurityRole, Set[Permission]] = {
    # ADMIN: All 46 permissions
    SecurityRole.ADMIN: {
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.CASE_ASSIGN,
        Permission.CASE_REASSIGN,
        Permission.CASE_APPROVE,
        Permission.CASE_REJECT,
        Permission.CASE_ESCALATE,
        Permission.CASE_CLOSE,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_UPLOAD,
        Permission.EVIDENCE_UPDATE,
        Permission.EVIDENCE_VERIFY,
        Permission.EVIDENCE_TRANSFER,
        Permission.ENTITY_VIEW,
        Permission.ENTITY_CREATE,
        Permission.ENTITY_UPDATE,
        Permission.ENTITY_MERGE,
        Permission.ENTITY_BLACKLIST,
        Permission.FINDING_VIEW,
        Permission.FINDING_CREATE,
        Permission.FINDING_UPDATE,
        Permission.FINDING_APPROVE,
        Permission.FINDING_REJECT,
        Permission.RECOMMENDATION_VIEW,
        Permission.RECOMMENDATION_CREATE,
        Permission.RECOMMENDATION_UPDATE,
        Permission.RECOMMENDATION_APPROVE,
        Permission.OUTCOME_VIEW,
        Permission.OUTCOME_UPDATE,
        Permission.RECOVERY_VIEW,
        Permission.RECOVERY_CREATE,
        Permission.RECOVERY_UPDATE,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
        Permission.REPORT_GENERATE,
        Permission.DASHBOARD_OPERATIONAL,
        Permission.DASHBOARD_EXECUTIVE,
        Permission.DASHBOARD_STRATEGIC,
        Permission.INTELLIGENCE_VIEW,
        Permission.INTELLIGENCE_GRAPH,
        Permission.INTELLIGENCE_RISK,
        Permission.ADMIN_USER_MANAGE,
        Permission.ADMIN_ROLE_MANAGE,
        Permission.ADMIN_SYSTEM_CONFIG,
        Permission.ADMIN_AUDIT_VIEW,
    },
    
    # INVESTIGATOR: 24 permissions
    SecurityRole.INVESTIGATOR: {
        Permission.CASE_VIEW,
        Permission.CASE_CREATE,
        Permission.CASE_UPDATE,
        Permission.CASE_ASSIGN,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_UPLOAD,
        Permission.EVIDENCE_UPDATE,
        Permission.ENTITY_VIEW,
        Permission.ENTITY_CREATE,
        Permission.ENTITY_UPDATE,
        Permission.FINDING_VIEW,
        Permission.FINDING_CREATE,
        Permission.FINDING_UPDATE,
        Permission.RECOMMENDATION_VIEW,
        Permission.RECOMMENDATION_CREATE,
        Permission.RECOMMENDATION_UPDATE,
        Permission.OUTCOME_VIEW,
        Permission.RECOVERY_VIEW,
        Permission.RECOVERY_CREATE,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
        Permission.DASHBOARD_OPERATIONAL,
        Permission.INTELLIGENCE_VIEW,
        Permission.INTELLIGENCE_GRAPH,
    },
    
    # IRBAN: 25 permissions
    SecurityRole.IRBAN: {
        Permission.CASE_VIEW,
        Permission.CASE_REASSIGN,
        Permission.CASE_APPROVE,
        Permission.CASE_REJECT,
        Permission.EVIDENCE_VIEW,
        Permission.EVIDENCE_VERIFY,
        Permission.EVIDENCE_TRANSFER,
        Permission.ENTITY_VIEW,
        Permission.ENTITY_MERGE,
        Permission.FINDING_VIEW,
        Permission.FINDING_APPROVE,
        Permission.FINDING_REJECT,
        Permission.RECOMMENDATION_VIEW,
        Permission.RECOMMENDATION_APPROVE,
        Permission.OUTCOME_VIEW,
        Permission.OUTCOME_UPDATE,
        Permission.RECOVERY_VIEW,
        Permission.RECOVERY_UPDATE,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
        Permission.REPORT_GENERATE,
        Permission.DASHBOARD_OPERATIONAL,
        Permission.INTELLIGENCE_VIEW,
        Permission.INTELLIGENCE_GRAPH,
        Permission.INTELLIGENCE_RISK,
    },
    
    # INSPEKTUR: 21 permissions
    SecurityRole.INSPEKTUR: {
        Permission.CASE_VIEW,
        Permission.CASE_APPROVE,
        Permission.CASE_REJECT,
        Permission.CASE_ESCALATE,
        Permission.CASE_CLOSE,
        Permission.EVIDENCE_VIEW,
        Permission.ENTITY_VIEW,
        Permission.ENTITY_BLACKLIST,
        Permission.FINDING_VIEW,
        Permission.FINDING_APPROVE,
        Permission.RECOMMENDATION_VIEW,
        Permission.RECOMMENDATION_APPROVE,
        Permission.OUTCOME_VIEW,
        Permission.REPORT_VIEW,
        Permission.REPORT_EXPORT,
        Permission.REPORT_GENERATE,
        Permission.DASHBOARD_EXECUTIVE,
        Permission.DASHBOARD_STRATEGIC,
        Permission.INTELLIGENCE_VIEW,
        Permission.INTELLIGENCE_GRAPH,
        Permission.INTELLIGENCE_RISK,
    },
    
    # EXECUTIVE: 5 permissions
    SecurityRole.EXECUTIVE: {
        Permission.DASHBOARD_EXECUTIVE,
        Permission.DASHBOARD_STRATEGIC,
        Permission.REPORT_VIEW,
        Permission.INTELLIGENCE_VIEW,
        Permission.OUTCOME_VIEW,
    },
    
    # ANALYST: 3 permissions
    SecurityRole.ANALYST: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.FINDING_VIEW,
    },
    
    # VIEWER: 3 permissions
    SecurityRole.VIEWER: {
        Permission.CASE_VIEW,
        Permission.EVIDENCE_VIEW,
        Permission.FINDING_VIEW,
    },
}


def get_permissions_for_role(role: SecurityRole) -> Set[Permission]:
    """Get all permissions for a given SecurityRole."""
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: SecurityRole, permission: Permission) -> bool:
    """Check if a SecurityRole has a specific permission."""
    return permission in get_permissions_for_role(role)


def get_roles_for_permission(permission: Permission) -> list[SecurityRole]:
    """Get all roles that have a specific permission."""
    return [
        role for role, perms in ROLE_PERMISSIONS.items()
        if permission in perms
    ]