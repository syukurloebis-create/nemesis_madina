"""
Finding Analysis Input - Application DTO untuk Engine
"""

from dataclasses import dataclass, field
from typing import List, Optional

from backend.dto.finding_dto import (
    FindingDTO,
    TimelineEventDTO,
    EvidenceDTO,
    DecisionDTO,
    ActionLogDTO,
    SLADTO
)


@dataclass(frozen=True)
class FindingAnalysisInput:
    """
    Input untuk FindingIntelligenceEngine.

    Ini adalah Application DTO, BUKAN Domain Object.
    Nama menunjukkan tujuannya: input untuk analysis engine.
    """
    finding: FindingDTO
    timeline: List[TimelineEventDTO] = field(default_factory=list)
    evidence: List[EvidenceDTO] = field(default_factory=list)
    decision: Optional[DecisionDTO] = None
    actions: List[ActionLogDTO] = field(default_factory=list)
    sla_breaches: List[SLADTO] = field(default_factory=list)