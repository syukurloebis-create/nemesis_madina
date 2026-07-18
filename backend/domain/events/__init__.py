"""
Domain Events Package - Sprint 2 Foundation + Concrete Events
"""

from .base import DomainEvent
from .metadata import EventMetadata
from .serialization import (
    register_event,
    get_event_class,
    serialize,
    deserialize,
    DuplicateEventRegistrationError,
    UnknownEventError,
    EventVersionMismatchError,
)

# Sprint 1 compatibility
from .case_events import (
    CaseCreated,
    CaseUpdated,
    CaseStatusChanged,
    CaseAssigned,
    CaseClosed,
)

# Sprint 2A.2 Concrete Domain Events
from .fraud_events import (
    FraudAnalysisRecorded,      
    # FraudPayload,             
    # FraudDetectionStarted,    
    # FraudDetectionCompleted,  
)

from .risk_events import (
    RiskPayload,
    RiskAssessmentCompleted,
)

from .evidence_events import (
    EvidencePayload,
    EvidenceVerificationCompleted,
)

from .graph_events import (
    GraphPayload,
    GraphAnalysisCompleted,
)

from .procurement_events import (
    ProcurementPayload,
    ProcurementAnalysisCompleted,
)

from .application_events import (
    IntelligenceAssessmentPayload,
    IntelligenceAssessmentCompleted,
)

# Register all events with duplicate detection
_events_to_register = [
    FraudAnalysisRecorded,      
    RiskAssessmentCompleted,    
    EvidenceVerificationCompleted,  
    GraphAnalysisCompleted,     
    ProcurementAnalysisCompleted,   
    IntelligenceAssessmentCompleted, 
]

for event_class in _events_to_register:
    register_event(event_class)

__all__ = [
    # Foundation
    "DomainEvent",
    "EventMetadata",
    "register_event",
    "get_event_class",
    "serialize",
    "deserialize",
    "DuplicateEventRegistrationError",
    "UnknownEventError",
    "EventVersionMismatchError",
    
    # Sprint 1
    "CaseCreated",
    "CaseUpdated",
    "CaseStatusChanged",
    "CaseAssigned",
    "CaseClosed",
    
    # Sprint 2A.2
    "FraudAnalysisRecorded",
    "RiskPayload",
    "RiskAssessmentCompleted",
    "EvidencePayload",
    "EvidenceVerificationCompleted",
    "GraphPayload",
    "GraphAnalysisCompleted",
    "ProcurementPayload",
    "ProcurementAnalysisCompleted",
    "IntelligenceAssessmentPayload",
    "IntelligenceAssessmentCompleted",
]