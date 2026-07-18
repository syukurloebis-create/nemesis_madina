"""
Finding Intelligence Composer - Murni agregasi data (sinkron)
"""

from typing import List, Dict, Optional

from backend.dto.finding_dto import (
    FindingDTO,
    TimelineEventDTO,
    EvidenceDTO,
    DecisionDTO,
    ActionLogDTO,
    SLADTO
)
from backend.application.dto.finding_analysis_input import FindingAnalysisInput


class FindingIntelligenceComposer:
    """
    Composer untuk finding intelligence - MURNI AGREGASI.

    Menerima DTO, menghasilkan FindingAnalysisInput.
    """

    def compose_batch(
        self,
        findings: List[FindingDTO],
        timeline_map: Dict[str, List[TimelineEventDTO]],
        evidence_map: Dict[str, List[EvidenceDTO]],  # <-- Evidence dari database
        decision_map: Dict[str, Optional[DecisionDTO]],
        action_map: Dict[str, List[ActionLogDTO]],
        sla_map: Dict[str, List[SLADTO]]
    ) -> Dict[str, FindingAnalysisInput]:
        result = {}
    
        for finding in findings:
            finding_id = finding.id
        
            # Evidence dari database
            evidence_list = evidence_map.get(finding_id, [])
        
            analysis_input = FindingAnalysisInput(
                finding=finding,
                timeline=timeline_map.get(finding_id, []),
                evidence=evidence_list,  # <-- FIX: evidence dari database
                decision=decision_map.get(finding_id),
                actions=action_map.get(finding_id, []),
                sla_breaches=sla_map.get(finding_id, [])
            )
        
            result[finding_id] = analysis_input
    
        return result