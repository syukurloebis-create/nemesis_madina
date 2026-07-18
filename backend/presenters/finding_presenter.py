"""
Finding Presenter — Pure Serializer.

ADR-020: Presenter = Serializer Only.
Domain Entity → Dict for API Response.
"""

from dataclasses import asdict
from typing import List, Dict, Any

from backend.domain.entities.finding import Finding


class FindingPresenter:
    """
    Finding Presenter — Pure Serializer.
    
    ONLY converts Domain Finding → Dict.
    NO business logic.
    NO calculations.
    """

    @staticmethod
    def present(finding: Finding) -> Dict[str, Any]:
        """
        Present a single Finding as dict.
        
        Args:
            finding: Domain Finding entity
            
        Returns:
            Dict: Serialized Finding
        """
        return asdict(finding)

    @staticmethod
    def present_list(findings: List[Finding]) -> List[Dict[str, Any]]:
        """
        Present a list of Findings as dicts.
        
        Args:
            findings: List of Domain Finding entities
            
        Returns:
            List[Dict]: Serialized Findings
        """
        return [asdict(f) for f in findings]