"""Canonical Permission Enum - SEC-4.5 Frozen Contract

Single source of truth for all authorization permissions.
Contains exactly 46 permissions.
CASE_DELETE and EVIDENCE_DELETE are intentionally excluded.
"""

from enum import Enum


class Permission(str, Enum):
    """Canonical permissions for NEMESIS authorization."""
    
    # Case Management (9 permissions)
    CASE_VIEW = "case:view"
    CASE_CREATE = "case:create"
    CASE_UPDATE = "case:update"
    CASE_ASSIGN = "case:assign"
    CASE_REASSIGN = "case:reassign"
    CASE_APPROVE = "case:approve"
    CASE_REJECT = "case:reject"
    CASE_ESCALATE = "case:escalate"
    CASE_CLOSE = "case:close"
    
    # Evidence Management (5 permissions)
    EVIDENCE_VIEW = "evidence:view"
    EVIDENCE_UPLOAD = "evidence:upload"
    EVIDENCE_UPDATE = "evidence:update"
    EVIDENCE_VERIFY = "evidence:verify"
    EVIDENCE_TRANSFER = "evidence:transfer"
    
    # Entity Management (5 permissions)
    ENTITY_VIEW = "entity:view"
    ENTITY_CREATE = "entity:create"
    ENTITY_UPDATE = "entity:update"
    ENTITY_MERGE = "entity:merge"
    ENTITY_BLACKLIST = "entity:blacklist"
    
    # Finding Management (5 permissions)
    FINDING_VIEW = "finding:view"
    FINDING_CREATE = "finding:create"
    FINDING_UPDATE = "finding:update"
    FINDING_APPROVE = "finding:approve"
    FINDING_REJECT = "finding:reject"
    
    # Recommendation Management (4 permissions)
    RECOMMENDATION_VIEW = "recommendation:view"
    RECOMMENDATION_CREATE = "recommendation:create"
    RECOMMENDATION_UPDATE = "recommendation:update"
    RECOMMENDATION_APPROVE = "recommendation:approve"
    
    # Outcome Management (2 permissions)
    OUTCOME_VIEW = "outcome:view"
    OUTCOME_UPDATE = "outcome:update"
    
    # Recovery Management (3 permissions)
    RECOVERY_VIEW = "recovery:view"
    RECOVERY_CREATE = "recovery:create"
    RECOVERY_UPDATE = "recovery:update"
    
    # Report Management (3 permissions)
    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"
    REPORT_GENERATE = "report:generate"
    
    # Dashboard Management (3 permissions)
    DASHBOARD_OPERATIONAL = "dashboard:operational"
    DASHBOARD_EXECUTIVE = "dashboard:executive"
    DASHBOARD_STRATEGIC = "dashboard:strategic"
    
    # Intelligence Management (3 permissions)
    INTELLIGENCE_VIEW = "intelligence:view"
    INTELLIGENCE_GRAPH = "intelligence:graph"
    INTELLIGENCE_RISK = "intelligence:risk"
    
    # Administration (4 permissions)
    ADMIN_USER_MANAGE = "admin:user:manage"
    ADMIN_ROLE_MANAGE = "admin:role:manage"
    ADMIN_SYSTEM_CONFIG = "admin:system:config"
    ADMIN_AUDIT_VIEW = "admin:audit:view"
    
    @classmethod
    def count(cls) -> int:
        """Return total number of permissions."""
        return len(cls.__members__)
    
    @classmethod
    def values(cls) -> list[str]:
        """Return all permission values as strings."""
        return [p.value for p in cls]
    
    @classmethod
    def all_permissions(cls) -> set["Permission"]:
        """Return all permissions as a set."""
        return set(cls.__members__.values())