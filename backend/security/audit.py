# backend/security/audit.py
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json


class AuditAction(str, Enum):
    """Actions yang diaudit"""
    # Authentication
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    
    # Case actions
    CASE_CREATED = "CASE_CREATED"
    CASE_UPDATED = "CASE_UPDATED"
    CASE_VIEWED = "CASE_VIEWED"
    CASE_DELETED = "CASE_DELETED"
    CASE_STATUS_CHANGED = "CASE_STATUS_CHANGED"
    
    # Evidence actions
    EVIDENCE_UPLOADED = "EVIDENCE_UPLOADED"
    EVIDENCE_VIEWED = "EVIDENCE_VIEWED"
    EVIDENCE_DOWNLOADED = "EVIDENCE_DOWNLOADED"
    EVIDENCE_DELETED = "EVIDENCE_DELETED"
    EVIDENCE_VERIFIED = "EVIDENCE_VERIFIED"
    
    # Entity actions
    ENTITY_CREATED = "ENTITY_CREATED"
    ENTITY_UPDATED = "ENTITY_UPDATED"
    ENTITY_VIEWED = "ENTITY_VIEWED"
    
    # Finding actions
    FINDING_CREATED = "FINDING_CREATED"
    FINDING_UPDATED = "FINDING_UPDATED"
    FINDING_APPROVED = "FINDING_APPROVED"
    
    # Recommendation actions
    RECOMMENDATION_CREATED = "RECOMMENDATION_CREATED"
    RECOMMENDATION_UPDATED = "RECOMMENDATION_UPDATED"
    RECOMMENDATION_APPROVED = "RECOMMENDATION_APPROVED"
    
    # Report actions
    REPORT_GENERATED = "REPORT_GENERATED"
    REPORT_EXPORTED = "REPORT_EXPORTED"
    
    # Admin actions
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    ROLE_ASSIGNED = "ROLE_ASSIGNED"
    ROLE_REVOKED = "ROLE_REVOKED"
    PERMISSION_CHANGED = "PERMISSION_CHANGED"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    
    # Access control
    ACCESS_DENIED = "ACCESS_DENIED"
    PERMISSION_CHECK = "PERMISSION_CHECK"


@dataclass
class AuditLogEntry:
    """Entry dalam audit log"""
    log_id: uuid.UUID
    timestamp: datetime
    user_id: uuid.UUID
    username: str
    user_role: str
    action: AuditAction
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str  # SUCCESS, FAILED, DENIED
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": str(self.log_id),
            "timestamp": self.timestamp.isoformat(),
            "user_id": str(self.user_id),
            "username": self.username,
            "user_role": self.user_role,
            "action": self.action.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "status": self.status
        }


class AuditTrailService:
    """Service untuk mencatat audit trail"""
    
    def __init__(self):
        self._logs: List[AuditLogEntry] = []
        self._retention_days = 365 * 10  # 10 years retention for audit logs
    
    async def log(
        self,
        user_id: uuid.UUID,
        username: str,
        user_role: str,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS"
    ) -> AuditLogEntry:
        """Create audit log entry"""
        
        entry = AuditLogEntry(
            log_id=uuid.uuid4(),
            timestamp=datetime.utcnow(),
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            status=status
        )
        
        self._logs.append(entry)
        
        # TODO: Persist to database
        # await self._persist(entry)
        
        return entry
    
    async def log_case_action(
        self,
        user_id: uuid.UUID,
        username: str,
        user_role: str,
        action: AuditAction,
        case_id: uuid.UUID,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLogEntry:
        """Log case-related action"""
        return await self.log(
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action,
            resource_type="case",
            resource_id=str(case_id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_evidence_action(
        self,
        user_id: uuid.UUID,
        username: str,
        user_role: str,
        action: AuditAction,
        evidence_id: uuid.UUID,
        case_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLogEntry:
        """Log evidence-related action"""
        details = details or {}
        if case_id:
            details["case_id"] = str(case_id)
        
        return await self.log(
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=action,
            resource_type="evidence",
            resource_id=str(evidence_id),
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    async def log_access_denied(
        self,
        user_id: uuid.UUID,
        username: str,
        user_role: str,
        resource_type: str,
        resource_id: Optional[str],
        permission_required: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLogEntry:
        """Log access denied event"""
        return await self.log(
            user_id=user_id,
            username=username,
            user_role=user_role,
            action=AuditAction.ACCESS_DENIED,
            resource_type=resource_type,
            resource_id=resource_id,
            details={"permission_required": permission_required},
            ip_address=ip_address,
            user_agent=user_agent,
            status="DENIED"
        )
    
    async def get_logs(
        self,
        user_id: Optional[uuid.UUID] = None,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLogEntry]:
        """Get audit logs with filters"""
        
        logs = self._logs
        
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        
        if action:
            logs = [l for l in logs if l.action == action]
        
        if resource_type:
            logs = [l for l in logs if l.resource_type == resource_type]
        
        if start_date:
            logs = [l for l in logs if l.timestamp >= start_date]
        
        if end_date:
            logs = [l for l in logs if l.timestamp <= end_date]
        
        # Sort by timestamp descending
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply pagination
        return logs[offset:offset + limit]
    
    async def get_logs_by_case(self, case_id: uuid.UUID, limit: int = 100) -> List[AuditLogEntry]:
        """Get all logs related to a case"""
        
        logs = []
        for log in self._logs:
            if log.resource_id == str(case_id) and log.resource_type == "case":
                logs.append(log)
            elif log.details.get("case_id") == str(case_id):
                logs.append(log)
        
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        return logs[:limit]
    
    async def get_user_activity_summary(
        self,
        user_id: uuid.UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get user activity summary for last N days"""
        
        cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate start date
        from datetime import timedelta
        start_date = cutoff - timedelta(days=days)
        
        user_logs = [l for l in self._logs if l.user_id == user_id and l.timestamp >= start_date]
        
        # Count by action
        action_counts = {}
        for log in user_logs:
            action = log.action.value
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Count by day
        daily_counts = {}
        for log in user_logs:
            day = log.timestamp.date().isoformat()
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        return {
            "user_id": str(user_id),
            "period_days": days,
            "total_actions": len(user_logs),
            "action_breakdown": action_counts,
            "daily_activity": daily_counts,
            "first_action": user_logs[-1].timestamp.isoformat() if user_logs else None,
            "last_action": user_logs[0].timestamp.isoformat() if user_logs else None
        }
    
    async def get_system_audit_report(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get system-wide audit report"""
        
        logs = [l for l in self._logs if start_date <= l.timestamp <= end_date]
        
        # Summary statistics
        total_actions = len(logs)
        success_count = len([l for l in logs if l.status == "SUCCESS"])
        denied_count = len([l for l in logs if l.status == "DENIED"])
        failed_count = len([l for l in logs if l.status == "FAILED"])
        
        # Actions by user
        user_activity = {}
        for log in logs:
            user_key = f"{log.username} ({log.user_role})"
            user_activity[user_key] = user_activity.get(user_key, 0) + 1
        
        # Actions by type
        action_breakdown = {}
        for log in logs:
            action = log.action.value
            action_breakdown[action] = action_breakdown.get(action, 0) + 1
        
        # Resources accessed
        resource_breakdown = {}
        for log in logs:
            resource = log.resource_type
            resource_breakdown[resource] = resource_breakdown.get(resource, 0) + 1
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_actions": total_actions,
                "success_rate": round(success_count / total_actions * 100, 1) if total_actions else 0,
                "denied_count": denied_count,
                "failed_count": failed_count
            },
            "top_users": sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_actions": sorted(action_breakdown.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_resources": sorted(resource_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]
        }


# Singleton instance
_audit_service = None

def get_audit_service() -> AuditTrailService:
    """Get singleton audit service"""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditTrailService()
    return _audit_service


# Middleware for audit logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware untuk mencatat semua request"""
    
    async def dispatch(self, request: Request, call_next):
        # Get user info from request state (if authenticated)
        user_id = getattr(request.state, 'user_id', None)
        username = getattr(request.state, 'username', 'anonymous')
        user_role = getattr(request.state, 'user_role', 'anonymous')
        
        # Process request
        response = await call_next(request)
        
        # Log API access (skip static files)
        if not request.url.path.startswith("/static") and not request.url.path.startswith("/health"):
            audit = get_audit_service()
            
            # Determine action based on method and path
            action = AuditAction.PERMISSION_CHECK
            if request.method == "GET":
                action = AuditAction.CASE_VIEWED if "cases" in request.url.path else AuditAction.PERMISSION_CHECK
            elif request.method == "POST":
                action = AuditAction.CASE_CREATED if "cases" in request.url.path else AuditAction.PERMISSION_CHECK
            elif request.method == "PUT":
                action = AuditAction.CASE_UPDATED if "cases" in request.url.path else AuditAction.PERMISSION_CHECK
            elif request.method == "DELETE":
                action = AuditAction.CASE_DELETED if "cases" in request.url.path else AuditAction.PERMISSION_CHECK
            
            await audit.log(
                user_id=user_id or uuid.uuid4(),
                username=username,
                user_role=user_role,
                action=action,
                resource_type=request.url.path.split("/")[1] if len(request.url.path.split("/")) > 1 else "api",
                resource_id=None,
                details={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code
                },
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                status="SUCCESS" if response.status_code < 400 else "FAILED"
            )
        
        return response