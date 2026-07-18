"""
Vendor Graph Builder Adapter - Legacy Compatibility

Adapts the legacy vendor_graph_builder.py to use the new architecture.
Wrapper ONLY - no business logic, no validation, no mapping.
"""

from typing import Dict, Any, Optional
from uuid import UUID
import logging

from backend.services.graph_regeneration_service import GraphRegenerationService
from backend.graph.dto.graph_regeneration_result import GraphRegenerationResult

logger = logging.getLogger(__name__)


class VendorGraphBuilderAdapter:
    """
    Legacy Vendor Graph Builder Adapter.
    
    This adapter allows the legacy vendor_graph_builder.py to use the new
    architecture without modifying the legacy code.
    
    Wrapper Rules:
    - ONLY normalize input → delegate → return result
    - NO business logic
    - NO validation
    - NO mapping
    """
    
    def __init__(self, service: GraphRegenerationService):
        self._service = service
    
    async def build_vendor_graph(
        self,
        case_id: Optional[UUID] = None,
        institution_id: Optional[UUID] = None,
        source_data: Optional[Dict[str, Any]] = None,
    ) -> GraphRegenerationResult:
        """
        Build vendor graph using the new architecture.
        
        Args:
            case_id: Case UUID (required for new architecture)
            institution_id: Institution UUID (required for new architecture)
            source_data: Source data (required for new architecture)
            
        Returns:
            GraphRegenerationResult
            
        Raises:
            ValueError: If required parameters are missing
        """
        # Validate required parameters
        if case_id is None:
            raise ValueError("case_id is required")
        if institution_id is None:
            raise ValueError("institution_id is required")
        if source_data is None:
            raise ValueError("source_data is required")
        
        # Delegate to service
        return await self._service.regenerate_graph(
            case_id=case_id,
            institution_id=institution_id,
            source_data=source_data,
            strategy="replace",
        )
    
    @staticmethod
    def convert_legacy_data(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert legacy data format to new format.
        
        This is a helper for callers that still use the old data format.
        
        Args:
            legacy_data: Legacy data from vendor_graph_builder
            
        Returns:
            Normalized data for GraphRegenerationService
        """
        return {
            "vendors": legacy_data.get("nodes", []),
            "packages": legacy_data.get("packages", []),
            "institutions": legacy_data.get("institutions", []),
            "relationships": legacy_data.get("edges", []),
        }