from enum import Enum
from typing import List, Dict, Any
from datetime import datetime


class CaseStatus(str, Enum):
    """Investigation lifecycle status"""
    REPORTED = "REPORTED"           # Laporan masuk
    SCREENING = "SCREENING"         # Screening awal
    ASSESSMENT = "ASSESSMENT"       # Assessment & prioritization
    INVESTIGATION = "INVESTIGATION" # Investigasi mendalam
    FINDING = "FINDING"             # Penyusunan temuan
    RECOMMENDATION = "RECOMMENDATION" # Rekomendasi tindak lanjut
    FOLLOW_UP = "FOLLOW_UP"         # Monitoring tindak lanjut
    CLOSED = "CLOSED"               # Kasus selesai


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Valid transitions berdasarkan lifecycle
TRANSITIONS: Dict[CaseStatus, List[CaseStatus]] = {
    CaseStatus.REPORTED: [CaseStatus.SCREENING, CaseStatus.CLOSED],
    CaseStatus.SCREENING: [CaseStatus.ASSESSMENT, CaseStatus.CLOSED],
    CaseStatus.ASSESSMENT: [CaseStatus.INVESTIGATION, CaseStatus.CLOSED],
    CaseStatus.INVESTIGATION: [CaseStatus.FINDING, CaseStatus.CLOSED],
    CaseStatus.FINDING: [CaseStatus.RECOMMENDATION],
    CaseStatus.RECOMMENDATION: [CaseStatus.FOLLOW_UP],
    CaseStatus.FOLLOW_UP: [CaseStatus.CLOSED],
    CaseStatus.CLOSED: []
}

# Required conditions untuk setiap transisi
TRANSITION_CONDITIONS: Dict[tuple, List[str]] = {
    (CaseStatus.REPORTED, CaseStatus.SCREENING): ["case_complete"],
    (CaseStatus.SCREENING, CaseStatus.ASSESSMENT): ["screening_complete"],
    (CaseStatus.ASSESSMENT, CaseStatus.INVESTIGATION): ["risk_assessed", "priority_assigned"],
    (CaseStatus.INVESTIGATION, CaseStatus.FINDING): ["evidence_sufficient"],
    (CaseStatus.FINDING, CaseStatus.RECOMMENDATION): ["finding_approved"],
    (CaseStatus.RECOMMENDATION, CaseStatus.FOLLOW_UP): ["recommendation_issued"],
    (CaseStatus.FOLLOW_UP, CaseStatus.CLOSED): ["followup_complete"]
}


def can_transition(from_status: CaseStatus, to_status: CaseStatus) -> bool:
    """Check if transition is valid"""
    return to_status in TRANSITIONS.get(from_status, [])


def get_required_conditions(from_status: CaseStatus, to_status: CaseStatus) -> List[str]:
    """Get required conditions for transition"""
    return TRANSITION_CONDITIONS.get((from_status, to_status), [])


def get_status_display_name(status: CaseStatus) -> str:
    """Get human-readable status name"""
    names = {
        CaseStatus.REPORTED: "Reported",
        CaseStatus.SCREENING: "Screening",
        CaseStatus.ASSESSMENT: "Assessment",
        CaseStatus.INVESTIGATION: "Investigation",
        CaseStatus.FINDING: "Finding",
        CaseStatus.RECOMMENDATION: "Recommendation",
        CaseStatus.FOLLOW_UP: "Follow Up",
        CaseStatus.CLOSED: "Closed"
    }
    return names.get(status, status.value)
