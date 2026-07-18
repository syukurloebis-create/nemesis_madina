"""
Graph Factory - Compatibility Wrapper

Phase B: Wrapper created
Phase C: Dual registration
Phase D: Import migration
Phase E: Legacy removal

MIGRATION METADATA:
{
    "phase": "B",
    "legacy_module": "backend.graph.application.assembler",
    "legacy_class": "GraphAssembler",
    "wrapper_version": 1
}

This is a COMPATIBILITY LAYER only.
DO NOT add business logic.
DO NOT change behavior.
DO NOT modify return values.
DO NOT change exceptions.
"""

from typing import Tuple

from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.application.dto import GraphBuildRequest
from backend.graph.application.statistics import BuilderStatistics


class GraphAssembler:
    def __init__(
        self,
        domain_builder,
        node_factory,
        edge_factory,
    ):
        from backend.graph.application.assembler import GraphAssembler as _GraphAssembler
        self._impl = _GraphAssembler(
            domain_builder=domain_builder,
            node_factory=node_factory,
            edge_factory=edge_factory,
        )
    
    def assemble(self, request):
        return self._impl.assemble(request)