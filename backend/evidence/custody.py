# backend/evidence/custody.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import uuid


class CustodyAction(str, Enum):
    """Actions in chain of custody"""
    UPLOADED = "UPLOADED"
    VIEWED = "VIEWED"
    VERIFIED = "VERIFIED"
    TRANSFERRED = "TRANSFERRED"
    RECEIVED = "RECEIVED"
    REVIEWED = "REVIEWED"
    SUBMITTED = "SUBMITTED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"


@dataclass
class CustodyEvent:
    """Event dalam chain of custody"""
    event_id: uuid.UUID
    evidence_id: uuid.UUID
    action: CustodyAction
    actor_id: uuid.UUID
    actor_name: str
    actor_role: str
    timestamp: datetime
    previous_holder: Optional[str] = None
    next_holder: Optional[str] = None
    notes: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "evidence_id": str(self.evidence_id),
            "action": self.action.value,
            "actor_id": str(self.actor_id),
            "actor_name": self.actor_name,
            "actor_role": self.actor_role,
            "timestamp": self.timestamp.isoformat(),
            "previous_holder": self.previous_holder,
            "next_holder": self.next_holder,
            "notes": self.notes,
            "ip_address": self.ip_address
        }


class CustodyChain:
    """Chain of custody untuk sebuah evidence"""
    
    def __init__(self, evidence_id: uuid.UUID):
        self.evidence_id = evidence_id
        self.events: List[CustodyEvent] = []
    
    def add_event(self, event: CustodyEvent):
        """Add event to custody chain"""
        self.events.append(event)
    
    def get_events(self) -> List[CustodyEvent]:
        """Get all custody events"""
        return self.events
    
    def get_current_holder(self) -> Optional[str]:
        """Get current holder of evidence"""
        if not self.events:
            return None
        
        # Find most recent transfer/receive event
        for event in reversed(self.events):
            if event.action == CustodyAction.RECEIVED:
                return event.actor_name
            elif event.action == CustodyAction.TRANSFERRED and event.next_holder:
                return event.next_holder
        
        # If no transfer, return uploader
        for event in reversed(self.events):
            if event.action == CustodyAction.UPLOADED:
                return event.actor_name
        
        return None
    
    def get_custody_history(self) -> List[Dict[str, Any]]:
        """Get formatted custody history"""
        history = []
        for event in self.events:
            history.append({
                "timestamp": event.timestamp.isoformat(),
                "action": event.action.value,
                "actor": event.actor_name,
                "role": event.actor_role,
                "from": event.previous_holder,
                "to": event.next_holder,
                "notes": event.notes
            })
        return history
    
    def validate_chain(self) -> Dict[str, Any]:
        """Validate integrity of custody chain"""
        
        issues = []
        warnings = []
        
        if not self.events:
            return {
                "is_valid": False,
                "issues": ["No custody events recorded"],
                "warnings": [],
                "completeness_score": 0
            }
        
        # Check for missing transfer/receive pairs
        transfers = [e for e in self.events if e.action == CustodyAction.TRANSFERRED]
        receives = [e for e in self.events if e.action == CustodyAction.RECEIVED]
        
        if len(transfers) != len(receives):
            issues.append(f"Mismatch between transfers ({len(transfers)}) and receives ({len(receives)})")
        
        # Check for gaps in chain
        for i in range(len(self.events) - 1):
            current = self.events[i]
            next_event = self.events[i + 1]
            
            # Check chronological order
            if next_event.timestamp < current.timestamp:
                issues.append(f"Chronological order violation between events {i} and {i+1}")
        
        # Check if we have proper start (UPLOADED)
        if self.events[0].action != CustodyAction.UPLOADED:
            issues.append("Custody chain does not start with UPLOADED event")
        
        # Check if we have proper end (not required for open cases)
        
        # Calculate completeness score
        required_events = ["UPLOADED", "VERIFIED"]
        present_events = set(e.action.value for e in self.events)
        completeness = len([r for r in required_events if r in present_events]) / len(required_events)
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "completeness_score": round(completeness * 100, 1),
            "total_events": len(self.events),
            "current_holder": self.get_current_holder(),
            "first_event": self.events[0].timestamp.isoformat() if self.events else None,
            "last_event": self.events[-1].timestamp.isoformat() if self.events else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "evidence_id": str(self.evidence_id),
            "events": [e.to_dict() for e in self.events],
            "current_holder": self.get_current_holder(),
            "total_events": len(self.events),
            "validation": self.validate_chain()
        }


class CustodyService:
    """Service untuk mengelola chain of custody"""
    
    def __init__(self):
        self._chains: Dict[uuid.UUID, CustodyChain] = {}
    
    def get_chain(self, evidence_id: uuid.UUID) -> CustodyChain:
        """Get or create custody chain for evidence"""
        if evidence_id not in self._chains:
            self._chains[evidence_id] = CustodyChain(evidence_id)
        return self._chains[evidence_id]
    
    def record_event(
        self,
        evidence_id: uuid.UUID,
        action: CustodyAction,
        actor_id: uuid.UUID,
        actor_name: str,
        actor_role: str,
        previous_holder: Optional[str] = None,
        next_holder: Optional[str] = None,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> CustodyEvent:
        """Record a custody event"""
        
        chain = self.get_chain(evidence_id)
        
        event = CustodyEvent(
            event_id=uuid.uuid4(),
            evidence_id=evidence_id,
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            timestamp=datetime.utcnow(),
            previous_holder=previous_holder,
            next_holder=next_holder,
            notes=notes,
            ip_address=ip_address
        )
        
        chain.add_event(event)
        
        # TODO: Persist to database
        
        return event
    
    def transfer_evidence(
        self,
        evidence_id: uuid.UUID,
        from_holder: str,
        to_holder: str,
        actor_id: uuid.UUID,
        actor_name: str,
        actor_role: str,
        notes: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> List[CustodyEvent]:
        """Record evidence transfer (two events: TRANSFERRED and RECEIVED)"""
        
        events = []
        
        # Record transfer from current holder
        transfer_event = self.record_event(
            evidence_id=evidence_id,
            action=CustodyAction.TRANSFERRED,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            previous_holder=from_holder,
            next_holder=to_holder,
            notes=notes,
            ip_address=ip_address
        )
        events.append(transfer_event)
        
        # Record receipt by new holder
        receive_event = self.record_event(
            evidence_id=evidence_id,
            action=CustodyAction.RECEIVED,
            actor_id=actor_id,
            actor_name=to_holder,  # Receiver is the actor
            actor_role=actor_role,
            previous_holder=from_holder,
            next_holder=to_holder,
            notes=f"Received from {from_holder}",
            ip_address=ip_address
        )
        events.append(receive_event)
        
        return events
    
    def verify_chain(self, evidence_id: uuid.UUID) -> Dict[str, Any]:
        """Verify chain of custody for evidence"""
        chain = self.get_chain(evidence_id)
        return chain.validate_chain()
    
    def get_full_chain(self, evidence_id: uuid.UUID) -> Dict[str, Any]:
        """Get full custody chain for evidence"""
        chain = self.get_chain(evidence_id)
        return chain.to_dict()
    
    def get_case_custody_summary(self, evidence_ids: List[uuid.UUID]) -> Dict[str, Any]:
        """Get custody summary for a case"""
        
        summaries = []
        valid_count = 0
        
        for evidence_id in evidence_ids:
            chain = self.get_chain(evidence_id)
            validation = chain.validate_chain()
            summaries.append({
                "evidence_id": str(evidence_id),
                "is_valid": validation["is_valid"],
                "completeness_score": validation["completeness_score"],
                "total_events": validation["total_events"]
            })
            if validation["is_valid"]:
                valid_count += 1
        
        return {
            "total_evidence": len(evidence_ids),
            "valid_chains": valid_count,
            "invalid_chains": len(evidence_ids) - valid_count,
            "overall_integrity": round(valid_count / len(evidence_ids) * 100, 1) if evidence_ids else 100,
            "evidence_summaries": summaries
        }


# Singleton instance
_custody_service = None

def get_custody_service() -> CustodyService:
    """Get singleton custody service"""
    global _custody_service
    if _custody_service is None:
        _custody_service = CustodyService()
    return _custody_service