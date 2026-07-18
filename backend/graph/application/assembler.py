"""
Graph Application - Assembler
"""

from typing import Tuple, List, Dict, Any
from uuid import UUID

from backend.graph.domain.node import GraphNode
from backend.graph.domain.edge import GraphEdge
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.builder import GraphDomainBuilder, DomainBuildResult
from backend.graph.domain.factory import GraphNodeFactory, GraphEdgeFactory
from backend.graph.application.dto import GraphBuildRequest
from backend.graph.application.statistics import BuilderStatistics


class GraphAssembler:
    def __init__(
        self,
        domain_builder,
        node_factory,
        edge_factory,
    ):
        self._domain_builder = domain_builder
        self._node_factory = node_factory
        self._edge_factory = edge_factory

    def assemble(self, request: GraphBuildRequest) -> Tuple[GraphAggregate, BuilderStatistics]:
        # ✅ 1. Build Nodes
        nodes: List[GraphNode] = []
        warnings: List[str] = []

        for vendor in request.vendors:
            node = self._node_factory.create_vendor({
                "npwp": vendor.npwp,
                "name": vendor.name,
                "address": vendor.address,
                "sector": vendor.sector,
                "registration_date": vendor.registration_date,
                "extra_data": vendor.extra_data,
            })
            nodes.append(node)

        for package in request.packages:
            node = self._node_factory.create_package({
                "package_code": package.package_code,
                "name": package.name,
                "value": package.value,
                "procuring_institution": package.procuring_institution,
                "procurement_method": package.procurement_method,
                "extra_data": package.extra_data,
            })
            nodes.append(node)

        for officer in request.officers:
            node = self._node_factory.create_officer({
                "nip": officer.nip,
                "name": officer.name,
                "position": officer.position,
                "institution": officer.institution,
                "extra_data": officer.extra_data,
            })
            nodes.append(node)

        for institution in request.institutions:
            node = self._node_factory.create_institution({
                "id": institution.id,
                "name": institution.name,
                "type": institution.type,
                "address": institution.address,
                "extra_data": institution.extra_data,
            })
            nodes.append(node)

        # ✅ 2. Build Edges
        edges: List[GraphEdge] = []
        node_keys = {n.business_key for n in nodes}

        for rel in request.relationships:
            if rel.source not in node_keys:
                warnings.append(f"Source not found: {rel.source}")
                continue
            if rel.target not in node_keys:
                warnings.append(f"Target not found: {rel.target}")
                continue

            if rel.relationship_type == "COLLUSION":
                edge = self._edge_factory.create_collusion_edge(
                    rel.source, rel.target, {
                        "weight": rel.weight,
                        "amount": rel.amount,
                        "description": rel.description,
                        "extra_data": rel.extra_data,
                    }
                )
            elif rel.relationship_type == "CONTRACT":
                edge = self._edge_factory.create_contract_edge(
                    rel.source, rel.target, {
                        "weight": rel.weight,
                        "amount": rel.amount,
                        "description": rel.description,
                        "extra_data": rel.extra_data,
                    }
                )
            elif rel.relationship_type == "OWNERSHIP":
                edge = self._edge_factory.create_ownership_edge(
                    rel.source, rel.target, {
                        "weight": rel.weight,
                        "amount": rel.amount,
                        "description": rel.description,
                        "extra_data": rel.extra_data,
                    }
                )
            else:
                edge = GraphEdge(
                    source_key=rel.source,
                    target_key=rel.target,
                    relationship_type=rel.relationship_type,
                    weight=rel.weight,
                    amount=rel.amount,
                    description=rel.description,
                    extra_data=rel.extra_data,
                )
            edges.append(edge)

        # ✅ 3. Build Aggregate using Domain Builder
        domain_result = self._domain_builder.build_from_nodes_and_edges(
            case_id=request.case_id,
            institution_id=request.institution_id,
            nodes=nodes,
            edges=edges,
        )

        # ✅ 4. Build Statistics
        statistics = BuilderStatistics(
            total_nodes=domain_result.nodes_count,
            total_edges=domain_result.edges_count,
            duplicates_removed=domain_result.duplicates_removed,
            invalid_edges_skipped=len(warnings),
            normalized_nodes=0,
            collapsed_nodes=0,
            warnings=tuple(warnings),
        )

        # ✅ 5. Return
        return domain_result.aggregate, statistics