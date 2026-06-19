# backend/domain/snapshots/snapshot.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

@dataclass
class EventSnapshot:
    """Snapshot of aggregate state at a specific version"""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    aggregate_id: str = ""
    aggregate_type: str = "case"
    version: int = 0
    snapshot_data: Dict[str, Any] = field(default_factory=dict)
    snapshot_hash: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        aggregate_id: str,
        version: int,
        snapshot_data: Dict[str, Any],
        created_by: Optional[str] = None,
        aggregate_type: str = "case"
    ) -> "EventSnapshot":
        """Factory method to create a new snapshot"""
        import hashlib
        import json
        
        # Compute hash of snapshot data
        canonical = json.dumps(snapshot_data, sort_keys=True, separators=(",", ":"))
        snapshot_hash = hashlib.sha256(canonical.encode()).hexdigest()
        
        return cls(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            version=version,
            snapshot_data=snapshot_data,
            snapshot_hash=snapshot_hash,
            created_by=created_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary"""
        return {
            "id": self.id,
            "aggregate_id": self.aggregate_id,
            "aggregate_type": self.aggregate_type,
            "version": self.version,
            "snapshot_data": self.snapshot_data,
            "snapshot_hash": self.snapshot_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventSnapshot":
        """Create snapshot from dictionary"""
        return cls(
            id=data.get("id", str(uuid4())),
            aggregate_id=data["aggregate_id"],
            aggregate_type=data.get("aggregate_type", "case"),
            version=data["version"],
            snapshot_data=data["snapshot_data"],
            snapshot_hash=data["snapshot_hash"],
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            created_by=data.get("created_by")
        )
