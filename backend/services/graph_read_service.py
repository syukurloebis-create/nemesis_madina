# backend/services/graph_read_service.py
"""
Graph Read Service.

F3.4-B (FINAL — Hybrid Contract)
---------------------------------
Thin application read boundary for Graph Intelligence.

Responsibilities:
- Read a case-scoped GraphAggregate through GraphRepository.
- Convert domain graph data into API-ready dictionaries.
- Compute read-only structural metrics for presentation.

Does NOT:
- Build graphs.
- Persist graphs.
- Modify risk_scores.
- Modify dashboard_view.
- Calculate canonical case risk.

Domain Truth (F3.4-A / F3.4-B):
- GraphNode has EXACTLY 5 fields:
    business_key, entity_type, name, source_id, extra_data
- GraphNode has NO risk_score, NO confidence, NO id.
- Actor ranking is STRUCTURAL (degree), not risk-weighted.
"""

from collections import defaultdict
from typing import Any, Dict, List
from uuid import UUID

from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.infrastructure.interfaces.repository import GraphRepository
from backend.infrastructure.unit_of_work import IUnitOfWork


class GraphReadService:
    """Case-scoped Graph Intelligence read boundary."""

    def __init__(self, graph_repository: GraphRepository):
        self._graph_repository = graph_repository

    async def get_graph(self, uow: IUnitOfWork, case_id: UUID) -> Dict[str, Any]:
        aggregate = await self._graph_repository.get_by_case(uow, case_id)

        if aggregate is None:
            return {
                "case_id": str(case_id),
                "has_data": False,
                "nodes": [],
                "edges": [],
                "summary": {"entities": 0, "relationships": 0},
            }

        nodes = [self._node_to_dict(n) for n in aggregate.nodes]
        edges = [self._edge_to_dict(e) for e in aggregate.edges]

        return {
            "case_id": str(case_id),
            "has_data": True,
            "nodes": nodes,
            "edges": edges,
            "summary": {
                "entities": len(nodes),
                "relationships": len(edges),
            },
            "version": getattr(aggregate, "version", None),
            "checksum": getattr(aggregate, "checksum", None),
        }

    async def get_entities(
        self, uow: IUnitOfWork, case_id: UUID, limit: int = 1000
    ) -> List[Dict[str, Any]]:
        aggregate = await self._graph_repository.get_by_case(uow, case_id)
        if aggregate is None:
            return []
        limit = max(0, min(limit, 5000))
        return [self._node_to_dict(n) for n in aggregate.nodes][:limit]

    async def get_relationships(
        self, uow: IUnitOfWork, case_id: UUID, limit: int = 5000
    ) -> List[Dict[str, Any]]:
        aggregate = await self._graph_repository.get_by_case(uow, case_id)
        if aggregate is None:
            return []
        limit = max(0, min(limit, 10000))
        return [self._edge_to_dict(e) for e in aggregate.edges][:limit]

    async def get_metrics(self, uow: IUnitOfWork, case_id: UUID) -> Dict[str, Any]:
        aggregate = await self._graph_repository.get_by_case(uow, case_id)

        if aggregate is None:
            return {
                "case_id": str(case_id),
                "total_entities": 0,
                "total_relationships": 0,
                "density": 0.0,
                "entity_types": {},
                "relationship_types": {},
            }

        node_count = len(aggregate.nodes)
        edge_count = len(aggregate.edges)

        entity_types: Dict[str, int] = defaultdict(int)
        relationship_types: Dict[str, int] = defaultdict(int)

        for node in aggregate.nodes:
            entity_types[str(node.entity_type)] += 1
        for edge in aggregate.edges:
            relationship_types[str(edge.relationship_type)] += 1

        # NOTE: density formula MUST remain identical to graph_risk
        # sub-formula in risk engine:
        #   graph_risk = min(100, entities * 0.05 + density * 10)
        # Do NOT change without risk engine sprint.
        max_edges = node_count * (node_count - 1) / 2 if node_count > 1 else 0
        density = edge_count / max_edges if max_edges > 0 else 0.0

        return {
            "case_id": str(case_id),
            "total_entities": node_count,
            "total_relationships": edge_count,
            "density": round(density, 6),
            "entity_types": dict(
                sorted(entity_types.items(), key=lambda kv: kv[1], reverse=True)
            ),
            "relationship_types": dict(
                sorted(relationship_types.items(), key=lambda kv: kv[1], reverse=True)
            ),
        }

    async def get_stats(self, uow: IUnitOfWork, case_id: UUID) -> Dict[str, Any]:
        metrics = await self.get_metrics(uow, case_id)
        return {
            "case_id": str(case_id),
            "total_entities": metrics["total_entities"],
            "total_relationships": metrics["total_relationships"],
            "entity_types": metrics["entity_types"],
            "relationship_types": metrics["relationship_types"],
        }

    async def get_key_actors(
        self, uow: IUnitOfWork, case_id: UUID, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Key actors — STRUCTURAL ranking by degree.

        F3.4-B: NO risk_score, NO confidence.
        GraphNode does not carry risk semantics; risk lives in Risk Engine v3.
        """
        aggregate = await self._graph_repository.get_by_case(uow, case_id)
        if aggregate is None:
            return []

        degree: Dict[str, int] = defaultdict(int)
        for edge in aggregate.edges:
            degree[str(edge.source_key)] += 1
            degree[str(edge.target_key)] += 1

        nodes_by_key = {str(n.business_key): n for n in aggregate.nodes}

        actors: List[Dict[str, Any]] = []
        for business_key, count in degree.items():
            node = nodes_by_key.get(business_key)
            if node is None:
                continue
            actors.append({
                "id": business_key,
                "business_key": business_key,
                "name": node.name,
                "entity_type": str(node.entity_type),
                "degree": count,
            })

        actors.sort(key=lambda a: a["degree"], reverse=True)
        return actors[: max(0, min(limit, 100))]

    # ---------------------------------------------------------------
    # Domain → dict
    # ---------------------------------------------------------------

    @staticmethod
    def _node_to_dict(node: Any) -> Dict[str, Any]:
        business_key = getattr(node, "business_key", None)
        node_id = str(business_key) if business_key is not None else ""

        return {
            "id": node_id,
            "business_key": business_key,
            "name": getattr(node, "name", ""),
            "entity_type": str(getattr(node, "entity_type", "")),
            "source_id": getattr(node, "source_id", None),   # int | None (domain truth)
            "extra_data": getattr(node, "extra_data", {}) or {},
            # NOTE: intentionally NO risk_score, NO confidence.
            # GraphNode has exactly 5 fields (F3.4-A audit).
        }

    @staticmethod
    def _edge_to_dict(edge: Any) -> Dict[str, Any]:
        return {
            "id": getattr(edge, "id", None),  # often None (domain truth)
            "source": str(getattr(edge, "source_key", "")),
            "target": str(getattr(edge, "target_key", "")),
            "relationship_type": str(getattr(edge, "relationship_type", "")),
            "weight": float(getattr(edge, "weight", 0) or 0),
            "amount": (
                float(edge.amount)
                if getattr(edge, "amount", None) is not None
                else None
            ),
            "description": getattr(edge, "description", None),
            "extra_data": getattr(edge, "extra_data", {}) or {},
        }


__all__ = ["GraphReadService"]