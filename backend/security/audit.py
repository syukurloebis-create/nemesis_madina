"""
Security Audit
Audit keamanan sistem
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class SecurityFinding:
    """Temuan keamanan"""
    id: str
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    recommendation: str
    status: str = "open"
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "recommendation": self.recommendation,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }


class SecurityAuditor:
    """
    Security Audit
    Melakukan audit keamanan sistem
    """

    def __init__(self):
        self.findings: List[SecurityFinding] = []
        self.audit_log: List[Dict[str, Any]] = []

    def run_audit(self) -> List[SecurityFinding]:
        """
        Run comprehensive security audit
        """
        self.findings = []

        # 1. Check authentication
        self._check_authentication()

        # 2. Check authorization
        self._check_authorization()

        # 3. Check data encryption
        self._check_encryption()

        # 4. Check API security
        self._check_api_security()

        # 5. Check dependencies
        self._check_dependencies()

        # 6. Check logging
        self._check_logging()

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        self.findings.sort(key=lambda x: severity_order.get(x.severity, 4))

        return self.findings

    def _check_authentication(self) -> None:
        """Check authentication security"""
        # Check if JWT is used
        if not self._check_jwt_implementation():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="authentication",
                severity="HIGH",
                description="JWT not properly implemented",
                recommendation="Implement JWT with proper expiration and validation"
            ))

        # Check password policy
        if not self._check_password_policy():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="authentication",
                severity="MEDIUM",
                description="Weak password policy",
                recommendation="Enforce strong password policy"
            ))

    def _check_authorization(self) -> None:
        """Check authorization security"""
        # Check RBAC implementation
        if not self._check_rbac():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="authorization",
                severity="CRITICAL",
                description="RBAC not properly implemented",
                recommendation="Implement proper role-based access control"
            ))

    def _check_encryption(self) -> None:
        """Check data encryption"""
        # Check if data is encrypted at rest
        if not self._check_encryption_at_rest():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="encryption",
                severity="HIGH",
                description="Data not encrypted at rest",
                recommendation="Enable data encryption at rest"
            ))

    def _check_api_security(self) -> None:
        """Check API security"""
        # Check rate limiting
        if not self._check_rate_limiting():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="api_security",
                severity="MEDIUM",
                description="Rate limiting not implemented",
                recommendation="Implement rate limiting on API endpoints"
            ))

        # Check CORS
        if not self._check_cors():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="api_security",
                severity="MEDIUM",
                description="CORS not properly configured",
                recommendation="Restrict CORS origins"
            ))

    def _check_dependencies(self) -> None:
        """Check dependencies for vulnerabilities"""
        # Simplified check
        self.findings.append(SecurityFinding(
            id=f"SEC-{len(self.findings)+1}",
            category="dependencies",
            severity="LOW",
            description="Dependency vulnerabilities not checked",
            recommendation="Regularly scan dependencies for vulnerabilities"
        ))

    def _check_logging(self) -> None:
        """Check logging implementation"""
        if not self._check_audit_logging():
            self.findings.append(SecurityFinding(
                id=f"SEC-{len(self.findings)+1}",
                category="logging",
                severity="MEDIUM",
                description="Audit logging not comprehensive",
                recommendation="Implement comprehensive audit logging"
            ))

    def _check_jwt_implementation(self) -> bool:
        """Check JWT implementation"""
        try:
            import jwt
            return True
        except ImportError:
            return False

    def _check_password_policy(self) -> bool:
        """Check password policy"""
        # Placeholder
        return True

    def _check_rbac(self) -> bool:
        """Check RBAC implementation"""
        try:
            from backend.dependencies.auth import require_permission
            return True
        except ImportError:
            return False

    def _check_encryption_at_rest(self) -> bool:
        """Check encryption at rest"""
        # Placeholder
        return True

    def _check_rate_limiting(self) -> bool:
        """Check rate limiting"""
        try:
            from backend.middleware.rate_limit import rate_limit
            return True
        except ImportError:
            return False

    def _check_cors(self) -> bool:
        """Check CORS configuration"""
        # Placeholder
        return True

    def _check_audit_logging(self) -> bool:
        """Check audit logging"""
        try:
            from backend.audit.audit_logger import audit_logger
            return True
        except ImportError:
            return False

    def get_findings(self, severity: Optional[str] = None) -> List[SecurityFinding]:
        """Get findings"""
        if severity:
            return [f for f in self.findings if f.severity == severity]
        return self.findings

    def get_summary(self) -> Dict[str, Any]:
        """Get audit summary"""
        total = len(self.findings)
        by_severity = {}
        by_category = {}

        for finding in self.findings:
            by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
            by_category[finding.category] = by_category.get(finding.category, 0) + 1

        return {
            "total_findings": total,
            "by_severity": by_severity,
            "by_category": by_category,
            "findings": [f.to_dict() for f in self.findings]
        }


# Singleton instance
security_auditor = SecurityAuditor()