# backend/events/versioning.py
from enum import IntEnum
from typing import Optional, Dict, Any
from datetime import datetime
import uuid


class EventVersion(IntEnum):
    """Event version tracking untuk schema evolution"""
    V1 = 1
    V2 = 2
    V3 = 3
    # Future versions as needed


class VersionedEvent:
    """Wrapper untuk event dengan versioning support"""
    
    def __init__(self, event, version: EventVersion = EventVersion.V1):
        self.event = event
        self.version = version
        self.migrated_at = None
        self.migration_history = []
    
    def migrate_to(self, target_version: EventVersion) -> 'VersionedEvent':
        """Migrate event ke version yang lebih baru"""
        if self.version == target_version:
            return self
        
        current = self
        while current.version < target_version:
            current = self._apply_migration(current)
        
        return current
    
    def _apply_migration(self, versioned_event: 'VersionedEvent') -> 'VersionedEvent':
        """Apply satu level migration"""
        from .migrations import get_migration
        
        next_version = EventVersion(versioned_event.version.value + 1)
        migration_func = get_migration(versioned_event.version, next_version)
        
        if migration_func:
            new_payload = migration_func(versioned_event.event.payload)
            versioned_event.event.payload = new_payload
            versioned_event.version = next_version
            versioned_event.migration_history.append({
                "from_version": versioned_event.version.value - 1,
                "to_version": next_version.value,
                "migrated_at": datetime.utcnow()
            })
        
        return versioned_event
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary untuk storage"""
        return {
            "event": self.event.dict() if hasattr(self.event, 'dict') else self.event,
            "version": self.version.value,
            "migration_history": self.migration_history
        }


class EventVersionManager:
    """Manager untuk event versioning"""
    
    def __init__(self):
        self._version_handlers = {}
    
    def register_handler(self, from_version: EventVersion, to_version: EventVersion, handler):
        """Register migration handler"""
        key = (from_version, to_version)
        self._version_handlers[key] = handler
    
    def get_migration(self, from_version: EventVersion, to_version: EventVersion):
        """Get migration handler"""
        return self._version_handlers.get((from_version, to_version))
    
    def can_migrate(self, from_version: EventVersion, to_version: EventVersion) -> bool:
        """Check if migration is possible"""
        return (from_version, to_version) in self._version_handlers


# Global instance
version_manager = EventVersionManager()


# ============================================================
# MIGRATION HANDLERS
# ============================================================

def register_migration_handlers():
    """Register semua migration handlers"""
    
    # Example: CASE_CREATED V1 → V2
    def migrate_case_created_v1_to_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add priority field jika belum ada"""
        if "priority" not in payload:
            payload["priority"] = "MEDIUM"
        return payload
    
    version_manager.register_handler(
        EventVersion.V1, EventVersion.V2,
        migrate_case_created_v1_to_v2
    )
    
    # Example: EVIDENCE_ADDED V1 → V2
    def migrate_evidence_added_v1_to_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Add trust_score field jika belum ada"""
        if "trust_score" not in payload:
            payload["trust_score"] = 50
        return payload
    
    version_manager.register_handler(
        EventVersion.V1, EventVersion.V2,
        migrate_evidence_added_v1_to_v2
    )